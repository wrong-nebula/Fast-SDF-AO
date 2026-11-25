# Fourth-frame two-ray directions on M1

**Keep the shipping ray pattern.** The finalist increased both production Gallery blotch contrast and lighting error on the original cut.

The baseline is 5f1ec58. The production blend stays at 21.875%. Only the fourth update with two active GI rays uses the new pattern. A 45-pattern Colab sweep selected elevation center 0.40625, width 0.625 and a −5.625° rotation of the pair, using only fitting tiles for selection. On check tiles RGB MAE rose 0.47% and blotch contrast fell 4.74%.

| M1 metric | Shipping | Candidate | Change |
|---|---:|---:|---:|
| Gallery F4 GI MAE | 0.070149 | 0.070218 | +0.10% |
| Gallery F4 p95 blotch contrast | 0.016295 | 0.017038 | +4.56% |
| Gallery F4 p95 temporal luma change | 0.023701 | 0.023139 | -2.37% |
| blind F4 recovery MAE | 0.005339 | 0.005429 | +1.68% |
| blind mean recovery MAE | 0.004295 | 0.004301 | +0.16% |
| blind worst recovery MAE | 0.007763 | 0.007764 | +0.01% |
| blind F2 p95 flicker | 0.007821 | 0.007821 | +0.00% |
| blind mean contact MAE | 0.027398 | 0.027398 | +0.00% |
| blind mean synchronized frame time | 10.139583 ms | 10.072917 ms | -0.66% |
| original F4 recovery MAE | 0.005288 | 0.005383 | +1.79% |
| original mean recovery MAE | 0.001612 | 0.001620 | +0.49% |
| original worst recovery MAE | 0.005288 | 0.005383 | +1.79% |
| original F2 p95 flicker | 0.007340 | 0.007340 | +0.00% |
| original mean contact MAE | 0.027401 | 0.027401 | +0.00% |
| original mean synchronized frame time | 10.208333 ms | 10.050000 ms | -1.55% |
| second blind F4 recovery MAE | 0.004905 | 0.004907 | +0.03% |
| second blind F2 p95 flicker | 0.007340 | 0.007340 | +0.00% |
| second blind mean contact MAE | 0.028523 | 0.028523 | +0.00% |
| second blind mean frame time (ms) | 9.991667 | 9.937500 | -0.54% |
| Gallery startup ms/frame, median block | 9.862500 | 9.937500 | +0.76% |

A second Colab sweep corrected the noise seed to use 320×180 GI texel centers for all four frames. The same pattern won again. On check tiles the predicted blotch reduction shrank to 1.17% and GI MAE rose 0.26%. The production renderer measured a 4.56% blotch increase. Geometry tracing in the proxy and tracing, filtering and history in production still differ.

Across 57,600 Gallery samples, 7, 6 and 10 pixels differed in frames 1, 2 and 3 respectively. The mean RGB GI error changed by less than 0.0000001 in each. All four AO readback hashes matched.

Gallery startup timings cover 24 paired blocks, with a median paired delta of -0.075 ms/frame. The candidate was slower in 10 blocks. Each block uses eleven four-frame starts. Cut timings use a separate six-pair run per shot. Each cut has a common fixed-pose reference per frame and independent ray-traced contact scores.

[Second fresh comparison](../frame4-grid-rays/blind/comparison.mp4) · [Second per-frame results](../frame4-grid-rays/blind/results.json) · [Fresh comparison](blind/comparison.mp4) · [Fresh per-frame results](blind/results.json) · [Original comparison](original/comparison.mp4) · [Original per-frame results](original/results.json) · [Gallery](gallery.json) · [Colab](colab.json)

Replay from the repo root with Chrome, Python Playwright, NumPy, Pillow and ffmpeg. Pass --three /path/to/three for offline three@0.170.0.

```sh
python3 output/frame4-directions/replay.py --shot blind
python3 output/frame4-directions/replay.py --shot original
```
