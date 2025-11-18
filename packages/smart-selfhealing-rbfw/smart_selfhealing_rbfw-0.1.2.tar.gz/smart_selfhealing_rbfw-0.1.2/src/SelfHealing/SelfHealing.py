"""
A Listener Library for Self Healing Browser.
Connects to the instance of the Browser Library.
Starts interaction with end_keyword and end_test listeners.
"""

from robot.api import logger
import re
import json
import atexit
from .browser_healing import BrowserHealer
from .appium_healing import AppiumHealer
from .selenium_healing import SeleniumHealer
from .visual_healing import VisualHealer
from robot.libraries.BuiltIn import BuiltIn
from .utils import extract_json_objects
from .locator_db import LocatorDetailsDB

try:
    from Browser.utils.data_types import ScreenshotReturnType
except ImportError:
    _has_browser = False
else:
    _has_browser = True


duplicate_test_pattern = re.compile(
    r"Multiple .*? with name '(?P<test>.*?)' executed in.*? suite '(?P<suite>.*?)'."
)

skip_parent_keywords = [
    "Run Keyword And Return Status",
    "Run Keyword And Expect Error",
    "Run Keyword And Ignore Error",
    "Run Keyword And Continue On Failure"
    ]

class SelfHealing:
    ROBOT_LIBRARY_SCOPE = 'SUITE'
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, collect_locator_info = False, ai_locator_database = False, ai_locator_llm = True, ai_locator_visual = False, heal_assertions = False, ai_locator_database_file = "locator_db.json"):
        self.ROBOT_LIBRARY_LISTENER = self
        self.fixed_locators = {}
        self.updated_locators = {}
        self.greedy_fix = True
        self.collect_locator_info = collect_locator_info
        self.use_locator_db = ai_locator_database
        self.use_llm_for_locator_proposals = ai_locator_llm
        self.use_llm_with_vision = ai_locator_visual
        self.heal_assertions = heal_assertions
        self._is_healing = False  # Flag to track if we're in healing process
        self._report_injected = False  # Flag to prevent duplicate injection
        self._output_path = None  # Store output path for atexit handler
        
        # Fix mode is always realtime (not exposed as parameter)
        self.fix_realtime = True
        self.fix_retry = False
        
        # Debug flag for logging LLM requests/responses (internal only, not exposed to users)
        import os
        self.debug_llm = os.getenv('SELFHEALING_DEBUG', 'false').lower() == 'true'
        
        # Validate LLM configuration if AI locator features are enabled
        if ai_locator_llm or ai_locator_visual:
            self._validate_llm_configuration()
        self.locator_info = {}
        try:
            # Use OUTPUT_DIR if available, otherwise use provided path
            try:
                output_dir = BuiltIn().get_variable_value("${OUTPUT_DIR}")
                if output_dir and not ai_locator_database_file.startswith("/"):
                    import os
                    ai_locator_database_file = os.path.join(output_dir, ai_locator_database_file)
            except:
                pass  # OUTPUT_DIR not available, use provided path as-is
            self.locator_db = LocatorDetailsDB(ai_locator_database_file).db
        except:
            pass
        
        # Register atexit handler to inject button after Robot Framework finishes
        atexit.register(self._inject_button_at_exit)

    def _validate_llm_configuration(self):
        """Validate that required LLM environment variables are set."""
        import os
        
        missing_configs = []
        warnings = []
        
        # Check for API keys from various AI providers
        # litellm supports many providers, check common ones
        api_keys = {
            'OpenAI': os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY'),
            'Google/Gemini': os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY'),
            'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'Azure': os.getenv('AZURE_API_KEY'),
            'Cohere': os.getenv('COHERE_API_KEY'),
            'Mistral': os.getenv('MISTRAL_API_KEY'),
            'Groq': os.getenv('GROQ_API_KEY'),
            'Together': os.getenv('TOGETHER_API_KEY'),
        }
        
        # Check if at least one API key is set
        has_api_key = any(api_keys.values())
        
        if not has_api_key:
            missing_configs.append('API Key (OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, etc.)')
            warnings.append("⚠️ No AI provider API key found")
        
        # Check for locator model (REQUIRED for ai_locator_llm)
        locator_model = os.getenv('LOCATOR_AI_MODEL')
        if not locator_model and self.use_llm_for_locator_proposals:
            missing_configs.append('LOCATOR_AI_MODEL')
            warnings.append("⚠️ LOCATOR_AI_MODEL environment variable is not set (required for AI locator healing)")
        
        # Log warnings if any configuration is missing
        if missing_configs:
            # Determine which API key instruction to show
            if not has_api_key:
                api_key_instruction = (
                    "  # For OpenAI:\n"
                    "  export OPENAI_API_KEY=your-openai-api-key-here\n"
                    "  # OR for Google Gemini:\n"
                    "  export GOOGLE_API_KEY=your-google-gemini-api-key-here\n"
                    "  # OR for Anthropic Claude:\n"
                    "  export ANTHROPIC_API_KEY=your-anthropic-api-key-here\n"
                    "  # OR for Azure OpenAI:\n"
                    "  export AZURE_API_KEY=your-azure-api-key-here\n"
                    "  # OR for other providers (Cohere, Mistral, Groq, Together, etc.):\n"
                    "  export <PROVIDER>_API_KEY=your-api-key-here\n"
                )
            else:
                api_key_instruction = ""
            
            warning_message = (
                "\n" + "="*80 + "\n"
                "⚠️  SELF-HEALING LLM CONFIGURATION WARNING\n"
                + "="*80 + "\n"
                + "The following required environment variables are not set:\n"
                + "\n".join(f"  • {config}" for config in missing_configs)
                + "\n\n"
                + "AI-powered locator healing may not work correctly.\n"
                + "Please set these environment variables:\n\n"
                + api_key_instruction
            )
            
            if not locator_model:
                warning_message += "  export LOCATOR_AI_MODEL=gpt-4o-mini  # or gemini/gemini-1.5-flash\n"
            
            if self.use_llm_with_vision:
                warning_message += "  export VISUAL_AI_MODEL=gpt-4o  # or gemini/gemini-1.5-pro (requires vision support)\n"
            
            warning_message += "\nFor more information, see the documentation.\n" + "="*80 + "\n"
            
            # Log to Robot Framework log
            logger.warn(warning_message, html=False)
            
            # Also print to console for visibility
            print(warning_message)

    def _start_library_keyword(self, data, implementation, result):
        if self.greedy_fix and data.args:
            data.args = list(data.args)
            if result.owner == 'Browser':
                if self.fixed_locators.get(data.args[0]):
                    healer = BrowserHealer(implementation.owner.instance, use_llm_for_locator_proposals = self.use_llm_for_locator_proposals, use_llm_with_vision = self.use_llm_with_vision, debug_llm = self.debug_llm)            
                    if healer.get_element_count_for_locator(data.args[0]) == 0:
                        broken_locator = data.args[0]
                        fixed_locator = self.fixed_locators.get(data.args[0])
                        if healer.get_element_count_for_locator(fixed_locator) != 0:
                            data.args[0] = fixed_locator
                            result.args = data.args
                            logger.info(f"Updated Keyword Argument with new selector {data.args[0]}", also_console=True)
                            self.updated_locators[f"{result.id}"] = {"keyword_name": result.name, "lineno": data.lineno, "source": data.source, "fixed_locator": fixed_locator, "test_name": BuiltIn().replace_variables("${TEST NAME}"), "suite_name": BuiltIn().replace_variables("${SUITE NAME}"), "broken_locator": broken_locator, "screenshot": None}
            elif result.owner == 'SeleniumLibrary':
                if self.fixed_locators.get(data.args[0]):
                    healer = SeleniumHealer(implementation.owner.instance, use_llm_for_locator_proposals = self.use_llm_for_locator_proposals, use_llm_with_vision = self.use_llm_with_vision, debug_llm = self.debug_llm)
                    if healer.get_element_count_for_locator(data.args[0]) == 0:
                        broken_locator = data.args[0]
                        fixed_locator = self.fixed_locators.get(data.args[0])
                        if healer.get_element_count_for_locator(fixed_locator) != 0:
                            data.args[0] = fixed_locator
                            result.args = data.args
                            logger.info(f"Updated Keyword Argument with new selector {data.args[0]}", also_console=True)
                            self.updated_locators[f"{result.id}"] = {"keyword_name": result.name, "lineno": data.lineno, "source": data.source, "fixed_locator": fixed_locator, "test_name": BuiltIn().replace_variables("${TEST NAME}"), "suite_name": BuiltIn().replace_variables("${SUITE NAME}"), "broken_locator": broken_locator, "screenshot": None}
        if result.owner == 'Browser' and self.collect_locator_info:
            self.locator_info = {}
            healer = BrowserHealer(implementation.owner.instance, use_llm_for_locator_proposals = self.use_llm_for_locator_proposals, use_llm_with_vision = self.use_llm_with_vision, debug_llm = self.debug_llm)
            if healer.has_locator(result):
                locator = BuiltIn().replace_variables(str(data.args[0]))
                self.locator_info = healer.get_locator_info(locator)
        elif result.owner == 'SeleniumLibrary' and self.collect_locator_info:
            self.locator_info = {}
            healer = SeleniumHealer(implementation.owner.instance, use_llm_for_locator_proposals = self.use_llm_for_locator_proposals, use_llm_with_vision = self.use_llm_with_vision, debug_llm = self.debug_llm)
            if healer.has_locator(result):
                locator = BuiltIn().replace_variables(str(data.args[0]))
                self.locator_info = healer.get_locator_info(locator)

    def _end_library_keyword(self, data, implementation, result):
        # Skip if we're in the middle of healing validation
        if self._is_healing:
            return
            
        # Check if Keyword belongs to Browser Library
        if result.owner == 'Browser' and result.failed and data.parent.name not in skip_parent_keywords:
            browser = implementation.owner.instance
            logger.info(f"Keyword '{result.full_name}' with arguments '{BuiltIn().replace_variables(data.args)}' used on line {data.lineno} failed.", also_console=True)
            healer = BrowserHealer(implementation.owner.instance, use_llm_for_locator_proposals = self.use_llm_for_locator_proposals, debug_llm = self.debug_llm)
            if healer.is_locator_broken(result.message):
                broken_locator = BuiltIn().replace_variables(data.args[0])
                self._is_healing = True  # Set flag before healing
                try:
                    fixed_locator = healer.get_fixed_locator(data, result)
                finally:
                    self._is_healing = False  # Reset flag after healing
                if self.fix_realtime:
                    if fixed_locator:
                        try:
                            # Capture screenshot BEFORE rerunning keyword (page may navigate)
                            screenshot_path = self._capture_screenshot_for_locator(fixed_locator, 'Browser')
                            
                            # Now rerun the keyword
                            return_value = healer.rerun_keyword(data, fixed_locator)
                            if return_value and result.assign:
                                BuiltIn().set_local_variable(result.assign[0], return_value)
                            self.fixed_locators[broken_locator] = fixed_locator
                            
                            self.updated_locators[f"{result.id}"] = {
                                "keyword_name": result.name, 
                                "lineno": data.lineno, 
                                "source": data.source, 
                                "fixed_locator": fixed_locator, 
                                "test_name": BuiltIn().replace_variables("${TEST NAME}"), 
                                "suite_name": BuiltIn().replace_variables("${SUITE NAME}"), 
                                "broken_locator": broken_locator,
                                "screenshot": screenshot_path
                            }
                            result.status = "PASS"
                            return return_value
                        except:
                            raise
            elif healer.is_element_not_ready(result.message):
                logger.info(f"SelfHealing: Element was not ready")
                if healer.is_modal_dialog_open():
                    healer.close_modal_dialog()
                    try:
                        # Rerun original step again
                        return_value = healer.rerun_keyword(data)
                        if return_value and result.assign:
                            BuiltIn().set_local_variable(result.assign[0], return_value)
                        result.status = "PASS"
                        return return_value
                    except:
                        raise
                elif healer.is_page_loading:
                    logger.info(f"Element was not ready as Page was readyState was not Complete.")
                    healer.wait_until_page_is_ready()
                    try:
                        # Rerun original step again
                        return_value = healer.rerun_keyword(data)
                        if return_value and result.assign:
                            BuiltIn().set_local_variable(result.assign[0], return_value)
                        result.status = "PASS"
                        return return_value
                    except:
                        raise
                else:
                    try:
                        import pyautogui
                        pyautogui.press('esc')
                        try:
                            # Rerun original step again
                            return_value = healer.rerun_keyword(data)
                            if return_value and result.assign:
                                BuiltIn().set_local_variable(result.assign[0], return_value)
                            result.status = "PASS"
                            return return_value
                        except:
                            raise
                    except:
                        logger.error("Cannot use pyautogui in HEADLESS mode")
            elif self.heal_assertions:
                screenshot_base64 = browser.take_screenshot(fullPage=True, log_screenshot=False, return_as=ScreenshotReturnType.base64)
                visual_healer = VisualHealer(instance=implementation.owner.instance, debug_llm=self.debug_llm)
                explanation = visual_healer.get_error_explanation(data, result, screenshot_base64)
                logger.info(explanation,  also_console=True)
                if "*Adjustment*" in explanation:
                    kw_list =  list(extract_json_objects(explanation))
                    if len(kw_list) > 0:
                        new_kw = kw_list[0]["keyword_name"]
                        if "args" in kw_list[0]:
                            new_args = list(kw_list[0]["args"])
                        elif "arguments" in kw_list[0]:
                            new_args = list(kw_list[0]["arguments"])
                        else:
                            new_args = []
                        new_args = [x.strip() for x in new_args]
                        try:
                            value = BuiltIn().run_keyword(new_kw, *new_args)                    
                            result.status = "PASS"
                            return value
                        except Exception as e:
                            logger.info(e)
                            result.status = "FAIL"                            
        if result.owner == 'Browser' and result.passed and self.collect_locator_info and self.locator_info:
                self._store_successful_locator_info(self.locator_info)
        if result.owner == 'SeleniumLibrary' and result.passed and self.collect_locator_info and self.locator_info:
                self._store_successful_locator_info(self.locator_info)
        if result.owner == 'SeleniumLibrary' and result.failed and data.parent.name not in skip_parent_keywords:
            selenium = implementation.owner.instance
            logger.info(f"Keyword '{result.full_name}' with arguments '{BuiltIn().replace_variables(data.args)}' used on line {data.lineno} failed.", also_console=True)
            healer = SeleniumHealer(implementation.owner.instance, use_llm_for_locator_proposals = self.use_llm_for_locator_proposals, use_llm_with_vision = self.use_llm_with_vision, debug_llm = self.debug_llm)
            logger.info(f"Checking if locator is broken. Message: '{result.message}'", also_console=True)
            logger.info(f"is_locator_broken result: {healer.is_locator_broken(result.message)}", also_console=True)
            if healer.is_locator_broken(result.message):
                self._is_healing = True  # Set flag before healing
                fixed_locator = None  # Initialize to None
                try:
                    broken_locator = BuiltIn().replace_variables(data.args[0])
                    logger.info(f"Attempting to fix broken locator: {broken_locator}", also_console=True)
                    fixed_locator = healer.get_fixed_locator(data, result)
                    logger.info(f"Fixed locator result: {fixed_locator}", also_console=True)
                except Exception as e:
                    logger.error(f"Error during healing process: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    raise
                finally:
                    self._is_healing = False  # Reset flag after healing
                
                logger.info(f"fix_realtime={self.fix_realtime}, fixed_locator={fixed_locator}", also_console=True)
                if self.fix_realtime:
                    logger.info("Entering fix_realtime block", also_console=True)
                    if fixed_locator:
                        logger.info(f"Fixed locator is valid, will retry with: {fixed_locator}", also_console=True)
                        try:
                            # Capture screenshot BEFORE rerunning keyword (page may navigate)
                            screenshot_path = self._capture_screenshot_for_locator(fixed_locator, 'SeleniumLibrary')
                            
                            # Now rerun the keyword
                            return_value = healer.rerun_keyword(data, fixed_locator)
                            if return_value and result.assign:
                                BuiltIn().set_local_variable(result.assign[0], return_value)
                            self.fixed_locators[broken_locator] = fixed_locator
                            
                            self.updated_locators[f"{result.id}"] = {
                                "keyword_name": result.name, 
                                "lineno": data.lineno, 
                                "source": data.source, 
                                "fixed_locator": fixed_locator, 
                                "test_name": BuiltIn().replace_variables("${TEST NAME}"), 
                                "suite_name": BuiltIn().replace_variables("${SUITE NAME}"), 
                                "broken_locator": broken_locator,
                                "screenshot": screenshot_path
                            }
                            result.status = "PASS"
                            return return_value
                        except:
                            raise
            elif healer.is_element_not_ready(result.message):
                logger.info(f"SelfHealing: Element was not ready")
                if healer.is_modal_dialog_open():
                    healer.close_modal_dialog()
                    try:
                        # Rerun original step again
                        return_value = healer.rerun_keyword(data)
                        if return_value and result.assign:
                            BuiltIn().set_local_variable(result.assign[0], return_value)
                        result.status = "PASS"
                        return return_value
                    except:
                        raise
                elif healer.is_page_loading():
                    logger.info(f"Element was not ready as Page readyState was not Complete.")
                    healer.wait_until_page_is_ready()
                    try:
                        # Rerun original step again
                        return_value = healer.rerun_keyword(data)
                        if return_value and result.assign:
                            BuiltIn().set_local_variable(result.assign[0], return_value)
                        result.status = "PASS"
                        return return_value
                    except:
                        raise
        if result.owner == 'AppiumLibrary' and result.failed:
            appium = implementation.owner.instance
            logger.info(f"Keyword '{result.full_name}' with arguments '{BuiltIn().replace_variables(data.args)}' used on line {data.lineno} failed.", also_console=True)
            healer = AppiumHealer(implementation.owner.instance, use_llm_for_locator_proposals = self.use_llm_for_locator_proposals)
            if healer.is_modal_dialog_open():
                logger.info(f"Modal dialog was open", also_console=True)
                healer.close_modal_dialog()
                # Rerun original step again
                BuiltIn().run_keyword("AppiumLibrary.Wait Until Element Is Visible", data.args[0])
                status = healer.rerun_keyword(data)
                result.status = status          
            elif healer.is_locator_broken(result.message):
                broken_locator = BuiltIn().replace_variables(data.args[0])
                self._is_healing = True  # Set flag before healing
                try:
                    fixed_locator = healer.get_fixed_locator(data, result)
                finally:
                    self._is_healing = False  # Reset flag after healing
                if self.fix_realtime:
                    if fixed_locator:
                        if healer.is_element_visible_with_swiping(fixed_locator):
                            # Capture screenshot BEFORE rerunning keyword
                            screenshot_path = self._capture_screenshot_for_locator(fixed_locator, 'Appium')
                            
                            # Now rerun the keyword
                            status = healer.rerun_keyword(data, fixed_locator)
                            result.status = status
                            if result.status == "PASS":
                                self.fixed_locators[broken_locator] = fixed_locator
                                
                                self.updated_locators[f"{result.id}"] = {
                                    "keyword_name": result.name, 
                                    "lineno": data.lineno, 
                                    "source": data.source, 
                                    "fixed_locator": fixed_locator, 
                                    "test_name": BuiltIn().replace_variables("${TEST NAME}"), 
                                    "suite_name": BuiltIn().replace_variables("${SUITE NAME}"), 
                                    "broken_locator": broken_locator,
                                    "screenshot": screenshot_path
                                } 

    def _calculate_statistics(self, data):
        """Calculate statistics for the report"""
        from collections import Counter
        
        # Count fixes by keyword
        keyword_counts = Counter(item['keyword_name'] for item in data)
        
        # Count fixes by suite
        suite_counts = Counter(item['suite_name'] for item in data)
        
        # Count unique tests and suites
        unique_tests = len(set(item['test_name'] for item in data))
        unique_suites = len(set(item['suite_name'] for item in data))
        
        return {
            'keyword_counts': dict(keyword_counts),
            'suite_counts': dict(suite_counts),
            'unique_tests': unique_tests,
            'unique_suites': unique_suites,
            'total_fixes': len(data)
        }

    def close(self):
        logger.info("="*50, also_console=True)
        logger.info("CLOSE METHOD CALLED - Generating Self-Healing Report", also_console=True)
        logger.info(f"Updated locators count: {len(self.updated_locators)}", also_console=True)
        logger.info("="*50, also_console=True)
        
        from jinja2 import Environment, FileSystemLoader
        import os

        output_path = BuiltIn().replace_variables("${OUTPUT DIR}")
        self._output_path = output_path  # Store for atexit handler
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set up the Jinja2 environment
        env = Environment(loader=FileSystemLoader(current_dir))
        
        # Add custom dirname filter
        env.filters['dirname'] = os.path.dirname
        
        template = env.get_template('template_new.html')

        data = [value for key, value in self.updated_locators.items()]
        
        # Convert any Path objects to strings for JSON serialization
        json_data = []
        for item in data:
            json_item = {}
            for k, v in item.items():
                if hasattr(v, '__fspath__'):  # Check if it's a path-like object
                    json_item[k] = str(v)
                else:
                    json_item[k] = v
            json_data.append(json_item)
        
        # Calculate statistics
        stats = self._calculate_statistics(data)
        
        # Render the template with data and stats
        output = template.render(data=data, stats=stats)

        # Save the rendered HTML to a file
        with open(os.path.join(output_path, "fixed_locators.html"), 'w') as f:
            f.write(output)
        
        # Also save as JSON for automation
        with open(os.path.join(output_path, "fixed_locators.json"), 'w') as f:
            json.dump(json_data, f, indent=2)
        
        logger.info(f"Fixed locators saved to: {os.path.join(output_path, 'fixed_locators.html')}", also_console=True)
        logger.info(f"Fixed locators JSON saved to: {os.path.join(output_path, 'fixed_locators.json')}", also_console=True)
        
        # Inject link into report.html and log.html
        if len(data) > 0:
            self._inject_link_to_report(output_path, len(data))

    def end_suite(self, data, result):
        """Called when a test suite ends - triggers the report generation"""
        logger.info(f"end_suite called for: {data.name}, parent: {data.parent}", also_console=True)
        # Only generate report at the top-level suite end
        if data.parent is None:
            logger.info("Calling close() to generate self-healing report...", also_console=True)
            self.close()
        else:
            logger.info("Not top-level suite, skipping report generation", also_console=True)

    def _inject_button_at_exit(self):
        """Called via atexit to inject button after Robot Framework finishes writing files"""
        if self._report_injected or len(self.updated_locators) == 0 or not self._output_path:
            return
        
        import time
        import os
        
        # Wait for Robot Framework to finish writing files
        time.sleep(2)
        
        try:
            logger.info(f"Atexit: Injecting button into {self._output_path}", also_console=True)
            self._inject_link_to_report(self._output_path, len(self.updated_locators))
            self._report_injected = True
            logger.info("Atexit: Button injection completed", also_console=True)
        except Exception as e:
            # Last resort: try finding the files
            try:
                if os.path.exists(os.path.join(self._output_path, 'log.html')):
                    self._inject_link_to_report(self._output_path, len(self.updated_locators))
                    self._report_injected = True
            except:
                pass

    def _inject_link_to_report(self, output_path, locator_count):
        """Inject a link to fixed_locators.html in the Robot Framework report.html and log.html"""
        import os
        import time
        
        # Create the link HTML matching Robot Framework's REPORT/LOG button style
        link_html = f'''
    <style>
    #self-healing-link {{
        position: fixed;
        top: 0;
        right: 12em;
        z-index: 1000;
        width: 12em;
        text-align: center;
    }}
    #self-healing-link a {{
        display: block;
        background: #1155cc;
        color: white;
        text-decoration: none;
        font-weight: bold;
        letter-spacing: 0.1em;
        padding: 0.3em 0;
        border-bottom-left-radius: 4px;
        font-family: Helvetica, sans-serif;
    }}
    #self-healing-link a:hover {{
        color: #ddd;
    }}
    </style>
    <div id="self-healing-link">
        <a href="fixed_locators.html" target="_blank">
            SELF HEALING<br>({locator_count} Fixed Locators)
        </a>
    </div>
'''
        
        # Wait briefly for Robot Framework to finish writing files
        time.sleep(1)
        
        # Inject into both report.html and log.html
        for filename in ['report.html', 'log.html']:
            file_path = os.path.join(output_path, filename)
            
            # Retry logic to wait for file to be available
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                if not os.path.exists(file_path):
                    logger.debug(f"{filename} not found yet, waiting... (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(0.5)
                    retry_count += 1
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if link already exists
                    if 'fixed_locators.html' in content:
                        logger.debug(f"Self-healing link already exists in {filename}")
                        break
                    
                    # Inject before closing body tag
                    if '</body>' in content:
                        content = content.replace('</body>', link_html + '\n</body>')
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        logger.info(f"✓ Self-healing link added to {filename}", also_console=True)
                        break
                    else:
                        logger.debug(f"Could not find </body> tag in {filename} (attempt {retry_count + 1}/{max_retries})")
                        time.sleep(0.5)
                        retry_count += 1
                        
                except Exception as e:
                    logger.debug(f"Error injecting link to {filename}: {e} (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(0.5)
                    retry_count += 1

    def _highlight_element(self, locator, library_type='SeleniumLibrary') -> str:
        """Highlight the element with a red border and return the highlight ID"""
        try:
            highlight_script = """
            (function(element) {
                if (!element) return null;
                
                // Store original style
                var originalBorder = element.style.border;
                var originalOutline = element.style.outline;
                var originalBoxShadow = element.style.boxShadow;
                var originalZIndex = element.style.zIndex;
                
                // Apply highlight
                element.style.border = '3px solid #FF0000';
                element.style.outline = '3px solid #FFFF00';
                element.style.boxShadow = '0 0 20px 5px rgba(255, 0, 0, 0.8), inset 0 0 20px 5px rgba(255, 255, 0, 0.6)';
                element.style.zIndex = '999999';
                
                // Scroll element into view
                element.scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});
                
                // Store original styles as data attributes
                element.setAttribute('data-original-border', originalBorder);
                element.setAttribute('data-original-outline', originalOutline);
                element.setAttribute('data-original-boxshadow', originalBoxShadow);
                element.setAttribute('data-original-zindex', originalZIndex);
                element.setAttribute('data-highlighted', 'true');
                
                return 'highlighted';
            })(arguments[0]);
            """
            
            if library_type == 'SeleniumLibrary':
                # Temporarily reduce log level to avoid verbose JavaScript in report
                old_log_level = BuiltIn().set_log_level("WARN")
                try:
                    element = BuiltIn().run_keyword("SeleniumLibrary.Get WebElement", locator)
                    result = BuiltIn().run_keyword("SeleniumLibrary.Execute Javascript", highlight_script, "ARGUMENTS", element)
                finally:
                    BuiltIn().set_log_level(old_log_level)
            elif library_type == 'Browser':
                # Browser library uses different approach
                highlight_js = f"""
                const element = document.querySelector('{locator.replace("css=", "").replace("xpath=", "")}');
                if (element) {{
                    element.style.border = '3px solid #FF0000';
                    element.style.outline = '3px solid #FFFF00';
                    element.style.boxShadow = '0 0 20px 5px rgba(255, 0, 0, 0.8)';
                    element.style.zIndex = '999999';
                    element.scrollIntoView({{behavior: 'instant', block: 'center'}});
                }}
                """
                BuiltIn().run_keyword("Browser.Evaluate JavaScript", highlight_js)
            
            # Small delay to ensure highlight is rendered
            import time
            time.sleep(0.3)
            
            return 'highlighted'
        except Exception as e:
            logger.debug(f"Could not highlight element: {e}")
            return None
    
    def _remove_highlight(self, locator, library_type='SeleniumLibrary'):
        """Remove the highlight from the element"""
        try:
            remove_script = """
            (function(element) {
                if (!element || element.getAttribute('data-highlighted') !== 'true') return;
                
                // Restore original styles
                element.style.border = element.getAttribute('data-original-border') || '';
                element.style.outline = element.getAttribute('data-original-outline') || '';
                element.style.boxShadow = element.getAttribute('data-original-boxshadow') || '';
                element.style.zIndex = element.getAttribute('data-original-zindex') || '';
                
                // Remove data attributes
                element.removeAttribute('data-original-border');
                element.removeAttribute('data-original-outline');
                element.removeAttribute('data-original-boxshadow');
                element.removeAttribute('data-original-zindex');
                element.removeAttribute('data-highlighted');
            })(arguments[0]);
            """
            
            if library_type == 'SeleniumLibrary':
                # Temporarily reduce log level to avoid verbose JavaScript in report
                old_log_level = BuiltIn().set_log_level("WARN")
                try:
                    element = BuiltIn().run_keyword("SeleniumLibrary.Get WebElement", locator)
                    BuiltIn().run_keyword("SeleniumLibrary.Execute Javascript", remove_script, "ARGUMENTS", element)
                finally:
                    BuiltIn().set_log_level(old_log_level)
            elif library_type == 'Browser':
                remove_js = f"""
                const element = document.querySelector('{locator.replace("css=", "").replace("xpath=", "")}');
                if (element) {{
                    element.style.border = '';
                    element.style.outline = '';
                    element.style.boxShadow = '';
                    element.style.zIndex = '';
                }}
                """
                BuiltIn().run_keyword("Browser.Evaluate JavaScript", remove_js)
        except Exception as e:
            logger.debug(f"Could not remove highlight: {e}")
    
    def _capture_screenshot_for_locator(self, locator=None, library_type='SeleniumLibrary') -> str:
        """Capture a screenshot with the element highlighted and return the relative path"""
        try:
            output_dir = BuiltIn().get_variable_value('${OUTPUT_DIR}')
            
            # Highlight the element if locator provided
            highlight_id = None
            if locator:
                highlight_id = self._highlight_element(locator, library_type)
            
            # Use SeleniumLibrary or Browser library screenshot
            screenshot_path = BuiltIn().run_keyword("Capture Page Screenshot")
            
            # Remove the highlight
            if locator and highlight_id:
                self._remove_highlight(locator, library_type)
            
            # Return relative path from output directory
            if screenshot_path:
                import os
                # Get just the filename
                filename = os.path.basename(screenshot_path)
                return filename
        except Exception as e:
            logger.debug(f"Could not capture screenshot: {e}")
        
        return None
    
    def _store_successful_locator_info(self, locator_info):
        self.locator_db.insert(locator_info)