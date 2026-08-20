---
name: "Family Force Commercial Guide"
description: "An Arabic arcade-operator service binder for exact order, production, QA, and APK delivery work."
colors:
  service-ink: "#f5f7ef"
  muted-steel: "#b8c7d2"
  midnight-floor: "#07101f"
  binder-panel: "#0d1b30"
  raised-panel: "#122541"
  registration-cyan: "#37d9e8"
  status-magenta: "#ff4f9f"
  safety-gold: "#f6c94d"
  danger-coral: "#ff6978"
  rule-blue: "#2d4963"
typography:
  display:
    fontFamily: "DIN Next Arabic, Noto Sans Arabic, Tahoma, Arial, sans-serif"
    fontSize: "clamp(1.65rem, 4vw, 3.5rem)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "DIN Next Arabic, Noto Sans Arabic, Tahoma, Arial, sans-serif"
    fontSize: "clamp(1.7rem, 4vw, 3.2rem)"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.025em"
  title:
    fontFamily: "DIN Next Arabic, Noto Sans Arabic, Tahoma, Arial, sans-serif"
    fontSize: "1.35rem"
    fontWeight: 700
  body:
    fontFamily: "DIN Next Arabic, Noto Sans Arabic, Tahoma, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "DIN Next Arabic, Noto Sans Arabic, Tahoma, Arial, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 800
rounded:
  tag: "8px"
  field: "10px"
  control: "12px"
  container: "14px"
  feature: "16px"
  round: "50%"
spacing:
  xs: "8px"
  sm: "12px"
  md: "18px"
  lg: "24px"
  xl: "28px"
  section: "42px"
components:
  button-primary:
    backgroundColor: "{colors.safety-gold}"
    textColor: "{colors.midnight-floor}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "12px 18px"
  button-secondary:
    backgroundColor: "{colors.registration-cyan}"
    textColor: "{colors.midnight-floor}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "12px 18px"
  button-reset:
    backgroundColor: "transparent"
    textColor: "{colors.muted-steel}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "12px 18px"
  input:
    backgroundColor: "{colors.binder-panel}"
    textColor: "{colors.service-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.field}"
    padding: "12px 13px"
  card:
    backgroundColor: "{colors.binder-panel}"
    textColor: "{colors.service-ink}"
    rounded: "{rounded.container}"
    padding: "18px 22px"
  tab-active:
    backgroundColor: "{colors.raised-panel}"
    textColor: "{colors.service-ink}"
    typography: "{typography.label}"
    padding: "17px 20px"
---

# Design System: Family Force Commercial Guide

## Overview

**Creative North Star: "The Arcade Operator Service Binder"**

This design system applies specifically to the `commercial-guide` web surface. It does not redefine the Android game's rendering, gameplay UI, or asset truth. The guide feels like a midnight service-manual opened beside an arcade cabinet: operational, exact, compact, and energized by high-visibility registration and safety colors.

The surface favors strong information hierarchy, tabbed dividers, specification tables, checklists, and status stamps over promotional cards. Dark tonal layers keep dense Arabic content readable; cyan marks technical structure, gold marks decisions and action, and magenta is reserved for identity or conspicuous status.

**Key Characteristics:**

- Arabic-first RTL composition with direct, practical copy.
- Midnight sheets separated by blue rules and restrained ambient lift.
- Cyan registration marks, safety-gold actions, and rare magenta stamps.
- Dense operational components that remain keyboard accessible, responsive, offline, and printable.

## Colors

The palette behaves like illuminated controls and registration ink on a midnight technical sheet.

### Primary

- **Safety Gold:** The decisive action and approval color, used for primary buttons, numbered markers, key values, legends, and release progress.

### Secondary

- **Registration Cyan:** The technical signal color for active tabs, secondary actions, table headings, process labels, checkboxes, and specification tags.

### Tertiary

- **Status Magenta:** A rare identity and status stamp used where a detail must feel branded or conspicuous.
- **Danger Coral:** Failure and not-ready language only; completed success uses the established mint-green state rather than borrowing cyan or gold.

### Neutral

- **Midnight Floor:** The page foundation and dark text used on bright controls.
- **Binder Panel:** The default content surface for cards, fields, fieldsets, and operational blocks.
- **Raised Panel:** A slightly brighter header or selected-surface layer.
- **Service Ink:** Primary high-contrast text.
- **Muted Steel:** Supporting prose, inactive navigation, metadata, and secondary controls.
- **Rule Blue:** Dividers, field borders, table rules, and grid seams.

### Named Rules

**The Signal Discipline Rule.** Gold means act or approve; cyan means technical structure or active position; magenta remains rare enough to read as a stamp.

**The Midnight Sheet Rule.** Build density with tonal panels and blue rules, never with a collage of unrelated card colors.

## Typography

**Display Font:** DIN Next Arabic, with Noto Sans Arabic, Tahoma, Arial, and sans-serif fallbacks  
**Body Font:** DIN Next Arabic, with Noto Sans Arabic, Tahoma, Arial, and sans-serif fallbacks  
**Label Font:** The same family stack in heavy weights

**Character:** One compact Arabic grotesk stack carries the entire manual. Scale, weight, color, and spacing—not decorative font changes—separate commands, specifications, prose, and status.

### Hierarchy

- **Display:** Bold, fluid masthead naming with tight tracking; it may grow from compact mobile scale to broad desktop scale.
- **Headline:** Bold, fluid panel title with tight tracking and compact leading.
- **Title:** Bold section heading used to open major specification groups.
- **Body:** Regular reading text with generous leading; lead copy is slightly enlarged and capped at roughly 68 characters.
- **Label:** Heavy compact type for controls, metadata, tab labels, badges, and status. It can be smaller without becoming faint.

