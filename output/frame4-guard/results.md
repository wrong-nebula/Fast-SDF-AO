# Frame-four GI recovery on Apple M1

Shipping baseline 5f1ec58, fixed fourth-frame weight 21.875%. Both experiments preserve the shipping second-frame guard. Each blind camera and trajectory was frozen before selecting or rendering its challenger. The two blind views differ, so each row compares against shipping in that same view.

| Trial / scene | F4 lighting recovery MAE, shipping → trial | F2 p95 flicker, shipping → trial | Mean edge AO MAE, shipping → trial | Mean frame time (ms), shipping → trial |
|---|---:|---:|---:|---:|
| lower / blind | 0.004596 → 0.004546 | 0.007525 → 0.007525 | 0.027459 → 0.027459 | 10.70 → 10.62 |
| lower / original | 0.005288 → 0.005206 | 0.007340 → 0.007340 | 0.027401 → 0.027401 | 13.40 → 11.45 |
| lower / reverse | 0.006064 → 0.005999 | 0.007821 → 0.007821 | 0.028570 → 0.028570 | 10.23 → 10.30 |
| guard / blind | 0.005688 → 0.005706 | 0.007340 → 0.007340 | 0.028414 → 0.028414 | 9.79 → 10.03 |
| guard / original | 0.005288 → 0.005312 | 0.007340 → 0.007340 | 0.027401 → 0.027401 | 9.74 → 9.85 |

| Gallery F4 metric | Shipping | Fixed 21.09375% | Conditional reduction |
|---|---:|---:|---:|
| gi_mae | 0.070149 | 0.070095 | 0.071773 |
| p95_blotch_contrast | 0.016295 | 0.016552 | 0.016404 |
| p95_temporal_luma_change | 0.023701 | 0.023132 | 0.022854 |

The fixed reduction improved recovery on three cuts but gave back most of the earlier Gallery blotch improvement. In the conditional trial, frame-four weight ramped down from 21.875% to 18.75% only for bright incoming samples. It ranked first of twelve by the worse of relative RGB MAE and p95 blotch contrast on fitting tiles in Colab. Both improved on the check tiles. In the production Gallery readback, mean signed linear-luminance error shifted from −0.06558 to −0.06771 and brightest-decile luminance MAE rose from 0.21051 to 0.21398. Keep the shipping blend.

The fixed finalist was selected using the previous Colab check tiles, which are now selection data. The adaptive finalist was selected on fitting tiles. Each M1 Gallery result used 57,600 pixels against the independent 512-ray reference. All four Gallery AO readbacks matched shipping exactly, as did GI readbacks on frames 1–3. Timing summarizes medians by frame from six alternating-order pairs.

[Fixed blind clip](../frame4-lower/blind/comparison.mp4) · [Conditional blind clip](blind/comparison.mp4) · [Conditional selection](colab.json) · [Previous Colab sweep](../frame4-cut/colab.csv)

Replay from the repository root with Chrome, NumPy, Pillow, Playwright, and ffmpeg. Use --three /path/to/three for an offline three@0.170.0 installation.

```sh
python3 output/frame4-lower/replay.py --shot blind
python3 output/frame4-guard/replay.py --shot blind
```
