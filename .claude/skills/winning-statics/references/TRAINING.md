# Winning-Statics — Master Training Document

The full training guide behind this skill. LIBRARY.md is the condensed per-reference catalog;
this document is the deep version — read the relevant section when you need more than the catalog gives:

- **Part 1-3** — what the skill does, setup, and the full workflow (mirrors SKILL.md)
- **Part 4** — the protocols, with fuller reasoning than SKILL.md's summaries
- **Part 5** — the 9 families and all 50 references with extended mechanism notes,
  when-to-use guidance, and recreation advice per reference (deeper than LIBRARY.md)
- **Part 6** — getting the most out of the user's inputs (product photo, site PDF, angle)
- **Part 7** — troubleshooting

A one-line intro to the source document: this guide teaches you to direct the skill
"like a media buyer instead of a passenger."
A complete guide to the Winning-Statics Claude Code skill: how it works, how to set it up, the 50 proven reference statics it is built on, the nine concept families they form, and how to think about each one so you can direct the skill like a media buyer instead of a passenger.


## Part 1 — What This Skill Does

Winning-Statics recreates proven, high-performing static image ads for your product. It does not brainstorm ad concepts from imagination. It takes 50 real winning statics — captured from live ad libraries with their performance receipts — and replicates their structure, hierarchy, and psychology with your product, your brand colors, your copy angle, and your market. The 80/20 of ad creative is not inventing the wheel; it is putting your tire on a wheel that is already rolling. You give it four inputs: a clean product photo, your website address, a full-page PDF snapshot of your site, and the customer angle you want to hit. It asks a few plain questions (how many images, what shape, where you advertise), shows you its plan, and then generates the batch with Google's Nano Banana Pro image model using your own Google API key. Every generation call sends the actual reference image — the model sees the winning ad with its own eyes and rebuilds it around your product, rather than working from a lossy text description. Expect real costs and real minutes: roughly $0.13–0.14 per image on your Google key (about $4 for a 30-image batch), and a large batch takes time to generate and quality-check. The skill tells you this up front because surprise bills kill trust.


## Part 2 — One-Time Setup

The skill folder contains GEMINI_SETUP.md with a click-by-click walkthrough written for someone who has never touched an API. The short version: create a free account at aistudio.google.com, click Get API Key, create a key, enable billing (you only pay for what you generate — set a budget alert), and store the key in an environment variable called GEMINI_API_KEY. Then ask Claude to run the self-test. Five minutes, one time, done. Your key never goes into the chat or into any file — the script reads it from your environment only. Installing the skill: place the winning-statics folder in your Claude Code skills directory (or open the .skill file and choose Save Skill). From then on, just tell Claude something like 'make me 20 statics for my product' and the skill takes over.


## Part 3 — The Workflow, Start to Finish

Step 1, Intake: the skill collects your product image, website, PDF snapshot, avatar/angle, advertising market (US, UK, AUS, CA, other), aspect ratio (1:1, 4:5, or a mix), quantity, and diversity preference. If you don't want to make expert decisions, take the Smart Mix default — it spreads your batch across concept families weighted toward how aware your customer is. If you know exactly what you want ('6 post-it notes, 4 comparisons, 10 before/afters'), say so and it obeys. Step 2, The Plan: before spending your API budget, the skill shows you a table — each planned image, which reference it will be built from, which family it belongs to, and the angle note. Veto anything; it re-plans instantly. Step 3, Generation: each image is generated from the reference static plus your product photo plus precise swap instructions (your colors, your headline, your market's spelling and currency). Text that must appear in the image is specified verbatim in quotes, because that is how Nano Banana Pro renders text most accurately. Step 4, Quality Control: every image is checked before you see it — product label fidelity, text spelling, structural match to the reference, realistic human skin where humans appear, and no leftover wrong-market elements. Failures are regenerated up to twice with corrective instructions, and anything still failing is flagged honestly instead of slipped into the pile. Step 5, Iterate: tell the skill which numbers worked ('3, 7, and 12 performed') and it produces variations of just those — same reference skeleton, adjusted angles, or siblings from the same family. This loop is where real testing programs live.


