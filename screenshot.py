#!/usr/bin/env python3
import argparse
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright


def make_output_path(url: str, ext: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "") or "screenshot"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{domain}_{timestamp}.{ext}"


def ensure_scheme(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


MOBILE_DEVICES = {
    "iphone-12": "iPhone 12",
    "iphone-14": "iPhone 14 Pro",
    "pixel-5": "Pixel 5",
    "galaxy-s21": "Galaxy S21",
    "ipad": "iPad Pro 11",
}


async def screenshot(
    url: str,
    output: str | None,
    full_page: bool,
    width: int,
    height: int,
    mobile: str | None,
    dark_mode: bool,
    wait: int,
    wait_for: str | None,
    element: str | None,
    to_pdf: bool,
    fmt: str,
    timeout: int,
    batch: list[str],
):
    urls = [url] + batch

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        for target_url in urls:
            target_url = ensure_scheme(target_url)
            ext = "pdf" if to_pdf else fmt
            out = output if (output and len(urls) == 1) else make_output_path(target_url, ext)

            context_kwargs: dict = {}

            if mobile:
                device_name = MOBILE_DEVICES.get(mobile)
                if device_name is None:
                    print(f"Unknown device '{mobile}'. Choices: {', '.join(MOBILE_DEVICES)}", file=sys.stderr)
                    sys.exit(1)
                context_kwargs = dict(p.devices[device_name])
            else:
                context_kwargs["viewport"] = {"width": width, "height": height}

            if dark_mode:
                context_kwargs["color_scheme"] = "dark"

            context = await browser.new_context(**context_kwargs)
            page = await context.new_page()
            page.set_default_timeout(timeout * 1000)

            print(f"  Loading {target_url} ...")
            try:
                await page.goto(target_url, wait_until="networkidle")
            except Exception:
                # fall back to domcontentloaded for pages that never reach networkidle
                await page.goto(target_url, wait_until="domcontentloaded")

            if wait_for:
                print(f"  Waiting for selector: {wait_for}")
                await page.wait_for_selector(wait_for)

            if wait > 0:
                print(f"  Waiting {wait}s ...")
                await asyncio.sleep(wait)

            if to_pdf:
                await page.pdf(path=out, format="A4", print_background=True)
                print(f"  PDF saved  -> {out}")
            elif element:
                el = await page.query_selector(element)
                if el is None:
                    print(f"  Element not found: {element}", file=sys.stderr)
                    sys.exit(1)
                await el.screenshot(path=out)
                print(f"  Element screenshot saved -> {out}")
            else:
                await page.screenshot(path=out, full_page=full_page, type=fmt)
                print(f"  Screenshot saved -> {out}")

            await context.close()

        await browser.close()


def main():
    parser = argparse.ArgumentParser(
        prog="screenshot",
        description="Full-page website screenshots from the command line.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python screenshot.py https://example.com
  python screenshot.py example.com -o out.png
  python screenshot.py https://example.com --mobile iphone-12
  python screenshot.py https://example.com --dark-mode --width 1440
  python screenshot.py https://example.com --element "#hero"
  python screenshot.py https://example.com --pdf
  python screenshot.py https://example.com --no-full-page --wait 2
  python screenshot.py https://a.com https://b.com https://c.com
        """,
    )

    parser.add_argument("url", help="Primary URL to screenshot")
    parser.add_argument("batch", nargs="*", metavar="URL", help="Additional URLs (batch mode)")
    parser.add_argument("-o", "--output", metavar="FILE",
                        help="Output file path (auto-named by domain+timestamp if omitted)")
    parser.add_argument("--no-full-page", action="store_true",
                        help="Capture viewport only instead of the full page")
    parser.add_argument("--width", type=int, default=1920, metavar="PX",
                        help="Viewport width in pixels (default: 1920)")
    parser.add_argument("--height", type=int, default=1080, metavar="PX",
                        help="Viewport height in pixels (default: 1080)")
    parser.add_argument("--mobile", metavar="DEVICE",
                        choices=MOBILE_DEVICES.keys(),
                        help=f"Emulate a mobile device: {', '.join(MOBILE_DEVICES)}")
    parser.add_argument("--dark-mode", action="store_true",
                        help="Request dark colour scheme")
    parser.add_argument("--wait", type=int, default=0, metavar="SEC",
                        help="Extra seconds to wait after page load (good for animations/lazy images)")
    parser.add_argument("--wait-for", metavar="SELECTOR",
                        help="Wait until a CSS selector appears on the page")
    parser.add_argument("--element", metavar="SELECTOR",
                        help="Screenshot only the element matching a CSS selector")
    parser.add_argument("--pdf", action="store_true",
                        help="Export as PDF (A4, with background graphics)")
    parser.add_argument("--format", dest="fmt", choices=["png", "jpeg"], default="png",
                        help="Image format (default: png)")
    parser.add_argument("--timeout", type=int, default=30, metavar="SEC",
                        help="Navigation timeout in seconds (default: 30)")

    args = parser.parse_args()

    print(f"\nBrowser screenshot tool")
    print(f"  URL   : {ensure_scheme(args.url)}")
    if args.batch:
        print(f"  Batch : {len(args.batch)} additional URL(s)")
    print()

    asyncio.run(screenshot(
        url=args.url,
        output=args.output,
        full_page=not args.no_full_page,
        width=args.width,
        height=args.height,
        mobile=args.mobile,
        dark_mode=args.dark_mode,
        wait=args.wait,
        wait_for=args.wait_for,
        element=args.element,
        to_pdf=args.pdf,
        fmt=args.fmt,
        timeout=args.timeout,
        batch=args.batch,
    ))


if __name__ == "__main__":
    main()
