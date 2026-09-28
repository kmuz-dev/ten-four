#!/usr/bin/env python3
"""Draw Handy's mark (DESIGN.md, "Mark"): the app icon and every tray icon.

One keycap seen from above with a caps-lock style LED; the LED is the only
color, and it is Tally. Everything is drawn from the geometry below, so edit a
number and re-run:

    python3 scripts/gen_brand_assets.py [--icon-out PATH]

Writes the tray PNGs into src-tauri/resources/ and a 1024px app icon (default
src-tauri/icons/app-icon.png); feed that to `bun run tauri icon <png>` to
regenerate the platform icon sets.
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "src-tauri" / "resources"

TALLY = (255, 74, 38, 255)  # #FF4A26
TALLY_HUD = (255, 90, 54, 255)  # #FF5A36, the LED on graphite
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
SS = 8  # supersampling factor for smooth edges


def vgradient(size, top, bottom):
    """RGBA image of `size` filled with a vertical gradient."""
    w, h = size
    t = np.linspace(0, 1, h)[:, None, None]
    rows = (1 - t) * np.array(top, float) + t * np.array(bottom, float)
    return Image.fromarray(np.repeat(rows, w, axis=1).astype("uint8"), "RGBA")


def rrect_mask(size, box, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius, fill=255)
    return mask


# ---------------------------------------------------------------- app icon


def app_icon(px=1024):
    """Graphite squircle, graphite keycap, Tally LED with a soft glow.

    Geometry is on the 128-unit grid from the design prototype; the squircle
    spans 12..116 (the ~81% macOS icon grid) so the system shadow has room.
    """
    s = px / 128
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))

    def box(x, y, w, h):
        return (round(x * s), round(y * s), round((x + w) * s), round((y + h) * s))

    # Soft shadow under the squircle.
    shadow = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        box(12, 14, 104, 104), 23.5 * s, fill=(0, 0, 0, 90)
    )
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2.2 * s)))

    layers = [
        # (box, radius, gradient top, gradient bottom)
        (box(12, 12, 104, 104), 23.5, (60, 60, 64, 255), (28, 28, 31, 255)),
        (box(30, 31, 68, 68), 17, (75, 75, 80, 255), (39, 39, 42, 255)),
        (box(38, 35, 52, 52), 13, (96, 96, 102, 255), (70, 70, 75, 255)),
    ]
    for b, r, top, bottom in layers:
        img.paste(vgradient((px, px), top, bottom), (0, 0), rrect_mask((px, px), b, r * s))

    # Hairline highlights on the squircle and the keycap's top face.
    lines = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(lines)
    d.rounded_rectangle(box(12.5, 12.5, 103, 103), 23 * s, outline=(255, 255, 255, 26), width=max(1, round(s)))
    d.rounded_rectangle(box(38.5, 35.5, 51, 51), 12.5 * s, outline=(255, 255, 255, 36), width=max(1, round(s)))
    img.alpha_composite(lines)

    # The LED: glow, then the lamp.
    glow = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    gx, gy = 78 * s, 47 * s
    ImageDraw.Draw(glow).ellipse((gx - 7 * s, gy - 7 * s, gx + 7 * s, gy + 7 * s), fill=(255, 74, 38, 150))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(3.5 * s)))
    ImageDraw.Draw(img).ellipse(
        (gx - 3.6 * s, gy - 3.6 * s, gx + 3.6 * s, gy + 3.6 * s), fill=TALLY_HUD
    )
    return img


# ------------------------------------------------------------- tray icons


def tray(ink, led="solid", led_color=None, badge=False, px=64):
    """The keycap outline on a 32-unit grid (matches HandyMark in the UI).

    led: "solid" (filled in `led_color` or ink), "ring" (hollow: working), or
    "none". badge: a small "!" disc in the lower right (needs attention).
    """
    big = px * SS
    u = big / 32
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((3 * u, 3 * u, 29 * u, 29 * u), 7 * u, outline=ink, width=round(2.2 * u))
    d.rounded_rectangle((7.5 * u, 6 * u, 24.5 * u, 23 * u), 4.5 * u, outline=ink, width=round(1.7 * u))
    cx, cy, r = 19.8 * u, 10.3 * u, 2.3 * u
    if led == "solid":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=led_color or ink)
    elif led == "ring":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ink, width=round(1.1 * u))
    if badge:
        bx, by, br = 25 * u, 25 * u, 6.6 * u
        # Punch a gap around the badge so it reads over the outline.
        gap = Image.new("L", (big, big), 255)
        ImageDraw.Draw(gap).ellipse((bx - br - 1.6 * u, by - br - 1.6 * u, bx + br + 1.6 * u, by + br + 1.6 * u), fill=0)
        img.putalpha(Image.fromarray(np.minimum(np.array(img.getchannel("A")), np.array(gap))))
        d = ImageDraw.Draw(img)
        d.ellipse((bx - br, by - br, bx + br, by + br), fill=ink)
        cut = (0, 0, 0, 0)
        d.rounded_rectangle((bx - 0.95 * u, by - 4.2 * u, bx + 0.95 * u, by + 1.2 * u), 0.9 * u, fill=cut)
        d.ellipse((bx - 1.05 * u, by + 2.1 * u, bx + 1.05 * u, by + 4.2 * u), fill=cut)
    return img.resize((px, px), Image.LANCZOS)


def colored(state, warning=False):
    """The "colored" tray theme: a miniature of the app icon itself."""
    icon = app_icon(512)
    d = ImageDraw.Draw(icon)
    s = 512 / 128
    if state == "transcribing":
        # Dim the LED to graphite with a light ring: busy, not live.
        gx, gy = 78 * s, 47 * s
        d.ellipse((gx - 9 * s, gy - 9 * s, gx + 9 * s, gy + 9 * s), fill=(70, 70, 75, 255))
        d.ellipse((gx - 4 * s, gy - 4 * s, gx + 4 * s, gy + 4 * s), outline=(235, 235, 235, 255), width=round(1.4 * s))
    if warning:
        # A white "!" on the warning orange, in the icon's lower right.
        bx, by, br = 98 * s, 98 * s, 17 * s
        d.ellipse((bx - br, by - br, bx + br, by + br), fill=(217, 119, 6, 255))
        d.rounded_rectangle((bx - 2.4 * s, by - 10 * s, bx + 2.4 * s, by + 3 * s), 2.4 * s, fill=WHITE)
        d.ellipse((bx - 2.8 * s, by + 5 * s, bx + 2.8 * s, by + 10.6 * s), fill=WHITE)
    # Crop to the squircle so it fills the menu bar slot.
    return icon.crop((40, 40, 472, 472)).resize((64, 64), Image.LANCZOS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--icon-out", default=str(ROOT / "src-tauri" / "icons" / "app-icon.png"))
    args = parser.parse_args()

    # White marks for dark menu bars, black (`_dark` files) for light ones.
    for suffix, ink in (("", WHITE), ("_dark", BLACK)):
        tray(ink).save(RES / f"tray_idle{suffix}.png")
        tray(ink, led_color=TALLY).save(RES / f"tray_recording{suffix}.png")
        tray(ink, led="ring").save(RES / f"tray_transcribing{suffix}.png")
        tray(ink, badge=True).save(RES / f"tray_idle_warning{suffix}.png")

    colored("idle").save(RES / "handy.png")
    colored("recording").save(RES / "recording.png")
    colored("transcribing").save(RES / "transcribing.png")
    colored("idle", warning=True).save(RES / "handy_warning.png")

    app_icon().save(args.icon_out)
    print("wrote tray icons to", RES, "and app icon to", args.icon_out)


if __name__ == "__main__":
    main()
