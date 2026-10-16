/*
 * Direction: Bento.
 * The whole project as one tiled board: title, numbers, brief, scope,
 * photos, the Instagram grid and the crew share a single grid, so a lot is
 * visible at once. Row height is 0.625 x column width, which makes a 1x2
 * tile exactly 4:5 (the Instagram post ratio). Columns: 6 desktop and
 * tablet landscape, 4 tablet portrait, 2 phone; wide tiles clamp to fit.
 */
(function () {
  const { el, t } = SC;
  const P = SC.parts;

  const tile = (span, cls, kids) => el("div", { class: "b-tile " + span + (cls ? " " + cls : "") }, kids);

  function render(d, root, ctx) {
    const photos = P.photos(d);
    const board = el("div", { class: "b-board" });
    const tiles = [];

    tiles.push(tile("w4 h3", "b-title", [
      el("p", { class: "b-eyebrow" }, [d.client && d.client.name, d.sector[0], d.year].filter(Boolean).join(" · ")),
      el("h1", {}, d.title),
      P.headline(d, 0),
    ]));
    if (d.cover) tiles.push(tile("w2 h4", "b-photo", SC.img(d.cover, { loading: "eager" })));
    if (d.results) d.results.items.forEach((r, i) => tiles.push(tile("w1 h2", "b-stat", [
      el("strong", { dir: "ltr" }, r.value), el("span", {}, r.label),
      i === 0 && d.results.example ? SC.exampleTag() : null,
    ])));
    const del = P.deliverables(d);
    if (del) tiles.push(tile("w2 h2", "b-deliv", [el("h2", { class: "p-label" }, t("Delivered", "اتسلّم")), del]));
    if (d.story) {
      if (d.story.goal) tiles.push(tile("w3 h3", "b-text", [el("h2", { class: "p-label" }, [t("The brief", "المطلوب"), d.story.goalExample ? SC.exampleTag() : null]), el("p", {}, d.story.goal)]));
      if (d.story.idea) tiles.push(tile("w3 h3", "b-text b-accent", [el("h2", { class: "p-label" }, [t("The idea", "الفكرة"), d.story.ideaExample ? SC.exampleTag() : null]), el("p", {}, d.story.idea)]));
    } else if (P.intro(d)) tiles.push(tile("w4 h3", "b-text", P.intro(d)));
    const journey = P.journey(d);
    if (journey) tiles.push(tile("w2 h4", "b-journey", journey));

    photos.forEach((m, i) => {
      const feature = i % 7 === 0;
      tiles.push(tile(feature ? "w2 h4" : "w1 h2", "b-photo", SC.img(m)));
      if (i === 5 && d.grid && d.grid.panoramas[0]) tiles.push(tile("w6 h4", "b-pano", P.panorama(d, 0)));
    });
    d.chapters.filter((c) => c.kind === "motion").forEach((c) => c.media.forEach((m) => tiles.push(tile("w2 h4", "b-video", SC.video(m)))));
    if (d.grid) {
      tiles.push(tile("w2 h6", "b-profile", P.profile(d)));
      if (d.grid.panoramas[1]) tiles.push(tile("w4 h4", "b-pano", P.panorama(d, 1)));
    }
    const quote = P.quote(d);
    if (quote) tiles.push(tile("w3 h3", "b-quote", quote));
    const crew = P.crew(d);
    if (crew) tiles.push(tile("w3 h3", "b-crew", crew));
    tiles.push(tile("w6 h3", "b-cta", P.cta(d)));
    board.append(...tiles);
    root.append(board);

    // Keep rows at 0.625 of a column so 1x2 tiles stay exactly 4:5.
    const size = () => {
      const cs = getComputedStyle(board);
      const cols = cs.gridTemplateColumns.split(" ").length;
      const gap = parseFloat(cs.columnGap) || 0;
      const colW = (board.clientWidth - gap * (cols - 1)) / cols;
      board.style.setProperty("--row", Math.max(40, colW * 0.625 - gap / 2) + "px");
    };
    const ro = new ResizeObserver(size);
    ro.observe(board);
    ctx.cleanup(() => ro.disconnect());
  }

  SC.direction("bento", { label: ["Bento", "بينتو"], render });
})();
