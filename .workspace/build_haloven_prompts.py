#!/usr/bin/env python3
"""Rebuild the 12 competitor-structure prompts for Nano Banana Pro.

Differences from the Higgsfield-era prompts (kept in .workspace/haloven_prompts_higgsfield/):

1. No hex code ever appears in the layout body. The old prompts wrote things like
   "a thick #C14201 border" in the instructions while the footer told the model never
   to render a hex code. Handing the model a '#' string next to a layout instruction is
   how the codes leaked into an earlier run as visible text. Colors are now named in
   words everywhere except the one painting-instruction block at the end.
2. Each prompt carries an ATMOSPHERE block derived from actually looking at its
   reference: light, texture, environment, camera feel, type treatment.
3. The magenta-placeholder line is gone from h02 (that was the Higgsfield composite
   path; Pro renders the supplied product directly).
4. Claims conform to the settled trust rules: no lab or clinical claim, no guarantee
   term, no review counts.

Run:  python3 .workspace/build_haloven_prompts.py
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "haloven_prompts")

PRODUCT = (
    "The product is the LAVENTRA GROW:TURN AMPOULE: a white squeeze tube with a "
    "built-in white comb/brush applicator tip at the bottom. Its label has an orange "
    "serif \"LAVENTRA\" wordmark, black \"GROW:TURN AMPOULE\", an orange pill badge, and "
    "\"100 ml / 3.38 fl. oz.\" Reproduce the supplied product photo faithfully — same "
    "proportions, same label layout, same wording. Do not redesign the label, do not "
    "invent extra label text, do not change the wordmark."
)

# The only place color codes are allowed to appear, framed unambiguously as pigment.
PALETTE = (
    "COLOR PALETTE — CRITICAL: the codes below tell you WHICH COLORS TO PAINT WITH. "
    "They are instructions to you, not content. NEVER draw, print, write, letter, or "
    "display any hex code, any '#' symbol, or any color name anywhere in the image — an "
    "image containing a code like E8B093 as visible text is a total failure. Paint with "
    "these colors: primary peach/terracotta (hex E8B093), brand orange (hex C14201), "
    "badge orange (hex B95618), text near-black (hex 000000), product white (hex F5F5F6), "
    "background white (hex FFFFFF)."
)

TEXT_RULES = (
    "US English spelling. Every quoted string must be spelled EXACTLY as written, letter "
    "for letter, and appear exactly ONCE. Render no other text anywhere — no extra "
    "wordmarks, no page numbers, no URLs, no hex codes, no ghost or duplicated lines, no "
    "half-formed or blurred second copy of any line. Type must be cleanly kerned and fully "
    "legible at every size."
)

REF_RULES = (
    "The reference image (image 1) is a screenshot from an ad library: it may include "
    "browser chrome, a social feed header, an advertiser name, a caption, a link preview "
    "and a call-to-action button. Reproduce NONE of that furniture — recreate only the ad "
    "creative itself, filling the whole frame. The reference advertises a DIFFERENT product "
    "in a different category; take from it only layout geometry, lighting, mood and type "
    "treatment. Never copy its words, its brand names, its logos, its badges or its product."
)


def tail(strict=""):
    parts = [PALETTE, TEXT_RULES, REF_RULES]
    if strict:
        parts.append("STRICT CONTENT RULES: " + strict)
    return "\n\n".join(parts)


ADS = {}

# ─────────────────────────────────────────────────────────────────────────────
# h01 — ref-40-oversized-quote-lead
# Reference: near-black frame, warm ember glow low in the scene, dramatic rim light
# on a centered product, atmospheric haze, oversized quote with ONE emphasized line.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h01_quote_hero"] = f"""Recreate the attached reference ad (image 1) as a layout template: an oversized customer quote fills the top half, with the product standing below it, dramatically lit against a deep saturated background.

ATMOSPHERE: cinematic and premium, high contrast, the mood of a late-evening photograph. The frame is almost black at the edges and warms toward the center, where a soft terracotta glow rises from below and behind the product like low firelight — warm peach light, never literal flames. Faint atmospheric haze softens the background. The product catches a bright specular rim highlight down one edge and sits on a barely-visible reflective surface. Deep shadow everywhere else. Nothing decorative, nothing cluttered — the drama comes entirely from light.