### Named Rules

**The One-Family Manual Rule.** Keep the interface in the established Arabic sans-serif stack; create hierarchy through weight and scale rather than introducing display faces.

## Layout

The guide uses a centered content frame capped at 1440px. Masthead and main gutters are fluid, while the sticky horizontal tab rail may scroll rather than wrap. The first viewport pairs a 1.5fr lead with a narrower operational stamp; later surfaces use explicit two-, three-, four-, five-, or six-column grids according to their data.

Spacing is compact but not cramped: 18–28px is the normal component rhythm, 34px separates major lead columns, and section headings typically open after 42px. At 900px, broad grids reduce to one or two columns. At 620px, content grids become single-column, the status rail is removed, controls tighten, and multi-part runbook rows reflow without losing sequence.

Print is a first-class layout. Navigation, masthead, footer actions, and interactive controls disappear; all panels become visible, each major panel begins on a new page, dark fills become white, text becomes near-black, and shadows are removed.

**The Operational Grid Rule.** Choose the column count from the data relationship, then collapse predictably; do not force desktop density onto a narrow screen.

## Elevation & Depth

Depth is hybrid but restrained. Tonal layering and crisp rules carry most structure. A single deep ambient shadow lifts only prominent stamps, asset cards, and estimate panels; the sticky tab rail uses a smaller downward shadow to clarify its fixed layer. Logo depth is a localized drop shadow, not a general decoration.

### Shadow Vocabulary

- **Binder Lift:** Deep ambient shadow for high-value floating surfaces such as the scope stamp, asset cards, and estimate summary.
- **Sticky Rail:** Compact downward shadow used only beneath the pinned tab divider.
- **Logo Drop:** Soft image-only depth beneath the brand mark.

### Named Rules

**The Tonal-First Rule.** Separate ordinary content with panel tone and rule lines; reserve shadows for hierarchy that must visibly lift.

## Shapes

The form language is gently machined rather than bubbly. Fields and tags use smaller corners, controls use a medium curve, and containers use 14–16px corners. Circles are reserved for sequence numbers and progress markers. Tables and ledgers use shared outer clipping and crisp internal seams; borders stay one pixel and blue-toned.

**The Circle Means Sequence Rule.** Circular geometry belongs to numbered steps and compact markers, not to arbitrary decoration.

## Components

### Buttons

- **Shape:** Compact, confident control with a medium curve and heavy label.
- **Primary:** Safety-gold fill with midnight text and compact horizontal padding.
- **Secondary:** Registration-cyan fill with midnight text.
- **Reset:** Transparent with muted text and a one-pixel rule-blue border.
- **Hover / Focus:** Hover preserves the semantic fill; keyboard focus receives a three-pixel gold outline with a two-pixel offset.

### Tags

- **Style:** Registration-cyan fill, midnight text, heavy label, compact 8px corners; used for exact specification identifiers.
- **Status:** Gold and magenta remain content signals, not interchangeable tag themes.

### Cards / Containers

- **Corner Style:** Gently curved 14px surfaces; featured stamps may use 16px.
- **Background:** Binder-panel fill, with raised-panel headers where grouping needs emphasis.
- **Shadow Strategy:** Flat by default; binder lift only for prominent summaries and catalog cards.
- **Border:** One-pixel rule-blue dividers or shared grid seams.
- **Internal Padding:** Usually 18–24px; featured overview stamps use 28px.

### Inputs / Fields

- **Style:** Binder-panel fill, service-ink text, one-pixel rule-blue stroke, and compact 10px corners.
- **Focus:** Three-pixel safety-gold outline with a two-pixel offset.
- **Selection:** Native checkbox controls use registration cyan and remain visibly labeled.

### Navigation

The physical-divider tab rail is sticky, horizontally scrollable, heavy-weight, and muted at rest. Hover raises the label to service ink. The active tab gains a raised-panel fill and a three-pixel cyan inset registration line; arrow, Home, and End keys move focus between tabs.

### Process Ledger

Sequential process items share a binder-panel sheet and rule-blue seams. Cyan labels identify the stage; muted supporting text describes the gate. Runbook steps use circular cyan counters, a main instruction column, and a compact gold effort/status label.

### Release Gate

The QA release gate pairs a large gold completion percentage with a coral not-ready verdict. Only 100% completion changes the verdict to the established success green; visual readiness never bypasses responsible approval.

## Do's and Don'ts

### Do:

- **Do** keep new commercial-guide surfaces Arabic-first, RTL, keyboard navigable, responsive, and printable.
- **Do** use safety gold for decisive action and approval, registration cyan for technical position, and coral for failure.
- **Do** favor tables, ledgers, checklists, process rails, and exact labels when expressing operational truth.
- **Do** preserve the 1440px frame, fluid gutters, and predictable 900px and 620px responsive reductions.
- **Do** honor reduced-motion preference by removing panel entrance animation.

### Don't:

- **Don't** apply this document to the Android game's gameplay visuals or asset contracts; its scope is the `commercial-guide` web surface.
- **Don't** turn the guide into a generic marketing-card dashboard or add ornamental gradients and shadows without an operational role.
- **Don't** use magenta as a routine action color or let gold, cyan, and coral exchange semantic jobs.
- **Don't** hide required production detail to create artificial whitespace.
- **Don't** ship a dark-only print view; printed panels must flatten to white with dark text and visible rules.