## Part 4 — The Protocols Working Behind the Scenes

Human realism: whenever a reference involves real human skin, faces, or bodies, the skill injects instructions for natural texture — visible pores, fine lines, imperfect lighting, no beauty-filter smoothing. In before/after formats it also protects the 'before' from being accidentally beautified and locks identity across panels (same face, hair, accessories, angle). If the reference is deliberately illustrated or cartoon, the protocol stands down — realistic skin on a cartoon would be wrong. Localization: mechanical market swaps (spelling, currency, country names, seasonal timing) happen automatically based on your market answer. Regulatory badges and credentials never get invented — if a reference carries a UK pharmacy registration and you sell in the US, the skill asks what real equivalent you hold, and if none, swaps that element for your review score or guarantee. Borrowed authority: a few references lean on press logos or named personalities. The skill replicates their structure but replaces borrowed authority with your real proof or generic trust elements — because a recreated ad wearing someone else's credibility is a liability, not an asset. Testimonial integrity: testimonial-format references are replicated as formats. The quote text comes from your real reviews, or is clearly proposed as placeholder copy for your approval. Platform note: some ad platforms restrict certain formats (like before/afters in some health verticals) — the skill will generate exactly what you ask for and simply attach a one-line heads-up where relevant, never altering your creative on its own.


## Part 5 — The Reference Library: 9 Families, 50 Winners

Everything below is a real static captured from live ad libraries, shown exactly as the skill's references folder stores it. Learn the families and you can direct the skill precisely. Family depth varies — Big-Claim Product Hero is the deepest; Editorial/Advertorial is the thinnest at two references — and the skill is honest about that when you ask for large single-family batches.


## Family 1 — Photographic Before/After

Real-photo transformation splits and timelines. The persuasion mechanism is credibility through unretouched realism: visible texture, real lighting, real people. The imperfection IS the proof. When recreating these, the skill automatically enforces natural skin texture, protects the 'before' state from being beautified, and locks the person's identity across panels. Strongest possible version: drop in your own real customer photos and let the model handle only typography and framing.


### Reference 11 — Day-Stamped Healing Grid

Six dated photos of the same feet, Day 1 through Day 56. Dated photo evidence reads as documentation, not advertising. Use when your product produces visible change over weeks and you can describe (or supply) honest progression.


### Reference 15 — Split-Face Comparison

One face, two halves — 'no cream' vs 'with product' — with a claim bar up top and the product claims strip at bottom. Ranked #1 in a 167-ad account. The realism of the woman's actual skin is why it works; a polished AI face would kill it.


### Reference 30 — Problem → Fix → Result Sequence

Three panels of the same child: struggling sleep, product in place, peaceful result. Parent-fear-to-relief arc. Same-kid consistency across panels is the entire credibility load — the QC step checks it explicitly.


## Family 2 — Illustrated Before/After & Mechanism Diagrams

Drawn or 3D-rendered condition contrasts and how-it-works anatomy. These sidestep every photo-credibility problem because the style is openly illustrative — the viewer's brain files it as education, not evidence. The mechanism is self-diagnosis: 'that is what's happening inside me.' The realism protocol is OFF here; stylization is the point.


### Reference 05 — Illustrated Condition Split

Red inflamed gums vs healthy gums in a friendly drawn style, product pen tucked in the bottom bar. Top 2% of 435 ads, copy reused across 40 others — a workhorse. The cartoon style lets it show a condition that would be repulsive as a photo.


### Reference 01 — Two-Figure Blame Reframe

'You're not fat, your cortisol is storing it' — two illustrated figures, product between them, callout arrows. Reframing blame away from the customer is one of the most reliable supplement mechanisms.


### Reference 10 — Staged Transformation Timeline

Four silhouettes across before / 24 hours / 1 week / 4 weeks with an oversized bottle. Staging makes a big claim feel plausible by breaking it into checkpoints.


### Reference 26 — Timeline Variant

Same brand and skeleton as the previous reference with minor copy differences — kept as a variant example of how one winning layout gets re-angled. The skill will never serve both in the same batch.


### Reference 44 — Elegant Line-Art Progress Map

