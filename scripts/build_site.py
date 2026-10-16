#!/usr/bin/env python3
"""Build the dependency-free GitHub Pages site from the two source catalogs."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
OUTPUT = ROOT / "dist"
SITE_URL = "https://awesomerea.org"
REPOSITORY_URL = "https://github.com/reacher-z/Awesome-REA"
TARGETS = {"website", "game", "app", "binary", "firmware"}


def group_for(record: dict) -> str:
    relationship = record["relationship"]
    if relationship == "independent-agent-integration":
        return "agents"
    if relationship == "foundation":
        return "tools"
    if relationship in {"learning", "community-learning-resource", "upstream-maintainer-companion-list"}:
        return "learn"
    return "rea"


def default_targets(record: dict) -> list[str]:
    """Conservative domain labels, never an assertion of REA compatibility."""
    category = record["category"]
    text = " ".join(str(record.get(k, "")) for k in ("id", "name", "description_en")).lower()
    if category == "core":
        return sorted(TARGETS)
    found: set[str] = set()
    if category in {"javascript-electron", "android", "dotnet"} or any(w in text for w in ("electron", "android", "aegis", "notion", "managed-code")):
        found.add("app")
    if category == "webassembly" or any(w in text for w in ("browser", "network capture", "web capture", "javascript", "webcrack")):
        found.add("website")
    if category == "firmware" or "firmware" in text:
        found.add("firmware")
    if any(w in text for w in ("dx-ball", "th04", "game", "unity")):
        found.add("game")
    if category in {"native-analysis", "dynamic-analysis", "binary-libraries", "binary-diffing", "agent-mcp", "agent-workflows", "learning"} or "native" in text:
        found.add("binary")
    return sorted(found or {"binary"})


def main() -> None:
    translations = json.loads((SOURCE / "translations.zh-CN.json").read_text(encoding="utf-8"))
    resources = []
    for filename in ("rea-resources.json", "tool-resources.json"):
        for original in json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")):
            record = dict(original)
            if isinstance(record["requirements"], str):
                record["requirements"] = [record["requirements"]]
            translation = translations.get(record["id"], {})
            record["requirements_zh"] = record.get("requirements_zh") or translation.get("requirements", record["requirements"])
            record["name_zh"] = record.get("name_zh") or translation.get("name", record["name"])
            record["group"] = group_for(record)
            targets = record.get("targets") or default_targets(record)
            if not isinstance(targets, list) or not set(targets).issubset(TARGETS):
                raise ValueError(f"Invalid targets: {record['id']}")
            record["targets"] = sorted(set(targets))
            resources.append(record)
    ids = [r["id"] for r in resources]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate catalog IDs")
    playbooks = (ROOT / "docs" / "playbooks.md").read_text(encoding="utf-8")
    playbook_count = len(re.findall(r"^## ", playbooks, flags=re.MULTILINE))
    latest_review = max(record["verified_at"] for record in resources)
    metadata = {"site_url": SITE_URL, "repository_url": REPOSITORY_URL, "resource_count": len(resources), "independent_integration_count": sum(r["group"] == "agents" for r in resources), "playbook_count": playbook_count, "latest_review": latest_review, "verification_note": "Catalog resources are source-reviewed. One CLI run and three original-fixture tests are recorded separately in the lab."}
    OUTPUT.mkdir(exist_ok=True)
    for path in SOURCE.iterdir():
        if path.name == "translations.zh-CN.json":
            continue
        if path.is_dir():
            shutil.copytree(path, OUTPUT / path.name, dirs_exist_ok=True)
        else:
            shutil.copy2(path, OUTPUT / path.name)
    html = (OUTPUT / "index.html").read_text(encoding="utf-8")
    for key, value in {"RESOURCE_COUNT": len(resources), "INTEGRATION_COUNT": metadata["independent_integration_count"], "PLAYBOOK_COUNT": str(playbook_count).zfill(2), "REVIEWED_AT": latest_review}.items():
        html = html.replace("{{" + key + "}}", str(value))
    (OUTPUT / "index.html").write_text(html, encoding="utf-8")
    (OUTPUT / "catalog.json").write_text(json.dumps({"meta": metadata, "resources": resources}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUTPUT / "CNAME").write_text("awesomerea.org\n", encoding="utf-8")
    (OUTPUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (OUTPUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE_URL}/</loc><lastmod>{latest_review}</lastmod></url></urlset>\n', encoding="utf-8")
    print(f"Built {len(resources)} resources, {playbook_count} playbooks → dist/ ({SITE_URL})")


if __name__ == "__main__":
    main()
