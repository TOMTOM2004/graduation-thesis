# DESIGN.md

## Purpose
This DESIGN.md defines the visual and structural rules for generating slides for a thesis proposal / research plan presentation.
The goal is not decorative presentation, but clear communication of:
- what the research is about
- why it matters
- what gap exists
- how the research will be conducted
- why the plan is feasible

Slides should feel academic, calm, refined, and logically ordered — with intentional visual hierarchy, not uniform flatness.

---

## Overall Design Direction

### Core Style
- clean
- minimal
- academic
- refined and intentional
- high readability with clear visual hierarchy
- logic-first
- low decoration
- serious but not intimidating
- **not monotonous** — visual rhythm is achieved through layout variation, not decoration

### Avoid
- flashy startup pitch style
- excessive icons
- overly bright gradients
- crowded pages
- long paragraphs
- decorative charts without analytical value
- too many colors
- playful or casual visual tone
- uniformly flat slides where everything looks equally important

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
4. readability (especially under screen-sharing conditions)

---

## Slide Philosophy

### One Slide, One Message
Each slide must communicate one primary message.

State that message explicitly — either as the slide title or as a single prominent sentence at the top.
Every bullet, table, or diagram on the slide must support that one message.
If you find yourself adding content that belongs to a different point, create a new slide.

Ask before building each slide: "What is the single thing the audience should remember from this slide?"
If the answer is more than one thing, split the slide.

### Three-Second Rule
Each slide must deliver its primary message within 3 seconds of first glance.
If the primary message is not immediately findable, the slide fails — regardless of how accurate the content is.

### Visual Focal Point
Every slide must have exactly one visual focal point.
The focal point is the element that the eye lands on first.
Everything else on the slide should be subordinate to that focal point.

Focal point can be created by:
- large font size relative to surrounding text
- bold weight against light-weight context
- generous whitespace isolating a single element
- a single use of accent color in an otherwise neutral slide

Never create two focal points on the same slide. If two elements seem equally important, one of them belongs on a different slide.

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
- text: dark gray or black (`#1a1a2e` or similar dark ink)
- primary accent: navy (`#1a237e` or similar)
- secondary accent / muted background: very light blue-gray (`#f0f4ff` or `#eef2f8`)
- caution / limitation / risk: muted orange (`#e65100` or similar, used sparingly)
- positive emphasis: restrained blue, not vivid green

### Rules
- Use at most 3 main colors on one slide
- Avoid bright red unless absolutely necessary
- Avoid rainbow palettes
- **Use color for hierarchy, not decoration**
- Accent color is reserved for anchor slides and the single most important element per slide

### Anchor Slide Color Privilege
Anchor slides (Title, Research Gap, Research Question, Hypothesis, Analytical Framework) are the only slides that may use full-saturation accent color as a background or dominant element.
All other slides use accent color for one element only — a single word, one border, one label.

### What Color Is For
Use color only for:
- anchor slide backgrounds / dominant treatments
- key terms in the research question or hypothesis
- causal arrows or phase labels in diagrams
- structural differentiation (e.g., phase colors in framework diagram)

Do not use color on body text. Do not use color to decorate bullets or general explanatory content.

---

## Typography

### General
- Prioritize readability over personality
- Use a clean sans-serif font
- Keep font usage consistent across all slides

### Hierarchy (5 levels, clearly differentiated)

| Level | Role | Size (px) | Notes |
|-------|------|-----------|-------|
| L1: Slide title | Topic + argument in short form | 26–28 | `h2` in slide header |
| L2: Anchor claim | Primary message of anchor slides; key takeaway sentence | 22–30 | Focal point; RQ ≥ 24, title slide h1 ≥ 30 |
| L3: Card heading / label | Section header within a slide, category name | 17–19 | `.gap-text h3`, `.fw-title`, phase labels |
| L4: Body text | Bullets, explanatory content, card body | 15–17 | Minimum 15px in cards, 16px for standalone bullets |
| L5: Note / source | Citations, footnotes, caveats | 14 | Never below 14px — no microtext |

