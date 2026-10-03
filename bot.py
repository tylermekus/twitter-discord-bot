import os, time, requests, threading, feedparser
from http.server import HTTPServer, BaseHTTPRequestHandler

WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # set this in Render's Environment tab
RSS_FEED_URL = "https://rss.app/feeds/dfDZVniCUL6gsKXM.xml"
TARGET_HANDLE = "IGN"  # must match the account the feed is for

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
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), HealthCheckHandler).serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

seen = set()
first_run = True

def main():
    global first_run
    while True:
        try:
            print(f"Checking feed for @{TARGET_HANDLE}...", flush=True)
            feed = feedparser.parse(RSS_FEED_URL)

            if not feed.entries:
                print("No entries found. Status:", getattr(feed, "status", "n/a"),
                      "| Error:", feed.get("bozo_exception"), flush=True)
            else:
                # oldest first so tweets post in order
                for entry in reversed(feed.entries):
                    tweet_id = entry.link.split("/")[-1].split("?")[0]
                    if tweet_id in seen:
                        continue
                    seen.add(tweet_id)
                    if not first_run:
                        url = f"https://x.com/{TARGET_HANDLE}/status/{tweet_id}"
                        print("Posting:", url, flush=True)
                        requests.post(WEBHOOK_URL, json={"content": url}, timeout=10)
                first_run = False

        except Exception as e:
            print(f"Error: {e}", flush=True)

        time.sleep(60)

if __name__ == "__main__":
    main()
