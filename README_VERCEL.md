# Deploying to Vercel

## Quick Deploy

1. **Install Vercel CLI** (if you want to deploy from command line):
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
vercel
```

Or use the Vercel dashboard:

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository `clipsog/ptg`
4. Vercel will automatically detect the Python/Flask setup
5. Click "Deploy"

## Important Notes

- Vercel is **serverless** - your app will work 24/7 even when your computer is off
- The `vercel.json` file configures the deployment
- Vercel automatically handles routing and serverless functions
- Your app will get a URL like: `https://ptg.vercel.app`

## Files for Vercel

- `vercel.json` - Vercel configuration
- `app.py` - Flask app (with `handler = app` for Vercel)
- `requirements.txt` - Python dependencies

## Comparison: Render vs Vercel

**Render:**
- Traditional server hosting
- Always-on service
- Good for long-running processes
- Free tier available

**Vercel:**
- Serverless functions
- Scales automatically
- Great for web apps
- Free tier with generous limits
- Very fast global CDN

Both are cloud-hosted and work when your computer is off!