Additional elements:
- Eyebrow / section tag: 12px, uppercase, letter-spaced (label-only, not readable content)
- Primary message bar: 17px, font-weight 600
- Conclusion emphasis (hypothesis conclusion, key takeaway): 18px, bold
- Table body: 16px minimum; table header: 14px

**The gap between L1 and L4 must be clearly visible. If all text looks the same size, the hierarchy has failed.**

### Rules
- Do not use many font sizes on one slide — stick to 2–3 levels per slide
- Do not mix multiple font families
- Do not use excessive bolding — bold is for the single most important phrase per slide
- Do not use underlines for decoration
- Avoid italics except for citations or special notation
- The primary claim must be visually dominant at screen-sharing distances

---

## Layout Rules

### Alignment
- Left alignment is default
- Avoid unnecessary center alignment (center is reserved for title slide and single-conclusion anchor slides)
- Use consistent margins and spacing

### Whitespace
- Generous whitespace is good
- Do not fill empty space just because it exists
- Spacing should clarify grouping
- Whitespace around the focal point is a design tool, not wasted space

### Structure
Preferred slide structure:
1. title (argument-bearing, not just a topic name)
2. optional: short takeaway sentence directly below title
3. core content (bullets, diagram, table, or takeaway statement)
4. source / note if needed

### Density
- Keep each slide visually light
- If content feels crowded, split into two slides
- Never force too much information into one page

### Vertical Balance
When a content block (card row, flow diagram, etc.) claims remaining slide height via `flex: 1`, it must be **vertically centered** within that space — not top-aligned.

