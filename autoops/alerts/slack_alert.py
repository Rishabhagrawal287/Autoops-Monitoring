import requests


class SlackAlert:

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send(self, message):

        payload = {"text": message}

        try:
            response = requests.post(self.webhook_url, json=payload)

            if response.status_code != 200:
                print(f"Slack alert failed: {response.text}")

        except Exception as e:
            print(f"Slack alert error: {e}")