import time, requests, threading, feedparser
from http.server import HTTPServer, BaseHTTPRequestHandler

WEBHOOK_URL = "https://discord.com/api/webhooks/1555668009085837454/n4MSvBnRQOq5RuzsItVaPp4sPKtq0NtkTNO6NYN8d2KDQ9W3-qasSu2_zkPz-IyjkR7J"
TARGET_HANDLE = "IGN"  # Switch to CoCVouchers once verified

# Health check server for Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

seen_tweet_ids = set()

def main():
    print("Bot started using RSS bridge...", flush=True)
    rss_url = f"https://nitter.net/{TARGET_HANDLE}/rss"
    
    while True:
        try:
            print(f"Checking RSS feed for @{TARGET_HANDLE}...", flush=True)
            feed = feedparser.parse(rss_url)
            
            if feed.entries:
                latest = feed.entries[0]
                tweet_id = latest.link.split('/')[-1]
                
                print(f"Latest tweet found: {latest.link}", flush=True)
                
                if tweet_id not in seen_tweet_ids:
                    if seen_tweet_ids:  # Send post when a new tweet arrives
                        tweet_url = f"https://x.com/{TARGET_HANDLE}/status/{tweet_id}"
                        print(f"Posting to Discord: {tweet_url}", flush=True)
                        requests.post(WEBHOOK_URL, json={"content": tweet_url})
                    seen_tweet_ids.add(tweet_id)
            else:
                print("No feed entries found. Retrying...", flush=True)

        except Exception as e:
            print(f"Error checking feed: {e}", flush=True)
            
        time.sleep(60)

if __name__ == "__main__":
    main()
