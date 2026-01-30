import requests, time, sys, os, json
from pystyle import *

def handle_response(response, service_name):
    """Parse and display API response with success status and cooldown info"""
    print("\n" + "="*60)
    print(f"Response for {service_name}:")
    print("="*60)
    
    try:
        # Get response text - requests automatically decompresses gzip/deflate
        # But if encoding is wrong, try to fix it
        try:
            response_text = response.text
            # If text looks like binary garbage, try to detect encoding
            if not response_text or any(ord(c) > 127 and c not in response_text[:100] for c in response_text[:100] if len(response_text) > 100):
                # Try to decode with different encodings
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                    try:
                        response_text = response.content.decode(encoding)
                        break
                    except:
                        continue
        except:
            # Fallback: decode with error handling
            response_text = response.content.decode('utf-8', errors='ignore')
        
        # Clean up the response text
        response_text = response_text.strip()
        
        # Try to parse as JSON first
        try:
            data = response.json()
        except (json.JSONDecodeError, ValueError):
            data = None
        
        # Display the response data
        if data is not None and isinstance(data, dict):
            # Check for success indicators
            has_success = False
            
            for key, value in data.items():
                key_lower = str(key).lower()
                value_str = str(value).lower()
                
                # Check if it's a success message
                if any(word in key_lower for word in ['success', 'status', 'order']):
                    if 'success' in value_str or 'ok' in value_str or 'created' in value_str or 'accepted' in value_str:
                        has_success = True
                        print(f"✓ Status: SUCCESS")
                    elif 'error' in value_str or 'fail' in value_str or 'denied' in value_str:
                        print(f"✗ Status: FAILED")
                    else:
                        print(f"  {key}: {value}")
                elif 'cooldown' in key_lower or 'wait' in key_lower or 'time' in key_lower:
                    print(f"⏱  Cooldown: {value}")
                elif 'message' in key_lower:
                    print(f"  Message: {value}")
                else:
                    print(f"  {key}: {value}")
            
            # If we couldn't determine success from structure, check the text
            if not has_success:
                response_text_lower = response_text.lower()
                if 'success' in response_text_lower or 'order created' in response_text_lower or 'accepted' in response_text_lower:
                    print("✓ Status: SUCCESS")
                elif 'error' in response_text_lower or 'failed' in response_text_lower or 'denied' in response_text_lower:
                    print("✗ Status: FAILED")
        else:
            # Not JSON, try to extract meaningful info from text
            response_text_lower = response_text.lower()
            
            # Check for common success/error patterns
            if 'success' in response_text_lower or ('order' in response_text_lower and 'created' in response_text_lower):
                print("✓ Status: SUCCESS")
            elif 'error' in response_text_lower or 'failed' in response_text_lower or 'denied' in response_text_lower:
                print("✗ Status: FAILED")
            elif 'cooldown' in response_text_lower:
                print("⏱  Cooldown information found in response")
            
            # Show the response (limit length if too long, and only if it's readable)
            if response_text and len(response_text) < 1000 and all(ord(c) < 128 or c.isprintable() for c in response_text[:200]):
                if len(response_text) > 500:
                    print(f"Response: {response_text[:500]}...")
                else:
                    print(f"Response: {response_text}")
            else:
                # Response seems to be binary or unreadable
                print("Response received (binary/unreadable format)")
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    print("✓ Status: Request completed (200 OK)")
                else:
                    print(f"✗ Status: HTTP {response.status_code}")
            
    except Exception as e:
        # Fallback: show status code and basic info
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✓ Status: Request completed (200 OK)")
        else:
            print(f"✗ Status: HTTP {response.status_code}")
        print(f"\nNote: Could not parse response format - {str(e)}")
    
    print("="*60)
    input("\nPress Enter to return to menu...")

