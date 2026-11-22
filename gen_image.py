"""Draw the one-page newspaper for Saturday 21 November 2026.

The whole front page is rendered with PIL alone -- no photographs, no
downloaded artwork, no network. Layout: masthead with the date, a lead
story on the Gulf, four smaller panels in two rows, one wide panel for
the world court ruling, and a dark "ALSO THAT DAY" strip of briefs.

Stories carried on the page, as reported that Saturday:
  lead   Iran strikes U.S. bases in Bahrain, Gulf tension spreads
  panel  Russian missile strikes the centre of Kryvyi Rih
  panel  Nasdaq falls 5.3% as the AI sell-off deepens
  panel  Mexican forces capture cartel boss "Chapo Isidro"
  panel  COP31 in Antalya runs past its deadline without a deal
  wide   ICJ rules Myanmar committed genocide against the Rohingya
  briefs the penny ends; GTA VI's record first day; dengue trial in Brazil
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
PAPER = (246, 241, 230)
BLACK = (26, 24, 20)
GREY = (94, 88, 78)
BODY_INK = (50, 46, 40)
RED = (148, 38, 28)
CARD = (255, 253, 246)
CARD_EDGE = (118, 110, 94)
LEAD_TINT = (238, 229, 208)
SEA = (24, 44, 66)
COAST = (16, 28, 40)
ARC = (214, 120, 60)

FONT_DIR = "/usr/share/fonts/truetype/noto"
FALLBACK_DIR = "/usr/share/fonts/truetype/dejavu"


def pick_font(noto_name, dejavu_name):
    """Prefer the Noto face; fall back to the DejaVu twin if absent."""
    candidate = os.path.join(FONT_DIR, noto_name)
    return candidate if os.path.isfile(candidate) else os.path.join(
        FALLBACK_DIR, dejavu_name)


SERIF_HEAVY = pick_font("NotoSerif-Black.ttf", "DejaVuSerif-Bold.ttf")
SERIF = pick_font("NotoSerif-Bold.ttf", "DejaVuSerif-Bold.ttf")
SANS_HEAVY = pick_font("NotoSans-Bold.ttf", "DejaVuSans-Bold.ttf")
SANS = pick_font("NotoSans-Regular.ttf", "DejaVuSans.ttf")


def load(path, size):
    return ImageFont.truetype(path, size)


def width_of(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def shrink_to_fit(draw, text, path, size, floor, max_width):
    """Largest size at or below `size` whose rendering fits max_width."""
    while size > floor and width_of(draw, text, load(path, size)) > max_width:
        size -= 2
    return load(path, size)


def wrap_lines(draw, text, fnt, max_width):
    """Greedy word wrap measured in pixels."""
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if width_of(draw, trial, fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def put_lines(draw, x, y, text, fnt, colour, max_width, step):
    """Draw wrapped text; return the y just past the last line."""
    for line in wrap_lines(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=colour)
        y += step
    return y


def put_centred(draw, cx, y, text, fnt, colour):
    draw.text((cx - width_of(draw, text, fnt) / 2, y), text,
              font=fnt, fill=colour)


def story_card(draw, box, kicker, headline, body,
               head_size=23, body_size=17):
    """One bordered news panel; asserts its text stays inside the box."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=CARD, outline=CARD_EDGE, width=2)
    inset = 14
    inner_w = (x1 - x0) - 2 * inset
    y = y0 + 8
    draw.text((x0 + inset, y), kicker, font=load(SANS_HEAVY, 15), fill=RED)
    y += 21
    y = put_lines(draw, x0 + inset, y, headline, load(SERIF, head_size),
                  BLACK, inner_w, head_size + 4)
    y += 3
    y = put_lines(draw, x0 + inset, y, body, load(SANS, body_size),
                  BODY_INK, inner_w, body_size + 4)
    assert y <= y1 - 6, f"overflow in panel '{headline}': ends {y}, box {y1}"
    return y


def gulf_motif(draw, x0, y0, x1, y1):
    """A dark sea band, a jagged coastline and three missile arcs."""
    draw.rectangle([x0, y0, x1, y1], fill=SEA)
    # coastline silhouette along the top edge of the band
    coast = [(x0, y0)]
    steps = 14
    for i in range(steps + 1):
        cx = x0 + (x1 - x0) * i / steps
        cy = y0 + 5 + 7 * abs(math.sin(i * 1.7))
        coast.append((cx, cy))
    coast += [(x1, y0)]
    draw.polygon(coast, fill=COAST)
    # three parabolic arcs rising from the sea and falling back down
    for frac, height in ((0.22, 30), (0.50, 38), (0.78, 27)):
        sx = x0 + (x1 - x0) * (frac - 0.13)
        ex = x0 + (x1 - x0) * (frac + 0.13)
        base = y1 - 5
        pts = []
        for i in range(25):
            t = i / 24
            px = sx + (ex - sx) * t
            py = base - height * 4 * t * (1 - t)
            pts.append((px, py))
        draw.line(pts, fill=ARC, width=3)
        draw.ellipse([ex - 3, base - 5, ex + 3, base + 1], fill=ARC)


