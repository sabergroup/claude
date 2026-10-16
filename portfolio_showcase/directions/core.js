/*
 * Shared core for the showcase design directions.
 *
 * Loads one project (live API or a packaged project.json), turns it into a
 * page model, measures every photo, and hands the model to whichever
 * direction is active. Directions only decide how things look; what goes on
 * the page (sections, photo order, text split, crew, contact) is decided here
 * once, so every direction stays automatic for every project.
 *
 * A direction registers itself with:
 *   SC.direction("name", { label: [en, ar], render(d, root, ctx) })
 */
(function () {
  "use strict";

  const SC = (window.SC = {});
  const cfg = (SC.cfg = Object.assign(
    {
      source: "api",
      api: "https://marketing-planner-tau.vercel.app/api/v1/projects/public?PageCount=all",
      imageProxy: "",
      lang: "en",
      contact: { whatsapp: "201080099757", phone: "01080099757" },
    },
    window.SHOWCASE || {}
  ));

  /* ---------- DOM helpers ---------- */

  const el = (SC.el = (tag, attrs, kids) => {
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
    [].concat(kids == null ? [] : kids).forEach((c) => {
      if (c == null || c === false || c === "") return;
      n.append(c.nodeType ? c : String(c));
    });
    return n;
  });

  const clean = (SC.clean = (s) =>
    String(s || "").replace(/[​‌‍﻿]/g, "").replace(/[ \t]+\n/g, "\n").trim());

  const pick = (SC.pick = (o, lang) => {
    if (!o) return "";
    if (typeof o === "string") return clean(o);
    return clean(o[lang]) || clean(o[lang === "ar" ? "en" : "ar"]);
  });

  // Editors separate paragraphs with blank lines or runs of 2+ spaces.
  // A short opening fragment with no full stop reads as the section's headline.
  const splitText = (SC.splitText = (text) => {
    const parts = clean(text).split(/\n\s*\n|\s{2,}/).map((s) => s.trim()).filter(Boolean);
    let lead = "";
    if (parts.length > 1 && parts[0].length <= 70 && !/[.!؟?]$/.test(parts[0])) lead = parts.shift();
    return { lead, paras: parts };
  });

  const slugify = (t) =>
    (t || "").normalize("NFD").replace(/\p{Diacritic}/gu, "")
      .toLowerCase().trim().replace(/[^a-z0-9\s-]/g, "").replace(/\s+/g, "-");
  const slugOf = (SC.slugOf = (p) => p.slug || slugify(p.name && p.name.en) || p._id);

  const sized = (SC.sized = (url, width) =>
    cfg.imageProxy && /^https?:/.test(url)
      ? cfg.imageProxy + "/?url=" + encodeURIComponent(url) + "&w=" + width + "&q=82&output=jpg"
      : url);

  SC.roman = (n) => {
    const map = [[10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]];
    let out = "";
    for (const [v, s] of map) while (n >= v) { out += s; n -= v; }
    return out;
  };
  SC.pad = (n) => String(n).padStart(2, "0");
  SC.t = (en, ar) => (state.lang === "ar" ? ar : en);
  SC.isPortrait = (m) => m.w / m.h < 0.95;

  function measure(m) {
    if (m.w && m.h) return Promise.resolve(m);
    return new Promise((res) => {
      const img = new Image();
      img.onload = () => { m.w = img.naturalWidth; m.h = img.naturalHeight; res(m); };
      img.onerror = () => { m.w = 4; m.h = 5; res(m); };
      img.src = m.src;
    });
  }

  /* ---------- API project -> page model ---------- */

  function normalize(p, lang) {
    const photo = (o, caption) => o && o.url && {
      type: "photo", url: o.url, src: sized(o.url, 1600), w: o.w, h: o.h, caption,
    };
    const chapters = [];
    const mats = (p.material || []).slice().sort((a, b) => (a.order || 0) - (b.order || 0));
    for (const m of mats) {
      const caption = pick(m.caption, lang);
      const text = splitText(pick(m.description, lang) || pick(m.textContent, lang));
      if (m.type === "video") {
        if (!m.url) continue;
        const v = { type: "video", url: m.url, poster: m.thumbnail || "", w: m.w, h: m.h, caption, text };
        const prev = chapters[chapters.length - 1];
        if (prev && prev.kind === "motion") prev.media.push(v);
        else chapters.push({ kind: "motion", caption: "", text: splitText(""), media: [v] });
      } else if (m.type === "before_after") {
        const b = photo(m.before, caption), a = photo(m.after, caption);
        if (b && a) chapters.push({
          kind: "compare", caption, text, media: [b, a],
          labels: [pick(m.before.label, lang) || SC.t("Before", "قبل"), pick(m.after.label, lang) || SC.t("After", "بعد")],
        });
      } else {
        const media = (m.items && m.items.length ? m.items : [m])
          .map((it) => (it.type === "video"
            ? { type: "video", url: it.url, poster: it.thumbnail || "", w: it.w, h: it.h, caption }
            : photo(it, caption)))
          .filter(Boolean);
        if (!media.length) continue;
        const prev = chapters[chapters.length - 1];
        if (!caption && !text.paras.length && !text.lead && prev && prev.kind === "gallery") {
          prev.media.push(...media);
          continue;
        }
        chapters.push({ kind: "gallery", caption, text, media });
      }
    }
    let plate = 0;
    chapters.forEach((c) => c.media.forEach((m) => { if (m.type === "photo") m.plate = ++plate; }));

    const company = p.company && !p.hideClientName ? p.company : null;
    const cover = p.fullMainCover || p.mainCover;
    const year = (clean(pick(p.name, "en")).match(/20\d\d/) || [new Date(p.createdAt || Date.now()).getFullYear()])[0];
    return {
      slug: slugOf(p),
      title: pick(p.name, lang),
      text: splitText(pick(p.description, lang)),
      client: company && { name: pick(company.name, lang), logo: company.logo || "" },
      sector: (p.categories || []).map((c) => pick(c.name, lang)).filter(Boolean),
      location: pick(p.location, lang),
      services: (p.types || []).map((t) => pick(t.name, lang)).filter(Boolean),
      cover: cover && cover.url ? { type: "photo", url: cover.url, src: sized(cover.url, 1800), w: cover.w, h: cover.h, caption: pick(p.name, lang) } : null,
      chapters,
      cast: (p.cast || []).slice().sort((a, b) => (a.order || 0) - (b.order || 0))
        .map((c) => ({ name: clean(c.castId && c.castId.name), role: clean(c.title) }))
        .filter((c) => c.name),
      photos: plate,
      films: chapters.reduce((n, c) => n + c.media.filter((x) => x.type === "video").length, 0),
      year,
      waLink: "https://wa.me/" + cfg.contact.whatsapp + "?text=" + encodeURIComponent(
        SC.t("Hi Saber Group, I saw \"" + pick(p.name, lang) + "\" and want a similar shoot.",
          "أهلاً صابر جروب، شفت مشروع \"" + pick(p.name, lang) + "\" وعايز شوت شبهه.")),
      phone: cfg.contact.phone,
    };
  }

  /* ---------- shared pieces directions reuse ---------- */

  // Photos register here in reading order so the viewer pages through them all.
  const lbItems = [];
  SC.img = (m, attrs) => {
    if (m.type === "photo" && !lbItems.includes(m)) lbItems.push(m);
    const img = el("img", Object.assign({
      src: m.src, alt: m.caption || "", loading: "lazy", decoding: "async", width: m.w, height: m.h, draggable: "false",
    }, attrs || {}));
    const done = () => img.classList.add("is-in");
    img.addEventListener("load", done);
    if (img.complete && img.naturalWidth) done();
    if (m.type === "photo") {
      img.classList.add("zoomable");
      img.addEventListener("click", () => SC.lightbox.open(lbItems.indexOf(m)));
    }
    return img;
  };

  const videoIO = "IntersectionObserver" in window && new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      const v = e.target;
      if (v.dataset.user) return;
      if (e.isIntersecting && !matchMedia("(prefers-reduced-motion: reduce)").matches) v.play().catch(() => {});
      else v.pause();
    });
  }, { threshold: 0.45 });

  SC.video = (m, cls) => {
    const v = el("video", {
      src: m.poster ? m.url : m.url + "#t=0.1", poster: m.poster || null,
      muted: true, loop: true, playsinline: true, preload: "metadata",
    });
    v.muted = true;
    const btn = el("button", { type: "button", class: "sc-play" }, SC.t("Play with sound", "تشغيل بالصوت"));
    const box = el("div", { class: "sc-video " + (cls || ""), style: { "--r": (m.w && m.h ? m.w / m.h : 9 / 16) } }, [v, btn]);
    btn.addEventListener("click", () => {
      v.dataset.user = "1"; v.muted = false; v.controls = true; v.currentTime = 0; v.play();
      box.classList.add("is-live");
    });
    if (videoIO) videoIO.observe(v);
    return box;
  };

  // Average colour of the most saturated pixels, used to tint a page to its photos.
  SC.palette = (src) => new Promise((res) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      try {
        const c = document.createElement("canvas");
        c.width = c.height = 40;
        const x = c.getContext("2d");
        x.drawImage(img, 0, 0, 40, 40);
        const px = x.getImageData(0, 0, 40, 40).data;
        const all = [];
        for (let i = 0; i < px.length; i += 4) {
          const [r, g, b] = [px[i], px[i + 1], px[i + 2]];
          const max = Math.max(r, g, b), min = Math.min(r, g, b);
          all.push({ r, g, b, s: max ? (max - min) / max : 0, l: max });
        }
        all.sort((a, b) => b.s * b.l - a.s * a.l);
        const top = all.slice(0, 200);
        const avg = (k) => top.reduce((s, p) => s + p[k], 0) / top.length;
        res(rgbToHsl(avg("r"), avg("g"), avg("b")));
      } catch (e) { res(null); }
    };
    img.onerror = () => res(null);
    img.src = src;
  });
  function rgbToHsl(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h = 0, s = 0;
    const l = (max + min) / 2;
    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      h = max === r ? (g - b) / d + (g < b ? 6 : 0) : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
      h *= 60;
    }
    return { h: Math.round(h), s: Math.round(s * 100), l: Math.round(l * 100) };
  }

  /* ---------- lightbox ---------- */

  function makeLightbox() {
    const img = el("img", { alt: "" });
    const cap = el("p", { class: "lb-cap" });
    const count = el("p", { class: "lb-count", dir: "ltr" });
    const box = el("div", { class: "lb", role: "dialog", "aria-modal": "true", hidden: true }, [
      el("div", { class: "lb-stage" }, img),
      el("div", { class: "lb-bar" }, [cap, count]),
      el("button", { type: "button", class: "lb-btn lb-close", "aria-label": SC.t("Close", "إغلاق"), onclick: () => close() }, "✕"),
      el("button", { type: "button", class: "lb-btn lb-prev", "aria-label": SC.t("Previous", "السابق"), onclick: () => go(-1) }, "←"),
      el("button", { type: "button", class: "lb-btn lb-next", "aria-label": SC.t("Next", "التالي"), onclick: () => go(1) }, "→"),
    ]);
    let at = 0, lastFocus = null;
    const show = () => {
      const m = lbItems[at];
      img.src = cfg.imageProxy ? sized(m.url, 2400) : m.src;
      img.alt = m.caption || "";
      cap.textContent = m.caption || "";
      count.textContent = (at + 1) + " / " + lbItems.length;
    };
    const go = (d) => { at = (at + d + lbItems.length) % lbItems.length; show(); };
    const close = () => { box.hidden = true; document.body.classList.remove("lb-open"); lastFocus && lastFocus.focus(); };
    box.addEventListener("click", (e) => { if (e.target === box || e.target.classList.contains("lb-stage")) close(); });
    let sx = null;
    box.addEventListener("touchstart", (e) => { sx = e.touches[0].clientX; }, { passive: true });
    box.addEventListener("touchend", (e) => {
      if (sx == null) return;
      const dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1);
      sx = null;
    });
    return {
      node: box,
      key(e) {
        if (box.hidden) return false;
        if (e.key === "Escape") close();
        else if (e.key === "ArrowRight") go(state.lang === "ar" ? -1 : 1);
        else if (e.key === "ArrowLeft") go(state.lang === "ar" ? 1 : -1);
        else return false;
        return true;
      },
      open(i) {
        lastFocus = document.activeElement;
        at = Math.max(0, i); show(); box.hidden = false; document.body.classList.add("lb-open");
        box.querySelector(".lb-close").focus();
      },
    };
  }

  /* ---------- page ---------- */

  const directions = {};
  const order = [];
  SC.direction = (name, def) => { directions[name] = def; order.push(name); };

  const state = (SC.state = { lang: cfg.lang, raw: null, current: null });
  let cleanups = [];
  // Listeners a direction adds through ctx.on are removed when it is swapped out.
  const ctx = {
    on(target, ev, fn, opts) { target.addEventListener(ev, fn, opts); cleanups.push(() => target.removeEventListener(ev, fn, opts)); },
    cleanup(fn) { cleanups.push(fn); },
  };

  document.addEventListener("keydown", (e) => { if (SC.lightbox && SC.lightbox.key(e)) e.preventDefault(); });

  async function draw() {
    cleanups.forEach((f) => f()); cleanups = [];
    const root = document.getElementById("showcase");
    const name = directions[state.current] ? state.current : order[0];
    state.current = name;
    const html = document.documentElement;
    html.lang = state.lang;
    html.dir = state.lang === "ar" ? "rtl" : "ltr";
    html.dataset.v = name;
    lbItems.length = 0;
    root.textContent = "";
    if (!state.raw) { root.append(el("p", { class: "sc-empty" }, SC.t("This project isn't published.", "المشروع ده مش منشور."))); return; }

    const d = normalize(state.raw, state.lang);
    const photos = [d.cover].concat(...d.chapters.map((c) => c.media.filter((m) => m.type === "photo"))).filter(Boolean);
    await Promise.all(photos.map(measure));
    d.chapters.forEach((c) => c.media.forEach((m) => m.type === "photo" && lbItems.push(m)));

    SC.lightbox = makeLightbox();
    const page = el("div", { class: "v-page v-" + name });
    root.append(page);
    await directions[name].render(d, page, ctx);
    root.append(switcher(), SC.lightbox.node);
    document.title = d.title + " | Saber Group";
  }

  function switcher() {
    const bar = el("nav", { class: "sc-switch", "aria-label": SC.t("Design direction", "اتجاه التصميم") });
    order.forEach((n, i) => {
      const lab = directions[n].label;
      bar.append(el("button", {
        type: "button", class: n === state.current ? "is-on" : "", "aria-pressed": String(n === state.current),
        onclick: () => {
          state.current = n;
          try { history.replaceState(null, "", "#" + n); } catch (e) {}
          draw().then(() => window.scrollTo(0, 0));
        },
      }, [el("span", { class: "sc-num" }, i + 1), SC.t(lab[0], lab[1])]));
    });
    bar.append(el("button", {
      type: "button", class: "sc-lang",
      onclick: () => { state.lang = state.lang === "ar" ? "en" : "ar"; draw(); },
    }, state.lang === "ar" ? "EN" : "ع"));
    return bar;
  }

  async function boot() {
    const root = document.getElementById("showcase");
    root.setAttribute("aria-busy", "true");
    const hash = location.hash.slice(1);
    state.current = directions[hash] ? hash : order[0];
    if (cfg.source === "api") {
      const all = (await (await fetch(cfg.api)).json()).projects.filter((p) => p.published !== false && !p.deleted);
      const want = cfg.slug || new URLSearchParams(location.search).get("slug");
      state.raw = all.find((p) => slugOf(p) === want) || all[0];
    } else {
      state.raw = await (await fetch(cfg.source)).json();
    }
    await draw();
    root.removeAttribute("aria-busy");
  }
  SC.boot = () => boot().catch((e) => {
    const root = document.getElementById("showcase");
    root.textContent = "";
    root.append(el("p", { class: "sc-empty" }, "Couldn't load the project: " + e.message));
  });
})();
