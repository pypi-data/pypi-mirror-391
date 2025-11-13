import asyncio
from typing import Any, Callable, Iterable, Optional

import browser_cookie3
import tiktoken
from loguru import logger


def remove_blank_lines(text: str) -> str:
    return '\n'.join(line for line in text.splitlines() if line.strip())


def first_element(iterable: Iterable) -> Any:
    return next(iter(iterable))


def num_tokens_from_text(content: str, encoding_name: str = 'o200k_base') -> int:
    return len(tiktoken.get_encoding(encoding_name).encode(content))


def call_async_func(func: Callable, *args, **kwargs) -> Any:
    """
    Call an async function in a synchronous context.
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        raise RuntimeError("Cannot call async function from a running event loop")
    return loop.run_until_complete(func(*args, **kwargs))


def ensure_folder(folder_path: str) -> None:
    """
    Ensure that a folder exists, creating it if necessary.
    """
    import os

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def get_cookie_from_browser(browser_name: str) -> Optional[tuple]:
    logger.info('get_cookie_from_browser, browser_name: %s', browser_name)

    browser_name = browser_name.lower()
    try:
        if browser_name == "firefox":
            cookies = browser_cookie3.firefox()
        elif browser_name == "chrome":
            cookies = browser_cookie3.chrome(domain_name='google.com')
        elif browser_name == "brave":
            cookies = browser_cookie3.brave()
        elif browser_name == "edge":
            cookies = browser_cookie3.edge()
        elif browser_name == "safari":
            cookies = browser_cookie3.safari()
        elif browser_name == 'arc':
            cookies = browser_cookie3.arc()
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")
        logger.info(f"Successfully retrieved cookies from {browser_name}")
    except ValueError as ve:
        logger.error(f"Unsupported browser: {browser_name} - {ve}")
        return None, None
    except browser_cookie3.BrowserCookieError as bce:
        logger.error(f"Error retrieving cookies from {browser_name}: {bce}")
        return None, None
    except Exception as e:
        logger.error(f"An unexpected error occurred while retrieving cookies from {browser_name}: {e}", exc_info=True)
        return None, None

    logger.info("Looking for Gemini cookies (__Secure-1PSID and __Secure-1PSIDTS)...")
    secure_1psid = None
    secure_1psidts = None
    for cookie in cookies:
        if cookie.name == "__Secure-1PSID" and "google" in cookie.domain:
            secure_1psid = cookie.value
            logger.info(f"Found __Secure-1PSID: {secure_1psid}")
        elif cookie.name == "__Secure-1PSIDTS" and "google" in cookie.domain:
            secure_1psidts = cookie.value
            logger.info(f"Found __Secure-1PSIDTS: {secure_1psidts}")
    if secure_1psid and secure_1psidts:
        logger.info("Both Gemini cookies found.")
        return secure_1psid, secure_1psidts
    else:
        logger.warning("Gemini cookies not found or incomplete.")
        return None, None
