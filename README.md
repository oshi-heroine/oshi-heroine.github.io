# 勝ち負けなんてどうでもいい。あんたの推しは必ずいる 〜アニメの美少女ヒロイン図鑑〜

https://oshi-heroine.github.io/ （GitHub oshi-heroine/oshi-heroine.github.io、Pages main:/docs）

## 月1回の更新
1. `cp ~/anime-oshi-ranking/pv.json ~/anime-oshi-ranking/watch.json data/`
2. `python3 ~/knowledge-os/raw/anime/heroines/fetch_heroines.py 120`（配信総合ランキング上位 → AniList 女性キャラ）
3. `python3 ~/knowledge-os/raw/anime/heroines/select_heroines.py`（選ぶルールは docstring）
4. `python3 tools_merge.py` → MISSING の子の推しポイントを data/points.json に書く（ネタバレなし・40〜70字）→ もう一度 tools_merge.py
5. `python3 build.py`

キャラクターの画像は使わない（公式PVの YouTube サムネイル直リンクのみ）。ヘッダーは tools_header.py（キャラなし）。
