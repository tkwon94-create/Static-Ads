#!/usr/bin/env python3
"""Regenerate the six ads the user gave notes on, carrying every prior directive.

Each prompt is assembled as: base prompt -> peach ground (for the peach-led ads)
-> this refinement -> placeholder instruction. Order matters: the refinement has to
sit after the ground override, and the placeholder last, because Pro weights later
instructions more heavily when they conflict with earlier description.

    python3 .workspace/refine_batch.py --only h02,h03,h04,h08,h09,h10
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, ".workspace"))
from run_gemini_batch import HALOVEN, REFDIR, GEN, PRODUCT  # noqa: E402
from peach_led import GROUND, NEUTRALIZE  # noqa: E402

PROMPT_DIR = os.path.join(ROOT, ".workspace/haloven_prompts")

# Placeholder wording that produces a paste-able zone: correct aspect, sitting in the
# scene's perspective, gripped by real fingers, and casting nothing of its own.
def placeholder(seating):
    return f"""

PRODUCT PLACEHOLDER — THIS OVERRIDES EVERY OTHER INSTRUCTION ABOUT THE PRODUCT.
Do NOT draw the product tube, its label, its wordmark, its badge or its brush tip.
Wherever the product should appear, paint a SOLID FLAT PURE MAGENTA shape instead
(maximum red, zero green, maximum blue).

SHAPE: upright, taller than wide, in the proportion 4 wide by 5 tall.

SEATING: {seating}

FLATNESS: the magenta is completely flat — no gradient, no shading, no highlight, no
reflection in any glossy surface, no drop shadow and no contact shadow. Nearby
surfaces keep their own natural color and reflect nothing. Its edges are hard.

OCCLUSION — IMPORTANT: anything that would realistically pass IN FRONT of the product
must still be drawn in front of it, over the magenta. Fingers gripping it wrap around
its edges and are drawn fully, in natural skin tone, on top of the magenta shape.
Draw those fingers completely and realistically; they are not magenta.

This magenta shape must be the only magenta anywhere in the image. Nothing else in
the frame may be magenta, pink, purple or violet.
"""


REFINE = {
    # ── h02: product read as pasted; it floated off the tray with no shadow ──────
    "h02_whiteboard": ("""

PRODUCT PLACEMENT — the tube must look genuinely photographed in this room, not added
afterwards. It stands UPRIGHT ON the whiteboard's aluminium pen tray, its base fully
resting on the tray shelf and NOT hanging below it or floating in front of the board.
It sits in the same perspective as the tray, which recedes slightly to the right, and
it is lit by the same soft daylight coming from the window at the left — brighter down
its left edge, softly shadowed down its right.

Also make sure the small handwritten line "hides it until you wash" is fully visible
and NOT covered or crowded by her hand or arm. Her gesturing hand stays clear of all
handwriting.

THE RED X MARKS — CRITICAL. There are THREE separate red X marks, one for each item,
each drawn immediately to the LEFT of its own line: one X beside "Dry shampoo", one X
beside "Volume powder", one X beside "Root spray". Each X is small, roughly the height
of the handwriting next to it. Do NOT draw one large X across the group, do NOT draw a
single X spanning several lines, and do NOT strike the items through. Three small,
separate, individual X marks.
""", "the magenta shape stands upright on the whiteboard's pen tray, its base fully "
     "resting on the tray, in the tray's perspective. It does not float and does not "
     "extend below the tray."),

    # ── h03: eight comparison items were blank white placeholder labels ──────────
    "h03_test_grid": ("""

THIS IS A GRID OF NINE REAL PHOTOGRAPHS. Compare against how a real product-test ad
looks: a hand holding one object against a plain wall, shot nine times.

NO PERSON, NO FACE — AND THIS CONTRADICTS THE REFERENCE IMAGE ON PURPOSE. The reference
(image 1) shows a woman's face behind the product in every cell. DO NOT REPRODUCE THAT.
Ignore the face in the reference completely; take only its grid geometry and badge
placement.

Each cell shows ONLY a hand and forearm holding the product against a plain, softly-lit
neutral wall. There is NO face, NO head, NO hair, NO shoulder, NO neck and NO body in
any cell — nothing but a hand, a forearm, the product and the wall behind them. If a
face appears anywhere in this image the result is a total failure.

