---
name: "Family Force: Neon Streets — Android Game UI"
description: "A joyful midnight transit-route arcade board that makes every controller-driven choice read as a journey."
colors:
  enamel-navy: "#091330"
  deep-midnight: "#071026"
  raised-navy: "#192246"
  porcelain: "#ffffff"
  muted-porcelain: "#b6d3dd"
  transit-rule: "#43567a"
  coral-line: "#ff535c"
  cyan-line: "#5390ff"
  mint-line: "#3fddac"
  gold-line: "#ffc041"
  electric-lime: "#d9ff55"
  ready-green: "#50dc87"
typography:
  display:
    fontFamily: "Android system sans-serif"
    fontSize: "19–34 canvas px"
    fontWeight: 700
  title:
    fontFamily: "Android system sans-serif"
    fontSize: "13–18 canvas px"
    fontWeight: 700
  label:
    fontFamily: "Android system sans-serif"
    fontSize: "7–12 canvas px"
    fontWeight: 700
rounded:
  status: "8 canvas px"
  button: "9–12 canvas px"
  card: "14 canvas px"
  feature: "16 canvas px"
  title-frame: "20 canvas px"
spacing:
  micro: "4 canvas px"
  xs: "8 canvas px"
  sm: "12 canvas px"
  md: "16 canvas px"
  lg: "24 canvas px"
  gutter: "28 canvas px"
components:
  menu-station-active:
    backgroundColor: "{colors.raised-navy}"
    textColor: "{colors.porcelain}"
    typography: "{typography.title}"
    rounded: "{rounded.button}"
  destination-board:
    backgroundColor: "{colors.enamel-navy}"
    textColor: "{colors.porcelain}"
    rounded: "{rounded.feature}"
  hero-card:
    backgroundColor: "{colors.enamel-navy}"
    textColor: "{colors.porcelain}"
    rounded: "{rounded.card}"
  depart-button:
    backgroundColor: "{colors.electric-lime}"
    textColor: "{colors.deep-midnight}"
    typography: "{typography.title}"
    rounded: "{rounded.button}"
---

# Design System: Family Force: Neon Streets — Android Game UI

## Overview

**Creative North Star: "The Midnight Family Metro"**

This document applies only to the native Android game rendered by `app/src/main/java/com/familyforce/neonstreets/GameView.java`. The root `DESIGN.md` remains the separate source of truth for the commercial-guide web surface.

The game UI is a joyful midnight transit mural adapted to an arcade cabinet. Choices are stations on one connected network, not a stack of unrelated app cards. Enamel-dark surfaces carry porcelain labels and luminous coral, cyan, mint, gold, and lime signals. The final reviewer disposition for this direction is **PASS**.

**Key Characteristics:**

- A continuous station list anchors the main menu, with the selected route feeding a destination board.
- Route geometry is disciplined: horizontal, vertical, and 45-degree segments only.
- Character setup reads as one journey: **P1 → LINK → P2 → LINK → GO**.
- High-contrast labels, persistent command hints, and explicit ready states prioritize controller clarity.
- The canonical design space is a compact 640 × 360 landscape canvas.

## Colors

The palette resembles colored enamel lines and illuminated station markers over a midnight transit board.

### Primary

- **Electric Lime** (`#d9ff55`): Primary confirmation, P1 selection, moving route beacon, ready emphasis, and unlocked departure.
- **Coral Line** (`#ff535c`): One-player route, final GO station, urgent actions, and the warm end of the journey.

### Secondary

- **Cyan Line** (`#5390ff`): Two-player route and the second LINK stop.
- **Mint Line** (`#3fddac`): Training route and the first LINK stop.
- **Gold Line** (`#ffc041`): Settings route and P2 identity/selection.

### Neutral

- **Enamel Navy** (`#091330`): Default menu, card, and board surface.
- **Deep Midnight** (`#071026`): Station centers and dark text on luminous controls.
- **Raised Navy** (`#192246`): Selected card fill and stronger local grouping.
- **Porcelain** (`#ffffff`): Primary labels and headings.
- **Muted Porcelain** (`#b6d3dd`): Subtitles, instructions, and supporting labels.
- **Transit Rule** (`#43567a`): Inactive tracks, dividers, and quiet structure.
- **Ready Green** (`#50dc87`): Confirmed-ready status only.

### Named Rules

**The Colored-Line Rule.** A route color identifies a destination or journey position; it does not become a decorative wash across unrelated surfaces.

**The Lime Means Proceed Rule.** Electric lime signals focus, confirmation, or permission to advance. Ready green is reserved for the completed ready state.

## Typography

**Display Font:** Android system sans-serif, bold  
**Body Font:** Android system sans-serif  
**Label Font:** Android system sans-serif, bold

**Character:** Compact, sturdy, all-caps arcade labeling behaves like station signage. Hierarchy comes from size, weight, color, and position rather than multiple font families.

### Hierarchy