Week 1 / 4 / 8 facial profiles in refined single-line sketch, product photo inset. Proof that 'before/after' can be done in a premium aesthetic for brands where cartoons feel cheap.


### Reference 45 — Corrective Timeline with Product Payoff

Illustrated feet progressing Week 0 → 4 → 9, insole beneath, guarantee line included. Parental urgency plus a fast-fix promise.


## Family 3 — Annotated Product Callouts

A product hero shot with labeled callout lines pointing to features, ingredients, or mechanisms, usually finished with a trust bar. This is proof-density for the solution-aware shopper who is comparing options. The layout skeleton (callout geometry, trust bar) is what gets preserved; the product, labels, and palette are what get swapped.


### Reference 12 — Formula Callout X-Pattern

Four benefit callouts orbiting a centered bottle, single CTA pill, tri-part trust bar (rating / regulator / guarantee). Note: the regulator badge is UK-specific — the skill asks what real credential YOU hold rather than inventing one.


### Reference 42 — Numbered Reasons-Why Diagram

'5 reasons this belt beat my $90 leather one' with numbered chips pinned to the product. Reasons-why is the oldest direct response play there is, compressed into one image.


### Reference 32 — Hand-Drawn Marker Annotation

Product photo scrawled over with marker arrows, a circle, and a price slash on hazard yellow. The deliberately loud, un-designed look is a pattern interrupt in polished feeds.


## Family 4 — Us-vs-Them Comparison

Two-column tables, side-by-sides, ranked tests, and 'ordinary vs ours' framings. The mechanism is choice architecture: you define the criteria, so your product wins. These target solution-aware and most-aware buyers, swap cleanly across niches, and carry almost no realism risk. One rule the skill enforces: competitor trademarks get genericized on recreation — layout is replicated, other brands' marks are not.


### Reference 41 — Complement Table (With, Not Against)

'What CPAP does / what we add' — positioning WITH the incumbent instead of attacking it. Clever for products adjacent to medical or entrenched solutions the customer will not abandon.


### Reference 38 — Expert Whiteboard Checklist

A makeup artist at a whiteboard: American foundations (X X X X) vs theirs (check check check). Teacher-authority plus handwritten contrast. The human presenter triggers the realism protocol.


### Reference 24 — Durability Time-Matrix

Month 1 vs Month 6, their product vs the copycat, with a DEAD stamp on the failed knockoff. Anti-copycat proof for anyone fighting cheap imitators.


### Reference 48 — Part vs Part

Factory handle vs upgraded handle side by side with spec captions — 'It ain't your back. It's the angle.' Blame-the-tool reframe plus a clean physical comparison.


### Reference 33 — Tested-Them-All Exposé

Five rival products on a table, warning icons, red verdict band: '4 were scams.' Authority-test framing with scam-fear. Rival brands must be genericized when recreating.


### Reference 04 — Ranked Test Grid

Nine devices, each hand-held with an x/10 score badge. 'We tested 21' editorial authority plus curiosity about the winner.


## Family 5 — Testimonial & Social-Proof Styles

Quote cards, handwritten post-its, review-interface frames, person-holding-product portraits, and AMA-style frames. The mechanism is peer proof — someone like me already took the risk. One firm rule: quote text and attributions come from YOUR real reviews, or are clearly proposed as placeholder copy for you to approve. The skill replicates the format; it does not invent customers as fact.


### Reference 14 — Post-It Handwritten Note

Lip serums casually lying on a windowsill above a marker-written post-it testimonial. Analog textures read human in a feed of polished ads. Ran 28 days, top 6%.


### Reference 17 — Breaking-News Post-It on Product Pile

A hand slaps a 'BREAKING: 2 free bottles' note over a heap of bottles. Urgency scribble plus abundance shot — testimonial format hybridized with an offer.


### Reference 19 — Portrait Quote with Attribution Bar

An older man in his workshop holding the product under a serif quote, name-age-job attribution, micro trust bar. Identity-proof: the customer sees themselves. Realism protocol fully on.


### Reference 40 — Oversized Quote Lead

