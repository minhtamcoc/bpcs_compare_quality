# bpcs_compare_quality

Labtainer package for bpcs_compare_quality.

## Install

```bash
imodule https://github.com/minhtamcoc/bpcs_compare_quality/raw/main/bpcs_compare_quality.tar.gz
labtainer bpcs_compare_quality
```

## Docker image

```text
tammaycay/bpcs_compare_quality.bpcs_compare_quality.student:latest
```

## Checkwork performance note

This release includes `config/skip_starts.txt` so generated frame folders, extracted media, and stego videos are not packed into the Labtainer result archive. The grading checks still use the small report/JSON/text files required by `results.config`.
