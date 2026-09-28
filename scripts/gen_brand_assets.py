#!/usr/bin/env python3
"""Draw Ten-Four's pocket-recorder identity and platform assets.

The geometry mirrors ``src/components/icons/HandyMark.tsx``. Edit the normalized
128-unit app-icon grid or 32-unit tray grid, then re-run:

    python3 scripts/gen_brand_assets.py [--icon-out PATH]

The script writes tray PNGs into ``src-tauri/resources`` and the 1024px app
icon master into ``src-tauri/icons/app-icon.png``. Run
``bun run tauri icon src-tauri/icons/app-icon.png`` afterward to regenerate the
platform icon family.
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "src-tauri" / "resources"

TALLY = (255, 74, 38, 255)  # #FF4A26
TALLY_HUD = (255, 90, 54, 255)  # #FF5A36
CREAM = (242, 241, 238, 255)
GRAPHITE = (41, 41, 44, 255)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
SS = 8


def vgradient(size, top, bottom):
    """Return an RGBA image filled with a vertical gradient."""
    width, height = size
    t = np.linspace(0, 1, height)[:, None, None]
    rows = (1 - t) * np.array(top, float) + t * np.array(bottom, float)
    return Image.fromarray(np.repeat(rows, width, axis=1).astype("uint8"), "RGBA")


def rrect_mask(size, box, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius, fill=255)
    return mask


def draw_numeric_wordmark(image, origin, scale, ink=CREAM, dot=TALLY):
    """Draw the approved custom ``10.4`` geometry on ``image``."""
    ox, oy = origin

    def points(values):
        return [(ox + x * scale, oy + y * scale) for x, y in values]

    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)

    draw.polygon(
        points([(0, 4), (4, 0), (9, 0), (9, 16), (4.2, 16), (4.2, 5.2), (0, 8)]),
        fill=255,
    )
    draw.polygon(
        points([(11, 3), (14, 0), (23, 0), (26, 3), (26, 13), (23, 16), (14, 16), (11, 13)]),
        fill=255,
    )
    draw.polygon(points([(16, 4), (21, 4), (21, 12), (16, 12)]), fill=0)

    draw.rectangle((ox + 41 * scale, oy, ox + 46 * scale, oy + 16 * scale), fill=255)
    draw.rectangle((ox + 30 * scale, oy + 9 * scale, ox + 49 * scale, oy + 13 * scale), fill=255)
    draw.polygon(points([(30, 8), (37, 0), (42, 0), (36, 9), (41, 9), (41, 13), (30, 13)]), fill=255)

    fill = Image.new("RGBA", image.size, ink)
    image.paste(fill, (0, 0), mask)

    d = ImageDraw.Draw(image)
    cx, cy, radius = ox + 28.5 * scale, oy + 13 * scale, 2.25 * scale
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=dot)


def app_icon(px=1024, state="idle"):
    """Render the pocket recorder app icon: the squircle is the recorder face."""
    scale = px / 128
    image = Image.new("RGBA", (px, px), (0, 0, 0, 0))

    def box(x, y, width, height):
        return (
            round(x * scale),
            round(y * scale),
            round((x + width) * scale),
            round((y + height) * scale),
        )

    # The 104-unit squircle sits on Apple's icon grid (824 of 1024px).
    shadow = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(box(12, 15, 104, 104), 23.5 * scale, fill=(0, 0, 0, 90))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(3 * scale)))

    image.paste(
        vgradient((px, px), (232, 226, 213, 255), (178, 169, 151, 255)),
        (0, 0),
        rrect_mask((px, px), box(12, 12, 104, 104), 23.5 * scale),
    )

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        box(12.4, 12.4, 103.2, 103.2),
        23.1 * scale,
        outline=(255, 255, 255, 130),
        width=max(1, round(0.8 * scale)),
    )

    draw.rounded_rectangle(box(22, 22, 84, 40), 10 * scale, fill=GRAPHITE)
    draw_numeric_wordmark(image, (29.7 * scale, 30.8 * scale), 1.4 * scale)

    draw = ImageDraw.Draw(image)
    for x in (22, 51, 80):
        draw.rounded_rectangle(box(x, 70, 26, 36), 8 * scale, fill=(52, 52, 56, 255))

    record_x, record_y = 35 * scale, 88 * scale
    if state == "recording":
        glow = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse(
            (record_x - 12 * scale, record_y - 12 * scale, record_x + 12 * scale, record_y + 12 * scale),
            fill=(255, 74, 38, 150),
        )
        image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4 * scale)))
        draw = ImageDraw.Draw(image)

    if state == "transcribing":
        draw.ellipse(
            (record_x - 7 * scale, record_y - 7 * scale, record_x + 7 * scale, record_y + 7 * scale),
            outline=CREAM,
            width=max(1, round(2 * scale)),
        )
    else:
        draw.ellipse(
            (record_x - 7 * scale, record_y - 7 * scale, record_x + 7 * scale, record_y + 7 * scale),
            fill=TALLY_HUD if state == "recording" else TALLY,
        )

    draw.rounded_rectangle(box(59.5, 83.5, 9, 9), 1.2 * scale, fill=(221, 214, 199, 255))
    draw.polygon(
        [(89 * scale, 82 * scale), (99 * scale, 88 * scale), (89 * scale, 94 * scale)],
        fill=(221, 214, 199, 255),
    )
    return image


def tray(ink, state="idle", badge=False, px=64):
    """Render the one-color pocket recorder on the 32-unit tray grid."""
    big = px * SS
    unit = big / 32
    image = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (21.5 * unit, 0.5 * unit, 25.5 * unit, 7 * unit),
        2 * unit,
        outline=ink,
        width=round(2 * unit),
    )
    draw.rounded_rectangle(
        (3 * unit, 5 * unit, 29 * unit, 30 * unit),
        4 * unit,
        outline=ink,
        width=round(2.1 * unit),
    )
    draw.rounded_rectangle(
        (7 * unit, 9 * unit, 25 * unit, 17 * unit),
        2 * unit,
        outline=ink,
        width=round(1.7 * unit),
    )

    cx, cy, radius = 10 * unit, 23 * unit, 2.3 * unit
    if state == "transcribing":
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=ink, width=round(1.1 * unit))
    else:
        draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            fill=TALLY if state == "recording" else ink,
        )
    draw.rounded_rectangle((14 * unit, 20.7 * unit, 18.6 * unit, 25.3 * unit), unit, fill=ink)
    draw.polygon(
        [(21.5 * unit, 20.5 * unit), (26.5 * unit, 23.3 * unit), (21.5 * unit, 26.1 * unit)],
        fill=ink,
    )

    if badge:
        bx, by, radius = 26 * unit, 26 * unit, 6.2 * unit
        gap = Image.new("L", (big, big), 255)
        ImageDraw.Draw(gap).ellipse(
            (bx - radius - 1.5 * unit, by - radius - 1.5 * unit, bx + radius + 1.5 * unit, by + radius + 1.5 * unit),
            fill=0,
        )
        image.putalpha(Image.fromarray(np.minimum(np.array(image.getchannel("A")), np.array(gap))))
        draw = ImageDraw.Draw(image)
        draw.ellipse((bx - radius, by - radius, bx + radius, by + radius), fill=ink)
        draw.rounded_rectangle(
            (bx - 0.9 * unit, by - 4 * unit, bx + 0.9 * unit, by + 1.1 * unit),
            0.9 * unit,
            fill=(0, 0, 0, 0),
        )
        draw.ellipse((bx - unit, by + 2 * unit, bx + unit, by + 4 * unit), fill=(0, 0, 0, 0))

    return image.resize((px, px), Image.LANCZOS)


def colored(state, warning=False):
    """Render the full-color tray theme from the app icon."""
    icon = app_icon(512, state)
    draw = ImageDraw.Draw(icon)
    scale = 512 / 128
    if warning:
        bx, by, radius = 98 * scale, 98 * scale, 17 * scale
        draw.ellipse((bx - radius, by - radius, bx + radius, by + radius), fill=(217, 119, 6, 255))
        draw.rounded_rectangle(
            (bx - 2.4 * scale, by - 10 * scale, bx + 2.4 * scale, by + 3 * scale),
            2.4 * scale,
            fill=WHITE,
        )
        draw.ellipse((bx - 2.8 * scale, by + 5 * scale, bx + 2.8 * scale, by + 10.6 * scale), fill=WHITE)
    return icon.crop((40, 40, 472, 472)).resize((64, 64), Image.LANCZOS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--icon-out", default=str(ROOT / "src-tauri" / "icons" / "app-icon.png"))
    args = parser.parse_args()

    for suffix, ink in (("", WHITE), ("_dark", BLACK)):
        tray(ink).save(RES / f"tray_idle{suffix}.png")
        tray(ink, state="recording").save(RES / f"tray_recording{suffix}.png")
        tray(ink, state="transcribing").save(RES / f"tray_transcribing{suffix}.png")
        tray(ink, badge=True).save(RES / f"tray_idle_warning{suffix}.png")

    colored("idle").save(RES / "handy.png")
    colored("recording").save(RES / "recording.png")
    colored("transcribing").save(RES / "transcribing.png")
    colored("idle", warning=True).save(RES / "handy_warning.png")

    app_icon().save(args.icon_out)
    print("wrote tray icons to", RES, "and app icon to", args.icon_out)


if __name__ == "__main__":
    main()
