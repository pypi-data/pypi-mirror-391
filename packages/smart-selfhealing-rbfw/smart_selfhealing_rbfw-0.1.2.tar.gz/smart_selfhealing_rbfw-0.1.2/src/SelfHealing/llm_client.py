import httpx
import os
from dotenv import load_dotenv
import base64
import litellm
from litellm import completion
from robot.api import logger
import json

load_dotenv()

LLM_API_KEY = os.environ.get('LLM_API_KEY', None)
LLM_API_BASE = os.environ.get('LLM_API_BASE', None)
LOCATOR_AI_MODEL = os.environ.get('LOCATOR_AI_MODEL', "ollama_chat/llama3.1")
VISUAL_AI_MODEL = os.environ.get('VISUAL_AI_MODEL', "ollama_chat/llama3.2-vision")

if LLM_API_KEY:
    litellm.api_key = LLM_API_KEY
if LLM_API_BASE:
    litellm.api_base = LLM_API_BASE

def debug_log_request(model, messages, **kwargs):
    """Log LLM request details for debugging (internal use only)"""
    # Only log if explicitly enabled via SELFHEALING_DEBUG, not just Robot Framework DEBUG level
    if not os.getenv('SELFHEALING_DEBUG', 'false').lower() == 'true':
        return
        
    log_msg = f"\n{'='*80}\n🔵 LLM REQUEST\n{'='*80}\n"
    log_msg += f"Model: {model}\n"
    log_msg += f"Temperature: {kwargs.get('temperature', 'default')}\n"
    log_msg += f"Response Format: {kwargs.get('response_format', 'default')}\n"
    log_msg += f"\nMessages:\n"
    for idx, msg in enumerate(messages):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        # Truncate very long content (e.g., screenshots, large DOM)
        if isinstance(content, str) and len(content) > 1000:
            content_preview = content[:500] + f"\n... [truncated {len(content) - 500} chars] ..."
        elif isinstance(content, list):
            content_preview = "[multipart content with images]"
        else:
            content_preview = content
        log_msg += f"\n[{idx+1}] {role.upper()}:\n{content_preview}\n"
    log_msg += f"{'='*80}\n"
    logger.info(log_msg, also_console=True)

def debug_log_response(response):
    """Log LLM response details for debugging (internal use only)"""
    # Only log if explicitly enabled via SELFHEALING_DEBUG, not just Robot Framework DEBUG level
    if not os.getenv('SELFHEALING_DEBUG', 'false').lower() == 'true':
        return
        
    log_msg = f"\n{'='*80}\n🟢 LLM RESPONSE\n{'='*80}\n"
    try:
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            log_msg += f"Content:\n{content}\n"
        else:
            log_msg += f"Raw Response:\n{str(response)}\n"
        
        # Log token usage if available
        if hasattr(response, 'usage'):
            log_msg += f"\nToken Usage:\n"
            log_msg += f"  Prompt: {response.usage.prompt_tokens}\n"
            log_msg += f"  Completion: {response.usage.completion_tokens}\n"
            log_msg += f"  Total: {response.usage.total_tokens}\n"
    except Exception as e:
        log_msg += f"Error parsing response: {e}\n"
        log_msg += f"Raw: {str(response)[:500]}\n"
    
    log_msg += f"{'='*80}\n"
    logger.info(log_msg, also_console=True)

def completion_with_debug(debug_enabled=False, **kwargs):
    """
    Wrapper around litellm.completion() that adds debug logging
    Internal use only - not exposed to end users
    """
    if debug_enabled:
        debug_log_request(
            kwargs.get('model', 'unknown'),
            kwargs.get('messages', []),
            temperature=kwargs.get('temperature'),
            response_format=kwargs.get('response_format')
        )
    
    response = completion(**kwargs)
    
    if debug_enabled:
        debug_log_response(response)
    
    return response