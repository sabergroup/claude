/*
 * Direction 4: Atelier.
 * A jewellery-house presentation. The page takes its colour from the
 * project's own photos (the most saturated tones of the cover, darkened), so
 * every project gets its own palette with no setup. Photos sit in arched
 * frames; sections with four or more photos become a showcase stage with a
 * loupe that magnifies the detail under the pointer, and a thumbnail rail.
 */
(function () {
  const { el, t, pad } = SC;

  const rule = () => el("div", { class: "at-rule", "aria-hidden": "true" }, el("span", {}, "◆"));

  function loupe(stage, getPhoto) {
    const lens = el("div", { class: "at-lens", "aria-hidden": "true" });
    stage.append(lens);
    const ZOOM = 2.6;
    const move = (e) => {
      const img = stage.querySelector(".at-main img");
      if (!img) return;
      const r = img.getBoundingClientRect();
      const x = e.clientX - r.left, y = e.clientY - r.top;
      if (x < 0 || y < 0 || x > r.width || y > r.height) { lens.classList.remove("is-on"); return; }
      const m = getPhoto();
      const sr = stage.getBoundingClientRect();
      lens.classList.add("is-on");
      lens.style.left = e.clientX - sr.left + "px";
      lens.style.top = e.clientY - sr.top + "px";
      lens.style.backgroundImage = "url(\"" + m.src + "\")";
      lens.style.backgroundSize = r.width * ZOOM + "px " + r.height * ZOOM + "px";
      lens.style.backgroundPosition = -(x * ZOOM - 90) + "px " + -(y * ZOOM - 90) + "px";
    };
    stage.addEventListener("pointermove", (e) => { if (e.pointerType === "mouse") move(e); });
    stage.addEventListener("pointerleave", () => lens.classList.remove("is-on"));
  }

  function showcase(photos) {
    let at = 0;
    const main = el("div", { class: "at-main" });
    const prevPeek = el("div", { class: "at-peek at-peek--prev" });
    const nextPeek = el("div", { class: "at-peek at-peek--next" });
    const counter = el("p", { class: "at-counter", dir: "ltr" });
    const thumbs = el("div", { class: "at-thumbs" }, photos.map((m, i) => el("button", {
      type: "button", class: "at-thumb", "aria-label": (m.caption || "") + " " + (i + 1), onclick: () => go(i),
    }, el("img", { src: m.src, alt: "", loading: "lazy" }))));
    const stage = el("div", { class: "at-stage" }, [prevPeek, main, nextPeek]);
    const go = (i) => {
      at = (i + photos.length) % photos.length;
      const m = photos[at];
      main.textContent = "";
      main.style.setProperty("--r", m.w / m.h);
      main.append(SC.img(m, { loading: "eager" }));
      const p = photos[(at - 1 + photos.length) % photos.length], n = photos[(at + 1) % photos.length];
      prevPeek.style.backgroundImage = "url(\"" + p.src + "\")";
      nextPeek.style.backgroundImage = "url(\"" + n.src + "\")";
      counter.textContent = pad(at + 1) + " — " + pad(photos.length);
      [...thumbs.children].forEach((b, j) => b.classList.toggle("is-on", j === at));
    };
    prevPeek.addEventListener("click", () => go(at - 1));
    nextPeek.addEventListener("click", () => go(at + 1));
    go(0);
    loupe(stage, () => photos[at]);
    return el("div", { class: "at-show" }, [
      stage,
      el("div", { class: "at-controls" }, [
        el("button", { type: "button", class: "at-arrow", "aria-label": t("Previous", "السابق"), onclick: () => go(at - 1) }, "←"),
        counter,
        el("button", { type: "button", class: "at-arrow", "aria-label": t("Next", "التالي"), onclick: () => go(at + 1) }, "→"),
      ]),
      thumbs,
      el("p", { class: "at-hint" }, t("Move over the photo to see the detail", "حرّك الماوس على الصورة عشان تشوف التفاصيل")),
    ]);
  }

  async function render(d, root) {
    // Tint the page from the cover: same hue, deep and quiet.
    const hsl = d.cover ? await SC.palette(d.cover.src) : null;
    const h = hsl ? hsl.h : 352, s = hsl ? Math.min(hsl.s, 70) : 55;
    root.style.setProperty("--at-bg", "hsl(" + h + " " + Math.round(s * 0.55) + "% 9%)");
    root.style.setProperty("--at-bg-2", "hsl(" + h + " " + Math.round(s * 0.5) + "% 13%)");
    document.documentElement.style.setProperty("--at-page", "hsl(" + h + " " + Math.round(s * 0.55) + "% 9%)");

    const line = [d.client && d.client.name, d.sector[0], d.year].filter(Boolean);
    root.append(el("header", { class: "at-hero" }, [
      el("p", { class: "at-line" }, line.map((x, i) => [i ? el("span", { class: "at-dia" }, "◆") : null, el("span", {}, x)]).flat()),
      el("h1", { class: "at-title" }, d.title),
      d.cover ? el("figure", { class: "at-arch at-arch--hero", style: { "--r": d.cover.w / d.cover.h } }, SC.img(d.cover, { loading: "eager" })) : null,
      el("dl", { class: "at-facts" }, [
        d.location && [t("Atelier", "المكان"), d.location],
        d.services.length && [t("Craft", "الخدمات"), d.services.slice(0, 3).join(" · ")],
        [t("Pieces", "القطع"), [d.photos && d.photos + t(" photographs", " صورة"), d.films && d.films + t(" films", " فيديو")].filter(Boolean).join(" · ")],
      ].filter(Boolean).map(([k, v]) => el("div", {}, [el("dt", {}, k), el("dd", {}, v)]))),
    ]));

    if (d.text.lead || d.text.paras.length) {
      root.append(rule(), el("section", { class: "at-intro" }, [
        d.text.lead ? el("p", { class: "at-intro-lead" }, d.text.lead) : null,
        ...d.text.paras.map((p) => el("p", {}, p)),
      ]));
    }

    d.chapters.forEach((ch) => {
      const title = ch.kind === "motion" ? t("In motion", "بالفيديو") : ch.caption;
      const head = el("header", { class: "at-head" }, [
        el("h2", { class: "at-h" }, title),
        ch.text.lead ? el("p", { class: "at-lead" }, ch.text.lead) : null,
        ...ch.text.paras.map((p) => el("p", { class: "at-para" }, p)),
      ]);
      let body;
      if (ch.kind === "motion") {
        body = el("div", { class: "at-arches" }, ch.media.map((m) => el("figure", { class: "at-film" }, [
          el("div", { class: "at-arch at-arch--video", style: { "--r": m.w && m.h ? m.w / m.h : 9 / 16 } }, SC.video(m)),
          el("figcaption", {}, [el("strong", {}, m.caption), m.text && m.text.lead ? el("span", {}, m.text.lead) : null]),
        ])));
      } else {
        const photos = ch.media.filter((m) => m.type === "photo");
        body = photos.length >= 4 ? showcase(photos)
          : el("div", { class: "at-arches" }, photos.map((m, i) => el("figure", {}, [
            el("div", { class: "at-arch", style: { "--r": m.w / m.h } }, SC.img(m)),
            ch.kind === "compare" ? el("figcaption", {}, ch.labels[i]) : null,
          ])));
      }
      root.append(rule(), el("section", { class: "at-chapter" }, [head, body]));
    });

    root.append(rule(), el("footer", { class: "at-end" }, [
      d.cast.length ? el("ul", { class: "at-crew" }, d.cast.map((c) => el("li", {}, [el("span", {}, c.role), el("strong", {}, c.name)]))) : null,
      el("h2", { class: "at-h" }, t("Reserve an atelier session", "احجز جلسة تصوير")),
      el("p", { class: "at-para" }, t("Your pieces, lit and styled the way they deserve.", "قطعك، بإضاءة وتنسيق يليقوا بيها.")),
      el("p", { class: "at-actions" }, [
        el("a", { class: "at-btn", href: d.waLink, target: "_blank", rel: "noopener" }, t("Book on WhatsApp", "احجز على واتساب")),
        el("span", { class: "at-num", dir: "ltr" }, d.phone),
      ]),
    ]));
  }

  SC.direction("atelier", { label: ["Atelier", "أتيليه"], render });
})();
