/*
 * Direction 1: Magazine.
 * A printed fashion editorial. Photos are laid out in staggered spreads on a
 * 12-column grid; each section's headline becomes a pull quote between them,
 * every photo is a numbered plate, and the crew becomes the masthead.
 */
(function () {
  const { el, t, roman, isPortrait } = SC;

  // Spread templates for portrait runs, used in rotation so no two spreads repeat.
  const TEMPLATES = [
    { take: 2, name: "a" }, // large left, small right set lower
    { take: 3, name: "b" }, // three across, middle one dropped
    { take: 1, name: "c" }, // one centred with the text beside it
    { take: 2, name: "d" }, // small left raised, large right
  ];

  function plate(m) {
    return el("figure", { class: "mg-fig" }, [
      SC.img(m),
      el("figcaption", {}, [el("span", {}, t("Plate ", "لوحة ") + m.plate), m.caption ? " — " + m.caption : ""]),
    ]);
  }

  function spreads(photos, text, startAt) {
    const out = [];
    let i = 0, k = startAt;
    let textUsed = false;
    while (i < photos.length) {
      if (!isPortrait(photos[i])) {
        out.push(el("div", { class: "mg-spread mg-spread--full" }, plate(photos[i])));
        i++; continue;
      }
      let tpl = TEMPLATES[k % TEMPLATES.length];
      const left = photos.length - i;
      if (tpl.take > left) tpl = left === 1 ? TEMPLATES[2] : left === 2 ? TEMPLATES[0] : tpl;
      const group = photos.slice(i, i + tpl.take);
      const kids = group.map(plate);
      if (tpl.name === "c") {
        const paras = !textUsed ? text.paras : [];
        textUsed = textUsed || paras.length > 0;
        kids.push(el("div", { class: "mg-side" }, paras.length
          ? paras.map((p) => el("p", {}, p))
          : el("p", { class: "mg-side-note" }, t("Shot at Saber Group Studios.", "اتصورت في استديوهات صابر جروب."))));
      }
      out.push(el("div", { class: "mg-spread mg-spread--" + tpl.name }, kids));
      i += tpl.take; k++;
    }
    return { nodes: out, textUsed, next: k };
  }

  function render(d, root) {
    const issue = [d.sector.join(" · "), d.year].filter(Boolean).join(" — ");
    root.append(
      el("header", { class: "mg-cover" }, [
        el("div", { class: "mg-mast" }, [
          el("span", { class: "mg-brand" }, "Saber Group Studios"),
          el("span", {}, t("Portfolio", "الأعمال") + (issue ? " · " + issue : "")),
        ]),
        el("h1", { class: "mg-title" }, d.title),
        el("div", { class: "mg-cover-grid" }, [
          d.cover ? el("figure", { class: "mg-cover-fig" }, SC.img(d.cover, { loading: "eager" })) : null,
          el("div", { class: "mg-stand" }, [
            d.text.lead ? el("p", { class: "mg-deck" }, d.text.lead) : null,
            ...d.text.paras.map((p, i) => el("p", { class: i === 0 ? "mg-dropcap" : "" }, p)),
            el("dl", { class: "mg-facts" }, [
              d.client && [t("Client", "العميل"), d.client.name],
              d.location && [t("Location", "المكان"), d.location],
              d.services.length && [t("Services", "الخدمات"), d.services.join(", ")],
              [t("In this story", "في القصة"), [d.photos && d.photos + t(" plates", " لوحة"), d.films && d.films + t(" films", " فيديو")].filter(Boolean).join(" · ")],
            ].filter(Boolean).map(([k, v]) => el("div", {}, [el("dt", {}, k), el("dd", {}, v)]))),
          ]),
        ]),
      ])
    );

    let k = 0, n = 0;
    d.chapters.forEach((ch) => {
      n++;
      const head = el("header", { class: "mg-head" }, [
        el("p", { class: "mg-kicker" }, t("Chapter ", "الفصل ") + roman(n)),
        ch.caption ? el("h2", { class: "mg-h" }, ch.caption) : null,
      ]);
      if (ch.kind === "motion") {
        root.append(el("section", { class: "mg-motion" }, [
          el("header", { class: "mg-head" }, [
            el("p", { class: "mg-kicker" }, t("Chapter ", "الفصل ") + roman(n)),
            el("h2", { class: "mg-h" }, t("In motion", "بالفيديو")),
          ]),
          el("div", { class: "mg-films" }, ch.media.map((m) => el("article", { class: "mg-film" }, [
            SC.video(m),
            el("h3", {}, m.caption),
            m.text && m.text.lead ? el("p", { class: "mg-film-lead" }, m.text.lead) : null,
            ...(m.text ? m.text.paras.slice(0, 2).map((p) => el("p", {}, p)) : []),
          ]))),
        ]));
        return;
      }
      if (ch.kind === "compare") {
        root.append(el("section", { class: "mg-story" }, [head, el("div", { class: "mg-spread mg-spread--pair" },
          ch.media.map((m, i) => el("figure", { class: "mg-fig" }, [SC.img(m), el("figcaption", {}, ch.labels[i])])))]));
        return;
      }
      const photos = ch.media.filter((m) => m.type === "photo");
      // A pull quote has to be short: the headline line, or a first sentence under ~140 characters.
      const firstSentence = (ch.text.paras[0] || "").split(/(?<=[.!?؟])\s/)[0];
      const quote = ch.text.lead || (firstSentence.length <= 140 ? firstSentence : "");
      const restParas = ch.text.paras.slice();
      if (!ch.text.lead && quote) restParas[0] = restParas[0].slice(quote.length).trim();
      const restText = { paras: restParas.filter(Boolean) };
      const first = spreads(photos.slice(0, Math.min(2, photos.length)), { paras: [] }, k);
      const rest = spreads(photos.slice(first.nodes.length ? Math.min(2, photos.length) : 0), restText, first.next);
      k = rest.next;
      const body = !rest.textUsed && restText.paras.length
        ? el("div", { class: "mg-body" }, restText.paras.map((p) => el("p", {}, p))) : null;
      root.append(el("section", { class: "mg-story" }, [
        head,
        ...first.nodes,
        quote ? el("blockquote", { class: "mg-quote" }, quote) : null,
        body,
        ...rest.nodes,
      ]));
    });

    root.append(el("footer", { class: "mg-end" }, [
      d.cast.length ? el("section", { class: "mg-masthead" }, [
        el("p", { class: "mg-kicker" }, t("Masthead", "فريق العمل")),
        el("dl", {}, d.cast.map((c) => el("div", {}, [el("dt", {}, c.role), el("dd", {}, c.name)]))),
      ]) : null,
      el("section", { class: "mg-ask" }, [
        el("p", { class: "mg-ask-line" }, t("Commission a story like this.", "اطلب قصة زي دي لبراندك.")),
        el("p", {}, [
          el("a", { href: d.waLink, target: "_blank", rel: "noopener" }, t("Write to us on WhatsApp", "كلمنا على واتساب")),
          el("span", {}, t(" or call ", " أو اتصل ")),
          el("span", { class: "mg-num", dir: "ltr" }, d.phone),
        ]),
      ]),
    ]));
  }

  SC.direction("magazine", { label: ["Magazine", "مجلة"], render });
})();
