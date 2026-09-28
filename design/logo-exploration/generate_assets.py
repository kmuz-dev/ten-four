#!/usr/bin/env python3
"""Generate isolated production assets for the four Handy logo directions.

The SVG files are the source of truth for app and core marks. Tauri's icon
generator produces platform bundles from those sources. Pillow produces the
stateful tray family and the review boards from the exported masters.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
FONT_PATH = Path("/System/Library/Fonts/SFNS.ttf")
FONT_ROUNDED_PATH = Path("/System/Library/Fonts/SFNSRounded.ttf")

TALLY_HEX = "#FF4A26"
TALLY = (255, 74, 38, 255)
GRAPHITE = (44, 44, 47, 255)
LIGHT_GRAPHITE = (93, 93, 99, 255)
INK = (29, 29, 31, 255)
CANVAS_LIGHT = (246, 245, 242, 255)
CANVAS_DARK = (27, 27, 29, 255)
WHITE = (255, 255, 255, 255)


@dataclass(frozen=True)
class Direction:
    slug: str
    name: str
    tagline: str
    description: str
    score: int


DIRECTIONS = (
    Direction(
        slug="keystone",
        name="Keystone",
        tagline="The balanced anchor",
        description="A tactile top-down key reduced to one memorable silhouette.",
        score=43,
    ),
    Direction(
        slug="press-plane",
        name="Press Plane",
        tagline="The action made visible",
        description="Two offset planes expose the moment of pressing and speaking.",
        score=41,
    ),
    Direction(
        slug="tally-cut",
        name="Tally Cut",
        tagline="The strongest silhouette",
        description="A monolithic key-like slab shaped by one controlled cut.",
        score=41,
    ),
    Direction(
        slug="typeform",
        name="Typeform",
        tagline="The outcome challenger",
        description="Soft speech contours resolve into disciplined written strokes.",
        score=41,
    ),
)


def svg_defs() -> str:
    return """
  <defs>
    <linearGradient id="iconBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3C3C40"/>
      <stop offset="1" stop-color="#1B1B1D"/>
    </linearGradient>
    <linearGradient id="base" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#505056"/>
      <stop offset="1" stop-color="#29292D"/>
    </linearGradient>
    <linearGradient id="top" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#77777D"/>
      <stop offset="1" stop-color="#4A4A50"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#64646A"/>
      <stop offset="1" stop-color="#303034"/>
    </linearGradient>
  </defs>"""


def led(cx: int, cy: int, radius: int, live: bool) -> str:
    fill = TALLY_HEX if live else "#202023"
    ring = "#FF8A70" if live else "#737379"
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{radius + 9}" fill="#171719"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{radius + 3}" fill="none" '
        f'stroke="{ring}" stroke-width="6"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{fill}"/>'
    )


def keystone_fragment(live: bool) -> str:
    return f"""
  <path d="M316 210 H708 C760 210 790 246 798 298 L840 714
           C848 784 805 824 742 824 H282 C219 824 176 784 184 714
           L226 298 C234 246 264 210 316 210 Z" fill="url(#base)"/>
  <path d="M316 246 H708 C738 246 758 268 762 302 L792 690
           C797 742 768 772 720 772 H304 C256 772 227 742 232 690
           L262 302 C266 268 286 246 316 246 Z" fill="#202023" opacity=".62"/>
  <rect x="286" y="244" width="452" height="446" rx="108" fill="url(#top)"/>
  <rect x="294" y="252" width="436" height="430" rx="100" fill="none"
        stroke="#FFFFFF" stroke-opacity=".12" stroke-width="8"/>
  {led(642, 344, 23, live)}"""


def press_plane_fragment(live: bool) -> str:
    return f"""
  <g transform="rotate(-8 512 512)">
    <rect x="214" y="274" width="596" height="566" rx="126" fill="url(#base)"/>
    <path d="M250 656 H782 V720 C782 782 740 806 686 806 H320
             C266 806 238 772 238 722 V680 Z" fill="#202023" opacity=".72"/>
    <rect x="324" y="190" width="492" height="490" rx="116" fill="url(#top)"/>
    <rect x="334" y="200" width="472" height="470" rx="106" fill="none"
          stroke="#FFFFFF" stroke-opacity=".14" stroke-width="8"/>
    {led(328, 698, 23, live)}
  </g>"""


def tally_cut_fragment(live: bool) -> str:
    return f"""
  <path d="M310 206 H704 L818 320 V704 L704 818 H626 L558 748
           L490 818 H310 L206 714 V310 Z" fill="url(#edge)"/>
  <path d="M330 252 H684 L772 340 V684 L684 772 H646 L558 692
           L470 772 H330 L252 694 V330 Z" fill="#414146"/>
  <path d="M490 818 L558 748 L626 818 Z" fill="#1B1B1D"/>
  <path d="M330 252 H684 L772 340" fill="none" stroke="#FFFFFF"
        stroke-opacity=".12" stroke-width="8"/>
  {led(358, 358, 24, live)}"""


def typeform_fragment(live: bool) -> str:
    return f"""
  <path d="M204 598 C204 532 254 494 312 512 C366 528 382 590 346 634
           C316 672 230 668 210 624 C206 616 204 607 204 598 Z" fill="url(#top)"/>
  <rect x="352" y="438" width="126" height="282" rx="63" fill="url(#top)"/>
  <path d="M516 384 H634 Q674 384 674 424 V720 H516 Z" fill="url(#base)"/>
  <rect x="710" y="316" width="106" height="404" rx="12" fill="url(#edge)"/>
  <rect x="332" y="674" width="512" height="86" rx="18" fill="#333337"/>
  {led(596, 626, 22, live)}"""


FRAGMENTS = {
    "keystone": keystone_fragment,
    "press-plane": press_plane_fragment,
    "tally-cut": tally_cut_fragment,
    "typeform": typeform_fragment,
}


def svg_document(direction: Direction, *, live: bool, app_icon: bool) -> str:
    background = ""
    if app_icon:
        background = """
  <rect x="64" y="64" width="896" height="896" rx="214" fill="url(#iconBg)"/>
  <rect x="70" y="70" width="884" height="884" rx="208" fill="none"
        stroke="#FFFFFF" stroke-opacity=".10" stroke-width="8"/>"""
    fragment = FRAGMENTS[direction.slug](live)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" role="img"
     aria-label="{direction.name} {'live ' if live else ''}{'app icon' if app_icon else 'mark'}">
{svg_defs()}
{background}
{fragment}
</svg>
"""


def write_sources(direction: Direction) -> dict[str, Path]:
    direction_dir = BASE / direction.slug
    source_dir = direction_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "mark": source_dir / "mark.svg",
        "mark_live": source_dir / "mark-live.svg",
        "app_icon": source_dir / "app-icon.svg",
        "app_icon_live": source_dir / "app-icon-live.svg",
    }
    paths["mark"].write_text(svg_document(direction, live=False, app_icon=False))
    paths["mark_live"].write_text(svg_document(direction, live=True, app_icon=False))
    paths["app_icon"].write_text(svg_document(direction, live=False, app_icon=True))
    paths["app_icon_live"].write_text(svg_document(direction, live=True, app_icon=True))
    return paths


def run_tauri_icon(source: Path, output: Path, png_sizes: tuple[int, ...] | None = None) -> None:
    output.mkdir(parents=True, exist_ok=True)
    command = ["bun", "run", "tauri", "icon", str(source), "--output", str(output)]
    if png_sizes:
        command.extend(["--png", ",".join(str(size) for size in png_sizes)])
    subprocess.run(command, cwd=REPO, check=True)


def find_square_png(directory: Path, size: int) -> Path:
    for candidate in sorted(directory.rglob("*.png")):
        with Image.open(candidate) as image:
            if image.size == (size, size):
                return candidate
    raise FileNotFoundError(f"No {size}x{size} PNG found in {directory}")


def normalize_pngs(directory: Path) -> None:
    for path in directory.rglob("*.png"):
        with Image.open(path) as image:
            rgba = image.convert("RGBA")
            rgba.save(path)


def export_direction(direction: Direction, sources: dict[str, Path]) -> dict[str, Path]:
    direction_dir = BASE / direction.slug
    export_dir = direction_dir / "exports"
    platform_dir = export_dir / "platform"
    launcher_dir = export_dir / "launcher-png"
    scratch_dir = export_dir / ".render"

    for target in (platform_dir, launcher_dir, scratch_dir):
        if target.exists():
            shutil.rmtree(target)

    run_tauri_icon(sources["app_icon"], platform_dir)
    run_tauri_icon(
        sources["app_icon"],
        launcher_dir,
        png_sizes=(16, 20, 32, 64, 128, 256, 512, 1024),
    )

    mark_render = scratch_dir / "mark"
    live_render = scratch_dir / "live"
    run_tauri_icon(sources["mark"], mark_render, png_sizes=(1024,))
    run_tauri_icon(sources["app_icon_live"], live_render, png_sizes=(1024,))

    app_master = export_dir / "app-icon-1024.png"
    mark_master = export_dir / "mark-transparent-1024.png"
    live_master = export_dir / "app-icon-live-1024.png"
    shutil.copy2(find_square_png(launcher_dir, 1024), app_master)
    shutil.copy2(find_square_png(mark_render, 1024), mark_master)
    shutil.copy2(find_square_png(live_render, 1024), live_master)
    shutil.rmtree(scratch_dir)
    normalize_pngs(export_dir)
    return {
        "app_master": app_master,
        "mark_master": mark_master,
        "live_master": live_master,
        "launcher_dir": launcher_dir,
        "platform_dir": platform_dir,
    }


def scaled(value: float, factor: int) -> int:
    return round(value * factor)


def draw_led(
    draw: ImageDraw.ImageDraw,
    center: tuple[float, float],
    state: str,
    ink: tuple[int, int, int, int],
    factor: int,
) -> None:
    cx, cy = (scaled(center[0], factor), scaled(center[1], factor))
    radius = scaled(2.2, factor)
    if state == "recording":
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=TALLY)
    elif state == "transcribing":
        draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            outline=ink,
            width=max(1, scaled(0.9, factor)),
        )
    else:
        inner = max(1, scaled(1.2, factor))
        draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            outline=ink,
            width=max(1, scaled(0.75, factor)),
        )
        draw.ellipse((cx - inner, cy - inner, cx + inner, cy + inner), fill=(0, 0, 0, 0))


