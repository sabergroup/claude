/*
 * Saber Group project showcase.
 *
 * Turns one project from the public projects API into an edited case-study
 * page. Every material (section) gets a layout chosen from its photos'
 * count and shapes, so no project needs to be laid out by hand:
 *
 *   1 landscape photo           -> bleed      full-width frame
 *   1 portrait/square photo     -> single     tall frame beside the section text
 *   2-3 portrait photos         -> row        one large row, equal heights
 *   4-8 portrait photos         -> spotlight  sticky lead frame + grid of the rest
 *   9+ portrait photos          -> strip      swipeable full-height filmstrip
 *   landscape or mixed sets     -> justified  rows of equal height, no cropping
 *   videos                      -> motion     players that loop muted on screen
 *   before/after                -> compare    drag-to-reveal slider
 *
 * A material's `viewStyle` in the CMS overrides the automatic choice when it
 * names one of the layouts above ("default" keeps it automatic).
 *
 * Config (window.SHOWCASE):
 *   source      "api" (live) or a URL of a single project JSON (preview)
 *   api         projects endpoint, used when source is "api"
 *   slug        project slug; defaults to ?slug=, #slug, or the last path segment
 *   imageProxy  resizing proxy for grid images (live only), e.g. images.weserv.nl
 *   lang        "en" | "ar"
 *   contact     { whatsapp: "201080099757", phone: "01080099757" }
 *   projectHref function(slug) -> link for related projects
 */
