"""楽天市場商品検索APIで、ヒロインごと・グッズの種類ごとに実在する商品を探す → data/goods.json
2026-10-28 本人「フィギュアってどんなフィギュア？これでは手が伸びない」→ 商品名と価格を並べ、商品が無い種類は出さない。
キーは .secrets.json（公開しない）。1秒に1回まで。途中で止まっても、取得済みのヒロインは飛ばして続きから再開できる。
使い方: python3 tools_goods_fetch.py [--all]   （--all で取得済みも取り直す。月次タスクで使う）
商品画像はキャラクターの絵が写るので保存しない（バリューコマースへの申告どおり、キャラ画像は使わない）。"""
import json, re, sys, time, datetime, urllib.request, urllib.parse, urllib.error

SEC = json.load(open(".secrets.json"))
SITE = json.load(open("data/site.json"))
H = json.load(open("data/heroines.json"))
OUT = "data/goods.json"
API = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
NG = "抱き枕 タペストリー R18 18禁 成人向け アダルト 同人"

# (build.py の GOODS と同じ見出し, 検索語, 商品名に必要な語)
# (見出し, 検索語, 商品名に必要な語, 商品名にあってはいけない語)
TYPES = [("アクスタ", "アクリルスタンド", r"アクリルスタンド|アクスタ", r"キーホルダー|全\d+種|ランダム|BOX"),
         ("ねんどろいど", "ねんどろいど", r"ねんどろいど", r"ぷらす|キーチェーン|ぷち|ラバー|どーる|着せ替え|パーツ"),
         ("スケールフィギュア", "スケール フィギュア", r"1/[3-9](?![0-9])|1/1[0-2](?![0-9])", r"ノンスケール|ねんどろいど|figma|プラモ|キット"),
         ("プライズフィギュア", "プライズ フィギュア", r"(プライズ|景品|一番くじ|Luminasta|SPM|ちょこのせ|ぬーどるストッパー|TENITOL|BiCute|Trio-Try-iT|Q ?posket|ESPRESTO|GLITTER|Relax ?time|Coreful|Aqua Float|AMP|EXQ|BUZZmod).*フィギュア|フィギュア.*(プライズ|景品|一番くじ)", r"ノンスケール ABS|ねんどろいど|ラバー|チャーム|ストラップ|キーホルダー"),
         ("缶バッジ・ラバスト", "缶バッジ", r"缶バッジ|缶バッチ|ラバスト|ラバーストラップ", r"全\d+種|BOX|コンプ")]

# どの種類でも除く: 舞台・ミュージカル（俳優のグッズ）、ペンスタンドなど別物
BAD_ALL = r"演劇|舞台|ミュージカル|ステージ|ペンスタンド|スマホスタンド"

def compact(s):
    return re.sub(r"[\s・･.\-ー＝=　「」『』（）()]", "", s or "")

def name_keys(h):
    """商品名に入っていればそのキャラとみなす語（フルネーム、または姓・名のどちらか2文字以上）"""
    ks = {compact(h["name"])}
    first = re.split(r"[・･\s=＝]", h["name"])[0]
    if len(first) >= 2: ks.add(first)  # 名（先頭）だけ。姓は家族キャラと重なる（例: アッカーマン）
    return ks

def work_keys(h):
    ks = set()
    for w in (h["work_short"], h["work"]):
        for t in re.split(r"[\s・:：/／!！?？、。「」『』（）()\-–—~〜]", w or ""):
            ks.add(compact(t))
        ks.add(compact(w))
    return {k for k in ks if len(k) >= (4 if k.isascii() else 2)}

def call(keyword):
    p = {"applicationId": SEC["rakuten_app_id"], "accessKey": SEC["rakuten_access_key"], "affiliateId": SITE["rakuten_affiliate_id"],
         "keyword": keyword[:60], "hits": 30, "formatVersion": 2, "availability": 1, "NGKeyword": NG,
         "elements": "itemName,itemPrice,affiliateUrl,itemUrl,shopName,reviewCount,reviewAverage,itemCode"}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(p), headers={"Referer": "https://oshi-heroine.github.io/", "Origin": "https://oshi-heroine.github.io"})
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(req, timeout=30)).get("Items", [])
        except urllib.error.HTTPError as e:
            if e.code == 404: return []
            if e.code in (429, 500, 503): time.sleep(5 * (i + 1)); continue
            raise
        except Exception:
            time.sleep(5 * (i + 1))
    return []

def tidy(n):
    n = re.sub(r"【|】|\[|\]|★|☆|◆|◇|■|□|※|＼|／(?=\s)", " ", n)
    n = re.sub(r"送料無料|ポイント\d+倍|P\d+倍|\d+%OFF|クーポン[^ ]*|あす楽|即納|在庫限り|在庫あり|新品|中古|ネコポス[^ ]*|メール便[^ ]*|宅配便[^ ]*", " ", n)
    n = re.sub(r"^\s*FIG\s+", "", re.sub(r"\s+", " ", n)).strip()
    return n[:70] + ("…" if len(n) > 70 else "")

def pick(h, items, need, bad):
    nk, wk = name_keys(h), work_keys(h)
    out, seen = [], set()
    for it in items:
        nm = it["itemName"]; c = compact(nm)
        if not any(k in c for k in nk): continue
        if not any(k in c for k in wk): continue
        if not re.search(need, nm) or re.search(bad, nm) or re.search(BAD_ALL, nm): continue
        used = "中古" in nm
        if not any(k in compact(tidy(nm)) for k in nk): continue  # 表示する商品名にキャラ名が残ること
        key = compact(tidy(nm))[:30]
        if key in seen: continue
        seen.add(key)
        out.append({"name": tidy(nm), "price": it["itemPrice"], "url": it.get("affiliateUrl") or it["itemUrl"], "shop": it["shopName"],
                    "reviews": it.get("reviewCount", 0), "used": used})
    out.sort(key=lambda x: (x["used"], -x["reviews"], x["price"]))
    return out[:2]

def main():
    redo = "--all" in sys.argv
    try: G = json.load(open(OUT))
    except FileNotFoundError: G = {}
    todo = [h for h in H if redo or str(h["id"]) not in G]
    print(len(todo), "heroines to fetch", flush=True)
    for n, h in enumerate(todo, 1):
        res = {}
        for lb, kw, need, bad in TYPES:
            items = call("%s %s" % (h["name"], kw))
            time.sleep(1.1)
            got = pick(h, items, need, bad)
            if got: res[lb] = got
        G[str(h["id"])] = {"date": datetime.date.today().isoformat(), "items": res}
        if n % 10 == 0 or n == len(todo):
            json.dump(G, open(OUT, "w"), ensure_ascii=False, indent=0)
            print(n, h["name"], {k: len(v) for k, v in res.items()}, flush=True)
    json.dump(G, open(OUT, "w"), ensure_ascii=False, indent=0)

if __name__ == "__main__":
    main()
