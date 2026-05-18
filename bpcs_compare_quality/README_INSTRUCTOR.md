# bpcs_compare_quality

Native Labtainer lab for comparing normal BPCS and Adaptive BPCS in video
steganography.

The lab uses original Labtainer checkwork/stoplab behavior. Do not install
custom wrappers.

Student-facing files:

```text
video.mp4
bpcs_basic_embed.py
bpcs_basic_extract.py
bpcs_adaptive_embed.py
bpcs_adaptive_extract.py
compare_metrics.py
bpcs_utils.py
```

Expected grading:

```text
cw1: basic_report.txt contains fixed_threshold.
cw2: adaptive_report.txt contains final_threshold.
cw3: basic_recovered_secret.txt contains the expected message.
cw4: adaptive_recovered_secret.txt contains the expected message.
cw5: comparison_report.txt contains PSNR metrics.
```
