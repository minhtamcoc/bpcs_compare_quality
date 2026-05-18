# So sanh BPCS thuong va Adaptive BPCS

## Muc dich

Bai thuc hanh giup sinh vien so sanh hai phuong phap giau tin trong
video:

```text
BPCS thuong: dung nguong phuc tap co dinh.
Adaptive BPCS: tinh nguong dong dua tren do phuc tap cua data block.
```

Sau bai lab, sinh vien biet cach:

```text
- tach video thanh frame va audio bang ffmpeg
- giau cung mot thong diep bang BPCS thuong va Adaptive BPCS
- tach lai thong diep da giau
- so sanh chat luong frame bang MSE, PSNR va so pixel bi thay doi
```

## File ban dau

```text
video.mp4
bpcs_basic_embed.py
bpcs_basic_extract.py
bpcs_adaptive_embed.py
bpcs_adaptive_extract.py
compare_metrics.py
bpcs_utils.py
```

Thong diep mau duoc giau trong lab:

```text
Compare BPCS and Adaptive BPCS
```

## Task 1: Chuan bi video

Xem thong tin ky thuat cua video:

```bash
ffmpeg -hide_banner -i video.mp4 2> video_info.txt
cat video_info.txt
```

Tach video thanh frame:

```bash
mkdir frames
ffmpeg -i video.mp4 frames/frame_%04d.png
```

Tach audio:

```bash
ffmpeg -hide_banner -i video.mp4 -q:a 0 -map a audio.mp3
```

Can chu y cac thong so:

```text
duration
resolution
fps
video codec
audio stream
```

## Task 2: Giau tin bang BPCS thuong

Mo file:

```bash
nano bpcs_basic_embed.py
```

Chu y cac bien:

```text
FIXED_THRESHOLD
TARGET_FRAME_INDEX
SECRET_DATA
BIT_PLANE
CHANNEL
FPS
```

Chay chuong trinh giau tin:

```bash
python3 bpcs_basic_embed.py
```

Ket qua can co:

```text
basic_frames/
basic_position.json
basic_output.avi
basic_report.txt
```

Trong BPCS thuong, frame se duoc chon block neu do phuc tap alpha cua
cover block lon hon hoac bang `FIXED_THRESHOLD`.

## Task 3: Giau tin bang Adaptive BPCS

Mo file:

```bash
nano bpcs_adaptive_embed.py
```

Chu y cac bien:

```text
BASE_ALPHA
ADAPTIVE_MARGIN
MAX_FINAL_THRESHOLD
TARGET_FRAME_INDEX
SECRET_DATA
BIT_PLANE
CHANNEL
FPS
```

Chay chuong trinh:

```bash
python3 bpcs_adaptive_embed.py
```

Ket qua can co:

```text
adaptive_frames/
adaptive_position.json
adaptive_output.avi
adaptive_report.txt
```

Adaptive BPCS se tinh:

```text
min_alpha_prime
max_alpha_prime
final_threshold
```

Neu data block chua du phuc tap, block se duoc conjugate bang
checkerboard:

```text
S* = S xor Wc
```

## Task 4: Tach tin tu hai video stego

Tach frame tu video BPCS thuong:

```bash
mkdir basic_extract_frames
ffmpeg -hide_banner -i basic_output.avi basic_extract_frames/frame_%04d.png
python3 bpcs_basic_extract.py
```

Tach frame tu video Adaptive BPCS:

```bash
mkdir adaptive_extract_frames
ffmpeg -hide_banner -i adaptive_output.avi adaptive_extract_frames/frame_%04d.png
python3 bpcs_adaptive_extract.py
```

Ket qua can co:

```text
basic_recovered_secret.txt
adaptive_recovered_secret.txt
```

Hai file nay phai chua dung thong diep:

```text
Compare BPCS and Adaptive BPCS
```

## Task 5: So sanh chat luong

Chay:

```bash
python3 compare_metrics.py
```

Ket qua can co:

```text
comparison_report.txt
```

Doc cac chi so:

```text
MSE: gia tri cang thap thi sai khac voi frame goc cang nho.
PSNR: gia tri cang cao thi chat luong sau khi giau tin cang tot.
changed_pixels: so pixel bi thay doi sau khi giau tin.
embedded_blocks: so block da dung de giau payload.
conjugated_blocks: so data block can conjugation.
```

Mau nhan xet:

```text
BPCS thuong dung nguong co dinh nen de cai dat va de giai thich.
Adaptive BPCS tinh nguong theo do phuc tap cua payload, vi vay co the
chon vung nhieu linh hoat hon.

Neu PSNR cua phuong phap nao cao hon va MSE thap hon, phuong phap do
giu chat luong frame tot hon trong lan thu nghiem nay.
```

## Checkwork

Tu terminal Labtainer ben ngoai container:

```bash
checkwork
```

Lab co 5 muc cham:

```text
cw1: co basic_report.txt voi fixed_threshold
cw2: co adaptive_report.txt voi final_threshold
cw3: tach duoc thong diep tu BPCS thuong
cw4: tach duoc thong diep tu Adaptive BPCS
cw5: co comparison_report.txt voi PSNR
```

## Stoplab

```bash
stoplab bpcs_compare_quality
```

## Khoi dong lai lab

```bash
labtainer -r bpcs_compare_quality
```
