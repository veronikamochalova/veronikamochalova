#!/usr/bin/env python3
"""Deploy the static site to IPFS Ninja via folder upload + snapshot."""

from __future__ import annotations

import base64
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

API = "https://api.ipfs.ninja"
ROOT = pathlib.Path(__file__).resolve().parent.parent
EXCLUDE = {".git", "scripts", "ipfs-cid.txt"}


def request(method: str, path: str, key: str, data: dict | None = None) -> dict:
    body = None
    headers = {"X-Api-Key": key}
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{API}{path}", data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    key = os.environ.get("IPFS_NINJA_API_KEY")
    if not key:
        print("Set IPFS_NINJA_API_KEY before running.", file=sys.stderr)
        return 1

    folder = request("POST", "/folders", {"name": f"veronika-site-{int(time.time())}"}, key)
    folder_id = folder["folderId"]
    print(f"Created folder: {folder_id}")

    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.split("/")[0] in EXCLUDE or rel == "ipfs-cid.txt":
            continue
        files.append((rel, path))

    for rel, path in files:
        payload = {
            "content": base64.b64encode(path.read_bytes()).decode(),
            "fileName": rel,
            "description": rel,
            "folderId": folder_id,
        }
        result = request("POST", "/upload/new", key, payload)
        print(f"Uploaded {rel} -> {result['cid']}")

    for attempt in range(5):
        try:
            snapshot = request("POST", f"/folders/{folder_id}/snapshot", key, {})
            break
        except urllib.error.HTTPError as err:
            if err.code in {503, 429} and attempt < 4:
                time.sleep(4)
                continue
            raise
    else:
        print("Snapshot failed.", file=sys.stderr)
        return 1

    cid = snapshot["cid"]
    ipfs_url = snapshot.get("ipfsUrl") or f"https://ipfs.ninja/ipfs/{cid}/"
    (ROOT / "ipfs-cid.txt").write_text(f"{cid}\n", encoding="utf-8")

    print("\nDeployed to IPFS Ninja")
    print(f"CID: {cid}")
    print(f"URL: {ipfs_url}")
    print("\nIf the gateway returns 410, pin the CID in IPFS Ninja or free file quota first.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())