#!/usr/bin/env python3
"""アニメヒロイン図鑑サイトを docs/ に書き出す。
ヘッダー assets/header.jpg はキャラなしの文字だけ画像（tools_header.py）。バリューコマースの「商用許諾のない画像を扱わない」申告のため、キャラ絵は使わない（2026-10-25 本人判断）。
入力: data/site.json, data/heroines.json, data/pv.json, data/watch.json
キャラ絵は一切使わない（YouTube 公式サムネイルの直リンクのみ）。"""
import json, os, html, urllib.parse, hashlib, datetime, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
D = lambda n: json.load(open(os.path.join(ROOT, "data", n), encoding="utf-8"))
S = D("site.json")
H = D("heroines.json")
PV = D("pv.json")
if os.path.exists(os.path.join(ROOT, "data", "pv_extra.json")):  # pv.json で見つからなかった作品の公式動画（手で採用）
    PV.update({k: v for k, v in D("pv_extra.json").items() if not k.startswith("_")})
W = D("watch.json")
OUT = os.path.join(ROOT, "docs")
BASE = S["site_url"].rstrip("/") + "/"
TODAY = datetime.date.today().isoformat()
esc = lambda s: html.escape(str(s or ""), quote=True)

# ---------- データ整理 ----------
WORKS = {}
for h in H:
    w = WORKS.setdefault(h["work"], {"work": h["work"], "rank": h["rank"], "key": h.get("key"), "list": []})
    w["list"].append(h)
WORKS = sorted(WORKS.values(), key=lambda w: w["rank"])
for w in WORKS:
    w["list"].sort(key=lambda h: (h["role"] != "main", -h["fav"]))
N_WORKS, N_HER = len(WORKS), len(H)
N_SUB = sum(1 for h in H if h["role"] == "sub")

PALETTE = ["#ff6fa5", "#8b7bff", "#3fb8ff", "#ff9f43", "#2ed3a0", "#f368e0", "#ffd166", "#5ad1e6"]
def color(h):
    return PALETTE[int(hashlib.md5(h["name"].encode()).hexdigest(), 16) % len(PALETTE)]

# ---------- アフィリエイト ----------
def amazon(q):
    return "https://www.amazon.co.jp/s?k=" + urllib.parse.quote_plus(q) + ("&tag=" + S["amazon_tag"] if S.get("amazon_tag") else "")
def rakuten(q):
    s = "https://search.rakuten.co.jp/search/mall/" + urllib.parse.quote(q) + "/"
    return "https://hb.afl.rakuten.co.jp/hgc/" + S["rakuten_affiliate_id"] + "/?pc=" + urllib.parse.quote(s, safe="") if S.get("rakuten_affiliate_id") else s
def yahoo(q):
    """Yahoo!ショッピングはバリューコマース経由（もしもは使わない、2026-10-25 本人）"""
    v = S.get("vc_yahoo")
    if not v or not v.get("active"): return None
    dest = "https://shopping.yahoo.co.jp/search?p=" + urllib.parse.quote(q)
    return "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=%s&pid=%s&vc_url=%s" % (
        v["sid"], v["pid"], urllib.parse.quote(dest, safe=""))
def btn(cls, url, label, style=""):
    return '<a class="btn %s" %shref="%s" target="_blank" rel="nofollow sponsored noopener">%s</a>' % (
        cls, ('style="%s" ' % style) if style else "", esc(url), label)

def watch_line(w):
    """作品がどこで観られるか（JustWatch 調べ）。文章で自然に案内する"""
    v = W.get(w.get("key") or "") or {}
    svc = list(dict.fromkeys(v.get("flatrate", []) + v.get("free", [])))
    svc = [s for s in svc if "チャンネル" not in s][:5]
    if not svc: return ""
    btns = [btn("vod", s["url"], esc(s["name"]), "--bc:%s" % s["color"]) for s in S.get("streaming", []) if s.get("url")]
    if "Prime Video" in svc:
        btns.append(btn("amz", amazon(w["work"] + " Prime Video"), "Prime Videoで探す"))
    return ('<div class="watch"><p>📺 本編は <b>%s</b> で観られます（%s 時点）</p>%s</div>'
            % ("・".join(esc(s) for s in svc), esc(v.get("date", "")), '<div class="btns">%s</div>' % "".join(btns) if btns else ""))

