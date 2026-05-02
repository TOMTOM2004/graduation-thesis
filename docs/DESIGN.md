# DESIGN.md

## Purpose
This DESIGN.md defines the visual and structural rules for generating slides for a thesis proposal / research plan presentation.
The goal is not decorative presentation, but clear communication of:
- what the research is about
- why it matters
- what gap exists
- how the research will be conducted
- why the plan is feasible

Slides should feel academic, calm, minimal, and logically ordered.

---

## Overall Design Direction

### Core Style
- clean
- minimal
- academic
- calm
- high readability
- logic-first
- low decoration
- serious but not intimidating

### Avoid
- flashy startup pitch style
- excessive icons
- overly bright gradients
- crowded pages
- long paragraphs
- decorative charts without analytical value
- too many colors
- playful or casual visual tone

---

## Audience
Primary audience:
- seminar professor
- thesis supervisor
- university students
- academic listeners who want to quickly understand the logic of the proposal

Slides must prioritize:
1. clarity
2. logical flow
3. feasibility
4. readability

---

## Slide Philosophy

### One Slide, One Message
Each slide must communicate only one main point.

### Slides Are for Display, Not Full Script
Slides should show key points only.
Do not write what should instead be spoken aloud.

### Logic Before Beauty
A plain but clear slide is preferred over a visually impressive but confusing slide.

### Brevity Is Mandatory
Use short phrases, not dense prose.

---

## Tone of Expression
Use language that is:
- precise
- neutral
- academic
- understandable for educated non-specialists

Avoid:
- exaggerated claims
- emotional wording
- vague buzzwords
- unnecessary jargon
- unexplained English technical terms

If a technical term is necessary, keep it concise and define it when first introduced.

---

## Color System

### Base
- background: white or near-white
- text: dark gray or black
- primary accent: navy / dark blue (`#1a2e4a`)
- secondary accent: muted blue-gray (`#4a7fa5`)
- **emphasis: muted crimson (`#b03050`)** — reserved for **key numbers, headline findings, and conclusion phrases** that must catch the eye in seconds. Use sparingly (typically 1–3 spots per slide).
- caution / limitation / risk: muted orange (`#b85c1a`) — reserved for **warnings, risks, and limitations**. Do not use for emphasis.
- positive emphasis (alternative): restrained blue, not vivid green

### Rules
- use at most 3 main colors on one slide
- avoid bright red unless absolutely necessary (muted crimson is acceptable as the dedicated emphasis color)
- avoid rainbow palettes
- use color for hierarchy, not decoration
- **emphasis color (crimson) and caution color (orange) MUST NOT be used in the same role**; they are semantically distinct. Crimson signals "this number / finding matters." Orange signals "be careful here."
- the emphasis color is also reserved for hook slides, headline figures in result slides, and the conclusion sentence in the contribution slide

### Emphasis Usage (per-slide rule)

How `<strong>` and the emphasis color (`.emp` / crimson) interact across the deck:

- **`<strong>`** = bold weight + default navy color. Use freely for sub-emphasis (sub-headings within a paragraph, contrasting words, etc.).
- **`.emp` (crimson)** = the *headline* of a slide. Layered on top of `<strong>` only when a phrase is THE one thing the audience must remember from that slide.

#### Rules
1. **One `.emp` spot per slide** is the default.
2. **Two `.emp` spots** are allowed only on contrast slides where symmetric emphasis on each side IS the design (e.g., cost-push vs demand-pull → one emp per column).
3. A **"number + unit" pair** (e.g., `6%`, `34.6 兆円`) counts as ONE spot.
4. **Never apply `.emp` to every `<strong>`** in a slide. If everything is emphasized, nothing is. The whole point of crimson is that the audience's eye jumps to it within a second.
5. Slides whose entire layout is already a strong visual cue (navy-background RQ box, navy-background hypothesis conclusion, full-frame diagram) do NOT need additional `.emp` — the layout itself is the emphasis.
6. Slides with existing semantic accent color (e.g., gap boxes with orange border) do NOT add `.emp` — color stacking dilutes both meanings.

