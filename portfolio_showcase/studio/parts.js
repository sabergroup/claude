/*
 * Content blocks shared by every direction. Each returns plain semantic
 * markup with p-* classes and nothing visual; directions place the blocks
 * where they want and style them under their own .v-<name> scope.
 * A block returns null when the project has no data for it.
 */
(function () {
  const { el, t, pad } = SC;
  const P = (SC.parts = {});

  P.facts = (d) => {
    const rows = [
      d.client && [t("Client", "العميل"), d.client.name],
      d.sector.length && [t("Sector", "القطاع"), d.sector.join(", ")],
      d.location && [t("Location", "المكان"), d.location],
      d.year && [t("Year", "السنة"), String(d.year)],
    ].filter(Boolean);
    return el("dl", { class: "p-facts" }, rows.map(([k, v]) => el("div", {}, [el("dt", {}, k), el("dd", {}, v)])));
  };

  P.deliverables = (d) => d.deliverables.length ? el("ul", { class: "p-deliv" },
    d.deliverables.map(([n, label]) => el("li", {}, [el("strong", { dir: "ltr" }, n), el("span", {}, label)]))) : null;

  P.results = (d, opts) => {
    if (!d.results) return null;
    opts = opts || {};
    return el("section", { class: "p-results" + (opts.cls ? " " + opts.cls : "") }, [
      el("header", { class: "p-results-head" }, [
        el("h2", { class: "p-label" }, t("Results", "النتايج")),
        d.results.period ? el("span", { class: "p-period" }, d.results.period) : null,
        d.results.example ? SC.exampleTag() : null,
      ]),
      el("ul", { class: "p-results-list" }, d.results.items.map((r) => el("li", {}, [
        el("strong", { class: "p-num", dir: "ltr" }, r.value),
        el("span", {}, r.label),
      ]))),
    ]);
  };

  P.story = (d) => {
    if (!d.story) return null;
    const block = (label, text, ex) => text ? el("div", { class: "p-story-block" }, [
      el("h3", { class: "p-label" }, [label, ex ? SC.exampleTag() : null]),
      el("p", {}, text),
    ]) : null;
    return el("section", { class: "p-story" }, [
      block(t("The brief", "المطلوب"), d.story.goal, d.story.goalExample),
      block(t("The idea", "الفكرة"), d.story.idea, d.story.ideaExample),
    ]);
  };

  P.journey = (d) => d.journey.length > 1 ? el("section", { class: "p-journey" }, [
    el("h2", { class: "p-label" }, t("What we did", "اللي عملناه")),
    el("ol", {}, d.journey.map((s, i) => el("li", { "data-k": s.key }, [el("span", { class: "p-step", dir: "ltr" }, pad(i + 1)), el("span", {}, s.label)]))),
  ]) : null;

  P.headline = (d, i) => d.headlines[i] ? el("p", { class: "p-headline" }, d.headlines[i]) : null;

  // A phone-sized Instagram profile: the designed grid rows first, then the shoot's photos.
  P.profile = (d, opts) => {
    if (!d.grid) return null;
    opts = opts || {};
    const photos = [].concat(...d.chapters.map((c) => c.media.filter((m) => m.type === "photo")));
    const extra = photos.slice(0, opts.extraRows ? opts.extraRows * 3 : 3);
    const tiles = [].concat(...d.grid.rows, extra);
    return el("div", { class: "p-profile" }, [
      el("div", { class: "p-profile-head" }, [
        d.client && d.client.logo ? el("span", { class: "p-avatar" }, el("img", { src: d.client.logo, alt: "" })) : el("span", { class: "p-avatar" }),
        el("div", {}, [
          el("strong", {}, d.client ? d.client.name : "Saber Group"),
          el("span", {}, d.grid.platform + " · " + t("as published", "زي ما اتنشر")),
        ]),
      ]),
      el("div", { class: "p-profile-grid" }, tiles.map((m) => el("div", { class: "p-tile" }, SC.img(m)))),
    ]);
  };

  P.panorama = (d, i, cls) => {
    const m = d.grid && d.grid.panoramas[i];
    if (!m) return null;
    return el("figure", { class: "p-pano " + (cls || ""), style: { "--r": m.w / m.h } }, [
      el("div", { class: "p-pano-img" }, SC.img(m)),
      el("figcaption", {}, [
        el("span", {}, t("Instagram grid", "جريد انستجرام") + " · " + t("3 posts, one image", "٣ بوستات، صورة واحدة")),
        el("span", { class: "p-pano-cuts", "aria-hidden": "true" }),
      ]),
    ]);
  };

  P.quote = (d) => d.quote ? el("figure", { class: "p-quote" }, [
    el("blockquote", {}, d.quote.text),
    el("figcaption", {}, [d.quote.by, d.quote.example ? SC.exampleTag() : null]),
  ]) : null;

  P.crew = (d) => d.cast.length ? el("section", { class: "p-crew" }, [
    el("h2", { class: "p-label" }, t("Crew", "فريق العمل")),
    el("ul", {}, d.cast.map((c) => el("li", {}, [el("strong", {}, c.name), el("span", {}, c.role)]))),
  ]) : null;

  P.cta = (d, title) => el("section", { class: "p-cta" }, [
    el("h2", {}, title || t("Want results like these?", "عايز نتايج زي دي؟")),
    el("p", {}, t("Strategy, shoot, design, publishing and ads. One team.", "استراتيجية، تصوير، تصميم، نشر وإعلانات. فريق واحد.")),
    el("p", { class: "p-cta-actions" }, [
      el("a", { class: "p-btn", href: d.waLink, target: "_blank", rel: "noopener" }, t("Message us on WhatsApp", "كلمنا على واتساب")),
      el("span", { class: "p-phone", dir: "ltr" }, d.phone),
    ]),
  ]);

  P.intro = (d) => (d.text.lead || d.text.paras.length) ? el("div", { class: "p-intro" }, [
    d.text.lead ? el("p", { class: "p-intro-lead" }, d.text.lead) : null,
    ...d.text.paras.map((p) => el("p", {}, p)),
  ]) : null;

  P.chapterText = (ch) => el("div", { class: "p-ch-text" }, [
    ch.caption ? el("h2", { class: "p-ch-title" }, ch.caption) : null,
    ch.text.lead ? el("p", { class: "p-ch-lead" }, ch.text.lead) : null,
    ...ch.text.paras.map((p) => el("p", {}, p)),
  ]);

  P.photos = (d) => [].concat(...d.chapters.map((c) => c.media.filter((m) => m.type === "photo")));
})();