The quote IS the headline, at maximum size, product below. When one customer sentence is stronger than any copywriter line, this is the format.


### Reference 25 — Lifestyle Scene with First-Person Overlay

Product glowing on a kitchen table under a serif first-person story line. Warm, native, editorial-feeling social proof.


### Reference 46 — Story-Style AMA Frame

Instagram-story question chip ('what do you actually give your dog…') answered by a product-in-hand photo with a caption block. Platform-native camouflage.


## Family 6 — Big-Claim Product Hero

The workhorse family and the deepest in this library: one dominant claim in large type, a clean product presentation, and usually an offer bar, stat strip, or icon row. The mechanism is single-claim clarity — one promise, zero ambiguity, product as proof-object. When in doubt, this family converts across nearly every niche.


### Reference 02 — Claim + Stat Strip

'Softer skin in the shower' over a floating showerhead with a three-stat bar (30-sec install / 96.6% chlorine reduced / 91.8% limescale blocked). Sensory promise up top, lab authority below.


### Reference 13 — Price-Anchor Slash

Product left, claim right, $78 struck through to $9. Outcome claim plus an offer too cheap to ignore. Top 1% of 263 ads.


### Reference 36 — Type-Scale Contrast Claim

'20 YEARS of eye bags / GONE IN 11 DAYS' — the time contrast carried entirely by type size. Simple, brutal, effective.


### Reference 39 — Sensory-Fear Claim

'Guests can smell it before you can' over the device mid-spray. Social embarrassment is one of the strongest problem-aware triggers in home and personal care.


### Reference 47 — Objection-Kill Split

'We cut the price. Not the performance.' Left rail handles the price objection and stacks ingredient bullets; right side holds the pack; scarcity bar underneath.


### Reference 21 — Podium Offer Hero

Dark studio podium, category-king claim, BOGO chip. Premium lighting on an unglamorous product category.


### Reference 29 — Pure Offer Trio

BUY 2 GET 1 FREE in giant type over a three-pack lineup. Sometimes the offer is the concept.


### Reference 16 — Premium Numeral Underlay

A soft-palette product floating over an enormous translucent '40%.' Offer-led without looking discount-brand.


### Reference 18 — Playful Claim + Highlight Bar

'Your bed wins when getting up is optional' with a yellow-highlighted solution line and the product held to camera.


### Reference 28 — Curiosity Demo Hero

'Why everyone is holding this pillow' over a hand pressing the grid — a demo moment frozen as a static.


### Reference 34 — Blunt Bravado + Icon Row

Aggressive outcome claim, benefit icon row, press-logo bar. The press logos are borrowed authority — on recreation they become YOUR real proof or generic trust chips.


### Reference 37 — Founder Holding the Offer

A woman holds a physical sign with the deadline offer while the dog enjoys the product below. Human-holding-message plus payoff shot.


### Reference 08 — Made-For-You Specificity

