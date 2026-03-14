import os
import json
import urllib.request
import xml.etree.ElementTree as ET

# ─── Config ───────────────────────────────────────────────────────────────────
DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]
SEEN_FILE       = "seen_videos.json"

# Flux RSS public de la chaîne officielle F1 (aucune clé API requise !)
RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCB_qr75-ydFVKSF9Dmo6izg"

HIGHLIGHT_KEYWORDS = [
    "highlights", "highlight", "race highlights",
    "qualifying highlights", "sprint highlights",
    "extended highlights", "top moments", "race edit"
]

NS = {
    "atom":  "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "yt":    "http://www.youtube.com/xml/schemas/2015",
}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def is_highlight(title: str) -> bool:
    return any(kw in title.lower() for kw in HIGHLIGHT_KEYWORDS)

def fetch_rss() -> list:
    with urllib.request.urlopen(RSS_URL) as resp:
        tree = ET.parse(resp)
    root = tree.getroot()
    return root.findall("atom:entry", NS)

def post_to_discord(video_id: str, title: str, thumbnail: str):
    yt_url  = f"https://www.youtube.com/watch?v={video_id}"
    payload = json.dumps({
        "content": "🚨 **Nouveau highlight F1 disponible !**",
        "embeds": [{
            "title": f"🏎️  {title}",
            "url":   yt_url,
            "color": 15158332,
            "image": {"url": thumbnail},
            "footer": {"text": "Formula 1 · YouTube"},
        }]
    }).encode()

    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        print(f"✅ Posté ({resp.status}) : {title}")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    seen    = load_seen()
    entries = fetch_rss()

    for entry in reversed(entries):
        video_id  = entry.findtext("yt:videoId", namespaces=NS)
        title     = entry.findtext("atom:title", namespaces=NS)
        thumbnail = entry.find(".//media:thumbnail", NS)
        thumb_url = thumbnail.attrib.get("url", "") if thumbnail is not None else ""

        if not video_id or video_id in seen:
            continue

        seen.add(video_id)

        if is_highlight(title):
            post_to_discord(video_id, title, thumb_url)
        else:
            print(f"⏭️  Ignoré : {title}")

    save_seen(seen)

if __name__ == "__main__":
    main()
