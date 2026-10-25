# 勝ち負けなんてどうでもいい。あんたの推しは必ずいる 〜アニメの美少女ヒロイン図鑑〜

https://oshi-heroine.github.io/ （GitHub oshi-heroine/oshi-heroine.github.io、Pages main:/docs）

## 月1回の更新
1. `cp ~/anime-oshi-ranking/pv.json ~/anime-oshi-ranking/watch.json data/`
2. `python3 ~/knowledge-os/raw/anime/heroines/fetch_heroines.py 120`（配信総合ランキング上位 → AniList 女性キャラ）
3. `python3 ~/knowledge-os/raw/anime/heroines/select_heroines.py`（1作品最大5人。できるだけ3人以上、3人未満の作品も載せる。除外は exclude_extra.json。人気作が3人未満なら refetch_more.py で取り直す）
4. `python3 tools_merge.py` → MISSING の子の推しポイントを data/points.json に書く（ネタバレなし・3行くらい＝100〜150字）→ もう一度 tools_merge.py
5. `python3 build.py`

キャラクターの画像は一切使わない（公式PVの YouTube サムネイル直リンクのみ）。ヘッダーは tools_header.py の文字だけ画像。バリューコマースに「商用許諾のない画像を扱っていません」と申告しているため（2026-10-25）。
