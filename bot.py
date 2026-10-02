import time, requests, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from twikit import Client

WEBHOOK_URL = https://discord.com/api/webhooks/1555668009085837454/n4MSvBnRQOq5RuzsItVaPp4sPKtq0NtkTNO6NYN8d2KDQ9W3-qasSu2_zkPz-IyjkR7J
TARGET_HANDLE = CoCVouchers

# Dummy web server to satisfy Render's free Web Service requirements
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

# Start dummy server in background
threading.Thread(target=run_web_server, daemon=True).start()

client = Client('en-US')
seen_tweet_ids = set()

# Main bot loop
while True:
    try:
        tweets = client.get_user_tweets(TARGET_HANDLE, 'Tweets')
        if tweets:
            latest = tweets[0]
            if latest.id not in seen_tweet_ids:
                if seen_tweet_ids:
                    tweet_url = f"https://x.com/{TARGET_HANDLE}/status/{latest.id}"
                    requests.post(WEBHOOK_URL, json={"content": tweet_url})
                seen_tweet_ids.add(latest.id)
    except Exception as e:
        print(f"Error checking tweets: {e}")
        
    time.sleep(20)