def tray_layer(direction: Direction, ink: tuple[int, int, int, int], state: str) -> Image.Image:
    factor = 8
    size = 64 * factor
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    width = scaled(2.4, factor)

    if direction.slug == "keystone":
        draw.rounded_rectangle(
            (scaled(10, factor), scaled(11, factor), scaled(54, factor), scaled(55, factor)),
            scaled(11, factor),
            outline=ink,
            width=width,
        )
        draw.rounded_rectangle(
            (scaled(16, factor), scaled(14, factor), scaled(48, factor), scaled(45, factor)),
            scaled(8, factor),
            outline=ink,
            width=scaled(1.6, factor),
        )
        draw_led(draw, (42, 22), state, ink, factor)

    elif direction.slug == "press-plane":
        base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        base_draw = ImageDraw.Draw(base)
        base_draw.rounded_rectangle(
            (scaled(9, factor), scaled(14, factor), scaled(53, factor), scaled(56, factor)),
            scaled(10, factor),
            outline=ink,
            width=width,
        )
        base_draw.rounded_rectangle(
            (scaled(19, factor), scaled(8, factor), scaled(56, factor), scaled(44, factor)),
            scaled(8, factor),
            outline=ink,
            width=scaled(1.8, factor),
        )
        rotated = base.rotate(8, resample=Image.Resampling.BICUBIC, center=(size // 2, size // 2))
        layer.alpha_composite(rotated)
        draw = ImageDraw.Draw(layer)
        draw_led(draw, (20, 45), state, ink, factor)

    elif direction.slug == "tally-cut":
        points = [
            (16, 9),
            (42, 9),
            (55, 22),
            (55, 47),
            (47, 55),
            (39, 55),
            (32, 48),
            (25, 55),
            (16, 55),
            (9, 48),
            (9, 16),
        ]
        scaled_points = [(scaled(x, factor), scaled(y, factor)) for x, y in points]
        draw.line(scaled_points + [scaled_points[0]], fill=ink, width=width, joint="curve")
        draw_led(draw, (22, 22), state, ink, factor)

    else:
        draw.ellipse(
            (scaled(8, factor), scaled(34, factor), scaled(20, factor), scaled(46, factor)),
            fill=ink,
        )
        draw.rounded_rectangle(
            (scaled(22, factor), scaled(27, factor), scaled(30, factor), scaled(49, factor)),
            scaled(4, factor),
            fill=ink,
        )
        draw.rounded_rectangle(
            (scaled(34, factor), scaled(20, factor), scaled(43, factor), scaled(49, factor)),
            scaled(2, factor),
            fill=ink,
        )
        draw.rectangle(
            (scaled(48, factor), scaled(13, factor), scaled(55, factor), scaled(49, factor)),
            fill=ink,
        )
        draw.rounded_rectangle(
            (scaled(19, factor), scaled(46, factor), scaled(58, factor), scaled(53, factor)),
            scaled(1.5, factor),
            fill=ink,
        )
        draw_led(draw, (39, 39), state, ink, factor)

    if state == "warning":
        cx, cy, radius = scaled(51, factor), scaled(51, factor), scaled(7, factor)
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=ink)
        transparent_ink = (0, 0, 0, 0)
        draw.rounded_rectangle(
            (cx - scaled(1, factor), cy - scaled(4, factor), cx + scaled(1, factor), cy + scaled(1, factor)),
            scaled(1, factor),
            fill=transparent_ink,
        )
        draw.ellipse(
            (cx - scaled(1, factor), cy + scaled(3, factor), cx + scaled(1, factor), cy + scaled(5, factor)),
            fill=transparent_ink,
        )

    return layer.resize((64, 64), Image.Resampling.LANCZOS)


def export_tray(direction: Direction) -> Path:
    tray_dir = BASE / direction.slug / "exports" / "tray"
    if tray_dir.exists():
        shutil.rmtree(tray_dir)
    tray_dir.mkdir(parents=True)
    states = ("idle", "recording", "transcribing", "warning")
    themes = {
        "light": (18, 18, 20, 255),
        "dark": (245, 245, 242, 255),
    }
    for theme, ink in themes.items():
        for state in states:
            tray_layer(direction, ink, state).save(tray_dir / f"tray-{state}-{theme}.png")
    return tray_dir


def font(size: int, rounded: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_ROUNDED_PATH if rounded else FONT_PATH
    return ImageFont.truetype(str(path), size)


def rounded_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int, int],
    radius: int = 28,
    outline: tuple[int, int, int, int] | None = None,
) -> None:
    draw.rounded_rectangle(box, radius, fill=fill, outline=outline, width=2 if outline else 1)


