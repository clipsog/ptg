from flask import Flask, render_template, request, jsonify
import requests
import json
import threading
import time
import os
import re

app = Flask(__name__)

# Keep-alive mechanism to prevent Render from spinning down
def keep_alive():
    """Ping the app every 5 minutes to keep it awake"""
    while True:
        try:
            time.sleep(300)  # Wait 5 minutes
            # Ping the health check endpoint
            if os.environ.get('RENDER'):
                # Only run keep-alive on Render
                try:
                    requests.get(f"https://{os.environ.get('RENDER_SERVICE_NAME', 'ptg')}.onrender.com/health", timeout=10)
                except:
                    pass
        except:
            pass

# Start keep-alive thread if on Render
if os.environ.get('RENDER'):
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()

def parse_response(response):
    """Parse API response and extract status and cooldown info"""
    result = {
        'status': 'unknown',
        'message': '',
        'cooldown': None,
        'raw_response': ''
    }
    
    try:
        # Try to get response text, handling encoding issues
        try:
            response_text = response.text.strip()
        except:
            # If text decoding fails, try different encodings
            try:
                response_text = response.content.decode('utf-8', errors='ignore').strip()
            except:
                response_text = response.content.decode('latin-1', errors='ignore').strip()
        
        result['raw_response'] = response_text
        
        # Try to parse as JSON first
        try:
            data = response.json()
            if isinstance(data, dict):
                # Look for all possible keys
                for key, value in data.items():
                    key_lower = str(key).lower()
                    value_str = str(value).lower()
                    
                    # Check for cooldown information
                    if 'cooldown' in key_lower:
                        result['cooldown'] = str(value)
                    elif 'wait' in key_lower or 'time' in key_lower or 'delay' in key_lower:
                        if 'cooldown' in value_str or 'minute' in value_str or 'hour' in value_str or 'second' in value_str:
                            result['cooldown'] = str(value)
                    
                    # Check for status
                    if any(word in key_lower for word in ['success', 'status', 'order', 'result']):
                        if 'success' in value_str or 'ok' in value_str or 'created' in value_str or 'accepted' in value_str:
                            result['status'] = 'success'
                        elif 'error' in value_str or 'fail' in value_str or 'denied' in value_str:
                            result['status'] = 'failed'
                        elif 'cooldown' in value_str or 'wait' in value_str:
                            result['status'] = 'cooldown'
                            result['cooldown'] = str(value)
                        result['message'] = str(value)
                    elif 'message' in key_lower or 'msg' in key_lower:
                        result['message'] = str(value)
                        # Check if message contains cooldown info
                        if 'cooldown' in value_str or 'wait' in value_str:
                            result['cooldown'] = str(value)
        except (json.JSONDecodeError, ValueError):
            # Not JSON, parse as text
            response_text_lower = response_text.lower()
            
            # Look for cooldown patterns in text
            import re
            cooldown_patterns = [
                r'cooldown[:\s]+([0-9]+\s*(?:minute|hour|second|day|week)s?)',
                r'wait[:\s]+([0-9]+\s*(?:minute|hour|second|day|week)s?)',
                r'(\d+\s*(?:minute|hour|second|day|week)s?\s*(?:cooldown|wait))',
            ]
            
            for pattern in cooldown_patterns:
                match = re.search(pattern, response_text_lower)
                if match:
                    result['cooldown'] = match.group(1).strip()
                    break
            
            # Check for status in text
            if 'cooldown' in response_text_lower or 'wait' in response_text_lower:
                if result['status'] == 'unknown':
                    result['status'] = 'cooldown'
                if not result['cooldown']:
                    # Extract any time mentioned
                    time_match = re.search(r'(\d+\s*(?:minute|hour|second|day|week)s?)', response_text_lower)
                    if time_match:
                        result['cooldown'] = time_match.group(1).strip()
            elif 'success' in response_text_lower or ('order' in response_text_lower and 'created' in response_text_lower):
                result['status'] = 'success'
            elif 'error' in response_text_lower or 'failed' in response_text_lower:
                result['status'] = 'failed'
        
        # Check HTTP status code
        if response.status_code == 200:
            if result['status'] == 'unknown':
                # If we got 200 but couldn't parse, assume success
                result['status'] = 'success'
                if not result['message']:
                    result['message'] = 'Request completed successfully'
        elif response.status_code != 200:
            result['status'] = 'failed'
            if not result['message']:
                result['message'] = f'HTTP {response.status_code}'
        
        # If we found cooldown but status is unknown, set it appropriately
        if result['cooldown'] and result['status'] == 'unknown':
            result['status'] = 'cooldown'
            
    except Exception as e:
        result['status'] = 'error'
        result['message'] = str(e)
    
    return result

