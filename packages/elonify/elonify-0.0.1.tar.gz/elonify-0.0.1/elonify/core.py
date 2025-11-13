import requests
from bs4 import BeautifulSoup
import re

class ElonResponse:
    def __init__(self, response):
        self.raw = response
        self.text = response.text
        self.status = response.status_code
        self.headers = response.headers

        # Try detect content type
        ctype = response.headers.get("Content-Type", "").lower()
        if "json" in ctype:
            try:
                self.json = response.json()
            except Exception:
                self.json = None
            self.html = None
        elif "<html" in self.text.lower():
            self.html = BeautifulSoup(self.text, "html.parser")
            self.json = None
        else:
            self.json = None
            self.html = None

    def find(self, pattern):
        return re.findall(pattern, self.text)

def get(url, **kwargs):
    """Smart GET request that returns an ElonResponse."""
    res = requests.get(url, **kwargs)
    return ElonResponse(res)
