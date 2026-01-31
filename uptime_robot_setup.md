# Keep Render App Alive - Setup Instructions

Render's free tier spins down services after 15 minutes of inactivity. Here are ways to keep it alive:

## Option 1: Use UptimeRobot (Recommended - Free)

1. Go to [UptimeRobot.com](https://uptimerobot.com) and sign up (free)
2. Click "Add New Monitor"
3. Configure:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: Zefame Keep-Alive
   - **URL**: `https://YOUR_APP_NAME.onrender.com/health`
   - **Monitoring Interval**: 5 minutes
4. Click "Create Monitor"

UptimeRobot will ping your app every 5 minutes, keeping it awake!

## Option 2: Use cron-job.org (Free)

1. Go to [cron-job.org](https://cron-job.org) and sign up
2. Create a new cron job:
   - **Title**: Keep Render Alive
   - **Address**: `https://YOUR_APP_NAME.onrender.com/health`
   - **Schedule**: Every 5 minutes (`*/5 * * * *`)
3. Save the cron job

## Option 3: Use PythonAnywhere (Free)

If you have a PythonAnywhere account, you can create a simple script:

```python
import requests
import time

while True:
    requests.get('https://YOUR_APP_NAME.onrender.com/health')
    time.sleep(300)  # 5 minutes
```

## What the /health endpoint does

The app now has a `/health` endpoint that returns:
```json
{"status": "ok", "message": "Service is running"}
```

This endpoint is lightweight and perfect for keep-alive pings.

## Note

The built-in keep-alive mechanism in the code will only work if you're on Render (checks for `RENDER` environment variable). For best results, use an external service like UptimeRobot.
