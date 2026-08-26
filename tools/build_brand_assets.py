"""Build deterministic ChurchManager raster and Windows icon assets.

The approved SVG files remain the authoritative scalable sources. This utility
creates repeatable PNG and ICO exports without network services or proprietary
design software.
"""

from __future__ import annotations

from pathlib import Path
from shutil import copyfile

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "assets" / "brand"
PNG = BRAND / "png"
NAVY = "#0B315B"
GOLD = "#F2B632"
MUTED = "#586A77"
WHITE = "#FFFFFF"


def _scaled_mark(size: int, monochrome: bool = False) -> Image.Image:
    """Return an antialiased transparent ChurchManager mark of ``size`` pixels."""

    scale = 4
    canvas_size = 512 * scale
    image = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    def box(values: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        return tuple(value * scale for value in values)

    def points(values: list[tuple[int, int]]) -> list[tuple[int, int]]:
        return [(x * scale, y * scale) for x, y in values]

    if monochrome:
        ink = NAVY
        draw.rounded_rectangle(box((246, 58, 266, 140)), radius=4 * scale, fill=ink)
        draw.rounded_rectangle(box((220, 82, 292, 102)), radius=4 * scale, fill=ink)
        draw.polygon(points([(256, 118), (194, 184), (220, 184), (220, 300), (292, 300), (292, 184), (318, 184)]), fill=ink)
        draw.polygon(points([(112, 228), (220, 154), (328, 228), (328, 300), (256, 300), (256, 238), (192, 238), (192, 300), (112, 300)]), fill=ink)
        draw.polygon(points([(292, 228), (358, 182), (424, 228), (424, 300), (292, 300)]), fill=ink)
        draw.ellipse(box((204, 173, 244, 213)), fill=WHITE)
        draw.rectangle(box((220, 173, 228, 213)), fill=ink)
        draw.rectangle(box((204, 189, 244, 197)), fill=ink)
        for top in (342, 390, 438):
            draw.rounded_rectangle(box((104, top, 408, top + 22)), radius=11 * scale, fill=ink)
    else:
        draw.rounded_rectangle(
            box((28, 28, 484, 484)),
            radius=104 * scale,
            fill=NAVY,
            outline=GOLD,
            width=18 * scale,
        )
        draw.rounded_rectangle(box((246, 76, 266, 154)), radius=4 * scale, fill=WHITE)
        draw.rounded_rectangle(box((222, 96, 290, 116)), radius=4 * scale, fill=WHITE)
        draw.polygon(points([(256, 132), (194, 198), (220, 198), (220, 314), (292, 314), (292, 198), (318, 198)]), fill=WHITE)
        draw.polygon(points([(126, 241), (220, 176), (314, 241), (314, 314), (256, 314), (256, 252), (192, 252), (192, 314), (126, 314)]), fill=WHITE)
        draw.polygon(points([(292, 241), (350, 201), (408, 241), (408, 314), (292, 314)]), fill=WHITE)
        draw.ellipse(box((204, 187, 244, 227)), fill=NAVY)
        draw.rectangle(box((220, 187, 228, 227)), fill=WHITE)
        draw.rectangle(box((204, 203, 244, 211)), fill=WHITE)
        for top in (346, 386, 426):
            draw.rounded_rectangle(box((118, top, 394, top + 20)), radius=10 * scale, fill=GOLD)

    return image.resize((size, size), Image.Resampling.LANCZOS)


def _font(name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a Windows system font with a portable fallback."""

    candidates = [
        Path("C:/Windows/Fonts") / name,
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _horizontal_logo(width: int) -> Image.Image:
    """Return a transparent horizontal logo at the requested pixel width."""

    height = round(width * 300 / 1120)
    scale = width / 1120
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    mark_size = round(272 * scale)
    mark = _scaled_mark(mark_size)
    image.alpha_composite(mark, (round(7 * scale), round(7 * scale)))
    draw = ImageDraw.Draw(image)
    title_font = _font("seguisb.ttf", max(12, round(88 * scale)))
    tagline_font = _font("segoeui.ttf", max(7, round(27 * scale)))
    draw.text((round(330 * scale), round(70 * scale)), "ChurchManager", fill=NAVY, font=title_font)
    draw.text(
        (round(336 * scale), round(182 * scale)),
        "LOCAL-FIRST CHURCH ADMINISTRATION FOR WINDOWS",
        fill=MUTED,
        font=tagline_font,
    )
    return image


def build() -> None:
    """Create the approved PNG, ICO, favicon, and website identity assets."""

    PNG.mkdir(parents=True, exist_ok=True)
    (ROOT / "website" / "assets").mkdir(parents=True, exist_ok=True)

    sizes = (32, 64, 128, 256, 512, 1024)
    for size in sizes:
        _scaled_mark(size).save(PNG / f"ChurchManager-mark-{size}.png", optimize=True)

    _scaled_mark(512, monochrome=True).save(
        PNG / "ChurchManager-mark-monochrome-512.png", optimize=True
    )
    for width in (600, 1200):
        _horizontal_logo(width).save(
            PNG / f"ChurchManager-logo-horizontal-{width}.png", optimize=True
        )

    icon = _scaled_mark(256)
    icon.save(
        ROOT / "cm.ico",
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    icon.save(
        ROOT / "website" / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    _scaled_mark(1024).save(ROOT / "assets" / "icons" / "ChurchManager-icon.png", optimize=True)
    _scaled_mark(1024).save(
        ROOT / "assets" / "icons" / "ChurchManager-icon-source.png", optimize=True
    )
    copyfile(BRAND / "ChurchManager-mark.svg", ROOT / "website" / "assets" / "ChurchManager-mark.svg")


if __name__ == "__main__":
    build()