**Implementation rule: Use CSS Grid with `align-content: center`.**
- The container gets `display: grid; flex: 1; align-content: center;`
- Grid auto-row sizing gives all cards uniform height (= tallest card's max-content)
- `align-content: center` centers the row vertically within the flex:1 space
- `align-items: start` keeps individual cards sized to content (no inflation)

Do NOT use `align-items: center` on flex containers for this purpose — it causes children with `align-self: stretch` to override back to inflation.

Applies to: `.two-col`, `.hyp-chain`, `.framework-flow`, and any future horizontal card/flow layout.

### Box and Card Sizing
- **Box height and padding must be proportional to content.**
- Do not use fixed large min-heights when the content is short — this creates "floating text in oversized boxes."
- Short label + 1-line text: compact padding (e.g., `12px 16px`)
- Normal card content: standard padding (e.g., `16px 20px`)
- Anchor slide emphasized statements: generous padding is acceptable
- **Parallel card sets** (e.g., 3 research gaps, 3 sub-questions, 3 phases): maintain visual parity by using consistent padding and min-height within the set — but that shared min-height should be the minimum needed for the shortest card, not inflated.
- Avoid oversized cards where text is surrounded by unnecessary whitespace within the box.

---

## Text Rules

### Bullet Points
- Use bullets for most explanatory content
- 3 to 5 bullets is standard
- 6 bullets is the upper limit
- Each bullet should ideally be one short phrase or one short sentence

### Paragraphs
- Avoid paragraphs
- Do not place long prose blocks on slides
- If explanation is long, convert into bullet hierarchy

### Slide Titles
- **Slide title is not just a topic label — it should carry an argument or purpose.**
- A viewer should be able to understand the intent of the slide from the title alone.
- Preferred forms: "X is insufficient because Y", "The gap is: [specific claim]", "Data covers [scope] for [reason]"
- Avoid generic titles like "Background", "Method", "Data" with no further specificity.
- A short takeaway sentence directly below the title is acceptable for supporting context.

### Emphasis

Allowed emphasis methods:
1. **size** — increase font size for the primary message only
2. **weight** — bold for key terms or the core takeaway
3. **whitespace** — isolate the most important element with surrounding space
4. **accent color** — use the primary accent (navy) to draw the eye once per slide

Rules:
- Use at most 2 of the 4 methods on a single slide
- Do not combine all four — it cancels the effect
- Never bold more than 3 phrases per slide
- Use accent color for one element only per slide
- **Every slide must have exactly one visual focal point** — the intersection of all emphasis methods applied

Use emphasis only for:
- research question
- gap
- hypothesis
- important finding expectation
- key methodological choice

---

## Charts, Tables, and Diagrams

### General Principle
Every visual must have analytical purpose.
Do not insert visuals only to make the slide look rich.

### Diagram-First Preference
For the following slide types, prefer diagrams over prose:
- **Hypothesis**: Show as a logical flow chain (premises → arrow → conclusion), not prose bullets
- **Analytical Framework**: Show as staged/phase diagram, not a list of steps
- **Research Gap vs Prior Research**: Show as a "what exists → what is missing" two-part structure
- **Variable or factor relationships**: Show as simple causal diagram

Diagrams for these slides should be:
- geometric and minimal (boxes, arrows, simple labels)
- immediately interpretable without reading explanatory text
- use phase/role differentiation through color labels or border styles, not decoration

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
- Keep tables compact
- Avoid large dense tables
- Highlight only the important row / column if needed

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

## Per-Slide Design Guidance

### Title Slide
Must include:
- thesis / proposal title
- name
- affiliation
- date if needed

Should feel clean and formal. The title is an anchor slide — it may use a full-width accent treatment or a strong typographic weight to establish visual presence.

### Background Slide
Use:
- 2 to 4 bullets
- 1 chart or fact if useful
- Clear statement of social / economic / academic relevance

### Prior Research Slide
Show:
- Major streams only
- No excessive literature listing
- Grouped comparison is preferred over random citation dump
- Consider a comparison structure (two columns or a table) to allow visual contrast between research traditions

### Research Gap Slide
**Anchor slide.** Treat this as a turning point in the narrative.
This slide should answer:
- what prior work has clarified
- what remains unclear
- why that unresolved part matters

**Design treatment**: Use stronger visual weight than surrounding slides. Options:
- Large numbered gap statements with significant size hierarchy
- Distinct background treatment (e.g., navy background with white text)
- Substantial whitespace around each gap item

Do not bury the gap in a list of bullets — make it impossible to miss.
Prefer a diagram-first or single-conclusion layout over a text-led layout.

### Research Question Slide
**Anchor slide.** This is the most important slide in the deck.
The research question must be visually dominant — large, isolated, and immediately readable.
Everything before this slide builds toward it. Everything after this slide follows from it.

**Design treatment**:
- The question text should be the largest and most prominent element on the slide
- Use a bordered box or strong typographic weight to isolate the question
- Do not place other content at the same visual weight as the research question itself
- Use center or generous left-aligned layout with maximum surrounding whitespace

### Hypothesis Slide
**Anchor slide.**
State the hypothesis as a clear, falsifiable claim.
Show the logical chain that leads to it (premises → conclusion).

**Design treatment**: Use a flow or stepped layout to make the reasoning structure visible.
- Premises are shown as labeled steps
- Conclusion is visually distinguished (e.g., filled background, distinct color)
- Use arrows or connecting lines to show directional reasoning
- Prefer diagram-first over prose-first

### Analytical Framework Slide
**Anchor slide.**
Show the overall structure of the analysis as a diagram or staged flow.
Each stage must be named and briefly described.
The audience should be able to grasp the full research architecture from this one slide.

**Design treatment**:
- Use a phase-based diagram (3 phases = 3 boxes with connecting arrows)
- Each phase box has a role label + 1-line description
- Differentiate phases visually using border-top color or background shade
- Do not use a prose list for a framework slide — it defeats the purpose

### Data Slide
Must specify:
- dataset source
- period
- unit of analysis
- main variables
- why the data is appropriate

Use a compact table or structured card layout. Avoid long prose.

### Method Slide
Must specify:
- analytical method
- why this method fits the question
- assumptions or points of caution if relevant

### Contribution Slide
Separate:
- academic contribution
- practical / policy contribution
when possible

### Timeline Slide
Use a simple structured layout.
Do not overcomplicate with detailed project management visuals.

### References Slide
Keep it compact and readable.
Use consistent citation style.

---

## Visual Rhythm Across the Deck

Monotony comes not from plain design, but from every slide using the same layout.
Break monotony through rhythm — alternating slide types — not through more decoration or more color.

### Four Slide Types

| Type | When to use | Primary element |
|------|-------------|-----------------|
| **Text-led** | argument, background, limitation | bullets or short prose |
| **Comparison** | prior research, two-sided problem, before/after, data structure | two-column or table |
| **Diagram-led** | framework, causal flow, analytical structure, hypothesis reasoning | flow diagram or staged layout |
| **Takeaway (single-conclusion)** | research question, hypothesis, key finding | one large statement, minimal surrounding content |

### Rules
- Do not use the same slide type more than 2 times in a row
- Anchor slides (Research Gap, Research Question, Hypothesis, Framework) should use Takeaway or Diagram-led type
- Background slides may use Text-led
- Prior research and data slides may use Comparison or Table
- At least every 3rd slide should differ in layout type from its neighbors

---

## Visual Restraint Rules
To preserve academic credibility:
- No excessive animation assumptions
- No trendy UI motifs
- No oversized decorative shapes
- No hero-image-heavy layouts
- No marketing-style slogans
- No uniform flatness — intentional hierarchy is required

This presentation is a research proposal, not a sales pitch.
But it is also not a homogeneous wall of bullets — intentional visual variety is an academic communication tool.

---

## Online Presentation Constraints

These slides are designed to be presented via screen sharing (HTML in browser) on a Mac display.
Apply the following constraints at all times.

### Readability at Distance
- Body text minimum: 16px equivalent (no microtext)
- Slide title: minimum 22–26px equivalent
- Anchor claim / focal point text: minimum 20px, preferably larger
- Avoid text that requires zooming or squinting
- Every element must be readable at 70% of the original size

### Screen Sharing Safety
- Do not rely on subtle color differences — they wash out on shared screens
- Ensure sufficient contrast between text and background (WCAG AA as a minimum target)
- Avoid very thin font weights — they disappear on low-quality streams
- Dark text on white/light background is strongly preferred for body content

### No Speaker Notes Embedded in Slides
- Do not add explanatory prose that belongs in spoken delivery
- If a sentence exists only to explain the slide to a reader, remove it
- Slides must stand alone visually without needing a caption

### Layout Stability
- Do not use layouts that break at different window sizes
- Avoid absolute pixel positions that assume a fixed viewport
- Test that the slide remains coherent when scaled down to 80%
- Prefer CSS flexbox / grid over fixed-position layouts

---

## Japanese Typography Rules

### Word Breaking
Japanese text in narrow containers (cards, flow boxes) must not break compound words or katakana phrases mid-word.

**CSS rule — apply to all card body text, card bullets, and card output labels:**
```css
word-break: keep-all;
overflow-wrap: break-word;
line-break: strict;
```

- `keep-all` prevents CJK line breaks between characters within a word boundary
- `overflow-wrap: break-word` allows emergency breaks only when a single word exceeds the container width
- `line-break: strict` enforces strict Japanese punctuation rules (no `。` or `、` at line start)

### Semantic Line Breaks in Narrow Cards
When card width is narrow (< 250px effective text width), long Japanese phrases will still wrap awkwardly even with `keep-all`. In these cases, insert explicit `<br>` tags at semantic boundaries:

- Between a subject/topic and its predicate
- Between a cause and its effect
- Before a particle that introduces a new clause (「が」「は」「を」)
- Between independent noun phrases joined by particles

Example: `外的ショック → 国内物価上昇 →<br>実質所得の減少` instead of letting the browser decide.

### Line Height for Japanese
Japanese text requires more generous line-height than Latin text due to character density:
- Card body: `line-height: 1.7` (minimum 1.6)
- Bullets: `line-height: 1.55–1.6`
- Conclusion / emphasis: `line-height: 1.55`

---

## Diagram Direction Rules

### Arrow Direction Must Match Layout Direction
- **Horizontal layouts** (side-by-side cards, flow diagrams): use `→` arrows
- **Vertical layouts** (stacked items, top-to-bottom flow): use `↓` arrows
- Never use `↓` in a horizontal flow or `→` in a vertical stack

### Arrow Styling
- Arrows between flow phases / hypothesis steps: accent color (`var(--blue-soft)` or similar), 22–24px
- Arrows should be visually subordinate to the cards they connect — they are structural, not focal
- Use `flex-shrink: 0` on arrow containers to prevent them from collapsing

---

## Default Generation Rules for AI
When generating slides from notes or source materials, always follow these rules:

1. One slide = one main idea
2. Convert long text into bullets
3. Shorten wording aggressively while preserving meaning
4. Prefer logical hierarchy over visual complexity
5. Define technical terms when first introduced
6. Create a smooth narrative from background to method
7. Split dense content into multiple slides
8. Include source labels when presenting factual data
9. **Prefer diagrams over prose for hypothesis, framework, and gap slides**
10. When unsure, choose the more conservative academic design
11. **Every slide must have one visual focal point** — identify it before placing content
12. **Box/card padding and min-height must match content size** — do not inflate boxes with empty space
13. **Slide titles must carry an argument, not just a topic label**
14. **Vary layout type across slides** — check that no type repeats more than twice in a row

---

## What Good Output Looks Like
A good slide deck should feel:
- coherent
- calm
- readable
- structured
- academically credible
- easy to present verbally
- **visually varied without being noisy**
- **intentionally weighted — important slides look more important**

A good deck should not feel:
- crowded
- flashy
- sales-oriented
- vague
- over-designed
- visually noisy
- **uniformly flat — where every slide looks as important as every other**

---

## Output Constraints
When creating slides:
- Keep titles short but argument-bearing
- Keep bullets short
- Avoid full sentences unless necessary
- Avoid text-heavy pages
- Prefer slide count increase over density increase
- Preserve consistent visual hierarchy across all slides
- **Compact boxes: size to content, not to a fixed template**

---

## Final Check
Before finalizing any deck, verify:

**Three-second test**
- Does each slide deliver its primary message within 3 seconds of first glance?
- Is the visual focal point immediately findable?

**One message per slide**
- Does each slide have a single identifiable primary message?
- Is that message stated explicitly — in the title or as a prominent element?

**Emphasis discipline**
- Is emphasis used with at most 2 methods per slide?
- Are there more than 3 bolded phrases on any single slide?
- Is there exactly one visual focal point per slide?

**Anchor slides**
- Do Title, Research Gap, Research Question, Hypothesis, and Analytical Framework stand out visually from surrounding slides?
- Is the research question the most visually dominant element in the deck?
- Do hypothesis and framework use diagram-led or flow-based layouts?

**Visual rhythm**
- Does the deck alternate between text-led, comparison, diagram-led, and takeaway slide types?
- Are there more than 2 consecutive slides of the same type?

**Box and card sizing**
- Are any boxes oversized relative to their content?
- Is padding proportional to content in card/box elements?
- Are parallel card sets (same role, same visual weight) consistent within the set?

**Typography hierarchy**
- Is the hierarchy between slide title, anchor claim, card heading, and body text clearly visible?
- Does the primary claim appear at a size that stands out from surrounding body text?

**Color discipline**
- Is accent color used for at most one element per non-anchor slide?
- Are anchor slides visually differentiated using color privilege?
- Is color used structurally (hierarchy, role), not decoratively?

**Diagram-first slides**
- Are hypothesis, analytical framework, and research gap presented with diagrams rather than prose?
- Can each diagram be interpreted without reading surrounding explanatory text?

**Online readability**
- Is every text element readable at 70% scale?
- Are there any microtext elements (notes, labels) that disappear on a shared screen?
- Does any slide contain prose that belongs in spoken delivery, not on the slide?
- Is contrast sufficient for screen sharing conditions?

**Overall**
- Is the research gap explicit?
- Is the overall structure logically progressive?
- Is the visual tone academic and restrained — but not uniformly flat?

If not, revise.