class TikTok:
    def views():
        url = input("enter your tiktok video url >> ")
        vid_id = url.split("/")[-1].rstrip("/").split("?")[0]
        #print(vid_id)   <<<<<this is js to make sure you get the correct video id not required to be here tho>>>>>

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "160",
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


        payload = {
            "service": "229",
            "link": url,
            "uuid": "8c79ac73-cdc9-4e07-bb0e-9fef32df490b",
            "videoId": vid_id
        }

        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "TikTok Views")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

    def likes():
        url = input("enter your tiktok video url >> ")
        vid_id = url.split("/")[-1].rstrip("/").split("?")[0]

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "160",
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



        payload = {
            "service": "232",
            "link": url,
            "uuid": "d306834e-ea98-4d9a-b961-fcb3850ed777",
            "videoId": vid_id
        }

        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "TikTok Likes")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

    def followers():
        profile = input("enter your tiktok profile url >> ")
        username = profile.split("/")[-1].lstrip("@")
        #print(profile_id)   <<<<<ones again this is not needed nor required its js to see if you get the correct username extracted>>>>>

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "121",
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


        payload = {
            "service": "228",
            "link": profile,
            "uuid": "51f635bc-9dfa-44d2-884b-143a7bf65e82",
            "username": username
        }

        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "TikTok Followers")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

    def shares():
        url = input("enter your tiktok video url >> ")
        vid_id = url.split("/")[-1].rstrip("/").split("?")[0]

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "160",
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

        payload = {
            "service": "235",
            "link": url,
            "uuid": "5ff7fa13-cc21-4799-9945-fd0daa4ab8e2",
            "videoId": vid_id
        }

        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "TikTok Shares")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

    def favorites():
        url = input("enter your tiktok video url >> ")
        vid_id = url.split("/")[-1].rstrip("/").split("?")[0]

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "160",
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


        payload = {
            "service": "236",
            "link": url,
            "uuid": "3d5100c2-d588-487f-911e-7d0480b9693e",
            "videoId": vid_id
        }

        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "TikTok Favorites")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

class Instagram:
    def views():
        url = input("enter your instagram post url >> ")
        vid_id = url.split("/")[-2]
        #print(vid_id)   <<<<<ones again this is not required it is js to see if you get the correct id>>>>>

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "133",
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

        payload = {
            "service": "237",
            "link": url,
            "uuid": "f105daef-f7a2-45a7-b9a2-4f9e0ce1e02e",
            "postId": vid_id
        }

        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "Instagram Views")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

    def likes():
        url = input("enter your instagram post url >> ")
        vid_id = url.split("/")[-2]

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "133",
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


        payload = {
            "service": "234",
            "link": url,
            "uuid": "dc3ec9ae-f285-45d7-a75b-7f98a639b56e",
            "postId": vid_id
        }

        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "Instagram Likes")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

    def followers():
        profile = input("enter your instagram profile url >> ")
        username = profile.split("/")[-1].split("?")[0]
        #print(username)   <<<<ones again this is not required it is js to see if you get the correct username of the profile you use>>>>>

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "125",
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


        payload = {
            "service": "233",
            "link": profile,
            "uuid": "01766496-0d5a-4679-ac6c-ad9f056c36b8",
            "username": username
        }


        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "Instagram Followers")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

    def story_views():
        profile = input("enter your instagram profile url >> ")
        username = profile.split("/")[-1].split("?")[0]

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "125",
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


        payload = {
            "service": "238",
            "link": profile,
            "uuid": "5d01c302-81d1-4bf9-ba9c-f21b3cef6073",
            "username": username
        }


        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "Instagram Story Views")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

class Twitter:
    def views():
        url = input("enter your twitter post url >> ")
        id = url.split("/")[-1].split("?")[0]
        #print(id)     <<<<<this is not required it is js to see if it returns the correct id of the video you used>>>>>

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "156",
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


        payload = {
            "service": "231",
            "link": url,
            "uuid": "eb12e5db-1b8c-40b9-b5c4-b00f0ce4e924",
            "tweetId": id
        }


        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "Twitter Views")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

class Facebook:
    def post_likes():
        url = input("enter your facebook post url >> ")
        username = url.split("/")[-2].split("?")[0]
        #print(username)   <<<<<this is still not required only uncomment it if u need to see the id to the facebook post>>>>>

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "157",
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

        payload = {
            "service": "242",
            "link": url,
            "uuid": "3c142a02-35ba-408a-8517-3b0c59ee481e",
            "username": username
        }

        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "Facebook Post Likes")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

    def followers():
        url = input("enter your facebook profile url >> ")
        user = url.split("id=", 1)[1].split("&", 1)[0] if "id=" in url else url.split("/")[-1].split("?")[0]
        #print(user)   <<<<<not needed js to see if it extracts the right things ones again>>>>>

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "149",
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


        payload = {
            "service": "244",
            "link": url,
            "uuid": "7e08d929-a29e-44d7-9fb8-edd9553653d8",
            "username": user
        }


        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "Facebook Followers")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