THE EIGHT COMPARISON PRODUCTS — these must look like eight things a real person actually
bought, which means they DO NOT match each other. Vary the material, the form and above
all the COLOR. Do not render them all in the same cream or beige plastic; that is the
main thing being corrected. Each is a distinctly different object:

- Dry Shampoo: a tall matte AEROSOL CAN, pale blue, metal, with a white plastic cap
- Biotin Gummies: a wide AMBER PLASTIC JAR, white screw lid, orange gummies visible inside
- Volume Powder: a small WHITE SHAKER BOTTLE with a perforated sifter top, dark grey cap
- Scalp Massager: a molded SILICONE SCALP BRUSH, bright teal, soft rubber nubs, no bottle
- Rosemary Oil: a small DARK GREEN GLASS DROPPER BOTTLE, black rubber dropper bulb
- Hair Vitamins: a white opaque SUPPLEMENT BOTTLE, sage green wrap label, white lid
- Thickening Spray: a slim CLEAR PLASTIC PUMP SPRAY, liquid visible inside, black trigger
- Silk Pillowcase: a folded CHARCOAL GREY SATIN pillowcase with a visible sheen and fold

Materials must read specifically: metal reflects, glass has depth and a highlight,
clear plastic shows the liquid inside with a meniscus, silicone is matte and soft,
satin has a directional sheen.

LABEL TEXT — EACH CATEGORY NAME APPEARS EXACTLY ONCE IN THE ENTIRE IMAGE. It is
PRINTED ONTO its own product's label, in small dark product typography, wrapping the
container and following its curve.

Do NOT also write it as a caption. There are NO caption strips, NO text rows, NO labels
above, below, beside or between the cells, and no repeated words anywhere. The previous
attempt printed "Thickening Spray" and "Silk Pillowcase" twice each — once on the
product and again as a caption — which is a duplication failure.

The ONLY text in this image is: the headline at the very top, one category name printed
on each of the eight products, the nine score badges, and the one short caption beneath
the ninth cell. Nothing else.

For the Scalp Massager and the Silk Pillowcase, which have no bottle to print on, place
the name on a small printed hang-tag or care-label attached to the object itself — still
part of the object, never a caption. No label may be blank.

Each label carries ONLY its category name from the list above. Invent NO brand names,
NO logos, NO slogans, NO other words.

Let each cell's wall vary very slightly in tone and shadow, as separate photographs
taken on different days would.

SCORE BADGES — every cell carries a small round WHITE badge with a thin dark outline in
its lower-right corner, containing a score in ordinary dark type. The eight scores read
exactly, one per cell in this order: "3/10", "4/10", "3/10", "5/10", "5/10", "4/10",
"3/10", "4/10". The ninth cell's badge reads exactly "9.4/10".

There are NO cross marks, NO X marks and NO check marks anywhere. The badges contain
only the score text.

THE NINTH CELL is the winner: outlined with a thick brand-orange border and washed with
a soft peach tint. It contains NO product, NO hand, NO forearm and NO object of any
kind — it is the plain tinted wall alone, completely empty, with its score badge in the
lower-right corner and the short caption beneath the grid. That empty space is reserved.

Do not sketch, outline or suggest a hand there. The previous attempt drew a cartoon
outline of a hand in this cell; the cell must be genuinely empty.
""", ""),

    # ── h04: middle-panel product didn't match the room; pink slab on the counter ─
    "h04_timestamp": ("""

MIDDLE PANEL PRODUCT PLACEMENT — this panel is the hero beat and the product must look
genuinely photographed on that counter, not added afterwards. The tube stands UPRIGHT
DIRECTLY ON the bathroom counter surface, its base in contact with the stone, in the
counter's perspective — the counter recedes to the right, so the tube sits in that same
space rather than facing the camera flat-on. It is lit by the same soft window daylight
as the faucet and the basin, brighter down one edge with gentle falloff on the other,
and it has the same shallow depth of field as the rest of the panel.

The counter is a matte surface. It shows NO colored reflection of the product and no
colored patch of any kind beneath or around it.
""", "the magenta shape stands upright directly on the bathroom counter, its base in "
     "contact with the surface, in the counter's perspective. The counter is matte and "
     "shows no reflection of it whatsoever."),

    # ── h08: the callout arrows pointed at the wrong parts of the product ────────
    "h08_marker": ("""

ANNOTATION ANCHORING — CRITICAL. Each hand-drawn arrow must physically touch and point
directly AT the exact part of the product it describes. Getting this wrong is the main
defect being corrected.

