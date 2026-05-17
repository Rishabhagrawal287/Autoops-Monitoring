import psutil
import requests
import time
import socket

# ── Configuration ──────────────────────────────────────────────
SERVER_NAME  = socket.gethostname()
API_BASE     = "http://127.0.0.1:8000"
INGEST_URL   = f"{API_BASE}/ingest"
TOKEN_URL    = f"{API_BASE}/token"
INTERVAL     = 5       # seconds between metric sends
USERNAME     = "admin"
PASSWORD     = "secret"  # change this if you changed the password

# ── Retry settings ─────────────────────────────────────────────
RETRY_INITIAL   = 5    # first retry after 5 seconds
RETRY_MAX       = 60   # never wait longer than 60 seconds
RETRY_BACKOFF   = 2    # multiply wait time by this each retry

# ── Auth token ─────────────────────────────────────────────────
token = None

def get_token():
    """Log in and get a JWT token from the API."""
    global token
    wait = RETRY_INITIAL
    while True:
        try:
            response = requests.post(TOKEN_URL, data={
                "username": USERNAME,
                "password": PASSWORD
            }, timeout=5)
            if response.status_code == 200:
                token = response.json()["access_token"]
                print(f"[{SERVER_NAME}] authenticated successfully")
                return
            else:
                print(f"[{SERVER_NAME}] auth failed: {response.status_code} — retrying in {wait}s")
        except Exception as e:
            print(f"[{SERVER_NAME}] cannot reach API: {e} — retrying in {wait}s")
        time.sleep(wait)
        wait = min(wait * RETRY_BACKOFF, RETRY_MAX)

def collect_metrics():
    """Collect current system metrics."""
    return {
        "server_name": SERVER_NAME,
        "cpu":    psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk":   psutil.disk_usage('/').percent
    }

def send_metrics(data):
    """
    Send metrics to the API with exponential backoff retry.
    If the token is expired (401), re-authenticate and retry once.
    If the API is unreachable, keep retrying with backoff up to RETRY_MAX.
    """
    global token
    wait = RETRY_INITIAL
    attempts = 0

    while True:
        try:
            response = requests.post(
                INGEST_URL,
                json=data,
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )

            if response.status_code == 200:
                print(f"[{SERVER_NAME}] metrics sent — CPU: {data['cpu']}% | MEM: {data['memory']}% | DISK: {data['disk']}%")
                return  # success — exit retry loop

            elif response.status_code == 401:
                print(f"[{SERVER_NAME}] token expired — re-authenticating")
                get_token()
                wait = RETRY_INITIAL  # reset backoff after re-auth

            elif response.status_code == 429:
                print(f"[{SERVER_NAME}] rate limited — waiting {wait}s")
                time.sleep(wait)
                wait = min(wait * RETRY_BACKOFF, RETRY_MAX)

            else:
                print(f"[{SERVER_NAME}] unexpected status {response.status_code} — retrying in {wait}s")
                time.sleep(wait)
                wait = min(wait * RETRY_BACKOFF, RETRY_MAX)

        except requests.exceptions.ConnectionError:
            attempts += 1
            print(f"[{SERVER_NAME}] API unreachable (attempt {attempts}) — retrying in {wait}s")
            time.sleep(wait)
            wait = min(wait * RETRY_BACKOFF, RETRY_MAX)

        except requests.exceptions.Timeout:
            attempts += 1
            print(f"[{SERVER_NAME}] request timed out (attempt {attempts}) — retrying in {wait}s")
            time.sleep(wait)
            wait = min(wait * RETRY_BACKOFF, RETRY_MAX)

        except Exception as e:
            print(f"[{SERVER_NAME}] unexpected error: {e} — retrying in {wait}s")
            time.sleep(wait)
            wait = min(wait * RETRY_BACKOFF, RETRY_MAX)

# ── Main loop ──────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[{SERVER_NAME}] AutoOps agent starting...")
    get_token()  # authenticate on startup
    while True:
        metrics = collect_metrics()
        send_metrics(metrics)
        time.sleep(INTERVAL)