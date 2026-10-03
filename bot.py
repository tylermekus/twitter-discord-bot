import asyncio, requests, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from twikit import Client

WEBHOOK_URL = "https://discord.com/api/webhooks/1555668009085837454/n4MSvBnRQOq5RuzsItVaPp4sPKtq0NtkTNO6NYN8d2KDQ9W3-qasSu2_zkPz-IyjkR7J"
TARGET_HANDLE = "IGN"

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

threading.Thread(target=run_web_server, daemon=True).start()

client = Client('en-US')
seen_tweet_ids = set()

async def main():
    print("Starting bot loop...")
    user_id = None
    
    while True:
        try:
            # 1. Convert handle to user ID if not fetched yet
            if not user_id:
                user = await client.get_user_by_screen_name(TARGET_HANDLE)
                user_id = user.id
                print(f"Target acquired: {TARGET_HANDLE} (ID: {user_id})")

            # 2. Fetch tweets using numeric ID
            tweets = await client.get_user_tweets(user_id, 'Tweets')
            if tweets:
                latest = tweets[0]
                if latest.id not in seen_tweet_ids:
                    tweet_url = f"https://x.com/{TARGET_HANDLE}/status/{latest.id}"
                    print(f"Sending tweet to Discord: {tweet_url}")
                    requests.post(WEBHOOK_URL, json={"content": tweet_url})
                    seen_tweet_ids.add(latest.id)
        except Exception as e:
            print(f"Error checking tweets: {e}")
            
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
