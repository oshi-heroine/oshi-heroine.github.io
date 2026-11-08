"""data/x_posts.json の公式X投稿が今も見られるか確かめ、消えた投稿を外す（毎月の更新で実行）"""
import json, time, urllib.request
P = "data/x_posts.json"
X = json.load(open(P)); gone = []
for k, v in list(X.items()):
    i = v["url"].rsplit("/", 1)[1]
    try:
        r = urllib.request.Request("https://cdn.syndication.twimg.com/tweet-result?id=%s&lang=ja&token=4c2mmul6mnh" % i, headers={"User-Agent": "Mozilla/5.0"})
        d = json.load(urllib.request.urlopen(r, timeout=20))
        if not d.get("mediaDetails"): raise ValueError("no media")
    except Exception as e:
        if "404" in str(e) or "no media" in str(e): gone.append(k); del X[k]
    time.sleep(.4)
json.dump(X, open(P, "w"), ensure_ascii=False, indent=0)
print("checked", len(X) + len(gone), "removed", gone)
