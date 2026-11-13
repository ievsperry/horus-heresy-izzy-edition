"""Build the files BattleScribe and New Recruit update from, for one release.

This replaces the BSData/publish-catpkg action, which GitHub can no longer resolve. It writes, into dist/:

- one .catz / .gstz per data file (a zip holding the file under its own name),
- <repo>.catpkg.json and .catpkg.json.gz (the repository description the apps read),
- <repo>.latest.bsi and <repo>.<tag>.bsi (the data index, a zip holding <name>.xml),
- <repo>.<tag>.bsr (every data file and an index.xml, for a one-file download),

with the same names and contents the action produced (v2.1.7 and earlier). Run from the repository root:

    python3 .github/scripts/publish_catpkg.py <owner/repo> <tag> <published-at> <release name>
"""
import gzip
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET

INDEX_NS = "http://www.battlescribe.net/schema/dataIndexSchema"


def asset_name(path, ext):
    """GitHub's name for an uploaded asset: "Homebrew - Aeldari (Asuryani).cat" is "Homebrew.-.Aeldari.Asuryani"."""
    stem = re.sub(r"[^A-Za-z0-9_.-]+", ".", path.stem)
    stem = re.sub(r"\.{2,}", ".", stem).strip(".")
    return stem + ext


def read_head(path):
    """The root element's attributes: id, name, revision, battleScribeVersion, authorName."""
    for _, el in ET.iterparse(path, events=("start",)):
        return el.tag.split("}")[-1], dict(el.attrib)


def index_xml(name, entries, index_url=None, ext_z=True):
    attrs = f'battleScribeVersion="2.03" name="{escape(name)}"'
    if index_url:
        attrs += f' indexUrl="{escape(index_url)}"'
    lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
             f'<dataIndex {attrs} xmlns="{INDEX_NS}">', "  <dataIndexEntries>"]
    for e in entries:
        path = e["zname"] if ext_z else e["rname"]
        lines.append(f'    <dataIndexEntry filePath="{escape(path)}" dataType="{e["type"]}" dataId="{e["id"]}" '
                     f'dataName="{escape(e["name"])}" dataBattleScribeVersion="{e["bs"]}" dataRevision="{e["revision"]}"/>')
    lines += ["  </dataIndexEntries>", "</dataIndex>", ""]
    return "\n".join(lines).encode("utf-8")


def escape(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;").replace("'", "&apos;").replace("<", "&lt;")
             .replace(">", "&gt;"))


def main():
    repo_full, tag, published, title = sys.argv[1:5]
    owner, repo = repo_full.split("/")
    gh = f"https://github.com/{repo_full}"
    dl = f"{gh}/releases/download/{tag}"
    latest = f"{gh}/releases/latest/download"
    dist = Path("dist")
    dist.mkdir(exist_ok=True)

    files = sorted(list(Path(".").glob("*.gst")) + list(Path(".").glob("*.cat")))
    entries = []
    for p in files:
        kind, a = read_head(p)
        dtype = "gamesystem" if kind == "gameSystem" else "catalogue"
        ext = ".gstz" if dtype == "gamesystem" else ".catz"
        e = dict(path=p, type=dtype, id=a["id"], name=a.get("name", p.stem), revision=int(a.get("revision", 1)),
                 bs=a.get("battleScribeVersion", "2.03"), author=a.get("authorName"),
                 contact=a.get("authorContact"), url=a.get("authorUrl"),
                 zname=asset_name(p, ext), rname=asset_name(p, p.suffix))
        entries.append(e)
        with zipfile.ZipFile(dist / e["zname"], "w", zipfile.ZIP_DEFLATED) as z:
            z.write(p, p.name)

    system = next(e for e in entries if e["type"] == "gamesystem")
    pkg = {
        "$schema": "https://raw.githubusercontent.com/BSData/schemas/master/src/catpkg.schema.json",
        "name": repo,
        "description": system["name"].split(" - ")[0],
        "battleScribeVersion": "2.03",
        "version": tag,
        "lastUpdated": published,
        "lastUpdateDescription": title,
        "indexUrl": f"{latest}/{repo}.latest.bsi",
        "repositoryUrl": f"{latest}/{repo}.catpkg.json",
        "repositoryGzipUrl": f"{latest}/{repo}.catpkg.json.gz",
        "repositoryBsrUrl": f"{dl}/{repo}.{tag}.bsr",
        "githubUrl": gh,
        "feedUrl": f"{gh}/releases.atom",
        "bugTrackerUrl": f"{gh}/issues",
        "reportBugUrl": f"http://battlescribedata.appspot.com/#/repo/{repo}",
        "repositoryFiles": [{
            "id": e["id"],
            "name": e["name"],
            "type": e["type"],
            "revision": e["revision"],
            "battleScribeVersion": e["bs"],
            "fileUrl": f"{dl}/{e['zname']}",
            "githubUrl": f"{gh}/blob/main/{quote(e['path'].name)}",
            "bugTrackerUrl": f"{gh}/issues",
            "reportBugUrl": f"http://battlescribedata.appspot.com/#/repo/{repo}",
            "authorName": e["author"],
            "authorContact": e["contact"],
            "authorUrl": e["url"],
            "sourceSha256": hashlib.sha256(e["path"].read_bytes()).hexdigest().upper(),
        } for e in entries],
    }
    body = json.dumps(pkg, indent=2, ensure_ascii=False).encode("utf-8")
    (dist / f"{repo}.catpkg.json").write_bytes(body)
    (dist / f"{repo}.catpkg.json.gz").write_bytes(gzip.compress(body))

    name = pkg["description"]
    for bsi in (f"{repo}.latest.bsi", f"{repo}.{tag}.bsi"):
        inner = bsi[:-4] + ".xml"
        with zipfile.ZipFile(dist / bsi, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr(inner, index_xml(name, entries, pkg["indexUrl"]))
    with zipfile.ZipFile(dist / f"{repo}.{tag}.bsr", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.xml", index_xml(name, entries, ext_z=False))
        for e in entries:
            z.write(e["path"], e["rname"])
    print(f"{len(entries)} data files; {len(list(dist.iterdir()))} assets in dist/")


if __name__ == "__main__":
    main()
