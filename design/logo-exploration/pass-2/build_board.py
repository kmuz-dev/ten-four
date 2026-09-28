#!/usr/bin/env python3
"""Build the consistent review board for logo exploration pass 2."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/SFNS.ttf"
FONT_ROUNDED = "/System/Library/Fonts/SFNSRounded.ttf"
CANVAS = (245, 243, 238, 255)
INK = (28, 28, 30, 255)
SECONDARY = (105, 104, 109, 255)
HAIRLINE = (218, 216, 209, 255)
WHITE = (255, 255, 255, 255)


OPTIONS = (
    ("01-caret-pulse.png", "01", "Caret Pulse", "Voice resolves into the insertion point."),
    ("02-press-seal.png", "02", "Press Seal", "The held gesture becomes the identity."),
    ("03-quiet-fold.png", "03", "Quiet Fold", "Soft input folds into written output."),
    ("04-pressure-field.png", "04", "Pressure Field", "A stable shell reacts to one deliberate press."),
    ("05-language-blocks.png", "05", "Language Blocks", "Organic language becomes typographic structure."),
)


def font(size: int, rounded: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_ROUNDED if rounded else FONT, size)


def cropped_mark(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    alpha_box = image.getchannel("A").getbbox()
    if alpha_box is None:
        raise ValueError(f"No visible pixels in {path}")
    image = image.crop(alpha_box)
    padding = max(image.size) // 14
    padded = Image.new("RGBA", (image.width + padding * 2, image.height + padding * 2), (0, 0, 0, 0))
    padded.alpha_composite(image, (padding, padding))
    return padded


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    output = image.copy()
    output.thumbnail(size, Image.Resampling.LANCZOS)
    return output


def draw_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    option: tuple[str, str, str, str],
) -> None:
    filename, number, name, rationale = option
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, 34, fill=WHITE, outline=HAIRLINE, width=2)
    draw.text((x0 + 34, y0 + 28), number, fill=SECONDARY, font=font(18))
    draw.text((x0 + 86, y0 + 24), name, fill=INK, font=font(34, rounded=True))
    draw.text((x0 + 36, y1 - 72), rationale, fill=SECONDARY, font=font(18))

    mark = cropped_mark(ROOT / "options" / filename)
    hero = fit(mark, (330, 290))
    hero_x = x0 + 42 + (330 - hero.width) // 2
    hero_y = y0 + 82 + (290 - hero.height) // 2
    canvas.alpha_composite(hero, (hero_x, hero_y))

    draw.text((x1 - 154, y0 + 92), "SCALE", fill=SECONDARY, font=font(13))
    for size, y in ((48, y0 + 136), (24, y0 + 232), (16, y0 + 302)):
        sample = fit(mark, (size, size))
        sample_x = x1 - 104 + (48 - sample.width) // 2
        sample_y = y + (48 - sample.height) // 2
        canvas.alpha_composite(sample, (sample_x, sample_y))
        draw.text((x1 - 50, y + 13), f"{size}px", fill=SECONDARY, font=font(13))


def main() -> None:
    canvas = Image.new("RGBA", (1920, 1260), CANVAS)
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 48), "Logo exploration / Pass 2", fill=INK, font=font(56, rounded=True))
    draw.text(
        (74, 118),
        "Five independent ideas based only on the product: press, speak, local processing, written output.",
        fill=SECONDARY,
        font=font(23),
    )

    boxes = (
        (60, 184, 620, 664),
        (680, 184, 1240, 664),
        (1300, 184, 1860, 664),
        (370, 716, 930, 1196),
        (990, 716, 1550, 1196),
    )
    for box, option in zip(boxes, OPTIONS):
        draw_card(canvas, draw, box, option)

    canvas.convert("RGB").save(ROOT / "comparison-board.png", quality=96)


if __name__ == "__main__":
    main()
