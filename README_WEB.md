# Zefame Web App

A web-based interface for the Zefame social media booster, accessible from any device including mobile phones.

## Features

- 📱 Mobile-friendly responsive design
- 🌐 Web-based interface accessible from anywhere
- ⚡ Fast and easy to use
- 📊 Real-time order status and cooldown information

## Deployment on Render

### Step 1: Push to GitHub

1. Initialize git repository (if not already):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Create a new repository on GitHub and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/zefame.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: zefame (or any name you prefer)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click "Create Web Service"

### Step 3: Access Your App

Once deployed, Render will provide you with a URL like:
`https://zefame.onrender.com`

You can access this from any device, including your phone!

## Local Development

To run locally:

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000` in your browser.

## Files Structure

- `app.py` - Flask web application
- `templates/index.html` - Web interface
- `requirements.txt` - Python dependencies
- `render.yaml` - Render deployment configuration

## Notes

- The app uses gunicorn for production deployment
- Make sure all dependencies are listed in `requirements.txt`
- The web app uses the same API endpoints as the CLI version
