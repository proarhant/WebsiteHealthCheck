from playwright.sync_api import sync_playwright, ConsoleMessage, Request
from urllib.parse import urlparse
from typing import List, Dict

def check_website_errors(url: str) -> Dict:
    result = {
        'url': url,
        'status_code': None,
        'title': '',
        'js_errors': [],
        'network_errors': [],
        'console_errors': [],
        'error': None
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Error collectors
            js_errors: List[str] = []
            network_errors: List[Dict] = []
            console_errors: List[Dict] = []

            # Event handlers
            def handle_js_error(error):
                js_errors.append(str(error))

            def handle_console(msg: ConsoleMessage):
                if msg.type == 'error':
                    console_errors.append({
                        'text': msg.text,
                        'location': msg.location
                    })

            def handle_failed_request(request: Request):
                if request.failure:
                    network_errors.append({
                        'url': request.url,
                        'failure': request.failure
                    })

            page.on("pageerror", handle_js_error)
            page.on("console", handle_console)
            page.on("requestfailed", handle_failed_request)

            response = page.goto(url, wait_until="networkidle", timeout=60000)
            result['status_code'] = response.status if response else None

            try:
                result['title'] = page.title()
            except Exception:
                result['title'] = "(Failed to retrieve title)"

            result['js_errors'] = js_errors
            result['network_errors'] = network_errors
            result['console_errors'] = console_errors

            browser.close()

    except Exception as e:
        result['error'] = str(e)

    return result
