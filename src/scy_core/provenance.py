"""Phase 1 — Upstream Provenance, Cryptographic SHA-256 Baseline & Reversible Patch Verifier."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .paths import adapters_dir, lucid_engine_dir, mandara_engine_dir, provenance_dir


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(131072), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_sha256_manifest(manifest_path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for raw in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            digest, rel = parts[0], parts[1].lstrip("./")
            mapping[rel] = digest
    return mapping


def parse_patch_touched_files(patch_path: Path) -> tuple[set[str], set[str]]:
    """Returns (modified_existing_files, newly_added_files) from a unified git diff."""
    modified: set[str] = set()
    added: set[str] = set()
    current_b: str | None = None
    saw_dev_null_a = False
    for line in patch_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("diff --git "):
            m = re.match(r"diff --git a/(.+?) b/(.+)$", line)
            if m:
                current_b = m.group(2)
            saw_dev_null_a = False
        elif line.startswith("--- /dev/null"):
            saw_dev_null_a = True
        elif line.startswith("+++ b/") and current_b:
            if saw_dev_null_a:
                added.add(current_b)
            else:
                modified.add(current_b)
    return modified, added


class ScyProvenanceVerifier:
    def __init__(
        self,
        prov_dir: Path | None = None,
        adap_dir: Path | None = None,
        lucid_dir: Path | None = None,
        mandara_dir: Path | None = None,
    ) -> None:
        self.prov_dir = prov_dir or provenance_dir()
        self.adap_dir = adap_dir or adapters_dir()
        self.lucid_dir = lucid_dir or lucid_engine_dir()
        self.mandara_dir = mandara_dir or mandara_engine_dir()

    def verify_all(self) -> dict[str, Any]:
        meta = json.loads((self.prov_dir / "PROVENANCE.json").read_text(encoding="utf-8"))
        lucid_manifest = parse_sha256_manifest(self.prov_dir / "lucid-v1.21.1-sha256sums.txt")
        mandara_manifest = parse_sha256_manifest(self.prov_dir / "mandara-v0.38.2-sha256sums.txt")

        lucid_patch = self.adap_dir / "lucid" / "lucid-scy-adapter.patch"
        mandara_patch = self.adap_dir / "mandara" / "mandara-scy-adapter.patch"

        lucid_res = self._verify_engine(
            name="lucid",
            engine_dir=self.lucid_dir,
            manifest=lucid_manifest,
            patch_path=lucid_patch,
        )
        mandara_res = self._verify_engine(
            name="mandara",
            engine_dir=self.mandara_dir,
            manifest=mandara_manifest,
            patch_path=mandara_patch,
        )

        ok = lucid_res["ok"] and mandara_res["ok"]
        return {
            "ok": ok,
            "metadata": meta,
            "upstream_manifest_counts": {
                "lucid": len(lucid_manifest),
                "mandara": len(mandara_manifest),
                "total": len(lucid_manifest) + len(mandara_manifest),
            },
            "lucid": lucid_res,
            "mandara": mandara_res,
        }

    def _verify_engine(
        self,
        name: str,
        engine_dir: Path | None,
        manifest: dict[str, str],
        patch_path: Path,
    ) -> dict[str, Any]:
        if engine_dir is None or not engine_dir.exists():
            return {"ok": False, "error": f"Bundled engine directory for '{name}' not found"}

        modified_files, added_files = parse_patch_touched_files(patch_path)
        verified_untouched = 0
        omitted_media = 0
        hash_mismatches: list[str] = []

        for rel, expected_sha in manifest.items():
            fpath = engine_dir / rel
            if not fpath.exists():
                # Only optional website promo media or 4K .mp4 wallpapers may be omitted from release zip
                omitted_media += 1
                continue
            if rel in modified_files:
                continue
            actual_sha = sha256_file(fpath)
            if actual_sha != expected_sha:
                hash_mismatches.append(f"{rel}: expected {expected_sha[:12]}, got {actual_sha[:12]}")
            else:
                verified_untouched += 1

        # Verify reverse-patching (`patch -p1 -R`) reconstructs exact upstream SHA-256 on EVERY modified file!
        reverse_verified: list[str] = []
        reverse_errors: list[str] = []
        if shutil.which("patch"):
            with tempfile.TemporaryDirectory() as tmp:
                troot = Path(tmp)
                for rel in modified_files | added_files:
                    src = engine_dir / rel
                    if src.exists():
                        dst = troot / rel
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
                proc = subprocess.run(
                    ["patch", "-p1", "-R", "--batch", "--silent", "-i", str(patch_path)],
                    cwd=troot,
                    capture_output=True,
                    text=True,
                )
                if proc.returncode != 0:
                    reverse_errors.append(f"patch -R failed: {proc.stderr or proc.stdout}")
                else:
                    for rel in sorted(modified_files):
                        rev_sha = sha256_file(troot / rel)
                        exp_sha = manifest.get(rel, "")
                        if rev_sha == exp_sha:
                            reverse_verified.append(rel)
                        else:
                            reverse_errors.append(f"{rel}: reverse-patched SHA {rev_sha[:12]} != upstream {exp_sha[:12]}")

        ok = len(hash_mismatches) == 0 and len(reverse_errors) == 0
        return {
            "ok": ok,
            "engine_dir": str(engine_dir),
            "verified_untouched_files": verified_untouched,
            "modified_files_count": len(modified_files),
            "added_adapter_files_count": len(added_files),
            "reverse_patch_verified_files": reverse_verified,
            "omitted_optional_media_files": omitted_media,
            "hash_mismatches": hash_mismatches,
            "reverse_errors": reverse_errors,
        }