class YouTube:
    def likes():
        url = input("enter your youtube video url >> ")
        id = url.split("v=")[1].split("&")[0]
        #print(id)   <<<<< this still isnt needed unless your making sure it gets the correct id>>>>>

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "134",
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

        payload = {
            "service": "246",
            "link": url,
            "uuid": "f0ae8f7f-dc25-4711-9667-1cf384d35214",
            "videoId": id
        }


        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "YouTube Likes")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

class Telegram:
    def views():
        link = input("enter your telegram post url >> ")

        endpoint = 'https://app.zefame.com/api_free.php?action=order'

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "103",
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


        payload = {
            "service": "248",
            "link": link,
            "uuid": "b16a3020-40a7-4414-938a-12d9a5c0c698"
        }

        try:
            r = requests.post(endpoint, headers=headers, data=payload, timeout=30)
            handle_response(r, "Telegram Views")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("✗ Error: Could not connect to the server.")
            print("  Please check your internet connection.")
            print("="*60)
            input("\nPress Enter to continue...")
        except requests.exceptions.Timeout:
            print("\n" + "="*60)
            print("✗ Error: Request timed out.")
            print("  Please try again later.")
            print("="*60)
            input("\nPress Enter to continue...")
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ Error: {str(e)}")
            print("="*60)
            input("\nPress Enter to continue...")

class all:
    def main():
        # Set window title (Windows only)
        if sys.platform == "win32":
            os.system("Title Social Media Booster Running By Zefame.com | Made By Lucas")
        banner = r"""
                    __                     
                   / _|                    
            _______| |_ __ _ _ __ ___   ___ 
╔═╗ ╗      |_  / _ \  _/ _` | '_ ` _ \ / _ \     ╔═╗ ╗
╔═╬═╝       / /  __/ || (_| | | | | | |  __/     ╔═╬═╝  
╚ ╚═╝      /___\___|_| \__,_|_| |_| |_|\___|     ╚ ╚═╝
                made by unjversql | lucas 
        """

        print(Center.XCenter(banner))

        choices = """
    [1]  TikTok Views              | cooldown = 5 Minutes
    [2]  TikTok Likes              | cooldown = 5 Minutes
    [3]  TikTok Followers          | cooldown = 24 Hours
    [4]  TikTok Shares             | cooldown = 1 Hour
    [5]  TikTok Favorites          | cooldown = 20 Minutes
    [15] TikTok Custom Comment Bot | uses your account
    ====================================================
    [6]  Instagram Views           | cooldown = 5 Minutes
    [7]  Instagram Likes          | cooldown = 3 Hours
    [8]  Instagram Followers      | cooldown = 24 Hours
    [9]  Instagram Story Views    | cooldown = 24 Hours
    ====================================================
    [10] Twitter Views            | cooldown = 20 Minutes
    ====================================================
    [11] Facebook Post Likes      | cooldown = 3 Hours
    [12] Facebook Followers       | cooldown = 12 Hours
    ====================================================
    [13] YouTube Likes            | cooldown = 3 Hours
    ====================================================
    [14] Telegram Views           | cooldown = 30 Minutes
    ====================================================
    [0]  Exit
        """

        print(choices)
        print()
        
        while True:
            choice = input("Enter your choice (or '0' to exit): ")

            if choice == "0":
                print()
                print(Center.XCenter("Exiting... Goodbye!"))
                break
            elif choice == "1":
                TikTok.views()
            elif choice == "2":
                TikTok.likes()
            elif choice == "3":
                TikTok.followers()
            elif choice == "4":
                TikTok.shares()
            elif choice == "5":
                TikTok.favorites()
            elif choice == "15":
                try:
                    import comment_bot
                    comment_bot.main()
                except ImportError:
                    print()
                    print(Center.XCenter("Install: pip install playwright && playwright install chromium"))
                    print(Center.XCenter("Then run: python comment_bot.py"))
                    print()
            elif choice == "6":
                Instagram.views()
            elif choice == "7":
                Instagram.likes()
            elif choice == "8":
                Instagram.followers()
            elif choice == "9":
                Instagram.story_views()
            elif choice == "10":
                Twitter.views()
            elif choice == "11":
                Facebook.post_likes()
            elif choice == "12":
                Facebook.followers()
            elif choice == "13":
                YouTube.likes()
            elif choice == "14":
                Telegram.views()
            else:
                print()
                print(Center.XCenter("Invalid choice! Please try again."))
                print()
                continue
            
            print()
            print(choices)
            print()

if __name__ == "__main__":
    all.main()