<inputs>
Ask me for anything below I haven't given you. If I skip it, use the default: the reel (1080x1920, its own frame rate, her original audio) and its words.json (faster-whisper word timestamps); shot type (wide = legs visible, close); the folder's caption colors (default: cream #F6EAD6, gold #F0C98A, soft brown shadow rgb(74,42,20)); sounds from `sfx_library/saber_v2` (default: soft reveal/1 for the reveal, one pop for the landing).
</inputs>

<direction>
An animated name intro for Dr. Marwa Magdy's Instagram reel. It plays over her footage during the first ~6 seconds while she is already talking: it is not a title card, not a hook and not a separate opening; the video starts on her first word.
The name is exactly DR. MARWA MAGDY: no title, no specialty, no icon. Font: Montserrat for the name (Montserrat SemiBold for MARWA MAGDY, Montserrat Medium for DR.), uppercase with wide letter spacing, cream, final size 36 px (never smaller at any frame), sitting under the caption between two thin gold lines, centered. Wide shot: on her lap, captions above it. Close shot: under the captions, never below 1450 px.
Through-line object: one gold point. It appears from the caption's baseline on her first word, stretches into a thin gold line, the line splits into the two dividers, and the dividers open the space where the name is revealed. At the end the two dividers close back into the point, which settles into the caption's baseline and disappears there. Name it before you storyboard.
The name is revealed, never faded in from nothing: a mask opens from the center outward between the dividers while the letter spacing tightens from wide to its final value with a spring. Each word (DR. / MARWA / MAGDY) has its own timing so letters never overlap.
One accent: gold only on the point and the dividers. Lots of empty space. Calm, elegant, feminine.
Motion rules: springs with at most a small overshoot; nothing appears from nothing (it grows, unfolds or is revealed by a mask); no camera moves of our own on Saber's edit (only the existing slow breathing zoom); something changes with each of her stressed words during the intro.
Banned: particle bursts, glows, halos, boxes or gradients behind the name, stroke around letters, italic, emoji, phone icon, pure white, yellow, lens flares, camera shake, RGB split, crossfades, motion blur or blending two frames, bouncy easing, music, any edit to her voice, anything that looks like a template.
</direction>

<timing>
Her speech is the clock, not a beat grid.
0: the point appears 2–3 frames before her first word.
First word: the point stretches into a line.
Second stressed word: the line splits into the two dividers and the mask opens: DR. then MARWA then MAGDY, each on its own word onset or within 0.15 s of it.
Hold readable until ~5.5 s, never shorter than 3 s fully readable.
Exit in her first pause after ~5.5 s: the mask closes toward the center, the dividers close into the point, the point drops into the caption baseline.
The Saber Group credit sits bottom center for the first 5 s; the name must never overlap it.
</timing>

<build>
1. One HTML file at 1080x1920. Every style is computed from time inside window.seek(t): no CSS animations, no transitions, no timers, no state carried between frames.
2. Springs and exponential easing written as closed-form functions of time; a value that changes target several times is the sum of one spring per change. No motion blur.
3. Measure the caption baseline and the name's width at runtime; never hard-code them.
4. Render with Playwright on a transparent background, one frame per video frame (the reel's own fps, no subframes, no tmix), PNG sequence.
5. Composite over the reel with ffmpeg. Her voice is copied untouched; sounds from saber_v2 are mixed about 6 dB under her voice, each placed on its measured peak at the moment it belongs to.
6. Before the full render, render one still per stage (point, line, split, DR., MARWA, MAGDY, hold, exit) and check readability, size 36, position on her lap and no overlap with the captions or the credit.
</build>

<gotchas>
Never put will-change on anything that scales or the text renders blurry. Montserrat letter spacing changes the measured width, so measure at the final spacing for the divider length. Keep the name at 36 px from its first visible frame; only spacing and the mask animate. The point must leave from the exact caption baseline it came from.
</gotchas>

<start>
Ask for missing inputs, show the through-line object and the word-anchored storyboard with stills, then build it.
</start>