def goods_box(h):
    q = "%s %s" % (h["name"], h["work_short"])
    items = [("アクスタ", " アクリルスタンド"), ("フィギュア", " フィギュア"), ("缶バッジ", " 缶バッジ")]
    rows = []
    for lb, suf in items:
        bs = [btn("amz", amazon(q + suf), "Amazon"), btn("rkt", rakuten(q + suf), "楽天")]
        if yahoo(q + suf): bs.append(btn("yho", yahoo(q + suf), "Yahoo!"))
        rows.append('<div class="g-row"><span>%s</span>%s</div>' % (lb, "".join(bs)))
    return ('<section class="goods"><h2>推しを、毎日そばに</h2><p class="muted">%sのグッズは、手元にあると毎日ちょっと元気が出ます。気になる形はどれですか？</p>%s</section>'
            % (esc(h["name"]), "".join(rows)))

# ---------- 部品 ----------
def pv_block(w, small=False):
    v = PV.get(w.get("key") or "") or {}
    if not v.get("video_id"): return ""
    vid = esc(v["video_id"])
    return ('<div class="pv%s" data-id="%s"><button class="pv-btn" type="button" aria-label="%s の公式PVを再生">'
            '<img class="pv-img" src="https://i.ytimg.com/vi/%s/hqdefault.jpg" alt="" loading="lazy" referrerpolicy="no-referrer">'
            '<span class="pv-play">▶</span><span class="pv-t">公式PV</span></button></div>'
            '<p class="src">出典: YouTube「%s」（%s 公開）</p>'
            % (" sm" if small else "", vid, esc(w["work"]), vid, esc(v.get("channel", "")), esc(v.get("published", ""))))

def tile(h, big=False):
    return '<div class="tile%s" style="--c:%s"><span>%s</span></div>' % (" big" if big else "", color(h), esc(h["name"][:1]))

def card(h, rel="", work=False):
    role = '<i class="role main">メイン</i>' if h["role"] == "main" else '<i class="role sub">勝ち負け関係なし枠</i>'
    return ('<a class="hcard" data-role="%s" data-q="%s" href="%sheroine/%s.html">%s<div class="hc-b"><b>%s</b>%s%s'
            '<p>%s</p><span class="fav">♡ %s人が推し登録</span></div></a>'
            % (h["role"], esc(h["name"] + " " + h["work"]), rel, h["id"], tile(h), esc(h["name"]), role,
               '<span class="hc-w">%s</span>' % esc(h["work_short"]) if work else "", esc(h["point"]), "{:,}".format(h["fav"])))

GA = S.get("ga_measurement_id")
GA_TAG = ('<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script><script>window.dataLayer=window.dataLayer||[];'
          'function gtag(){dataLayer.push(arguments)}gtag("js",new Date());gtag("config","%s");</script>' % (GA, GA)) if GA else ""

def page(path, title, desc, body, rel=""):
    full = title if title == S["seo_title"] else "%s｜%s" % (title, S["name"])
    canon = BASE + path.replace("index.html", "")
    og = BASE + "img/header.jpg" if os.path.exists(os.path.join(ROOT, "assets", "header.jpg")) else ""
    nav = "".join('<a href="%s%s">%s</a>' % (rel, u, l) for u, l in
                  [("index.html", "作品ランキング"), ("chara.html", "キャラ人気ランキング"), ("sub.html", "勝ち負け関係なし枠"), ("about.html", "運営者の気持ち")])
    html_ = """<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{full}</title><meta name="description" content="{desc}"><link rel="canonical" href="{canon}">
<meta property="og:title" content="{full}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{canon}">
<meta property="og:type" content="website">{ogimg}<meta name="twitter:card" content="summary_large_image">{gsv}
<link rel="stylesheet" href="{rel}style.css">{ga}</head><body>
<p class="pr">当サイトはアフィリエイト広告（{asps}）を利用しています</p>
<header class="top"><a class="logo" href="{rel}index.html"><b>{name}</b><small>{catch}</small></a><nav>{nav}</nav></header>
<main>{body}</main>
<footer><p>{name}　{catch}</p><p><a href="{rel}about.html">運営者の気持ち</a>・<a href="{rel}privacy.html">プライバシーポリシー・広告について</a></p>
<p class="muted">キャラクターの人気数は AniList のお気に入り登録数、作品の並びは国内・世界の配信サービス総合ランキング（JustWatch ほか）をもとにしています。作品・キャラクターの権利は各権利者に帰属します。キャラクターの画像は掲載していません。</p></footer>
<script src="{rel}app.js"></script></body></html>""".format(
        full=esc(full), desc=esc(desc), canon=canon, ogimg='<meta property="og:image" content="%s">' % og if og else "",
        gsv='<meta name="google-site-verification" content="%s">' % esc(S["google_site_verification"]) if S.get("google_site_verification") else "",
        rel=rel, ga=GA_TAG, asps=ASPS_TXT, name=esc(S["name"]), catch=esc(S["catch"]), nav=nav, body=body)
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(html_)
    SITEMAP.append(canon)

