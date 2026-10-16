#!/usr/bin/env python3
"""Package one portfolio project for an offline preview of the showcase page.

Pulls the project from the public projects API, downloads its media, resizes
photos (long edge 1600px), re-encodes videos to 540p, records every photo's
real width/height, and writes:

    <out>/project.json   API project with URLs rewritten to local media/ paths
    <out>/media/*        photos, video posters, compressed videos

The live page (index.html) does not need this: it reads the API directly and
measures images in the browser. This exists for previews that cannot reach
the API or the upload host (sandboxed viewers, slow links, offline review).

Usage: python3 build_preview.py <slug> <out_dir>
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.request

from PIL import Image

API = "https://marketing-planner-tau.vercel.app/api/v1/projects/public?PageCount=all"
LONG_EDGE = 1600

# The upload host rejects urllib's default user agent.
_opener = urllib.request.build_opener()
_opener.addheaders = [("User-Agent", "Mozilla/5.0 (saber-showcase-preview)")]
urllib.request.install_opener(_opener)


def slugify(text):
    text = unicodedata.normalize("NFD", text or "")
    text = "".join(c for c in text if unicodedata.category(c) != "Mn").lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"\s+", "-", text)


def project_slug(p):
    return p.get("slug") or slugify((p.get("name") or {}).get("en", "")) or p["_id"]


def fetch(url, dest):
    if not os.path.exists(dest):
        urllib.request.urlretrieve(url, dest)
    return dest


def main(slug, out):
    media_dir = os.path.join(out, "media")
    raw_dir = os.path.join(out, ".raw")
    os.makedirs(media_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)

    with urllib.request.urlopen(API) as r:
        projects = json.load(r)["projects"]
    project = next((p for p in projects if project_slug(p) == slug), None)
    if not project:
        sys.exit(f"No project with slug {slug!r}")

    seen = {}

    def local(url, kind="photo"):
        """Download url, write a web-sized copy into media/, return its record."""
        if not url:
            return None
        if url in seen:
            return seen[url]
        name = url.rsplit("/", 1)[-1]
        raw = fetch(url, os.path.join(raw_dir, name))
        stem = os.path.splitext(name)[0]
        if kind == "video":
            dest = os.path.join(media_dir, stem + ".mp4")
            if not os.path.exists(dest):
                subprocess.run(
                    ["ffmpeg", "-v", "error", "-y", "-i", raw,
                     "-vf", "scale='if(gt(iw,ih),960,540)':-2",
                     "-c:v", "libx264", "-crf", "30", "-preset", "slow",
                     "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", dest],
                    check=True)
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=width,height", "-of", "csv=p=0", dest],
                capture_output=True, text=True, check=True).stdout.strip().split(",")
            rec = {"url": "media/" + stem + ".mp4", "w": int(probe[0]), "h": int(probe[1])}
        else:
            ext = ".png" if url.lower().endswith(".png") and "logo" in kind else ".jpg"
            dest = os.path.join(media_dir, stem + ext)
            im = Image.open(raw)
            w, h = im.size
            if not os.path.exists(dest):
                im.thumbnail((LONG_EDGE, LONG_EDGE))
                if ext == ".jpg":
                    im.convert("RGB").save(dest, quality=80, optimize=True, progressive=True)
                else:
                    im.save(dest, optimize=True)
            rec = {"url": "media/" + stem + ext, "w": w, "h": h}
        seen[url] = rec
        return rec

    def poster(video_path):
        """Grab a frame 1s in, for videos uploaded without a cover image."""
        dest = os.path.join(out, video_path.replace(".mp4", "-poster.jpg"))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", os.path.join(out, video_path),
                        "-frames:v", "1", "-q:v", "4", dest], check=True)
        return video_path.replace(".mp4", "-poster.jpg")

    def apply(obj, rec):
        if rec:
            obj["url"], obj["w"], obj["h"] = rec["url"], rec["w"], rec["h"]

    for key in ("mainCover", "fullMainCover"):
        if project.get(key):
            apply(project[key], local(project[key]["url"]))
    company = project.get("company") or {}
    if company.get("logo"):
        company["logo"] = local(company["logo"], "logo")["url"]

    for m in project.get("material") or []:
        if m["type"] == "video":
            if m.get("thumbnail"):
                m["thumbnail"] = local(m["thumbnail"])["url"]
            apply(m, local(m.get("url"), "video"))
            if not m.get("thumbnail") and m.get("url"):
                m["thumbnail"] = poster(m["url"])
        elif m["type"] == "before_after":
            for side in ("before", "after"):
                if m.get(side):
                    apply(m[side], local(m[side].get("url")))
        else:
            if m.get("url"):
                apply(m, local(m["url"]))
            for item in m.get("items") or []:
                apply(item, local(item["url"], "video" if item.get("type") == "video" else "photo"))

    with open(os.path.join(out, "project.json"), "w") as f:
        json.dump(project, f, ensure_ascii=False)
    print(f"{project['name']['en']}: {len(seen)} files -> {out}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
