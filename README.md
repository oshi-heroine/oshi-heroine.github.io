# 勝ち負けなんてどうでもいい。あんたの推しは必ずいる 〜アニメの美少女ヒロイン図鑑〜

https://oshi-heroine.github.io/ （GitHub oshi-heroine/oshi-heroine.github.io、Pages main:/docs）

## 月1回の更新
1. `cp ~/anime-oshi-ranking/pv.json ~/anime-oshi-ranking/watch.json data/`
2. `python3 ~/knowledge-os/raw/anime/heroines/fetch_heroines.py 120`（配信総合ランキング上位 → AniList 女性キャラ）
3. `python3 ~/knowledge-os/raw/anime/heroines/select_heroines.py`（選ぶルールは docstring）
4. `python3 tools_merge.py` → MISSING の子の推しポイントを data/points.json に書く（ネタバレなし・3行くらい＝100〜150字）→ もう一度 tools_merge.py
5. `python3 build.py`

ヘッダー assets/header.jpg は本人提供の画像（上書きしない）。それ以外にキャラクターの画像は使わない（公式PVの YouTube サムネイル直リンクのみ）。tools_header.py は予備の文字だけヘッダー（header_drawn.jpg）。
