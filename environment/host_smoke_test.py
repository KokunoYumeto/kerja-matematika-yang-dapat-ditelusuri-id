"""Run an isolated host-side equivalent of the immutable rebuild procedure."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
RECEIPT = ROOT / "qa" / "ENVIRONMENT_HOST_SMOKE_TEST_2026.08.22.json"
VERIFY_ENVIRONMENT = ROOT / "environment" / "verify_environment.py"
VERIFY_REBUILD = ROOT / "environment" / "verify_rebuild.py"


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command!r}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def main() -> None:
    tmp_parent = (ROOT / "tmp").resolve()
    tmp_parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="o017-env-host-smoke-", dir=tmp_parent)).resolve()
    if tmp_parent not in stage.parents:
        raise RuntimeError(f"unsafe smoke-test stage: {stage}")

    payload: dict[str, object] = {
        "schema": "o017-environment-host-smoke-v1",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "scope": "isolated host-equivalent build; container digest itself was verified separately",
        "stage_removed": False,
    }
    try:
        shutil.copytree(SOURCE, stage / "source")
        copied_source = stage / "source"

        environment = json.loads(run([sys.executable, str(VERIFY_ENVIRONMENT)], ROOT).stdout)
        mst = run(
            [sys.executable, str(copied_source / "code" / "verify_mst_uniqueness.py")],
            stage,
        )
        expected_mst = (copied_source / "code" / "expected-output.txt").read_text(
            encoding="utf-8"
        )
        if mst.stdout.replace("\r\n", "\n") != expected_mst.replace("\r\n", "\n"):
            raise RuntimeError("MST witness output differs from its frozen oracle")

        recurrence = run(
            [sys.executable, str(copied_source / "code" / "u06_recurrence_witness.py")],
            stage,
        )
        expected_recurrence = (
            copied_source / "code" / "u06-expected-output.txt"
        ).read_text(encoding="utf-8")
        if recurrence.stdout.replace("\r\n", "\n") != expected_recurrence.replace(
            "\r\n", "\n"
        ):
            raise RuntimeError("recurrence witness output differs from its frozen oracle")

        run(["quarto", "render"], copied_source)
        run(["quarto", "render", "--profile", "pdf", "--to", "pdf"], copied_source)
        rebuilt = json.loads(run([sys.executable, str(VERIFY_REBUILD), str(stage)], ROOT).stdout)

        pdf_candidates = sorted((stage / "output" / "pdf").glob("*.pdf"))
        if len(pdf_candidates) != 1:
            raise RuntimeError(f"expected one rebuilt PDF, observed {pdf_candidates!r}")
        pdf = pdf_candidates[0]
        font_output = run(["pdffonts", str(pdf)], ROOT).stdout
        required_font_names = (
            "LatinModernMath",
            "FontAwesome5Free",
            "MSAM10",
            "LMRoman",
        )
        missing_fonts = [name for name in required_font_names if name not in font_output]
        if missing_fonts:
            raise RuntimeError(f"rebuilt PDF is missing font families: {missing_fonts}")

        payload.update(
            {
                "status": "PASS",
                "environment": environment,
                "mathematical_witnesses": {
                    "mst_stdout_sha256": hashlib.sha256(
                        mst.stdout.encode("utf-8")
                    ).hexdigest(),
                    "recurrence_stdout_sha256": hashlib.sha256(
                        recurrence.stdout.encode("utf-8")
                    ).hexdigest(),
                },
                "rebuild": rebuilt,
                "rebuilt_pdf_font_families_present": list(required_font_names),
                "source_files": len([path for path in copied_source.rglob("*") if path.is_file()]),
                "source_bytes": sum(
                    path.stat().st_size for path in copied_source.rglob("*") if path.is_file()
                ),
                "source_tree_rows": [
                    {
                        "path": path.relative_to(copied_source).as_posix(),
                        "bytes": path.stat().st_size,
                        "sha256": sha256(path),
                    }
                    for path in sorted(
                        (path for path in copied_source.rglob("*") if path.is_file()),
                        key=lambda value: value.relative_to(copied_source).as_posix(),
                    )
                ],
            }
        )
    finally:
        shutil.rmtree(stage)
        payload["stage_removed"] = not stage.exists()
        payload["finished_at"] = datetime.now(timezone.utc).isoformat()
        RECEIPT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print(json.dumps({"receipt": str(RECEIPT), "status": payload.get("status")}))


if __name__ == "__main__":
    main()
