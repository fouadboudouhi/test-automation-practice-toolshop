import time
import requests

def wait_for_http(url: str, timeout_s: int = 30) -> None:
    end = time.time() + timeout_s
    last_err = None
    while time.time() < end:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return
        except Exception as e:
            last_err = e
        time.sleep(0.5)
    raise RuntimeError(f"Service did not become ready in {timeout_s}s. Last error: {last_err}")
