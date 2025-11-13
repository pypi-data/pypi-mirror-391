import openai
import requests, tempfile
import logging
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ...tools import load_settings
from urllib.parse import urljoin

logging.basicConfig(level=logging.ERROR, force=True)
logger = logging.getLogger(__name__)

def remove_duplicate_css(css_content: str) -> str:
    lines = css_content.split('\n')
    seen = set()
    unique_lines = []

    for line in lines:
        if line.strip() and line not in seen:
            seen.add(line)
            unique_lines.append(line)
        elif not line.strip():
            unique_lines.append(line)

    return '\n'.join(unique_lines)

def get_website_css(url:str) -> str:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    css_links = [urljoin(url, link["href"]) for link in soup.find_all("link", rel="stylesheet")]
    inline_styles = [tag.get_text() for tag in soup.find_all("style")]

    excluded_libraries = [
        'swiper', 'highlight.js', 'hljs', 'toastify',
        'bootstrap', 'fontawesome', 'font-awesome',
        'jquery-ui', 'animate.css', 'slick'
    ]

    max_css_size = 500 * 1024

    all_css = []

    for css_url in css_links:
        if any(lib in css_url.lower() for lib in excluded_libraries):
            logger.debug(f"Ignorando biblioteca externa: {css_url}")
            continue

        try:
            resp = requests.get(css_url, timeout=10)
            if resp.ok:
                if len(resp.text) > max_css_size:
                    logger.debug(f"Ignorando arquivo CSS muito grande ({len(resp.text)/1024:.1f}KB): {css_url}")
                    continue
                all_css.append(f"/* {css_url} */\n" + resp.text)
        except Exception as e:
            logger.debug(f"Erro ao baixar {css_url}: {e}")

    if inline_styles:
        all_css.append("/* Inline styles */\n" + "\n".join(inline_styles))

    combined_css = "\n".join(all_css)
    combined_css = remove_duplicate_css(combined_css)

    return combined_css

def get_website_screenshot(url:str) -> str:
    """
    Takes a screenshot of the given website URL.
    Arguments:
        url (str): The URL of the website to screenshot.
    Returns:
        str: The file path to the screenshot image (temporary file).
    """
    settings = load_settings()
    with sync_playwright() as p:
        logger.debug(f"Launching browser for screenshot: {url}")
        browser = p.chromium.launch(executable_path=settings.get("browser_path"), headless=True)
        page = browser.new_page()
        page.goto(url)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            screenshot_path = tmpfile.name
            logger.debug(f"Taking screenshot and saving to: {screenshot_path}")
        page.set_viewport_size({"width": 1920, "height": 2000})
        page.screenshot(path=screenshot_path, full_page=False)
        browser.close()
    return screenshot_path