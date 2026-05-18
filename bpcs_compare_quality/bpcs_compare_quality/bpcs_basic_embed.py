from pathlib import Path

from bpcs_utils import (
    block_complexity,
    compute_cover_complexities,
    copy_frame_directory,
    iter_block_coords,
    load_frame_bit_plane,
    prepare_payload_blocks,
    rebuild_video,
    save_frame_bit_plane,
    write_json,
    write_report,
)


# ====== Student configuration ======
FRAMES_DIR = "frames"
BASIC_FRAMES_DIR = "basic_frames"
AUDIO_FILE = "audio.mp3"
OUTPUT_VIDEO = "basic_output.avi"
TARGET_FRAME_INDEX = 100
SECRET_DATA = "Compare BPCS and Adaptive BPCS"
FPS = 30

POSITION_FILE = "basic_position.json"
REPORT_FILE = "basic_report.txt"

BLOCK_SIZE = 8
BIT_PLANE = 0
CHANNEL = 0
FIXED_THRESHOLD = 0.35
# ===================================


def main():
    copy_frame_directory(FRAMES_DIR, BASIC_FRAMES_DIR)
    frame, channel, bit_plane, frame_path = load_frame_bit_plane(
        BASIC_FRAMES_DIR, TARGET_FRAME_INDEX, CHANNEL, BIT_PLANE
    )
    secret_bits, payload_blocks = prepare_payload_blocks(
        SECRET_DATA, BLOCK_SIZE, FIXED_THRESHOLD
    )

    cover_alphas = compute_cover_complexities(bit_plane, BLOCK_SIZE)
    usable_cover_blocks = sum(1 for alpha in cover_alphas if alpha >= FIXED_THRESHOLD)
    if usable_cover_blocks < len(payload_blocks):
        raise RuntimeError("Not enough complex cover blocks for normal BPCS.")

    positions = []
    payload_index = 0
    height, width = bit_plane.shape

    for y, x in iter_block_coords(height, width, BLOCK_SIZE):
        if payload_index >= len(payload_blocks):
            break
        cover_block = bit_plane[y : y + BLOCK_SIZE, x : x + BLOCK_SIZE]
        cover_alpha = block_complexity(cover_block)
        if cover_alpha < FIXED_THRESHOLD:
            continue

        payload = payload_blocks[payload_index]
        bit_plane[y : y + BLOCK_SIZE, x : x + BLOCK_SIZE] = payload["block"]
        positions.append(
            {
                "y": int(y),
                "x": int(x),
                "valid_bits": int(payload["valid_bits"]),
                "cover_alpha": round(cover_alpha, 6),
                "alpha_before": round(payload["alpha_before"], 6),
                "alpha_after": round(payload["alpha_after"], 6),
                "conjugated": bool(payload["conjugated"]),
            }
        )
        payload_index += 1

    if payload_index < len(payload_blocks):
        raise RuntimeError(f"Embedded only {payload_index}/{len(payload_blocks)} blocks")

    save_frame_bit_plane(frame, channel, bit_plane, CHANNEL, BIT_PLANE, frame_path)

    report = {
        "method": "normal_bpcs",
        "fixed_threshold": FIXED_THRESHOLD,
        "target_frame_index": TARGET_FRAME_INDEX,
        "payload_bits": len(secret_bits),
        "payload_blocks": len(payload_blocks),
        "cover_blocks": len(cover_alphas),
        "usable_cover_blocks": usable_cover_blocks,
        "embedded_blocks": len(positions),
        "conjugated_blocks": sum(1 for entry in payload_blocks if entry["conjugated"]),
        "output_video": OUTPUT_VIDEO,
    }
    write_report(REPORT_FILE, "Normal BPCS report", report)

    metadata = {
        "method": "Normal BPCS fixed threshold",
        "frame_index": TARGET_FRAME_INDEX,
        "block_size": BLOCK_SIZE,
        "bit_plane": BIT_PLANE,
        "channel": CHANNEL,
        "secret_bit_count": len(secret_bits),
        "secret_text": SECRET_DATA,
        "report": report,
        "positions": positions,
    }
    write_json(POSITION_FILE, metadata)

    print(f"BPCS_POSITION_WRITTEN {POSITION_FILE}")
    print(f"Embedded blocks: {len(positions)}")
    print(f"Report: {Path(REPORT_FILE).resolve()}")
    rebuild_video(BASIC_FRAMES_DIR, AUDIO_FILE, OUTPUT_VIDEO, FPS)


if __name__ == "__main__":
    main()