- **Display:** 19–34 canvas px, bold; title moments and major state announcements.
- **Title:** 13–18 canvas px, bold; route names, hero names, menu destinations, and action buttons.
- **Label:** 7–12 canvas px, predominantly bold; instructions, roles, station labels, statistics, and controller legends.
- **Supporting text:** 9–13 canvas px, regular or bold as implemented; concise descriptions only.

### Named Rules

**The Cabinet-Distance Rule.** Critical labels stay bold and high-contrast because the game must remain readable from controller distance, not only at phone-reading distance.

## Layout

The UI is authored in a 640 × 360 landscape coordinate system. Headings and a thin rule establish the top band; the main content occupies the middle; persistent controller instructions sit along the bottom edge.

The main menu is one continuous route assembly. A 290 × 230 canvas-pixel station panel sits left, with four 53-pixel-high rows connected by a vertical trunk and horizontal tracks. A 273 × 230 destination board sits right and changes with the active station. The two halves animate inward as a paired composition.

Character selection uses four evenly spaced hero cards across the upper field, a five-stop route across the middle, two player boards below it, and one terminal departure control. Preserve the reading order **P1 → LINK → P2 → LINK → GO**, even when P2 is disabled; disabled stops may quiet down, but the journey must remain legible.

Route segments must follow 45-degree or 90-degree geometry. Avoid loose curves, arbitrary diagonals, and disconnected markers. Keep important content inside the established 24–28 canvas-pixel outer gutters and retain the bottom controller legend.

## Elevation & Depth

Depth is primarily tonal and state-driven. Opaque and translucent navy layers distinguish the backdrop, station panel, cards, and destination board. Selected states gain luminous strokes, local glow, or an animated route beacon; ordinary surfaces remain flat. Do not introduce generic drop-shadow cards into this world.

## Shapes

The system combines rounded enamel boards with precise transit geometry. Standard cards use 14 canvas-pixel corners, feature boards use 16, buttons use 9–12, and the title frame may use 20. Station rings are circular with dark centers; route tracks have round caps where animated, while structural dividers remain crisp.

Selection is shown with a 3–6 canvas-pixel colored outline, not by changing the entire composition. Circles carry a functional meaning: station, player marker, selection check, or route position.

## Components

### Main Menu Station List

- **Structure:** Four continuous route rows—1 Player, 2 Players, Training, Settings—share one vertical trunk.
- **State:** The active row gains a colored outline, larger station ring, brighter local panel, and matching destination-board stroke.
- **Continuity:** Tracks visibly pass through the list so each option belongs to the same map.
- **Destination board:** Shows the selected route name, party/configuration promise, miniature route, and best-run status.

### Transit Routes

- **Track:** Six canvas pixels for the destination map and four for the selection journey.
- **Stations:** Bright outer rings with deep-midnight centers.
- **Motion:** A lime beacon traces the route on entry; reduced-motion mode resolves to a stable state without losing information.
- **Geometry:** Use only horizontal, vertical, and 45-degree connections.

### Hero Cards

- **Shape:** 140 × 175 canvas pixels with 14-pixel corners.
- **Content:** Portrait, colored identity rule, hero name, role, and compact power/speed bars.
- **Selected:** Hero-color stroke and glow, lime check, explicit P1/P2 badge, and strong active-slot outline.
- **Clarity:** Color supports identity; names and player badges carry the meaning independently.

### Player Boards and Departure

- **Boards:** Dark enamel panels with a colored player medallion, hero name, LINK companion, and full-width ready instruction/status strip.
- **Disabled P2:** Remains visible as optional and explains how to enable it.
- **Ready:** Uses ready green and the explicit copy `READY — PRESS AGAIN TO DEPART`.
- **Departure:** Stays muted until required riders are ready, then becomes electric lime with `DEPART` and `TEAM LOCKED` confirmation.

### Controller Guidance

Every choice screen exposes its relevant physical commands in plain language. The main menu keeps `D-PAD NAVIGATE`, `A / OK SELECT`, and `B / BACK RETURN` visible; selection repeats the LINK and ready controls inside each player board. Visual focus, player ownership, enabled state, and action result must never rely on color alone.

## Do's and Don'ts

### Do:

- **Do** extend menus as connected station networks with a clearly highlighted active journey.
- **Do** preserve enamel navy, porcelain labels, and the established coral/cyan/mint/gold/lime signal roles.
- **Do** keep controller instructions persistent, specific, and close to the state they affect.
- **Do** label player ownership, optional/disabled state, readiness, and departure eligibility explicitly.
- **Do** honor reduced-motion settings while preserving every route and focus cue in a static form.

### Don't:

- **Don't** replace the main menu with detached generic cards, tiles, or a conventional mobile settings list.
- **Don't** draw transit paths with undisciplined angles, curves, or ornamental branches.
- **Don't** skip or reorder the selection journey **P1 → LINK → P2 → LINK → GO**.
- **Don't** use glow, color, or animation as the only indication of focus or readiness.
- **Don't** apply this Android game system to the commercial-guide web surface; follow the root `DESIGN.md` there.
