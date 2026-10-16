/*
 * Direction: Cinema (developed).
 * The project plays as a short film, but scrolling stays easy: the page
 * snaps only near a scene (proximity, never forced), each chapter is ONE
 * scene whose photos sit side by side on a horizontal reel (swipe, drag,
 * arrows or keys), and a chapter index on the edge jumps anywhere.
 * The Instagram grid, being 2.25:1, plays as a widescreen frame.
 */
(function () {
  const { el, t, pad } = SC;
  const P = SC.parts;

  function scene(cls, bg, kids, name) {
    const s = el("section", { class: "c-scene " + cls, "data-name": name || "" });
    if (bg) s.append(el("div", { class: "c-amb", style: { backgroundImage: "url(\"" + bg + "\")" } }));
    s.append(...[].concat(kids).filter(Boolean));
    return s;
  }

  function reel(photos, ctx) {
    const track = el("div", { class: "c-track", tabindex: "0", "aria-label": t("Photos, scroll sideways", "صور، اسحب للجنب") },
      photos.map((m) => el("div", { class: "c-shot", style: { "--r": m.w / m.h } }, SC.img(m))));
    const count = el("span", { class: "c-reel-n", dir: "ltr" }, "01 / " + pad(photos.length));
    const bar = el("span", { class: "c-reel-bar" });
    const step = (dir) => {
      const shot = track.querySelector(".c-shot");
      const w = shot ? shot.getBoundingClientRect().width + 16 : track.clientWidth * 0.8;
      const rtl = document.documentElement.dir === "rtl" ? -1 : 1;
      track.scrollBy({ left: dir * rtl * w, behavior: "smooth" });
    };
    const update = () => {
      const max = track.scrollWidth - track.clientWidth;
      const p = max > 0 ? Math.abs(track.scrollLeft) / max : 1;
      bar.style.setProperty("--p", Math.max(p, 0.04));
      count.textContent = pad(Math.min(photos.length, Math.round(p * (photos.length - 1)) + 1)) + " / " + pad(photos.length);
    };
    track.addEventListener("scroll", update, { passive: true });
    track.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { step(document.documentElement.dir === "rtl" ? -1 : 1); e.preventDefault(); }
      if (e.key === "ArrowLeft") { step(document.documentElement.dir === "rtl" ? 1 : -1); e.preventDefault(); }
    });
    // Drag with the mouse on desktop; touch already scrolls natively.
    let down = null;
    track.addEventListener("pointerdown", (e) => { if (e.pointerType === "mouse") down = { x: e.clientX, l: track.scrollLeft, moved: false }; });
    ctx.on(window, "pointermove", (e) => {
      if (!down) return;
      const dx = e.clientX - down.x;
      if (Math.abs(dx) > 4) { down.moved = true; track.classList.add("is-drag"); }
      track.scrollLeft = down.l - dx;
    });
    ctx.on(window, "pointerup", () => {
      if (down && down.moved) track.addEventListener("click", (e) => e.stopPropagation(), { capture: true, once: true });
      down = null; track.classList.remove("is-drag");
    });
    requestAnimationFrame(update);
    return el("div", { class: "c-reel" }, [
      track,
      el("div", { class: "c-reel-ui" }, [
        el("button", { type: "button", class: "c-arrow", "aria-label": t("Previous", "السابق"), onclick: () => step(-1) }, "←"),
        el("span", { class: "c-reel-progress" }, bar),
        count,
        el("button", { type: "button", class: "c-arrow", "aria-label": t("Next", "التالي"), onclick: () => step(1) }, "→"),
      ]),
    ]);
  }

  function render(d, root, ctx) {
    document.documentElement.classList.add("c-snap");
    ctx.cleanup(() => document.documentElement.classList.remove("c-snap"));
    const scenes = [];
    const cover = d.cover && d.cover.src;

    scenes.push(scene("c-open", cover, el("div", { class: "c-card" }, [
      el("p", { class: "c-pre" }, t("Saber Group Studios presents", "استديوهات صابر جروب تقدّم")),
      el("h1", { class: "c-title" }, d.title),
      d.client ? el("p", { class: "c-for" }, t("for ", "لـ ") + d.client.name) : null,
      P.deliverables(d),
    ]), t("Opening", "البداية")));

    const story = P.story(d) || P.intro(d);
    const journey = P.journey(d);
    if (story || journey) scenes.push(scene("c-brief", null, el("div", { class: "c-card c-card--wide" }, [story, journey]), t("The brief", "المطلوب")));

    d.chapters.forEach((ch, i) => {
      const photos = ch.media.filter((m) => m.type === "photo");
      const name = ch.kind === "motion" ? t("In motion", "بالفيديو") : ch.caption || t("Chapter ", "الفصل ") + pad(i + 1);
      if (ch.kind === "motion") {
        scenes.push(scene("c-films", null, [
          el("div", { class: "c-card c-card--top" }, [el("p", { class: "c-pre" }, t("Chapter ", "الفصل ") + pad(i + 1)), el("h2", { class: "c-h" }, name)]),
          el("div", { class: "c-film-row" }, ch.media.map((m) => SC.video(m, "c-video"))),
        ], name));
        return;
      }
      scenes.push(scene("c-chapter", photos[0] && photos[0].src, [
        el("div", { class: "c-card c-card--top" }, [
          el("p", { class: "c-pre" }, t("Chapter ", "الفصل ") + pad(i + 1) + " · " + photos.length + t(" frames", " كادر")),
          el("h2", { class: "c-h" }, name),
          ch.text.lead || ch.text.paras[0] ? el("p", { class: "c-sub" }, ch.text.lead || ch.text.paras[0]) : null,
        ]),
        reel(photos, ctx),
      ], name));
    });

    if (d.grid) {
      d.grid.panoramas.forEach((m, i) => scenes.push(scene("c-wide", m.src, [
        el("div", { class: "c-card c-card--top" }, [
          el("p", { class: "c-pre" }, t("Instagram grid", "جريد انستجرام") + " · " + pad(i + 1)),
          d.headlines[i] ? el("h2", { class: "c-h c-h--sm" }, d.headlines[i]) : null,
        ]),
        el("div", { class: "c-wide-frame", style: { "--r": m.w / m.h } }, SC.img(m)),
      ], t("Instagram grid", "جريد انستجرام"))));
    }

    if (d.results) scenes.push(scene("c-results", cover, el("div", { class: "c-card c-card--wide" }, P.results(d)), t("Results", "النتايج")));

    const quote = P.quote(d);
    if (quote) scenes.push(scene("c-quote", null, el("div", { class: "c-card" }, quote), t("Client", "العميل")));

    if (d.cast.length) {
      scenes.push(scene("c-credits", null, el("div", { class: "c-roll" }, el("div", { class: "c-roll-inner" }, [
        el("p", { class: "c-pre" }, t("Credits", "فريق العمل")),
        ...d.cast.map((c) => el("p", { class: "c-credit" }, [el("span", {}, c.role), el("strong", {}, c.name)])),
      ])), t("Credits", "فريق العمل")));
    }
    scenes.push(scene("c-end", cover, el("div", { class: "c-card" }, P.cta(d, t("Your brand, next.", "البراند بتاعك، المرة الجاية."))), t("Contact", "تواصل")));

    // Chapter index on the edge: one dot per scene, labelled, jumps on click.
    const dots = el("nav", { class: "c-index", "aria-label": t("Scenes", "المشاهد") }, scenes.map((s) =>
      el("button", { type: "button", onclick: () => s.scrollIntoView({ behavior: "smooth" }) }, el("span", {}, s.dataset.name))));
    const hudN = el("span", { class: "c-hud-n", dir: "ltr" });
    root.append(...scenes, dots, el("div", { class: "c-hud", "aria-hidden": "true" }, [el("span", { class: "c-hud-brand" }, "Saber Group Studios"), hudN]));

    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      e.target.classList.toggle("is-on", e.isIntersecting);
      if (e.isIntersecting) {
        const i = scenes.indexOf(e.target);
        hudN.textContent = pad(i + 1) + " / " + pad(scenes.length);
        [...dots.children].forEach((b, j) => b.classList.toggle("is-on", j === i));
      }
    }), { threshold: 0.5 });
    scenes.forEach((s) => io.observe(s));
    ctx.cleanup(() => io.disconnect());
  }

  SC.direction("cinema", { label: ["Cinema", "سينما"], render });
})();
