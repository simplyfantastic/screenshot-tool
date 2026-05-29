# Website Screenshot Tool

A simple command-line tool that takes full-page screenshots of any website — no scrolling, no stitching multiple images together. It works the same way as Chrome DevTools' built-in "Capture full size screenshot" feature, but from your terminal.

---

## How it works

The tool launches a real (headless, invisible) Chromium browser in the background, opens the URL you give it, waits for the page to fully load, then saves a screenshot of the entire page — including content below the fold that you would normally have to scroll to see. The browser is then closed automatically.

No extensions, no browser plugins, no manual scrolling needed.

---

## Requirements

- Python 3.8 or newer — download from [python.org](https://www.python.org/downloads/)
- An internet connection (to fetch the page you want to screenshot)

---

## Installation

Open a terminal (Command Prompt, PowerShell, or Terminal on Mac/Linux) in the folder where you downloaded this tool, then run:

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

The first command installs the Playwright library. The second downloads the headless Chromium browser (~150 MB, one-time download).

---

## Basic usage

```bash
python screenshot.py https://example.com
```

That's it. A PNG file will be saved in the same folder as the script.

You can leave out the `https://` prefix — the tool adds it automatically:

```bash
python screenshot.py example.com
```

---

## Where is the screenshot saved?

By default, screenshots are saved **in the same folder as `screenshot.py`**, with a filename built from the website's domain name and the current date/time:

```
example.com_20240601_143022.png
```

To choose your own filename and location:

```bash
python screenshot.py https://example.com -o my_screenshot.png
python screenshot.py https://example.com -o C:/Users/YourName/Desktop/shot.png
```

---

## All options

```
python screenshot.py [URL] [options]
```

| Option | Description |
|---|---|
| `-o FILE` | Save to a specific file path instead of auto-naming |
| `--no-full-page` | Capture only what's visible on screen (no auto-scroll) |
| `--width PX` | Browser window width in pixels (default: 1920) |
| `--height PX` | Browser window height in pixels (default: 1080) |
| `--mobile DEVICE` | Emulate a mobile device (see list below) |
| `--dark-mode` | Request the dark version of the site (if it supports it) |
| `--wait N` | Wait N extra seconds after load — useful for animations or lazy-loaded images |
| `--wait-for SELECTOR` | Wait until a specific page element appears (CSS selector) |
| `--element SELECTOR` | Screenshot only one element on the page (CSS selector) |
| `--pdf` | Save as a PDF instead of a PNG |
| `--format jpeg` | Save as JPEG instead of PNG |
| `--timeout SEC` | How long to wait for the page to load before giving up (default: 30s) |

### Mobile devices

```bash
--mobile iphone-12
--mobile iphone-14
--mobile pixel-5
--mobile galaxy-s21
--mobile ipad
```

---

## Examples

Full-page screenshot (default):
```bash
python screenshot.py https://github.com
```

Save to a specific file:
```bash
python screenshot.py https://github.com -o github.png
```

Mobile view:
```bash
python screenshot.py https://github.com --mobile iphone-14
```

Dark mode:
```bash
python screenshot.py https://github.com --dark-mode
```

Wait 3 seconds after load (good for sites with animations):
```bash
python screenshot.py https://github.com --wait 3
```

Screenshot only the navigation bar:
```bash
python screenshot.py https://github.com --element "nav"
```

Export as PDF:
```bash
python screenshot.py https://github.com --pdf
```

Screenshot several sites at once:
```bash
python screenshot.py https://github.com https://example.com https://wikipedia.org
```

---

## Security

**What the tool does:**
- Opens the URL in a headless Chromium browser (the same engine as Google Chrome)
- Takes a screenshot of what the browser renders
- Saves the file to your computer
- Closes the browser

**What the tool does NOT do:**
- It does not collect, send, or store any data about you or the websites you screenshot
- It does not run any code from the website on your machine beyond what a normal browser visit would
- It does not log your activity anywhere
- It does not require an account or API key

**Things to be aware of:**
- Screenshotting a website makes an ordinary HTTP request to that server — the site can see your IP address, just like any normal visit
- Do not screenshot pages that require you to be logged in, as this tool does not handle authentication
- Only screenshot websites you have permission to access

---

## Troubleshooting

**"pip is not recognized"** — Make sure Python is installed and added to your PATH during installation. Re-run the Python installer and check "Add Python to PATH".

**"playwright is not recognized"** — Use `python -m playwright install chromium` instead of just `playwright install chromium`.

**The screenshot is blank or cut off** — The page may use heavy JavaScript. Try adding `--wait 3` to give it more time to render.

**The page times out** — Some sites block automated browsers. Try increasing the timeout with `--timeout 60`.

---

## License

MIT — free to use, modify, and share.
