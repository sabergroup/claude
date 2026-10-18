<inputs>
Ask me for: the reel (1080x1920, 30fps, her original audio), its word timestamps (words.json from faster-whisper), whether the shot is wide (legs visible) or close, and the 4 to 8 moments I want animated (counts like "1 / 2 / 3", key words, before→after, warnings, the closing call to see a dermatologist).
No music and no sound effects unless I upload them; her voice is never touched.
</inputs>

<direction>
Premium kinetic typography for a dermatologist's Instagram reel. One element, never cut: a thin gold line that morphs through every state (underline under a key word → ring around a counter → bullet rail of a list → check mark → divider lines around DR. MARWA MAGDY) while its content swaps cleanly. The speech drives every change; nothing moves that she didn't just say.
Palette only: cream #F6EAD6 for text, gold #F0C98A for key words, numbers and lines, brown rgb(74,42,20) for the soft shadow. Font: Alexandria (500 body, 800 key words and numbers, 400 for the name with wide letter spacing). Calm, elegant, feminine. Springs everywhere with a tiny overshoot at most.
Banned: bouncy easing, particle bursts, glows, halos, boxes or gradients behind text (soft shadow only), stroke around letters, italic, emoji, pure white, yellow, any color outside the palette, motion blur or blending two frames, flashy transitions, zoom punch-ins, dead time, anything that looks like a template.
</direction>

<timing>
Speech is the clock, not a beat grid.
- Every event is anchored to a word onset from words.json: an element starts 2–3 frames before the word it belongs to and settles by the end of that word.
- Measure her pace per phrase (words per second). Spring stiffness scales with it: faster phrases get snappier springs (settle ≈ 0.25 s), slower ones calmer (≈ 0.45 s). Never faster than 6 frames for any move.
- An element holds while she talks about it and leaves in the pause before the next idea, never mid-word. The last word of every line stays fully visible before it leaves.
- Counting: the number flips 1 → 2 → 3 exactly on the onset of each item, the ring draws during that item's first word, the item's title appears under it; earlier items dim but stay readable as a small list.
</timing>

<structure>
Per reel, from the moments I give you, e.g.:
hook question (gold question mark draws, key word scales in) → reassurance (line becomes a check) → explanation (line becomes a two-stop timeline that a dot travels along) → counting (line becomes the ring around a flipping counter, list builds) → warning signs (counter 1/2/3) → closing advice (line settles into the two dividers around the name).
</structure>

<layout>
- Captions word by word on one baseline, never lower than 1450 px from the top.
- Close shot: the element sits beside or above the caption block.
- Wide shot (legs visible): captions, element and name sit centered on her lap; no icons on her body and no icons scattered on the backdrop. A big counter may sit behind her (person segmentation mask, her body in front of it) only if I approve a still first.
- DR. MARWA MAGDY under the captions, size 36, between two gold lines, first ~6 seconds, never shrunk.
- Saber Group credit stays bottom center for the first 5 seconds; don't cover it.
</layout>

<build>
1. One HTML file at 1080x1920. Every style is computed from time inside seek(t): no CSS transitions, no timers, no state carried between frames.
2. Springs are closed-form step responses. A value that changes target many times is the sum of one spring per change, so it stays a pure function of time.
3. When the line morphs, its two ends ride different springs so the leading end stretches ahead of the trailing one.
4. Render with Playwright on a transparent background, one frame per video frame at 30fps (no subframes, no tmix), as a PNG sequence.
5. Composite over the reel with ffmpeg, then copy her audio stream untouched (-map 1:a -c copy) and verify it is bit-identical to the source.
6. Before the full render, render one still per animated moment. Fix anything off-sync, cramped, hard to read or touching her body.
</build>

<gotchas>
Never put will-change on anything that scales or the Arabic text renders blurry. Arabic is RTL; English terms (PRP, Biostimulators) render LTR inside the line. Text that swaps inside the morphing element needs its own enter and exit timing or it overlaps. Keep words on one baseline so no word drops below the line.
</gotchas>

<start>
Ask me for the inputs, then show me the list of animated moments on her word timeline (timestamp → word → what happens) before you write any code.
</start>