Knitting-brace hands forming a heart, claim naming the exact audience ('Your hands weren't made to knit for hours'), seasonal 50% block.


## Family 7 — Editorial / Advertorial Style

Article-look framing: serif long headlines, story logic, authority figures, 'read the full story' energy. The mechanism is borrowed journalistic context — it earns attention as content before it sells. HONEST DEPTH NOTE: this library holds only two editorial references, so requests for large all-advertorial batches will show less structural variety than other families. The concepts themselves are strong; the variety ceiling is just lower.


### Reference 03 — Cultural-Secret Long Headline

A serif, magazine-style headline about a Korean scalp ritual vs Western shampoo habits, three copy blocks down the left rail, one product object. 72 days running, #1 of 238. Story-first selling.


### Reference 06 — Authority's Private Notes

'A retired hip surgeon's 5 notes' on aged notebook paper beside a vintage anatomical plate. Insider-secrets framing plus myth-busting checklist. The persona is editorial framing — replicate the structure with your own credible angle.


## Family 8 — Problem-Agitation Visual

The pain point dominates the frame; the product is secondary or entirely absent. Anatomy renders, exposé lighting, pattern-interrupt photography. The mechanism: press on the problem until clicking is the relief. These are your reminder that a static does not need the product in it to sell the product.


### Reference 09 — Anatomy Self-Diagnosis (No Product)

Healthy vs blocked nasal passages in 3D render — no product anywhere. 'The real reason your nose never feels clear' plus a promise line. #1 of 65.


### Reference 22 — Visceral Organ Concern

A photoreal overworked liver floating center-frame, claim above, protocol tease below, arrow CTA. Concern-generation for detox and organ-support niches.


### Reference 27 — Pattern-Interrupt Marker-on-Skin

A man drinks from a bottle with the benefit handwritten ON his cheek. Impossible to scroll past; the weirdness is the strategy.


### Reference 31 — Flashlight Label Exposé

A flashlight beam on a supplement's ingredient panel with one ingredient circled in red. Investigation framing — 'flip your child's bottle over right now.'


### Reference 07 — Private-Pain First Person

An illustrated intimate skin-fold problem with a first-person quote bar and small product inset. Illustration handles what photography can't show; first-person voice makes it recognition, not shame.


### Reference 49 — Shock Education Split

Two tissue specimens, BEFORE and AFTER, under 'The truth about quitting acid blockers.' Strong imagery — use deliberately; it earns attention at the cost of comfort.


## Family 9 — Grid, Checklist & Catalog Formats

Multi-panel avatar grids, product ranges, icon-benefit checklists, seasonal posters. The mechanism is breadth-of-fit: show enough versions of the buyer or the benefit that every viewer finds their square. These also carry offers well because the structure feels like merchandising, not persuasion.


### Reference 35 — Four-Avatar Identity Grid

The same hat on The Angler, The Gardener, The Golfer, The Rancher. Same product, your life — self-selection by quadrant. #1 of 139.


### Reference 50 — Benefit Checklist + Wearer Portrait

Four checkmarked benefits down the left, a silver-bearded gent in the cap on the right, guarantee chip below. Checklist authority plus identification.


### Reference 43 — Seasonal Urgency Poster

Storm-season pet earmuffs: icon rail left, hero dog center, four trust chips, red CTA band. Benefit stacking inside a seasonal window.


### Reference 23 — Neutral Range Grid

Twelve garments on an even grid with one positioning line. Minimalist breadth for brand-builders and B2B.


### Reference 20 — Try-On Collage (Weak-Signal Example)

A multi-model collage with sale ribbons — included deliberately as a LOW performer at capture (bottom-quartile rank, 1 day running). Kept as a teaching contrast: busy, unfocused, no single mechanism doing the work. The skill weights it down unless specifically requested.


## Part 6 — Getting the Most Out of Your Inputs

Product photo: the single biggest quality lever you control. Use a clean, well-lit, high-resolution PNG on a plain background. The model preserves your product with the fidelity of the photo you feed it — a blurry photo produces blurry-label recreations, and no prompt can fix that. Website PDF snapshot: use any full-page screenshot tool (browser extensions like GoFullPage, or Print to PDF) to capture your homepage top to bottom. This is the skill's reliable source for your brand colors, typography feel, claims, and guarantee terms — it works even when your live site blocks automated visitors. Avatar and angle: say it in plain words, like you'd brief a freelancer. 'Stay-at-home moms with foot pain from being on their feet all day; angle is all-day comfort without ugly orthopedic looks.' The more specific the human, the sharper the headlines. Quantity and testing: more is not automatically better. A well-spread 20 across four families usually teaches you more than an unfocused 50. Launch, read the numbers, then come back and ask for variations of only the winners — that iteration request is where this system compounds.


## Part 7 — When Something Goes Wrong

Key errors, quota errors, and billing errors each print a specific message, and GEMINI_SETUP.md's troubleshooting table maps each one to its fix. Generation quality issues (warped label, misspelled text, plastic-looking skin) are caught by the built-in QC pass and regenerated automatically up to two times. If a concept keeps failing on your product — some products photograph poorly into certain layouts — the skill will tell you and suggest the nearest family that suits your product's shape instead of silently delivering junk. Final note on ownership: everything generated belongs to your account and your Google key. The skill ships with zero information about any other person's brand — your inputs in the conversation are its only source of your brand data, by design.
