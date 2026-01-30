# zefame

a zefame aio thats fully requests based

use this bot through the cmd promot using python zefame.py so that you can see it actually works since im to lazy and made it only send 1 requests then auto close the python terminal (if opened is py terminal and not cmd)

ill make it more requests when i get bored again at some point

---

## TikTok Custom Comment Bot

Post custom comments from your TikTok account — **no paid signatures** needed. Uses Playwright (real browser + session cookie).

### Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

### Get Session Cookie

1. Log in at [tiktok.com](https://www.tiktok.com)
2. F12 → Application → Cookies → `sessionid`
3. Copy the value

### Run

**Option 1:** From zefame menu → `[15] TikTok Custom Comment Bot`

**Option 2:** Standalone:

```bash
python comment_bot.py
```

### Verify Before You Have Accounts

Run **verify mode** to confirm the bot can find the comment input (no comment is posted):

```bash
python comment_bot.py --verify
# or
python comment_bot.py -v
```

- Without sessionid: opens a video, shows "Log in" (expected)
- With sessionid: checks if comment box is found — if yes, you're ready to post

### Config (optional)

Copy `comment_config.example.json` → `comment_config.json` and add your `session_id` and custom `comments` list. The bot picks randomly from your list.
