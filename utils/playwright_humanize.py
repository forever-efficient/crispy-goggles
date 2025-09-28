"""Small helpers to make Playwright actions look more human for local dev.

These helpers are intended for local development and debugging only. They
introduce small, configurable delays and mouse movements to reduce obvious
automation fingerprints during manual headed testing.
"""
import random
import time
from typing import Any
import math


def human_type(locator: Any, text: str, *, min_delay: float = 0.01, max_delay: float = 0.05):
    """Type text into a Playwright locator with per-character random delay.

    Args:
        locator: Playwright Locator or ElementHandle with a `type` method.
        text: text to type.
        min_delay: minimum delay per character in seconds.
        max_delay: maximum delay per character in seconds.
    """
    # Some locator implementations accept a delay arg on `type`; prefer using
    # the built-in method when possible for efficiency, but fall back to per-
    # char typing which is more variable.
    try:
        # delay is in ms for Playwright's type
        avg_delay_ms = int(((min_delay + max_delay) / 2.0) * 1000)
        locator.type(text, delay=avg_delay_ms)
        return
    except Exception:
        # fall back to char-by-char typing
        try:
            locator.click()
        except Exception:
            pass
        for ch in text:
            try:
                locator.page.keyboard.type(ch)
            except Exception:
                # last resort: set value directly via JS
                try:
                    locator.evaluate("(el, c) => { el.value = (el.value || '') + c; el.dispatchEvent(new Event('input', { bubbles: true })); }", ch)
                except Exception:
                    pass
        time.sleep(random.uniform(min_delay, max_delay))


def small_mouse_moves(page: Any, times: int = 3):
    """Perform a few small mouse moves to simulate human repositioning.

    Args:
        page: Playwright Page
        times: number of small movements
    """
    try:
        box = page.viewport_size
        if not box:
            return
        w = box.get('width', 1280)
        h = box.get('height', 800)
        for _ in range(times):
            start_x = random.randint(int(w * 0.1), int(w * 0.9))
            start_y = random.randint(int(h * 0.1), int(h * 0.9))
            end_x = random.randint(int(w * 0.1), int(w * 0.9))
            end_y = random.randint(int(h * 0.1), int(h * 0.9))
            try:
                curve_move_to(page, (start_x, start_y), (end_x, end_y), steps=random.randint(6, 12))
            except Exception:
                page.mouse.move(end_x, end_y, steps=random.randint(3, 8))
            time.sleep(random.uniform(0.01, 0.06))
    except Exception:
        pass


def curve_move_to(page: Any, start: tuple, end: tuple, steps: int = 20):
    """Move the mouse along a simple quadratic Bezier curve from start to end.

    Args:
        page: Playwright Page
        start: (x, y) start position
        end: (x, y) end position
        steps: number of intermediate steps
    """
    (x0, y0) = start
    (x2, y2) = end
    # control point roughly in the middle with a random offset
    cx = (x0 + x2) / 2 + random.uniform(-50, 50)
    cy = (y0 + y2) / 2 + random.uniform(-50, 50)

    def quad_bezier(t, p0, p1, p2):
        return (1 - t) * (1 - t) * p0 + 2 * (1 - t) * t * p1 + t * t * p2

    # move to start quickly
    page.mouse.move(int(x0), int(y0))
    for i in range(1, steps + 1):
        t = i / steps
        x = quad_bezier(t, x0, cx, x2)
        y = quad_bezier(t, y0, cy, y2)
        page.mouse.move(int(x), int(y))
        # small variable sleep to mimic real motion
        time.sleep(random.uniform(0.002, 0.008))


def simulate_micro_interactions(page: Any, *, hover_selector: str = None):
    """Perform a few low-impact interactions: small scrolls, hover, and pauses.

    Args:
        page: Playwright Page
        hover_selector: optional CSS selector to hover before typing/clicking
    """
    try:
        # small random scrolls
        try:
            box = page.viewport_size or {"width": 1280, "height": 800}
            w = box.get("width", 1280)
            h = box.get("height", 800)
            for _ in range(random.randint(0, 1)):
                x = random.randint(int(w * 0.1), int(w * 0.9))
                y = random.randint(int(h * 0.2), int(h * 0.8))
                page.mouse.wheel(0, y // 8)
                time.sleep(random.uniform(0.005, 0.06))
        except Exception:
            pass

        # small hover over a selector if provided
        if hover_selector:
            try:
                el = page.locator(hover_selector).first
                box = el.bounding_box()
                if box:
                    cx = int(box["x"] + box["width"] / 2)
                    cy = int(box["y"] + box["height"] / 2)
                    curve_move_to(page, (cx - 20, cy - 10), (cx, cy), steps=random.randint(4, 8))
                    time.sleep(random.uniform(0.01, 0.06))
            except Exception:
                pass

        # a few small mouse repositionings
        try:
            small_mouse_moves(page, times=random.randint(1, 3))
        except Exception:
            pass

        # small pause to mimic reading/thinking
        time.sleep(random.uniform(0.01, 0.08))
    except Exception:
        pass
