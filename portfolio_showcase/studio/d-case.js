/*
 * Direction: Case study.
 * Reads like a top agency's case study: the business story and the numbers
 * lead, the photos prove it. Light page, large serif statements, a sticky
 * contents rail on wide screens, an asymmetric bento of the work, and the
 * campaign shown on a phone as it lived on Instagram.
 */
(function () {
  const { el, t } = SC;
  const P = SC.parts;

  // Bento spans on a 6-column grid. Full cycles of 8 photos, then a tail
  // pattern chosen by what is left, so every row closes.
  const CYCLE = ["w3 h2", "w3", "w3", "w2", "w2", "w2", "w4 h2", "w2 h2"];
  const TAIL = {
    1: ["w6"], 2: ["w3", "w3"], 3: ["w2", "w2", "w2"], 4: ["w3", "w3", "w3", "w3"],
    5: ["w2", "w2", "w2", "w3", "w3"], 6: ["w2", "w2", "w2", "w2", "w2", "w2"],
    7: ["w3", "w3", "w2", "w2", "w2", "w3", "w3"],
  };

  function bento(photos) {
    const full = photos.length - (photos.length % CYCLE.length);
    const tail = TAIL[photos.length % CYCLE.length] || [];
    return el("div", { class: "s-bento" }, photos.map((m, i) =>
      el("figure", { class: "s-cell " + (i < full ? CYCLE[i % CYCLE.length] : tail[i - full]) }, SC.img(m))));
  }

  function section(id, label, kids) {
    return el("section", { class: "s-sec", id: "s-" + id }, [el("h2", { class: "s-label" }, label), el("div", { class: "s-sec-body" }, kids)]);
  }

  function render(d, root) {
    const photos = P.photos(d);
    const toc = [];
    const add = (id, label, kids) => { toc.push([id, label]); return section(id, label, kids); };

    root.append(el("header", { class: "s-hero" }, [
      el("div", { class: "s-hero-top" }, [
        d.client && d.client.logo ? el("img", { class: "s-logo", src: d.client.logo, alt: d.client.name }) : null,
        el("p", { class: "s-eyebrow" }, t("Case study", "دراسة حالة") + " · " + [d.client && d.client.name, d.year].filter(Boolean).join(", ")),
      ]),
      el("h1", { class: "s-title" }, d.headlines[0] ? d.headlines[0] + "." : d.title),
      el("p", { class: "s-sub" }, d.title),
      d.results ? el("ul", { class: "s-kpis" }, d.results.items.slice(0, 3).map((r) =>
        el("li", {}, [el("strong", { dir: "ltr" }, r.value), el("span", {}, r.label)]))) : null,
      d.results && d.results.example ? el("p", { class: "s-kpi-note" }, [SC.exampleTag(), " ", t("Placeholder figures until real insights are added.", "أرقام توضيحية لحد ما الأرقام الحقيقية تتضاف.")]) : null,
      d.cover ? el("figure", { class: "s-hero-img" }, SC.img(d.cover, { loading: "eager" })) : null,
    ]));

    const body = [];
    const story = P.story(d);
    if (story) body.push(add("brief", t("Brief & idea", "المطلوب والفكرة"), story));
    else if (P.intro(d)) body.push(add("brief", t("Overview", "نظرة عامة"), P.intro(d)));
    const journey = P.journey(d);
    if (journey) body.push(add("scope", t("Scope", "نطاق الشغل"), [journey, P.deliverables(d)]));
    if (photos.length) body.push(add("work", t("The work", "الشغل"), [
      ...d.chapters.filter((c) => c.kind === "gallery" && (c.text.lead || c.text.paras.length)).map((c) => P.chapterText(c)),
      bento(photos),
    ]));
    d.chapters.filter((c) => c.kind === "motion").forEach((c) => body.push(add("film", t("Film", "فيديو"),
      el("div", { class: "s-films" }, c.media.map((m) => SC.video(m))))));
    if (d.grid) body.push(add("social", t("On Instagram", "على انستجرام"), el("div", { class: "s-social" }, [
      el("div", { class: "s-phone" }, P.profile(d, { extraRows: 2 })),
      el("div", { class: "s-social-text" }, [
        el("p", { class: "s-statement" }, t("Designed for the profile, not only the post.", "متصمم للبروفايل كله، مش للبوست بس.")),
        el("p", {}, t("Each row of three posts forms one wide image, so the brand page looks like a campaign the moment someone opens it.", "كل صف من ٣ بوستات بيكوّن صورة عريضة واحدة، فصفحة البراند تبان كحملة أول ما حد يفتحها.")),
        P.panorama(d, 0),
      ]),
    ])));
    const results = P.results(d);
    if (results) body.push(add("results", t("Results", "النتايج"), results));
    const quote = P.quote(d);
    if (quote) body.push(add("client", t("Client", "العميل"), quote));
    const crew = P.crew(d);
    if (crew) body.push(add("team", t("Team", "الفريق"), crew));

    root.append(el("div", { class: "s-layout" }, [
      el("nav", { class: "s-toc", "aria-label": t("Contents", "المحتوى") }, el("ol", {}, toc.map(([id, label]) =>
        el("li", {}, el("a", { href: "#s-" + id, onclick: (e) => { e.preventDefault(); document.getElementById("s-" + id).scrollIntoView({ behavior: "smooth" }); } }, label))))),
      el("div", { class: "s-main" }, body),
    ]), P.cta(d));
  }

  SC.direction("case", { label: ["Case study", "دراسة حالة"], render });
})();