(function () {
  "use strict";

  const cfg = Object.assign(
    {
      source: "api",
      api: "https://marketing-planner-tau.vercel.app/api/v1/projects/public?PageCount=all",
      imageProxy: "",
      lang: "en",
      contact: { whatsapp: "201080099757", phone: "01080099757" },
      projectHref: (slug) => "?slug=" + encodeURIComponent(slug),
      picker: false,
    },
    window.SHOWCASE || {}
  );

  const LAYOUTS = ["bleed", "single", "row", "spotlight", "strip", "justified"];
  const T = {
    en: {
      client: "Client", sector: "Sector", location: "Location", services: "Services",
      photos: (n) => (n === 1 ? "1 photo" : n + " photos"),
      films: (n) => (n === 1 ? "1 film" : n + " films"),
      crew: "Crew", motion: "In motion", ask: "Want a shoot like this?",
      askBody: "Tell us about your brand and we'll plan a shoot around it.",
      whatsapp: "Message us on WhatsApp", or: "or call",
      more: "More from", play: "Play with sound", close: "Close", prev: "Previous", next: "Next",
      before: "Before", after: "After", drag: "Drag to compare", portfolio: "Portfolio",
      loading: "Loading project", notFound: "This project isn't published.",
      waText: (t) => "Hi Saber Group, I saw \"" + t + "\" and want a similar shoot.",
      other: "Preview another project",
    },
    ar: {
      client: "العميل", sector: "القطاع", location: "المكان", services: "الخدمات",
      photos: (n) => (n === 1 ? "صورة واحدة" : n + " صورة"),
      films: (n) => (n === 1 ? "فيديو واحد" : n + " فيديو"),
      crew: "فريق العمل", motion: "بالفيديو", ask: "عايز شوت زي ده؟",
      askBody: "احكيلنا عن البراند بتاعك وهنخطط الشوت على مقاسه.",
      whatsapp: "كلمنا على واتساب", or: "أو اتصل",
      more: "أعمال أخرى في", play: "تشغيل بالصوت", close: "إغلاق", prev: "السابق", next: "التالي",
      before: "قبل", after: "بعد", drag: "اسحب للمقارنة", portfolio: "الأعمال",
      loading: "جاري التحميل", notFound: "المشروع ده مش منشور.",
      waText: (t) => "أهلاً صابر جروب، شفت مشروع \"" + t + "\" وعايز شوت شبهه.",
      other: "اعرض مشروع تاني",
    },
  };

  /* ---------- helpers ---------- */

  const $ = (sel, root) => (root || document).querySelector(sel);
  const el = (tag, attrs, kids) => {
    const n = document.createElement(tag);
    for (const k in attrs || {}) {
      const v = attrs[k];
      if (v == null || v === false) continue;
      if (k === "class") n.className = v;
      else if (k === "style" && typeof v === "object")
        for (const p in v) p.startsWith("--") ? n.style.setProperty(p, v[p]) : (n.style[p] = v[p]);
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? "" : v);
    }
    [].concat(kids || []).forEach((c) => c != null && c !== false && n.append(c.nodeType ? c : String(c)));
    return n;
  };
  // append() that skips empty slots, so optional blocks can be passed inline.
  const add = (parent, ...kids) => { kids.forEach((k) => k && parent.append(k)); return parent; };

  const clean = (s) =>
    String(s || "").replace(/[​‌‍﻿]/g, "").replace(/[ \t]+\n/g, "\n").trim();

  const pick = (o, lang) => {
    if (!o) return "";
    if (typeof o === "string") return clean(o);
    return clean(o[lang]) || clean(o[lang === "ar" ? "en" : "ar"]);
  };

  // Editors separate paragraphs with blank lines or runs of 2+ spaces.
  // A short opening fragment with no full stop reads as the section's headline.
  function splitText(text) {
    const parts = clean(text).split(/\n\s*\n|\s{2,}/).map((s) => s.trim()).filter(Boolean);
    let lead = "";
    if (parts.length > 1 && parts[0].length <= 70 && !/[.!؟?]$/.test(parts[0])) lead = parts.shift();
    return { lead, paras: parts };
  }

  function slugify(t) {
    return (t || "")
      .normalize("NFD").replace(/\p{Diacritic}/gu, "")
      .toLowerCase().trim().replace(/[^a-z0-9\s-]/g, "").replace(/\s+/g, "-");
  }
  const slugOf = (p) => p.slug || slugify(p.name && p.name.en) || p._id;

  const sized = (url, width) =>
    cfg.imageProxy && /^https?:/.test(url)
      ? cfg.imageProxy + "/?url=" + encodeURIComponent(url) + "&w=" + width + "&q=80&output=jpg"
      : url;

  // Resolve every photo's natural size before layout; previews carry w/h already.
  function measure(m) {
    if (m.w && m.h) return Promise.resolve(m);
    return new Promise((res) => {
      const img = new Image();
      img.onload = () => { m.w = img.naturalWidth; m.h = img.naturalHeight; res(m); };
      img.onerror = () => { m.w = 4; m.h = 5; m.broken = true; res(m); };
      img.src = m.src;
    });
  }

  /* ---------- API project -> page model ---------- */

  function normalize(p, lang) {
    const photo = (o, caption) => o && o.url && {
      type: "photo", url: o.url, src: sized(o.url, 1400), w: o.w, h: o.h, caption,
    };
    const chapters = [];
    const mats = (p.material || []).slice().sort((a, b) => (a.order || 0) - (b.order || 0));
    for (const m of mats) {
      const caption = pick(m.caption, lang);
      const text = splitText(pick(m.description, lang) || pick(m.textContent, lang));
      const style = LAYOUTS.includes(m.viewStyle) ? m.viewStyle : null;
      if (m.type === "video") {
        if (!m.url) continue;
        const v = {
          type: "video", url: m.url, poster: m.thumbnail || "", w: m.w, h: m.h, caption, text,
        };
        const prev = chapters[chapters.length - 1];
        // Consecutive films read as one "in motion" section.
        if (prev && prev.kind === "motion") prev.media.push(v);
        else chapters.push({ kind: "motion", caption: "", text: { lead: "", paras: [] }, media: [v] });
      } else if (m.type === "before_after") {
        const b = photo(m.before, caption), a = photo(m.after, caption);
        if (b && a) chapters.push({
          kind: "compare", caption, text, before: b, after: a,
          labels: [pick(m.before.label, lang), pick(m.after.label, lang)],
        });
      } else {
        const media = (m.items && m.items.length ? m.items : [m])
          .map((it) => (it.type === "video"
            ? { type: "video", url: it.url, poster: it.thumbnail || "", w: it.w, h: it.h, caption }
            : photo(it, caption)))
          .filter(Boolean);
        if (!media.length) continue;
        const prev = chapters[chapters.length - 1];
        // Untitled single photos with no story join the section before them.
        if (!caption && !text.paras.length && !text.lead && prev && prev.kind === "gallery") {
          prev.media.push(...media);
          continue;
        }
        chapters.push({ kind: "gallery", caption, text, media, style });
      }
    }

    const company = p.company && !p.hideClientName ? p.company : null;
    const cover = p.fullMainCover || p.mainCover;
    const photos = chapters.reduce((n, c) => n + (c.kind === "gallery"
      ? c.media.filter((x) => x.type === "photo").length : c.kind === "compare" ? 2 : 0), 0);
    const films = chapters.reduce((n, c) => n + (c.media || []).filter((x) => x.type === "video").length, 0);
    return {
      slug: slugOf(p),
      title: pick(p.name, lang),
      text: splitText(pick(p.description, lang)),
      client: company && { name: pick(company.name, lang), logo: company.logo || "" },
      sector: (p.categories || []).map((c) => pick(c.name, lang)).filter(Boolean),
      location: pick(p.location, lang),
      services: (p.types || []).map((t) => pick(t.name, lang)).filter(Boolean),
      cover: cover && cover.url ? { url: cover.url, src: sized(cover.url, 1800), w: cover.w, h: cover.h } : null,
      chapters,
      cast: (p.cast || []).slice().sort((a, b) => (a.order || 0) - (b.order || 0))
        .map((c) => ({ name: clean(c.castId && c.castId.name), role: clean(c.title) }))
        .filter((c) => c.name),
      photos,
      films,
      categoryIds: (p.categories || []).map((c) => c._id),
    };
  }

  /* ---------- layout choice ---------- */

  function chooseLayout(ch) {
    if (ch.style) return ch.style;
    const ms = ch.media.filter((m) => m.type === "photo");
    const n = ms.length;
    const ratios = ms.map((m) => m.w / m.h);
    const portrait = ratios.every((r) => r < 0.95);
    if (n === 1) return ratios[0] > 1.15 ? "bleed" : "single";
    if (!portrait) return "justified";
    if (n <= 3) return "row";
    if (n <= 8) return "spotlight";
    return "strip";
  }

  /* ---------- rendering ---------- */

  let lightbox; // set up once per render
  // Every photo in reading order; filled before render so redrawn rows keep their index.
  const lbItems = [];

  function frame(m, opts) {
    opts = opts || {};
    if (!lbItems.includes(m)) lbItems.push(m);
    const img = el("img", {
      src: m.src, alt: m.caption || "", loading: opts.eager ? "eager" : "lazy", decoding: "async",
      width: m.w, height: m.h, draggable: "false",
    });
    const f = el("button", {
      type: "button", class: "frame" + (opts.cls ? " " + opts.cls : ""),
      style: { aspectRatio: m.w + " / " + m.h, "--r": m.w / m.h },
      "aria-label": m.caption || "Photo",
      onclick: () => lightbox.open(lbItems.indexOf(m)),
    }, img);
    img.addEventListener("load", () => f.classList.add("is-in"));
    if (img.complete) f.classList.add("is-in");
    return f;
  }

  function textBlock(caption, text, opts) {
    opts = opts || {};
    return el("div", { class: "ch-text" + (opts.cls ? " " + opts.cls : "") }, [
      caption ? el("h2", { class: "ch-title" }, caption) : null,
      opts.meta ? el("p", { class: "ch-meta" }, opts.meta) : null,
      text.lead ? el("p", { class: "ch-lead" }, text.lead) : null,
      ...text.paras.map((p) => el("p", { class: "ch-para" }, p)),
    ]);
  }

  // Rows of equal height that fill the width; frames keep their own ratio.
  function justified(ms, targetRatioSum) {
    const wrap = el("div", { class: "justified" });
    const draw = () => {
      wrap.textContent = "";
      const W = wrap.clientWidth || 1000;
      const target = targetRatioSum || Math.max(1.6, W / 380);
      let row = [], sum = 0;
      const flush = (last) => {
        if (!row.length) return;
        const r = el("div", { class: "jrow" + (last && sum < target * 0.6 ? " is-short" : "") },
          row.map((m) => frame(m)));
        if (last && sum < target * 0.6) r.style.maxWidth = (sum / target) * 100 + "%";
        wrap.append(r);
        row = []; sum = 0;
      };
      ms.forEach((m) => {
        row.push(m); sum += m.w / m.h;
        if (sum >= target) flush(false);
      });
      flush(true);
    };
    requestAnimationFrame(draw);
    let lastW = 0;
    new ResizeObserver(() => {
      if (Math.abs(wrap.clientWidth - lastW) > 40) { lastW = wrap.clientWidth; draw(); }
    }).observe(wrap);
    return wrap;
  }

  function renderGallery(ch, idx) {
    const ms = ch.media.filter((m) => m.type === "photo");
    const vids = ch.media.filter((m) => m.type === "video");
    const layout = chooseLayout(ch);
    const flip = idx % 2 === 1;
    const meta = T[state.lang].photos(ms.length);
    const sec = el("section", { class: "ch ch--" + layout + (flip ? " is-flip" : ""), "data-layout": layout });

    if (layout === "bleed") {
      add(sec, textBlock(ch.caption, ch.text, { meta, cls: "ch-text--wide" }), frame(ms[0], { cls: "frame--bleed" }));
    } else if (layout === "single") {
      add(sec, el("div", { class: "single" }, [frame(ms[0]), textBlock(ch.caption, ch.text, { meta })]));
    } else if (layout === "row") {
      const sum = ms.reduce((s, m) => s + m.w / m.h, 0);
      add(sec, 
        textBlock(ch.caption, ch.text, { meta, cls: "ch-text--wide" }),
        el("div", { class: "row", style: { "--sum": sum, "--n": ms.length } }, ms.map((m) => frame(m)))
      );
    } else if (layout === "spotlight") {
      const [lead, ...rest] = ms;
      const cols = rest.length % 3 === 0 && rest.length % 2 !== 0 ? 3 : 2;
      const gridCount = rest.length - (rest.length % cols);
      const grid = rest.slice(0, gridCount), tail = rest.slice(gridCount);
      add(sec, 
        textBlock(ch.caption, ch.text, { meta, cls: "ch-text--wide" }),
        el("div", { class: "spotlight" }, [
          el("div", { class: "spot-lead" }, frame(lead)),
          el("div", { class: "spot-grid", style: { "--cols": cols } }, grid.map((m) => frame(m))),
        ]),
        tail.length ? justified(tail, Math.max(2.4, tail.reduce((s, m) => s + m.w / m.h, 0))) : null
      );
    } else if (layout === "strip") {
      const track = el("div", { class: "strip-track", tabindex: "0", "aria-label": ch.caption || meta },
        ms.map((m) => frame(m)));
      const bar = el("span", { class: "strip-bar" });
      const step = (d) => {
        const rtl = state.lang === "ar" ? -1 : 1;
        track.scrollBy({ left: d * rtl * track.clientWidth * 0.8, behavior: "smooth" });
      };
      track.addEventListener("scroll", () => {
        const max = track.scrollWidth - track.clientWidth;
        bar.style.setProperty("--p", max > 0 ? Math.abs(track.scrollLeft) / max : 1);
      }, { passive: true });
      add(sec, 
        el("div", { class: "strip-head" }, [
          textBlock(ch.caption, ch.text, { meta }),
          el("div", { class: "strip-nav" }, [
            el("button", { type: "button", class: "icon-btn", "aria-label": T[state.lang].prev, onclick: () => step(-1) }, arrow(-1)),
            el("button", { type: "button", class: "icon-btn", "aria-label": T[state.lang].next, onclick: () => step(1) }, arrow(1)),
          ]),
        ]),
        el("div", { class: "strip" }, [track, el("div", { class: "strip-progress" }, bar)])
      );
    } else {
      add(sec, textBlock(ch.caption, ch.text, { meta, cls: "ch-text--wide" }), justified(ms));
    }
    if (vids.length) add(sec, renderMotion({ media: vids, caption: "", text: { lead: "", paras: [] } }, idx, true));
    return sec;
  }

  function arrow(dir) {
    const s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    s.setAttribute("viewBox", "0 0 24 24");
    s.setAttribute("aria-hidden", "true");
    s.innerHTML = dir > 0
      ? '<path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.6"/>'
      : '<path d="M19 12H5M11 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="1.6"/>';
    s.classList.add("arrow");
    return s;
  }

  const videoIO = "IntersectionObserver" in window && new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      const v = e.target;
      if (v.dataset.user) return;
      if (e.isIntersecting && !matchMedia("(prefers-reduced-motion: reduce)").matches) v.play().catch(() => {});
      else v.pause();
    });
  }, { threshold: 0.4 });

  function player(m) {
    const ratio = m.w && m.h ? m.w / m.h : 9 / 16;
    // Without a poster, start at a tiny offset so browsers paint the first frame.
    const v = el("video", {
      src: m.poster ? m.url : m.url + "#t=0.1", poster: m.poster || null, muted: true, loop: true, playsinline: true, preload: "metadata",
    });
    v.muted = true;
    const btn = el("button", { type: "button", class: "play" }, [el("span", { class: "play-dot" }), T[state.lang].play]);
    const box = el("div", { class: "player", style: { aspectRatio: ratio, "--r": ratio } }, [v, btn]);
    btn.addEventListener("click", () => {
      v.dataset.user = "1"; v.muted = false; v.controls = true; v.currentTime = 0; v.play();
      box.classList.add("is-live");
    });
    if (videoIO) videoIO.observe(v);
    return box;
  }

  function renderMotion(ch, idx, nested) {
    const L = T[state.lang];
    const sec = el(nested ? "div" : "section", { class: "ch ch--motion" + (ch.media.length > 1 ? " is-multi" : "") });
    if (!nested) add(sec, el("h2", { class: "eyebrow-title" }, L.motion + " · " + L.films(ch.media.length)));
    add(sec, el("div", { class: "motion" }, ch.media.map((m) =>
      el("article", { class: "film" }, [player(m), m.text ? textBlock(m.caption, m.text) : null]))));
    return sec;
  }

  function renderCompare(ch) {
    const L = T[state.lang];
    const ratio = ch.after.w && ch.after.h ? ch.after.w / ch.after.h : 4 / 5;
    const range = el("input", { type: "range", min: "0", max: "100", value: "50", "aria-label": L.drag, class: "cmp-range" });
    const box = el("div", { class: "cmp", style: { aspectRatio: ratio, "--r": ratio, "--x": "50%" } }, [
      el("img", { src: ch.after.src, alt: ch.labels[1] || L.after, loading: "lazy" }),
      el("div", { class: "cmp-before" }, el("img", { src: ch.before.src, alt: ch.labels[0] || L.before, loading: "lazy" })),
      el("span", { class: "cmp-tag cmp-tag--b" }, ch.labels[0] || L.before),
      el("span", { class: "cmp-tag cmp-tag--a" }, ch.labels[1] || L.after),
      el("span", { class: "cmp-handle", "aria-hidden": "true" }),
      range,
    ]);
    range.addEventListener("input", () => box.style.setProperty("--x", range.value + "%"));
    return el("section", { class: "ch ch--compare" }, [
      el("div", { class: "single" }, [box, textBlock(ch.caption, ch.text, { meta: L.drag })]),
    ]);
  }

  function renderHero(d) {
    const L = T[state.lang];
    const facts = [
      d.client && [L.client, d.client.name],
      d.sector.length && [L.sector, d.sector.join(", ")],
      d.location && [L.location, d.location],
    ].filter(Boolean);
    const counts = [d.photos ? L.photos(d.photos) : "", d.films ? L.films(d.films) : ""].filter(Boolean).join(" · ");
    const wide = d.cover && d.cover.w >= 1800 && d.cover.w / d.cover.h > 1.2;
    const text = el("div", { class: "hero-text" }, [
      d.client && d.client.logo ? el("img", { class: "client-logo", src: d.client.logo, alt: d.client.name }) : null,
      el("h1", { class: "hero-title" }, d.title),
      counts ? el("p", { class: "hero-counts" }, counts) : null,
      el("dl", { class: "facts" }, facts.map(([k, v]) => el("div", {}, [el("dt", {}, k), el("dd", {}, v)]))),
    ]);
    const hero = el("header", { class: "hero" + (wide ? " hero--wide" : "") }, [text]);
    if (d.cover) {
      const m = Object.assign({ type: "photo", caption: d.title }, d.cover);
      add(hero, el("div", { class: "hero-media" }, frame(m, { eager: true, cls: "frame--hero" })));
    }
    return hero;
  }

  function renderIntro(d) {
    const L = T[state.lang];
    if (!d.text.lead && !d.text.paras.length && !d.services.length) return null;
    return el("section", { class: "intro" }, [
      el("div", { class: "intro-body" }, [
        d.text.lead ? el("p", { class: "ch-lead" }, d.text.lead) : null,
        ...d.text.paras.map((p, i) => el("p", { class: i === 0 ? "intro-first" : "ch-para" }, p)),
      ]),
      d.services.length ? el("div", { class: "services" }, [
        el("h2", { class: "label" }, L.services),
        el("ul", {}, d.services.map((s) => el("li", {}, s))),
      ]) : null,
    ]);
  }

  function renderOutro(d, related) {
    const L = T[state.lang];
    const wa = "https://wa.me/" + cfg.contact.whatsapp + "?text=" + encodeURIComponent(L.waText(d.title));
    const out = el("footer", { class: "outro" });
    if (d.cast.length) {
      add(out, el("section", { class: "crew" }, [
        el("h2", { class: "label" }, L.crew),
        el("ul", {}, d.cast.map((c) => el("li", {}, [el("span", { class: "crew-role" }, c.role), el("span", { class: "crew-name" }, c.name)]))),
      ]));
    }
    add(out, el("section", { class: "ask" }, [
      el("h2", { class: "ask-title" }, L.ask),
      el("p", {}, L.askBody),
      el("div", { class: "ask-actions" }, [
        el("a", { class: "btn", href: wa, target: "_blank", rel: "noopener" }, L.whatsapp),
        el("span", { class: "ask-phone" }, [L.or + " ", el("span", { class: "num", dir: "ltr" }, cfg.contact.phone)]),
      ]),
    ]));
    if (related && related.length) {
      add(out, el("section", { class: "related" }, [
        el("h2", { class: "label" }, L.more + " " + d.sector.join(", ")),
        el("ul", {}, related.slice(0, 4).map((p) => {
          const c = p.mainCover || p.fullMainCover;
          return el("li", {}, el("a", { href: cfg.projectHref(slugOf(p)) }, [
            c && c.url ? el("img", { src: sized(c.url, 600), alt: "", loading: "lazy" }) : null,
            el("span", {}, pick(p.name, state.lang)),
          ]));
        })),
      ]));
    }
    return out;
  }

  /* ---------- lightbox ---------- */

  function makeLightbox() {
    const L = T[state.lang];
    const img = el("img", { alt: "" });
    const cap = el("p", { class: "lb-cap" });
    const count = el("p", { class: "lb-count", dir: "ltr" });
    const box = el("div", { class: "lb", role: "dialog", "aria-modal": "true", hidden: true }, [
      el("div", { class: "lb-stage" }, img),
      el("div", { class: "lb-bar" }, [cap, count]),
      el("button", { type: "button", class: "icon-btn lb-close", "aria-label": L.close, onclick: () => close() }, "✕"),
      el("button", { type: "button", class: "icon-btn lb-prev", "aria-label": L.prev, onclick: () => go(-1) }, arrow(-1)),
      el("button", { type: "button", class: "icon-btn lb-next", "aria-label": L.next, onclick: () => go(1) }, arrow(1)),
    ]);
    let at = 0, lastFocus = null;
    const show = () => {
      const m = lbItems[at];
      img.src = m.url && cfg.imageProxy ? sized(m.url, 2400) : m.url || m.src;
      img.alt = m.caption || "";
      cap.textContent = m.caption || "";
      count.textContent = (at + 1) + " / " + lbItems.length;
    };
    const go = (d) => {
      const rtl = state.lang === "ar" ? -1 : 1;
      at = (at + d * rtl + lbItems.length) % lbItems.length;
      show();
    };
    const close = () => { box.hidden = true; document.body.classList.remove("lb-open"); lastFocus && lastFocus.focus(); };
    box.addEventListener("click", (e) => { if (e.target === box || e.target.classList.contains("lb-stage")) close(); });
    document.addEventListener("keydown", (e) => {
      if (box.hidden) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowRight") go(state.lang === "ar" ? -1 : 1);
      if (e.key === "ArrowLeft") go(state.lang === "ar" ? 1 : -1);
    });
    let sx = null;
    box.addEventListener("touchstart", (e) => { sx = e.touches[0].clientX; }, { passive: true });
    box.addEventListener("touchend", (e) => {
      if (sx == null) return;
      const dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 50) go(dx < 0 ? (state.lang === "ar" ? -1 : 1) : (state.lang === "ar" ? 1 : -1));
      sx = null;
    });
    return {
      node: box,
      open(i) {
        lastFocus = document.activeElement;
        at = i; show(); box.hidden = false; document.body.classList.add("lb-open");
        box.querySelector(".lb-close").focus();
      },
    };
  }

  /* ---------- page ---------- */

  const state = { lang: cfg.lang, raw: null, all: null };
  const root = document.getElementById("showcase") || document.body.appendChild(el("main", { id: "showcase" }));

  async function load() {
    root.setAttribute("aria-busy", "true");
    if (cfg.source === "api") {
      const res = await fetch(cfg.api);
      const all = (await res.json()).projects.filter((p) => p.published !== false && !p.deleted);
      state.all = all;
      const want = cfg.slug || new URLSearchParams(location.search).get("slug") ||
        location.hash.slice(1) || location.pathname.split("/").filter(Boolean).pop();
      state.raw = all.find((p) => slugOf(p) === want) || (cfg.picker ? all[0] : null);
    } else {
      state.raw = await (await fetch(cfg.source)).json();
    }
    await render();
  }

  async function render() {
    const L = T[state.lang];
    document.documentElement.lang = state.lang;
    document.documentElement.dir = state.lang === "ar" ? "rtl" : "ltr";
    lbItems.length = 0;
    root.textContent = "";
    if (!state.raw) {
      add(root, el("p", { class: "empty" }, L.notFound));
      return;
    }
    const d = normalize(state.raw, state.lang);
    document.title = d.title + " | Saber Group";

    // Measure every photo first so each section's layout is decided on real shapes.
    const all = [d.cover].concat(...d.chapters.map((c) =>
      c.kind === "compare" ? [c.before, c.after] : c.media.filter((m) => m.type === "photo"))).filter(Boolean);
    await Promise.all(all.map(measure));
    d.chapters.forEach((c) => c.kind === "gallery" && lbItems.push(...c.media.filter((m) => m.type === "photo")));

    lightbox = makeLightbox();
    const related = state.all
      ? state.all.filter((p) => p !== state.raw && (p.categories || []).some((c) => d.categoryIds.includes(c._id)))
      : [];

    add(root, topbar(d), renderHero(d));
    const intro = renderIntro(d);
    if (intro) add(root, intro);
    let g = 0;
    d.chapters.forEach((ch) => {
      if (ch.kind === "gallery") add(root, renderGallery(ch, g++));
      else if (ch.kind === "motion") add(root, renderMotion(ch, g++));
      else if (ch.kind === "compare") add(root, renderCompare(ch));
    });
    add(root, renderOutro(d, related), lightbox.node);
    root.removeAttribute("aria-busy");
  }

  function topbar(d) {
    const L = T[state.lang];
    const bar = el("nav", { class: "topbar" }, [
      el("a", { class: "back", href: cfg.portfolioHref || "/portfolio" }, [arrow(state.lang === "ar" ? 1 : -1), L.portfolio]),
      el("span", { class: "topbar-title" }, d.title),
      el("div", { class: "topbar-end" }, [
        cfg.picker && state.all ? pickerSelect() : null,
        el("button", {
          type: "button", class: "lang", onclick: () => { state.lang = state.lang === "ar" ? "en" : "ar"; render(); },
        }, state.lang === "ar" ? "EN" : "ع"),
      ]),
      el("span", { class: "progress", "aria-hidden": "true" }),
    ]);
    return bar;
  }

  function pickerSelect() {
    const s = el("select", { id: "project-picker", class: "picker", "aria-label": T[state.lang].other },
      state.all.map((p) => el("option", { value: slugOf(p), selected: p === state.raw }, pick(p.name, state.lang))));
    s.addEventListener("change", () => {
      state.raw = state.all.find((p) => slugOf(p) === s.value);
      history.replaceState(null, "", "?slug=" + encodeURIComponent(s.value));
      render().then(() => window.scrollTo(0, 0));
    });
    return s;
  }

  addEventListener("scroll", () => {
    const p = $(".progress");
    if (!p) return;
    const max = document.documentElement.scrollHeight - innerHeight;
    p.style.setProperty("--p", max > 0 ? scrollY / max : 0);
    document.documentElement.classList.toggle("past-hero", scrollY > innerHeight * 0.6);
  }, { passive: true });

  load().catch((e) => {
    root.textContent = "";
    add(root, el("p", { class: "empty" }, "Couldn't load the project: " + e.message));
  });
})();
