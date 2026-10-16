/*
 * Direction: Feed.
 * Shows the work the way audiences met it: as posts. Photos are grouped
 * into swipeable carousels (Instagram's 4:5 is their native ratio), the
 * designed grid appears as the profile it was made for, and the agency's
 * side of the story (brief, scope, results) sits beside the feed.
 * Desktop: info | feed | profile. Tablet landscape: info | feed.
 * Tablet portrait and phone: one column that opens like the profile itself.
 */
(function () {
  const { el, t } = SC;
  const P = SC.parts;

  const ICONS = {
    heart: '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    comment: '<path d="M20 12a8 8 0 1 1-3.1-6.3A8 8 0 0 1 20 12l1 6-5-1.8"/>',
    send: '<path d="M21 4 10 14M21 4l-7 17-4-7-7-4z"/>',
    save: '<path d="M6 3h12v18l-6-4-6 4z"/>',
  };
  const icon = (k) => {
    const s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    s.setAttribute("viewBox", "0 0 24 24"); s.setAttribute("aria-hidden", "true");
    s.innerHTML = ICONS[k];
    return s;
  };

  function carousel(items) {
    const track = el("div", { class: "f-track" }, items.map((m) => el("div", { class: "f-slide", style: { "--r": m.w / m.h } }, SC.img(m))));
    const dots = el("div", { class: "f-dots" }, items.length > 1 ? items.map(() => el("span")) : []);
    const count = el("span", { class: "f-count", dir: "ltr" }, items.length > 1 ? "1/" + items.length : "");
    const update = () => {
      const i = Math.round(Math.abs(track.scrollLeft) / Math.max(1, track.clientWidth));
      [...dots.children].forEach((d, j) => d.classList.toggle("is-on", j === i));
      if (items.length > 1) count.textContent = (i + 1) + "/" + items.length;
    };
    track.addEventListener("scroll", update, { passive: true });
    const go = (dir) => {
      const rtl = document.documentElement.dir === "rtl" ? -1 : 1;
      track.scrollBy({ left: dir * rtl * track.clientWidth, behavior: "smooth" });
    };
    requestAnimationFrame(update);
    return el("div", { class: "f-media" }, [
      track, count,
      items.length > 1 ? el("button", { type: "button", class: "f-nav f-nav--prev", "aria-label": t("Previous", "السابق"), onclick: () => go(-1) }, "‹") : null,
      items.length > 1 ? el("button", { type: "button", class: "f-nav f-nav--next", "aria-label": t("Next", "التالي"), onclick: () => go(1) }, "›") : null,
      dots,
    ]);
  }

  function post(d, media, caption, kind) {
    return el("article", { class: "f-post" }, [
      el("header", { class: "f-post-head" }, [
        el("span", { class: "p-avatar" }, d.client && d.client.logo ? el("img", { src: d.client.logo, alt: "" }) : null),
        el("div", {}, [el("strong", {}, d.client ? d.client.name : "Saber Group"), el("span", {}, kind)]),
      ]),
      media,
      el("div", { class: "f-actions", "aria-hidden": "true" }, [icon("heart"), icon("comment"), icon("send"), el("span", { class: "f-grow" }), icon("save")]),
      caption ? el("p", { class: "f-caption" }, [el("strong", {}, d.client ? d.client.name : "Saber Group"), " ", caption]) : null,
    ]);
  }

  // Up to 5 per carousel, split evenly so no post ends with a lone photo.
  function chunks(list) {
    const n = Math.ceil(list.length / 5);
    const size = Math.ceil(list.length / n);
    const out = [];
    for (let i = 0; i < list.length; i += size) out.push(list.slice(i, i + size));
    return out;
  }

  function render(d, root) {
    const feed = el("div", { class: "f-feed" });
    let h = 0;
    if (d.grid) feed.append(post(d, carousel([].concat(...d.grid.rows)), d.headlines[0] || "", t("Grid · 3 posts", "جريد · ٣ بوستات")));
    d.chapters.forEach((ch) => {
      if (ch.kind === "motion") {
        ch.media.forEach((m) => feed.append(post(d, el("div", { class: "f-media" }, SC.video(m)), m.caption, t("Reel", "ريل"))));
        return;
      }
      const photos = ch.media.filter((m) => m.type === "photo");
      chunks(photos).forEach((group, i) => {
        const text = i === 0 ? (ch.text.lead || ch.text.paras[0] || ch.caption) : (d.headlines[++h] || ch.caption);
        feed.append(post(d, carousel(group), text, t("Carousel · ", "كاروسيل · ") + group.length));
      });
    });

    const info = el("aside", { class: "f-info" }, [
      el("p", { class: "f-eyebrow" }, t("Saber Group Studios · Case", "استديوهات صابر جروب · مشروع")),
      el("h1", { class: "f-title" }, d.title),
      P.facts(d),
      P.deliverables(d),
      P.story(d) || P.intro(d),
      P.journey(d),
      P.results(d),
    ]);
    const profile = d.grid ? el("aside", { class: "f-side" }, [el("div", { class: "f-phone" }, P.profile(d, { extraRows: 3 }))]) : null;

    root.append(el("div", { class: "f-layout" + (profile ? "" : " no-profile") }, [info, feed, profile]),
      el("footer", { class: "f-end" }, [P.quote(d), P.crew(d), P.cta(d)]));
  }

  SC.direction("feed", { label: ["Feed", "فيد"], render });
})();
