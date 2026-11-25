# A moving plank immediately after a camera cut

**Ship the Gallery brightness guard.** It reduced the largest flicker event by 6.2% on the second frame after the cut and matched shipping contact error on every frame. The cost was slightly greater deviation from settled lighting, largest on frame 4. This is a recommendation based on the held-out shot and the earlier Gallery data.

| Metric, lower is better | Shipping mean | Challenger mean | Shipping worst (frame) | Challenger worst (frame) |
|---|---:|---:|---:|---:|
| Moving-edge AO visibility MAE | .02740 | .02740 | .02859 (17) | .02859 (17) |
| Flicker, p95 linear luma residual change | .006045 | .006024 | .007821 (2) | .007340 (2) |
| Recovery, linear luma MAE | .001587 | .001613 | .005183 (4) | .005290 (4) |
| Synchronized beauty frame time, ms | 13.26 | 13.39 | 15.70 (2) | 15.75 (9) |

Each variant first met the predeclared recovery threshold on frames 1–3, briefly exceeded it on frame 4, and returned below it on frame 5. Each timing cell summarizes per-frame medians over six order-alternated pairs on Apple M1 / Chrome ANGLE Metal. Each variant was faster in three of the six whole-shot pairs. The table’s worst time is the highest per-frame median. Individual timing samples are in [results.json](results.json).

## Shot and scoring

The historical static plate at 20 cm clearance retained a positive visibility bias. Recent two-ray Gallery measurements favored the brightness guard on frame 2, with 6.35% lower p95 harmful luminance change and 0.57% lower GI MAE, alongside 0.23% higher blotch contrast. Those results selected the failure case and challenger before this shot. [Contact measurements](../../benchmark/contact-results.md) · [Gallery measurements](../m1-gallery-brightness/results_biasGuard.json)

A 2.0 × 0.6 × 0.04 m Archive plank crosses a sunlit floor at 1.44 m/s. Eight establishing frames precede a hard camera cut and history reset. Motion starts on the cut and continues through 24 scored frames at 24 Hz. Both columns in the [comparison clip](comparison.mp4) play the same poses at half speed. The [worst contact still](worst-frame.png) preserves frame 17 and the [edge diagnostic](worst-edge.png) shows its scored receiver samples against the analytic reference.

AO uses 1,024 independent cosine-weighted rays per sample and tests actual box intersections. Mean signed visibility error was +.00070 for both shaders. Flicker and recovery use common 96-frame fixed-pose shipping renders as the settled appearance reference. Flicker subtracts the expected luminance change as the plank moves and scores floor pixels visible in both frames. This isolates temporal instability on the receiver. The explicit history reset exercises startup after a hard cut. [Frozen specification](../../benchmark/heldout-cut/shot.json) · [Challenger patch](../../benchmark/heldout-cut/challenger.patch)

## Replay

From the repository root on the M1, run the following with Chrome, ffmpeg, and Python packages numpy, Pillow and playwright installed.

```sh
python3 benchmark/heldout-cut/replay.py
```

For offline loading, pass `--three /path/to/three` pointing to three@0.170.0. The script also detects a local node_modules/three installation. It verifies the frozen specification and patch, extracts shipping commit 809e8e6 into a temporary directory, runs both production variants and regenerates the clip, diagnostics and raw results.