- "brush tip, not greasy fingers" sits at the LEFT of the frame. Its arrow curves from
  that text DOWN and RIGHT and its head lands precisely ON the comb/brush applicator
  teeth at the very BOTTOM of the tube — on the bristles themselves, not below them,
  not beside them, and not on empty background.
- "works while your hair dries" sits at the RIGHT of the frame. Its arrow curves from
  that text LEFT and its head lands precisely ON THE MIDDLE OF THE TUBE'S BODY, on the
  white label area — not on the cap, not on the applicator, not on empty background.
- The hand-drawn marker circle is drawn AROUND the applicator teeth at the bottom of
  the tube, enclosing them cleanly, and it does not overlap the arrowheads.

Every arrowhead must terminate on the product itself. No arrow may end in empty space.
""", "the magenta shape stands centered in the frame, upright, straight-on, filling "
     "the middle of the composition."),

    # ── h09: product too small and floating ─────────────────────────────────────
    "h09_time_promise": ("""

PRODUCT SIZE AND PLACEMENT — the product was previously far too small and looked
parked in the corner. It must now read as a proper hero element: LARGE, occupying a
substantial part of the lower-left quadrant, big enough that its label is comfortably
readable. It is anchored into the composition rather than floating — its base sits on
an implied surface with a soft contact shadow beneath it, and it slightly overlaps the
lower edge of the bottom benefit chip so it belongs to the layout instead of hovering
in empty space. It is lit from the same soft direction as her face.

Everything else in this ad stays exactly as described above — the headline, the small
line beneath it, all five benefit chips, the oval badge, her portrait and the peach
ground are all unchanged.
""", "the magenta shape is LARGE and stands in the lower-left quadrant, upright, its "
     "base resting on an implied surface, slightly overlapping the bottom benefit "
     "chip. It should be big enough to be a hero element, not a small inset."),

    # ── h10: subject and product both read as AI ────────────────────────────────
    "h10_selfie_checklist": ("""

PHOTOGRAPHIC REALISM — CRITICAL, THIS IS THE MAIN THING BEING FIXED. The previous
version read as an AI portrait: too smooth, too symmetrical, too evenly lit, expression
blank. This must look like an actual photograph taken of an actual person.

Shoot it like a real photograph with real imperfections:
- Skin is genuinely textured and uneven — visible pores, a little redness around the
  nose and cheeks, faint under-eye shadow, a blemish or two, fine lines at the eyes
  when she smiles. Absolutely no retouching, no smoothing, no glow, no even-toned
  complexion.
- Her face is ASYMMETRIC, as real faces are, and she is NOT perfectly centered on the
  lens axis — turned very slightly off-square to the camera.
- Expression is a real, half-caught in-between moment — a small tired, genuine smile
  rather than a held pose or a blank neutral stare. She looks like a person who has
  been up since 5am with a baby.
- Hair is not uniform: stray flyaways catching the window light, a few strands out of
  place, natural uneven parting.
- Lighting is directional and UNEVEN — strong soft daylight from the window at the
  left, the right side of her face falling into gentle shadow. Not beauty lighting, not
  flat fill. Allow slight underexposure in the shadows.
- Shot on a 35mm lens at f/2 on a full-frame camera: shallow but not extreme depth of
  field, the room behind her genuinely soft, faint sensor grain across the frame, very
  slight chromatic aberration at the window edge.
- Her cream sweater has real knit texture, natural creases and a little pilling.

The room behind her stays a real, specific, lived-in nursery — actual identifiable
objects, not vague AI shapes.
""", "the magenta shape is held at chest height in BOTH of her hands, at the natural "
     "size of a 100 ml tube — about the length of her hand, no larger. Her fingers "
     "wrap around its sides and are drawn completely and realistically ON TOP of the "
     "magenta, so the grip is clearly visible."),
}


# Ads where the placeholder approach fails. Whenever the prompt puts the product in
# someone's hands, Pro renders the magenta as a large flat SIGN being held up — on h10
# it drew a 2.5:1 landscape rectangle spanning her chest, on h09 it invented hands that
# were never in the design. Inpainting a block that size leaves a smear no threshold can
# rescue. For these, no product is drawn at all: the scene is generated with clear space
# and the real tube is composited into it, so there is nothing to remove and no residue.
NO_PRODUCT = {
    "h03_test_grid": """

