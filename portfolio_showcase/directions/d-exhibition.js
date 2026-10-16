/*
 * Direction 3: Exhibition.
 * The project is hung as a gallery show. Each chapter is a room with its own
 * wall text; photos hang in black frames with white mats along one eye line,
 * at varied sizes, each with a museum label (number, title, medium, size).
 * Films play in a darkened screening room.
 */
(function () {
  const { el, t, roman } = SC;

  // Relative frame heights along a wall; the first work in a room hangs largest.
  const SCALE = [1.18, 0.86, 1, 0.78, 0.94, 0.82];

  function label(m, d, extra) {
    return el("div", { class: "ex-label" }, [
      el("p", { class: "ex-no" }, t("No. ", "رقم ") + m.plate),
      el("p", { class: "ex-work" }, m.caption || d.title),
      el("p", {}, extra || t("Photograph, retouched", "صورة فوتوغرافية، معدّلة")),
      el("p", { class: "ex-dim", dir: "ltr" }, m.w + " × " + m.h + " px"),
    ]);
  }

  function work(m, d, i) {
    return el("figure", { class: "ex-work-wrap", style: { "--s": SCALE[i % SCALE.length], "--r": m.w / m.h } }, [
      el("div", { class: "ex-frame" }, el("div", { class: "ex-mat" }, SC.img(m))),
      label(m, d),
    ]);
  }

  function render(d, root) {
    const counts = [d.photos && d.photos + t(" photographs", " صورة"), d.films && d.films + t(" films", " فيديو")].filter(Boolean).join(t(" and ", " و"));
    root.append(el("header", { class: "ex-entrance" }, [
      el("div", { class: "ex-wall-text" }, [
        el("p", { class: "ex-venue" }, [d.location || "Saber Group Studios", d.year].filter(Boolean).join(", ")),
        el("h1", { class: "ex-title" }, d.title),
        el("p", { class: "ex-by" }, t("Photographs by Saber Group Studios", "صور من استديوهات صابر جروب") + (d.client ? t(" for ", " لـ ") + d.client.name : "")),
        counts ? el("p", { class: "ex-count" }, counts) : null,
      ]),
      d.cover ? el("figure", { class: "ex-work-wrap ex-hero", style: { "--s": 1.3, "--r": d.cover.w / d.cover.h } },
        el("div", { class: "ex-frame" }, el("div", { class: "ex-mat" }, SC.img(d.cover, { loading: "eager" })))) : null,
    ]));

    if (d.text.lead || d.text.paras.length) {
      root.append(el("section", { class: "ex-intro" }, [
        d.text.lead ? el("p", { class: "ex-intro-lead" }, d.text.lead) : null,
        el("div", { class: "ex-cols" }, d.text.paras.map((p) => el("p", {}, p))),
      ]));
    }

    let room = 0;
    d.chapters.forEach((ch) => {
      room++;
      const head = el("div", { class: "ex-room-text" }, [
        el("p", { class: "ex-room-no" }, t("Room ", "قاعة ") + roman(room)),
        el("h2", { class: "ex-room-title" }, ch.kind === "motion" ? t("Screening room", "قاعة العرض") : ch.caption),
        ch.text.lead ? el("p", { class: "ex-room-lead" }, ch.text.lead) : null,
        ...ch.text.paras.map((p) => el("p", {}, p)),
      ]);
      if (ch.kind === "motion") {
        root.append(el("section", { class: "ex-room ex-room--dark" }, [head, el("div", { class: "ex-screens" },
          ch.media.map((m) => el("figure", { class: "ex-screen" }, [
            SC.video(m),
            el("div", { class: "ex-label" }, [
              el("p", { class: "ex-work" }, m.caption),
              el("p", {}, t("Film, colour, sound", "فيلم، ألوان، صوت")),
              m.text && m.text.lead ? el("p", {}, m.text.lead) : null,
            ]),
          ])))]));
        return;
      }
      const photos = ch.media.filter((m) => m.type === "photo");
      const hang = ch.kind === "compare"
        ? ch.media.map((m, i) => el("figure", { class: "ex-work-wrap", style: { "--s": 1, "--r": m.w / m.h } }, [
            el("div", { class: "ex-frame" }, el("div", { class: "ex-mat" }, SC.img(m))), label(m, d, ch.labels[i])]))
        : photos.map((m, i) => work(m, d, i));
      root.append(el("section", { class: "ex-room" }, [head, el("div", { class: "ex-wall" }, hang)]));
    });

    root.append(el("footer", { class: "ex-exit" }, [
      d.cast.length ? el("section", { class: "ex-credits" }, [
        el("p", { class: "ex-room-no" }, t("The exhibition was made by", "المعرض من صنع")),
        el("ul", {}, d.cast.map((c) => el("li", {}, [el("span", { class: "ex-c-name" }, c.name), el("span", { class: "ex-c-role" }, c.role)]))),
      ]) : null,
      el("section", { class: "ex-ask" }, [
        el("h2", { class: "ex-room-title" }, t("Hang your brand here.", "خلّي البراند بتاعك هنا.")),
        el("p", {}, t("Every show starts with one conversation.", "كل معرض بيبدأ بمكالمة.")),
        el("p", { class: "ex-ask-actions" }, [
          el("a", { class: "ex-btn", href: d.waLink, target: "_blank", rel: "noopener" }, t("Plan a shoot on WhatsApp", "خطط لشوت على واتساب")),
          el("span", { dir: "ltr", class: "ex-num" }, d.phone),
        ]),
      ]),
    ]));
  }

  SC.direction("exhibition", { label: ["Exhibition", "معرض"], render });
})();
