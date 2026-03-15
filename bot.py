import os
import json
import time
import requests
import urllib.request
import xml.etree.ElementTree as ET

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
SEEN_FILE       = "seen_videos.json"
RSS_URL         = "https://www.youtube.com/feeds/videos.xml?channel_id=UCB_qr75-ydFVKSF9Dmo6izg"

HIGHLIGHT_KEYWORDS = [
    "race highlights",
    "qualifying highlights",
    "sprint highlights",
    "sprint race highlights",
]

NS = {
    "atom":  "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "yt":    "http://www.youtube.com/xml/schemas/2015",
}

def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_F
