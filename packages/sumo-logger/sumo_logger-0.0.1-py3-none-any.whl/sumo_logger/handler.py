import logging
import json
import requests
import time
from datetime import datetime


class SumoHttpHandler(logging.Handler):
    """
    A custom logging handler that sends log messages to a Sumo Logic HTTP Source
    with retry and exponential backoff.
    """

    def __init__(self, http_source_url, max_retries=5, backoff_factor=1):
        super().__init__()
        if not http_source_url:
            raise ValueError(
                "HTTP Source URL is required for SumoHttpHandler.")
        self.http_source_url = http_source_url
        self.headers = {'Content-Type': 'application/json'}
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def emit(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "funcName": record.funcName,
        }
        json_payload = json.dumps(log_data)

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.http_source_url,
                    data=json_payload,
                    headers=self.headers,
                    timeout=5
                )
                response.raise_for_status()
                return
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    delay = self.backoff_factor * (2 ** attempt)
                    print(
                        f"Rate limit exceeded (429). Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    print(f"HTTP error: {e}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Connection error: {e}")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        print("Maximum retries reached. Log not sent to Sumo Logic.")
