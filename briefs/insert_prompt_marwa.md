<inputs>
Ask me for: the reel and its words.json (faster-whisper word timestamps), the stretch of speech to turn into an insert (6–10 s where she lists or compares things), the 2–4 items it shows and their icons. If I skip anything, use the dandruff reel 11.4–21.4 s: ١ دهنية (oil drop), ٢ جافة (flakes), ٣ أمراض جلدية with chips الصدفية / الحزاز.
No music and no UI sounds unless I upload them; her voice runs underneath untouched (audio stream copied, bit-identical).
</inputs>

<direction>
A full-frame 2D motion insert inside a vertical reel (1080x1920, the reel's own frame rate, 25 fps here). Her voice keeps talking; the picture cuts away to one animated world and comes back to her.
Deep brown canvas (#2E1A0D) with a faint beige dot grid, brown cards (rgb(74,42,20)) with a thin muted-gold border, cream text (#F6EAD6), one gold accent (#F0C98A) and a cream ball that travels through the whole insert. Alexandria for everything (800 for numbers and titles, 500 for chips). Gold line icons with one stroke width.
The ball opens the insert: it rises from the caption on her lap and grows into a circular reveal of the world; at the end the world shrinks back into the ball over her lap. Move the camera through one continuous layout so every item fills the frame when she says it. Small spring overshoots only.
Banned: hard cuts, dissolves or any blending of two frames, motion blur, glows, particle bursts, gradients on cards, emoji, pure white, yellow, colors outside the palette, excessive bouncing, blurry text during camera moves, captions under 1450 px, anything that looks like a template.
</direction>

<timing>
Her words are the clock, not a beat grid. Every landing, card arrival, number and chip is anchored to the onset of the word that names it (from words.json): motion starts 2–3 frames before the word and lands on it. Travel between landings fills the time between those words, so a fast phrase gives a short hop and a slow phrase a longer, calmer arc. Nothing waits on screen after she has moved on, and nothing appears before she says it.
</timing>

<structure>
Reveal: on her first listed word the ball lifts off her lap and opens the brown world.
Item 1: card ١ arrives; the ball lands on its icon on the item word, the icon fills gold, the title types in.
Item 2: the ball arcs to card ٢; the camera follows; same landing on her word.
Item 3: the camera travels down to the wide card ٣; the title appears with her words; each example she names stretches out of the card as a chip when she says it, the ball tapping each one.
Return: the camera pulls back to show all cards in one world, the ball goes back to card ١ as she says it again, and the world closes into the ball over her lap.
</structure>

<build>
1. One HTML file at 1080x1920. Every visual is computed from time inside seek(t): no CSS transitions, timers or state carried between frames.
2. All cards live in one world; a single camera transform with position and log-space zoom, summed closed-form springs per target change.
3. One continuous ball route between card icons and chips; closed-form spring landings with a brief squash on impact; never teleport.
4. The reveal and close are a circular clip mask centered on the ball, not a cross-fade.
5. Render the overlay with Playwright on a transparent background, one frame per video frame, composite with ffmpeg over the reel, copy the audio stream untouched and verify it is bit-identical.
6. Render one still per landing first and check sync, readability and that nothing sits on her body outside the insert.
</build>

<gotchas>
Arabic is RTL: item ١ sits on the right. Never put will-change on anything the camera scales. Keep chip text attached to its chip while it stretches. The ball must be where the next landing starts when the camera arrives.
</gotchas>

<start>
Ask me for the inputs, then show me the word-anchored landing map and stills before building the full insert.
</start>
