import asyncio, requests, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from twikit import Client

WEBHOOK_URL = "https://discord.com/api/webhooks/1555668009085837454/n4MSvBnRQOq5RuzsItVaPp4sPKtq0NtkTNO6NYN8d2KDQ9W3-qasSu2_zkPz-IyjkR7J"
TARGET_HANDLE = "IGN"

# Dummy HTTP server so Render health check passes (supports GET & HEAD)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

# Start health check server in background thread
threading.Thread(target=run_web_server, daemon=True).start()

client = Client('en-US')
seen_tweet_ids = set()

async def main():
    while True:
        try:
            # Twikit functions must be awaited
            tweets = await client.get_user_tweets(TARGET_HANDLE, 'Tweets')
            if tweets:
                latest = tweets[0]
                if latest.id not in seen_tweet_ids:
                    if seen_tweet_ids:  # Skip sending the baseline post on boot
                        tweet_url = f"https://x.com/{TARGET_HANDLE}/status/{latest.id}"
                        requests.post(WEBHOOK_URL, json={"content": tweet_url})
                    seen_tweet_ids.add(latest.id)
        except Exception as e:
            print(f"Error checking tweets: {e}")
            
        await asyncio.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    asyncio.run(main())
