/*
 * Direction 2: Cinema.
 * The project plays like a film. Every scroll lands on a full-screen scene:
 * an opening title, a title card per chapter, then the frames themselves over
 * a blurred, enlarged copy of the photo so portraits fill a wide screen.
 * On wide screens portrait photos are grouped into diptychs or triptychs.
 * A fixed overlay shows the chapter and scene count; the crew rolls as
 * closing credits.
 */
(function () {
  const { el, t, pad, isPortrait } = SC;

  function groupFrames(photos) {
    const wide = matchMedia("(min-aspect-ratio: 5/4)").matches;
    const groups = [];
    let i = 0;
    while (i < photos.length) {
      if (!wide || !isPortrait(photos[i])) { groups.push([photos[i]]); i++; continue; }
      let run = 0;
      while (i + run < photos.length && isPortrait(photos[i + run]) && run < 3) run++;
      // Prefer threes, but never leave a single portrait stranded at the end.
      const left = photos.length - i;
      const take = left === 4 ? 2 : Math.min(run, 3);
      groups.push(photos.slice(i, i + take));
      i += take;
    }
    return groups;
  }

  function scene(cls, bgSrc, kids, meta) {
    const s = el("section", { class: "cn-scene " + cls, "data-chapter": meta || "" });
    if (bgSrc) s.append(el("div", { class: "cn-ambient", style: { backgroundImage: "url(\"" + bgSrc + "\")" } }));
    s.append(...[].concat(kids).filter(Boolean));
    return s;
  }

  function render(d, root, ctx) {
    document.documentElement.classList.add("cn-snap");
    ctx.cleanup(() => document.documentElement.classList.remove("cn-snap"));

    const scenes = [];
    scenes.push(scene("cn-open", d.cover && d.cover.src, el("div", { class: "cn-card" }, [
      el("p", { class: "cn-pre" }, t("Saber Group Studios presents", "استديوهات صابر جروب تقدّم")),
      el("h1", { class: "cn-title" }, d.title),
      d.client ? el("p", { class: "cn-for" }, t("for ", "لـ ") + d.client.name) : null,
      el("p", { class: "cn-hint", "aria-hidden": "true" }, t("Scroll", "مرّر")),
    ]), t("Opening", "البداية")));

    if (d.text.paras.length || d.text.lead) {
      scenes.push(scene("cn-text", null, el("div", { class: "cn-card cn-card--text" }, [
        d.text.lead ? el("p", { class: "cn-lead" }, d.text.lead) : null,
        ...d.text.paras.slice(0, 2).map((p) => el("p", {}, p)),
        el("p", { class: "cn-meta" }, [d.location, d.services.slice(0, 4).join(" · ")].filter(Boolean).join("  —  ")),
      ]), t("Synopsis", "الفكرة")));
    }

    let n = 0;
    d.chapters.forEach((ch) => {
      n++;
      const name = ch.kind === "motion" ? t("In motion", "بالفيديو") : ch.caption || t("Scene ", "مشهد ") + n;
      const firstPhoto = ch.media.find((m) => m.type === "photo");
      scenes.push(scene("cn-inter", firstPhoto && firstPhoto.src, el("div", { class: "cn-card" }, [
        el("p", { class: "cn-pre" }, t("Chapter ", "الفصل ") + pad(n)),
        el("h2", { class: "cn-h" }, name),
        ch.text.lead ? el("p", { class: "cn-lead" }, ch.text.lead) : null,
        ch.text.paras[0] ? el("p", { class: "cn-sub" }, ch.text.paras[0]) : null,
      ]), name));

      if (ch.kind === "motion") {
        ch.media.forEach((m) => scenes.push(scene("cn-film", m.poster, [
          SC.video(m, "cn-video"),
          el("p", { class: "cn-subtitle" }, m.caption),
        ], name)));
        return;
      }
      const photos = ch.media.filter((m) => m.type === "photo");
      groupFrames(photos).forEach((g) => {
        scenes.push(scene("cn-frames cn-frames--" + g.length, g[Math.floor(g.length / 2)].src,
          el("div", { class: "cn-row" }, g.map((m) => el("div", { class: "cn-frame", style: { "--r": m.w / m.h } }, SC.img(m)))), name));
      });
    });

    if (d.cast.length) {
      scenes.push(scene("cn-credits", null, el("div", { class: "cn-roll" }, el("div", { class: "cn-roll-inner" }, [
        el("p", { class: "cn-pre" }, t("Credits", "فريق العمل")),
        ...d.cast.map((c) => el("p", { class: "cn-credit" }, [el("span", {}, c.role), el("strong", {}, c.name)])),
        el("p", { class: "cn-credit cn-credit--studio" }, [el("span", {}, t("Produced at", "إنتاج")), el("strong", {}, "Saber Group Studios")]),
      ])), t("Credits", "فريق العمل")));
    }
    scenes.push(scene("cn-end", d.cover && d.cover.src, el("div", { class: "cn-card" }, [
      el("h2", { class: "cn-h" }, t("Your brand, next.", "البراند بتاعك، المرة الجاية.")),
      el("p", { class: "cn-sub" }, t("Tell us what you sell. We'll plan the shoot around it.", "قولنا بتبيع إيه، وإحنا نخطط الشوت على مقاسه.")),
      el("p", { class: "cn-actions" }, [
        el("a", { class: "cn-btn", href: d.waLink, target: "_blank", rel: "noopener" }, t("Message us on WhatsApp", "كلمنا على واتساب")),
        el("span", { class: "cn-num", dir: "ltr" }, d.phone),
      ]),
    ]), t("The end", "النهاية")));

    const hudChapter = el("span", { class: "cn-hud-ch" });
    const hudCount = el("span", { class: "cn-hud-n", dir: "ltr" });
    const bar = el("span", { class: "cn-hud-bar" });
    root.append(...scenes, el("div", { class: "cn-hud", "aria-hidden": "true" }, [
      el("span", { class: "cn-hud-brand" }, "Saber Group Studios"), hudChapter, hudCount, bar,
    ]));

    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        e.target.classList.toggle("is-on", e.isIntersecting);
        if (e.isIntersecting) {
          const i = scenes.indexOf(e.target);
          hudChapter.textContent = e.target.dataset.chapter;
          hudCount.textContent = pad(i + 1) + " / " + pad(scenes.length);
          bar.style.setProperty("--p", (i + 1) / scenes.length);
        }
      });
    }, { threshold: 0.55 });
    scenes.forEach((s) => io.observe(s));
    ctx.cleanup(() => io.disconnect());
    // Redraw when the screen crosses between wide (grouped frames) and narrow.
    const mq = matchMedia("(min-aspect-ratio: 5/4)");
    const redraw = () => { root.textContent = ""; io.disconnect(); render(d, root, ctx); };
    ctx.on(mq, "change", redraw);
  }

  SC.direction("cinema", { label: ["Cinema", "سينما"], render });
})();
