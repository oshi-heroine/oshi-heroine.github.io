"""candidates.json と data/points.json を合わせて data/heroines.json を作る。
推しポイントが未記入のヒロインは掲載せず、一覧を表示する（月1作業で書き足す）"""
import json, os
c = json.load(open(os.path.expanduser("~/knowledge-os/raw/anime/heroines/candidates.json")))
p = json.load(open("data/points.json"))
miss = [x for x in c if not p.get(str(x["id"]))]
out = [{k: x[k] for k in ("id", "name", "work", "work_short", "rank", "key", "fav", "role")} | {"point": p[str(x["id"])]} for x in c if p.get(str(x["id"]))]
json.dump(out, open("data/heroines.json", "w"), ensure_ascii=False, indent=1)
s = json.load(open("data/site.json"))
s["description"] = "いま配信でよく観られているアニメ%d作品から、美少女ヒロイン%d人を人気の数字と公式PVつきで紹介。メインもサブも、あなたの推しがきっと見つかります。" % (len({x["work"] for x in out}), len(out))
json.dump(s, open("data/site.json", "w"), ensure_ascii=False, indent=1)
print("掲載", len(out), "人 / 推しポイント未記入", len(miss), "人")
for x in miss: print("MISSING", x["id"], x["name"], "|", x["work"], "|", x["role"], x["fav"], "|", x["desc"][:200].replace("\n", " "))
