#!/usr/bin/env python3
"""
TikTok Custom Comment Bot
Uses Playwright browser automation + session cookie — no signature cracking needed.
"""

import asyncio
import json
import os
import random
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Install Playwright: pip install playwright && playwright install chromium")
    sys.exit(1)


# --- Config ---
CONFIG_PATH = Path(__file__).parent / "comment_config.json"
DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def extract_video_id(url: str) -> str:
    """Extract aweme_id from TikTok URL."""
    parts = url.rstrip("/").split("/")
    for i, p in enumerate(parts):
        if p == "video" and i + 1 < len(parts):
            return parts[i + 1].split("?")[0]
    # Fallback: last path segment
    return parts[-1].split("?")[0] if parts else ""


async def post_comment(
    page,
    video_url: str,
    comment_text: str,
    headless: bool = True,
) -> tuple:
    """Navigate to video and post a comment via the web UI."""
    video_id = extract_video_id(video_url)
    if not video_id or not video_id.isdigit():
        return False, f"Invalid video URL: {video_url}"

    if video_url.startswith("http"):
        full_url = video_url
    else:
        full_url = f"https://www.tiktok.com/@{video_id}/video/{video_id}"

    try:
        await page.goto(full_url, wait_until="networkidle", timeout=30000)
    except PlaywrightTimeout:
        await page.goto(full_url, wait_until="domcontentloaded", timeout=15000)

    await asyncio.sleep(1.5)

    # TikTok web: comment input is often in a div with contenteditable or a textarea
    selectors = [
        '[data-e2e="comment-input"]',
        '[contenteditable="true"][data-e2e="comment-input"]',
        'div[contenteditable="true"]',
        'textarea[placeholder*="comment" i]',
        'textarea[placeholder*="Add" i]',
        '[data-e2e="comment-input"]',
        'div[class*="DraftEditor"]',
        '[class*="comment-input"]',
        'div[role="textbox"]',
    ]

    input_el = None
    for sel in selectors:
        try:
            input_el = await page.wait_for_selector(sel, timeout=3000)
            if input_el:
                break
        except PlaywrightTimeout:
            continue

    if not input_el:
        return False, "Could not find comment input. Page might require login or has changed."

    await input_el.click()
    await asyncio.sleep(0.3)
    await input_el.fill(comment_text)
    await asyncio.sleep(0.5)

    # Submit button
    submit_selectors = [
        '[data-e2e="comment-post"]',
        'button[data-e2e="comment-post"]',
        'button:has-text("Post")',
        'button:has-text("post")',
        '[data-e2e="comment-submit"]',
        'button[type="submit"]',
        'div[class*="SubmitButton"]',
        'button[class*="submit"]',
    ]

    for sel in submit_selectors:
        try:
            btn = await page.wait_for_selector(sel, timeout=2000)
            if btn:
                await btn.click()
                break
        except PlaywrightTimeout:
            continue
    else:
        # Fallback: press Enter
        await page.keyboard.press("Enter")

    await asyncio.sleep(2)
    return True, "Comment posted successfully"