SITEMAP = []
ASPS_TXT = "Amazonアソシエイト・楽天アフィリエイト" + ("・バリューコマース" if (S.get("vc_yahoo") or {}).get("active") else "")
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)

# ---------- トップ ----------
work_secs = []
for w in WORKS:
    work_secs.append(
        '<section class="work" id="w%d"><div class="w-head"><span class="rank">配信総合 %d位</span><h2>%s</h2></div>'
        '<div class="w-body"><div class="w-pv">%s</div><div class="w-list">%s</div></div>%s</section>'
        % (w["rank"], w["rank"], esc(w["work"]), pv_block(w, True) or '<p class="pv-none">公式PVは準備中です</p>', "".join(card(h) for h in w["list"]), watch_line(w)))
picks = [{"id": h["id"], "n": h["name"], "w": h["work"], "p": h["point"], "c": color(h)} for h in H]
hero = """<section class="hero"><h1>{name}</h1><p class="catch">{catch}</p>
<p class="lead">{lead}</p>
<ul class="nums"><li><b>{nw}</b>作品</li><li><b>{nh}</b>人のヒロイン</li><li><b>{ns}</b>人は勝ち負け関係なし枠</li></ul>
<div class="cta"><button id="gacha" class="b1" type="button">今日の推し候補を引く</button><a class="b2" href="chara.html">キャラ人気順で見る</a></div>
<div id="gacha-out" class="gacha-out" hidden></div></section>""".format(
    name=esc(S["name"]).replace("。", "。<br>", 1), catch=esc(S["catch"]), lead=S["lead_html"], nw=N_WORKS, nh=N_HER, ns=N_SUB)
tools = """<div class="tools" id="list"><div class="chips"><button class="on" data-f="all">すべて（{nh}）</button><button data-f="main">メイン</button><button data-f="sub">勝ち負け関係なし枠</button></div>
<input id="q" type="search" placeholder="名前・作品名でさがす" aria-label="名前・作品名でさがす"></div>""".format(nh=N_HER)
body = hero + tools + "".join(work_secs) + '<script>window.PICKS=%s;</script>' % json.dumps(picks, ensure_ascii=False)
page("index.html", S["seo_title"], S["description"], body)

# ---------- キャラ人気ランキング（2026-10-28 本人「キャラでランキングのページを追加して」） ----------
ranked = sorted(H, key=lambda h: (-h["fav"], h["rank"]))
rows, prev, n = [], None, 0
for i, h in enumerate(ranked, 1):
    if h["fav"] != prev: n, prev = i, h["fav"]  # 同じ数なら同じ順位
    rows.append('<li class="crow%s"><span class="cr-n">%d<small>位</small></span>%s</li>' % (" top" if n <= 3 else "", n, card(h, work=True)))
body = ('<section class="intro"><h1>キャラ人気ランキング</h1><p class="lead">作品の順位ではなく、ヒロイン一人ひとりの人気で並べました。'
        '数字は、世界中のアニメファンが AniList で「お気に入り」に登録した人数です（%s 時点）。%d人のうち、あなたの推しは何位にいますか？</p></section>'
        '<div class="tools" id="list"><div class="chips"><button class="on" data-f="all">すべて（%d）</button><button data-f="main">メイン</button><button data-f="sub">勝ち負け関係なし枠</button></div>'
        '<input id="q" type="search" placeholder="名前・作品名でさがす" aria-label="名前・作品名でさがす"></div>'
        '<ol class="rank-list">%s</ol>' % (TODAY, N_HER, N_HER, "".join(rows)))
page("chara.html", "アニメヒロイン キャラ人気ランキング%d人" % N_HER,
     "配信ランキング上位アニメのヒロイン%d人を、AniList のお気に入り登録数で順位づけ。1位は%s（%s）。あなたの推しは何位？" % (N_HER, ranked[0]["name"], ranked[0]["work_short"]), body)

# ---------- 勝ち負け関係なし枠 ----------
subs = sorted([h for h in H if h["role"] == "sub"], key=lambda h: -h["fav"])
body = ('<section class="intro"><h1>勝ち負けなんてどうでもいい枠</h1><p class="lead">物語の「勝ち負け」で選ばれなかったとしても、推したくなる子はたくさんいます。'
        'ここには、主役ではないのに多くの人に推されているヒロインを%d人集めました。あなたの心に残るのは、どの子でしょうか？</p></section>'
        '<div class="grid">%s</div>' % (len(subs), "".join(card(h) for h in subs)))
