<inputs>
Use what is already in the session; ask me nothing. You have the reel (1080x1920, its own frame rate, usually 25 fps), her original audio, words.json (faster-whisper word timestamps, corrected), the shot list with the lap position of each shot, and the folder's palette from SKILL.md.
The moments to animate are every place where she counts (١ / ٢ / ٣), lists, compares two things, or gives steps. Find them yourself by listening: one insert (ball + cards) for the single most important part, and an on-lap device for each of the other moments.
Sounds come only from `sfx_library/saber_v2`, about 6 dB under her voice. Her voice is never touched.
</inputs>

<direction>
Calm, elegant, feminine kinetic typography that sits on her lap, not a template. The number is always beside its words, on the right (Arabic is RTL), never under them. Each moment gets the device that fits what she says, and the devices vary across a video:
- **Split screen** (`split`): she names two things and then a third. ١ and its words on the right half, ٢ and its words on the left half; on the first word of the third item the two halves close to the middle on different springs, the numbers flip up and ٣ arrives, and the two rings become one. Item ٣'s title stays, and each example she names appears under it, one at a time, with a gold line drawing under each example.
- **Counter** (`counter`): one ring with the number beside the words. The number flips ١ → ٢ → ٣ on the onset of each item. The ring slides as the text width changes, and the item's words swap.
- **Pair** (`pair`): two stacked rows, each with its own ring and number beside its words (for example, find the cause → the right plan).
- **Title and traits** (`cmp`): a title (one or more that flip in turn) with its traits building under it, separated by gold dots (for example, dandruff: oily ← dry; drug treatment ← sessions: PRP · stem cells).
Ring: gold #F0C98A stroke 3, radius 40, drawn clockwise from the top by a spring. The number sits inside it: Alexandria 800, gold. Words: Alexandria; cream #F6EAD6 with key words in gold, or the folder's own caption colors. Soft shadow only.
Banned: boxes, halos or gradients behind text; stroke around letters; italic; emoji; bouncy easing; particle bursts; glows; motion blur or blending two frames; punch-in zooms; icons on her body or the backdrop in a wide shot.
</direction>

<timing>
Her speech is the clock.
- Every word of the moment appears on its own onset, rising from under the baseline (masked, 3 frames before the word). Nothing is distributed on a grid, and no line is written faster than she says it.
- The device shows ALL her words in that part, not only the key words. Captions pause while a device is on; the device itself is the caption.
- A number flips exactly on the onset of its item. The words of the current item stay at least 0.8 s after their last word before the next item replaces them.
- The last word of the whole device stays at least 1 s after it is said. The device exits at max(start of the next sentence, last word + 1 s), and the caption after it waits.
- A device or the insert waits for the caption before it: it starts only after that caption's last word has been on screen for at least 0.8 s. Never cut a caption to make room.
- A different sound for each number and for the merge, chosen by what she says, e.g. ١ pop/1, ٢ Hint/solid, merge whoosh/light, ٣ Hint/simble notification. Never two similar sounds in a row.
</timing>

<layout>
- Wide shot: the device sits centered on her lap, at the same place as the captions (top of the lap, under her hands). It never goes on her body above that, and has no icons.
- Close shot (desk): bottom third, never lower than 1450 px.
- The name block and the Saber Group credit (first 5 s, bottom center) are never covered.
</layout>

<build>
1. Use `.claude/skills/montage/templates/reel_overlay.html`: `split` / `devices` (`counter`, `pair`, `cmp`) in data.json. Read `templates/reel_overlay.example.json` and `scripts/build_example.py` (folder 3) for exact data shapes.
2. Every style is computed from time inside seek(t): closed-form springs, a sum of springs for values that change target; no CSS transitions, no timers, no state between frames.
3. Before rendering, run `scripts/audit.js`. It lists every word (captions + devices + insert) that stays under 0.8 s, and every last word of a device that stays under 1 s. Render only when that list is empty.
4. Render one still per number flip, merge and exit, and check that no Arabic letter is clipped (masks padded 12 px above and 28 px below) and nothing touches her body.
5. Render at the source fps on 4 cores; composite with `scripts/composite.py` (slow breathing zoom only); mix with `scripts/mixsfx.py`; add the credit with `sg_intro.py`, which keeps the fps.
6. For a fix in one place, re-render only that segment (SKILL.md: «التعديلات الصغيرة», `segfix.py`), never the whole video.
</build>
