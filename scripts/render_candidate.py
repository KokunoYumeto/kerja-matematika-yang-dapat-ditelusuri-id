"""Render and statically verify the registered O017 reader without admitting a unit.

This separates the browser-evidence boundary from admission: the command
promotes a clean, checked HTML candidate, after which the visual-QA runner can
capture evidence for the exact candidate bytes.  It never writes QA/admission
receipts or backend exports.
"""

from __future__ import annotations

import json
import shutil

from o017_pipeline import (
    COURSE,
    HTML_ROOT,
    build_backend,
    check_unit,
    digest,
    finalize_html_outputs,
    find_quarto,
    install_reader_release_files,
    parse_html,
    promote_html,
    render_stage,
    run_computations,
    unit_hashes,
    verify_local_links,
    verify_offline_css,
)


def main() -> None:
    for unit in COURSE.units:
        if not unit.source_path.is_file():
            raise RuntimeError(f"registered unit source is missing: {unit.source_path}")
        if unit.expected_source_sha256 and digest(unit.source_path) != unit.expected_source_sha256:
            raise RuntimeError(f"registered unit source hash changed: {unit.id}")
    computation_results = {unit.id: run_computations(unit) for unit in COURSE.units}
    stage = None
    try:
        stage, render = render_stage(find_quarto())
        install_reader_release_files(stage)
        html_paths = sorted(
            stage.rglob("*.html"),
            key=lambda path: path.relative_to(stage).as_posix().casefold(),
        )
        finalize_html_outputs(html_paths)
        verify_offline_css(stage.rglob("*.css"))
        documents = {path.resolve(): parse_html(path) for path in html_paths}
        checks = {
            unit.id: check_unit(unit, stage, documents, computation_results[unit.id])
            for unit in COURSE.units
        }
        local_links, fragments = verify_local_links(documents)
        hashes = {unit.id: unit_hashes(unit, checks[unit.id].html_path) for unit in COURSE.units}
        backend = build_backend(COURSE, hashes)
        result = {
            "status": "PASS",
            "registered_units": [unit.id for unit in COURSE.units],
            "html_files": len(html_paths),
            "local_links_checked": local_links,
            "fragment_links_checked": fragments,
            "unit_html_sha256": {
                unit.id: digest(checks[unit.id].html_path) for unit in COURSE.units
            },
            "issued_relation_count": backend.relation_count,
            "active_relation_count": backend.active_relation_count,
            "superseded_relation_count": backend.superseded_relation_count,
            "stable_relation_map_sha256": backend.stable_relation_map_sha256,
            "quarto_stdout": render.stdout.strip(),
        }
        promote_html(stage)
        stage = None
        if any(
            digest(HTML_ROOT / unit.html_relative_path) != result["unit_html_sha256"][unit.id]
            for unit in COURSE.units
        ):
            raise RuntimeError("promoted reader differs from the checked stage")
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)


if __name__ == "__main__":
    main()
