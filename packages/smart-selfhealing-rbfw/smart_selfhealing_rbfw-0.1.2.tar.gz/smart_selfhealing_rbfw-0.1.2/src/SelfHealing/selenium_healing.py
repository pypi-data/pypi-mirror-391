from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
import json
import os
import base64
import tempfile
import traceback
from bs4 import BeautifulSoup
from bs4.element import Comment
import re
from .llm_client import LOCATOR_AI_MODEL, completion_with_debug
from .utils import (extract_json_objects, generate_unique_css_selector, 
                    generate_unique_xpath_selector)
from .locator_db import LocatorDetailsDB
import time

try:
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from selenium.webdriver.common.by import By
except ImportError:
    _has_selenium = False
else:
    _has_selenium = True


class SeleniumHealer:
    _instance = None
    _locator_variable_map = {}  # Maps locator values to their original variable names

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SeleniumHealer, cls).__new__(cls)
        return cls._instance

    def __init__(self, instance=None, **kwargs):
        self.selenium = instance
        self.use_locator_db = kwargs.get('use_locator_db', False)
        self.use_llm_for_locator_proposals = kwargs.get('use_llm_for_locator_proposals', True)
        self.use_llm_with_vision = kwargs.get('use_llm_with_vision', False)  # New option for vision API
        self.read_clickable_info = kwargs.get('read_clickable_info', True)
        self.debug_llm = kwargs.get('debug_llm', False)
    
    def is_locator_broken(self, message) -> bool:
        """Check if the error message indicates a broken locator"""
        broken_indicators = [
            'Unable to locate element',
            'no such element',
            'NoSuchElementException',
            'Element not found',
            'Could not find element',
            'did not match any elements',
            'Element with locator',
            'not found',
            'not visible after',  # Added: visibility timeout indicates potential locator issue
            'element is not visible',  # Added: explicit visibility check failure
        ]
        message_lower = message.lower()
        return any(indicator.lower() in message_lower for indicator in broken_indicators)
    
    def is_element_not_ready(self, message) -> bool:
        """Check if the error message indicates element is not ready"""
        not_ready_indicators = [
            'element is not visible',
            'element is not interactable',
            'ElementNotInteractableException',
            'ElementNotVisibleException',
            'element not visible',
            'not clickable'
        ]
        message_lower = message.lower()
        return any(indicator.lower() in message_lower for indicator in not_ready_indicators)

    def is_modal_dialog_open(self) -> bool:
        """Check if a modal dialog is currently open on the page"""
        try:
            page_source = self.selenium.get_source()
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Check for dialog elements
            dialogs = soup.find_all('dialog', {"open": True})
            if len(dialogs) > 0:
                return True
            
            # Check for common modal patterns (divs with modal classes)
            modal_patterns = ['modal', 'dialog', 'popup', 'overlay']
            for pattern in modal_patterns:
                modals = soup.find_all(lambda tag: tag.get('class') and 
                                      any(pattern in ' '.join(tag.get('class', [])).lower() 
                                      for pattern in modal_patterns))
                if len(modals) > 0:
                    return True
            
            return False
        except Exception as e:
            logger.debug(f"Error checking for modal dialog: {e}")
            return False

    def is_page_loading(self) -> bool:
        """Check if the page is still loading"""
        try:
            is_loading_script = "return document.readyState != 'complete';"
            is_loading = self.selenium.execute_javascript(is_loading_script)
            return bool(is_loading)
        except Exception as e:
            logger.debug(f"Error checking page loading state: {e}")
            return False

    def is_page_ready(self) -> bool:
        """Check if the page is fully loaded"""
        try:
            is_ready_script = "return document.readyState == 'complete';"
            is_ready = self.selenium.execute_javascript(is_ready_script)
            return bool(is_ready)
        except Exception as e:
            logger.debug(f"Error checking page ready state: {e}")
            return False

    def wait_until_page_is_ready(self, timeout=20):
        """Wait until the page is fully loaded"""
        try:
            BuiltIn().wait_until_keyword_succeeds(timeout, "1s", 
                                                  "SeleniumLibrary.Wait For Condition", 
                                                  "return document.readyState == 'complete'", 
                                                  f"{timeout}s")
        except Exception as e:
            logger.debug(f"Error waiting for page to be ready: {e}")

    def close_modal_dialog(self):
        """Attempt to close a modal dialog using LLM to find the close button"""
        try:
            page_source = self.selenium.get_source()
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find the dialog element
            dialog = soup.find('dialog', {"open": True})
            if not dialog:
                # Look for common modal patterns
                modal_patterns = ['modal', 'dialog', 'popup']
                for pattern in modal_patterns:
                    dialog = soup.find(lambda tag: tag.get('class') and 
                                      pattern in ' '.join(tag.get('class', [])).lower())
                    if dialog:
                        break
            
            if not dialog:
                logger.warn("Could not find dialog element to close")
                return None

            schema = {
                "fixed_locator": "The fixed css or xpath locator. Starts with xpath= or css="
            }

            messages = []
            messages.append({
                'role': 'system',
                'content': (
                    "You are a xpath and css selector tool that shall close a dialog."
                    "You will analyze the `page_source` and find a short and unique xpath or css selector to close the dialog."
                    "Most likely a button or a link needs to be clicked"
                    "Respond only in valid json that looks like this: {'fixed_locator': <a fixed xpath or css locator>}"         
                    "When the 'fixed_locator' is an xpath, always add a xpath= prefix to the locator."
                    "When the 'fixed_locator' is an css selector, always add a css= prefix to the locator."
                    f"Use the following schema: ```json{json.dumps(schema)}```."
                )
            })
            
            messages.append({
                'role': 'user',
                'content': f"'page_source': ```{str(dialog)}```\n"
            })

            locator_has_been_fixed = False
            retry_count = 0
            
            while not locator_has_been_fixed and retry_count < 5:
                retry_count += 1
                
                response = completion_with_debug(
                    debug_enabled=self.debug_llm,
                    model=LOCATOR_AI_MODEL,
                    messages=messages,
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                solution_text = response['choices'][0]['message']['content']

                try:
                    solution_dict = list(extract_json_objects(solution_text))[0]
                    fixed_locator = str(solution_dict['fixed_locator'])
                except Exception as e:
                    logger.debug(f"Error parsing LLM response: {e}")
                    continue

                # Convert locator format for Selenium
                retry_selector = self._normalize_locator(fixed_locator)

                try:
                    if self.get_element_count_for_locator(retry_selector) == 1:
                        locator_has_been_fixed = True
                        logger.info(f"Locator to close dialog has been found: {retry_selector}", also_console=True)
                        BuiltIn().run_keyword("SeleniumLibrary.Click Element", retry_selector)
                        return fixed_locator
                except Exception as e:
                    logger.debug(f"Failed to click close button: {e}")
                    locator_has_been_fixed = False
            
            return None
        except Exception as e:
            logger.error(f"Error closing modal dialog: {e}")
            return None

    def _normalize_locator(self, locator):
        """Normalize locator format for SeleniumLibrary"""
        if locator.startswith('xpath=') or locator.startswith('css='):
            return locator
        elif locator.startswith('/') or locator.startswith('('):
            return f"xpath={locator}"
        elif locator.startswith('#') or locator.startswith('.'):
            return f"css={locator}"
        else:
            # Try to determine if it's xpath or css
            if '//' in locator or locator.startswith('/'):
                return f"xpath={locator}"
            else:
                return f"css={locator}"

    def get_fixed_locator(self, data, result) -> str:
        """Get a fixed locator using LLM or parser-based approach"""
        # Keep log level at DEBUG to see healing process
        old_log_level = "DEBUG"
        try:
            old_log_level = BuiltIn().set_log_level("DEBUG")
        except Exception as e:
            logger.info(f"Error when setting log level: {e}")

        logger.info("▶ Starting get_fixed_locator process", also_console=True)
        
        output_dir = BuiltIn().get_variable_value('${OUTPUT_DIR}')
        testsuite = BuiltIn().get_variable_value('${SUITE NAME}')
        
        # Get page source
        try:
            page_source = self.selenium.get_source()
            logger.info(f"Page source retrieved: {len(page_source)} chars", also_console=True)
        except Exception as e:
            logger.info(f"⚠ Error getting page source: {e}", also_console=True)
            return None

        soup = BeautifulSoup(page_source, 'html.parser')
        failed_locator = BuiltIn().replace_variables(str(result.args[0]))
        
        # Extract logical element name from variable (e.g., ${corporate_event_page.dropdown_search_by_category})
        original_variable = str(data.args[0]) if data.args else ""
        logger.info(f"Original variable from data.args: {original_variable}", also_console=True)
        
        # Try to find a better variable name by searching all Robot Framework variables
        # This helps when the locator is passed through custom keywords (e.g., ${locator} -> actual variable)
        if original_variable in ["${locator}", "${element}", "${selector}"]:
            logger.info(f"Generic variable name detected: {original_variable}, searching for original variable...", also_console=True)
            
            # Check if we have it in our map
            if failed_locator in self._locator_variable_map:
                original_variable = self._locator_variable_map[failed_locator]
                logger.info(f"Found original variable from map: {original_variable}", also_console=True)
            else:
                # Search all Robot Framework variables for one that matches this locator value
                try:
                    all_vars = BuiltIn().get_variables()
                    for var_name, var_value in all_vars.items():
                        # Skip system variables and generic names
                        if var_name.startswith('${') and var_name not in ["${locator}", "${element}", "${selector}", "${EMPTY}", "${SPACE}", "${True}", "${False}", "${None}", "${null}"]:
                            # Check if this variable resolves to our failed locator
                            try:
                                resolved_value = str(var_value)
                                if resolved_value == failed_locator:
                                    original_variable = var_name
                                    # Store in map for future use
                                    self._locator_variable_map[failed_locator] = var_name
                                    logger.info(f"Found matching variable: {var_name} = {resolved_value}", also_console=True)
                                    break
                            except:
                                pass
                except Exception as e:
                    logger.debug(f"Error searching variables: {e}")
        
        logical_name = self._extract_logical_name_from_variable(original_variable)
        logger.info(f"Extracted logical element name: {logical_name}", also_console=True)
        
        fixed_locator_list = []
        
        if self.use_llm_for_locator_proposals:
            logger.info("▶ Using LLM for locator proposals", also_console=True)
            try:
                fixed_locator_list = self.get_locator_proposals_from_llm(data, result, soup, logical_name)
                logger.info(f"▶ LLM returned {len(fixed_locator_list)} proposals", also_console=True)
            except Exception as e:
                import traceback
                logger.info(f"⚠ Exception in get_locator_proposals_from_llm: {e}", also_console=True)
                logger.info(f"Traceback: {traceback.format_exc()}", also_console=True)
        else:
            logger.info("▶ Using parser for locator proposals", also_console=True)
            fixed_locator_list = self.get_locator_proposals_from_parser(data, result, soup)

        # Filter and validate locators
        if fixed_locator_list:
            logger.info(f"▶ Validating {len(fixed_locator_list)} locator proposals", also_console=True)
            valid_locators = []
            for i, locator in enumerate(fixed_locator_list, 1):
                try:
                    normalized = self._normalize_locator(locator)
                    logger.info(f"  Testing locator {i}/{len(fixed_locator_list)}: {normalized}", also_console=True)
                    count = self.get_element_count_for_locator(normalized)
                    logger.info(f"  Found {count} matching elements", also_console=True)
                    if count > 0:
                        valid_locators.append(normalized)
                        logger.info(f"  ✓ Locator {i} is valid!", also_console=True)
                except Exception as e:
                    logger.info(f"  ✗ Locator {i} failed: {e}", also_console=True)
                    continue
            
            if valid_locators:
                logger.info(f"▶ Found {len(valid_locators)} valid locators: {valid_locators}", also_console=True)
                try:
                    BuiltIn().set_log_level(old_log_level)
                except:
                    pass
                return valid_locators[0]
            else:
                logger.info("⚠ No valid locators found after validation", also_console=True)
        else:
            logger.info("⚠ No locator proposals generated", also_console=True)
        
        try:
            BuiltIn().set_log_level(old_log_level)
        except:
            pass
        
        logger.info("▶ Returning None - healing failed", also_console=True)
        return None

    def _clean_html_for_llm(self, html_content: str) -> str:
        """Remove scripts, styles, and other unnecessary content from HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script tags
            for script in soup.find_all('script'):
                script.decompose()
            
            # Remove style tags
            for style in soup.find_all('style'):
                style.decompose()
            
            # Remove noscript tags
            for noscript in soup.find_all('noscript'):
                noscript.decompose()
            
            # Remove head tag (keep body only)
            for head in soup.find_all('head'):
                head.decompose()
            
            # Remove SVG path elements (they're huge and not useful for locators)
            for path in soup.find_all('path'):
                path.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            cleaned = str(soup)
            logger.info(f"HTML cleaned: {len(html_content)} chars → {len(cleaned)} chars (saved {len(html_content) - len(cleaned)} chars)", also_console=True)
            return cleaned
        except Exception as e:
            logger.info(f"⚠ Error cleaning HTML: {e}, using original", also_console=True)
            return html_content
    
    def get_locator_proposals_from_llm(self, data, result, soup, logical_name=None) -> list:
        """Use LLM to generate locator proposals with enhanced prompt for reliability"""
        import os
        import json
        from datetime import datetime
        
        logger.info("=" * 80, also_console=True)
        logger.info("Starting LLM-based locator healing process", also_console=True)
        logger.info("=" * 80, also_console=True)
        
        failed_locator = BuiltIn().replace_variables(str(result.args[0]))
        keyword_name = data.name
        
        logger.info(f"Failed locator: {failed_locator}", also_console=True)
        logger.info(f"Keyword name: {keyword_name}", also_console=True)
        
        # Get full page source and clean it
        page_source_raw = str(soup)
        logger.info(f"Raw page source length: {len(page_source_raw)} chars", also_console=True)
        
        # Clean HTML by removing scripts, styles, comments, etc.
        page_source = self._clean_html_for_llm(page_source_raw)
        logger.info(f"Cleaned page source length: {len(page_source)} chars", also_console=True)
        
        # Try to extract the element context around the failed locator
        # This helps LLM understand what element we're trying to locate
        element_context = self._extract_element_context(failed_locator, soup)
        logger.info(f"Element context extracted: {len(element_context)} chars", also_console=True)
        
        # Use logical name if provided, otherwise derive from locator/keyword
        if logical_name and logical_name != "element_target":
            locator_name = logical_name
            logger.info(f"Using logical element name from variable: {locator_name}", also_console=True)
        else:
            locator_name = self._derive_locator_name(failed_locator, keyword_name)
            logger.info(f"Derived element name from locator: {locator_name}", also_console=True)
        
        # Capture screenshot for visual context only if vision is enabled
        screenshot_base64 = None
        use_vision = False
        
        if self.use_llm_with_vision:
            logger.info("Vision API enabled - capturing screenshot for analysis", also_console=True)
            screenshot_base64 = self._capture_screenshot_as_base64()
            use_vision = screenshot_base64 is not None
            if not use_vision:
                logger.info("⚠ Vision enabled but screenshot capture failed - falling back to text-only mode", also_console=True)
            else:
                logger.info(f"Screenshot captured successfully (base64 length: {len(screenshot_base64)})", also_console=True)
        else:
            logger.info("Vision API disabled - using text-only analysis (use_llm_with_vision=False)", also_console=True)

        messages = []
        
        # Enhanced system prompt when vision is available
        if use_vision:
            system_content = (
                "You are an expert in generating reliable and precise **XPath locators** that can be tested in **Chrome DevTools**.\n"
                "You have been provided with a **screenshot** of the page and the HTML source code.\n"
                "Your task is to generate **up to 5 valid, reliable, and unique XPath locators** that accurately identify the target element.\n\n"
                "**Use the screenshot to:**\n"
                "- Visually identify the target element based on the `locator_name` (e.g., for 'btn_view_results', find the visible 'View results' button)\n"
                "- Understand the element's position, size, and visual context\n"
                "- Distinguish between similar elements by their visual appearance\n"
                "- Identify the correct element when multiple candidates exist in the HTML\n\n"
            )
        else:
            system_content = (
                "You are an expert in generating reliable and precise **XPath locators** that can be tested in **Chrome DevTools**.\n"
                "Your task is to generate **up to 5 valid, reliable, and unique XPath locators** that accurately identify the given HTML `element` within the full page `page_source`.\n\n"
            )
        
        messages.append({
            'role': 'system',
            'content': system_content + (
                
                "### Your Inputs:\n"
                "- `page_source`: The complete HTML content of the page (used for context and uniqueness verification).\n"
                "- `element`: The specific HTML element to target (e.g. `<input name=\"email\" id=\"user_email\" ...>`).\n"
                "- `locator_name`: A descriptive logical name for the element (e.g. `dropdown_search_by_category`, `btn_view_results`, `input_search_subrurb`).\n"
                "  **IMPORTANT**: This name comes from the test code and describes the element's PURPOSE and TYPE. Use it to:\n"
                "  - Identify what kind of element to look for (dropdown, button, input, etc.)\n"
                "  - Match against HTML attributes (id, name, class, aria-label, title) that contain related keywords\n"
                "  - Example: `dropdown_search_by_category` suggests looking for a dropdown/select element with category-related attributes\n"
                "- `keyword`: The Robot Framework keyword being executed (e.g. 'Click Element', 'Input Text').\n"
                "- `failed_locator`: The original locator that didn't work - use this to understand what approach failed.\n\n"
                
                "### Your Task:\n"
                "Generate XPath locators that precisely and uniquely identify the provided `element`, strictly following the rules below.\n\n"
                
                "---\n\n"
                "### Locator Generation Rules:\n\n"
                
                "1. **Use only attributes that actually exist on the provided `element`.**\n"
                "   - Do not assume or fabricate any attributes.\n\n"
                
                "2. **Intelligently use `locator_name` to find matching attributes.** The `locator_name` is a rich source of information:\n"
                "   - Break it down: `dropdown_search_by_category` → look for 'dropdown', 'search', 'category' in attributes\n"
                "   - Extract type: `btn_view_results` → it's a button, prioritize button/a/clickable elements\n"
                "   - Match keywords: `input_search_subrurb` → look for input with 'search' or 'suburb' in id/name/placeholder\n"
                "   - Example: For `dropdown_when_options`, look for select/mat-select elements with 'when' or 'time' related attributes\n\n"
                
                "3. **Only use reliable attributes — and only if their values are related to the `locator_name`.** Prioritize in this order:\n"
                "   `id` > `name` > visible `text` > `class` > `aria-label` > `title` > `placeholder` > `data-*`\n"
                "   - Use `id` only if:\n"
                "      - It is not auto-generated (no random numbers/UUIDs) OR\n"
                "      - It matches the pattern/keywords from `locator_name` (e.g., 'mat-select-1' for 'dropdown_when_options')\n"
                "   - Use `name`, `aria-label`, `title`, or `placeholder` if their values relate to keywords in `locator_name`.\n"
                "   - Use `class` only if at least one class segment matches keywords from `locator_name`.\n"
                "   - Do not use generic or unrelated values like `form-control`, `input`, `btn`, or random strings.\n\n"
                
                "4. **If the target element lacks reliable attributes, base the XPath on a reliable parent, then traverse down.**\n"
                "   - First, locate a parent or ancestor with a stable attribute related to `locator_name`.\n"
                "   - Then generate XPath from that parent down to the target element using tag and structure.\n"
                "   - Prefer clean DOM traversal over long XPath axes.\n"
                "   - Avoid reverse or indirect references like `ancestor::div[...]` unless unavoidable.\n\n"
                
                "5. **For `<label>`, `<a>`, `<div>`, or similar elements that contain a child `<span>` with visible text:**\n"
                "   - Always locate the element using: `//label[.//span[normalize-space()='Email or User ID']]`\n"
                "   - This applies whether the text contains spaces or not.\n"
                "   - Do not use text()='...' as it breaks with nested tags or formatting.\n"
                "   - Always use `normalize-space()` when matching visible text.\n\n"
                
                "6. **Do not use absolute XPath or index unless absolutely necessary.**\n"
                "   - Avoid paths like `/html/body/...`\n"
                "   - Do not use `[1]` or other indices unless the XPath would otherwise match multiple elements.\n"
                "   - Use index only when disambiguation is required.\n\n"
                
                "7. **Ensure deterministic output.**\n"
                "   The same `page_source`, `element`, and `locator_name` must always result in the same locators and order.\n"
                "   - No randomness.\n\n"
                
                "8. **Output format must be JSON only, with no explanations.**\n"
                "   Format: `{\"fixed_locators\": [\"locator_1\", \"locator_2\", ...]}`\n\n"
                
                "9. **Generate the simplest XPath possible.**\n"
                "   - Prefer one-attribute match when sufficient: `//input[@name='email']`\n"
                "   - Avoid multiple-attribute XPath like: `//input[@type='text' and @name='email']` unless absolutely necessary.\n\n"
                
                "10. **Generate XPath strictly based on the provided `element`.**\n"
                "   - Do not use sibling or similar-looking elements with matching attributes.\n"
                "   - The XPath must match **only** the actual `element` from the input.\n\n"
                
                "11. **Do not use class unless it contains a segment that maps clearly to the `locator_name`.**\n"
                "    - Prefer short, semantic classes like `product-lists`.\n"
                "    - Use `contains(@class, '...')` only when the value is meaningful.\n"
                "    - Avoid long, generic utility classes or the entire `class` value.\n\n"
                
                "12. **Honor indexing information from `locator_name`.**\n"
                "    - If `locator_name` includes an ordinal (e.g., `btn_first_reorder`), use it in the XPath:\n"
                "    Example: `(//a[normalize-space(.)='Reorder'])[1]`\n"
                "    - Do not return unindexed XPath when `locator_name` implies a specific index.\n\n"
                
                "13. **Only generate XPath locators.**\n"
                "    - Do not return CSS selectors, even if valid.\n"
                "    - The output must consist of valid XPath expressions only.\n\n"
                
                "14. **Avoid returning multiple XPath variants that resolve to the same element.**\n"
                "    - Each XPath must match a unique approach or targeting logic.\n"
                "    - Do not return both `//*[@id='login']` and `//input[@id='login']` — pick only the best one.\n\n"
                
                "15. **Every XPath must be built using a different primary attribute or strategy. If there are not enough unique strategies available, return fewer locators — never repeat the same attribute strategy. This rule is strict and non-negotiable.**\n"
                "    These XPath locators are used for self-healing — if multiple locators rely on the same attribute or logic, they will all fail together.\n"
                "    - Each generated XPath must use a completely different attribute or structural approach.\n"
                "    - Valid strategies include: id, name, title, aria-label, text(), class, data-*, DOM traversal via parent/ancestor, sibling-based navigation, etc.\n"
                "    - You may use one of each type — but do not use the same attribute (even partially) in more than one XPath.\n"
                "    - Example — correct diversity:\n"
                "        //a[contains(@class, 'product-item-photo')]      (class)\n"
                "        //a[@title='View product']                       (title)\n"
                "        //div[@data-product-id]//a                       (data-attribute)\n"
                "        (//a[normalize-space(.)='Reorder'])[1]          (visible text)\n"
                "        //div[@id='product-wrapper']//a                  (id on parent, DOM traversal)\n"
                "    - Example — invalid redundancy:\n"
                "        //a[contains(@class, 'product')]\n"
                "        //a[contains(@class, 'product-item-photo')]\n\n"
                
                "---\n"
                "### Example\n"
                "Input element:\n"
                "```html\n"
                "<input name=\"login[username]\" id=\"login\" title=\"Email or User ID\">\n"
                "```\n"
                "Return:\n"
                "{\"fixed_locators\": [\"//input[@id='login']\", \"//input[@name='login[username]']\", \"//input[@title='Email or User ID']\"]}\n"
            )
        })
        
        # Build user message content
        if use_vision:
            # Use vision API format with image
            # After cleaning, we can send more content since scripts/styles are removed
            user_content = [
                {
                    "type": "text",
                    "text": (
                        f"### Your Input Values:\n\n"
                        f"**IMPORTANT**: Look at the screenshot to visually identify the element described by `locator_name: {locator_name}`\n\n"
                        f"- locator_name: **{locator_name}**\n"
                        f"  (Find this element in the screenshot and generate XPath locators for it)\n\n"
                        f"- keyword: {keyword_name}\n"
                        f"  (The action being performed: {keyword_name})\n\n"
                        f"- failed_locator: {failed_locator}\n"
                        f"  (This locator failed - generate better alternatives)\n\n"
                        f"- page_source:\n```html\n{page_source[:20000]}\n```\n\n"
                        f"- element_context:\n```html\n{element_context}\n```\n"
                    )
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{screenshot_base64}",
                        "detail": "high"
                    }
                }
            ]
        else:
            # Text-only format - send more context for Angular Material apps
            # After cleaning HTML, we can send significantly more without hitting token limits
            page_source_excerpt = page_source[:30000]  # Increased from 15000 - cleaned HTML is much smaller
            
            # If element_context is just a placeholder, try to include more relevant HTML
            if "<element matching locator:" in element_context:
                # Element not found, but we can still provide more page context
                logger.info("Element not found in page source, sending larger page excerpt", also_console=True)
                page_source_excerpt = page_source[:50000]  # Even more context when element not found (cleaned HTML)
            
            user_content = (
                f"### Your Input Values:\n\n"
                f"- page_source:\n```html\n{page_source_excerpt}\n```\n\n"
                f"- element:\n```html\n{element_context}\n```\n\n"
                f"- locator_name: **{locator_name}**\n"
                f"  (This is the logical/descriptive name for the element being targeted. "
                f"Use it to understand the element's purpose and find matching attributes.)\n\n"
                f"- keyword: {keyword_name}\n"
                f"  (The action being performed on the element)\n\n"
                f"- failed_locator: {failed_locator}\n"
                f"  (The original locator that failed - analyze why it failed and generate better alternatives)\n\n"
            )
        
        messages.append({
            'role': 'user',
            'content': user_content
        })

        try:
            # Use vision model if screenshot is available, otherwise use standard model
            from .llm_client import VISUAL_AI_MODEL
            
            if use_vision:
                # Use VISUAL_AI_MODEL if set, otherwise try to select based on available API keys
                if VISUAL_AI_MODEL and VISUAL_AI_MODEL != "ollama_chat/llama3.2-vision":
                    model = VISUAL_AI_MODEL
                    logger.info(f"Using configured VISUAL_AI_MODEL: {model}", also_console=True)
                else:
                    # Auto-select vision model based on available API keys
                    if os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY'):
                        # Use gemini/ prefix to route through Google AI Studio (not Vertex AI)
                        model = 'gemini/gemini-1.5-flash'
                        logger.info(f"Google API key detected, using {model} for vision analysis", also_console=True)
                    elif os.getenv('ANTHROPIC_API_KEY'):
                        model = 'claude-3-5-sonnet-20241022'
                        logger.info(f"Anthropic API key detected, using {model} for vision analysis", also_console=True)
                    elif os.getenv('OPENAI_API_KEY'):
                        model = 'gpt-4o'
                        logger.info(f"OpenAI API key detected, using {model} for vision analysis", also_console=True)
                    else:
                        logger.warn(f"Vision enabled but no supported API key found (GOOGLE_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY). Using LOCATOR_AI_MODEL: {LOCATOR_AI_MODEL}")
                        model = LOCATOR_AI_MODEL
            else:
                model = LOCATOR_AI_MODEL
                logger.info(f"Using text-only model: {model}", also_console=True)
            
            # Save request to file for debugging
            output_dir = BuiltIn().get_variable_value('${OUTPUT_DIR}', '.')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            request_file = os.path.join(output_dir, f"llm_request_{timestamp}.json")
            
            # Prepare request data (mask screenshot for readability)
            request_data = {
                "timestamp": timestamp,
                "model": model,
                "use_vision": use_vision,
                "failed_locator": failed_locator,
                "locator_name": locator_name,
                "keyword_name": keyword_name,
                "page_source_length": len(page_source),
                "element_context_length": len(element_context),
                "screenshot_available": screenshot_base64 is not None,
                "screenshot_length": len(screenshot_base64) if screenshot_base64 else 0,
                "temperature": 0.1,
                "messages": []
            }
            
            # Add messages (truncate screenshot for file)
            for msg in messages:
                msg_copy = msg.copy()
                if isinstance(msg_copy.get('content'), list):
                    # Vision format - truncate image
                    content_copy = []
                    for item in msg_copy['content']:
                        if item.get('type') == 'image_url':
                            content_copy.append({
                                'type': 'image_url',
                                'image_url': {
                                    'url': f"data:image/png;base64,[TRUNCATED:{len(screenshot_base64)} chars]",
                                    'detail': 'high'
                                }
                            })
                        else:
                            content_copy.append(item)
                    msg_copy['content'] = content_copy
                request_data['messages'].append(msg_copy)
            
            # Save to file
            try:
                with open(request_file, 'w') as f:
                    json.dump(request_data, f, indent=2)
                logger.info(f"LLM request saved to: {request_file}", also_console=True)
            except Exception as e:
                logger.warn(f"Failed to save request to file: {e}")
            
            logger.info(f"Sending request to LLM model: {model}", also_console=True)
            logger.info(f"Request size: ~{len(json.dumps(request_data)) // 1024} KB (excluding full screenshot)", also_console=True)
            
            # Prepare completion kwargs
            completion_kwargs = {
                "debug_enabled": self.debug_llm,
                "model": model,
                "messages": messages,
                "temperature": 0.1,  # Low temperature for deterministic output
                "response_format": {"type": "json_object"} if not use_vision else None  # Some vision models don't support JSON mode
            }
            
            # Add API key explicitly for Gemini models to ensure proper routing
            if model.startswith('gemini/'):
                api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
                if api_key:
                    completion_kwargs['api_key'] = api_key
                    logger.info("Using GOOGLE_API_KEY for Gemini model", also_console=True)
            
            response = completion_with_debug(**completion_kwargs)
            
            logger.info("LLM response received successfully", also_console=True)
            solution_text = response['choices'][0]['message']['content']
            logger.info(f"Response length: {len(solution_text)} chars", also_console=True)
            logger.info(f"Response preview: {solution_text[:200]}...", also_console=True)
            
            # Save response to file (make non-JSON-serializable objects safe)
            response_file = os.path.join(output_dir, f"llm_response_{timestamp}.json")
            try:
                # Try to coerce usage field to a serializable form
                usage_val = response.get('usage', {})
                try:
                    if hasattr(usage_val, 'to_dict'):
                        usage_serializable = usage_val.to_dict()
                    elif hasattr(usage_val, '__dict__'):
                        usage_serializable = vars(usage_val)
                    else:
                        usage_serializable = usage_val
                except Exception:
                    usage_serializable = str(usage_val)

                response_data = {
                    "timestamp": timestamp,
                    "model": model,
                    "response_text": solution_text,
                    "response_metadata": {
                        "finish_reason": response['choices'][0].get('finish_reason'),
                        "usage": usage_serializable
                    }
                }

                # Use default=str to ensure any remaining non-serializable parts are stringified
                with open(response_file, 'w') as f:
                    json.dump(response_data, f, indent=2, default=str)
                logger.info(f"LLM response saved to: {response_file}", also_console=True)
            except Exception as e:
                # Fallback: try saving a plain string representation of the whole response
                try:
                    with open(response_file, 'w') as f:
                        f.write(str(response))
                    logger.info(f"LLM response saved as raw text to: {response_file}", also_console=True)
                except Exception as e2:
                    logger.info(f"Failed to save response to file: {e2}", also_console=True)
            
            solution_dict = list(extract_json_objects(solution_text))[0]
            
            if 'fixed_locators' in solution_dict:
                # Normalize locators to include xpath= prefix if not present
                locators = solution_dict['fixed_locators']
                normalized_locators = []
                for loc in locators:
                    if not loc.startswith('xpath=') and not loc.startswith('css='):
                        normalized_locators.append(f"xpath={loc}")
                    else:
                        normalized_locators.append(loc)
                logger.info(f"LLM generated {len(normalized_locators)} locator proposals: {normalized_locators}", also_console=True)
                logger.info("=" * 80, also_console=True)
                return normalized_locators
            else:
                logger.info("⚠ No 'fixed_locators' found in LLM response", also_console=True)
                logger.info("=" * 80, also_console=True)
                return []
        except Exception as e:
            import traceback
            logger.info(f"⚠ Error getting LLM proposals: {e}", also_console=True)
            logger.info(f"Full traceback:\n{traceback.format_exc()}", also_console=True)
            
            # Save error to file
            try:
                output_dir = BuiltIn().get_variable_value('${OUTPUT_DIR}', '.')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                error_file = os.path.join(output_dir, f"llm_error_{timestamp}.txt")
                with open(error_file, 'w') as f:
                    f.write(f"Error: {e}\n\n")
                    f.write(f"Traceback:\n{traceback.format_exc()}\n\n")
                    f.write(f"Failed locator: {failed_locator}\n")
                    f.write(f"Locator name: {locator_name}\n")
                    f.write(f"Use vision: {use_vision}\n")
                logger.info(f"Error details saved to: {error_file}", also_console=True)
            except:
                pass
            
            logger.info("=" * 80, also_console=True)
        
        return []
    
    def _capture_screenshot_as_base64(self) -> str:
        """Capture current page screenshot and return as base64 string for LLM vision analysis"""
        try:
            import base64
            import tempfile
            import os
            
            # Create temporary file for screenshot
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                # Capture screenshot using SeleniumLibrary
                BuiltIn().run_keyword("SeleniumLibrary.Capture Page Screenshot", tmp_path)
                
                # Read and encode as base64
                with open(tmp_path, 'rb') as image_file:
                    screenshot_data = image_file.read()
                    screenshot_base64 = base64.b64encode(screenshot_data).decode('utf-8')
                
                logger.info(f"Screenshot captured for vision analysis (size: {len(screenshot_data)} bytes)", also_console=True)
                return screenshot_base64
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            logger.warn(f"Failed to capture screenshot for vision analysis: {e}")
            return None
    
    def _extract_element_context(self, failed_locator, soup) -> str:
        """Extract HTML context for the failed locator to help LLM understand the element"""
        try:
            # Remove xpath= or css= prefix
            locator = failed_locator
            if locator.startswith('xpath='):
                locator = locator[6:]
            elif locator.startswith('css='):
                locator = locator[4:]
            
            # Try to find similar elements in the soup
            # This is a best-effort attempt to provide context
            # Look for elements with similar attributes
            
            # For id= locator format
            if locator.startswith('id='):
                id_value = locator[3:]
                elem = soup.find(id=id_value)
                if elem:
                    logger.info(f"Found element by id={id_value}", also_console=True)
                    return str(elem)[:1000]
                else:
                    # Try partial match - Angular Material often has similar IDs
                    # e.g., mat-option-84, mat-option-85, etc.
                    base_id = re.sub(r'\d+$', '', id_value)  # Remove trailing numbers
                    logger.info(f"Element id={id_value} not found, searching for similar elements with base: {base_id}", also_console=True)
                    
                    # Find any elements with IDs starting with the base
                    similar_elements = soup.find_all(id=re.compile(f'^{re.escape(base_id)}'))
                    if similar_elements:
                        logger.info(f"Found {len(similar_elements)} similar elements with base id={base_id}", also_console=True)
                        # Return the first similar element as context
                        return str(similar_elements[0])[:1000]
            
            # For XPath with @id
            if '@id' in locator:
                id_match = re.search(r"@id\s*=\s*['\"]([^'\"]+)['\"]", locator)
                if id_match:
                    id_value = id_match.group(1)
                    elem = soup.find(id=id_value)
                    if elem:
                        logger.info(f"Found element by xpath @id={id_value}", also_console=True)
                        return str(elem)[:1000]
            
            # For name= locator format
            if locator.startswith('name='):
                name_value = locator[5:]
                elem = soup.find(attrs={'name': name_value})
                if elem:
                    logger.info(f"Found element by name={name_value}", also_console=True)
                    return str(elem)[:1000]
            
            # For XPath with @name
            if '@name' in locator:
                name_match = re.search(r"@name\s*=\s*['\"]([^'\"]+)['\"]", locator)
                if name_match:
                    name_value = name_match.group(1)
                    elem = soup.find(attrs={'name': name_value})
                    if elem:
                        logger.info(f"Found element by xpath @name={name_value}", also_console=True)
                        return str(elem)[:1000]
            
            # If we can't find specific element, return a generic placeholder
            logger.info(f"⚠ Could not find element matching locator: {failed_locator}", also_console=True)
            return f"<element matching locator: {failed_locator}>"
        except Exception as e:
            logger.debug(f"Error extracting element context: {e}")
            return f"<element matching locator: {failed_locator}>"
    
    def _extract_logical_name_from_variable(self, variable_string: str) -> str:
        """Extract logical element name from Robot Framework variable
        
        Examples:
            ${corporate_event_page.dropdown_search_by_category} -> dropdown_search_by_category
            ${page.btn_submit} -> btn_submit
            id=mat-select-0 -> mat-select-0
        """
        try:
            # Check if it's a Robot Framework variable (${...})
            if variable_string.startswith('${') and '}' in variable_string:
                # Extract variable content
                var_content = variable_string[2:variable_string.rfind('}')]
                
                # Check if it's a dictionary access (e.g., dict.key)
                if '.' in var_content:
                    # Return the key part after the last dot
                    return var_content.split('.')[-1]
                else:
                    # Return the variable name
                    return var_content
            
            # If it's not a variable, try to extract something meaningful from the locator itself
            return self._derive_locator_name(variable_string, "")
        except Exception as e:
            logger.debug(f"Error extracting logical name from variable: {e}")
            return "element_target"

    def _derive_locator_name(self, failed_locator, keyword_name) -> str:
        """Derive a meaningful locator name from the failed locator and keyword"""
        try:
            # Extract meaningful parts from the locator
            locator = failed_locator.lower()
            
            # Remove prefixes
            for prefix in ['xpath=', 'css=', 'id=', '//', '.']:
                if locator.startswith(prefix):
                    locator = locator[len(prefix):]
            
            # Extract id, name, or class if present
            if '@id' in locator:
                id_match = re.search(r"@id='([^']+)'", locator)
                if id_match:
                    return id_match.group(1)
            
            if '@name' in locator:
                name_match = re.search(r"@name='([^']+)'", locator)
                if name_match:
                    return name_match.group(1)
            
            # Derive from keyword
            keyword_lower = keyword_name.lower()
            if 'click' in keyword_lower:
                return 'btn_target'
            elif 'input' in keyword_lower or 'text' in keyword_lower:
                return 'txt_input'
            elif 'select' in keyword_lower:
                return 'sel_dropdown'
            elif 'checkbox' in keyword_lower:
                return 'chk_checkbox'
            else:
                return 'element_target'
        except Exception as e:
            logger.debug(f"Error deriving locator name: {e}")
            return 'element_target'

    def get_locator_proposals_from_parser(self, data, result, soup) -> list:
        """Parse page source to generate locator proposals"""
        keyword_name = data.name
        locators = []
        
        # Determine element types based on keyword
        element_types = []
        keyword_lower = keyword_name.lower()
        
        if any(kw in keyword_lower for kw in ['click', 'button']):
            element_types = ['button', 'a', 'input']
        elif any(kw in keyword_lower for kw in ['input', 'type', 'text']):
            element_types = ['input', 'textarea']
        elif any(kw in keyword_lower for kw in ['select', 'dropdown']):
            element_types = ['select']
        elif any(kw in keyword_lower for kw in ['checkbox']):
            element_types = ['input']
        else:
            element_types = ['button', 'a', 'input', 'div', 'span']
        
        # Generate locators for matching elements
        for elem_type in element_types:
            elements = soup.find_all(elem_type)
            for elem in elements[:10]:  # Limit to first 10 of each type
                # Generate CSS selector
                css_selector = generate_unique_css_selector(elem, soup)
                if css_selector:
                    locators.append(f"css={css_selector}")
                
                # Generate XPath
                xpath = generate_unique_xpath_selector(elem, soup)
                if xpath:
                    locators.append(f"xpath={xpath}")
        
        return locators[:20]  # Return top 20 candidates

    def rerun_keyword(self, data, fixed_locator=None) -> str:
        """Rerun the failed keyword with the fixed locator"""
        if fixed_locator:
            data.args = list(data.args)
            data.args[0] = fixed_locator
        try:
            logger.info(f"Re-trying Keyword '{data.name}' with arguments '{data.args}'.", also_console=True)
            return_value = BuiltIn().run_keyword(data.name, *data.args)
            BuiltIn().run_keyword("SeleniumLibrary.Capture Page Screenshot")
            return return_value
        except Exception as e:
            logger.debug(f"Unexpected error: {e}")
            raise

    def get_element_count_for_locator(self, locator) -> int:
        """Get the count of elements matching the locator"""
        try:
            count = BuiltIn().run_keyword("SeleniumLibrary.Get Element Count", locator)
            return int(count)
        except Exception as e:
            logger.debug(f"Error getting element count: {e}")
            return 0

    def has_locator(self, result) -> bool:
        """Check if the keyword result contains a locator argument"""
        # Keywords that use locators typically have them as first argument
        locator_keywords = [
            'Click Element', 'Input Text', 'Select From List', 'Get Text',
            'Wait Until Element Is Visible', 'Element Should Be Visible',
            'Click Button', 'Click Link', 'Input Password', 'Select Checkbox',
            'Unselect Checkbox', 'Get Element Attribute', 'Element Should Contain'
        ]
        return any(kw in result.name for kw in locator_keywords)

    def get_locator_info(self, locator):
        """Get detailed information about a locator"""
        locator_info = {}
        locator_info["locator"] = locator
        
        try:
            # Get element attributes
            tag_name = BuiltIn().run_keyword("SeleniumLibrary.Get Element Attribute", locator, "tagName")
            locator_info["tagName"] = tag_name
            
            # Try to get text
            try:
                text = BuiltIn().run_keyword("SeleniumLibrary.Get Text", locator)
                if text:
                    locator_info["text"] = text
            except:
                pass
            
            # Try to get common attributes
            for attr in ['id', 'class', 'name', 'type', 'value', 'placeholder', 'role']:
                try:
                    value = BuiltIn().run_keyword("SeleniumLibrary.Get Element Attribute", locator, attr)
                    if value:
                        locator_info[attr] = value
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"Error getting locator info: {e}")
        
        return locator_info

    def get_attribute_value(self, locator, attribute):
        """Get an attribute value from an element"""
        try:
            return BuiltIn().run_keyword("SeleniumLibrary.Get Element Attribute", locator, attribute)
        except:
            return None

    def get_property_value(self, locator, property_name):
        """Get a property value from an element using JavaScript"""
        try:
            script = f"return arguments[0].{property_name};"
            element = BuiltIn().run_keyword("SeleniumLibrary.Get WebElement", locator)
            return self.selenium.execute_javascript(script, element)
        except:
            return None