def make_request(service_id, url, vid_id=None, username=None, post_id=None, tweet_id=None, link=None):
    """Make API request to zefame"""
    endpoint = 'https://app.zefame.com/api_free.php?action=order'
    
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "connection": "keep-alive",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "host": "app.zefame.com",
        "origin": "https://zefame.com",
        "referer": "https://zefame.com/",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Microsoft Edge\";v=\"144\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
    }
    
    payload = {"service": str(service_id), "link": url}
    
    # Add service-specific fields
    if vid_id:
        payload["videoId"] = vid_id
    if username:
        payload["username"] = username
    if post_id:
        payload["postId"] = post_id
    if tweet_id:
        payload["tweetId"] = tweet_id
    if link:
        payload["link"] = link
    
    # Add UUIDs based on service
    uuids = {
        "229": "8c79ac73-cdc9-4e07-bb0e-9fef32df490b",  # TikTok Views
        "232": "d306834e-ea98-4d9a-b961-fcb3850ed777",  # TikTok Likes
        "228": "51f635bc-9dfa-44d2-884b-143a7bf65e82",  # TikTok Followers
        "235": "5ff7fa13-cc21-4799-9945-fd0daa4ab8e2",  # TikTok Shares
        "236": "3d5100c2-d588-487f-911e-7d0480b9693e",  # TikTok Favorites
        "237": "f105daef-f7a2-45a7-b9a2-4f9e0ce1e02e",  # Instagram Views
        "234": "dc3ec9ae-f285-45d7-a75b-7f98a639b56e",  # Instagram Likes
        "233": "01766496-0d5a-4679-ac6c-ad9f056c36b8",  # Instagram Followers
        "238": "5d01c302-81d1-4bf9-ba9c-f21b3cef6073",  # Instagram Story Views
        "231": "eb12e5db-1b8c-40b9-b5c4-b00f0ce4e924",  # Twitter Views
        "242": "3c142a02-35ba-408a-8517-3b0c59ee481e",  # Facebook Post Likes
        "244": "7e08d929-a29e-44d7-9fb8-edd9553653d8",  # Facebook Followers
        "246": "f0ae8f7f-dc25-4711-9667-1cf384d35214",  # YouTube Likes
        "248": "b16a3020-40a7-4414-938a-12d9a5c0c698",  # Telegram Views
    }
    
    if str(service_id) in uuids:
        payload["uuid"] = uuids[str(service_id)]
    
    try:
        # Make request with automatic decompression
        r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
        
        # Ensure response is properly decoded
        # Requests should handle gzip automatically, but let's be explicit
        if r.headers.get('content-encoding') == 'gzip':
            import gzip
            try:
                r._content = gzip.decompress(r.content)
                r._content_consumed = True
            except:
                pass
        
        return parse_response(r)
    except requests.exceptions.ConnectionError:
        return {'status': 'error', 'message': 'Could not connect to the server. Please check your internet connection.'}
    except requests.exceptions.Timeout:
        return {'status': 'error', 'message': 'Request timed out. Please try again later.'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tiktok-download', methods=['POST'])
def tiktok_download():
    """Download TikTok video without watermark"""
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid request data'}), 400
            
        url = data.get('url')
        
        if not url:
            return jsonify({'status': 'error', 'message': 'Missing URL'}), 400
        
        # Use a simpler, more reliable method - use an external API service
        # Since TikTok's direct API is unreliable, we'll use a proxy service
        try:
            # Try using tiklydown API (free service)
            api_endpoint = "https://tiklydown.com/api/download"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/json',
            }
            
            payload = {'url': url}
            
            response = requests.post(api_endpoint, json=payload, headers=headers, timeout=20)
            
            if response.status_code == 200:
                try:
                    api_data = response.json()
                    if api_data.get('status') == 'success' or api_data.get('video'):
                        video_url = api_data.get('video') or api_data.get('videoUrl') or api_data.get('url')
                        if video_url:
                            return jsonify({
                                'status': 'success',
                                'video_url': video_url,
                                'title': api_data.get('title', 'TikTok Video'),
                                'author': api_data.get('author', {}).get('name', 'Unknown') if isinstance(api_data.get('author'), dict) else api_data.get('author', 'Unknown')
                            })
                except:
                    pass
            
            # Fallback: Try alternative API
            alt_endpoint = "https://api.tiklydown.eu.org/api/download"
            response = requests.post(alt_endpoint, json=payload, headers=headers, timeout=20)
            
            if response.status_code == 200:
                try:
                    api_data = response.json()
                    if api_data.get('status') == 'success' or api_data.get('video'):
                        video_url = api_data.get('video') or api_data.get('videoUrl') or api_data.get('url')
                        if video_url:
                            return jsonify({
                                'status': 'success',
                                'video_url': video_url,
                                'title': api_data.get('title', 'TikTok Video'),
                                'author': api_data.get('author', 'Unknown')
                            })
                except:
                    pass
            
            # If all APIs fail, provide helpful message
            return jsonify({
                'status': 'error',
                'message': 'Unable to download video. Please try: https://ssstik.io or https://snapany.com/tiktok'
            }), 400
            
        except requests.exceptions.RequestException as e:
            return jsonify({
                'status': 'error',
                'message': f'Network error. Please try: https://ssstik.io or https://snapany.com/tiktok'
            }), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint to keep the app alive"""
    return jsonify({'status': 'ok', 'message': 'Service is running'}), 200

@app.route('/api/order', methods=['POST'])
def create_order():
    data = request.json
    service_id = data.get('service_id')
    url = data.get('url')
    
    if not service_id or not url:
        return jsonify({'status': 'error', 'message': 'Missing service_id or url'}), 400
    
    # Extract IDs based on service type
    vid_id = None
    username = None
    post_id = None
    tweet_id = None
    
    if service_id in ['229', '232', '235', '236']:  # TikTok video services
        vid_id = url.split("/")[-1].rstrip("/").split("?")[0]
    elif service_id == '228':  # TikTok Followers
        username = url.split("/")[-1].lstrip("@")
    elif service_id in ['237', '234']:  # Instagram post services
        post_id = url.split("/")[-2]
    elif service_id in ['233', '238']:  # Instagram profile services
        username = url.split("/")[-1].split("?")[0]
    elif service_id == '231':  # Twitter
        tweet_id = url.split("/")[-1].split("?")[0]
    elif service_id == '242':  # Facebook Post Likes
        username = url.split("/")[-2].split("?")[0]
    elif service_id == '244':  # Facebook Followers
        username = url.split("id=", 1)[1].split("&", 1)[0] if "id=" in url else url.split("/")[-1].split("?")[0]
    elif service_id == '246':  # YouTube
        vid_id = url.split("v=")[1].split("&")[0]
    elif service_id == '248':  # Telegram
        pass  # No extra ID needed
    
    result = make_request(service_id, url, vid_id, username, post_id, tweet_id)
    return jsonify(result)

# Vercel requires a handler function
handler = app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 3002))
    print(f"Starting Flask app on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
