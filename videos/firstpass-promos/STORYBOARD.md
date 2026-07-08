---
format: 1920x1080
message: "Every contract gets an AI first pass. A human confirms. The queue gets shorter every month."
arc: Demo Loop — question → product intro → demo cycle 1 → demo cycle 2 → trust → CTA
audience: PortSwigger hiring panel — technical, product-minded, security-conscious
---

## Video direction

- **palette** — `frame.md` broadside preset: `ink-black` (#15171C) canvas, `fire-orange` (#E14E12) sole accent, `cream` (#FFFFFF) text on dark canvas. Cards tint with `cream-muted` (#FF6633). Type ramp by role: h1/h2 for display, body/lead for prose, label (IBM Plex Mono uppercase) for chrome.
- **motion grammar** — long-tail `power3` default (smooth over bouncy). VO-paced reveal model: each piece enters when the voiceover names it, never front-loaded. Held frames use subtle jitter (`sine-wave-loop`, low amplitude) only — no lazy breathing, no back-half pan/push.
- **rhythm** — most frames reveal to the VO across their duration. Frame 8 (Privacy) is a deliberate held breather before the close. Frame 9 (Close) is the climax with push-through exit.
- **negative list** — no bouncy/elastic/back.out entrances. No front-load-then-freeze (slideshow). No floating independent elements (screensaver). No browser chrome, scrollbars, or generic AI gradients. No `repeat`/`yoyo`, no `Math.random`/`Date.now`. Seek-safe: all motion inside paused GSAP timeline, entrances use `fromTo`.

---

## Frame 1 — Hook

- scene: Bold stat punches onto a bare dark canvas, one phrase at a time
- voiceover: "Eighty percent of a contract is boilerplate. Agreed a hundred times before. Yet every single one still gets a full cold read — by a scarce, expensive human."
- duration: 5s
- transition_in: cut
- status: animated
- src: compositions/frames/01-hook.html
- type: hook
- persuasion: Pain agitation
- beat: tension + curiosity
- blueprint: kinetic-type-beats (Reproduce)
- focal:
- roles:
- sfx: impact-soft

Reproduce: the hook maps cleanly — three escalating statements, each its own beat, landing the punchline. Signature move: in-place word-swap on hard cut.

Scene 1 (0.0–1.6s): solid ink-black canvas. "80% of a contract is boilerplate." — h1 in cream, dead-center, springs in via spring-pop-entrance on power3 settle. Held still.
Scene 2 (1.6–3.2s): the first line fades down. "Agreed a hundred times before." hard-cuts in at the same position via discrete-text-sequence. The swap IS the beat — no roll, no fade.
Scene 3 (3.2–5.0s): both lines clear. "Yet every single one still gets a full cold read — by a scarce, expensive human." — h2 in cream, lower-third, reveals word-by-word via per-word staggered reveal (dynamic-content-sequencing) on power3, each chunk landing on its own beat. Final phrase "scarce, expensive human" gets a fire-orange keyword glow (asr-keyword-glow). Hold still to read. Subtle jitter only (sine-wave-loop, low amp).

---

## Frame 2 — The Queue

- scene: The pressure builds: end-of-quarter, sales waiting, queue backing up
- voiceover: "End of quarter, the sales team is waiting. The queue is longer than the day. And there is no way to tell the safe contracts from the risky ones — not until someone reads every single page."
- duration: 6s
- transition_in: crossfade
- status: animated
- src: compositions/frames/02-problem.html
- type: pain_point
- persuasion: Pain agitation + urgency
- beat: frustration + overwhelm
- blueprint: overwhelm-surround (Adapt)
- focal:
- roles:
- sfx: riser

Adapt: keep the accumulation structure and the closing-in mechanic; swap the tool-surround for text phrases that pile in from all sides. Signature move: elements accumulate then close in from all edges — the claustrophobic crowd.

Scene 1 (0.0–2.0s): ink-black canvas. "End of quarter." — h2 in cream, dead-center, enters via spring-pop-entrance on power3. Below it, "the sales team is waiting." — body text fades in. Slow push on root (multi-phase-camera) starts.
Scene 2 (2.0–4.0s): "The queue is longer than the day." — h3, upper-right, enters via per-word staggered reveal. "No way to tell safe from risky." — h3, lower-left, enters same way. Elements accumulate at diagonal positions — the spread implies overwhelm.
Scene 3 (4.0–6.0s): all text elements begin a slow drift inward via center-outward-expansion reversed (inward collapse). Camera push intensifies. "Not until someone reads every single page." — body text, center, fire-orange, reveals word-by-word and holds. The frame ends in a tight cluster — visually claustrophobic. Hold with subtle jitter.

---

## Frame 3 — Product Intro

- scene: Hard cut. The FirstPass name drops in bold, center-frame. Tagline assembles beneath.
- voiceover: "Introducing FirstPass. An AI triage layer that reads every contract, checks it against your team's own playbook, and routes it — before a lawyer ever opens the file."
- duration: 5s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/03-intro.html
- type: product_intro
- persuasion: Category announcement
- beat: curiosity + relief
- blueprint: kinetic-type-beats (Reproduce)
- focal:
- roles:
- sfx: impact-soft, whoosh

Reproduce: classic "Introducing…" name-drop pattern. Signature move: hard-cut through beats to resolve on the brand name.

Scene 1 (0.0–1.2s): "Introducing" — label (IBM Plex Mono, uppercase, fire-orange, 0.14em tracking), dead-center, springs in via spring-pop-entrance on power3 settle, then fades down.
Scene 2 (1.2–2.8s): "FirstPass." — h1 in cream, dead-center, slams in via kinetic beat-slam (the percussive beat array). The name lands and holds. Fire-orange ambient glow blooms behind it (ambient-glow-bloom).
Scene 3 (2.8–5.0s): below the name, three capability lines reveal sequentially via per-word staggered reveal: "reads every contract" → "checks it against your playbook" → "routes it — before a lawyer opens the file." Each is body text in cream-muted, entering on its spoken cue. Hold on the full lockup. Subtle jitter on the name only.

---

## Frame 4 — The Dashboard

- scene: The web console dashboard fills the frame. GREEN/AMBER/RED pills are visible. Summary tiles show counts and hours saved.
- voiceover: "This is the queue a lawyer opens each morning. Contracts sorted by risk. Green, auto-clear. Amber, confirm — the redlines are already drafted. Red, escalate — the risky twenty percent, waiting for a human."
- duration: 8s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/04-dashboard.html
- type: feature_showcase
- persuasion: Show-don't-tell proof
- beat: clarity + control
- blueprint: device-surface-showcase (Adapt)
- focal: assets/shot_dashboard.png
- roles: shot_dashboard.png = cutout
- sfx: whoosh

Adapt: use a static tour variant — the screenshot is the hero surface, held as a floating window while callout text labels the GREEN/AMBER/RED rows. Keep the surface-as-hero structure; swap the device mockup for a clean floating window with the screenshot. Signature move: the surface cycles through interaction states — here, callouts highlight rows in sequence.

Scene 1 (0.0–1.5s): ink-black canvas. The dashboard screenshot slides in from right as a floating window (spring-pop-entrance, power3), centered, ~70% of frame width. 1px hairline border (border-dark). Slow push on root starts.
Scene 2 (1.5–4.5s): as the VO names "Green," a fire-orange outline box highlights the GREEN row on the screenshot (css-marker-patterns, hand-drawn circle feel). Callout text "AUTO-CLEAR" — label, fire-orange — appears beside it via spring-pop-entrance. Same pattern repeats for "Amber" → AMBER row highlighted, "CONFIRM" callout. Then "Red" → RED row highlighted, "ESCALATE" callout. Each reveal fires on its spoken cue.
Scene 3 (4.5–8.0s): all three callouts co-resident. Camera push settles. "The risky twenty percent, waiting for a human." — body text in cream, lower-third, reveals per-word and holds. The screenshot reads clean. Subtle jitter on the floating window.

---

## Frame 5 — Inside a Review

- scene: The detail view screenshot slides in. The AMBER banner is visible at top. Below: key terms extracted, a deviation finding with evidence and redline, and Accept/Edit/Reject buttons.
- voiceover: "Key terms already extracted. Every issue shows the evidence, the reason, and the exact redline the team has used before. The lawyer confirms. They do not start from scratch."
- duration: 8s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/05-review.html
- type: feature_showcase
- persuasion: Friction reduction + Show-don't-tell proof
- beat: confidence + ease
- blueprint: cursor-ui-demo (Adapt)
- focal: assets/shot_detail_amber.png
- roles: shot_detail_amber.png = cutout
- sfx: whoosh

Adapt: swap the reconstructed UI for the real screenshot as the surface; keep the cursor-driven walkthrough structure — a visible custom cursor moves across the screenshot, pointing at each section. Signature move: the cursor chases each interaction as the screen state is explained.

Scene 1 (0.0–1.5s): the detail-view screenshot enters from right as a floating window (spring-pop-entrance, power3), centered, ~65% of frame width, 1px hairline border.
Scene 2 (1.5–4.0s): a custom cursor (fire-orange dot + ring) sweeps in from the left and lands on the key-terms bar (cursor-click-ripple — cursor moves to target, depresses, emits ripple). "Key terms already extracted." — body text, cream, upper-right, reveals per-word on the spoken cue.
Scene 3 (4.0–6.5s): the cursor moves down to the deviation finding box and hovers. A fire-orange outline box highlights the evidence snippet (css-marker-patterns). Then the cursor slides to the redline section. "The exact redline the team has used before." — body text, cream, reveals.
Scene 4 (6.5–8.0s): the cursor lands on the green "Accept" button and a press-release-spring animation fires — the button compresses then springs back. "The lawyer confirms. They do not start from scratch." — h3 in cream, lower-third, reveals word-by-word. The button glow holds. Subtle jitter.

---

## Frame 6 — The Numbers

- scene: Dark background. Four metrics count up one by one, large and centered. Each lands with authority.
- voiceover: "Measured on a labelled set. Zero unsafe misses — nothing risky was auto-cleared. One hundred percent triage accuracy. And fifty-eight percent of review time removed. About seventy-three legal hours, returned every month."
- duration: 7s
- transition_in: blur-crossfade
- status: animated
- src: compositions/frames/06-metrics.html
- type: benefit_highlight
- persuasion: Statistical proof
- beat: trust + confidence
- blueprint: dataviz-countup (Adapt)
- focal:
- roles:
- sfx: impact-heavy, riser

Adapt: keep the count-up structure and the push-through camera; use four stat cards instead of a ring + chart. Each stat counts up on its spoken cue. Signature move: the camera pushes through to land on one hero metric.

Scene 1 (0.0–2.0s): ink-black canvas. "Measured on a labelled set." — label (IBM Plex Mono, fire-orange), top-center, fades in. Below it, the first stat card springs in: "0" in stat-value (cream, weight 900), with label "unsafe misses" in caption beneath. The "0" holds — it's the most important number. Fire-orange ambient glow behind it.
Scene 2 (2.0–3.8s): the camera begins a slow push. Second stat card: "100%" counts up via value-scaled counter (counting-dynamic-scale) — font grows with the value. "triage accuracy" beneath. Third stat card: "58%" counts up the same way. "review time removed" beneath. Cards stack vertically, each entering on its spoken cue via spring-pop-entrance staggered.
Scene 3 (3.8–7.0s): camera push intensifies through the stack toward the top stat "0" — it becomes the hero. Fourth stat card: "73h" counts up largest of all via value-scaled counter, fire-orange, and takes center. "legal hours returned every month" in body text beneath. Camera settles. The four cards hold, co-resident, with subtle jitter on the hero "0" and "73h".

---

## Frame 7 — The Flywheel

- scene: A cycle diagram unfolds: RED → lawyer resolves → playbook entry → next time AMBER → queue shorter. Clean, typographic, no screenshot needed.
- voiceover: "And here is why it compounds. When a lawyer resolves a novel RED case, it becomes a playbook entry. Next time that clause appears, it is Amber — with the redline pre-drafted. Every human decision permanently shrinks the future queue."
- duration: 7s
- transition_in: crossfade
- status: animated
- src: compositions/frames/07-flywheel.html
- type: benefit_highlight
- persuasion: Future pacing
- beat: awe + inevitability
- blueprint: kinetic-type-beats (Adapt)
- focal:
- roles:
- sfx: riser

Adapt: keep the escalating value-beat structure; swap the rapid-fire montage for a cycle that builds itself step by step. Signature move: each beat resolves on the next, building toward the defining idea.

Scene 1 (0.0–2.0s): "And here is why it compounds." — h3 in cream, center-top, springs in. Below it, the word "RED" — label, fire-orange, large — appears via spring-pop-entrance. A small arrow ("→") appears beside it (svg-path-draw, fire-orange).
Scene 2 (2.0–4.5s): "lawyer resolves" — body text in cream — reveals beside the arrow via per-word staggered reveal. Another arrow draws. "playbook entry" reveals. The chain builds left-to-right: RED → lawyer resolves → playbook entry. Each piece arrives on its spoken cue.
Scene 3 (4.5–7.0s): the chain continues: another arrow draws, "next time: AMBER" — h3 in cream-muted, with the word "AMBER" in fire-orange — reveals. "redline pre-drafted" — body text — reveals below it. Final arrow draws. "queue shorter" — h2 in cream, the defining idea, springs in via kinetic beat-slam and holds. Fire-orange glow blooms behind it. The full cycle is visible: RED → resolve → playbook → AMBER → shorter. Hold with subtle jitter on "queue shorter."

---

## Frame 8 — Private by Design

- scene: A lock icon and text: "On-prem. Local model. No cloud. No contract text ever leaves the building."
- voiceover: "And it runs entirely on your own servers. The deterministic engine needs no model at all. The reasoning layer is a local open-weight model — no contract text ever touches the cloud."
- duration: 5s
- transition_in: crossfade
- status: animated
- src: compositions/frames/08-privacy.html
- type: branding
- persuasion: Risk reversal
- beat: peace of mind + trust
- blueprint: titlecard-reveal (Reproduce)
- focal:
- roles:
- sfx:

Reproduce: one clean two-line title card, one restrained move, then held still. The breather beat. Signature move: low motion is the payload.

Scene 1 (0.0–1.5s): ink-black canvas. A simple lock SVG icon (svg-path-draw, fire-orange, self-drawing stroke-by-stroke) draws itself center-top. Below it, "On your own servers." — h2 in cream, reveals via slide-up crossfade. The single restrained move.
Scene 2 (1.5–5.0s): beneath the headline, three short lines reveal sequentially via per-word staggered reveal on their spoken cues: "The engine needs no model." → "The reasoning layer is local." → "No contract text ever touches the cloud." Each is body text in cream-muted. Once revealed, the full card holds STILL — no camera push, no breathing, no drift. At most, subtle jitter on the lock icon. The stillness IS the point — deliberate breather before the close.

---

## Frame 9 — Close

- scene: The FirstPass name centers. Tagline below. GitHub URL at the bottom. Fire-orange on black.
- voiceover: "FirstPass. Every contract gets an AI first pass. A human confirms. The queue gets shorter every month."
- duration: 5s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/09-close.html
- type: cta
- persuasion: Call to action
- beat: motivation + inevitability
- blueprint: logo-assemble-lockup (Adapt)
- focal:
- roles:
- sfx: impact-heavy

Adapt: keep the mark-build → push-through structure; use the FirstPass wordmark (no graphic logo, so the word IS the mark). Signature move: camera pushes through into the final URL.

Scene 1 (0.0–1.8s): ink-black canvas. "FirstPass" — h1 in cream, dead-center — assembles letter-by-letter via per-word staggered reveal with 3D char flip-decode feel: characters flip in and resolve from blurred to sharp. (Adapt: no graphic mark, so the wordmark assembly carries the logo-assemble weight.)
Scene 2 (1.8–3.5s): below the name, the tagline assembles word-by-word via per-word staggered reveal: "Every contract gets an AI first pass. A human confirms. The queue gets shorter every month." — body text, cream-muted, centered. Fire-orange ambient glow blooms behind the name.
Scene 3 (3.5–5.0s): camera push-through intensifies (multi-phase-camera, push phase). The tagline fades down. Only "FirstPass" remains, now larger (the push scales it). Below it, the GitHub URL — "github.com/Abdelrhman-Rayis/FirstPass" — in label (IBM Plex Mono, fire-orange) types on character-by-character via type-on with caret (discrete-text-sequence + context-sensitive-cursor). The URL holds as the final frame. The camera settles. The push-through lands on the CTA.
