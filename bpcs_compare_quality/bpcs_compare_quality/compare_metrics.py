from pathlib import Path

from bpcs_utils import frame_name, image_metrics


TARGET_FRAME_INDEX = 100
ORIGINAL_FRAME = Path("frames") / frame_name(TARGET_FRAME_INDEX)
BASIC_FRAME = Path("basic_frames") / frame_name(TARGET_FRAME_INDEX)
ADAPTIVE_FRAME = Path("adaptive_frames") / frame_name(TARGET_FRAME_INDEX)
BASIC_REPORT = Path("basic_report.txt")
ADAPTIVE_REPORT = Path("adaptive_report.txt")
BASIC_RECOVERED = Path("basic_recovered_secret.txt")
ADAPTIVE_RECOVERED = Path("adaptive_recovered_secret.txt")
OUTPUT_REPORT = Path("comparison_report.txt")
EXPECTED_SECRET = "Compare BPCS and Adaptive BPCS"


def parse_report(path):
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        values[key.strip()] = value.strip()
    return values


def decode_ok(path):
    if not path.exists():
        return "no"
    return "yes" if EXPECTED_SECRET in path.read_text(encoding="utf-8") else "no"


def main():
    basic_metrics = image_metrics(ORIGINAL_FRAME, BASIC_FRAME)
    adaptive_metrics = image_metrics(ORIGINAL_FRAME, ADAPTIVE_FRAME)
    basic_report = parse_report(BASIC_REPORT)
    adaptive_report = parse_report(ADAPTIVE_REPORT)

    basic_psnr = basic_metrics["PSNR"]
    adaptive_psnr = adaptive_metrics["PSNR"]
    if adaptive_psnr > basic_psnr:
        conclusion = "Adaptive BPCS has higher PSNR in this run."
    elif adaptive_psnr < basic_psnr:
        conclusion = "Normal BPCS has higher PSNR in this run."
    else:
        conclusion = "Both methods have the same PSNR in this run."

    lines = [
        "BPCS Method Comparison",
        "",
        "method,threshold,usable_blocks,embedded_blocks,conjugated_blocks,MSE,PSNR,changed_pixels,decode_success",
        (
            "normal_bpcs,"
            f"{basic_report.get('fixed_threshold', '')},"
            f"{basic_report.get('usable_cover_blocks', '')},"
            f"{basic_report.get('embedded_blocks', '')},"
            f"{basic_report.get('conjugated_blocks', '')},"
            f"{basic_metrics['MSE']:.6f},"
            f"{basic_metrics['PSNR']:.6f},"
            f"{basic_metrics['changed_pixels']},"
            f"{decode_ok(BASIC_RECOVERED)}"
        ),
        (
            "adaptive_bpcs,"
            f"{adaptive_report.get('final_threshold', '')},"
            f"{adaptive_report.get('usable_cover_blocks', '')},"
            f"{adaptive_report.get('embedded_blocks', '')},"
            f"{adaptive_report.get('conjugated_blocks', '')},"
            f"{adaptive_metrics['MSE']:.6f},"
            f"{adaptive_metrics['PSNR']:.6f},"
            f"{adaptive_metrics['changed_pixels']},"
            f"{decode_ok(ADAPTIVE_RECOVERED)}"
        ),
        "",
        conclusion,
        "",
        "MSE lower is better. PSNR higher is better.",
    ]

    OUTPUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUTPUT_REPORT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