#### Pattern across the deck
| Slide type | Default emphasis treatment |
|------------|----------------------------|
| Hook / number highlight | big number in navy (main), `.emp` on the comparison anchor (1–2 spots) |
| Background fact | one `.emp` on the structural conclusion phrase |
| Background number table | one `.emp` on the most important row's number |
| Problem setting (contrast) | one `.emp` per column (the conclusion arrow of each side) |
| Prior research / literature | no `.emp` (inventory slide; emphasis dilutes) |
| Research gap | no `.emp` (gap boxes already carry orange accent) |
| Research question | no `.emp` (RQ box's navy background IS the emphasis) |
| Hypothesis | no `.emp` (conclusion box's navy background IS the emphasis) |
| Framework / diagram | no `.emp` (full diagram carries the message) |
| Data / methods | optional, only on the most decisive datasource or method choice |
| Schedule | no `.emp` (current-position orange already strong) |
| Contribution | one `.emp` on the contribution sentence's headline phrase |
| References | no `.emp` |

---

## Typography

### General
- prioritize readability over personality
- use a clean sans-serif font
- keep font usage consistent across all slides

### Hierarchy
- title: large and bold
- section labels: medium, clearly separated
- body text: medium size, readable from a distance
- notes / references: smaller but still legible

### Rules
- do not use many font sizes on one slide
- do not mix multiple font families
- do not use excessive bolding
- do not use underlines for decoration
- avoid italics except for citations or special notation

---

## Layout Rules

### Alignment
- left alignment is default
- avoid unnecessary center alignment
- use consistent margins and spacing

### Whitespace
- generous whitespace is good
- do not fill empty space just because it exists
- spacing should clarify grouping, **not split a group apart**
- when the natural reading flow is `A → B → conclusion`, the gap between B and the conclusion must be **smaller** than the surrounding whitespace. Otherwise the conclusion reads as an unrelated footnote.
- if vertically centering a group of cards introduces a large gap between the cards and the conclusion that follows, **prefer top-aligning the cards** and leaving empty space below the conclusion as "tail whitespace". Tail whitespace is acceptable; mid-flow whitespace that splits a group is not.

### Structure
Preferred slide structure:
1. title
2. core message / takeaway
3. supporting bullets, figure, or table
4. source / note if needed

### Density
- keep each slide visually light
- if content feels crowded, split into two slides
- never force too much information into one page

---

## Text Rules

### Bullet Points
- use bullets for most explanatory content
- 3 to 5 bullets is standard
- 6 bullets is the upper limit
- each bullet should ideally be one short phrase or one short sentence

### Paragraphs
- avoid paragraphs
- do not place long prose blocks on slides
- if explanation is long, convert into bullet hierarchy

### Emphasis
Use emphasis only for:
- research question
- gap
- hypothesis
- important finding expectation
- key methodological choice

Avoid emphasizing too many things at once.

---

## Line Breaks Inside Boxes

When text sits inside framed boxes (hypothesis steps, gap boxes, sub-RQ cards, flow boxes, etc.), the browser's automatic wrap frequently breaks lines at awkward positions — splitting compound words, technical terms, or proper nouns. This damages readability and looks unprofessional in academic presentations.

### Rules
- **Never let auto-wrap break a compound word or technical term.** Protect words like:
  - 「コストプッシュインフレ」「デマンドプル」「裁量的支出」「輸入含有率」「実質消費」「価格転嫁率」
- Insert explicit `<br>` at semantically meaningful break points:
  - after a comma (`、`) or period (`。`) — clause boundary
  - before a new subject or topic shift
  - **never inside a noun phrase or proper noun**
- Apply CSS safety net to box containers:
  ```css
  word-break: keep-all;       /* CJK: do not break inside a word block */
  overflow-wrap: anywhere;    /* allow break only when unavoidable */
  ```
- For surgical protection of specific phrases, wrap them in `<span class="nowrap">…</span>` (with `.nowrap { white-space: nowrap; }` defined globally). Apply this only to the actual technical term, not the surrounding clause — overusing `nowrap` causes overflow.
- Box width must comfortably fit the longest single phrase that must not break. If a phrase exceeds the box width, widen the box (reduce padding / arrow padding / inter-box gap) or rephrase shorter — do not let the browser decide.

### Implementation menu (pick the lightest sufficient one)
1. **Explicit `<br>`** at semantic boundaries — primary tool.
2. **`<span class="nowrap">熟語</span>`** — for individual technical terms.
3. **CSS `word-break: keep-all`** — global safety net on the box.
4. **Reduce `.hyp-box` / `.hyp-arrow` padding** — gain a few pixels of content width across all boxes.
5. **Rephrase shorter** — last resort if layout cannot be widened.

### Workflow
1. After authoring the slide, view it in the browser at the production size (e.g. 1200×675).
2. Read every box. If a line breaks mid-word, fix it with `<br>` at the next sensible break point upstream.
3. Re-check after any text edit, since changing a single character can shift wrapping.

---

## Contrastive Information

When a slide presents a binary contrast (e.g. 低所得層 vs 高所得層, コストプッシュ vs デマンドプル, ベースライン vs 介入後), do not pack both sides into a single paragraph or list.

### Rules
- Use **two `<p>` paragraphs within the same box** (with a small vertical gap), OR
- Use **two adjacent boxes / columns** when the contrast is the central message of the slide.

### Reasoning
Contrastive structure parses faster when each side has its own visual block. A single run-on paragraph forces the reader to mentally segment the comparison and slows comprehension during a live presentation.

### Examples
- Q1 vs Q5 expenditure shares → two paragraphs in the hypothesis premise box
- Cost-push vs demand-pull mechanism → two columns (current `s4` design)
- Baseline vs policy intervention outcomes → two side-by-side mini-tables

---

## Charts, Tables, and Diagrams

### General Principle
Every visual must have analytical purpose.
Do not insert visuals only to make the slide look rich.

### Charts
Use charts when showing:
- trends
- comparisons
- distributions
- causal framework components
- expected analytical outputs

Preferred chart style:
- minimal
- labeled clearly
- low visual noise
- readable axes
- direct titles

Avoid:
- 3D charts
- overloaded legends
- too many categories
- decorative colors

### Tables
Use tables only when exact values or structured comparison are necessary.

Rules:
- keep tables compact
- avoid large dense tables
- highlight only the important row / column if needed

### Diagrams
Use simple diagrams for:
- research framework
- variable relationships
- causal assumptions
- analytical flow
- data processing flow

Diagrams should be linear and interpretable at a glance.

---

## Academic Content Priorities

When generating slides, prioritize the following order of importance:

1. research theme
2. background / problem awareness
3. research gap
4. research objective
5. research question
6. hypothesis
7. data
8. method
9. expected contribution
10. schedule
11. references

Slides should make it easy for the audience to answer:
- What is this study about?
- Why is it worth doing?
- What is missing in existing work?
- What exactly will be analyzed?
- Can this actually be done?

---

## Recommended Slide Flow
Preferred structure for a thesis proposal presentation:

1. Title
2. Research background
3. Problem setting
4. Why this matters
5. Prior research
6. Research gap
7. Research objective
8. Research question / hypothesis
9. Analytical framework
10. Data
11. Method
12. Expected contribution
13. Risks / limitations
14. Timeline
15. References

If the deck is short, combine related items carefully:
- background + problem setting
- research question + hypothesis
- risks + limitations

---

## Slide Deck Pacing

A 10–15 slide academic deck should not be a uniform sequence of identical text-and-bullet pages. Build mild rhythm so the audience's eye does not glaze.

### Rule of thumb
- Every 4–5 slides should carry **one strong visual element** (chart, diagram, big-number layout, or framework figure).
- Around the start of the deck, place **one or two "anchor" slides** that orient the audience to the scale and stakes of the problem.
- Avoid back-to-back slides of the same visual structure.

### Recommended structure (proposal deck)
| # | Slide | Visual weight |
|---|-------|---------------|
| 1 | Title | calm |
| 2 | Hook / Number highlight (optional) | **strong** |
| 3–4 | Background / motivation | text + small chart |
| 5 | Problem setting | diagram |
| 6 | Prior research | grouped cards |
| 7 | Research gap | text + venn / diagram |
| 8 | Research question | **strong** (centered) |
| 9 | Hypothesis | diagram |
| 10 | Analytical framework | **strong** (full diagram) |
| 11 | Data | table |
| 12 | Method / Feasibility | text + evidence |
| 13 | Expected contribution | structured cards |
| 14 | Timeline | timeline |
| 15 | References | text |

If the deck is short, drop low-weight slides first; keep the visually strong ones to preserve rhythm.

---

## Page Indicator

Every slide should display its page index (e.g. `7 / 14`) — this helps the audience track progress and lets the presenter handle questions ("can you go back to slide 4?") cleanly.

### Rules
- **Position**: bottom center, **inside the slide's white frame** (not in the dark viewport background outside the slide). For a 1200×675 slide scaled-to-fit on a standard viewport, `bottom: 40–60px` is usually correct; `bottom: 18px` typically falls outside the white frame and gets visually clipped.
- **Color**: very light gray (`#aaa` or similar) — must not compete with content
- **Size**: 12–13 px, tabular-nums for stable digit width
- **Letter-spacing**: slight (0.04–0.08em) for legibility
- Keep it as a fixed UI element relative to the viewport, but verify visually that it lands inside the white frame at presentation resolution

### Why bottom-center over bottom-right
- bottom-center reads as "frame metadata" and stays out of the content's visual flow
- on slides with content concentrated in the upper half (e.g. contribution slide with tail whitespace), the centered indicator gently fills the lower visual gap without competing for attention
- bottom-right works too but tends to clash with content corners on dense slides

---

## Per-Slide Design Guidance

### Title Slide
Must include:
- thesis / proposal title
- name
- affiliation
- date if needed

Should feel clean and formal.

### Hook Slide / Number Highlight (optional, used 0–2 times per deck)
A slide built around a **single dominant number** so the audience grasps the scale of the problem within seconds.

Use cases:
- before the detailed background, to anchor the magnitude of the issue
- after the framework, to emphasize an estimated headline effect

Required elements:
- **one large numeric figure** (90–140 px), in navy or muted blue
- a **one-line caption** naming what the number represents (period, scope)
- a **comparison anchor** (e.g. share of GDP / per household / vs prior estimate)
- **source label** at the bottom

Rules:
- at most one hook per ~6 slides — overuse breaks academic tone
- the number must come from a verified source or own estimate; mark "暫定" (provisional) if not finalized
- no decorative backgrounds, gradients, or vivid colors — the number itself is the visual
- horizontal centering, generous whitespace, no bullets

### Background Slide
Use:
- 2 to 4 bullets
- 1 chart or fact if useful
- clear statement of social / economic / academic relevance

### Prior Research Slide
Show:
- major streams only
- no excessive literature listing
- grouped comparison is preferred over random citation dump

### Research Gap Slide
Must be explicit.
This slide should answer:
- what prior work has clarified
- what remains unclear
- why that unresolved part matters

### Research Question Slide
This is a key slide.
The research question should be visually prominent and written clearly.

### Data Slide
Must specify:
- dataset source
- period
- unit of analysis
- main variables
- why the data is appropriate

### Method Slide
Must specify:
- analytical method
- why this method fits the question
- assumptions or points of caution if relevant

### Feasibility Slide (mid-stage and onward)
A slide that demonstrates implementation viability by listing concrete progress already achieved.

#### When to use
- ❌ **Not** in the **first proposal seminar** (theme + plan stage). Showing concrete results (e.g. estimation outputs, identification placebos) at the planning stage breaks the academic pacing — it pre-empts the discussion that the second/third seminars are for, and it usurps the advisor's "advise the plan" role.
- ✅ Mid-term seminars (after Phase 1 / Phase 2 completion), when the question becomes "is the rest of the plan still feasible given what we now know?"
- ✅ Final pre-submission deck, as evidence that the ambitious scope was actually delivered.

#### Why include it (when timing is right)
- Ambitious proposals (especially undergraduate theses spanning identification + simulation) face skeptical reactions from advisors at later stages
- Naming work already done converts "promises" into "completed steps"
- Strengthens the credibility of the remaining schedule

#### Structure
- 4–6 concrete checkpoints, each one short phrase + tiny anchor (a number, a method name, or a key dataset)
- ✓ check-mark list, navy text, no decorative icons
- one conclusion sentence at the bottom: "Phase X risks substantially reduced"

#### Rules
- only show items actually completed or in measurable progress — do not pad
- avoid placing headline result numbers here when the slide's purpose is feasibility (those belong on Hook / Result slides)
- one `.emp` spot allowed on the conclusion sentence

#### What goes in the first proposal deck instead
For seminar 1, feasibility is communicated **implicitly** through:
- the data slide (sources are public/already accessible)
- the framework slide (each phase is methodologically grounded in cited prior work)
- the schedule slide (timeline is realistic)
There is no need for a dedicated "we already did it" slide at this stage.

### Contribution Slide

Use a **3-axis structure** for thesis projects whose deliverables include both empirical findings and a reusable model/tool:

1. **Academic contribution** — what the study adds to existing literature (a new identification, a new decomposition, a previously unstudied case).
2. **Policy / practical contribution** — concrete policy implications, scenarios evaluated, decisions the work informs.
3. **Deliverable / model contribution** — when applicable, the analytical artifact itself is part of the contribution (a parameterized simulation model, a public dataset, a reusable estimation pipeline).

For purely empirical theses (no model artifact), drop axis 3 and use the original 2-axis split.

#### Layout
- 3 cards side by side, equal width
- card header with axis label (Academic / Policy / Deliverable) and full-name title
- short body (3–4 short lines) describing the specific contribution
- one conclusion sentence below the cards summarizing the deck's takeaway; **one `.emp` spot allowed** on the headline phrase

#### Rules
- Each card must claim only what the study can actually deliver — do not list aspirational extensions
- Keep the academic axis tight: the contribution should map directly to one or more research-gap items already shown in the gap slide
- The conclusion sentence should not introduce a new claim — it should distill the three axes into one memorable phrase

### Timeline Slide
Use a simple structured layout.
Do not overcomplicate with detailed project management visuals.

### References Slide
Keep it compact and readable.
Use consistent citation style.

---

## Visual Restraint Rules
To preserve academic credibility:
- no excessive animation assumptions
- no trendy UI motifs
- no oversized decorative shapes
- no hero-image-heavy layouts
- no marketing-style slogans

This presentation is a research proposal, not a sales pitch.

---

## Default Generation Rules for AI
When generating slides from notes or source materials, always follow these rules:

1. one slide = one main idea
2. convert long text into bullets
3. shorten wording aggressively while preserving meaning
4. prefer logical hierarchy over visual complexity
5. define technical terms when first introduced
6. create a smooth narrative from background to method
7. split dense content into multiple slides
8. include source labels when presenting factual data
9. prefer simple diagrams over decorative layouts
10. when unsure, choose the more conservative academic design

---

## What Good Output Looks Like
A good slide deck should feel:
- coherent
- calm
- readable
- structured
- academically credible
- easy to present verbally

A good deck should not feel:
- crowded
- flashy
- sales-oriented
- vague
- over-designed
- visually noisy

---

## Output Constraints
When creating slides:
- keep titles short
- keep bullets short
- avoid full sentences unless necessary
- avoid text-heavy pages
- prefer slide count increase over density increase
- preserve consistent visual hierarchy across all slides

---

## Image Workflow

### 素材生成
- スライドに必要な画像（概念図・フロー図・背景ビジュアル等）は **OpenAI Images2** で生成する
- 生成した画像は `slides/assets/` に格納する（ファイル名: `s<スライド番号>-<内容>.png`）

### ブラッシュアップ時の差し込み
- 初回生成時はプレースホルダー（`<!-- [IMAGE: slides/assets/s09-framework.png] -->` 等）をスライド内に記述する
- ブラッシュアップフェーズで実画像を `<img>` タグに差し替える
- 画像は DESIGN.md の既存ルール（分析目的のあるビジュアルのみ、装飾的な画像は不可）に従う

### 画像の品質基準
- アカデミックなトーンに合致すること（派手・カジュアルな画像は不可）
- スライドの配色（navy / blue-gray / white）と調和すること
- 解像度: スライド表示に十分な品質（最低 1200×675px 推奨）

---

## Final Check
Before finalizing any deck, verify:

- Is each slide about one clear point?
- Is the research gap explicit?
- Is the research question visible and understandable?
- Are data and method concrete enough?
- Is the slide readable within a few seconds?
- Is the visual tone academic and restrained?
- Is the overall structure logically progressive?

If not, revise.