TYPE TREATMENT: the quote is enormous, set in a warm off-white serif, tightly leaded so the lines nearly touch, centered across the top. The middle line is set in the peach/terracotta accent color while the other two lines stay off-white — this single color shift is the only emphasis in the layout.

Giant serif quote across the top, on exactly three lines, reading exactly: "In 3 weeks I stopped" then "checking the drain" then "every morning."
Set the middle line, "checking the drain", in peach/terracotta; the other two lines off-white.

Small attribution line beneath the quote in letter-spaced caps, exactly: "VERIFIED CUSTOMER  ★★★★★  4.8 RATED"

{PRODUCT} Product standing centered in the lower half, lit as described above.

{tail("the image contains ONLY the three quote lines, the one attribution line, and the product. No headline, no logo, no button, no price, no extra badge, no caption.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h02 — ref-38-expert-whiteboard-checklist
# Reference: bright daylit room, real whiteboard filling most of frame, presenter at
# right gesturing, uneven handwriting, red X / green check, red circle + "ours!" note,
# markers resting on the tray. Slightly amateur phone-camera authenticity.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h02_whiteboard"] = f"""Recreate the attached reference ad (image 1) as a layout template: a real photograph of a woman standing beside a large whiteboard, gesturing at a hand-written two-column comparison she has drawn on it.

ATMOSPHERE: a real room, not a studio set — bright flat daylight from a window out of frame, plain walls, the faint sheen and ghosting of a whiteboard that has been wiped many times. The photograph looks like it was taken on a phone by a colleague: straight-on, slightly imperfect framing, no professional lighting rig, no bokeh. The whiteboard fills most of the frame and the woman stands at the right edge, turned toward the board, one hand open toward the column she is making her point about. The handwriting is genuinely hand-made — uneven baselines, varying letter sizes, the honest look of someone writing fast on a vertical surface. A couple of dry-erase markers and an eraser rest on the pen tray.

Realism protocol ON: a plainly-dressed woman aged 34, minimal makeup, hair tied back, a simple solid-color top. Natural skin texture with real pores, real daylight falloff, absolutely no beauty-filter smoothing, no airbrushing, no glamour lighting.

Hand-written on the whiteboard in black marker, a title across the top on exactly two lines, line one exactly: "MASKING vs. FIXING" and line two exactly: "POSTPARTUM SHEDDING". Write "vs." between MASKING and FIXING on the SAME line.

Below the title, two columns divided by a single vertical marker line.
Left column header exactly: "MASKS IT"
Left column items, each with a hand-drawn red X to its left, exactly: "Dry shampoo", "Volume powder", "Root spray"
Beneath them a smaller hand-written line exactly: "hides it until you wash"
Right column header exactly: "FIXES IT"
Right column item with a hand-drawn green check to its left, exactly: "Scalp serum"
Beneath it a smaller hand-written line exactly: "works at the root, not the strands"

Draw a loose red hand-drawn circle around the right column, in the same marker style as the reference.

{PRODUCT} The tube rests on the whiteboard's pen tray at the bottom of the board, in the photograph, as a real object.

{tail("the whiteboard contains ONLY the two title lines, the two column headers, the three left items with their red X marks, the one small left caption, the one right item with its green check, the one small right caption, and the red circle around the right column — nothing else. Every line appears EXACTLY ONCE: never repeat 'Dry shampoo', never write a word twice, never add a fourth left item. No scribbles, no extra annotations, no additional products anywhere in the room, nothing held in her hand.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h03 — ref-04-ranked-test-grid
# Reference: 3x3 grid, soft even light, plain warm-neutral wall, each cell a hand
# holding one item at matched scale/angle, holder's face soft behind, small dark
# rounded score badge lower-left of each cell. Dispassionate editorial listicle.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h03_test_grid"] = f"""Recreate the attached reference ad (image 1) as a layout template: a clean 3x3 grid of nine photo cells, each cell a hand holding one product toward the camera, with a small badge pinned in the corner of every cell.

ATMOSPHERE: dispassionate editorial product-test photography, like a magazine round-up. Soft, even, shadowless light across all nine cells; a plain warm-neutral wall behind every hand; identical camera distance, identical hand position, identical product scale in each cell so the grid reads as one controlled test rather than nine stock photos. In each cell the same woman's face is visible but softly out of focus behind the product she is holding — present, not the subject. Thin white gutters separate the cells. Calm, clinical, evidence-like. No lifestyle styling, no props, no color grading tricks.

Bold black headline across the very top, exactly: "WE TRIED 9 POSTPARTUM HAIR FIXES FOR 30 DAYS"

Eight cells hold GENERIC unbranded products with plain white labels — no brand names, no logos, no readable text beyond the one label word given here. Their plain labels read exactly, one per cell: "Dry Shampoo", "Biotin Gummies", "Volume Powder", "Scalp Massager", "Rosemary Oil", "Hair Vitamins", "Thickening Spray", "Silk Pillowcase". Each of these eight cells carries a small round white badge in its lower-left corner with a hand-drawn grey X inside.

The ninth cell, bottom-right, is outlined with a thick brand-orange border and washed with a soft peach tint so it reads as the winner at a glance. It holds the product. {PRODUCT} Its badge is a filled brand-orange circle in the lower-left corner with a white check mark inside.

Directly beneath the ninth cell, a short label exactly: "The only one that treats the scalp"

{tail("exactly nine cells, three across and three down. Each of the eight generic labels appears exactly ONCE and only inside its own cell. No brand names, no logos, no score numbers, no extra captions, no text of any kind inside the cells beyond the eight plain labels named above.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h04 — ref-30-problem-fix-result
# Reference: three panels, same subject locked. Cold blue night → neutral daylight
# product → bright warm daylight resolution. Colored corner tag chips. Documentary.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h04_timestamp"] = f"""Recreate the attached reference ad (image 1) as a layout template: three stacked horizontal panels telling a before / product / after story, each with a small rounded time-stamp chip in its top-left corner, and a solid claim bar across the very bottom.

ATMOSPHERE: documentary, like three real photos pulled from the same phone. The light tells the story and carries the whole arc. Panel one is cold and dim — early-morning bathroom, blue-grey cast, overhead light not yet on, the flat unflattering light of 7am. Panel two is neutral and clean — the same bathroom counter, daylight, a plain product photograph with nothing staged around it. Panel three is warm and bright — the same bathroom with real daylight coming in, warmer skin tones, open and calm. No filters, no grading beyond what the room's own light would do.

Realism protocol ON: natural skin, real hair with flyaways, real bathroom lighting, absolutely no beauty-filter smoothing. LOCK the same woman's identity across the top and bottom panels — same face, same age, same hair color and length, same bathroom, same camera angle and distance. She is aged 32.

Top panel: she looks down at a hairbrush full of loose hair, worried, shoulders down. A small red rounded chip in the top-left corner reads exactly: "7:12 AM"

Middle panel: a clean product shot on the bathroom counter. A small brand-orange rounded chip reads exactly: "THE SWITCH". {PRODUCT}

Bottom panel: the SAME woman, same bathroom, now relaxed and smiling faintly, running her fingers through her hair. A small brand-orange chip reads exactly: "7:12 AM — FOUR WEEKS LATER"

Solid brand-orange bar across the very bottom with white caps text, exactly: "TWO MINUTES AFTER EVERY WASH  ·  FREE SHIPPING  ·  EASY RETURNS"

{tail("exactly three panels and exactly three chips, one chip per panel. The bottom bar contains only the one line specified. No other text in any panel, no watermarks, no timestamps burned anywhere else, no logos.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h05 — ref-46-story-ama-frame
# Reference: authentic first-person UGC in a real outdoor environment, hand entering
# from below holding the product, Instagram-story furniture layered over the photo:
# dark rounded "ask me anything" pill, white rounded question bubble, dark rounded
# caption block of dense small text at the bottom.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h05_comment_reply"] = f"""Recreate the attached reference ad (image 1) as a layout template: a vertical social-media story screenshot — a real first-person photograph with story-interface furniture layered over it.

ATMOSPHERE: unmistakably native and un-designed, like a story posted by a real person rather than a brand. Handheld phone camera, slightly off-center framing, real soft daylight, real surface texture and clutter at the edges. The woman's own hand enters from the bottom of the frame holding the product up toward the camera, close enough that you can see her skin texture and a little motion softness. Nothing about the photograph looks art-directed. The overlay furniture sits on top of the photo with soft drop shadows, exactly as a story interface would render it.

Realism ON for the hand and skin: real texture, visible knuckle creases, natural nails, no smoothing.

Environment: a real bathroom counter in soft daylight. Beside her, slightly out of focus, sit a GENERIC unbranded dry shampoo can and a GENERIC unbranded gummy vitamin jar — plain white labels, no brand names, no logos, no readable text on them at all.

At the top, a white rounded comment card with a small round profile photo at its left. Bold dark text in the card exactly: "but doesn't postpartum shedding stop on its own??" and beneath it in small grey text exactly: "Replying to @jessica_marie87"

{PRODUCT}

Three white rounded caption bubbles stacked over the lower half, dark text, reading exactly:
"I DID. I took the gummies, used the dry shampoo, wore the bun... and still lost handfuls in the shower"
"Then I started brushing this into my scalp after every wash"
"Now I'm not hiding my part with powder — I actually look forward to washing my hair"

{tail("exactly one comment card at the top and exactly three caption bubbles below. Each bubble contains only its one specified sentence, appearing exactly ONCE, fully legible, with no faded or doubled second copy inside any bubble. No like buttons, no emoji reactions, no send bar, no profile name other than the one specified, no additional interface elements.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h06 — ref-25-lifestyle-first-person-overlay
# Reference: warm domestic morning light, rustic wood, steam, natural textures,
# generous negative space, elegant serif overlay set quietly in the upper area.
# Calm and aspirational rather than loud.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h06_pov_callouts"] = f"""Recreate the attached reference ad (image 1) as a layout template: a first-person point-of-view lifestyle photograph with a quiet headline set into the negative space, small callout labels down one side, and a small trust card at the bottom.

ATMOSPHERE: warm, domestic and calm — the single most important quality of this layout. Low golden morning light rakes in from a window at the side, catching dust in the air and warming every surface it touches. Real textures: a wooden shelf or counter, a folded linen towel, soft shadows with warm edges. The scene is unhurried and lived-in, the visual opposite of a hard-sell ad. Generous empty space in the upper third where the type sits. Shallow depth of field, filmic and slightly soft. Aspirational domestic quiet.

Realism ON: natural light only, real textures, no smoothing, no artificial studio fill.

Scene: looking down from the woman's own eye level at her hand holding the product over a bathroom counter in that warm morning light.

TYPE TREATMENT: the headline is set in an elegant off-white serif, generously leaded, placed in the open space at the top — quiet and confident, not bold or shouty.
Headline across the top, exactly two lines: "Fuller hair without" then "the daily cover-up."

{PRODUCT}

Four small dark rounded callout labels down the right side, each with a thin leader line pointing to the product, reading exactly: "Works at the scalp", "Brush tip, no mess", "Two minutes after washing", "No powders or root spray"

Small white trust card at the bottom with five small brand-orange stars and text exactly: "Thousands of new moms making it their daily routine"

{tail("exactly four callout labels and exactly one trust card. Each callout contains only its one specified phrase, appearing exactly ONCE. No fifth callout, no price, no button, no logo, no extra badge.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h07 — ref-47-objection-kill-split
# Reference: loud direct-response retail. Flat bright ground, huge condensed black
# headline upper-left with one line in an accent color, product large at right with
# hard product lighting, icon+text rows down the left, solid bottom bar.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h07_dont_try"] = f"""Recreate the attached reference ad (image 1) as a layout template: an enormous reverse-psychology headline stacked at the upper left, benefit rows beneath it, the product standing large at the right, and a solid bar across the bottom.

ATMOSPHERE: loud, flat and commercial — a deliberate pattern interrupt. The background is a flat solid peach field with no gradient, no texture and no photographic depth, so the type and the product read instantly at thumbnail size. The product is lit like a retail product shot: bright, crisp, hard-edged, with a tight contact shadow directly beneath it and a clean specular highlight down one side. Maximum contrast, maximum legibility, zero softness. This ad is designed to stop a scroll, not to be beautiful.

TYPE TREATMENT: the headline is a heavy condensed sans in near-black, set very large and tight, filling the upper-left corner edge to edge. The second line is set in brand orange while the first stays near-black.

Enormous headline stacked at the upper left, exactly two lines: "DON'T TRY THIS" then "IF YOU LIKE DRY SHAMPOO"
Set the first line near-black and the second line brand orange.

Beneath it in smaller near-black text, exactly: "It works at the scalp, so you stop covering the problem up."

Three benefit rows down the left beneath that text, each with a simple brand-orange line icon at its left, reading exactly: "Brush tip reaches the root", "Two minutes after every wash", "No powder, no root spray"

{PRODUCT} The tube stands large at the right side of frame, lit as described above.

Solid brand-orange bar across the very bottom with white caps text, exactly: "FREE SHIPPING  ·  EASY RETURNS  ·  4.8★ RATED"

{tail("exactly two headline lines, one sub-line, three benefit rows and one bottom bar. Each line appears exactly ONCE. No discount badge, no percentage, no price, no starburst, no fourth benefit row.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h08 — ref-32-hand-drawn-marker-annotation
# Reference: flat saturated ground filling frame, product straight-on center,
# scrappy hand-drawn marker scrawl in black and red — arrows, a circle, an
# underline. Deliberately un-designed, loud, hand-made.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h08_marker"] = f"""Recreate the attached reference ad (image 1) as a layout template: the product photographed dead-center on a flat saturated background, with casual hand-drawn marker annotations, arrows and a circle scrawled around it.

ATMOSPHERE: deliberately scrappy and un-designed — it should look like someone printed a product photo and attacked it with markers. The background is a completely flat, saturated peach field edge to edge, no gradient and no texture. The product is photographed straight on, evenly lit, catalog-plain, so the scrawl on top is the only energy in the frame. The annotations are genuinely hand-made: uneven baselines, wobbling arrow shafts, a circle that does not quite close, varying pressure in the stroke, the occasional overshoot. Nothing is aligned to a grid. Loud, immediate, obviously human.

TYPE TREATMENT: every word in this ad is hand-written marker lettering, never a typeface. The headline is thick black marker caps across the top; the bottom line is written in brand orange with a hand-drawn underline scratched beneath it.

Hand-written marker headline across the top in black caps, exactly: "THE LAST HAIR PRODUCT YOU'LL BUY"

{PRODUCT} The tube centered, photographed straight on.

A hand-drawn black marker circle around the brush tip at the bottom of the tube, with a hand-drawn arrow pointing to it and hand-written text beside it exactly: "brush tip, not greasy fingers"

A second hand-drawn arrow pointing at the middle of the tube with hand-written text exactly: "works while your hair dries"

At the bottom, hand-written in brand orange with a hand-drawn underline beneath it, exactly: "cheaper than your dry shampoo habit"

{tail("exactly one headline, two annotations with one arrow each, and one underlined bottom line. Each appears exactly ONCE. No price, no percentage, no discount badge, no starburst, no additional scribbles or stray words.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h09 — ref-50-benefit-checklist-portrait
# Reference: clean bright catalog. Soft warm ground, rounded pill chips with check
# icons stacked upper-left, subject portrait at right, product lower-left, oval
# badge bottom. Calm premium retail — no shouting.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h09_time_promise"] = f"""Recreate the attached reference ad (image 1) as a layout template: a headline across the top, rounded benefit chips stacked down the left, a portrait at the right, the product at the lower left, and a small oval trust badge at the bottom.

ATMOSPHERE: clean, bright and premium — the calm confidence of a good catalog page. Soft warm peach background with a gentle vignette, even diffused light, no hard shadows anywhere. The portrait is warmly lit and relaxed, shot against the same soft ground so the subject and the chips feel like one composed page rather than a cut-out pasted on. The product sits at the lower left with a soft contact shadow. Everything is generously spaced and quietly ordered. Restrained, reassuring, adult.

Realism protocol ON: a woman aged 31, a new mother, smooth youthful face with NO wrinkles, NO crow's feet and NO gray hair, natural healthy brown hair worn down, gentle closed-mouth smile, minimal makeup. Natural skin texture with visible pores, absolutely no beauty-filter smoothing.

TYPE TREATMENT: the headline is a clean bold sans in near-black. The chips are white rounded pills with a soft shadow, each opening with a small filled brand-orange circle holding a white check.

Bold headline at the top, exactly two lines: "LESS SHEDDING TO SWEEP UP" then "IN YOUR SHOWER."

Small line directly beneath it, exactly: "Individual results vary."

Five white rounded benefit chips stacked down the left, each with a brand-orange check circle at its left, reading exactly: "Works at the scalp", "Brush tip, no mess", "Two minutes after washing", "No powders or root spray", "Made for postpartum shedding"

{PRODUCT} The tube sits at the lower left beneath the chips.

Small white oval badge at the bottom with a near-black outline and text exactly: "4.8★ RATED  ·  FREE SHIPPING  ·  EASY RETURNS"

{tail("EXACTLY FIVE benefit chips, no more and no fewer. Each chip contains one short phrase only, appearing exactly ONCE, fully legible with no faded, ghosted, doubled or half-formed second line inside any chip. No sixth chip, no percentage, no price, no discount badge, no guarantee wording.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h10 — ref-19-portrait-quote-attribution
# Reference: cinematic environmental portrait, real room with depth, warm natural
# light from a door/window, subject center holding the product at chest height,
# serif quote across the top, small letterspaced attribution beneath, thin trust
# line at the very bottom. Filmic and documentary rather than snapshot.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h10_selfie_checklist"] = f"""Recreate the attached reference ad (image 1) as a layout template: an environmental portrait of a woman holding the product at chest height, with a large serif quote across the top, a small attribution line beneath it, and a thin trust line at the very bottom.

ATMOSPHERE: filmic and documentary — a real person photographed in her own home, not a model in a studio. Warm natural light comes from a window or doorway at one side, falling across her face and leaving the depth of the room soft behind her: a hallway, a doorframe, the ordinary domestic clutter of a house with a baby in it, all gently out of focus. Slight film grain, warm midtones, natural falloff into shadow. She looks directly at the camera, calm and unperformed. The quote sits over the darker upper area of the photograph in off-white.

Realism protocol ON: a woman aged 30 — early thirties, a new mother, smooth youthful face with NO wrinkles, NO crow's feet and NO gray hair, long healthy brown hair. Natural skin with visible pores and real texture, real window light, absolutely no beauty-filter smoothing and no glamour retouching.

TYPE TREATMENT: the quote is a large off-white serif with curly quotation marks, set across the top on two lines. The attribution beneath is small, letter-spaced caps. The bottom line is small letter-spaced caps in off-white.

Large serif quote across the top, exactly two lines: "I stopped dreading the shower drain." then "That's the whole review."

Small attribution line directly beneath the quote in letter-spaced caps, exactly: "★★★★★  VERIFIED CUSTOMER  ·  4.8 RATED"

{PRODUCT} She holds the tube at chest height, turned so the label faces the camera, both hands relaxed.

Thin line of small letter-spaced caps across the very bottom, exactly: "FREE SHIPPING  ·  EASY RETURNS  ·  THOUSANDS OF NEW MOMS"

{tail("the image contains ONLY the two quote lines, the one attribution line and the one bottom line. Each appears exactly ONCE. No checklist chips, no badges, no logo, no button, no caption block. The woman must look about 30 years old — a young mother, not a middle-aged woman.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h11 — ref-02-claim-stat-strip
# Reference is a LIGHT layout: warm off-white ground, big condensed headline top,
# small subline, centered product in a soft panel, three-column stat strip with
# icons at the bottom, tiny wordmark. Calm, premium, engineered.
# The delivered creative is a dark hero; that is kept, but the reference's
# compositional discipline (centered product, stat strip, restraint) is adopted.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h11_dark_hero"] = f"""Recreate the attached reference ad (image 1) as a layout template: a bold two-line thesis headline across the top, a small line beneath it, the product centered in the middle of the frame, and a row of stat columns divided by thin vertical rules across the lower area.

ATMOSPHERE: premium, restrained and engineered — the calm authority of a well-made product page. Follow the reference's composition and restraint exactly, but invert its tone: where the reference sits on warm off-white, this sits on a deep rich charcoal, almost black, filling the frame. A single soft pool of light falls on the centered product, which is lit dramatically with a bright specular rim down one edge and a soft gradient falloff into darkness at the corners. Everything is symmetrical and generously spaced. No texture, no props, no background detail whatsoever — the product alone in the dark, and type. Confident and quiet, not loud.

TYPE TREATMENT: the headline is a heavy condensed sans in white caps, tightly set, centered across the top. The stat columns beneath use a small white line icon above a short bold label, separated by thin vertical hairlines, exactly as the reference arranges its bottom strip.

Enormous white headline across the top, exactly two lines: "YOUR HAIR ISN'T THE" then "PROBLEM. YOUR SCALP IS."

Small white line directly beneath it, exactly: "That's where we put it."

{PRODUCT} Product centered, dramatically lit against the dark background.

A row of three stat columns across the lower area, separated by thin vertical hairlines, each with a small white line icon above a short white label. The three labels read exactly: "WORKS AT THE ROOT", "BRUSH APPLICATOR", "TWO MINUTES A DAY"

Thin white line of small text at the very bottom, exactly: "4.8★ rated  ·  Free shipping  ·  Easy returns"

{tail("exactly three stat columns, no more. Each label appears exactly ONCE. No percentages, no invented statistics, no ingredient claims, no laboratory or testing claims, no logo other than the product's own label, no button, no price.")}"""

# ─────────────────────────────────────────────────────────────────────────────
# h12 — ref-06-authority-private-notes
# Reference: aged notebook page, spiral binding at the left edge, sepia/parchment
# tones, fine ink illustration, serif display headline, numbered list with check
# marks, hand-drawn underlines, small icon rows. Scholarly and archival.
# The delivered creative is a pinned poster; kept, with the reference's paper
# texture, ink linework and serif discipline applied.
# ─────────────────────────────────────────────────────────────────────────────
ADS["h12_poster"] = f"""Recreate the attached reference ad (image 1) as a layout template: a printed sheet held by a black binder clip at the top, on textured paper, with a serif headline, the product centered, hand-drawn annotations curving out to short labels, and a solid footer bar.

ATMOSPHERE: archival and scholarly — the reference's central quality, and the reason it does not read as advertising. Warm off-white paper with real fiber texture, a faint aged tone toward the edges, and the soft shadow of a sheet that is physically pinned to a wall. Every drawn element looks like fine ink on paper: thin confident pen strokes, hand-ruled underlines, slightly irregular hand-lettering. The lighting is flat and even, as if the page were photographed straight on in daylight. Nothing glossy, nothing digital, no drop shadows on the type. It should feel like a page from a well-kept notebook rather than a poster from a brand.

TYPE TREATMENT: the headline is a classic serif with a hand-ruled ink underline beneath it. The five labels are hand-lettered in ink, small and neat.

Serif headline across the top with a hand-drawn ink underline beneath it, exactly: "Still finding hair all over the shower?"

Small line beneath the headline, exactly: "Scalp support that goes beyond dry shampoo, powders, and buns."

{PRODUCT} Product centered on the sheet.

Five hand-drawn curving ink arrows pointing outward from the product to five short hand-lettered labels placed around it, reading exactly: "Supports the scalp, not the strands", "Brush tip reaches the root", "Two minutes after washing", "No powders or root spray", "Loved by moms growing it back"

Solid brand-orange footer bar across the bottom with white caps text, exactly: "MAKE IT PART OF YOUR SHOWER"

{tail("exactly five arrows and five labels. Each label appears exactly ONCE. No page numbers, no dates, no signature, no handwriting other than the five labels, no ingredient or laboratory claims, no extra annotations in the margins.")}"""


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, text in sorted(ADS.items()):
        path = os.path.join(OUT, f"{name}.txt")
        with open(path, "w") as f:
            f.write(text.strip() + "\n")
        print(f"wrote {path}  ({len(text)} chars)")
    print(f"\n{len(ADS)} prompts rebuilt.")

    # guardrail: no '#' hex string may survive anywhere in the layout body
    bad = []
    for name, text in ADS.items():
        body = text.split("COLOR PALETTE — CRITICAL")[0]
        if "#" in body:
            bad.append(name)
    if bad:
        raise SystemExit(f"FAIL: '#' found in layout body of: {', '.join(bad)}")
    print("check passed: no '#' character in any layout body.")


if __name__ == "__main__":
    main()
