# Frame-four two-ray GI blend

Keep 5f1ec58. The strongest fitting candidate increased the fourth-frame weight from 21.875% to 23.4375%. It increased frame-four recovery error on the fresh Archive cut. Both camera poses, trajectories, and score definitions were frozen before the sweep. The fresh shot reverses the plank and views the lit floor from a different angle.

In Colab the nine weights ranged from 18.75% to 25% in steps of 1/128. We fixed the frame-two brightness guard, then minimized the mean of GI MAE and p95 blotch contrast, each divided by its control on the fitting tiles. The selected weight improved held-out tile GI MAE by 0.067% and worsened blotch contrast by 0.536%. [Sweep](colab.csv)

| Apple M1 production metric | 21.875% shipping | 23.4375% candidate | Change |
|---|---:|---:|---:|
| Gallery F4 gi_mae | 0.070149 | 0.070266 | +0.17% |
| Gallery F4 p95_blotch_contrast | 0.016295 | 0.016498 | +1.25% |
| fresh F4 recovery (luminance MAE) | 0.006064 | 0.006173 | +1.80% |
| fresh F2 flicker (p95 residual change) | 0.007821 | 0.007821 | +0.00% |
| fresh mean moving-edge AO MAE | 0.028570 | 0.028570 | +0.00% |
| fresh mean synchronized frame time (ms) | 10.041667 | 10.039583 | -0.02% |
| regression F4 recovery (luminance MAE) | 0.005288 | 0.005455 | +3.15% |
| regression F2 flicker (p95 residual change) | 0.007340 | 0.007340 | +0.00% |
| regression mean moving-edge AO MAE | 0.027401 | 0.027401 | +0.00% |
| regression mean synchronized frame time (ms) | 10.187500 | 10.193750 | +0.06% |

Gallery GI output matched shipping on frames 1–3. Gallery AO readbacks matched on all four frames. Both Archive tests used the same 96-render fixed-pose lighting reference for each pair and six alternating-order timing pairs. Positive error changes are worse.

[Fresh comparison](fresh/comparison.mp4) · [Fresh per-frame results](fresh/results.json) · [Original-shot comparison](regression/comparison.mp4) · [Original-shot per-frame results](regression/results.json) · [Gallery results](gallery.json)

Replay either cut from the repository root with Chrome, Python Playwright, Pillow, NumPy, and ffmpeg installed. Add --three /path/to/three for an offline three@0.170.0 installation.

```sh
python3 output/frame4-cut/replay.py --shot fresh
python3 output/frame4-cut/replay.py --shot regression
```