async def verify_setup(session_id: str, video_url: str, headless: bool = False) -> None:
    """
    Dry run: open browser, navigate to video, check if comment input is found.
    Does NOT post anything. Use this to confirm the bot works before you have accounts ready.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent=DEFAULT_UA,
            viewport={"width": 1280, "height": 720},
            locale="en-US",
        )

        if session_id:
            await context.add_cookies([{
                "name": "sessionid",
                "value": session_id,
                "domain": ".tiktok.com",
                "path": "/",
            }])

        page = await context.new_page()
        video_id = extract_video_id(video_url)
        full_url = video_url if video_url.startswith("http") else f"https://www.tiktok.com/@{video_id}/video/{video_id}"

        print("\n[VERIFY] Opening browser and navigating to video...")
        try:
            await page.goto(full_url, wait_until="domcontentloaded", timeout=20000)
        except PlaywrightTimeout:
            print("[VERIFY] Page load timed out.")
            await browser.close()
            return

        await asyncio.sleep(2)

        # Check if we see "Log in" (means not logged in)
        content = await page.content()
        if "Log in" in content or "log in" in content:
            if not session_id:
                print("\n[VERIFY] You're not logged in. TikTok shows 'Log in' — expected without sessionid.")
                print("         Create a free TikTok account, get sessionid, then run verify again.")
            else:
                print("\n[VERIFY] Page shows 'Log in' — your sessionid may be invalid or expired.")
                print("         Re-copy sessionid from TikTok.com (F12 → Application → Cookies).")

        # Try to find comment input
        selectors = [
            '[data-e2e="comment-input"]',
            '[contenteditable="true"]',
            'textarea[placeholder*="comment" i]',
            'textarea[placeholder*="Add" i]',
            '[class*="comment-input"]',
            'div[role="textbox"]',
        ]

        found = None
        for sel in selectors:
            try:
                el = await page.wait_for_selector(sel, timeout=2000)
                if el:
                    found = sel
                    break
            except PlaywrightTimeout:
                continue

        print()
        if found:
            print("[VERIFY] ✓ Found comment input! The bot should work.")
            print(f"         Selector: {found}")
        else:
            print("[VERIFY] ✗ Could not find comment input.")
            print("         Possible causes: not logged in, TikTok changed their page, or video is private.")
        print("\n[VERIFY] Browser will stay open 5 seconds so you can see the page...")
        await asyncio.sleep(5)
        await browser.close()


async def run_bot(
    session_id: str,
    video_url: str,
    comments: list[str],
    headless: bool = True,
    use_cookie: bool = True,
) -> None:
    """Run the comment bot: open browser, inject session, post comment(s)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent=DEFAULT_UA,
            viewport={"width": 1280, "height": 720},
            locale="en-US",
        )

        if use_cookie and session_id:
            await context.add_cookies([
                {
                    "name": "sessionid",
                    "value": session_id,
                    "domain": ".tiktok.com",
                    "path": "/",
                }
            ])

        page = await context.new_page()
        comment = random.choice(comments) if comments else "Nice video!"
        ok, msg = await post_comment(page, video_url, comment, headless)
        await browser.close()

        if ok:
            print(f"[OK] {msg}")
        else:
            print(f"[ERR] {msg}")
            sys.exit(1)


def main():
    verify_mode = "--verify" in sys.argv or "-v" in sys.argv

    cfg = load_config()
    session_id = cfg.get("session_id") or os.environ.get("TIKTOK_SESSION_ID")
    comments = cfg.get("comments", ["Fire! 🔥", "Love this!"])

    if verify_mode:
        print("=== TikTok Comment Bot — VERIFY MODE (no comment will be posted) ===\n")
        if not session_id:
            session_id = input("Sessionid (or Enter to test without — you'll see 'Log in'): ").strip()
        video_url = input("TikTok video URL >> ").strip()
        if not video_url:
            print("No URL provided.")
            sys.exit(1)
        asyncio.run(verify_setup(session_id or "", video_url, headless=False))
        return

    if not session_id:
        print("No session_id found.")
        print("  Option 1: Set TIKTOK_SESSION_ID env var")
        print("  Option 2: Create comment_config.json with 'session_id' and 'comments'")
        print()
        print("  Get sessionid: TikTok.com → F12 → Application → Cookies → sessionid")
        print()
        session_id = input("Paste sessionid (or Enter to skip and try without): ").strip()
        if session_id:
            cfg["session_id"] = session_id
            cfg.setdefault("comments", comments)
            save_config(cfg)

    if not session_id:
        print("Running without session — you may need to log in manually in the browser window.")

    video_url = input("TikTok video URL >> ").strip()
    if not video_url:
        print("No URL provided.")
        sys.exit(1)

    asyncio.run(
        run_bot(
            session_id=session_id or "",
            video_url=video_url,
            comments=comments,
            headless=cfg.get("headless", False),
            use_cookie=bool(session_id),
        )
    )


if __name__ == "__main__":
    main()