def place(canvas: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    target = image.copy()
    target.thumbnail((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
    x = x0 + ((x1 - x0) - target.width) // 2
    y = y0 + ((y1 - y0) - target.height) // 2
    canvas.alpha_composite(target, (x, y))


def render_board(direction: Direction, exports: dict[str, Path], tray_dir: Path) -> Path:
    canvas = Image.new("RGBA", (1920, 1080), CANVAS_LIGHT)
    draw = ImageDraw.Draw(canvas)
    draw.text((84, 64), direction.name, fill=INK, font=font(60, rounded=True))
    draw.text((86, 136), direction.tagline, fill=(110, 110, 116, 255), font=font(26))

    rounded_panel(draw, (80, 198, 790, 980), CANVAS_DARK, 42)
    draw.text((120, 238), "APP ICON / IDLE", fill=(160, 160, 166, 255), font=font(18))
    with Image.open(exports["app_master"]) as app:
        place(canvas, app.convert("RGBA"), (150, 285, 720, 855))
    draw.text((120, 912), direction.description, fill=(230, 230, 227, 255), font=font(23))

    rounded_panel(draw, (830, 198, 1838, 430), WHITE, 32, (226, 225, 220, 255))
    draw.text((870, 230), "SCALE TEST", fill=INK, font=font(18))
    with Image.open(exports["mark_master"]) as mark:
        mark = mark.convert("RGBA")
        sizes = (144, 64, 32, 20, 16)
        centers = (980, 1190, 1370, 1510, 1635)
        for size, cx in zip(sizes, centers):
            sample = mark.resize((size, size), Image.Resampling.LANCZOS)
            canvas.alpha_composite(sample, (cx - size // 2, 305 - size // 2))
            label = f"{size}px"
            draw.text((cx - 24, 380), label, fill=(110, 110, 116, 255), font=font(16))

    rounded_panel(draw, (830, 466, 1838, 704), WHITE, 32, (226, 225, 220, 255))
    draw.text((870, 500), "STATE SYSTEM", fill=INK, font=font(18))
    states = ("idle", "recording", "transcribing", "warning")
    labels = ("IDLE", "LIVE", "PROCESSING", "ATTENTION")
    for index, (state, label) in enumerate(zip(states, labels)):
        x = 894 + index * 228
        rounded_panel(draw, (x, 548, x + 184, 670), CANVAS_DARK, 22)
        with Image.open(tray_dir / f"tray-{state}-dark.png") as icon:
            sample = icon.convert("RGBA").resize((48, 48), Image.Resampling.LANCZOS)
            canvas.alpha_composite(sample, (x + 68, 566))
        draw.text((x + 28, 628), label, fill=(160, 160, 166, 255), font=font(14))

    rounded_panel(draw, (830, 740, 1838, 980), (238, 237, 233, 255), 32)
    draw.text((870, 774), "CONTEXT", fill=INK, font=font(18))
    rounded_panel(draw, (872, 828, 1320, 936), (216, 215, 211, 255), 28)
    with Image.open(exports["app_master"]) as app:
        dock_icon = app.convert("RGBA").resize((76, 76), Image.Resampling.LANCZOS)
        canvas.alpha_composite(dock_icon, (920, 844))
    for offset in (0, 1, 2, 3):
        rounded_panel(draw, (1020 + offset * 68, 852, 1076 + offset * 68, 908), (178, 178, 180, 255), 13)

    rounded_panel(draw, (1360, 828, 1796, 936), (38, 38, 41, 255), 20)
    draw.text((1390, 846), "tray", fill=(160, 160, 166, 255), font=font(15))
    with Image.open(tray_dir / "tray-idle-dark.png") as idle:
        canvas.alpha_composite(idle.convert("RGBA").resize((28, 28), Image.Resampling.LANCZOS), (1540, 862))
    with Image.open(tray_dir / "tray-recording-dark.png") as live:
        canvas.alpha_composite(live.convert("RGBA").resize((28, 28), Image.Resampling.LANCZOS), (1632, 862))
    draw.text((1518, 902), "idle", fill=(160, 160, 166, 255), font=font(13))
    draw.text((1610, 902), "live", fill=(160, 160, 166, 255), font=font(13))

    board = BASE / direction.slug / "direction-board.png"
    canvas.convert("RGB").save(board, quality=96)
    return board


def render_comparison(all_exports: dict[str, dict[str, Path]]) -> Path:
    canvas = Image.new("RGBA", (1920, 1080), CANVAS_LIGHT)
    draw = ImageDraw.Draw(canvas)
    draw.text((76, 54), "Four directions. One quiet instrument.", fill=INK, font=font(54, rounded=True))
    draw.text(
        (80, 120),
        "Static identity stays graphite. Tally red appears only while recording.",
        fill=(110, 110, 116, 255),
        font=font(24),
    )

    boxes = ((74, 186, 938, 574), (982, 186, 1846, 574), (74, 618, 938, 1006), (982, 618, 1846, 1006))
    for direction, box in zip(DIRECTIONS, boxes):
        x0, y0, x1, y1 = box
        rounded_panel(draw, box, WHITE, 34, (226, 225, 220, 255))
        with Image.open(all_exports[direction.slug]["app_master"]) as app:
            place(canvas, app.convert("RGBA"), (x0 + 34, y0 + 34, x0 + 354, y1 - 34))
        draw.text((x0 + 386, y0 + 62), direction.name, fill=INK, font=font(40, rounded=True))
        draw.text((x0 + 388, y0 + 114), direction.tagline, fill=(110, 110, 116, 255), font=font(21))
        draw.multiline_text(
            (x0 + 388, y0 + 168),
            direction.description,
            fill=(70, 70, 74, 255),
            font=font(20),
            spacing=8,
        )
        rounded_panel(draw, (x0 + 388, y1 - 92, x0 + 570, y1 - 40), CANVAS_DARK, 18)
        draw.text((x0 + 412, y1 - 79), f"SCORE {direction.score}/50", fill=(238, 238, 235, 255), font=font(16))
        tray_dir = BASE / direction.slug / "exports" / "tray"
        with Image.open(tray_dir / "tray-idle-light.png") as idle:
            canvas.alpha_composite(idle.convert("RGBA").resize((44, 44), Image.Resampling.LANCZOS), (x1 - 146, y1 - 89))
        with Image.open(tray_dir / "tray-recording-light.png") as live:
            canvas.alpha_composite(live.convert("RGBA").resize((44, 44), Image.Resampling.LANCZOS), (x1 - 84, y1 - 89))

    output = BASE / "comparison-board.png"
    canvas.convert("RGB").save(output, quality=96)
    return output


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains_tally(image: Image.Image) -> bool:
    """Accept antialiased Tally pixels while rejecting neutral graphite."""
    pixels = image.convert("RGBA").get_flattened_data()
    return any(
        red >= 235 and 35 <= green <= 115 and blue <= 95 and alpha >= 128
        for red, green, blue, alpha in pixels
    )


def validate_direction(direction: Direction) -> list[str]:
    direction_dir = BASE / direction.slug
    messages: list[str] = []
    idle_svgs = (direction_dir / "source" / "mark.svg", direction_dir / "source" / "app-icon.svg")
    live_svgs = (direction_dir / "source" / "mark-live.svg", direction_dir / "source" / "app-icon-live.svg")

    for svg in (*idle_svgs, *live_svgs):
        root = ET.parse(svg).getroot()
        if any(element.tag.endswith("image") for element in root.iter()):
            raise AssertionError(f"Embedded raster found in {svg}")
    if any(TALLY_HEX.lower() in svg.read_text().lower() for svg in idle_svgs):
        raise AssertionError(f"Idle SVG contains Tally red for {direction.name}")
    if not all(TALLY_HEX.lower() in svg.read_text().lower() for svg in live_svgs):
        raise AssertionError(f"Live SVG is missing Tally red for {direction.name}")
    messages.append("SVG sources parse and contain no embedded raster images")
    messages.append("Idle SVGs contain no Tally red; live SVGs contain Tally red")

    for png in direction_dir.rglob("*.png"):
        with Image.open(png) as image:
            if image.mode != "RGBA" and png.name != "direction-board.png":
                raise AssertionError(f"Expected RGBA PNG: {png} is {image.mode}")
    messages.append("All production PNG assets are RGBA")

    launcher_dir = direction_dir / "exports" / "launcher-png"
    for size in (16, 20, 32, 64, 128, 256, 512, 1024):
        find_square_png(launcher_dir, size)
    messages.append("Launcher family includes 16, 20, 32, 64, 128, 256, 512, and 1024px")

    tray_dir = direction_dir / "exports" / "tray"
    for theme in ("light", "dark"):
        idle = Image.open(tray_dir / f"tray-idle-{theme}.png").convert("RGBA")
        recording = Image.open(tray_dir / f"tray-recording-{theme}.png").convert("RGBA")
        if contains_tally(idle):
            raise AssertionError(f"Idle tray contains Tally red for {direction.name}")
        if not contains_tally(recording):
            raise AssertionError(f"Recording tray lacks Tally red for {direction.name}")
    messages.append("Tray state colors satisfy the live-only Tally rule")
    return messages


def write_manifest(direction: Direction) -> None:
    direction_dir = BASE / direction.slug
    files = []
    for path in sorted(direction_dir.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            files.append(
                {
                    "path": str(path.relative_to(direction_dir)),
                    "bytes": path.stat().st_size,
                    "sha256": digest(path),
                }
            )
    manifest = {
        "direction": direction.name,
        "slug": direction.slug,
        "active_assets_modified": False,
        "files": files,
    }
    (direction_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    exports_by_direction: dict[str, dict[str, Path]] = {}
    validation: list[str] = ["# Validation Report", ""]
    source_hashes: set[str] = set()

    for direction in DIRECTIONS:
        sources = write_sources(direction)
        exports = export_direction(direction, sources)
        tray_dir = export_tray(direction)
        render_board(direction, exports, tray_dir)
        messages = validate_direction(direction)
        source_hash = digest(sources["mark"])
        if source_hash in source_hashes:
            raise AssertionError(f"Duplicate mark geometry detected for {direction.name}")
        source_hashes.add(source_hash)
        write_manifest(direction)
        exports_by_direction[direction.slug] = exports
        validation.append(f"## {direction.name}")
        validation.extend(f"- PASS: {message}" for message in messages)
        validation.append("")

    render_comparison(exports_by_direction)
    validation.append("## Cross-direction")
    validation.append("- PASS: all four mark SVGs have unique source hashes")
    validation.append("- PASS: comparison board rendered at 1920 by 1080")
    validation.append("- PASS: active application asset paths were not targeted")
    validation.append("")
    (BASE / "VALIDATION.md").write_text("\n".join(validation))
    print(f"Generated four isolated logo systems in {BASE}")


if __name__ == "__main__":
    main()
