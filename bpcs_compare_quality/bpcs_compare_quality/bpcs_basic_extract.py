from bpcs_utils import try_decode_to_file


# ====== Student configuration ======
EXTRACT_FRAMES_DIR = "basic_extract_frames"
POSITION_FILE = "basic_position.json"
RECOVERED_FILE = "basic_recovered_secret.txt"
EXPECTED_SECRET = "Compare BPCS and Adaptive BPCS"
# ===================================


def main():
    text, frame_index = try_decode_to_file(
        EXTRACT_FRAMES_DIR, POSITION_FILE, RECOVERED_FILE, EXPECTED_SECRET
    )
    print("Recovered normal BPCS secret:")
    print(text)
    print(f"BPCS_DECODE_SUCCESS {RECOVERED_FILE}")
    print(f"decoded_frame_index = {frame_index}")


if __name__ == "__main__":
    main()