page("sub.html", "勝ち負けなんてどうでもいい枠（サブヒロイン・負けヒロイン）", "主役じゃなくても推したい。配信ランキング上位アニメのサブヒロイン%d人を、人気の数字つきで紹介します。" % len(subs), body)

# ---------- ヒロイン個別 ----------
for w in WORKS:
    for h in w["list"]:
        others = [o for o in w["list"] if o["id"] != h["id"]]
        role = "メインヒロイン" if h["role"] == "main" else "勝ち負けなんてどうでもいい枠（サブヒロイン）"
        body = """<nav class="crumb"><a href="../index.html">トップ</a> › <a href="../index.html#w{rank}">{work}</a> › {name}</nav>
<section class="hp"><div class="hp-top">{tile}<div><p class="muted">{work}</p><h1>{name}</h1><p><i class="role {rc}">{role}</i></p>
<p class="fav big">♡ <b>{fav}</b>人が推し登録<small>（AniList お気に入り数）</small></p></div></div>
<h2>ここが推せる</h2><p class="point">{point}</p>{more}
<h2>まずは公式PVで会いに行く</h2>{pv}{watch}{goods}
{others}<div class="next"><p>ほかの子にも会ってみませんか？</p><a class="b1" href="../index.html#list">ランキングに戻る</a><a class="b2" href="../sub.html">勝ち負け関係なし枠</a></div></section>""".format(
            rank=w["rank"], work=esc(w["work"]), name=esc(h["name"]), tile=tile(h, True), rc=h["role"], role=role,
            fav="{:,}".format(h["fav"]), point=esc(h["point"]),
            more="<p>%s</p>" % esc(h["more"]) if h.get("more") else "",
            pv=pv_block(w) or '<p class="muted">公式PVは準備中です。</p>', watch=watch_line(w), goods=goods_box(h),
            others=('<h2>同じ作品のヒロイン</h2><div class="grid">%s</div>' % "".join(card(o, "../") for o in others)) if others else "")
        page("heroine/%s.html" % h["id"], "%s（%s）の推しポイント" % (h["name"], h["work_short"]),
             "%s（%s）の推しポイントを紹介。%s ♡%s人が推し登録。" % (h["name"], h["work"], h["point"][:60], "{:,}".format(h["fav"])), body, "../")

# ---------- 運営者・プライバシー ----------
page("about.html", "運営者の気持ち", "知らない美少女を、みんなに知ってもらうためのサイトです。", '<section class="intro"><h1>運営者の気持ち</h1>%s</section>' % S["about_html"])
page("privacy.html", "プライバシーポリシー・広告について", "当サイトのプライバシーポリシーと広告の表示について。", """<section class="intro"><h1>プライバシーポリシー・広告について</h1>
<h2>広告について</h2><p>当サイトは """ + ASPS_TXT + """ に参加しています。リンクからの購入で、運営者に紹介料が入ることがあります。紹介する作品やキャラクターの選び方は、広告の有無とは関係ありません。</p>
<h2>アクセス解析</h2><p>当サイトは Google アナリティクスを利用しています。データは匿名で集められ、個人を特定するものではありません。ブラウザの設定で Cookie を無効にできます。</p>
<h2>著作権について</h2><p>作品・キャラクターの権利は各権利者に帰属します。キャラクターの画像は掲載していません。それ以外にキャラクターの画像は掲載せず、作品の映像は公式 YouTube の動画を埋め込みでのみ紹介しています。問題がある場合はお手数ですがご連絡ください。</p>
<h2>データの出典</h2><p>人気数: AniList（お気に入り登録数）／作品の並び: JustWatch・Netflix 公式 Top 10 ほかの配信サービス総合ランキング／配信先: JustWatch。</p></section>""")

# ---------- 静的ファイル ----------
for f in ("style.css", "app.js"):
    shutil.copy(os.path.join(ROOT, "assets", f), os.path.join(OUT, f))
if os.path.exists(os.path.join(ROOT, "assets", "header.jpg")):
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "assets", "header.jpg"), os.path.join(OUT, "img", "header.jpg"))
open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>'
    % "".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (u, TODAY) for u in SITEMAP))
open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % BASE)
open(os.path.join(OUT, ".nojekyll"), "w").write("")
print("built", len(SITEMAP), "pages:", N_WORKS, "works /", N_HER, "heroines")
