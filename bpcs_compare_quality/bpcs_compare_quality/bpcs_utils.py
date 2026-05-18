import json
import math
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np


def text_to_bits(text):
    payload = text.encode("utf-8")
    length_header = len(payload).to_bytes(4, "big")
    data = length_header + payload
    bits = []
    for byte in data:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)
    return bits


def bits_to_bytes(bits):
    out = bytearray()
    for start in range(0, len(bits), 8):
        chunk = bits[start : start + 8]
        if len(chunk) < 8:
            break
        value = 0
        for bit in chunk:
            value = (value << 1) | int(bit)
        out.append(value)
    return bytes(out)


def checkerboard(n):
    y, x = np.indices((n, n))
    return ((x + y) % 2).astype(np.uint8)


def block_complexity(block):
    horizontal = np.sum(block[:, :-1] != block[:, 1:])
    vertical = np.sum(block[:-1, :] != block[1:, :])
    max_transitions = 2 * block.shape[0] * (block.shape[0] - 1)
    return float(horizontal + vertical) / float(max_transitions)


def bits_to_blocks(bits, block_size):
    block_bits = block_size * block_size
    blocks = []
    for start in range(0, len(bits), block_bits):
        chunk = bits[start : start + block_bits]
        valid_bits = len(chunk)
        if len(chunk) < block_bits:
            chunk = chunk + [0] * (block_bits - len(chunk))
        block = np.array(chunk, dtype=np.uint8).reshape(block_size, block_size)
        blocks.append((block, valid_bits))
    return blocks


def prepare_payload_blocks(secret_text, block_size, threshold):
    secret_bits = text_to_bits(secret_text)
    raw_blocks = bits_to_blocks(secret_bits, block_size)
    board = checkerboard(block_size)
    prepared = []

    for index, (block, valid_bits) in enumerate(raw_blocks):
        alpha_before = block_complexity(block)
        conjugated = alpha_before < threshold
        stored_block = block ^ board if conjugated else block
        alpha_after = block_complexity(stored_block)
        prepared.append(
            {
                "index": index,
                "block": stored_block,
                "valid_bits": valid_bits,
                "alpha_before": alpha_before,
                "alpha_after": alpha_after,
                "conjugated": conjugated,
            }
        )

    return secret_bits, prepared


def frame_name(frame_index):
    return f"frame_{frame_index:04d}.png"


def copy_frame_directory(source_dir, dest_dir):
    source = Path(source_dir)
    dest = Path(dest_dir)
    if not source.is_dir():
        raise FileNotFoundError(
            f"Cannot find {source}. Run: ffmpeg -i video.mp4 frames/frame_%04d.png"
        )
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)


def load_frame_bit_plane(frame_dir, frame_index, channel_index, bit_plane_index):
    frame_path = Path(frame_dir) / frame_name(frame_index)
    if not frame_path.exists():
        raise FileNotFoundError(f"Cannot find {frame_path}")

    frame = cv2.imread(str(frame_path), cv2.IMREAD_COLOR)
    if frame is None:
        raise RuntimeError(f"Cannot read frame {frame_path}")

    channel = frame[:, :, channel_index].copy()
    bit_plane = ((channel >> bit_plane_index) & 1).astype(np.uint8)
    return frame, channel, bit_plane, frame_path


def save_frame_bit_plane(frame, channel, bit_plane, channel_index, bit_plane_index, frame_path):
    clear_mask = np.uint8(255 - (1 << bit_plane_index))
    channel = (channel & clear_mask) | (bit_plane.astype(np.uint8) << bit_plane_index)
    frame[:, :, channel_index] = channel
    cv2.imwrite(str(frame_path), frame)


def iter_block_coords(height, width, block_size):
    for y in range(0, height - height % block_size, block_size):
        for x in range(0, width - width % block_size, block_size):
            yield y, x


def compute_cover_complexities(bit_plane, block_size):
    values = []
    height, width = bit_plane.shape
    for y, x in iter_block_coords(height, width, block_size):
        block = bit_plane[y : y + block_size, x : x + block_size]
        values.append(block_complexity(block))
    return values


def rebuild_video(frames_dir, audio_file, output_video, fps):
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        f"{frames_dir}/frame_%04d.png",
    ]
    if Path(audio_file).exists():
        cmd += ["-i", audio_file, "-c:a", "copy", "-shortest"]
    cmd += ["-c:v", "ffv1", output_video]

    print("Rebuilding video:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


def write_report(path, title, values):
    lines = [title]
    for key, value in values.items():
        if isinstance(value, float):
            lines.append(f"{key} = {value:.6f}")
        else:
            lines.append(f"{key} = {value}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def decode_text_from_frame(frame_dir, frame_index, metadata):
    block_size = int(metadata["block_size"])
    bit_plane_index = int(metadata["bit_plane"])
    channel_index = int(metadata["channel"])
    secret_bit_count = int(metadata["secret_bit_count"])
    positions = metadata["positions"]

    frame, _, bit_plane, _ = load_frame_bit_plane(
        frame_dir, frame_index, channel_index, bit_plane_index
    )
    if frame is None:
        raise RuntimeError("Cannot read frame")

    board = checkerboard(block_size)
    bits = []
    for pos in positions:
        y = int(pos["y"])
        x = int(pos["x"])
        valid_bits = int(pos["valid_bits"])
        block = bit_plane[y : y + block_size, x : x + block_size].copy()
        if pos.get("conjugated", False):
            block = block ^ board
        bits.extend(block.reshape(-1).tolist()[:valid_bits])

    bits = bits[:secret_bit_count]
    raw = bits_to_bytes(bits)
    if len(raw) < 4:
        raise RuntimeError("Recovered data is too short")

    payload_len = int.from_bytes(raw[:4], "big")
    available = max(0, len(raw) - 4)
    if payload_len <= 0 or payload_len > available:
        raise RuntimeError("Invalid payload length")

    return raw[4 : 4 + payload_len].decode("utf-8")


def try_decode_to_file(frame_dir, metadata_path, recovered_file, expected_text):
    metadata = read_json(metadata_path)
    target = int(metadata["frame_index"])
    candidates = [target, target + 1, target - 1, target + 2, target - 2]
    tried = []

    for frame_index in candidates:
        if frame_index <= 0 or frame_index in tried:
            continue
        tried.append(frame_index)
        try:
            text = decode_text_from_frame(frame_dir, frame_index, metadata)
        except Exception:
            continue
        if expected_text in text:
            Path(recovered_file).write_text(text, encoding="utf-8")
            return text, frame_index

    raise RuntimeError(
        "Could not recover the expected secret. Check extracted frames and frame index."
    )


def image_metrics(original_path, stego_path):
    original = cv2.imread(str(original_path), cv2.IMREAD_COLOR)
    stego = cv2.imread(str(stego_path), cv2.IMREAD_COLOR)
    if original is None:
        raise RuntimeError(f"Cannot read {original_path}")
    if stego is None:
        raise RuntimeError(f"Cannot read {stego_path}")
    if original.shape != stego.shape:
        raise RuntimeError("Images do not have the same shape")

    diff = original.astype(np.float64) - stego.astype(np.float64)
    mse = float(np.mean(diff * diff))
    psnr = math.inf if mse == 0 else float(20.0 * math.log10(255.0 / math.sqrt(mse)))
    changed_pixels = int(np.count_nonzero(np.any(original != stego, axis=2)))
    return {"MSE": mse, "PSNR": psnr, "changed_pixels": changed_pixels}
