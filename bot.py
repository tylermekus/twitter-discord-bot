import asyncio, requests, threading, sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from twikit import Client

WEBHOOK_URL = "https://discord.com/api/webhooks/1555668009085837454/n4MSvBnRQOq5RuzsItVaPp4sPKtq0NtkTNO6NYN8d2KDQ9W3-qasSu2_zkPz-IyjkR7J"
TARGET_HANDLE = "IGN"  # Currently set to IGN for testing

class HealthCheckHandler(BaseHTTPRequestHandler):
    def handle_http(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is active")

    def do_GET(self):
        self.handle_http()

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        self.handle_http()

    def log_message(self, format, *args):
        return  # Suppress health check spam in logs

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

client = Client('en-US')
seen_tweet_ids = set()

async def main():
    print(f"[{datetime.now()}] Bot starting up...", flush=True)
    user_id = None
    
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        try:
            print(f"[{timestamp}] Checking X for target: {TARGET_HANDLE}...", flush=True)
            
            if not user_id:
                user = await asyncio.wait_for(client.get_user_by_screen_name(TARGET_HANDLE), timeout=15)
                user_id = user.id
                print(f"[{timestamp}] Target acquired: {TARGET_HANDLE} (ID: {user_id})", flush=True)

            tweets = await asyncio.wait_for(client.get_user_tweets(user_id, 'Tweets'), timeout=15)
            if tweets:
                latest = tweets[0]
                print(f"[{timestamp}] Fetched latest tweet ID: {latest.id}", flush=True)
                
                if latest.id not in seen_tweet_ids:
                    tweet_url = f"https://x.com/{TARGET_HANDLE}/status/{latest.id}"
                    print(f"[{timestamp}] Posting new tweet to Discord: {tweet_url}", flush=True)
                    
                    res = requests.post(WEBHOOK_URL, json={"content": tweet_url})
                    print(f"[{timestamp}] Webhook response status: {res.status_code}", flush=True)
                    
                    seen_tweet_ids.add(latest.id)
            else:
                print(f"[{timestamp}] No tweets returned for user ID {user_id}", flush=True)

        except asyncio.TimeoutError:
            print(f"[{timestamp}] Request to X timed out. Retrying next cycle...", flush=True)
        except Exception as e:
            print(f"[{timestamp}] Error during check cycle: {type(e).__name__} - {e}", flush=True)
            
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
