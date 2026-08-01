#!/usr/bin/env python3
"""Generate transparent, theme-neutral visual cues for the clinic website.

The artwork is drawn at build time from simple medical geometry. No icon has a
baked light-mode tile, so the same WebP files remain clean on white, blush and
dark surfaces. Each semantic cue is emitted at 128, 256 and 512 pixels.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "home" / "static" / "images" / "visual-cues"
SIZES = (128, 256, 512)

CUE_SLUGS = {
    "acne": "acne-care",
    "pigmentation": "pigmentation-care",
    "hair": "hair-scalp-care",
    "diagnosis": "dermatologist-diagnosis",
    "experience": "medical-experience",
    "locations": "two-clinic-locations",
    "complete": "complete-care",
    "plan": "personalised-plan",
    "laser": "advanced-laser-care",
    "clinical": "clinical-skin-care",
    "allergy": "allergy-inflammatory-rashes",
    "growths": "moles-growths-nails",
    "scars": "scars-texture-skin-quality",
    "children": "childrens-dermatology",
    "dermatosurgery": "minor-dermatosurgery",
    "ageing": "skin-quality-ageing",
    "infection": "fungal-infection-care",
}

PALETTE = {
    "plum": "#7A2748",
    "plum_dark": "#4D1730",
    "rose": "#E886AB",
    "rose_light": "#F7C8D9",
    "skin": "#F1B9A8",
    "skin_light": "#FFD8C9",
    "gold": "#D3AD5B",
    "gold_light": "#F3D991",
    "teal": "#65A9A0",
    "blue": "#7891C7",
    "blue_light": "#C9D4F0",
    "cream": "#FFF8F5",
    "ink": "#402533",
    "red": "#C95167",
}


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = hex_color.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4)) + (
        alpha,
    )


def canvas() -> Image.Image:
    return Image.new("RGBA", (512, 512), (0, 0, 0, 0))


def shadow(
    layer: Image.Image,
    blur: int = 18,
    offset: tuple[int, int] = (0, 14),
    opacity: int = 70,
) -> Image.Image:
    alpha = layer.getchannel("A").filter(ImageFilter.GaussianBlur(blur))
    shadow_alpha = alpha.point(lambda pixel: pixel * opacity // 255)
    colour = Image.new("RGBA", layer.size, rgba(PALETTE["plum_dark"]))
    colour.putalpha(shadow_alpha)
    shifted = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shifted.alpha_composite(colour, offset)
    return shifted


def finish(layer: Image.Image) -> Image.Image:
    output = canvas()
    output.alpha_composite(shadow(layer))
    output.alpha_composite(layer)
    return output


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: str,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=rgba(fill),
        outline=rgba(outline) if outline else None,
        width=width,
    )


def line(
    draw: ImageDraw.ImageDraw,
    points,
    fill: str,
    width: int = 16,
) -> None:
    draw.line(points, fill=rgba(fill), width=width, joint="curve")


def skin_block(
    draw: ImageDraw.ImageDraw,
    y: int = 288,
    fill: str = "skin_light",
) -> None:
    rounded(
        draw,
        (108, y, 404, y + 128),
        42,
        PALETTE[fill],
        PALETTE["plum"],
        7,
    )
    line(draw, [(108, y + 48), (404, y + 48)], PALETTE["rose"], 8)
    line(
        draw,
        [(108, y + 80), (404, y + 80)],
        PALETTE["gold_light"],
        7,
    )


def icon_acne() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    skin_block(draw, 292)
    for x, y, radius in ((180, 335, 18), (255, 360, 22), (330, 325, 14)):
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=rgba(PALETTE["red"]),
            outline=rgba(PALETTE["plum"]),
            width=6,
        )
        draw.ellipse(
            (x - 5, y - 5, x + 5, y + 5),
            fill=rgba(PALETTE["gold_light"]),
        )
    rounded(
        draw,
        (230, 86, 292, 226),
        22,
        PALETTE["blue_light"],
        PALETTE["plum"],
        7,
    )
    draw.polygon(
        ((265, 70), (315, 120), (289, 146), (242, 98)),
        fill=rgba(PALETTE["gold"]),
        outline=rgba(PALETTE["plum"]),
    )
    line(draw, [(288, 144), (323, 248)], PALETTE["plum"], 14)
    draw.ellipse(
        (306, 232, 340, 270),
        fill=rgba(PALETTE["rose"]),
        outline=rgba(PALETTE["plum"]),
        width=6,
    )
    return finish(layer)


def icon_pigmentation() -> Image.Image:
    import math

    layer = canvas()
    draw = ImageDraw.Draw(layer)
    rounded(
        draw,
        (120, 150, 392, 406),
        74,
        PALETTE["skin_light"],
        PALETTE["plum"],
        7,
    )
    draw.arc(
        (144, 174, 368, 382),
        start=250,
        end=70,
        fill=rgba(PALETTE["rose"]),
        width=12,
    )
    for x, y, radius in ((230, 245, 15), (286, 292, 12), (330, 230, 10), (208, 330, 9)):
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=rgba(PALETTE["gold"]),
            outline=rgba(PALETTE["plum"]),
            width=4,
        )
    draw.ellipse(
        (66, 72, 178, 184),
        fill=rgba(PALETTE["gold_light"]),
        outline=rgba(PALETTE["gold"]),
        width=7,
    )
    for angle in range(0, 360, 45):
        x1 = 122 + 62 * math.cos(math.radians(angle))
        y1 = 128 + 62 * math.sin(math.radians(angle))
        x2 = 122 + 86 * math.cos(math.radians(angle))
        y2 = 128 + 86 * math.sin(math.radians(angle))
        line(draw, [(x1, y1), (x2, y2)], PALETTE["gold"], 8)
    return finish(layer)


def icon_hair() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    skin_block(draw, 300)
    for x in (180, 240, 300, 350):
        draw.arc(
            (x - 60, 110, x + 35, 340),
            start=198,
            end=340,
            fill=rgba(PALETTE["plum_dark"]),
            width=14,
        )
        draw.arc(
            (x - 42, 134, x + 18, 340),
            start=200,
            end=336,
            fill=rgba(PALETTE["rose"]),
            width=7,
        )
    draw.ellipse(
        (215, 296, 296, 376),
        fill=rgba(PALETTE["rose_light"]),
        outline=rgba(PALETTE["plum"]),
        width=6,
    )
    return finish(layer)


def icon_diagnosis() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    rounded(
        draw,
        (130, 86, 360, 416),
        34,
        PALETTE["cream"],
        PALETTE["plum"],
        8,
    )
    rounded(
        draw,
        (196, 56, 294, 118),
        24,
        PALETTE["gold_light"],
        PALETTE["plum"],
        6,
    )
    for y in (170, 228, 286):
        draw.ellipse(
            (170, y, 196, y + 26),
            fill=rgba(PALETTE["teal"]),
            outline=rgba(PALETTE["plum"]),
            width=4,
        )
        line(draw, [(220, y + 13), (320, y + 13)], PALETTE["plum"], 8)
    draw.arc(
        (310, 176, 456, 342),
        start=80,
        end=280,
        fill=rgba(PALETTE["blue"]),
        width=14,
    )
    draw.ellipse(
        (394, 318, 446, 370),
        fill=rgba(PALETTE["rose"]),
        outline=rgba(PALETTE["plum"]),
        width=7,
    )
    line(draw, [(350, 326), (392, 350)], PALETTE["blue"], 13)
    return finish(layer)


def icon_experience() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    draw.polygon(
        ((256, 70), (398, 130), (374, 318), (256, 430), (138, 318), (114, 130)),
        fill=rgba(PALETTE["blue_light"]),
        outline=rgba(PALETTE["plum"]),
    )
    draw.polygon(
        ((256, 104), (360, 148), (342, 292), (256, 380), (170, 292), (152, 148)),
        fill=rgba(PALETTE["cream"]),
        outline=rgba(PALETTE["gold"]),
    )
    rounded(
        draw,
        (224, 164, 288, 322),
        18,
        PALETTE["rose"],
        PALETTE["plum"],
        6,
    )
    rounded(
        draw,
        (176, 212, 336, 276),
        18,
        PALETTE["rose"],
        PALETTE["plum"],
        6,
    )
    draw.arc(
        (174, 126, 338, 370),
        start=210,
        end=330,
        fill=rgba(PALETTE["gold"]),
        width=13,
    )
    return finish(layer)


def icon_locations() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    for offset in (86, 274):
        rounded(
            draw,
            (offset, 220, offset + 150, 388),
            26,
            PALETTE["cream"],
            PALETTE["plum"],
            7,
        )
        draw.polygon(
            ((offset - 8, 220), (offset + 75, 150), (offset + 158, 220)),
            fill=rgba(PALETTE["rose_light"]),
            outline=rgba(PALETTE["plum"]),
        )
        rounded(
            draw,
            (offset + 55, 298, offset + 96, 388),
            12,
            PALETTE["blue_light"],
            PALETTE["plum"],
            5,
        )
        draw.ellipse(
            (offset + 56, 92, offset + 100, 136),
            fill=rgba(PALETTE["rose"]),
            outline=rgba(PALETTE["plum"]),
            width=6,
        )
        draw.polygon(
            ((offset + 78, 150), (offset + 54, 120), (offset + 102, 120)),
            fill=rgba(PALETTE["rose"]),
            outline=rgba(PALETTE["plum"]),
        )
    line(draw, [(160, 424), (352, 424)], PALETTE["gold"], 12)
    return finish(layer)


def icon_complete() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    rounded(
        draw,
        (220, 118, 292, 330),
        20,
        PALETTE["rose"],
        PALETTE["plum"],
        6,
    )
    rounded(
        draw,
        (150, 188, 362, 260),
        20,
        PALETTE["rose"],
        PALETTE["plum"],
        6,
    )
    draw.arc(
        (70, 78, 246, 254),
        start=8,
        end=132,
        fill=rgba(PALETTE["gold"]),
        width=16,
    )
    draw.arc(
        (264, 70, 442, 248),
        start=48,
        end=174,
        fill=rgba(PALETTE["blue"]),
        width=16,
    )
    skin_block(draw, 330)
    for x in (184, 226, 268):
        draw.arc(
            (x - 36, 250, x + 34, 358),
            start=198,
            end=340,
            fill=rgba(PALETTE["plum_dark"]),
            width=8,
        )
    return finish(layer)


def icon_plan() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    rounded(
        draw,
        (138, 84, 374, 420),
        34,
        PALETTE["cream"],
        PALETTE["plum"],
        8,
    )
    rounded(
        draw,
        (204, 54, 308, 120),
        24,
        PALETTE["gold_light"],
        PALETTE["plum"],
        6,
    )
    for y in (164, 228, 292):
        line(
            draw,
            [(176, y + 16), (190, y + 30), (216, y)],
            PALETTE["teal"],
            10,
        )
        line(draw, [(236, y + 10), (334, y + 10)], PALETTE["plum"], 8)
    rounded(
        draw,
        (80, 286, 142, 414),
        20,
        PALETTE["rose_light"],
        PALETTE["plum"],
        6,
    )
    draw.ellipse(
        (90, 264, 132, 306),
        fill=rgba(PALETTE["gold"]),
        outline=rgba(PALETTE["plum"]),
        width=5,
    )
    return finish(layer)


def icon_laser() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    skin_block(draw, 306)
    rounded(
        draw,
        (192, 86, 270, 238),
        26,
        PALETTE["blue_light"],
        PALETTE["plum"],
        7,
    )
    draw.polygon(
        ((244, 80), (358, 158), (324, 202), (220, 124)),
        fill=rgba(PALETTE["gold_light"]),
        outline=rgba(PALETTE["plum"]),
    )
    line(draw, [(326, 205), (288, 310)], PALETTE["rose"], 12)
    for x in (248, 280, 312):
        line(draw, [(x, 278), (x - 18, 306)], PALETTE["gold"], 6)
    return finish(layer)


def icon_clinical() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    skin_block(draw, 314)
    draw.ellipse(
        (104, 90, 300, 286),
        fill=rgba(PALETTE["cream"]),
        outline=rgba(PALETTE["plum"]),
        width=10,
    )
    draw.ellipse(
        (146, 132, 258, 244),
        fill=rgba(PALETTE["rose_light"]),
        outline=rgba(PALETTE["plum"]),
        width=7,
    )
    for x, y in ((180, 170), (216, 198), (190, 224)):
        draw.ellipse(
            (x - 12, y - 12, x + 12, y + 12),
            fill=rgba(PALETTE["red"]),
        )
    line(draw, [(270, 260), (380, 370)], PALETTE["blue"], 30)
    draw.ellipse(
        (352, 342, 410, 400),
        fill=rgba(PALETTE["gold"]),
        outline=rgba(PALETTE["plum"]),
        width=8,
    )
    return finish(layer)


def icon_allergy() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    rounded(
        draw,
        (118, 130, 394, 404),
        74,
        PALETTE["skin_light"],
        PALETTE["plum"],
        8,
    )
    for x, y, radius in ((190, 222, 18), (260, 190, 14), (312, 252, 22), (220, 310, 13), (330, 328, 12)):
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=rgba(PALETTE["red"]),
            outline=rgba(PALETTE["plum"]),
            width=4,
        )
    for points in (
        ((88, 178), (58, 160), (76, 132)),
        ((410, 190), (446, 166), (430, 132)),
        ((380, 382), (422, 410), (414, 448)),
    ):
        line(draw, points, PALETTE["gold"], 10)
    line(
        draw,
        [(270, 270), (300, 300), (276, 332), (320, 362)],
        PALETTE["rose"],
        9,
    )
    return finish(layer)


def icon_growths() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    rounded(
        draw,
        (110, 194, 266, 412),
        70,
        PALETTE["skin_light"],
        PALETTE["plum"],
        8,
    )
    rounded(
        draw,
        (226, 98, 394, 412),
        72,
        PALETTE["skin"],
        PALETTE["plum"],
        8,
    )
    rounded(
        draw,
        (260, 130, 360, 196),
        28,
        PALETTE["cream"],
        PALETTE["rose"],
        6,
    )
    draw.ellipse(
        (150, 248, 196, 294),
        fill=rgba(PALETTE["plum"]),
        outline=rgba(PALETTE["gold"]),
        width=5,
    )
    draw.ellipse(
        (184, 324, 226, 366),
        fill=rgba(PALETTE["rose"]),
        outline=rgba(PALETTE["plum"]),
        width=5,
    )
    line(draw, [(284, 112), (330, 86), (364, 122)], PALETTE["gold"], 10)
    return finish(layer)


def icon_scars() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    skin_block(draw, 228)
    line(
        draw,
        [(150, 290), (194, 256), (232, 314), (276, 270), (330, 322), (372, 276)],
        PALETTE["plum"],
        12,
    )
    for x in range(154, 380, 44):
        draw.ellipse((x, 366, x + 16, 382), fill=rgba(PALETTE["teal"]))
    draw.arc(
        (96, 82, 262, 238),
        start=210,
        end=45,
        fill=rgba(PALETTE["gold"]),
        width=14,
    )
    draw.polygon(
        ((260, 96), (278, 148), (228, 138)),
        fill=rgba(PALETTE["gold"]),
    )
    draw.arc(
        (250, 70, 432, 250),
        start=30,
        end=155,
        fill=rgba(PALETTE["rose"]),
        width=14,
    )
    draw.polygon(
        ((246, 202), (232, 150), (282, 164)),
        fill=rgba(PALETTE["rose"]),
    )
    return finish(layer)


def icon_children() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    draw.ellipse(
        (154, 90, 358, 294),
        fill=rgba(PALETTE["skin_light"]),
        outline=rgba(PALETTE["plum"]),
        width=8,
    )
    draw.arc(
        (170, 70, 344, 250),
        start=190,
        end=350,
        fill=rgba(PALETTE["plum_dark"]),
        width=28,
    )
    draw.ellipse((210, 182, 230, 202), fill=rgba(PALETTE["ink"]))
    draw.ellipse((282, 182, 302, 202), fill=rgba(PALETTE["ink"]))
    draw.arc(
        (224, 204, 292, 250),
        start=10,
        end=170,
        fill=rgba(PALETTE["rose"]),
        width=8,
    )
    rounded(
        draw,
        (136, 286, 376, 426),
        58,
        PALETTE["blue_light"],
        PALETTE["plum"],
        8,
    )
    rounded(
        draw,
        (224, 302, 288, 404),
        18,
        PALETTE["rose"],
        PALETTE["plum"],
        5,
    )
    rounded(
        draw,
        (204, 322, 308, 384),
        18,
        PALETTE["rose"],
        PALETTE["plum"],
        5,
    )
    return finish(layer)


def icon_dermatosurgery() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    skin_block(draw, 304)
    line(
        draw,
        [(154, 350), (200, 322), (244, 356), (292, 322), (342, 354)],
        PALETTE["plum"],
        10,
    )
    for x in (184, 226, 270, 316):
        line(draw, [(x, 318), (x + 10, 370)], PALETTE["gold"], 6)
    rounded(
        draw,
        (112, 100, 338, 154),
        20,
        PALETTE["blue_light"],
        PALETTE["plum"],
        7,
    )
    draw.polygon(
        ((334, 102), (430, 126), (336, 154)),
        fill=rgba(PALETTE["gold_light"]),
        outline=rgba(PALETTE["plum"]),
    )
    line(draw, [(194, 154), (246, 294)], PALETTE["blue"], 16)
    return finish(layer)


def icon_ageing() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    draw.arc(
        (126, 72, 390, 430),
        start=80,
        end=282,
        fill=rgba(PALETTE["skin"]),
        width=56,
    )
    draw.arc(
        (168, 110, 356, 388),
        start=90,
        end=275,
        fill=rgba(PALETTE["plum"]),
        width=9,
    )
    line(draw, [(272, 206), (320, 222)], PALETTE["plum"], 8)
    line(draw, [(266, 250), (314, 254)], PALETTE["rose"], 7)
    for x, y in ((106, 118), (396, 108), (420, 250)):
        line(draw, [(x - 18, y), (x + 18, y)], PALETTE["gold"], 8)
        line(draw, [(x, y - 18), (x, y + 18)], PALETTE["gold"], 8)
    draw.arc(
        (74, 278, 232, 440),
        start=210,
        end=330,
        fill=rgba(PALETTE["teal"]),
        width=14,
    )
    draw.polygon(
        ((220, 414), (250, 392), (238, 430)),
        fill=rgba(PALETTE["teal"]),
    )
    return finish(layer)


def icon_infection() -> Image.Image:
    layer = canvas()
    draw = ImageDraw.Draw(layer)
    rounded(
        draw,
        (110, 214, 402, 404),
        60,
        PALETTE["skin_light"],
        PALETTE["plum"],
        8,
    )
    draw.ellipse(
        (178, 250, 310, 382),
        outline=rgba(PALETTE["red"]),
        width=18,
    )
    draw.ellipse((216, 286, 272, 342), fill=rgba(PALETTE["cream"]))
    for x, y in ((340, 260), (364, 312), (332, 352)):
        draw.ellipse(
            (x - 14, y - 14, x + 14, y + 14),
            fill=rgba(PALETTE["gold"]),
            outline=rgba(PALETTE["plum"]),
            width=4,
        )
    draw.ellipse(
        (82, 70, 282, 270),
        fill=rgba(PALETTE["cream"]),
        outline=rgba(PALETTE["plum"]),
        width=10,
    )
    draw.ellipse(
        (126, 114, 238, 226),
        outline=rgba(PALETTE["red"]),
        width=15,
    )
    line(draw, [(254, 242), (382, 372)], PALETTE["blue"], 28)
    return finish(layer)


GENERATORS = {
    "acne": icon_acne,
    "pigmentation": icon_pigmentation,
    "hair": icon_hair,
    "diagnosis": icon_diagnosis,
    "experience": icon_experience,
    "locations": icon_locations,
    "complete": icon_complete,
    "plan": icon_plan,
    "laser": icon_laser,
    "clinical": icon_clinical,
    "allergy": icon_allergy,
    "growths": icon_growths,
    "scars": icon_scars,
    "children": icon_children,
    "dermatosurgery": icon_dermatosurgery,
    "ageing": icon_ageing,
    "infection": icon_infection,
}


def _webp_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(
        buffer,
        format="WEBP",
        lossless=True,
        method=6,
        exact=True,
    )
    return buffer.getvalue()


def _write_if_changed(path: Path, data: bytes) -> bool:
    if path.is_file() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def build_assets() -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    expected_names: set[str] = set()
    changed: list[Path] = []

    for cue, generator in sorted(GENERATORS.items()):
        source = generator()
        slug = CUE_SLUGS[cue]
        for size in SIZES:
            name = f"{slug}-{size}.webp"
            expected_names.add(name)
            rendered = (
                source.copy()
                if size == 512
                else source.resize((size, size), Image.Resampling.LANCZOS)
            )
            output = OUTPUT_DIR / name
            if _write_if_changed(output, _webp_bytes(rendered)):
                changed.append(output)

    for stale in OUTPUT_DIR.glob("*.webp"):
        if stale.name not in expected_names:
            stale.unlink()
            changed.append(stale)

    return changed


def main() -> int:
    changed = build_assets()
    status = (
        f"generated {len(changed)} changed file(s)"
        if changed
        else "already current"
    )
    print(f"Visual cue assets: {status} in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
