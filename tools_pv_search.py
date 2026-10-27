#!/usr/bin/env python3
"""pv.json（推しアニメから複写）で PV が見つからなかった作品だけ、YouTube を検索して候補を並べる。
採用は人（Claude）が公式チャンネルかを見て data/pv_extra.json に書く。キーは ~/anime-oshi-ranking/.secrets.json。"""
import json, os, subprocess, urllib.parse, sys
HERE = os.path.dirname(os.path.abspath(__file__))
key = json.load(open(os.path.expanduser("~/anime-oshi-ranking/.secrets.json")))["youtube_api_key"]
H = json.load(open(os.path.join(HERE, "data/heroines.json")))
PV = json.load(open(os.path.join(HERE, "data/pv.json")))
EX = json.load(open(os.path.join(HERE, "data/pv_extra.json"))) if os.path.exists(os.path.join(HERE, "data/pv_extra.json")) else {}
seen = {}
for h in H: seen.setdefault(h["key"], h["work"])
out = {}
for k, w in seen.items():
    if (PV.get(k) or {}).get("video_id") or k in EX: continue
    q = "%s アニメ PV" % w
    url = "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(dict(part="snippet", type="video", maxResults=10, q=q, regionCode="JP", videoEmbeddable="true", key=key))
    d = json.loads(subprocess.run(["curl", "-s", "-m", "30", url], capture_output=True, text=True).stdout or "{}")
    if "error" in d: print("API error", d["error"].get("message")); break
    out[k] = {"work": w, "items": [(it["id"]["videoId"], it["snippet"]["title"], it["snippet"]["channelTitle"], it["snippet"]["publishedAt"][:10]) for it in d.get("items", [])]}
    print("##", k, w)
    for i, it in enumerate(out[k]["items"]): print("  %d %s | %s | %s" % (i, it[2], it[1][:70], it[3]))
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "/dev/null", "w"), ensure_ascii=False, indent=1)
