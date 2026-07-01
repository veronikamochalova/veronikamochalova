#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGING="$(mktemp -d)"
CID_FILE="$ROOT/ipfs-cid.txt"

if ! command -v ipfs >/dev/null; then
  echo "IPFS (kubo) not found. Install from https://docs.ipfs.tech/install/"
  exit 1
fi

if ! ipfs id >/dev/null 2>&1; then
  echo "Start the IPFS daemon first: ipfs daemon"
  exit 1
fi

rsync -a \
  --exclude='.git' \
  --exclude='scripts' \
  --exclude='ipfs-cid.txt' \
  "$ROOT/" "$STAGING/"

CID="$(ipfs add -r -Q --cid-version=1 "$STAGING")"
ipfs pin add "$CID" >/dev/null

printf '%s\n' "$CID" > "$CID_FILE"
rm -rf "$STAGING"

echo "Deployed to IPFS"
echo "CID: $CID"
echo "Gateways:"
echo "  https://ipfs.io/ipfs/$CID/"
echo "  https://dweb.link/ipfs/$CID/"
echo "  https://cloudflare-ipfs.com/ipfs/$CID/"
echo ""
echo "For 24/7 public access, pin this CID on Pinata or web3.storage."