"""Captures interface screenshots for the report. Needs the app running."""

import sys
import time

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8520"
OUT = "figures"

# (filename, preset label shown in the sidebar select)
SHOTS = [
    ("ui_case_a.png", "Case A: (1, 4)"),
    ("ui_case_b.png", "Case B: (1, 1.1)"),
    ("ui_case_c.png", "Case C: (1, 2, 3)"),
]


def trim(path, sidebar_frac=0.25):
    """Crop the blank band below the content.

    The bbox is taken from the main panel only: the sidebar is a full-height
    grey block, so including it would always report the full image height.
    """
    from PIL import Image, ImageChops
    im = Image.open(path).convert("RGB")
    x0 = int(im.width * sidebar_frac)
    main = im.crop((x0, 0, im.width, im.height))
    bg = Image.new("RGB", main.size, main.getpixel((main.width - 5, main.height - 5)))
    box = ImageChops.difference(main, bg).getbbox()
    if box:
        im.crop((0, 0, im.width, min(im.height, box[3] + 60))).save(path)


def settle(page, seconds=4.0):
    """Streamlit reruns on every change; wait for it to stop being busy."""
    page.wait_for_load_state("networkidle")
    time.sleep(seconds)


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1500, "height": 2750},
                            device_scale_factor=2)
    page.goto(URL, timeout=60000)
    settle(page, 8.0)

    for name, preset in SHOTS:
        # the preset dropdown is the first combobox in the sidebar
        box = page.get_by_role("combobox").first
        box.click()
        page.get_by_text(preset, exact=True).last.click()
        settle(page)
        path = f"{OUT}/{name}"
        page.screenshot(path=path, full_page=True)
        trim(path)
        print("wrote", name)

    browser.close()
