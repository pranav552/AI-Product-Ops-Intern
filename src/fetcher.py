import io
import json
import re

import requests
import trafilatura
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/153.0 Safari/537.36"
)


TIMEOUT = 20
RENDER_TIMEOUT = 30000
RENDER_WAIT_MS = 1500


def clean_text(text: str) -> str:
    """
    Normalize extracted text.
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")

    text = re.sub(
        r"\r\n?",
        "\n",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    text = re.sub(
        r"[ \t]{2,}",
        " ",
        text
    )

    return text.strip()


def is_garbage(text: str) -> bool:
    """
    Detect empty, very short, or obvious SPA/error-page content.
    """

    if not text:
        return True

    text = clean_text(text)
    lowered = text.lower()

    # Extremely short content is not useful evidence.
    if len(text) < 200:
        return True

    garbage_markers = [
        "sorry to interrupt",
        "css error",
        "enable javascript",
        "javascript is required",
        "please enable javascript",
        "please wait",
        "loading ×",
        "loading\n×",
    ]

    # Only apply marker rejection to relatively short pages.
    # A real long document could legitimately contain one of these words.
    if len(text) < 1000:
        for marker in garbage_markers:
            if marker in lowered:
                return True

    return False


def extract_html(html: str) -> str:
    """
    Extract useful textual content from HTML.

    Uses Trafilatura first and BeautifulSoup as fallback.
    """

    if not html:
        return ""

    candidates = []

    # ========================================================
    # Trafilatura
    # ========================================================

    try:

        text = trafilatura.extract(
            html,
            include_links=True,
            include_tables=True,
            favor_precision=True
        )

        if text:
            candidates.append(text)

    except Exception:
        pass

    # ========================================================
    # BeautifulSoup fallback
    # ========================================================

    try:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "noscript",
            "svg"
        ]):
            tag.decompose()

        text = soup.get_text(
            "\n",
            strip=True
        )

        if text:
            candidates.append(text)

    except Exception:
        pass

    if not candidates:
        return ""

    # Prefer the longest extraction.
    candidates.sort(
        key=len,
        reverse=True
    )

    return clean_text(
        candidates[0]
    )


def extract_pdf(content: bytes) -> str:
    """
    Extract text from a PDF.
    """

    try:

        from pypdf import PdfReader

        reader = PdfReader(
            io.BytesIO(content)
        )

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(text)

        return clean_text(
            "\n\n".join(pages)
        )

    except Exception as e:

        print(
            f"PDF extraction failed: {e}"
        )

        return ""


def _build_result(
    url: str,
    status_code,
    text: str,
    error=None
) -> dict:
    """
    Keep fetch results consistent across all fetch methods.
    """

    text = clean_text(text)

    if not text or is_garbage(text):

        return {
            "url": url,
            "status_code": status_code,
            "success": False,
            "text": "",
            "error": error or "Low-quality or SPA-shell content"
        }

    return {
        "url": url,
        "status_code": status_code,
        "success": True,
        "text": text,
        "error": None
    }


def fetch_page(url: str) -> dict:
    """
    Fast static fetch.

    Handles:
        - HTML
        - plain text
        - JSON
        - PDF

    JavaScript-rendered pages will normally fail the garbage
    check and can then be passed to fetch_page_rendered().
    """

    try:

        response = requests.get(
            url,
            timeout=TIMEOUT,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/pdf,"
                    "application/json,"
                    "text/plain;q=0.9,"
                    "*/*;q=0.8"
                ),
                "Accept-Language":
                    "en-US,en;q=0.9",
            },
            allow_redirects=True
        )

        response.raise_for_status()

        content_type = (
            response.headers.get(
                "Content-Type",
                ""
            )
            .lower()
        )

        # ====================================================
        # PDF
        # ====================================================

        if (
            "application/pdf" in content_type
            or url.lower().split("?")[0].endswith(".pdf")
        ):

            text = extract_pdf(
                response.content
            )

        # ====================================================
        # JSON
        # ====================================================

        elif "application/json" in content_type:

            try:

                data = response.json()

                text = json.dumps(
                    data,
                    indent=2,
                    ensure_ascii=False
                )

            except Exception:

                text = response.text

        # ====================================================
        # HTML / TEXT
        # ====================================================

        else:

            text = extract_html(
                response.text
            )

        return _build_result(
            url=url,
            status_code=response.status_code,
            text=text
        )

    except Exception as e:

        return {
            "url": url,
            "status_code": None,
            "success": False,
            "text": "",
            "error": str(e)
        }


def fetch_page_rendered(url: str) -> dict:
    """
    JavaScript-rendered fallback.

    This should normally be called ONLY when fetch_page()
    fails.

    Playwright launches Chromium, executes the page's
    JavaScript, waits for the page to render, and then
    extracts the resulting HTML.

    This solves cases such as:

        <div id="app"></div>

    where the actual documentation is inserted into the DOM
    only after JavaScript executes.
    """

    try:

        from playwright.sync_api import sync_playwright

    except ImportError:

        return {
            "url": url,
            "status_code": None,
            "success": False,
            "text": "",
            "error": (
                "Playwright is not installed. "
                "Run: pip install playwright"
            )
        }

    browser = None

    try:

        with sync_playwright() as p:

            # ------------------------------------------------
            # Launch Chromium
            # ------------------------------------------------

            browser = p.chromium.launch(
                headless=True
            )

            # ------------------------------------------------
            # Create page
            # ------------------------------------------------

            page = browser.new_page(
                user_agent=USER_AGENT,
                viewport={
                    "width": 1440,
                    "height": 900
                }
            )

            # ------------------------------------------------
            # Navigate
            # ------------------------------------------------

            response = page.goto(
                url,
                timeout=RENDER_TIMEOUT,
                wait_until="domcontentloaded"
            )

            # ------------------------------------------------
            # Give client-side JavaScript time to render.
            #
            # We intentionally don't require networkidle here.
            # Modern applications can keep analytics/websocket/
            # tracking requests open indefinitely.
            # ------------------------------------------------

            page.wait_for_timeout(
                RENDER_WAIT_MS
            )

            # ------------------------------------------------
            # Try to wait for meaningful body content.
            # This is best-effort; some pages don't expose a
            # useful selector.
            # ------------------------------------------------

            try:

                page.wait_for_function(
                    """
                    () => {
                        const body = document.body;
                        if (!body) return false;

                        const text = body.innerText || "";
                        return text.trim().length >= 200;
                    }
                    """,
                    timeout=10000
                )

            except Exception:
                # Do not fail just because the wait condition
                # timed out. We still inspect the page.
                pass

            # ------------------------------------------------
            # Capture final rendered DOM
            # ------------------------------------------------

            html = page.content()

            status_code = (
                response.status
                if response
                else 200
            )

            # ------------------------------------------------
            # Extract text
            # ------------------------------------------------

            text = extract_html(
                html
            )

            text = clean_text(
                text
            )

            # ------------------------------------------------
            # Validate rendered result
            # ------------------------------------------------

            if not text or is_garbage(text):

                return {
                    "url": url,
                    "status_code": status_code,
                    "success": False,
                    "text": "",
                    "error": (
                        "Rendered page contained "
                        "no usable evidence text"
                    )
                }

            return {
                "url": url,
                "status_code": status_code,
                "success": True,
                "text": text,
                "error": None
            }

    except Exception as e:

        return {
            "url": url,
            "status_code": None,
            "success": False,
            "text": "",
            "error": str(e)
        }

    finally:

        if browser:

            try:
                browser.close()
            except Exception:
                pass