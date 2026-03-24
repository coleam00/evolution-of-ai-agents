#!/usr/bin/env python3
"""
Slide Visual Validator - Renders PPTX slides to PNG for visual inspection.

Uses aspose-slides to render each slide as a high-quality PNG image.
Images are saved to a temporary preview folder for Claude to visually analyze.

Usage:
    uv run --with aspose-slides python validate-slides.py <pptx_path> [--slides 1,5,10] [--output-dir ./preview]

Arguments:
    pptx_path       Path to the PPTX file to validate
    --slides        Comma-separated slide numbers to render (default: all)
    --output-dir    Directory to save preview images (default: .tmp/preview)
    --scale         Render scale factor (default: 2.0 for 2x resolution)
"""
import argparse
import os
import sys


def render_slides(pptx_path: str, output_dir: str, slide_numbers: list[int] | None = None, scale: float = 2.0):
    """Render PPTX slides to PNG images for visual inspection."""
    try:
        import aspose.slides as slides
    except ImportError:
        print("ERROR: aspose-slides not installed. Run:")
        print("  uv run --with aspose-slides python validate-slides.py <path>")
        sys.exit(1)

    if not os.path.exists(pptx_path):
        print(f"ERROR: File not found: {pptx_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    prs = slides.Presentation(pptx_path)
    total = prs.slides.length
    print(f"Loaded {total} slides from {os.path.basename(pptx_path)}")

    if slide_numbers is None:
        slide_numbers = list(range(1, total + 1))

    rendered = []
    for num in slide_numbers:
        if num < 1 or num > total:
            print(f"  WARNING: Slide {num} out of range (1-{total}), skipping")
            continue

        slide = prs.slides[num - 1]
        out_path = os.path.join(output_dir, f"slide_{num:02d}.png")
        bitmap = slide.get_image(scale, scale)
        bitmap.save(out_path, slides.ImageFormat.PNG)
        rendered.append(out_path)
        print(f"  Rendered slide {num:2d} -> {out_path}")

    print(f"\nRendered {len(rendered)} slides to {output_dir}")
    print("\nTo validate visually, read the PNG files and inspect for:")
    print("  - Spacing and alignment issues")
    print("  - Text overflow or truncation")
    print("  - Overlapping elements")
    print("  - Empty/unused space")
    print("  - Consistent styling across slides")
    print("  - Background color correctness")

    return rendered


def main():
    parser = argparse.ArgumentParser(description="Render PPTX slides to PNG for visual validation")
    parser.add_argument("pptx_path", help="Path to the PPTX file")
    parser.add_argument("--slides", help="Comma-separated slide numbers (default: all)", default=None)
    parser.add_argument("--output-dir", help="Output directory for PNGs", default=".tmp/preview")
    parser.add_argument("--scale", help="Render scale factor", type=float, default=2.0)

    args = parser.parse_args()

    slide_numbers = None
    if args.slides:
        slide_numbers = [int(s.strip()) for s in args.slides.split(",")]

    render_slides(args.pptx_path, args.output_dir, slide_numbers, args.scale)


if __name__ == "__main__":
    main()