PRODUCT — DO NOT DRAW IT, AND DO NOT DRAW ANY PLACEHOLDER. There is no magenta shape
anywhere in this image. Nothing in any cell is magenta, pink, purple or violet.

The ninth cell (bottom-right) is EMPTY: the plain peach-tinted wall alone, inside its
brand-orange border, with its score badge in the lower-right corner. No product, no
hand, no forearm, no outline and no object of any kind in that cell. That space is
reserved and must stay clear.

The other eight cells each contain their hand and their product exactly as described.
""",
    "h04_timestamp": """

PRODUCT — DO NOT DRAW IT. There is NO product, NO tube, NO bottle and NO container
anywhere in any of the three panels, and no placeholder or stand-in of any kind.

The MIDDLE panel is the empty bathroom counter alone: a clean, uncluttered stretch of
counter beside the basin, lit by soft window daylight, photographed straight across so
the counter surface reads clearly. Leave the LEFT HALF of that counter completely bare
— no soap, no bottle, no cloth, no object and no shadow of an object. That space is
reserved. Keep the small rounded chip in its top-left corner as specified.

The top and bottom panels are unchanged and contain no product either.
""",
    "h09_time_promise": """

PRODUCT — DO NOT DRAW IT. There is NO product, NO tube, NO bottle and NO container
anywhere in this image, and nobody is holding anything. Do not draw a placeholder, a
box, a blank shape or a stand-in of any kind.

Leave the LOWER-LEFT QUADRANT of the frame completely clear and uncluttered — nothing
but the smooth peach background there, no text, no chip, no hand, no object, no shadow.
That space is reserved. Her hands and arms stay out of frame entirely; she is shown from
the shoulders up only.

Everything else stays exactly as described: the headline, the small line beneath it, all
five benefit chips down the left, the oval trust badge at the bottom, her portrait at
the right, and the peach ground.
""",
    "h10_selfie_checklist": """

PRODUCT — DO NOT DRAW IT. There is NO product, NO tube and NO container anywhere in
this image, and she is NOT holding anything. Do not draw a placeholder, a sign, a card,
a box or a blank shape of any kind — she is not holding up an object.

Instead she stands relaxed and natural with her arms at her sides, hands loosely at hip
level, facing the camera. Keep the chest and lower-centre of the frame clear of clutter.

Everything else stays exactly as described: the quote, the attribution, the bottom trust
line, the peach nursery, and above all the photographic realism direction.
""",
}


def build(pf):
    with open(os.path.join(PROMPT_DIR, f"{pf}.txt")) as f:
        text = f.read().rstrip()
    for old, new in NEUTRALIZE.get(pf, []):
        text = text.replace(old, new)
    if pf in GROUND:
        text += GROUND[pf]
    refine, seating = REFINE[pf]
    text += refine
    if pf in NO_PRODUCT:
        text += NO_PRODUCT[pf]
    else:
        text += placeholder(seating)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="h02,h03,h04,h08,h09,h10")
    ap.add_argument("--out", default=os.path.join(ROOT, "out_gemini/v2_layouts"))
    ap.add_argument("--retries", type=int, default=2)
    a = ap.parse_args()

    want = {x.strip() for x in a.only.split(",") if x.strip()}
    os.makedirs(a.out, exist_ok=True)
    tmp = os.path.join(a.out, "_prompts")
    os.makedirs(tmp, exist_ok=True)

    ok, failed = [], []
    for num, pf, ref, ratio in HALOVEN:
        if num not in want or pf not in REFINE:
            continue
        ppath = os.path.join(tmp, f"{num}.txt")
        with open(ppath, "w") as f:
            f.write(build(pf))
        out_path = os.path.join(a.out, f"{num}_{pf}.png")
        cmd = [sys.executable, GEN,
               "--reference", os.path.join(REFDIR, ref),
               "--product", PRODUCT,
               "--prompt-file", ppath,
               "--aspect-ratio", ratio,
               "--out", out_path]
        for attempt in range(1, a.retries + 1):
            print(f"{num} {pf} ({ratio})  attempt {attempt}/{a.retries} ...")
            if subprocess.call(cmd) == 0:
                ok.append(num)
                break
        else:
            failed.append(num)

    print(f"\ngenerated: {', '.join(ok) or 'none'}")
    if failed:
        print(f"failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
