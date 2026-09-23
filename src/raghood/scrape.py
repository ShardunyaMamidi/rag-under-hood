"""Download the Flask docs (pinned version) as raw .rst files.

The docs website sits behind Cloudflare and blocks Jina Reader, so we read
the same docs from the open-source repo instead: one tarball from the GitHub
API (per-file downloads from raw.githubusercontent.com were far too slow).
"""
import io
import json
import tarfile
from pathlib import Path

import requests

REPO = "pallets/flask"
REF = "3.1.0"  # pinned tag so the corpus is reproducible
ROOT = Path(__file__).resolve().parents[2]  # project root, so paths work from any cwd (notebooks too)
RAW_DIR = ROOT / "data" / "raw"
MIN_BYTES = 200  # skip stub pages that only `include::` another file


def scrape_all(ref: str = REF, out_dir: Path = RAW_DIR) -> list[dict]:
    """Download all docs/*.rst to out_dir and write manifest.jsonl."""
    r = requests.get(f"https://api.github.com/repos/{REPO}/tarball/{ref}", timeout=120)
    r.raise_for_status()
    tar = tarfile.open(fileobj=io.BytesIO(r.content))

    out_dir.mkdir(parents=True, exist_ok=True)
    version = ref.rsplit(".", 1)[0] + ".x"
    manifest = []
    for member in sorted(tar.getmembers(), key=lambda m: m.name):
        # member.name looks like "pallets-flask-<sha>/docs/patterns/caching.rst"
        _, _, path = member.name.partition("/")
        if not (member.isfile() and path.startswith("docs/") and path.endswith(".rst")):
            continue
        if member.size < MIN_BYTES:
            continue
        rel = path.removeprefix("docs/")
        text = tar.extractfile(member).read().decode("utf-8")
        dest = out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        page = rel.removesuffix(".rst")
        manifest.append({
            "page": page,
            "path": dest.relative_to(ROOT).as_posix(),
            "url": f"https://flask.palletsprojects.com/en/{version}/{page}/",
            "source": f"https://github.com/{REPO}/blob/{ref}/{path}",
            "words": len(text.split()),
        })

    with open(out_dir / "manifest.jsonl", "w", encoding="utf-8") as f:
        for m in manifest:
            f.write(json.dumps(m) + "\n")
    return manifest


if __name__ == "__main__":
    m = scrape_all()
    print(f"{len(m)} pages, {sum(x['words'] for x in m)} words")
