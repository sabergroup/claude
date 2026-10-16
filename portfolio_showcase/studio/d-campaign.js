/*
 * Direction: Campaign.
 * Built like an ad campaign: heavy condensed type, black, white and brand
 * red. Photos sit in black and white and turn to colour as they reach the
 * middle of the screen, the way the gold is the only colour in the grid
 * design. On wide screens the text column stays pinned while photos scroll
 * beside it in pairs; on phones and tablets in portrait it stacks.
 */
(function () {
  const { el, t, pad } = SC;
  const P = SC.parts;

  function colourOnView(nodes, ctx) {
    const io = new IntersectionObserver((es) => es.forEach((e) => e.target.classList.toggle("is-colour", e.isIntersecting)),
      { rootMargin: "-35% 0px -35% 0px" });
    nodes.forEach((n) => io.observe(n));
    ctx.cleanup(() => io.disconnect());
  }

  // Pairs side by side with every third row a single full-width frame.
  function stack(photos) {
    const rows = [];
    let i = 0, r = 0;
    while (i < photos.length) {
      const take = (r % 3 === 2 || photos.length - i === 1) ? 1 : 2;
      rows.push(el("div", { class: "k-row k-row--" + take }, photos.slice(i, i + take).map((m) =>
        el("figure", { class: "k-shot" }, [SC.img(m), el("figcaption", { dir: "ltr" }, pad(m.plate))]))));
      i += take; r++;
    }
    return rows;
  }

  function render(d, root, ctx) {
    const head = d.headlines[0] || d.title;
    root.append(el("header", { class: "k-hero" }, [
      el("div", { class: "k-hero-media" }, d.cover ? SC.img(d.cover, { loading: "eager" }) : null),
      el("h1", { class: "k-vertical" }, head),
      el("div", { class: "k-hero-text" }, [
        el("p", { class: "k-kicker" }, [d.client && d.client.name, d.sector[0], d.year].filter(Boolean).join(" / ")),
        el("p", { class: "k-title" }, d.title),
        P.deliverables(d),
      ]),
    ]));

    const results = P.results(d, { cls: "k-results" });
    if (results) root.append(results);

    let n = 0;
    d.chapters.forEach((ch) => {
      const photos = ch.media.filter((m) => m.type === "photo");
      if (!photos.length) {
        if (ch.kind === "motion") root.append(el("section", { class: "k-films" }, ch.media.map((m) => SC.video(m))));
        return;
      }
      n++;
      const side = el("aside", { class: "k-side" }, [
        el("p", { class: "k-num", dir: "ltr" }, pad(n)),
        P.chapterText(ch),
        n === 1 ? P.story(d) : null,
        n === 1 ? P.journey(d) : null,
      ]);
      const rows = stack(photos);
      root.append(el("section", { class: "k-split" }, [side, el("div", { class: "k-photos" }, rows)]));
      colourOnView(rows.flatMap((r) => [...r.children]), ctx);
    });

    if (d.grid) {
      const panos = d.grid.panoramas.map((m, i) => el("figure", { class: "k-pano" }, [
        SC.img(m),
        d.headlines[i + 1] ? el("figcaption", {}, d.headlines[i + 1]) : null,
      ]));
      root.append(el("section", { class: "k-social" }, [
        el("h2", { class: "k-big" }, t("One grid. One image.", "جريد واحد. صورة واحدة.")),
        ...panos,
        el("div", { class: "k-social-row" }, [
          el("p", { class: "k-social-text" }, t("Three posts that read as one frame on the profile, in colour and in black and white.", "٣ بوستات بيبانوا كادر واحد على البروفايل، بالألوان وبالأبيض والأسود.")),
          P.profile(d),
        ]),
      ]));
      colourOnView(panos, ctx);
    }
    const quote = P.quote(d);
    root.append(el("footer", { class: "k-end" }, [quote, P.crew(d), P.cta(d, t("Next campaign: yours.", "الحملة الجاية: بتاعتك."))]));
  }

  SC.direction("campaign", { label: ["Campaign", "حملة"], render });
})();
