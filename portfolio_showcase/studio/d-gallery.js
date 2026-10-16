/*
 * Direction: Gallery (the first layout, developed).
 * Dark screening-room page that keeps many photos in view at once. Each
 * section picks its layout from its photos (see chooseLayout); large
 * portrait sets become a mosaic whose column count follows the screen
 * (4 desktop, 3 tablet landscape, 2 tablet portrait and phone) and whose
 * feature tiles are counted so every row ends full.
 */
(function () {
  const { el, t, isPortrait } = SC;
  const P = SC.parts;

  function chooseLayout(ms) {
    const n = ms.length;
    if (n === 1) return isPortrait(ms[0]) ? "single" : "bleed";
    if (!ms.every(isPortrait)) return "justified";
    if (n <= 3) return "row";
    if (n <= 8) return "spotlight";
    return "mosaic";
  }

  const cell = (m, cls) => el("div", { class: "g-cell" + (cls ? " " + cls : ""), style: { "--r": m.w / m.h } }, SC.img(m));

  function mosaic(ms, ctx) {
    const box = el("div", { class: "g-mosaic" });
    let lastCols = 0;
    const draw = () => {
      const w = box.clientWidth || innerWidth;
      const cols = w >= 1100 ? 4 : w >= 740 ? 3 : 2;
      if (cols === lastCols) return;
      lastCols = cols;
      // Feature tiles take 2x2 cells; pick how many so the last row is full.
      let f = 1;
      while (f < 4 && (ms.length + 3 * f) % cols !== 0) f++;
      if ((ms.length + 3 * f) % cols !== 0) f = 1;
      const at = new Set(Array.from({ length: f }, (_, i) => Math.round((i * ms.length) / f)));
      box.style.setProperty("--cols", cols);
      box.textContent = "";
      let side = 0;
      ms.forEach((m, i) => box.append(cell(m, at.has(i) ? "is-feature" + (side++ % 2 ? " is-right" : "") : "")));
    };
    const ro = new ResizeObserver(draw);
    ro.observe(box);
    ctx.cleanup(() => ro.disconnect());
    requestAnimationFrame(draw);
    return box;
  }

  function justified(ms) {
    const rows = [];
    let row = [], sum = 0;
    const target = innerWidth < 600 ? 1.6 : innerWidth < 1024 ? 2.4 : 3.2;
    ms.forEach((m) => { row.push(m); sum += m.w / m.h; if (sum >= target) { rows.push(row); row = []; sum = 0; } });
    if (row.length) rows.push(row);
    return el("div", { class: "g-just" }, rows.map((r) => el("div", { class: "g-jrow" }, r.map((m) => cell(m)))));
  }

  function chapter(ch, i, ctx) {
    const ms = ch.media.filter((m) => m.type === "photo");
    const layout = chooseLayout(ms);
    const count = el("p", { class: "g-count" }, ms.length + " " + t(ms.length === 1 ? "photo" : "photos", "صورة"));
    const head = el("header", { class: "g-ch-head" }, [P.chapterText(ch), count]);
    let body;
    if (layout === "mosaic") body = mosaic(ms, ctx);
    else if (layout === "spotlight") {
      const [lead, ...rest] = ms;
      body = el("div", { class: "g-spot" + (i % 2 ? " is-flip" : "") }, [
        el("div", { class: "g-spot-lead" }, cell(lead)),
        el("div", { class: "g-spot-grid" }, rest.map((m) => cell(m))),
      ]);
    } else if (layout === "row") body = el("div", { class: "g-row" }, ms.map((m) => cell(m)));
    else if (layout === "single") body = el("div", { class: "g-single" }, cell(ms[0]));
    else if (layout === "bleed") body = el("div", { class: "g-bleed" }, cell(ms[0]));
    else body = justified(ms);
    return el("section", { class: "g-ch g-ch--" + layout }, [head, body]);
  }

  function render(d, root, ctx) {
    root.append(
      el("header", { class: "g-hero" }, [
        el("div", { class: "g-hero-text" }, [
          el("p", { class: "g-eyebrow" }, [d.sector[0], d.year].filter(Boolean).join(" · ")),
          el("h1", { class: "g-title" }, d.title),
          P.headline(d, 0),
          P.deliverables(d),
          P.facts(d),
        ]),
        d.cover ? el("div", { class: "g-hero-media" }, cell(d.cover)) : null,
      ])
    );
    const results = P.results(d);
    if (results) root.append(results);
    const story = P.story(d), intro = P.intro(d), journey = P.journey(d);
    if (story || intro || journey) root.append(el("section", { class: "g-about" }, [story || intro, journey]));

    let i = 0;
    d.chapters.forEach((ch) => {
      if (ch.kind === "gallery") root.append(chapter(ch, i++, ctx));
      else if (ch.kind === "motion") root.append(el("section", { class: "g-ch g-motion" }, [
        el("h2", { class: "p-ch-title" }, t("In motion", "بالفيديو")),
        el("div", { class: "g-films" }, ch.media.map((m) => el("figure", {}, [SC.video(m), el("figcaption", {}, m.caption)]))),
      ]));
      else if (ch.kind === "compare") root.append(el("section", { class: "g-ch" }, [P.chapterText(ch), el("div", { class: "g-row" }, ch.media.map((m) => cell(m)))]));
    });

    if (d.grid) {
      root.append(el("section", { class: "g-social" }, [
        el("header", { class: "g-ch-head" }, [
          el("div", { class: "p-ch-text" }, [
            el("h2", { class: "p-ch-title" }, t("Live on Instagram", "منشور على انستجرام")),
            el("p", {}, t("The campaign was designed as a grid: three posts that read as one image on the profile.", "الحملة اتصممت كجريد: ٣ بوستات بيبانوا صورة واحدة على البروفايل.")),
          ]),
        ]),
        el("div", { class: "g-social-body" }, [
          el("div", { class: "g-panos" }, [P.panorama(d, 0), P.panorama(d, 1)]),
          P.profile(d),
        ]),
      ]));
    }
    const quote = P.quote(d);
    if (quote) root.append(quote);
    root.append(el("footer", { class: "g-end" }, [P.crew(d), P.cta(d)]));
  }

  SC.direction("gallery", { label: ["Gallery", "معرض صور"], render });
})();