def build():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)
    margin = 32
    content_w = PAGE - 2 * margin

    d.rectangle([14, 14, PAGE - 14, PAGE - 14], outline=BLACK, width=3)

    # ---- Masthead ----
    put_centred(d, PAGE / 2, 20, "ONE PAGE  ·  ONE DAY  ·  THE WHOLE WORLD",
                load(SANS_HEAVY, 17), GREY)
    d.line([(margin, 44), (PAGE - margin, 44)], fill=BLACK, width=2)
    name = "THE WORLD IN ONE DAY"
    put_centred(d, PAGE / 2, 50, name,
                shrink_to_fit(d, name, SERIF_HEAVY, 54, 30, content_w), BLACK)
    day = "SATURDAY 21 NOVEMBER 2026"
    put_centred(d, PAGE / 2, 106, day,
                shrink_to_fit(d, day, SERIF_HEAVY, 30, 20, content_w), RED)
    d.line([(margin, 142), (PAGE - margin, 142)], fill=BLACK, width=4)
    d.line([(margin, 149), (PAGE - margin, 149)], fill=BLACK, width=1)

    # ---- Lead: the Gulf ----
    top, bottom = 157, 392
    d.rectangle([margin, top, PAGE - margin, bottom],
                fill=LEAD_TINT, outline=BLACK, width=2)
    d.text((margin + 16, top + 10), "MANAMA · THE GULF",
           font=load(SANS_HEAVY, 17), fill=RED)
    y = put_lines(d, margin + 16, top + 36,
                  "Iran strikes U.S. bases in Bahrain",
                  load(SERIF, 31), BLACK, content_w - 32, 37)
    y = put_lines(
        d, margin + 16, y + 5,
        "Iran's Revolutionary Guards said they hit two U.S. military "
        "positions in Bahrain. Bahrain reported a fire at a civilian "
        "industrial site and said its defences intercepted other attacks, "
        "and projectiles were reported near the Strait of Hormuz. Saudi "
        "defences destroyed three Houthi ballistic missiles fired at "
        "Riyadh, while President Trump weighed new U.S. strikes on Iran "
        "as Israel pressed for action.",
        load(SANS, 18), BODY_INK, content_w - 32, 23)
    band_top = bottom - 46
    assert y <= band_top - 6, f"lead text runs into motif: {y} > {band_top}"
    gulf_motif(d, margin + 2, band_top, PAGE - margin - 2, bottom - 2)

    # ---- Four panels, two rows of two ----
    col_w = (content_w - 12) // 2
    left = (margin, margin + col_w)
    right = (margin + col_w + 12, PAGE - margin)
    story_card(d, (left[0], 400, left[1], 590),
               "KRYVYI RIH · UKRAINE",
               "Russian missile hits Zelensky's hometown",
               "A Russian ballistic missile struck the centre of Kryvyi "
               "Rih on Saturday, killing a paramedic and a seven-year-old "
               "boy and wounding dozens. Russian drones and missiles also "
               "strayed into Polish airspace.")
    story_card(d, (right[0], 400, right[1], 590),
               "NEW YORK · MARKETS",
               "Nasdaq plunges 5.3% in AI rout",
               "U.S. stocks fell into correction as a sell-off in AI and "
               "chip companies capped Wall Street's worst week since 2020. "
               "The fighting in the Gulf added to the unease.")
    story_card(d, (left[0], 598, left[1], 788),
               "GUASAVE · MEXICO",
               "FBI's most-wanted cartel boss captured",
               "Mexican special forces captured Fausto Isidro Meza "
               "Flores, known as Chapo Isidro, who was on the FBI's ten "
               "most-wanted list. Gunfights, fires and road blockades "
               "followed and at least 11 people died.")
    story_card(d, (right[0], 598, right[1], 788),
               "ANTALYA · CLIMATE",
               "Climate talks run past deadline",
               "The UN climate summit COP31 in Antalya, Turkey, ran into "
               "overtime without a deal on fossil fuels, with negotiators "
               "still arguing into the weekend.")

    # ---- Wide panel: the world court ----
    w0, w1 = 796, 915
    d.rectangle([margin, w0, PAGE - margin, w1],
                fill=CARD, outline=CARD_EDGE, width=2)
    d.text((margin + 14, w0 + 8), "THE HAGUE · WORLD COURT",
           font=load(SANS_HEAVY, 15), fill=RED)
    y = put_lines(d, margin + 14, w0 + 29,
                  "Myanmar committed genocide against the Rohingya, "
                  "court rules",
                  load(SERIF, 24), BLACK, content_w - 28, 28)
    y = put_lines(
        d, margin + 14, y + 3,
        "The International Court of Justice ruled that Myanmar's "
        "campaign against its Rohingya Muslim minority amounted to "
        "genocide. Myanmar rejected the ruling as unfair, while "
        "Switzerland called it a crucial step forward for justice.",
        load(SANS, 17), BODY_INK, content_w - 28, 21)
    assert y <= w1 - 6, f"wide panel overflow: {y} > {w1}"

    # ---- ALSO THAT DAY strip ----
    s0, s1 = 923, 1008
    d.rectangle([margin, s0, PAGE - margin, s1],
                fill=BLACK, outline=BLACK, width=2)
    d.text((margin + 14, s0 + 7), "ALSO THAT DAY",
           font=load(SANS_HEAVY, 18), fill=PAPER)
    briefs = [
        "Trump signs law ending production of the penny",
        "GTA VI sells an estimated $2.36 billion on its first day",
        "Mosquitoes carrying a bacterium cut dengue cases among "
        "children in Brazil",
    ]
    brief_w = (content_w - 28 - 16) // 3
    for i, brief in enumerate(briefs):
        bx = margin + 14 + i * (brief_w + 8)
        end = put_lines(d, bx, s0 + 31, "·  " + brief, load(SANS, 15),
                        (224, 218, 202), brief_w, 19)
        assert end <= s1 - 4, f"brief overflow: ends {end} > {s1}"

    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, "entry.png")
    img.save(target, format="PNG", optimize=True)
    print(f"wrote {target} size={os.path.getsize(target)} dims={img.size}")


if __name__ == "__main__":
    build()
