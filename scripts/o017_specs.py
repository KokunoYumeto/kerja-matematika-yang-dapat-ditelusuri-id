"""Declarative course and unit specifications for the O017 reader pipeline.

IDs in this module are issued identifiers.  In particular, relation IDs are
explicit data: aggregate sort order must never be used to allocate them.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
BUILD = ROOT / "build"

ENTITY_CLASSES = (
    "program",
    "course",
    "resource",
    "edition",
    "unit",
    "prerequisite",
    "concept",
    "segment",
    "term",
    "definition",
    "theorem",
    "proof",
    "example",
    "counterexample",
    "exercise",
    "solution",
    "citation",
    "source",
    "asset",
    "relation",
    "rights",
    "qa_event",
    "artifact",
    "correction",
)


def record(entity_type: str, identifier: str, **fields: Any) -> dict[str, Any]:
    if entity_type not in ENTITY_CLASSES:
        raise ValueError(f"unsupported entity type {entity_type}")
    return {
        "schema": "o017-backend-record-v1",
        "id": identifier,
        "entity_type": entity_type,
        **fields,
    }


@dataclass(frozen=True)
class RelationSpec:
    id: str
    source: str
    predicate: str
    target: str
    evidence_kind: str | None = None
    status: str = "active"
    superseded_by: str | None = None
    correction_id: str | None = None


@dataclass(frozen=True)
class ComputationSpec:
    code_path: Path
    expected_stdout_path: Path
    result_path: Path
    expected_result: Mapping[str, Any]
    expected_code_sha256: str | None = None
    expected_stdout_sha256: str | None = None


RecordFactory = Callable[[Mapping[str, str]], tuple[dict[str, Any], ...]]


@dataclass(frozen=True)
class UnitSpec:
    id: str
    ordinal: int
    title: str
    source_path: Path
    html_relative_path: Path
    required_section_ids: frozenset[str]
    required_entity_fragments: frozenset[str]
    exercise_solution_pairs: tuple[tuple[str, str], ...]
    computations: tuple[ComputationSpec, ...]
    records_factory: RecordFactory
    relations: tuple[RelationSpec, ...]
    manifest_inputs: tuple[Path, ...]
    scope_notes: tuple[str, ...]
    admission_filename: str
    qa_filename: str
    visual_qa_filename: str | None = None
    visual_qa_script_filename: str | None = None
    expected_source_sha256: str | None = None
    expected_id_type_sha256: str | None = None
    expected_relation_map_sha256: str | None = None
    id_type_baseline_includes_common: bool = False


@dataclass(frozen=True)
class CourseSpec:
    lane_id: str
    entity_classes: tuple[str, ...]
    common_records: tuple[dict[str, Any], ...]
    common_relations: tuple[RelationSpec, ...]
    units: tuple[UnitSpec, ...]


EXPECTED_MST_RESULT = {
    "schema": "o017-unit-01-mst-check-v1",
    "claim_tested": "Distinct edge weights imply a unique MST.",
    "logical_status": "finite computational evidence; not a proof",
    "k4_distinct_weight_assignments_checked": 720,
    "k4_uniqueness_violations": 0,
    "equal_weight_triangle_mst_count": 3,
    "equal_weight_triangle_minimum_weight": 2,
}

EXPECTED_U06_RESULT = json.loads(
    (SOURCE / "code" / "u06-expected-output.txt").read_text(encoding="utf-8")
)


COMMON_RECORDS = (
    record("program", "O017-PROGRAM", title="Kerja Matematika yang Dapat Ditelusuri"),
    record(
        "course",
        "O017-D120",
        title="Research Reading, Exposition, and Reproducible Mathematical Work",
    ),
    record("prerequisite", "C20", title="prerequisite course C20"),
    record("prerequisite", "C40", title="prerequisite course C40"),
    record(
        "prerequisite",
        "B80",
        title="Mathematical Computing and Reproducible Experiments",
    ),
    record("resource", "O017-READER", title="Pembaca O017", role="coursebook"),
    record(
        "edition",
        "O017-EDITION-01",
        locale="id-ID",
        status="release-candidate",
        version="2026.08.22",
        creator="Floris",
        production_system="OpenAI Codex",
        production_disclosure="produced with OpenAI Codex under Floris's direction",
        admission_evidence="nine unit admissions plus final-reader and release QA receipts",
    ),
    record(
        "source",
        "O017-SOURCE-ORIGINAL",
        title="Original O017 bridge material",
        role="authored course source",
    ),
    record(
        "source",
        "O017-SOURCE-TTW-C98A",
        title="The Turing Way selected witness",
        commit="c98a0e6ca47450456cca7c5eedda2d5ee131d1ce",
        manifest_sha256="82a352d497ecdf372b1628b405ef83754f960b7ace239e1710e06e4eb6c9c133",
        identity_scope="repository-commit",
        repository_url="https://github.com/the-turing-way/the-turing-way",
        role="cited methodological donor; no Unit 1 prose copied",
    ),
    record(
        "source",
        "O017-SOURCE-PYRSE-6221",
        title="Research Software Engineering with Python selected witness",
        commit="62217e6606842ab9752fcf8e73954d1eb4a3cf07",
        manifest_sha256="003333798535f050c359f26ea0d5936dd6e43a722b32890b3079b90b2333870f",
        identity_scope="repository-commit",
        repository_url="https://github.com/merely-useful/py-rse",
        role="cited provenance donor; no Unit 1 prose copied",
    ),
    record(
        "citation",
        "O017-CIT-TTW",
        html_fragment="ref-turingway2022",
        doi="10.5281/zenodo.3233853",
        identity_scope="published-release",
        version="1.2.3",
        doi_scope="concept",
        bibliographic_key="turingway2022",
    ),
    record(
        "citation",
        "O017-CIT-PYRSE",
        html_fragment="ref-irving2021",
        isbn="978-0367698348",
        identity_scope="published-book",
        bibliographic_key="irving2021",
    ),
    record("term", "O017-TERM-PROOF", canonical_en="proof", preferred_id="pembuktian"),
    record(
        "term",
        "O017-TERM-EMPIRICAL-EVIDENCE",
        canonical_en="empirical evidence",
        preferred_id="bukti empiris",
    ),
    record(
        "rights",
        "O017-RIGHTS-ORIGINAL-TEXT",
        license="CC BY-SA 4.0",
        license_url="https://creativecommons.org/licenses/by-sa/4.0/",
        licensor="Floris",
        copyright_year=2026,
    ),
    record(
        "rights",
        "O017-RIGHTS-ORIGINAL-CODE",
        license="MIT",
        license_url="https://opensource.org/license/mit/",
        licensor="Floris",
        copyright_year=2026,
    ),
    record(
        "rights",
        "O017-RIGHTS-GENERATED-DATA",
        license="CC0 1.0",
        license_url="https://creativecommons.org/publicdomain/zero/1.0/",
        licensor="Floris",
        copyright_year=2026,
    ),
    record(
        "rights",
        "O017-RIGHTS-TTW",
        license="CC BY 4.0 content; MIT infrastructure",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        licensor="The Turing Way Community",
    ),
    record(
        "rights",
        "O017-RIGHTS-PYRSE",
        license="CC BY 4.0 prose; MIT code",
        license_url="https://creativecommons.org/licenses/by/4.0/",
        licensor="Irving, Hertweck, Johnston, Ostblom, Wickham, and Wilson",
    ),
)


def unit1_records(hashes: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = [
        record(
            "unit",
            "O017-U01",
            ordinal=1,
            title="Membaca Argumen sebagai Jejaring Klaim",
            locale="id-ID",
        ),
        record(
            "citation",
            "O017-CIT-KRUSKAL-1956",
            html_fragment="ref-kruskal1956",
            doi="10.1090/S0002-9939-1956-0078686-7",
        ),
        record("definition", "O017-U01-D01", unit="O017-U01", html_fragment="o017-u01-d01"),
        record("definition", "O017-U01-D02", unit="O017-U01", html_fragment="o017-u01-d02"),
        record("definition", "O017-U01-D03", unit="O017-U01", html_fragment="o017-u01-d03"),
        record(
            "theorem",
            "O017-U01-THEOREM-01",
            unit="O017-U01",
            html_fragment="thm-o017-u01-01",
            title="Ketunggalan pohon rentang minimum",
        ),
        record("proof", "O017-U01-PROOF-01", unit="O017-U01", html_fragment="prf-o017-u01-01"),
        record("example", "O017-U01-EXAMPLE-01", unit="O017-U01", html_fragment="o017-u01-example-01"),
        record(
            "counterexample",
            "O017-U01-COUNTEREXAMPLE-01",
            unit="O017-U01",
            html_fragment="o017-u01-counterexample-01",
        ),
        record(
            "asset",
            "O017-U01-ASSET-MST-CODE",
            path="source/code/verify_mst_uniqueness.py",
            sha256=hashes["code"],
            media_type="text/x-python",
        ),
        record(
            "asset",
            "O017-U01-ASSET-MST-RESULT",
            path="build/unit-01-mst-check.json",
            sha256=hashes["result"],
            media_type="application/json",
        ),
        record(
            "qa_event",
            "O017-U01-QA-01",
            status="pass",
            checks=[
                "mathematical-computation",
                "html-structure",
                "offline-mathml",
                "local-link-closure",
                "exercise-solution-correspondence",
                "rights-attribution",
                "backend-referential-integrity",
            ],
        ),
        record(
            "artifact",
            "O017-U01-ARTIFACT-HTML",
            path="build/html/units/01-membaca-argumen.html",
            sha256=hashes["html"],
            media_type="text/html",
        ),
    ]
    concepts = {
        "O017-CONCEPT-CLAIM-MAP": "jejaring klaim",
        "O017-CONCEPT-PROOF-OBLIGATION": "kewajiban pembuktian",
        "O017-CONCEPT-ASSUMPTION-AUDIT": "audit asumsi",
        "O017-CONCEPT-EXPERIMENT-PROOF": "batas eksperimen dan pembuktian",
        "O017-CONCEPT-READING-LEDGER": "catatan pembacaan",
    }
    records.extend(
        record("concept", identifier, label_id=label, unit="O017-U01")
        for identifier, label in concepts.items()
    )
    segments = {
        "O017-U01-SEG-OUTCOMES": "o017-u01-outcomes",
        "O017-U01-SEG-READING": "o017-u01-reading",
        "O017-U01-SEG-EXCERPT": "o017-u01-synthetic-excerpt",
        "O017-U01-SEG-PROOF": "o017-u01-proof-reconstruction",
        "O017-U01-SEG-ASSUMPTIONS": "o017-u01-assumption-audit",
        "O017-U01-SEG-COMPUTATION": "o017-u01-computation",
        "O017-U01-SEG-PRACTICE": "o017-u01-guided-practice",
        "O017-U01-SEG-EXERCISES": "o017-u01-exercises",
        "O017-U01-SEG-GUIDANCE": "o017-u01-guidance",
        "O017-U01-SEG-COMPLETION": "o017-u01-completion-task",
        "O017-U01-SEG-PROVENANCE": "o017-u01-provenance",
    }
    records.extend(
        record("segment", identifier, unit="O017-U01", html_fragment=fragment)
        for identifier, fragment in segments.items()
    )
    for index in range(1, 7):
        records.extend(
            (
                record(
                    "exercise",
                    f"O017-U01-X{index:02d}",
                    unit="O017-U01",
                    ordinal=index,
                    html_fragment=f"o017-u01-x{index:02d}",
                ),
                record(
                    "solution",
                    f"O017-U01-H{index:02d}",
                    unit="O017-U01",
                    ordinal=index,
                    solution_kind="guidance",
                    html_fragment=f"o017-u01-h{index:02d}",
                ),
            )
        )
    return tuple(records)


# These 65 mappings are the already-issued Unit 1 relation identifiers.  Do
# not reorder, insert into, or regenerate this table by sorting triples.
UNIT1_RELATIONS = (
    RelationSpec(
        "O017-REL-001",
        "O017-CIT-PYRSE",
        "identifies",
        "O017-SOURCE-PYRSE-6221",
        status="superseded",
        superseded_by="O017-U02-REL-112",
        correction_id="O017-CORRECTION-DONOR-IDENTITY-001",
    ),
    RelationSpec(
        "O017-REL-002",
        "O017-CIT-TTW",
        "identifies",
        "O017-SOURCE-TTW-C98A",
        status="superseded",
        superseded_by="O017-U02-REL-113",
        correction_id="O017-CORRECTION-DONOR-IDENTITY-001",
    ),
    RelationSpec("O017-REL-003", "O017-D120", "requires", "B80"),
    RelationSpec("O017-REL-004", "O017-D120", "requires", "C20"),
    RelationSpec("O017-REL-005", "O017-D120", "requires", "C40"),
    RelationSpec("O017-REL-006", "O017-D120", "uses", "O017-READER"),
    RelationSpec("O017-REL-007", "O017-EDITION-01", "contains", "O017-U01"),
    RelationSpec("O017-REL-008", "O017-PROGRAM", "contains", "O017-D120"),
    RelationSpec("O017-REL-009", "O017-READER", "has-edition", "O017-EDITION-01"),
    RelationSpec("O017-REL-010", "O017-SOURCE-PYRSE-6221", "governed-by", "O017-RIGHTS-PYRSE"),
    RelationSpec("O017-REL-011", "O017-SOURCE-TTW-C98A", "governed-by", "O017-RIGHTS-TTW"),
    RelationSpec("O017-REL-012", "O017-U01", "authored-from", "O017-SOURCE-ORIGINAL"),
    RelationSpec("O017-REL-013", "O017-U01", "cites", "O017-CIT-KRUSKAL-1956"),
    RelationSpec("O017-REL-014", "O017-U01", "cites", "O017-CIT-PYRSE"),
    RelationSpec("O017-REL-015", "O017-U01", "cites", "O017-CIT-TTW"),
    RelationSpec("O017-REL-016", "O017-U01", "contains", "O017-U01-COUNTEREXAMPLE-01"),
    RelationSpec("O017-REL-017", "O017-U01", "contains", "O017-U01-D01"),
    RelationSpec("O017-REL-018", "O017-U01", "contains", "O017-U01-D02"),
    RelationSpec("O017-REL-019", "O017-U01", "contains", "O017-U01-D03"),
    RelationSpec("O017-REL-020", "O017-U01", "contains", "O017-U01-EXAMPLE-01"),
    RelationSpec("O017-REL-021", "O017-U01", "contains", "O017-U01-H01"),
    RelationSpec("O017-REL-022", "O017-U01", "contains", "O017-U01-H02"),
    RelationSpec("O017-REL-023", "O017-U01", "contains", "O017-U01-H03"),
    RelationSpec("O017-REL-024", "O017-U01", "contains", "O017-U01-H04"),
    RelationSpec("O017-REL-025", "O017-U01", "contains", "O017-U01-H05"),
    RelationSpec("O017-REL-026", "O017-U01", "contains", "O017-U01-H06"),
    RelationSpec("O017-REL-027", "O017-U01", "contains", "O017-U01-PROOF-01"),
    RelationSpec("O017-REL-028", "O017-U01", "contains", "O017-U01-SEG-ASSUMPTIONS"),
    RelationSpec("O017-REL-029", "O017-U01", "contains", "O017-U01-SEG-COMPLETION"),
    RelationSpec("O017-REL-030", "O017-U01", "contains", "O017-U01-SEG-COMPUTATION"),
    RelationSpec("O017-REL-031", "O017-U01", "contains", "O017-U01-SEG-EXCERPT"),
    RelationSpec("O017-REL-032", "O017-U01", "contains", "O017-U01-SEG-EXERCISES"),
    RelationSpec("O017-REL-033", "O017-U01", "contains", "O017-U01-SEG-GUIDANCE"),
    RelationSpec("O017-REL-034", "O017-U01", "contains", "O017-U01-SEG-OUTCOMES"),
    RelationSpec("O017-REL-035", "O017-U01", "contains", "O017-U01-SEG-PRACTICE"),
    RelationSpec("O017-REL-036", "O017-U01", "contains", "O017-U01-SEG-PROOF"),
    RelationSpec("O017-REL-037", "O017-U01", "contains", "O017-U01-SEG-PROVENANCE"),
    RelationSpec("O017-REL-038", "O017-U01", "contains", "O017-U01-SEG-READING"),
    RelationSpec("O017-REL-039", "O017-U01", "contains", "O017-U01-THEOREM-01"),
    RelationSpec("O017-REL-040", "O017-U01", "contains", "O017-U01-X01"),
    RelationSpec("O017-REL-041", "O017-U01", "contains", "O017-U01-X02"),
    RelationSpec("O017-REL-042", "O017-U01", "contains", "O017-U01-X03"),
    RelationSpec("O017-REL-043", "O017-U01", "contains", "O017-U01-X04"),
    RelationSpec("O017-REL-044", "O017-U01", "contains", "O017-U01-X05"),
    RelationSpec("O017-REL-045", "O017-U01", "contains", "O017-U01-X06"),
    RelationSpec("O017-REL-046", "O017-U01", "has-artifact", "O017-U01-ARTIFACT-HTML"),
    RelationSpec("O017-REL-047", "O017-U01", "has-asset", "O017-U01-ASSET-MST-CODE"),
    RelationSpec("O017-REL-048", "O017-U01", "has-asset", "O017-U01-ASSET-MST-RESULT"),
    RelationSpec("O017-REL-049", "O017-U01", "licensed-by", "O017-RIGHTS-ORIGINAL-TEXT"),
    RelationSpec("O017-REL-050", "O017-U01", "teaches", "O017-CONCEPT-ASSUMPTION-AUDIT"),
    RelationSpec("O017-REL-051", "O017-U01", "teaches", "O017-CONCEPT-CLAIM-MAP"),
    RelationSpec("O017-REL-052", "O017-U01", "teaches", "O017-CONCEPT-EXPERIMENT-PROOF"),
    RelationSpec("O017-REL-053", "O017-U01", "teaches", "O017-CONCEPT-PROOF-OBLIGATION"),
    RelationSpec("O017-REL-054", "O017-U01", "teaches", "O017-CONCEPT-READING-LEDGER"),
    RelationSpec("O017-REL-055", "O017-U01", "verified-by", "O017-U01-QA-01"),
    RelationSpec("O017-REL-056", "O017-U01-ASSET-MST-CODE", "licensed-by", "O017-RIGHTS-ORIGINAL-CODE"),
    RelationSpec("O017-REL-057", "O017-U01-ASSET-MST-RESULT", "generated-by", "O017-U01-ASSET-MST-CODE"),
    RelationSpec("O017-REL-058", "O017-U01-ASSET-MST-RESULT", "licensed-by", "O017-RIGHTS-GENERATED-DATA"),
    RelationSpec("O017-REL-059", "O017-U01-THEOREM-01", "proved-by", "O017-U01-PROOF-01"),
    RelationSpec("O017-REL-060", "O017-U01-X01", "guided-by", "O017-U01-H01"),
    RelationSpec("O017-REL-061", "O017-U01-X02", "guided-by", "O017-U01-H02"),
    RelationSpec("O017-REL-062", "O017-U01-X03", "guided-by", "O017-U01-H03"),
    RelationSpec("O017-REL-063", "O017-U01-X04", "guided-by", "O017-U01-H04"),
    RelationSpec("O017-REL-064", "O017-U01-X05", "guided-by", "O017-U01-H05"),
    RelationSpec("O017-REL-065", "O017-U01-X06", "guided-by", "O017-U01-H06"),
)


UNIT1 = UnitSpec(
    id="O017-U01",
    ordinal=1,
    title="Membaca Argumen sebagai Jejaring Klaim",
    source_path=SOURCE / "units" / "01-membaca-argumen.qmd",
    html_relative_path=Path("units/01-membaca-argumen.html"),
    required_section_ids=frozenset(
        {
            "o017-u01-outcomes",
            "o017-u01-reading",
            "o017-u01-synthetic-excerpt",
            "o017-u01-proof-reconstruction",
            "thm-o017-u01-01",
            "prf-o017-u01-01",
            "o017-u01-assumption-audit",
            "o017-u01-example-01",
            "o017-u01-counterexample-01",
            "o017-u01-computation",
            "o017-u01-guided-practice",
            "o017-u01-exercises",
            "o017-u01-guidance",
            "o017-u01-completion-task",
            "o017-u01-provenance",
        }
    ),
    required_entity_fragments=frozenset(
        {
            "o017-u01-d01",
            "o017-u01-d02",
            "o017-u01-d03",
            "thm-o017-u01-01",
            "prf-o017-u01-01",
            "o017-u01-example-01",
            "o017-u01-counterexample-01",
            "ref-kruskal1956",
            "ref-turingway2022",
            "ref-irving2021",
            *{f"o017-u01-x{index:02d}" for index in range(1, 7)},
            *{f"o017-u01-h{index:02d}" for index in range(1, 7)},
        }
    ),
    exercise_solution_pairs=tuple(
        (f"O017-U01-X{index:02d}", f"O017-U01-H{index:02d}")
        for index in range(1, 7)
    ),
    computations=(
        ComputationSpec(
            code_path=SOURCE / "code" / "verify_mst_uniqueness.py",
            expected_stdout_path=SOURCE / "code" / "expected-output.txt",
            result_path=BUILD / "unit-01-mst-check.json",
            expected_result=EXPECTED_MST_RESULT,
        ),
    ),
    records_factory=unit1_records,
    relations=UNIT1_RELATIONS,
    manifest_inputs=(SOURCE / "code" / "verify_mst_uniqueness.py", SOURCE / "code" / "expected-output.txt"),
    scope_notes=(
        "Unit 1 is original O017 bridge material; no donor prose is copied.",
        "The finite MST enumeration is diagnostic evidence, not a universal proof.",
        "Unit 1 admission is not full-course completion.",
    ),
    admission_filename="UNIT_01_ADMISSION.md",
    qa_filename="UNIT_01_QA.json",
    visual_qa_filename="UNIT_01_VISUAL_QA.json",
    visual_qa_script_filename="visual_qa_unit.cjs",
    expected_source_sha256="a174ae167c2a84124ca189722b3d54c399aef8b038a4c863b329da64eaba7faa",
    expected_id_type_sha256="25e93aeb0a63e34942ef54b341f23e5cb01ee72d719f0cea909d8e9010da1521",
    expected_relation_map_sha256="9634a027bce6dbd6374b84b44ba7cc417b3379d23ba0977b6b14a3bfd3ef67b8",
    id_type_baseline_includes_common=True,
)


AUTHORITY_DIMENSIONS = (
    "proximity",
    "version_traceability",
    "provenance",
    "locator",
    "support",
)


def synthetic_source(
    identifier: str,
    *,
    authority_dimensions: Mapping[str, str],
    unresolved_fields: tuple[str, ...],
    **fields: Any,
) -> dict[str, Any]:
    """Return one disclosed, non-public classroom source record."""

    if tuple(authority_dimensions) != AUTHORITY_DIMENSIONS:
        raise ValueError(f"authority dimensions are incomplete or out of order for {identifier}")
    return record(
        "source",
        identifier,
        synthetic=True,
        public_pid=False,
        authority_dimensions=dict(authority_dimensions),
        unresolved_fields=list(unresolved_fields),
        **fields,
    )


def unit2_records(hashes: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = [
        record(
            "unit",
            "O017-U02",
            ordinal=2,
            title="Menelusuri Literatur dan Menilai Otoritas Sumber",
            locale="id-ID",
        ),
        record(
            "source",
            "O017-SOURCE-TTW-RELEASE-1-2-3",
            title="The Turing Way Handbook for Reproducible, Ethical and Collaborative Research",
            identity_scope="published-release",
            concept_doi="10.5281/zenodo.3233853",
            doi_scope="concept",
            version="1.2.3",
            repository_url="https://github.com/the-turing-way/the-turing-way",
        ),
        record(
            "source",
            "O017-SOURCE-PYRSE-BOOK-2021",
            title="Research Software Engineering with Python: Building Software that Makes Research Possible",
            identity_scope="published-book",
            isbn="978-0367698348",
            publication_year=2021,
            repository_url="https://github.com/merely-useful/py-rse",
        ),
        record(
            "citation",
            "O017-CIT-TTW-C98A",
            html_fragment="ref-turingwaycommitc98a",
            commit="c98a0e6ca47450456cca7c5eedda2d5ee131d1ce",
            source_state="post-release frozen source witness",
            release_version_label=None,
            identity_scope="repository-commit",
            bibliographic_key="turingwaycommitc98a",
        ),
        record(
            "citation",
            "O017-CIT-PYRSE-6221",
            html_fragment="ref-pyrsecommit62217",
            commit="62217e6606842ab9752fcf8e73954d1eb4a3cf07",
            source_state="frozen exact source witness",
            release_version_label=None,
            identity_scope="repository-commit",
            bibliographic_key="pyrsecommit62217",
        ),
        record(
            "correction",
            "O017-CORRECTION-DONOR-IDENTITY-001",
            unit="O017-U02",
            correction_kind="relation-supersession",
            reason_code="citation-source-identity-scope-mismatch",
            status="applied",
            replacements=[
                {
                    "issued_relation_id": "O017-REL-001",
                    "replacement_relation_id": "O017-U02-REL-112",
                },
                {
                    "issued_relation_id": "O017-REL-002",
                    "replacement_relation_id": "O017-U02-REL-113",
                },
            ],
            issued_relation_id_preserved=True,
        ),
        record(
            "definition",
            "O017-U02-D01",
            unit="O017-U02",
            html_fragment="o017-u02-def01",
            title="Otoritas bergantung pada pertanyaan",
        ),
        record(
            "definition",
            "O017-U02-D02",
            unit="O017-U02",
            html_fragment="o017-u02-def-pid",
            title="PID karya dan PID versi",
        ),
        record(
            "theorem",
            "O017-U02-THEOREM-K1",
            unit="O017-U02",
            html_fragment="thm-o017-u02-v1",
            claim_label="K1",
            claim_status="refuted",
            statement="If a real series sum(a_n) converges, then sum(a_n^2) converges.",
        ),
        record(
            "counterexample",
            "O017-U02-COUNTEREXAMPLE-K1",
            unit="O017-U02",
            html_fragment="o017-u02-counterexample-v1",
            refutes="O017-U02-THEOREM-K1",
            witness="a_n=(-1)^(n+1)/sqrt(n)",
        ),
        record(
            "theorem",
            "O017-U02-THEOREM-K2",
            unit="O017-U02",
            html_fragment="thm-o017-u02-v2",
            claim_label="K2",
            claim_status="proved",
            statement="If sum(abs(a_n)) converges, then sum(a_n^2) converges.",
        ),
        record(
            "proof",
            "O017-U02-PROOF-K2",
            unit="O017-U02",
            html_fragment="prf-o017-u02-v2",
            proves="O017-U02-THEOREM-K2",
            method="tail comparison a_n^2 <= abs(a_n)",
        ),
        record(
            "qa_event",
            "O017-U02-QA-01",
            status="pass",
            checks=[
                "source-hash-lock",
                "html-structure",
                "offline-mathml",
                "local-link-closure",
                "exercise-solution-correspondence",
                "synthetic-source-disclosure",
                "authority-dimension-completeness",
                "unresolved-field-preservation",
                "metadata-inference-separation",
                "mathematical-proof-counterexample",
                "rights-attribution",
                "backend-referential-integrity",
            ],
        ),
        record(
            "artifact",
            "O017-U02-ARTIFACT-HTML",
            path="build/html/units/02-menelusuri-sumber.html",
            sha256=hashes["html"],
            media_type="text/html",
        ),
    ]

    concepts = (
        ("O017-CONCEPT-SOURCE-NETWORK", "jejaring sumber"),
        ("O017-CONCEPT-SEARCH-CARD", "kartu penelusuran"),
        ("O017-CONCEPT-QUESTION-RELATIVE-AUTHORITY", "otoritas relatif terhadap pertanyaan"),
        ("O017-CONCEPT-SOURCE-SURFACES", "lima permukaan bukti sumber"),
        ("O017-CONCEPT-CONCEPT-VERSION-PID", "PID konsep dan PID versi"),
        ("O017-CONCEPT-TYPED-CITATION-CHAIN", "rantai sitasi berarah dan berjenis"),
        ("O017-CONCEPT-METADATA-INFERENCE", "pemisahan metadata dan inferensi"),
        ("O017-CONCEPT-UNRESOLVED-METADATA", "data bibliografis yang belum diketahui"),
    )
    records.extend(
        record("concept", identifier, label_id=label, unit="O017-U02")
        for identifier, label in concepts
    )

    segments = (
        ("O017-U02-SEG-OUTCOMES", "o017-u02-outcomes"),
        ("O017-U02-SEG-CLAIM-TO-SOURCE", "o017-u02-claim-to-source"),
        ("O017-U02-SEG-SEARCH-CARD", "o017-u02-search-card"),
        ("O017-U02-SEG-THREE-PASS", "o017-u02-three-pass"),
        ("O017-U02-SEG-STOP-RULE", "o017-u02-stop-rule"),
        ("O017-U02-SEG-FIVE-SURFACES", "o017-u02-five-surfaces"),
        ("O017-U02-SEG-AUTHORITY-MATRIX", "o017-u02-authority-matrix"),
        ("O017-U02-SEG-EDITIONS-PIDS", "o017-u02-editions-pids"),
        ("O017-U02-SEG-TYPED-RELATIONS", "o017-u02-typed-relations"),
        ("O017-U02-SEG-WORKED-CASE", "o017-u02-worked-case"),
        ("O017-U02-SEG-SOURCE-PACKET", "o017-u02-source-packet-series"),
        ("O017-U02-SEG-SERIES-V1-AUDIT", "o017-u02-series-v1-audit"),
        ("O017-U02-SEG-SERIES-V2-AUDIT", "o017-u02-series-v2-audit"),
        ("O017-U02-SEG-CITATION-CHOICE", "o017-u02-citation-choice"),
        ("O017-U02-SEG-MINIMAL-LEDGER", "o017-u02-minimal-ledger"),
        ("O017-U02-SEG-EXERCISES", "o017-u02-exercises"),
        ("O017-U02-SEG-GUIDANCE", "o017-u02-guidance"),
        ("O017-U02-SEG-COMPLETION", "o017-u02-completion-task"),
        ("O017-U02-SEG-RUBRIC", "o017-u02-completion-rubric"),
        ("O017-U02-SEG-BOUNDARY", "o017-u02-boundary"),
        ("O017-U02-SEG-PROVENANCE", "o017-u02-provenance"),
    )
    records.extend(
        record("segment", identifier, unit="O017-U02", html_fragment=fragment)
        for identifier, fragment in segments
    )

    for index in range(1, 7):
        records.extend(
            (
                record(
                    "exercise",
                    f"O017-U02-X{index:02d}",
                    unit="O017-U02",
                    ordinal=index,
                    html_fragment=f"o017-u02-x{index:02d}",
                ),
                record(
                    "solution",
                    f"O017-U02-H{index:02d}",
                    unit="O017-U02",
                    ordinal=index,
                    solution_kind="guidance",
                    html_fragment=f"o017-u02-h{index:02d}",
                ),
            )
        )

    records.extend(
        (
            synthetic_source(
                "O017-U02-SRC-S0",
                title="Cuplikan indeks kelas",
                source_role="discovery-index",
                html_fragment="o017-u02-src-s0",
                authority_dimensions={
                    "proximity": "discovery-only; truncated sentence",
                    "version_traceability": "no edition or version identified",
                    "provenance": "classroom packet; creator and date unresolved",
                    "locator": "candidate title only",
                    "support": "none; discovery is not mathematical support",
                },
                unresolved_fields=("creator", "date", "edition_or_version", "full_text_locator"),
            ),
            synthetic_source(
                "O017-U02-SRC-S1",
                title="Ringkasan Seminar Deret",
                date_display="20 Maret",
                source_role="secondary-source",
                html_fragment="o017-u02-src-s1",
                authority_dimensions={
                    "proximity": "quotes K1 wording and cites the concept record",
                    "version_traceability": "seminar item fixed; cited source version unresolved",
                    "provenance": "classroom packet; creator and year unresolved",
                    "locator": "quoted wording is available; no version locator",
                    "support": "secondary quotation; no independent proof",
                },
                unresolved_fields=("creator", "year", "repository", "cited_version", "source_version_used"),
            ),
            synthetic_source(
                "O017-U02-SRC-S2",
                title="Kuadrat Deret Konvergen",
                version="1",
                date_display="10 Maret",
                pid="PID-KELAS-O017-DERET-V1",
                source_role="version-artifact",
                html_fragment="o017-u02-src-s2",
                claim_locator="K1",
                authority_dimensions={
                    "proximity": "contains K1 and a summarized proof",
                    "version_traceability": "version 1 is identified by a classroom version PID",
                    "provenance": "classroom packet; creator, year, and repository unresolved",
                    "locator": "K1",
                    "support": "states K1; does not establish its truth",
                },
                unresolved_fields=("creator", "year", "repository"),
            ),
            synthetic_source(
                "O017-U02-SRC-S3",
                title="Kuadrat Deret Konvergen",
                version="2",
                date_display="8 April",
                pid="PID-KELAS-O017-DERET-V2",
                source_role="version-artifact-correction",
                html_fragment="o017-u02-src-s3",
                claim_locator="K2",
                authority_dimensions={
                    "proximity": "contains K2, its proof, and a change note",
                    "version_traceability": "version 2 is identified by a classroom version PID",
                    "provenance": "classroom packet; creator, year, and repository unresolved",
                    "locator": "K2 and version-change note",
                    "support": "contains a comparison proof for K2",
                },
                unresolved_fields=("creator", "year", "repository"),
            ),
            synthetic_source(
                "O017-U02-SRC-S4",
                title="Analisis Real: Edisi Kelas",
                edition="3",
                year=2024,
                locator="p. 141",
                source_role="independent-comparator",
                html_fragment="o017-u02-src-s4",
                authority_dimensions={
                    "proximity": "contains the alternating-series, harmonic-series, and comparison tools",
                    "version_traceability": "edition 3 and page 141 are visible",
                    "provenance": "classroom packet; creator and publisher unresolved",
                    "locator": "p. 141",
                    "support": "independent synthetic mathematical comparator",
                },
                unresolved_fields=("creator", "publisher"),
            ),
            synthetic_source(
                "PID-KELAS-O017-DERET-KONSEP",
                title="Kuadrat Deret Konvergen",
                pid="PID-KELAS-O017-DERET-KONSEP",
                pid_scope="concept",
                source_role="concept-record",
                html_fragment="o017-u02-pid-concept",
                authority_dimensions={
                    "proximity": "groups versions; does not freeze quoted wording",
                    "version_traceability": "persistent classroom concept identity; resolves to a changing version",
                    "provenance": "classroom-local simulated PID record",
                    "locator": "concept record",
                    "support": "version metadata only; not proof",
                },
                unresolved_fields=("creator", "repository", "version_resolved_by_the_seminar_citation"),
            ),
            synthetic_source(
                "PID-KELAS-O017-DERET-V1",
                title="Kuadrat Deret Konvergen",
                pid="PID-KELAS-O017-DERET-V1",
                pid_scope="version",
                version="1",
                date_display="10 Maret",
                source_role="version-record",
                html_fragment="o017-u02-pid-v1",
                claim_locator="K1",
                authority_dimensions={
                    "proximity": "identifies the exact version that states K1",
                    "version_traceability": "version-specific classroom identity",
                    "provenance": "classroom-local simulated PID record",
                    "locator": "K1",
                    "support": "establishes what version 1 states; K1 is refuted separately",
                },
                unresolved_fields=("creator", "year", "repository"),
            ),
            synthetic_source(
                "PID-KELAS-O017-DERET-V2",
                title="Kuadrat Deret Konvergen",
                pid="PID-KELAS-O017-DERET-V2",
                pid_scope="version",
                version="2",
                date_display="8 April",
                source_role="version-record-correction",
                html_fragment="o017-u02-pid-v2",
                claim_locator="K2",
                authority_dimensions={
                    "proximity": "identifies the exact version that states and proves K2",
                    "version_traceability": "version-specific classroom identity",
                    "provenance": "classroom-local simulated PID record",
                    "locator": "K2 and change note",
                    "support": "comparison proof is present in the version packet",
                },
                unresolved_fields=("creator", "year", "repository"),
            ),
            synthetic_source(
                "PID-KELAS-O017-FUNGSI-KONSEP",
                title="Batas Fungsi Kontinu",
                pid="PID-KELAS-O017-FUNGSI-KONSEP",
                pid_scope="concept",
                source_role="completion-concept-record",
                authority_dimensions={
                    "proximity": "groups the two stated classroom versions",
                    "version_traceability": "persistent classroom concept identity; not a fixed version",
                    "provenance": "classroom-local simulated PID record",
                    "locator": "concept record",
                    "support": "version metadata only; not proof",
                },
                unresolved_fields=("creator", "date", "repository", "version_used_by_lecture_note"),
            ),
            synthetic_source(
                "PID-KELAS-O017-FUNGSI-V1",
                title="Batas Fungsi Kontinu",
                pid="PID-KELAS-O017-FUNGSI-V1",
                pid_scope="version",
                version="1",
                source_role="completion-version-record",
                claim="pointwise limits of continuous functions on [0,1] are always continuous",
                authority_dimensions={
                    "proximity": "identifies the exact version 1 claim",
                    "version_traceability": "version-specific classroom identity",
                    "provenance": "classroom-local simulated PID record",
                    "locator": "version 1 claim; finer locator unresolved",
                    "support": "states the claim; x^n is a counterexample",
                },
                unresolved_fields=("creator", "date", "repository", "claim_locator"),
            ),
            synthetic_source(
                "PID-KELAS-O017-FUNGSI-V2",
                title="Batas Fungsi Kontinu",
                pid="PID-KELAS-O017-FUNGSI-V2",
                pid_scope="version",
                version="2",
                source_role="completion-version-record-correction",
                claim="uniform limits of continuous functions on [0,1] are continuous",
                authority_dimensions={
                    "proximity": "identifies the corrected version 2 claim and change note",
                    "version_traceability": "version-specific classroom identity",
                    "provenance": "classroom-local simulated PID record",
                    "locator": "version 2 claim; finer locator unresolved",
                    "support": "the completion task requires an epsilon-over-three proof",
                },
                unresolved_fields=("creator", "date", "repository", "claim_locator"),
            ),
            synthetic_source(
                "O017-U02-SRC-FUNGSI-LECTURE-NOTE",
                source_role="completion-secondary-source",
                description="Catatan kuliah yang menyitasi rekaman konsep tanpa nomor versi",
                authority_dimensions={
                    "proximity": "cites the concept record; exact quoted wording is not supplied",
                    "version_traceability": "lecture-note edition and date unresolved",
                    "provenance": "classroom source; creator and repository unresolved",
                    "locator": "no section or page supplied",
                    "support": "no independent proof is supplied",
                },
                unresolved_fields=("title", "creator", "date", "edition", "repository", "locator", "version_used"),
            ),
            synthetic_source(
                "O017-U02-SRC-FUNGSI-TEXTBOOK-E2",
                edition="2",
                locator="sec. 6.4",
                source_role="completion-independent-comparator",
                description="Buku teks sintetis yang memuat teorema limit seragam",
                authority_dimensions={
                    "proximity": "contains the uniform-limit theorem",
                    "version_traceability": "edition 2 is known; remaining bibliographic identity is unresolved",
                    "provenance": "classroom source; creator, publisher, and date unresolved",
                    "locator": "sec. 6.4",
                    "support": "independent synthetic support for the corrected theorem",
                },
                unresolved_fields=("title", "creator", "publisher", "date"),
            ),
        )
    )
    return tuple(records)


# Unit 2 relation IDs are issued in a unit namespace.  Keep every mapping
# explicit: neither this table nor future aggregate sorting allocates IDs.
UNIT2_RELATIONS = (
    RelationSpec("O017-U02-REL-001", "O017-EDITION-01", "contains", "O017-U02", "metadata"),
    RelationSpec("O017-U02-REL-002", "O017-U02", "authored-from", "O017-SOURCE-ORIGINAL", "metadata"),
    RelationSpec("O017-U02-REL-003", "O017-U02", "cites", "O017-CIT-TTW", "metadata"),
    RelationSpec("O017-U02-REL-004", "O017-U02", "cites", "O017-CIT-PYRSE", "metadata"),
    RelationSpec("O017-U02-REL-005", "O017-U02", "adapted-from", "O017-SOURCE-TTW-C98A", "metadata"),
    RelationSpec("O017-U02-REL-006", "O017-U02", "reviewed-with", "O017-SOURCE-PYRSE-6221", "metadata"),
    RelationSpec("O017-U02-REL-007", "O017-U02", "licensed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-008", "O017-U02", "verified-by", "O017-U02-QA-01", "metadata"),
    RelationSpec("O017-U02-REL-009", "O017-U02", "has-artifact", "O017-U02-ARTIFACT-HTML", "metadata"),
    RelationSpec("O017-U02-REL-010", "O017-U02", "teaches", "O017-CONCEPT-SOURCE-NETWORK", "metadata"),
    RelationSpec("O017-U02-REL-011", "O017-U02", "teaches", "O017-CONCEPT-SEARCH-CARD", "metadata"),
    RelationSpec("O017-U02-REL-012", "O017-U02", "teaches", "O017-CONCEPT-QUESTION-RELATIVE-AUTHORITY", "metadata"),
    RelationSpec("O017-U02-REL-013", "O017-U02", "teaches", "O017-CONCEPT-SOURCE-SURFACES", "metadata"),
    RelationSpec("O017-U02-REL-014", "O017-U02", "teaches", "O017-CONCEPT-CONCEPT-VERSION-PID", "metadata"),
    RelationSpec("O017-U02-REL-015", "O017-U02", "teaches", "O017-CONCEPT-TYPED-CITATION-CHAIN", "metadata"),
    RelationSpec("O017-U02-REL-016", "O017-U02", "teaches", "O017-CONCEPT-METADATA-INFERENCE", "metadata"),
    RelationSpec("O017-U02-REL-017", "O017-U02", "teaches", "O017-CONCEPT-UNRESOLVED-METADATA", "metadata"),
    RelationSpec("O017-U02-REL-018", "O017-U02", "contains", "O017-U02-SEG-OUTCOMES", "metadata"),
    RelationSpec("O017-U02-REL-019", "O017-U02", "contains", "O017-U02-SEG-CLAIM-TO-SOURCE", "metadata"),
    RelationSpec("O017-U02-REL-020", "O017-U02", "contains", "O017-U02-SEG-SEARCH-CARD", "metadata"),
    RelationSpec("O017-U02-REL-021", "O017-U02", "contains", "O017-U02-SEG-THREE-PASS", "metadata"),
    RelationSpec("O017-U02-REL-022", "O017-U02", "contains", "O017-U02-SEG-STOP-RULE", "metadata"),
    RelationSpec("O017-U02-REL-023", "O017-U02", "contains", "O017-U02-SEG-FIVE-SURFACES", "metadata"),
    RelationSpec("O017-U02-REL-024", "O017-U02", "contains", "O017-U02-SEG-AUTHORITY-MATRIX", "metadata"),
    RelationSpec("O017-U02-REL-025", "O017-U02", "contains", "O017-U02-SEG-EDITIONS-PIDS", "metadata"),
    RelationSpec("O017-U02-REL-026", "O017-U02", "contains", "O017-U02-SEG-TYPED-RELATIONS", "metadata"),
    RelationSpec("O017-U02-REL-027", "O017-U02", "contains", "O017-U02-SEG-WORKED-CASE", "metadata"),
    RelationSpec("O017-U02-REL-028", "O017-U02", "contains", "O017-U02-SEG-SOURCE-PACKET", "metadata"),
    RelationSpec("O017-U02-REL-029", "O017-U02", "contains", "O017-U02-SEG-SERIES-V1-AUDIT", "metadata"),
    RelationSpec("O017-U02-REL-030", "O017-U02", "contains", "O017-U02-SEG-SERIES-V2-AUDIT", "metadata"),
    RelationSpec("O017-U02-REL-031", "O017-U02", "contains", "O017-U02-SEG-CITATION-CHOICE", "metadata"),
    RelationSpec("O017-U02-REL-032", "O017-U02", "contains", "O017-U02-SEG-MINIMAL-LEDGER", "metadata"),
    RelationSpec("O017-U02-REL-033", "O017-U02", "contains", "O017-U02-SEG-EXERCISES", "metadata"),
    RelationSpec("O017-U02-REL-034", "O017-U02", "contains", "O017-U02-SEG-GUIDANCE", "metadata"),
    RelationSpec("O017-U02-REL-035", "O017-U02", "contains", "O017-U02-SEG-COMPLETION", "metadata"),
    RelationSpec("O017-U02-REL-036", "O017-U02", "contains", "O017-U02-SEG-RUBRIC", "metadata"),
    RelationSpec("O017-U02-REL-037", "O017-U02", "contains", "O017-U02-SEG-BOUNDARY", "metadata"),
    RelationSpec("O017-U02-REL-038", "O017-U02", "contains", "O017-U02-SEG-PROVENANCE", "metadata"),
    RelationSpec("O017-U02-REL-039", "O017-U02", "contains", "O017-U02-D01", "metadata"),
    RelationSpec("O017-U02-REL-040", "O017-U02", "contains", "O017-U02-D02", "metadata"),
    RelationSpec("O017-U02-REL-041", "O017-U02", "contains", "O017-U02-THEOREM-K1", "metadata"),
    RelationSpec("O017-U02-REL-042", "O017-U02", "contains", "O017-U02-COUNTEREXAMPLE-K1", "metadata"),
    RelationSpec("O017-U02-REL-043", "O017-U02", "contains", "O017-U02-THEOREM-K2", "metadata"),
    RelationSpec("O017-U02-REL-044", "O017-U02", "contains", "O017-U02-PROOF-K2", "metadata"),
    RelationSpec("O017-U02-REL-045", "O017-U02", "contains", "O017-U02-X01", "metadata"),
    RelationSpec("O017-U02-REL-046", "O017-U02", "contains", "O017-U02-H01", "metadata"),
    RelationSpec("O017-U02-REL-047", "O017-U02", "contains", "O017-U02-X02", "metadata"),
    RelationSpec("O017-U02-REL-048", "O017-U02", "contains", "O017-U02-H02", "metadata"),
    RelationSpec("O017-U02-REL-049", "O017-U02", "contains", "O017-U02-X03", "metadata"),
    RelationSpec("O017-U02-REL-050", "O017-U02", "contains", "O017-U02-H03", "metadata"),
    RelationSpec("O017-U02-REL-051", "O017-U02", "contains", "O017-U02-X04", "metadata"),
    RelationSpec("O017-U02-REL-052", "O017-U02", "contains", "O017-U02-H04", "metadata"),
    RelationSpec("O017-U02-REL-053", "O017-U02", "contains", "O017-U02-X05", "metadata"),
    RelationSpec("O017-U02-REL-054", "O017-U02", "contains", "O017-U02-H05", "metadata"),
    RelationSpec("O017-U02-REL-055", "O017-U02", "contains", "O017-U02-X06", "metadata"),
    RelationSpec("O017-U02-REL-056", "O017-U02", "contains", "O017-U02-H06", "metadata"),
    RelationSpec("O017-U02-REL-057", "O017-U02", "contains", "O017-U02-SRC-S0", "metadata"),
    RelationSpec("O017-U02-REL-058", "O017-U02", "contains", "O017-U02-SRC-S1", "metadata"),
    RelationSpec("O017-U02-REL-059", "O017-U02", "contains", "O017-U02-SRC-S2", "metadata"),
    RelationSpec("O017-U02-REL-060", "O017-U02", "contains", "O017-U02-SRC-S3", "metadata"),
    RelationSpec("O017-U02-REL-061", "O017-U02", "contains", "O017-U02-SRC-S4", "metadata"),
    RelationSpec("O017-U02-REL-062", "O017-U02", "contains", "PID-KELAS-O017-DERET-KONSEP", "metadata"),
    RelationSpec("O017-U02-REL-063", "O017-U02", "contains", "PID-KELAS-O017-DERET-V1", "metadata"),
    RelationSpec("O017-U02-REL-064", "O017-U02", "contains", "PID-KELAS-O017-DERET-V2", "metadata"),
    RelationSpec("O017-U02-REL-065", "O017-U02", "contains", "PID-KELAS-O017-FUNGSI-KONSEP", "metadata"),
    RelationSpec("O017-U02-REL-066", "O017-U02", "contains", "PID-KELAS-O017-FUNGSI-V1", "metadata"),
    RelationSpec("O017-U02-REL-067", "O017-U02", "contains", "PID-KELAS-O017-FUNGSI-V2", "metadata"),
    RelationSpec("O017-U02-REL-068", "O017-U02", "contains", "O017-U02-SRC-FUNGSI-LECTURE-NOTE", "metadata"),
    RelationSpec("O017-U02-REL-069", "O017-U02", "contains", "O017-U02-SRC-FUNGSI-TEXTBOOK-E2", "metadata"),
    RelationSpec("O017-U02-REL-070", "O017-U02-SRC-S2", "identifies", "PID-KELAS-O017-DERET-V1", "metadata"),
    RelationSpec("O017-U02-REL-071", "O017-U02-SRC-S3", "identifies", "PID-KELAS-O017-DERET-V2", "metadata"),
    RelationSpec("O017-U02-REL-072", "O017-U02-SRC-S1", "cites", "PID-KELAS-O017-DERET-KONSEP", "metadata"),
    RelationSpec("O017-U02-REL-073", "PID-KELAS-O017-DERET-KONSEP", "hasVersion", "PID-KELAS-O017-DERET-V1", "metadata"),
    RelationSpec("O017-U02-REL-074", "PID-KELAS-O017-DERET-KONSEP", "hasVersion", "PID-KELAS-O017-DERET-V2", "metadata"),
    RelationSpec("O017-U02-REL-075", "PID-KELAS-O017-DERET-V2", "isNewVersionOf", "PID-KELAS-O017-DERET-V1", "metadata"),
    RelationSpec("O017-U02-REL-076", "O017-U02-THEOREM-K2", "corrects", "O017-U02-THEOREM-K1", "metadata"),
    RelationSpec("O017-U02-REL-077", "PID-KELAS-O017-DERET-V2", "cites", "O017-U02-SRC-S4", "metadata"),
    RelationSpec("O017-U02-REL-078", "O017-U02-SRC-S1", "quotes", "O017-U02-THEOREM-K1", "metadata"),
    RelationSpec("O017-U02-REL-079", "O017-U02-THEOREM-K1", "stated-in", "PID-KELAS-O017-DERET-V1", "metadata"),
    RelationSpec("O017-U02-REL-080", "O017-U02-THEOREM-K2", "stated-in", "PID-KELAS-O017-DERET-V2", "metadata"),
    RelationSpec("O017-U02-REL-081", "O017-U02-SRC-S1", "likely-used-version", "PID-KELAS-O017-DERET-V1", "inference"),
    RelationSpec("O017-U02-REL-082", "O017-U02-THEOREM-K2", "proved-by", "O017-U02-PROOF-K2", "mathematical-proof"),
    RelationSpec("O017-U02-REL-083", "O017-U02-COUNTEREXAMPLE-K1", "refutes", "O017-U02-THEOREM-K1", "mathematical-counterexample"),
    RelationSpec("O017-U02-REL-084", "O017-U02-COUNTEREXAMPLE-K1", "supported-by", "O017-U02-SRC-S4", "mathematical-support"),
    RelationSpec("O017-U02-REL-085", "O017-U02-SRC-FUNGSI-LECTURE-NOTE", "cites", "PID-KELAS-O017-FUNGSI-KONSEP", "metadata"),
    RelationSpec("O017-U02-REL-086", "PID-KELAS-O017-FUNGSI-KONSEP", "hasVersion", "PID-KELAS-O017-FUNGSI-V1", "metadata"),
    RelationSpec("O017-U02-REL-087", "PID-KELAS-O017-FUNGSI-KONSEP", "hasVersion", "PID-KELAS-O017-FUNGSI-V2", "metadata"),
    RelationSpec("O017-U02-REL-088", "PID-KELAS-O017-FUNGSI-V2", "isNewVersionOf", "PID-KELAS-O017-FUNGSI-V1", "metadata"),
    RelationSpec("O017-U02-REL-089", "PID-KELAS-O017-FUNGSI-V2", "corrects", "PID-KELAS-O017-FUNGSI-V1", "metadata"),
    RelationSpec("O017-U02-REL-090", "O017-U02-SRC-FUNGSI-TEXTBOOK-E2", "independently-supports", "PID-KELAS-O017-FUNGSI-V2", "mathematical-support"),
    RelationSpec("O017-U02-REL-091", "O017-U02-SRC-S0", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-092", "O017-U02-SRC-S1", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-093", "O017-U02-SRC-S2", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-094", "O017-U02-SRC-S3", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-095", "O017-U02-SRC-S4", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-096", "PID-KELAS-O017-DERET-KONSEP", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-097", "PID-KELAS-O017-DERET-V1", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-098", "PID-KELAS-O017-DERET-V2", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-099", "PID-KELAS-O017-FUNGSI-KONSEP", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-100", "PID-KELAS-O017-FUNGSI-V1", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-101", "PID-KELAS-O017-FUNGSI-V2", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-102", "O017-U02-SRC-FUNGSI-LECTURE-NOTE", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-103", "O017-U02-SRC-FUNGSI-TEXTBOOK-E2", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U02-REL-104", "O017-U02-X01", "guided-by", "O017-U02-H01", "metadata"),
    RelationSpec("O017-U02-REL-105", "O017-U02-X02", "guided-by", "O017-U02-H02", "metadata"),
    RelationSpec("O017-U02-REL-106", "O017-U02-X03", "guided-by", "O017-U02-H03", "metadata"),
    RelationSpec("O017-U02-REL-107", "O017-U02-X04", "guided-by", "O017-U02-H04", "metadata"),
    RelationSpec("O017-U02-REL-108", "O017-U02-X05", "guided-by", "O017-U02-H05", "metadata"),
    RelationSpec("O017-U02-REL-109", "O017-U02-X06", "guided-by", "O017-U02-H06", "metadata"),
    RelationSpec("O017-U02-REL-110", "O017-U02", "cites", "O017-CIT-TTW-C98A", "metadata"),
    RelationSpec("O017-U02-REL-111", "O017-CIT-TTW-C98A", "identifies", "O017-SOURCE-TTW-C98A", "metadata"),
    RelationSpec("O017-U02-REL-112", "O017-CIT-PYRSE", "identifies", "O017-SOURCE-PYRSE-BOOK-2021", "metadata"),
    RelationSpec("O017-U02-REL-113", "O017-CIT-TTW", "identifies", "O017-SOURCE-TTW-RELEASE-1-2-3", "metadata"),
    RelationSpec("O017-U02-REL-114", "O017-U02", "cites", "O017-CIT-PYRSE-6221", "metadata"),
    RelationSpec("O017-U02-REL-115", "O017-CIT-PYRSE-6221", "identifies", "O017-SOURCE-PYRSE-6221", "metadata"),
    RelationSpec("O017-U02-REL-116", "O017-SOURCE-PYRSE-BOOK-2021", "governed-by", "O017-RIGHTS-PYRSE", "metadata"),
    RelationSpec("O017-U02-REL-117", "O017-SOURCE-TTW-RELEASE-1-2-3", "governed-by", "O017-RIGHTS-TTW", "metadata"),
)


UNIT2 = UnitSpec(
    id="O017-U02",
    ordinal=2,
    title="Menelusuri Literatur dan Menilai Otoritas Sumber",
    source_path=SOURCE / "units" / "02-menelusuri-sumber.qmd",
    html_relative_path=Path("units/02-menelusuri-sumber.html"),
    required_section_ids=frozenset(
        {
            "o017-u02-outcomes",
            "o017-u02-claim-to-source",
            "o017-u02-search-card",
            "o017-u02-three-pass",
            "o017-u02-stop-rule",
            "o017-u02-five-surfaces",
            "o017-u02-authority-matrix",
            "o017-u02-editions-pids",
            "o017-u02-typed-relations",
            "o017-u02-worked-case",
            "o017-u02-source-packet-series",
            "o017-u02-series-v1-audit",
            "thm-o017-u02-v1",
            "o017-u02-counterexample-v1",
            "o017-u02-series-v2-audit",
            "thm-o017-u02-v2",
            "prf-o017-u02-v2",
            "o017-u02-citation-choice",
            "o017-u02-minimal-ledger",
            "o017-u02-exercises",
            "o017-u02-guidance",
            "o017-u02-completion-task",
            "o017-u02-completion-rubric",
            "o017-u02-boundary",
            "o017-u02-provenance",
        }
    ),
    required_entity_fragments=frozenset(
        {
            "o017-u02-def01",
            "o017-u02-def-pid",
            "o017-u02-src-s0",
            "o017-u02-src-s1",
            "o017-u02-src-s2",
            "o017-u02-src-s3",
            "o017-u02-src-s4",
            "o017-u02-pid-concept",
            "o017-u02-pid-v1",
            "o017-u02-pid-v2",
            "thm-o017-u02-v1",
            "o017-u02-counterexample-v1",
            "thm-o017-u02-v2",
            "prf-o017-u02-v2",
            "ref-turingway2022",
            "ref-turingwaycommitc98a",
            "ref-irving2021",
            "ref-pyrsecommit62217",
            *{f"o017-u02-x{index:02d}" for index in range(1, 7)},
            *{f"o017-u02-h{index:02d}" for index in range(1, 7)},
        }
    ),
    exercise_solution_pairs=tuple(
        (f"O017-U02-X{index:02d}", f"O017-U02-H{index:02d}")
        for index in range(1, 7)
    ),
    computations=(),
    records_factory=unit2_records,
    relations=UNIT2_RELATIONS,
    manifest_inputs=(),
    scope_notes=(
        "All worked-case and completion-package people, titles, dates, and PID-KELAS identifiers are synthetic classroom data, not public citations.",
        "Authority is represented across proximity, version traceability, provenance, locator, and support dimensions; missing fields remain unresolved rather than inferred.",
        "The Turing Way release citation and the exact c98a source-witness citation remain distinct and point to their respective identities.",
        "The py-rse book citation and exact 62217 source-witness citation likewise point to distinct work and commit-source identities.",
        "Issued Unit 1 relation IDs O017-REL-001 and O017-REL-002 retain their original triples in the immutable ledger, but are machine-marked superseded by correctly scoped book/release relations issued in Unit 2.",
        "The seminar summary's likely use of version 1 is an inference from wording and chronology, not recorded metadata.",
        "Unit 2 teaches source identity and version relations; full provenance notebooks remain Unit 4 scope.",
    ),
    admission_filename="UNIT_02_ADMISSION.md",
    qa_filename="UNIT_02_QA.json",
    visual_qa_filename="UNIT_02_VISUAL_QA.json",
    visual_qa_script_filename="visual_qa_unit.cjs",
    expected_source_sha256="f18e5579a6ece824a4a3dddb9344868755aeedc4c70665364023fa5e36c90d17",
    expected_id_type_sha256="daeedc50cd916ceb97147e130a823c71896cf89727887e96269b625e87c444b4",
    expected_relation_map_sha256="7b4b1d453fc24a598c0f4a4a11ec9be28d5831aef623673db79d473d8295201e",
)


def unit3_records(hashes: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = [
        record(
            "unit",
            "O017-U03",
            ordinal=3,
            title="Merekonstruksi Pembuktian yang Diringkas atau Dihilangkan",
            locale="id-ID",
        ),
        record(
            "definition",
            "O017-U03-D01",
            unit="O017-U03",
            html_fragment="o017-u03-frozen-statement",
            title="Kekompakan melalui liputan terbuka pada ruang induk",
        ),
        record(
            "definition",
            "O017-U03-D02",
            unit="O017-U03",
            html_fragment="o017-u03-stage-obligations",
            title="Kewajiban pembuktian yang dapat diaudit",
        ),
        record(
            "definition",
            "O017-U03-D03",
            unit="O017-U03",
            html_fragment="o017-u03-stage-lemma-retrieval",
            title="Kontrak lemma",
        ),
        record(
            "definition",
            "O017-U03-D04",
            unit="O017-U03",
            html_fragment="o017-u03-stage-minimal-proof",
            title="Status celah rekonstruksi",
        ),
        record(
            "theorem",
            "O017-U03-THEOREM-COMPACT-IMAGE",
            unit="O017-U03",
            html_fragment="thm-o017-u03-compact-image",
            title="Citra kontinu dari himpunan kompak",
            claim_status="proved",
        ),
        record(
            "proof",
            "O017-U03-PROOF-COMPACT-IMAGE",
            unit="O017-U03",
            html_fragment="prf-o017-u03-compact-image",
            proves="O017-U03-THEOREM-COMPACT-IMAGE",
            method="open-cover pullback with explicit quantifier and domain audit",
        ),
        record(
            "theorem",
            "O017-U03-THEOREM-HAUSDORFF-CLOSED",
            unit="O017-U03",
            html_fragment="o017-u03-lemma-audit",
            title="Himpunan kompak dalam ruang Hausdorff tertutup",
            claim_status="proved-locally",
        ),
        record(
            "proof",
            "O017-U03-PROOF-HAUSDORFF-CLOSED",
            unit="O017-U03",
            html_fragment="o017-u03-lemma-audit",
            proves="O017-U03-THEOREM-HAUSDORFF-CLOSED",
            method="Hausdorff separation followed by a finite subcover",
        ),
        record(
            "counterexample",
            "O017-U03-COUNTEREXAMPLE-COVER-SCOPE",
            unit="O017-U03",
            html_fragment="o017-u03-cover-scope-error",
            refutes="a cover of f[K] must cover the whole codomain or domain",
        ),
        record(
            "counterexample",
            "O017-U03-COUNTEREXAMPLE-IMAGE-PREIMAGE",
            unit="O017-U03",
            html_fragment="o017-u03-image-preimage-error",
            refutes="f[f^{-1}[V]] equals V for an arbitrary function",
        ),
        record(
            "counterexample",
            "O017-U03-COUNTEREXAMPLE-NONCOMPACT",
            unit="O017-U03",
            html_fragment="o017-u03-counterexample-noncompact",
            witness="the inclusion of (0,1) into the real line",
        ),
        record(
            "counterexample",
            "O017-U03-COUNTEREXAMPLE-DISCONTINUOUS",
            unit="O017-U03",
            html_fragment="o017-u03-counterexample-discontinuous",
            witness="g(0)=0 and g(1/n)=n on a compact convergent sequence",
        ),
        record(
            "counterexample",
            "O017-U03-COUNTEREXAMPLE-SIERPINSKI",
            unit="O017-U03",
            html_fragment="o017-u03-lemma-audit",
            witness="the compact nonclosed singleton {1} in Sierpinski space",
        ),
        record(
            "qa_event",
            "O017-U03-QA-01",
            status="pass",
            checks=[
                "source-hash-lock",
                "html-structure",
                "offline-mathml",
                "local-link-closure",
                "exercise-solution-correspondence",
                "quantifier-domain-audit",
                "proof-dependency-closure",
                "counterexample-correctness",
                "lemma-contract-hypothesis-check",
                "rights-attribution",
                "backend-referential-integrity",
            ],
        ),
        record(
            "artifact",
            "O017-U03-ARTIFACT-HTML",
            path="build/html/units/03-merekonstruksi-pembuktian.html",
            sha256=hashes["html"],
            media_type="text/html",
        ),
    ]

    concepts = (
        ("O017-CONCEPT-CLAIM-CONTEXT-FREEZE", "pembekuan klaim dan konteks"),
        ("O017-CONCEPT-QUANTIFIER-DOMAIN-AUDIT", "audit kuantor dan domain"),
        ("O017-CONCEPT-PROOF-DEPENDENCY-GRAPH", "graf ketergantungan pembuktian"),
        ("O017-CONCEPT-LEMMA-CONTRACT", "kontrak lemma"),
        ("O017-CONCEPT-BIDIRECTIONAL-PROOF-PLANNING", "perencanaan pembuktian dua arah"),
        ("O017-CONCEPT-MINIMAL-SUFFICIENT-RECONSTRUCTION", "rekonstruksi minimal yang memadai"),
        ("O017-CONCEPT-GAP-STATUS", "status celah pembuktian"),
        ("O017-CONCEPT-HYPOTHESIS-STRESS-TEST", "uji tekanan hipotesis"),
        ("O017-CONCEPT-TYPED-PROOF-RECONSTRUCTION", "rekonstruksi pembuktian bertipe"),
    )
    records.extend(
        record("concept", identifier, label_id=label, unit="O017-U03")
        for identifier, label in concepts
    )

    segments = (
        ("O017-U03-SEG-OUTCOMES", "o017-u03-outcomes"),
        ("O017-U03-SEG-RECONSTRUCTION-PROBLEM", "o017-u03-reconstruction-problem"),
        ("O017-U03-SEG-SEVEN-STAGE-PROTOCOL", "o017-u03-seven-stage-protocol"),
        ("O017-U03-SEG-STAGE-FREEZE", "o017-u03-stage-freeze"),
        ("O017-U03-SEG-STAGE-QUANTIFIERS", "o017-u03-stage-quantifiers"),
        ("O017-U03-SEG-STAGE-OBLIGATIONS", "o017-u03-stage-obligations"),
        ("O017-U03-SEG-STAGE-DEPENDENCY-GRAPH", "o017-u03-stage-dependency-graph"),
        ("O017-U03-SEG-STAGE-LEMMA-RETRIEVAL", "o017-u03-stage-lemma-retrieval"),
        ("O017-U03-SEG-STAGE-BIDIRECTIONAL-PLANNING", "o017-u03-stage-bidirectional-planning"),
        ("O017-U03-SEG-STAGE-MINIMAL-PROOF", "o017-u03-stage-minimal-proof"),
        ("O017-U03-SEG-RECONSTRUCTION-SHEET", "o017-u03-reconstruction-sheet"),
        ("O017-U03-SEG-WORKED-CASE", "o017-u03-worked-case"),
        ("O017-U03-SEG-FROZEN-STATEMENT", "o017-u03-frozen-statement"),
        ("O017-U03-SEG-QUANTIFIER-DOMAIN-AUDIT", "o017-u03-quantifier-domain-audit"),
        ("O017-U03-SEG-OBLIGATIONS", "o017-u03-obligations"),
        ("O017-U03-SEG-COMPACT-IMAGE-GRAPH", "o017-u03-compact-image-graph"),
        ("O017-U03-SEG-NEEDED-LEMMAS", "o017-u03-needed-lemmas"),
        ("O017-U03-SEG-TWO-WAY-PLAN", "o017-u03-two-way-plan"),
        ("O017-U03-SEG-COMPLETE-RECONSTRUCTION", "o017-u03-complete-reconstruction"),
        ("O017-U03-SEG-MINIMALITY-AUDIT", "o017-u03-minimality-audit"),
        ("O017-U03-SEG-INVALID-SHORTCUTS", "o017-u03-invalid-shortcuts"),
        ("O017-U03-SEG-COVER-SCOPE-ERROR", "o017-u03-cover-scope-error"),
        ("O017-U03-SEG-IMAGE-PREIMAGE-ERROR", "o017-u03-image-preimage-error"),
        ("O017-U03-SEG-OPENNESS-DOMAIN-ERROR", "o017-u03-openness-domain-error"),
        ("O017-U03-SEG-ASSUMPTION-STRESS-TESTS", "o017-u03-assumption-stress-tests"),
        ("O017-U03-SEG-COUNTEREXAMPLE-NONCOMPACT", "o017-u03-counterexample-noncompact"),
        ("O017-U03-SEG-COUNTEREXAMPLE-DISCONTINUOUS", "o017-u03-counterexample-discontinuous"),
        ("O017-U03-SEG-LEMMA-AUDIT", "o017-u03-lemma-audit"),
        ("O017-U03-SEG-DETAIL-LEVEL", "o017-u03-detail-level"),
        ("O017-U03-SEG-SHORT-AUDIT", "o017-u03-short-audit"),
        ("O017-U03-SEG-EXERCISES", "o017-u03-exercises"),
        ("O017-U03-SEG-GUIDANCE", "o017-u03-guidance"),
        ("O017-U03-SEG-COMPLETION", "o017-u03-completion-task"),
        ("O017-U03-SEG-RUBRIC", "o017-u03-completion-rubric"),
        ("O017-U03-SEG-BOUNDARY", "o017-u03-boundary"),
        ("O017-U03-SEG-PROVENANCE", "o017-u03-provenance"),
    )
    records.extend(
        record("segment", identifier, unit="O017-U03", html_fragment=fragment)
        for identifier, fragment in segments
    )

    for index in range(1, 7):
        records.extend(
            (
                record(
                    "exercise",
                    f"O017-U03-X{index:02d}",
                    unit="O017-U03",
                    ordinal=index,
                    html_fragment=f"o017-u03-x{index:02d}",
                ),
                record(
                    "solution",
                    f"O017-U03-H{index:02d}",
                    unit="O017-U03",
                    ordinal=index,
                    solution_kind="guidance",
                    html_fragment=f"o017-u03-h{index:02d}",
                ),
            )
        )
    return tuple(records)


# Unit 3 relation IDs are issued in a unit namespace.  Keep every mapping
# explicit: neither this table nor future aggregate sorting allocates IDs.
UNIT3_RELATIONS = (
    RelationSpec("O017-U03-REL-001", "O017-EDITION-01", "contains", "O017-U03", "metadata"),
    RelationSpec("O017-U03-REL-002", "O017-U03", "authored-from", "O017-SOURCE-ORIGINAL", "metadata"),
    RelationSpec("O017-U03-REL-003", "O017-U03", "licensed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U03-REL-004", "O017-SOURCE-ORIGINAL", "governed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U03-REL-005", "O017-U03", "verified-by", "O017-U03-QA-01", "metadata"),
    RelationSpec("O017-U03-REL-006", "O017-U03", "has-artifact", "O017-U03-ARTIFACT-HTML", "metadata"),
    RelationSpec("O017-U03-REL-007", "O017-U03", "teaches", "O017-CONCEPT-CLAIM-CONTEXT-FREEZE", "metadata"),
    RelationSpec("O017-U03-REL-008", "O017-U03", "teaches", "O017-CONCEPT-QUANTIFIER-DOMAIN-AUDIT", "metadata"),
    RelationSpec("O017-U03-REL-009", "O017-U03", "teaches", "O017-CONCEPT-PROOF-DEPENDENCY-GRAPH", "metadata"),
    RelationSpec("O017-U03-REL-010", "O017-U03", "teaches", "O017-CONCEPT-LEMMA-CONTRACT", "metadata"),
    RelationSpec("O017-U03-REL-011", "O017-U03", "teaches", "O017-CONCEPT-BIDIRECTIONAL-PROOF-PLANNING", "metadata"),
    RelationSpec("O017-U03-REL-012", "O017-U03", "teaches", "O017-CONCEPT-MINIMAL-SUFFICIENT-RECONSTRUCTION", "metadata"),
    RelationSpec("O017-U03-REL-013", "O017-U03", "teaches", "O017-CONCEPT-GAP-STATUS", "metadata"),
    RelationSpec("O017-U03-REL-014", "O017-U03", "teaches", "O017-CONCEPT-HYPOTHESIS-STRESS-TEST", "metadata"),
    RelationSpec("O017-U03-REL-015", "O017-U03", "teaches", "O017-CONCEPT-TYPED-PROOF-RECONSTRUCTION", "metadata"),
    RelationSpec("O017-U03-REL-016", "O017-U03", "contains", "O017-U03-SEG-OUTCOMES", "metadata"),
    RelationSpec("O017-U03-REL-017", "O017-U03", "contains", "O017-U03-SEG-RECONSTRUCTION-PROBLEM", "metadata"),
    RelationSpec("O017-U03-REL-018", "O017-U03", "contains", "O017-U03-SEG-SEVEN-STAGE-PROTOCOL", "metadata"),
    RelationSpec("O017-U03-REL-019", "O017-U03", "contains", "O017-U03-SEG-STAGE-FREEZE", "metadata"),
    RelationSpec("O017-U03-REL-020", "O017-U03", "contains", "O017-U03-SEG-STAGE-QUANTIFIERS", "metadata"),
    RelationSpec("O017-U03-REL-021", "O017-U03", "contains", "O017-U03-SEG-STAGE-OBLIGATIONS", "metadata"),
    RelationSpec("O017-U03-REL-022", "O017-U03", "contains", "O017-U03-SEG-STAGE-DEPENDENCY-GRAPH", "metadata"),
    RelationSpec("O017-U03-REL-023", "O017-U03", "contains", "O017-U03-SEG-STAGE-LEMMA-RETRIEVAL", "metadata"),
    RelationSpec("O017-U03-REL-024", "O017-U03", "contains", "O017-U03-SEG-STAGE-BIDIRECTIONAL-PLANNING", "metadata"),
    RelationSpec("O017-U03-REL-025", "O017-U03", "contains", "O017-U03-SEG-STAGE-MINIMAL-PROOF", "metadata"),
    RelationSpec("O017-U03-REL-026", "O017-U03", "contains", "O017-U03-SEG-RECONSTRUCTION-SHEET", "metadata"),
    RelationSpec("O017-U03-REL-027", "O017-U03", "contains", "O017-U03-SEG-WORKED-CASE", "metadata"),
    RelationSpec("O017-U03-REL-028", "O017-U03", "contains", "O017-U03-SEG-FROZEN-STATEMENT", "metadata"),
    RelationSpec("O017-U03-REL-029", "O017-U03", "contains", "O017-U03-SEG-QUANTIFIER-DOMAIN-AUDIT", "metadata"),
    RelationSpec("O017-U03-REL-030", "O017-U03", "contains", "O017-U03-SEG-OBLIGATIONS", "metadata"),
    RelationSpec("O017-U03-REL-031", "O017-U03", "contains", "O017-U03-SEG-COMPACT-IMAGE-GRAPH", "metadata"),
    RelationSpec("O017-U03-REL-032", "O017-U03", "contains", "O017-U03-SEG-NEEDED-LEMMAS", "metadata"),
    RelationSpec("O017-U03-REL-033", "O017-U03", "contains", "O017-U03-SEG-TWO-WAY-PLAN", "metadata"),
    RelationSpec("O017-U03-REL-034", "O017-U03", "contains", "O017-U03-SEG-COMPLETE-RECONSTRUCTION", "metadata"),
    RelationSpec("O017-U03-REL-035", "O017-U03", "contains", "O017-U03-SEG-MINIMALITY-AUDIT", "metadata"),
    RelationSpec("O017-U03-REL-036", "O017-U03", "contains", "O017-U03-SEG-INVALID-SHORTCUTS", "metadata"),
    RelationSpec("O017-U03-REL-037", "O017-U03", "contains", "O017-U03-SEG-COVER-SCOPE-ERROR", "metadata"),
    RelationSpec("O017-U03-REL-038", "O017-U03", "contains", "O017-U03-SEG-IMAGE-PREIMAGE-ERROR", "metadata"),
    RelationSpec("O017-U03-REL-039", "O017-U03", "contains", "O017-U03-SEG-OPENNESS-DOMAIN-ERROR", "metadata"),
    RelationSpec("O017-U03-REL-040", "O017-U03", "contains", "O017-U03-SEG-ASSUMPTION-STRESS-TESTS", "metadata"),
    RelationSpec("O017-U03-REL-041", "O017-U03", "contains", "O017-U03-SEG-COUNTEREXAMPLE-NONCOMPACT", "metadata"),
    RelationSpec("O017-U03-REL-042", "O017-U03", "contains", "O017-U03-SEG-COUNTEREXAMPLE-DISCONTINUOUS", "metadata"),
    RelationSpec("O017-U03-REL-043", "O017-U03", "contains", "O017-U03-SEG-LEMMA-AUDIT", "metadata"),
    RelationSpec("O017-U03-REL-044", "O017-U03", "contains", "O017-U03-SEG-DETAIL-LEVEL", "metadata"),
    RelationSpec("O017-U03-REL-045", "O017-U03", "contains", "O017-U03-SEG-SHORT-AUDIT", "metadata"),
    RelationSpec("O017-U03-REL-046", "O017-U03", "contains", "O017-U03-SEG-EXERCISES", "metadata"),
    RelationSpec("O017-U03-REL-047", "O017-U03", "contains", "O017-U03-SEG-GUIDANCE", "metadata"),
    RelationSpec("O017-U03-REL-048", "O017-U03", "contains", "O017-U03-SEG-COMPLETION", "metadata"),
    RelationSpec("O017-U03-REL-049", "O017-U03", "contains", "O017-U03-SEG-RUBRIC", "metadata"),
    RelationSpec("O017-U03-REL-050", "O017-U03", "contains", "O017-U03-SEG-BOUNDARY", "metadata"),
    RelationSpec("O017-U03-REL-051", "O017-U03", "contains", "O017-U03-SEG-PROVENANCE", "metadata"),
    RelationSpec("O017-U03-REL-052", "O017-U03", "contains", "O017-U03-D01", "metadata"),
    RelationSpec("O017-U03-REL-053", "O017-U03", "contains", "O017-U03-D02", "metadata"),
    RelationSpec("O017-U03-REL-054", "O017-U03", "contains", "O017-U03-D03", "metadata"),
    RelationSpec("O017-U03-REL-055", "O017-U03", "contains", "O017-U03-D04", "metadata"),
    RelationSpec("O017-U03-REL-056", "O017-U03", "contains", "O017-U03-THEOREM-COMPACT-IMAGE", "metadata"),
    RelationSpec("O017-U03-REL-057", "O017-U03", "contains", "O017-U03-THEOREM-HAUSDORFF-CLOSED", "metadata"),
    RelationSpec("O017-U03-REL-058", "O017-U03", "contains", "O017-U03-PROOF-COMPACT-IMAGE", "metadata"),
    RelationSpec("O017-U03-REL-059", "O017-U03", "contains", "O017-U03-PROOF-HAUSDORFF-CLOSED", "metadata"),
    RelationSpec("O017-U03-REL-060", "O017-U03", "contains", "O017-U03-COUNTEREXAMPLE-COVER-SCOPE", "metadata"),
    RelationSpec("O017-U03-REL-061", "O017-U03", "contains", "O017-U03-COUNTEREXAMPLE-IMAGE-PREIMAGE", "metadata"),
    RelationSpec("O017-U03-REL-062", "O017-U03", "contains", "O017-U03-COUNTEREXAMPLE-NONCOMPACT", "metadata"),
    RelationSpec("O017-U03-REL-063", "O017-U03", "contains", "O017-U03-COUNTEREXAMPLE-DISCONTINUOUS", "metadata"),
    RelationSpec("O017-U03-REL-064", "O017-U03", "contains", "O017-U03-COUNTEREXAMPLE-SIERPINSKI", "metadata"),
    RelationSpec("O017-U03-REL-065", "O017-U03", "contains", "O017-U03-X01", "metadata"),
    RelationSpec("O017-U03-REL-066", "O017-U03", "contains", "O017-U03-H01", "metadata"),
    RelationSpec("O017-U03-REL-067", "O017-U03", "contains", "O017-U03-X02", "metadata"),
    RelationSpec("O017-U03-REL-068", "O017-U03", "contains", "O017-U03-H02", "metadata"),
    RelationSpec("O017-U03-REL-069", "O017-U03", "contains", "O017-U03-X03", "metadata"),
    RelationSpec("O017-U03-REL-070", "O017-U03", "contains", "O017-U03-H03", "metadata"),
    RelationSpec("O017-U03-REL-071", "O017-U03", "contains", "O017-U03-X04", "metadata"),
    RelationSpec("O017-U03-REL-072", "O017-U03", "contains", "O017-U03-H04", "metadata"),
    RelationSpec("O017-U03-REL-073", "O017-U03", "contains", "O017-U03-X05", "metadata"),
    RelationSpec("O017-U03-REL-074", "O017-U03", "contains", "O017-U03-H05", "metadata"),
    RelationSpec("O017-U03-REL-075", "O017-U03", "contains", "O017-U03-X06", "metadata"),
    RelationSpec("O017-U03-REL-076", "O017-U03", "contains", "O017-U03-H06", "metadata"),
    RelationSpec("O017-U03-REL-077", "O017-U03-THEOREM-COMPACT-IMAGE", "proved-by", "O017-U03-PROOF-COMPACT-IMAGE", "mathematical-proof"),
    RelationSpec("O017-U03-REL-078", "O017-U03-THEOREM-HAUSDORFF-CLOSED", "proved-by", "O017-U03-PROOF-HAUSDORFF-CLOSED", "mathematical-proof"),
    RelationSpec("O017-U03-REL-079", "O017-U03-COUNTEREXAMPLE-COVER-SCOPE", "illustrates", "O017-CONCEPT-QUANTIFIER-DOMAIN-AUDIT", "mathematical-counterexample"),
    RelationSpec("O017-U03-REL-080", "O017-U03-COUNTEREXAMPLE-IMAGE-PREIMAGE", "illustrates", "O017-CONCEPT-QUANTIFIER-DOMAIN-AUDIT", "mathematical-counterexample"),
    RelationSpec("O017-U03-REL-081", "O017-U03-COUNTEREXAMPLE-NONCOMPACT", "stress-tests", "O017-U03-THEOREM-COMPACT-IMAGE", "mathematical-counterexample"),
    RelationSpec("O017-U03-REL-082", "O017-U03-COUNTEREXAMPLE-DISCONTINUOUS", "stress-tests", "O017-U03-THEOREM-COMPACT-IMAGE", "mathematical-counterexample"),
    RelationSpec("O017-U03-REL-083", "O017-U03-COUNTEREXAMPLE-SIERPINSKI", "bounds-application-of", "O017-U03-THEOREM-HAUSDORFF-CLOSED", "mathematical-counterexample"),
    RelationSpec("O017-U03-REL-084", "O017-U03-X01", "guided-by", "O017-U03-H01", "metadata"),
    RelationSpec("O017-U03-REL-085", "O017-U03-X02", "guided-by", "O017-U03-H02", "metadata"),
    RelationSpec("O017-U03-REL-086", "O017-U03-X03", "guided-by", "O017-U03-H03", "metadata"),
    RelationSpec("O017-U03-REL-087", "O017-U03-X04", "guided-by", "O017-U03-H04", "metadata"),
    RelationSpec("O017-U03-REL-088", "O017-U03-X05", "guided-by", "O017-U03-H05", "metadata"),
    RelationSpec("O017-U03-REL-089", "O017-U03-X06", "guided-by", "O017-U03-H06", "metadata"),
    RelationSpec("O017-U03-REL-090", "O017-U03-D01", "described-in", "O017-U03-SEG-FROZEN-STATEMENT", "metadata"),
    RelationSpec("O017-U03-REL-091", "O017-U03-D02", "described-in", "O017-U03-SEG-STAGE-OBLIGATIONS", "metadata"),
    RelationSpec("O017-U03-REL-092", "O017-U03-D03", "described-in", "O017-U03-SEG-STAGE-LEMMA-RETRIEVAL", "metadata"),
    RelationSpec("O017-U03-REL-093", "O017-U03-D04", "described-in", "O017-U03-SEG-STAGE-MINIMAL-PROOF", "metadata"),
    RelationSpec("O017-U03-REL-094", "O017-U03-THEOREM-COMPACT-IMAGE", "stated-in", "O017-U03-SEG-FROZEN-STATEMENT", "metadata"),
    RelationSpec("O017-U03-REL-095", "O017-U03-THEOREM-HAUSDORFF-CLOSED", "stated-in", "O017-U03-SEG-LEMMA-AUDIT", "metadata"),
    RelationSpec("O017-U03-REL-096", "O017-U03-PROOF-COMPACT-IMAGE", "presented-in", "O017-U03-SEG-COMPLETE-RECONSTRUCTION", "metadata"),
    RelationSpec("O017-U03-REL-097", "O017-U03-PROOF-HAUSDORFF-CLOSED", "presented-in", "O017-U03-SEG-LEMMA-AUDIT", "metadata"),
    RelationSpec("O017-U03-REL-098", "O017-U03-COUNTEREXAMPLE-COVER-SCOPE", "presented-in", "O017-U03-SEG-COVER-SCOPE-ERROR", "metadata"),
    RelationSpec("O017-U03-REL-099", "O017-U03-COUNTEREXAMPLE-IMAGE-PREIMAGE", "presented-in", "O017-U03-SEG-IMAGE-PREIMAGE-ERROR", "metadata"),
    RelationSpec("O017-U03-REL-100", "O017-U03-COUNTEREXAMPLE-NONCOMPACT", "presented-in", "O017-U03-SEG-COUNTEREXAMPLE-NONCOMPACT", "metadata"),
    RelationSpec("O017-U03-REL-101", "O017-U03-COUNTEREXAMPLE-DISCONTINUOUS", "presented-in", "O017-U03-SEG-COUNTEREXAMPLE-DISCONTINUOUS", "metadata"),
    RelationSpec("O017-U03-REL-102", "O017-U03-COUNTEREXAMPLE-SIERPINSKI", "presented-in", "O017-U03-SEG-LEMMA-AUDIT", "metadata"),
    RelationSpec("O017-U03-REL-103", "O017-CONCEPT-CLAIM-CONTEXT-FREEZE", "developed-in", "O017-U03-SEG-STAGE-FREEZE", "metadata"),
    RelationSpec("O017-U03-REL-104", "O017-CONCEPT-QUANTIFIER-DOMAIN-AUDIT", "developed-in", "O017-U03-SEG-STAGE-QUANTIFIERS", "metadata"),
    RelationSpec("O017-U03-REL-105", "O017-CONCEPT-PROOF-DEPENDENCY-GRAPH", "developed-in", "O017-U03-SEG-STAGE-DEPENDENCY-GRAPH", "metadata"),
    RelationSpec("O017-U03-REL-106", "O017-CONCEPT-LEMMA-CONTRACT", "developed-in", "O017-U03-SEG-STAGE-LEMMA-RETRIEVAL", "metadata"),
    RelationSpec("O017-U03-REL-107", "O017-CONCEPT-BIDIRECTIONAL-PROOF-PLANNING", "developed-in", "O017-U03-SEG-STAGE-BIDIRECTIONAL-PLANNING", "metadata"),
    RelationSpec("O017-U03-REL-108", "O017-CONCEPT-MINIMAL-SUFFICIENT-RECONSTRUCTION", "developed-in", "O017-U03-SEG-MINIMALITY-AUDIT", "metadata"),
    RelationSpec("O017-U03-REL-109", "O017-CONCEPT-GAP-STATUS", "developed-in", "O017-U03-SEG-STAGE-MINIMAL-PROOF", "metadata"),
    RelationSpec("O017-U03-REL-110", "O017-CONCEPT-HYPOTHESIS-STRESS-TEST", "developed-in", "O017-U03-SEG-ASSUMPTION-STRESS-TESTS", "metadata"),
    RelationSpec("O017-U03-REL-111", "O017-CONCEPT-TYPED-PROOF-RECONSTRUCTION", "developed-in", "O017-U03-SEG-RECONSTRUCTION-SHEET", "metadata"),
    RelationSpec("O017-U03-REL-112", "O017-U03-QA-01", "verifies", "O017-U03-ARTIFACT-HTML", "metadata"),
)


UNIT3_SOURCE_ANCHORS = frozenset(
    {
        "o017-u03-outcomes",
        "o017-u03-reconstruction-problem",
        "o017-u03-seven-stage-protocol",
        "o017-u03-stage-freeze",
        "o017-u03-stage-quantifiers",
        "o017-u03-stage-obligations",
        "o017-u03-stage-dependency-graph",
        "o017-u03-stage-lemma-retrieval",
        "o017-u03-stage-bidirectional-planning",
        "o017-u03-stage-minimal-proof",
        "o017-u03-reconstruction-sheet",
        "o017-u03-worked-case",
        "o017-u03-frozen-statement",
        "thm-o017-u03-compact-image",
        "o017-u03-quantifier-domain-audit",
        "o017-u03-obligations",
        "o017-u03-compact-image-graph",
        "o017-u03-needed-lemmas",
        "o017-u03-two-way-plan",
        "o017-u03-complete-reconstruction",
        "prf-o017-u03-compact-image",
        "o017-u03-minimality-audit",
        "o017-u03-invalid-shortcuts",
        "o017-u03-cover-scope-error",
        "o017-u03-image-preimage-error",
        "o017-u03-openness-domain-error",
        "o017-u03-assumption-stress-tests",
        "o017-u03-counterexample-noncompact",
        "o017-u03-counterexample-discontinuous",
        "o017-u03-lemma-audit",
        "o017-u03-detail-level",
        "o017-u03-short-audit",
        "o017-u03-exercises",
        *{f"o017-u03-x{index:02d}" for index in range(1, 7)},
        "o017-u03-guidance",
        *{f"o017-u03-h{index:02d}" for index in range(1, 7)},
        "o017-u03-completion-task",
        "o017-u03-completion-rubric",
        "o017-u03-boundary",
        "o017-u03-provenance",
    }
)


UNIT3 = UnitSpec(
    id="O017-U03",
    ordinal=3,
    title="Merekonstruksi Pembuktian yang Diringkas atau Dihilangkan",
    source_path=SOURCE / "units" / "03-merekonstruksi-pembuktian.qmd",
    html_relative_path=Path("units/03-merekonstruksi-pembuktian.html"),
    required_section_ids=UNIT3_SOURCE_ANCHORS,
    required_entity_fragments=UNIT3_SOURCE_ANCHORS,
    exercise_solution_pairs=tuple(
        (f"O017-U03-X{index:02d}", f"O017-U03-H{index:02d}")
        for index in range(1, 7)
    ),
    computations=(),
    records_factory=unit3_records,
    relations=UNIT3_RELATIONS,
    manifest_inputs=(),
    scope_notes=(
        "Unit 3 is original O017 exposition built around classical topology results; no donor prose, figures, code, or exercises are adapted.",
        "Every abbreviated step in the compact-image case is resolved through explicit quantifiers, typed domains, proof obligations, and dependency edges.",
        "Counterexamples test the compactness, continuity, and Hausdorff boundaries without strengthening the frozen theorem statement.",
        "Unit 3 teaches logical proof reconstruction; computational implementation remains B80 and source/provenance notebooks remain later-unit scope.",
        "Unit 3 admission is not full-course completion.",
    ),
    admission_filename="UNIT_03_ADMISSION.md",
    qa_filename="UNIT_03_QA.json",
    visual_qa_filename="UNIT_03_VISUAL_QA.json",
    visual_qa_script_filename="visual_qa_unit.cjs",
    expected_source_sha256="9c91ad1f451a9b00c4fd2b8513aebf66b5ff75575922b47fab8351ab4fee52d9",
    expected_id_type_sha256="fb02c932290c89de347861df63f2a7bdd5aec326fdda1d8ce3de04235e772caf",
    expected_relation_map_sha256="e28010a1c7bb1240c5bc029be2e646c1625d827a32d07bec2b0c81c221cb3a78",
)


def unit4_records(hashes: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = [
        record(
            "unit",
            "O017-U04",
            ordinal=4,
            title="Sitasi, Provenance, dan Buku Catatan Sumber",
            locale="id-ID",
        ),
        record(
            "theorem",
            "O017-U04-CLAIM-PACKET-V1",
            unit="O017-U04",
            html_fragment="o017-u04-packet-v1",
            title="Klaim integral paket V1",
            claim_status="refuted",
        ),
        record(
            "correction",
            "O017-U04-CORRECTION-PACKET",
            unit="O017-U04",
            html_fragment="o017-u04-packet-correction",
            correction_kind="mathematical-statement",
            status="applied",
        ),
        record(
            "theorem",
            "O017-U04-CLAIM-PACKET-V2",
            unit="O017-U04",
            html_fragment="thm-o017-u04-packet-v2",
            title="Klaim integral paket V2",
            claim_status="proved",
        ),
        record(
            "proof",
            "O017-U04-PROOF-PACKET-V2",
            unit="O017-U04",
            html_fragment="prf-o017-u04-v2",
            proves="O017-U04-CLAIM-PACKET-V2",
            method="perbandingan dengan batas pangkat lokal",
        ),
        record(
            "counterexample",
            "O017-U04-COUNTEREXAMPLE-PACKET-V1",
            unit="O017-U04",
            html_fragment="o017-u04-v1-counterexample",
            refutes="O017-U04-CLAIM-PACKET-V1",
        ),
        record(
            "theorem",
            "O017-U04-COMPLETION-CLAIM-V1",
            unit="O017-U04",
            html_fragment="o017-u04-completion-v1",
            title="Klaim norma matriks V1",
            claim_status="superseded-for-student-audit",
        ),
        record(
            "correction",
            "O017-U04-COMPLETION-CORRECTION",
            unit="O017-U04",
            html_fragment="o017-u04-completion-correction",
            correction_kind="mathematical-statement",
            status="exercise-input",
        ),
        record(
            "theorem",
            "O017-U04-COMPLETION-CLAIM-V2",
            unit="O017-U04",
            html_fragment="o017-u04-completion-v2",
            title="Klaim norma matriks V2",
            claim_status="exercise-input",
        ),
        record(
            "qa_event",
            "O017-U04-QA-01",
            status="pass",
            checks=[
                "source-hash-lock",
                "html-structure",
                "offline-mathml",
                "local-link-closure",
                "exercise-solution-correspondence",
                "source-version-locator-separation",
                "correction-history-preservation",
                "counterexample-and-proof-correctness",
                "rights-attribution",
                "backend-referential-integrity",
            ],
        ),
        record(
            "artifact",
            "O017-U04-ARTIFACT-HTML",
            path="build/html/units/04-sitasi-provenance-catatan-sumber.html",
            sha256=hashes["html"],
            media_type="text/html",
        ),
    ]

    concepts = (
        ("O017-CONCEPT-CITATION-VS-PROVENANCE", "pemisahan sitasi dan provenance"),
        ("O017-CONCEPT-SOURCE-IDENTITY-LEVELS", "tingkat identitas sumber"),
        ("O017-CONCEPT-SOURCE-OBJECT-EVENT", "lapis objek dan peristiwa sumber"),
        ("O017-CONCEPT-CLAIM-LOCATOR-CHAIN", "rantai klaim ke penunjuk"),
        ("O017-CONCEPT-EVIDENCE-PROVENANCE", "provenance bukti"),
        ("O017-CONCEPT-COMPUTATION-PROVENANCE", "provenance komputasi"),
        ("O017-CONCEPT-CORRECTION-HISTORY", "sejarah koreksi yang tidak destruktif"),
        ("O017-CONCEPT-UNCERTAINTY-LEDGER", "buku catatan keputusan dan ketidakpastian"),
    )
    records.extend(
        record("concept", identifier, label_id=label, unit="O017-U04")
        for identifier, label in concepts
    )

    segments = (
        ("O017-U04-SEG-OUTCOMES", "o017-u04-outcomes"),
        ("O017-U04-SEG-BIBLIOGRAPHY-NOT-EVIDENCE", "o017-u04-bibliography-is-not-evidence"),
        ("O017-U04-SEG-ORIGINAL-BRIDGE", "o017-u04-original-bridge"),
        ("O017-U04-SEG-THREE-RECORDS", "o017-u04-three-records"),
        ("O017-U04-SEG-CITATION-ROLE", "o017-u04-citation-role"),
        ("O017-U04-SEG-EVIDENCE-PROVENANCE", "o017-u04-evidence-provenance"),
        ("O017-U04-SEG-COMPUTATION-PROVENANCE", "o017-u04-computation-provenance"),
        ("O017-U04-SEG-FOUR-SOURCE-LEVELS", "o017-u04-four-source-levels"),
        ("O017-U04-SEG-TWO-LAYER-NOTEBOOK", "o017-u04-two-layer-notebook"),
        ("O017-U04-SEG-OBJECT-LAYER", "o017-u04-object-layer"),
        ("O017-U04-SEG-EVENT-LAYER", "o017-u04-event-layer"),
        ("O017-U04-SEG-SEVEN-TABLES", "o017-u04-six-tables"),
        ("O017-U04-SEG-LEDGER-PROTOCOL", "o017-u04-ledger-protocol"),
        ("O017-U04-SEG-WORKED-CASE", "o017-u04-worked-case"),
        ("O017-U04-SEG-VERSION-PACKET", "o017-u04-version-packet"),
        ("O017-U04-SEG-SOURCE-LEDGER", "o017-u04-source-ledger"),
        ("O017-U04-SEG-NORMALIZED-CLAIMS", "o017-u04-normalized-claims"),
        ("O017-U04-SEG-V2-PROOF", "o017-u04-v2-proof"),
        ("O017-U04-SEG-CLAIM-LOCATOR-CHAIN", "o017-u04-claim-locator-chain"),
        ("O017-U04-SEG-DECISION-LEDGER", "o017-u04-decision-ledger"),
        ("O017-U04-SEG-CITATION-AFTER-AUDIT", "o017-u04-citation-after-audit"),
        ("O017-U04-SEG-COMPUTATION-IN-CASE", "o017-u04-computation-in-case"),
        ("O017-U04-SEG-CORRECTIONS-PRESERVE-HISTORY", "o017-u04-corrections-preserve-history"),
        ("O017-U04-SEG-GUIDED-PRACTICE", "o017-u04-guided-practice"),
        ("O017-U04-SEG-EXERCISES", "o017-u04-exercises"),
        ("O017-U04-SEG-GUIDANCE", "o017-u04-guidance"),
        ("O017-U04-SEG-COMPLETION", "o017-u04-completion-task"),
        ("O017-U04-SEG-RUBRIC", "o017-u04-completion-rubric"),
        ("O017-U04-SEG-BOUNDARY", "o017-u04-boundary"),
        ("O017-U04-SEG-PROVENANCE", "o017-u04-provenance"),
    )
    records.extend(
        record("segment", identifier, unit="O017-U04", html_fragment=fragment)
        for identifier, fragment in segments
    )

    for index in range(1, 7):
        records.extend(
            (
                record(
                    "exercise",
                    f"O017-U04-E{index:02d}",
                    unit="O017-U04",
                    ordinal=index,
                    html_fragment=f"o017-u04-e{index:02d}",
                ),
                record(
                    "solution",
                    f"O017-U04-H{index:02d}",
                    unit="O017-U04",
                    ordinal=index,
                    solution_kind="guidance",
                    html_fragment=f"o017-u04-h{index:02d}",
                ),
            )
        )
    return tuple(records)


UNIT4_RELATIONS = (
    RelationSpec("O017-U04-REL-001", "O017-EDITION-01", "contains", "O017-U04", "metadata"),
    RelationSpec("O017-U04-REL-002", "O017-U04", "authored-from", "O017-SOURCE-ORIGINAL", "metadata"),
    RelationSpec("O017-U04-REL-003", "O017-U04", "licensed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U04-REL-004", "O017-U04", "verified-by", "O017-U04-QA-01", "metadata"),
    RelationSpec("O017-U04-REL-005", "O017-U04", "has-artifact", "O017-U04-ARTIFACT-HTML", "metadata"),
    RelationSpec("O017-U04-REL-006", "O017-U04", "teaches", "O017-CONCEPT-CITATION-VS-PROVENANCE", "metadata"),
    RelationSpec("O017-U04-REL-007", "O017-U04", "teaches", "O017-CONCEPT-SOURCE-IDENTITY-LEVELS", "metadata"),
    RelationSpec("O017-U04-REL-008", "O017-U04", "teaches", "O017-CONCEPT-SOURCE-OBJECT-EVENT", "metadata"),
    RelationSpec("O017-U04-REL-009", "O017-U04", "teaches", "O017-CONCEPT-CLAIM-LOCATOR-CHAIN", "metadata"),
    RelationSpec("O017-U04-REL-010", "O017-U04", "teaches", "O017-CONCEPT-EVIDENCE-PROVENANCE", "metadata"),
    RelationSpec("O017-U04-REL-011", "O017-U04", "teaches", "O017-CONCEPT-COMPUTATION-PROVENANCE", "metadata"),
    RelationSpec("O017-U04-REL-012", "O017-U04", "teaches", "O017-CONCEPT-CORRECTION-HISTORY", "metadata"),
    RelationSpec("O017-U04-REL-013", "O017-U04", "teaches", "O017-CONCEPT-UNCERTAINTY-LEDGER", "metadata"),
    RelationSpec("O017-U04-REL-014", "O017-U04", "contains", "O017-U04-SEG-OUTCOMES", "metadata"),
    RelationSpec("O017-U04-REL-015", "O017-U04", "contains", "O017-U04-SEG-BIBLIOGRAPHY-NOT-EVIDENCE", "metadata"),
    RelationSpec("O017-U04-REL-016", "O017-U04", "contains", "O017-U04-SEG-ORIGINAL-BRIDGE", "metadata"),
    RelationSpec("O017-U04-REL-017", "O017-U04", "contains", "O017-U04-SEG-THREE-RECORDS", "metadata"),
    RelationSpec("O017-U04-REL-018", "O017-U04", "contains", "O017-U04-SEG-CITATION-ROLE", "metadata"),
    RelationSpec("O017-U04-REL-019", "O017-U04", "contains", "O017-U04-SEG-EVIDENCE-PROVENANCE", "metadata"),
    RelationSpec("O017-U04-REL-020", "O017-U04", "contains", "O017-U04-SEG-COMPUTATION-PROVENANCE", "metadata"),
    RelationSpec("O017-U04-REL-021", "O017-U04", "contains", "O017-U04-SEG-FOUR-SOURCE-LEVELS", "metadata"),
    RelationSpec("O017-U04-REL-022", "O017-U04", "contains", "O017-U04-SEG-TWO-LAYER-NOTEBOOK", "metadata"),
    RelationSpec("O017-U04-REL-023", "O017-U04", "contains", "O017-U04-SEG-OBJECT-LAYER", "metadata"),
    RelationSpec("O017-U04-REL-024", "O017-U04", "contains", "O017-U04-SEG-EVENT-LAYER", "metadata"),
    RelationSpec("O017-U04-REL-025", "O017-U04", "contains", "O017-U04-SEG-SEVEN-TABLES", "metadata"),
    RelationSpec("O017-U04-REL-026", "O017-U04", "contains", "O017-U04-SEG-LEDGER-PROTOCOL", "metadata"),
    RelationSpec("O017-U04-REL-027", "O017-U04", "contains", "O017-U04-SEG-WORKED-CASE", "metadata"),
    RelationSpec("O017-U04-REL-028", "O017-U04", "contains", "O017-U04-SEG-VERSION-PACKET", "metadata"),
    RelationSpec("O017-U04-REL-029", "O017-U04", "contains", "O017-U04-SEG-SOURCE-LEDGER", "metadata"),
    RelationSpec("O017-U04-REL-030", "O017-U04", "contains", "O017-U04-SEG-NORMALIZED-CLAIMS", "metadata"),
    RelationSpec("O017-U04-REL-031", "O017-U04", "contains", "O017-U04-SEG-V2-PROOF", "metadata"),
    RelationSpec("O017-U04-REL-032", "O017-U04", "contains", "O017-U04-SEG-CLAIM-LOCATOR-CHAIN", "metadata"),
    RelationSpec("O017-U04-REL-033", "O017-U04", "contains", "O017-U04-SEG-DECISION-LEDGER", "metadata"),
    RelationSpec("O017-U04-REL-034", "O017-U04", "contains", "O017-U04-SEG-CITATION-AFTER-AUDIT", "metadata"),
    RelationSpec("O017-U04-REL-035", "O017-U04", "contains", "O017-U04-SEG-COMPUTATION-IN-CASE", "metadata"),
    RelationSpec("O017-U04-REL-036", "O017-U04", "contains", "O017-U04-SEG-CORRECTIONS-PRESERVE-HISTORY", "metadata"),
    RelationSpec("O017-U04-REL-037", "O017-U04", "contains", "O017-U04-SEG-GUIDED-PRACTICE", "metadata"),
    RelationSpec("O017-U04-REL-038", "O017-U04", "contains", "O017-U04-SEG-EXERCISES", "metadata"),
    RelationSpec("O017-U04-REL-039", "O017-U04", "contains", "O017-U04-SEG-GUIDANCE", "metadata"),
    RelationSpec("O017-U04-REL-040", "O017-U04", "contains", "O017-U04-SEG-COMPLETION", "metadata"),
    RelationSpec("O017-U04-REL-041", "O017-U04", "contains", "O017-U04-SEG-RUBRIC", "metadata"),
    RelationSpec("O017-U04-REL-042", "O017-U04", "contains", "O017-U04-SEG-BOUNDARY", "metadata"),
    RelationSpec("O017-U04-REL-043", "O017-U04", "contains", "O017-U04-SEG-PROVENANCE", "metadata"),
    RelationSpec("O017-U04-REL-044", "O017-U04", "contains", "O017-U04-CLAIM-PACKET-V1", "metadata"),
    RelationSpec("O017-U04-REL-045", "O017-U04", "contains", "O017-U04-CORRECTION-PACKET", "metadata"),
    RelationSpec("O017-U04-REL-046", "O017-U04", "contains", "O017-U04-CLAIM-PACKET-V2", "metadata"),
    RelationSpec("O017-U04-REL-047", "O017-U04", "contains", "O017-U04-PROOF-PACKET-V2", "metadata"),
    RelationSpec("O017-U04-REL-048", "O017-U04", "contains", "O017-U04-COUNTEREXAMPLE-PACKET-V1", "metadata"),
    RelationSpec("O017-U04-REL-049", "O017-U04", "contains", "O017-U04-COMPLETION-CLAIM-V1", "metadata"),
    RelationSpec("O017-U04-REL-050", "O017-U04", "contains", "O017-U04-COMPLETION-CORRECTION", "metadata"),
    RelationSpec("O017-U04-REL-051", "O017-U04", "contains", "O017-U04-COMPLETION-CLAIM-V2", "metadata"),
    RelationSpec("O017-U04-REL-052", "O017-U04", "contains", "O017-U04-E01", "metadata"),
    RelationSpec("O017-U04-REL-053", "O017-U04", "contains", "O017-U04-H01", "metadata"),
    RelationSpec("O017-U04-REL-054", "O017-U04", "contains", "O017-U04-E02", "metadata"),
    RelationSpec("O017-U04-REL-055", "O017-U04", "contains", "O017-U04-H02", "metadata"),
    RelationSpec("O017-U04-REL-056", "O017-U04", "contains", "O017-U04-E03", "metadata"),
    RelationSpec("O017-U04-REL-057", "O017-U04", "contains", "O017-U04-H03", "metadata"),
    RelationSpec("O017-U04-REL-058", "O017-U04", "contains", "O017-U04-E04", "metadata"),
    RelationSpec("O017-U04-REL-059", "O017-U04", "contains", "O017-U04-H04", "metadata"),
    RelationSpec("O017-U04-REL-060", "O017-U04", "contains", "O017-U04-E05", "metadata"),
    RelationSpec("O017-U04-REL-061", "O017-U04", "contains", "O017-U04-H05", "metadata"),
    RelationSpec("O017-U04-REL-062", "O017-U04", "contains", "O017-U04-E06", "metadata"),
    RelationSpec("O017-U04-REL-063", "O017-U04", "contains", "O017-U04-H06", "metadata"),
    RelationSpec("O017-U04-REL-064", "O017-U04-CLAIM-PACKET-V2", "proved-by", "O017-U04-PROOF-PACKET-V2", "mathematical-proof"),
    RelationSpec("O017-U04-REL-065", "O017-U04-COUNTEREXAMPLE-PACKET-V1", "refutes", "O017-U04-CLAIM-PACKET-V1", "mathematical-counterexample"),
    RelationSpec("O017-U04-REL-066", "O017-U04-CORRECTION-PACKET", "corrects", "O017-U04-CLAIM-PACKET-V1", "source-evidence"),
    RelationSpec("O017-U04-REL-067", "O017-U04-CORRECTION-PACKET", "motivates", "O017-U04-CLAIM-PACKET-V2", "source-evidence"),
    RelationSpec("O017-U04-REL-068", "O017-U04-COMPLETION-CORRECTION", "corrects", "O017-U04-COMPLETION-CLAIM-V1", "exercise-evidence"),
    RelationSpec("O017-U04-REL-069", "O017-U04-COMPLETION-CORRECTION", "motivates", "O017-U04-COMPLETION-CLAIM-V2", "exercise-evidence"),
    RelationSpec("O017-U04-REL-070", "O017-U04-E01", "guided-by", "O017-U04-H01", "metadata"),
    RelationSpec("O017-U04-REL-071", "O017-U04-E02", "guided-by", "O017-U04-H02", "metadata"),
    RelationSpec("O017-U04-REL-072", "O017-U04-E03", "guided-by", "O017-U04-H03", "metadata"),
    RelationSpec("O017-U04-REL-073", "O017-U04-E04", "guided-by", "O017-U04-H04", "metadata"),
    RelationSpec("O017-U04-REL-074", "O017-U04-E05", "guided-by", "O017-U04-H05", "metadata"),
    RelationSpec("O017-U04-REL-075", "O017-U04-E06", "guided-by", "O017-U04-H06", "metadata"),
    RelationSpec("O017-U04-REL-076", "O017-CONCEPT-CITATION-VS-PROVENANCE", "developed-in", "O017-U04-SEG-THREE-RECORDS", "metadata"),
    RelationSpec("O017-U04-REL-077", "O017-CONCEPT-SOURCE-IDENTITY-LEVELS", "developed-in", "O017-U04-SEG-FOUR-SOURCE-LEVELS", "metadata"),
    RelationSpec("O017-U04-REL-078", "O017-CONCEPT-SOURCE-OBJECT-EVENT", "developed-in", "O017-U04-SEG-TWO-LAYER-NOTEBOOK", "metadata"),
    RelationSpec("O017-U04-REL-079", "O017-CONCEPT-CLAIM-LOCATOR-CHAIN", "developed-in", "O017-U04-SEG-CLAIM-LOCATOR-CHAIN", "metadata"),
    RelationSpec("O017-U04-REL-080", "O017-CONCEPT-EVIDENCE-PROVENANCE", "developed-in", "O017-U04-SEG-EVIDENCE-PROVENANCE", "metadata"),
    RelationSpec("O017-U04-REL-081", "O017-CONCEPT-COMPUTATION-PROVENANCE", "developed-in", "O017-U04-SEG-COMPUTATION-PROVENANCE", "metadata"),
    RelationSpec("O017-U04-REL-082", "O017-CONCEPT-CORRECTION-HISTORY", "developed-in", "O017-U04-SEG-CORRECTIONS-PRESERVE-HISTORY", "metadata"),
    RelationSpec("O017-U04-REL-083", "O017-CONCEPT-UNCERTAINTY-LEDGER", "developed-in", "O017-U04-SEG-DECISION-LEDGER", "metadata"),
    RelationSpec("O017-U04-REL-084", "O017-U04-QA-01", "verifies", "O017-U04-ARTIFACT-HTML", "metadata"),
    RelationSpec("O017-U04-REL-085", "O017-U04", "cites", "O017-CIT-TTW", "metadata"),
    RelationSpec("O017-U04-REL-086", "O017-U04", "cites", "O017-CIT-PYRSE", "metadata"),
    RelationSpec("O017-U04-REL-087", "O017-U04", "adapted-from", "O017-SOURCE-TTW-C98A", "metadata"),
    RelationSpec("O017-U04-REL-088", "O017-U04", "adapted-from", "O017-SOURCE-PYRSE-6221", "metadata"),
    RelationSpec("O017-U04-REL-089", "O017-U04-SEG-CITATION-ROLE", "adapted-from", "O017-SOURCE-TTW-C98A", "component-rights"),
    RelationSpec("O017-U04-REL-090", "O017-U04-SEG-COMPUTATION-PROVENANCE", "adapted-from", "O017-SOURCE-PYRSE-6221", "component-rights"),
)


UNIT4_SOURCE_ANCHORS = frozenset(
    {
        "o017-u04-outcomes",
        "o017-u04-bibliography-is-not-evidence",
        "o017-u04-original-bridge",
        "o017-u04-three-records",
        "o017-u04-citation-role",
        "o017-u04-evidence-provenance",
        "o017-u04-computation-provenance",
        "o017-u04-four-source-levels",
        "o017-u04-two-layer-notebook",
        "o017-u04-object-layer",
        "o017-u04-event-layer",
        "o017-u04-six-tables",
        "o017-u04-ledger-protocol",
        "o017-u04-worked-case",
        "o017-u04-version-packet",
        "o017-u04-packet-v1",
        "o017-u04-packet-correction",
        "thm-o017-u04-packet-v2",
        "o017-u04-source-ledger",
        "o017-u04-normalized-claims",
        "o017-u04-v1-counterexample",
        "o017-u04-v2-proof",
        "prf-o017-u04-v2",
        "o017-u04-claim-locator-chain",
        "o017-u04-decision-ledger",
        "o017-u04-citation-after-audit",
        "o017-u04-computation-in-case",
        "o017-u04-corrections-preserve-history",
        "o017-u04-guided-practice",
        "o017-u04-exercises",
        *{f"o017-u04-e{index:02d}" for index in range(1, 7)},
        "o017-u04-guidance",
        *{f"o017-u04-h{index:02d}" for index in range(1, 7)},
        "o017-u04-completion-task",
        "o017-u04-completion-v1",
        "o017-u04-completion-correction",
        "o017-u04-completion-v2",
        "o017-u04-completion-rubric",
        "o017-u04-boundary",
        "o017-u04-provenance",
    }
)


UNIT4 = UnitSpec(
    id="O017-U04",
    ordinal=4,
    title="Sitasi, Provenance, dan Buku Catatan Sumber",
    source_path=SOURCE / "units" / "04-sitasi-provenance-catatan-sumber.qmd",
    html_relative_path=Path("units/04-sitasi-provenance-catatan-sumber.html"),
    required_section_ids=UNIT4_SOURCE_ANCHORS,
    required_entity_fragments=UNIT4_SOURCE_ANCHORS,
    exercise_solution_pairs=tuple(
        (f"O017-U04-E{index:02d}", f"O017-U04-H{index:02d}")
        for index in range(1, 7)
    ),
    computations=(),
    records_factory=unit4_records,
    relations=UNIT4_RELATIONS,
    manifest_inputs=(),
    scope_notes=(
        "Unit 4 contains original O017 source packets, version records, counterexample, proof, exercises, and correction cases; its citation/version and per-result provenance concepts are limited, attributed adaptations from the frozen TTW and py-rse witnesses, with no donor prose, figures, code, or exercises copied.",
        "Citation, source identity, evidence provenance, and computation provenance remain separate records joined by explicit relations and locators.",
        "A correction adds a new version and preserves the old claim, evidence, and decision history rather than silently overwriting them.",
        "Unit 4 specifies provenance fields and research-use decisions; B80 retains programming, environment setup, numerical methods, and tool mechanics.",
        "Unit 4 admission is not full-course completion.",
    ),
    admission_filename="UNIT_04_ADMISSION.md",
    qa_filename="UNIT_04_QA.json",
    visual_qa_filename="UNIT_04_VISUAL_QA.json",
    visual_qa_script_filename="visual_qa_unit.cjs",
    expected_source_sha256="08062db275a9620512c8dc4f8abc2a6d0cc93db2d55229cf1542747d69f8cd4f",
    expected_id_type_sha256="6cc475fb13460ac6d8e9525f10b8ae31cedca0987b538e663c2bfc4ec657ba0b",
    expected_relation_map_sha256="caa0bfcf2b985b5db5a52b9f9d566140d36d841b80783c5594b0cd74b8e840da",
)


def unit5_records(hashes: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = [
        record(
            "unit",
            "O017-U05",
            ordinal=5,
            title="Menulis Eksposisi Matematika yang Dapat Diaudit",
            locale="id-ID",
        ),
        record(
            "definition",
            "O017-U05-D01",
            unit="O017-U05",
            html_fragment="def-o017-u05-prime",
            title="Keterbagian dan bilangan prima",
        ),
        record(
            "theorem",
            "O017-U05-LEMMA-PRIME-DIVISOR",
            unit="O017-U05",
            html_fragment="lem-o017-u05-prime-divisor",
            title="Setiap bilangan bulat lebih dari satu mempunyai pembagi prima",
            claim_status="proved",
        ),
        record(
            "proof",
            "O017-U05-PROOF-PRIME-DIVISOR",
            unit="O017-U05",
            html_fragment="prf-o017-u05-prime-divisor",
            proves="O017-U05-LEMMA-PRIME-DIVISOR",
            method="minimal-counterexample descent",
        ),
        record(
            "theorem",
            "O017-U05-THEOREM-INFINITE-PRIMES",
            unit="O017-U05",
            html_fragment="thm-o017-u05-infinitely-many-primes",
            title="Terdapat tak berhingga banyak bilangan prima",
            claim_status="proved",
        ),
        record(
            "proof",
            "O017-U05-PROOF-INFINITE-PRIMES",
            unit="O017-U05",
            html_fragment="prf-o017-u05-infinitely-many-primes",
            proves="O017-U05-THEOREM-INFINITE-PRIMES",
            method="Euclid number and prime-divisor lemma",
        ),
        record(
            "example",
            "O017-U05-EXAMPLE-EUCLID",
            unit="O017-U05",
            html_fragment="o017-u05-example-01",
            title="Bilangan Euclid dari tiga prima",
        ),
        record(
            "counterexample",
            "O017-U05-COUNTEREXAMPLE-EUCLID-PRIME",
            unit="O017-U05",
            html_fragment="o017-u05-counterexample-01",
            witness="30031 = 59 × 509",
            refutes="the product of listed primes plus one is always prime",
        ),
        record(
            "example",
            "O017-U05-FLAWED-DRAFT",
            unit="O017-U05",
            html_fragment="o017-u05-flawed-draft",
            example_kind="draft-for-dependency-audit",
        ),
        record(
            "definition",
            "O017-U05-PKT-DEF01",
            unit="O017-U05",
            html_fragment="o017-u05-pkt-def01",
            title="Paket polinom: definisi kerja",
        ),
        record(
            "theorem",
            "O017-U05-PKT-LEM01",
            unit="O017-U05",
            html_fragment="o017-u05-pkt-lem01",
            claim_status="completion-input",
        ),
        record(
            "theorem",
            "O017-U05-PKT-LEM02",
            unit="O017-U05",
            html_fragment="o017-u05-pkt-lem02",
            claim_status="completion-input",
        ),
        record(
            "theorem",
            "O017-U05-PKT-LEM03",
            unit="O017-U05",
            html_fragment="o017-u05-pkt-lem03",
            claim_status="completion-input",
        ),
        record(
            "example",
            "O017-U05-PKT-EXM01",
            unit="O017-U05",
            html_fragment="o017-u05-pkt-exm01",
            example_kind="completion-input",
        ),
        record(
            "counterexample",
            "O017-U05-PKT-CTR01",
            unit="O017-U05",
            html_fragment="o017-u05-pkt-ctr01",
            example_kind="completion-input",
        ),
        record(
            "counterexample",
            "O017-U05-PKT-CTR02",
            unit="O017-U05",
            html_fragment="o017-u05-pkt-ctr02",
            example_kind="completion-input",
        ),
        record(
            "qa_event",
            "O017-U05-QA-01",
            status="pass",
            checks=[
                "source-hash-lock",
                "html-structure",
                "offline-mathml",
                "local-link-closure",
                "exercise-solution-correspondence",
                "definition-lemma-theorem-proof-closure",
                "example-counterexample-epistemic-status",
                "scope-and-notation-consistency",
                "rights-attribution",
                "backend-referential-integrity",
            ],
        ),
        record(
            "artifact",
            "O017-U05-ARTIFACT-HTML",
            path="build/html/units/05-eksposisi-matematika.html",
            sha256=hashes["html"],
            media_type="text/html",
        ),
    ]

    concepts = (
        ("O017-CONCEPT-READER-CONTRACT", "kontrak pembaca dan cakupan"),
        ("O017-CONCEPT-EXPOSITION-SCOPE-AUDIT", "audit cakupan eksposisi"),
        ("O017-CONCEPT-CLAIM-ARCHITECTURE", "arsitektur dan lokator klaim"),
        ("O017-CONCEPT-HONEST-CITATION", "sitasi sesuai pekerjaan klaim"),
        ("O017-CONCEPT-NOTATION-DISCIPLINE", "disiplin notasi"),
        ("O017-CONCEPT-LOCAL-SIGNPOSTING", "penanda arah lokal"),
        ("O017-CONCEPT-PARAGRAPH-LOAD", "satu beban utama per paragraf"),
        ("O017-CONCEPT-DEPENDENCY-REVISION", "revisi melalui audit ketergantungan"),
        ("O017-CONCEPT-SEMINAR-EXPOSITION", "arsitektur seminar yang dapat diaudit"),
    )
    records.extend(
        record("concept", identifier, label_id=label, unit="O017-U05")
        for identifier, label in concepts
    )

    segments = (
        ("O017-U05-SEG-OUTCOMES", "o017-u05-outcomes"),
        ("O017-U05-SEG-EXPOSITION-INTERFACE", "o017-u05-exposition-interface"),
        ("O017-U05-SEG-ORIGINAL-BRIDGE", "o017-u05-original-bridge"),
        ("O017-U05-SEG-READER-CONTRACT", "o017-u05-reader-contract"),
        ("O017-U05-SEG-SCOPE-TESTS", "o017-u05-scope-tests"),
        ("O017-U05-SEG-CLAIM-ARCHITECTURE", "o017-u05-claim-architecture"),
        ("O017-U05-SEG-HONEST-CITATION", "o017-u05-honest-citation"),
        ("O017-U05-SEG-NOTATION-DISCIPLINE", "o017-u05-notation-discipline"),
        ("O017-U05-SEG-WORKED-EXPOSITION", "o017-u05-worked-exposition"),
        ("O017-U05-SEG-PRIME-DIVISOR", "o017-u05-prime-divisor-section"),
        ("O017-U05-SEG-INFINITUDE", "o017-u05-infinitude-section"),
        ("O017-U05-SEG-EXAMPLE-EUCLID", "o017-u05-example-euclid-number"),
        ("O017-U05-SEG-COUNTEREXAMPLE-EUCLID", "o017-u05-counterexample-euclid-number"),
        ("O017-U05-SEG-WORKED-SCOPE-CLOSE", "o017-u05-worked-scope-close"),
        ("O017-U05-SEG-LOCAL-SIGNPOSTING", "o017-u05-local-signposting"),
        ("O017-U05-SEG-PARAGRAPH-LOAD", "o017-u05-paragraph-load"),
        ("O017-U05-SEG-DEPENDENCY-REVISION", "o017-u05-dependency-revision"),
        ("O017-U05-SEG-GUIDED-PRACTICE", "o017-u05-guided-practice"),
        ("O017-U05-SEG-GUIDED-MODEL", "o017-u05-guided-model"),
        ("O017-U05-SEG-GEOMETRIC-SUM", "eq-o017-u05-gs"),
        ("O017-U05-SEG-GUIDED-AUDIT", "o017-u05-guided-audit"),
        ("O017-U05-SEG-SEMINAR", "o017-u05-seminar-exposition"),
        ("O017-U05-SEG-PREFLIGHT", "o017-u05-preflight"),
        ("O017-U05-SEG-EXERCISES", "o017-u05-exercises"),
        ("O017-U05-SEG-GUIDANCE", "o017-u05-guidance"),
        ("O017-U05-SEG-COMPLETION", "o017-u05-completion-task"),
        ("O017-U05-SEG-COMPLETION-PACKET", "o017-u05-completion-packet"),
        ("O017-U05-SEG-RUBRIC", "o017-u05-completion-rubric"),
        ("O017-U05-SEG-BOUNDARY", "o017-u05-boundary"),
        ("O017-U05-SEG-PROVENANCE", "o017-u05-provenance"),
    )
    records.extend(
        record("segment", identifier, unit="O017-U05", html_fragment=fragment)
        for identifier, fragment in segments
    )

    for index in range(1, 7):
        records.extend(
            (
                record(
                    "exercise",
                    f"O017-U05-E{index:02d}",
                    unit="O017-U05",
                    ordinal=index,
                    html_fragment=f"o017-u05-e{index:02d}",
                ),
                record(
                    "solution",
                    f"O017-U05-H{index:02d}",
                    unit="O017-U05",
                    ordinal=index,
                    solution_kind="guidance",
                    html_fragment=f"o017-u05-h{index:02d}",
                ),
            )
        )
    return tuple(records)


UNIT5_RELATIONS = (
    RelationSpec("O017-U05-REL-001", "O017-EDITION-01", "contains", "O017-U05", "metadata"),
    RelationSpec("O017-U05-REL-002", "O017-U05", "authored-from", "O017-SOURCE-ORIGINAL", "metadata"),
    RelationSpec("O017-U05-REL-003", "O017-U05", "cites", "O017-CIT-TTW", "metadata"),
    RelationSpec("O017-U05-REL-004", "O017-U05", "adapted-from", "O017-SOURCE-TTW-C98A", "metadata"),
    RelationSpec("O017-U05-REL-005", "O017-U05", "licensed-by", "O017-RIGHTS-ORIGINAL-TEXT", "metadata"),
    RelationSpec("O017-U05-REL-006", "O017-U05", "verified-by", "O017-U05-QA-01", "metadata"),
    RelationSpec("O017-U05-REL-007", "O017-U05", "has-artifact", "O017-U05-ARTIFACT-HTML", "metadata"),
    RelationSpec("O017-U05-REL-008", "O017-U05", "teaches", "O017-CONCEPT-READER-CONTRACT", "metadata"),
    RelationSpec("O017-U05-REL-009", "O017-U05", "teaches", "O017-CONCEPT-EXPOSITION-SCOPE-AUDIT", "metadata"),
    RelationSpec("O017-U05-REL-010", "O017-U05", "teaches", "O017-CONCEPT-CLAIM-ARCHITECTURE", "metadata"),
    RelationSpec("O017-U05-REL-011", "O017-U05", "teaches", "O017-CONCEPT-HONEST-CITATION", "metadata"),
    RelationSpec("O017-U05-REL-012", "O017-U05", "teaches", "O017-CONCEPT-NOTATION-DISCIPLINE", "metadata"),
    RelationSpec("O017-U05-REL-013", "O017-U05", "teaches", "O017-CONCEPT-LOCAL-SIGNPOSTING", "metadata"),
    RelationSpec("O017-U05-REL-014", "O017-U05", "teaches", "O017-CONCEPT-PARAGRAPH-LOAD", "metadata"),
    RelationSpec("O017-U05-REL-015", "O017-U05", "teaches", "O017-CONCEPT-DEPENDENCY-REVISION", "metadata"),
    RelationSpec("O017-U05-REL-016", "O017-U05", "teaches", "O017-CONCEPT-SEMINAR-EXPOSITION", "metadata"),
    RelationSpec("O017-U05-REL-017", "O017-U05", "contains", "O017-U05-SEG-OUTCOMES", "metadata"),
    RelationSpec("O017-U05-REL-018", "O017-U05", "contains", "O017-U05-SEG-EXPOSITION-INTERFACE", "metadata"),
    RelationSpec("O017-U05-REL-019", "O017-U05", "contains", "O017-U05-SEG-ORIGINAL-BRIDGE", "metadata"),
    RelationSpec("O017-U05-REL-020", "O017-U05", "contains", "O017-U05-SEG-READER-CONTRACT", "metadata"),
    RelationSpec("O017-U05-REL-021", "O017-U05", "contains", "O017-U05-SEG-SCOPE-TESTS", "metadata"),
    RelationSpec("O017-U05-REL-022", "O017-U05", "contains", "O017-U05-SEG-CLAIM-ARCHITECTURE", "metadata"),
    RelationSpec("O017-U05-REL-023", "O017-U05", "contains", "O017-U05-SEG-HONEST-CITATION", "metadata"),
    RelationSpec("O017-U05-REL-024", "O017-U05", "contains", "O017-U05-SEG-NOTATION-DISCIPLINE", "metadata"),
    RelationSpec("O017-U05-REL-025", "O017-U05", "contains", "O017-U05-SEG-WORKED-EXPOSITION", "metadata"),
    RelationSpec("O017-U05-REL-026", "O017-U05", "contains", "O017-U05-SEG-PRIME-DIVISOR", "metadata"),
    RelationSpec("O017-U05-REL-027", "O017-U05", "contains", "O017-U05-SEG-INFINITUDE", "metadata"),
    RelationSpec("O017-U05-REL-028", "O017-U05", "contains", "O017-U05-SEG-EXAMPLE-EUCLID", "metadata"),
    RelationSpec("O017-U05-REL-029", "O017-U05", "contains", "O017-U05-SEG-COUNTEREXAMPLE-EUCLID", "metadata"),
    RelationSpec("O017-U05-REL-030", "O017-U05", "contains", "O017-U05-SEG-WORKED-SCOPE-CLOSE", "metadata"),
    RelationSpec("O017-U05-REL-031", "O017-U05", "contains", "O017-U05-SEG-LOCAL-SIGNPOSTING", "metadata"),
    RelationSpec("O017-U05-REL-032", "O017-U05", "contains", "O017-U05-SEG-PARAGRAPH-LOAD", "metadata"),
    RelationSpec("O017-U05-REL-033", "O017-U05", "contains", "O017-U05-SEG-DEPENDENCY-REVISION", "metadata"),
    RelationSpec("O017-U05-REL-034", "O017-U05", "contains", "O017-U05-SEG-GUIDED-PRACTICE", "metadata"),
    RelationSpec("O017-U05-REL-035", "O017-U05", "contains", "O017-U05-SEG-GUIDED-MODEL", "metadata"),
    RelationSpec("O017-U05-REL-036", "O017-U05", "contains", "O017-U05-SEG-GEOMETRIC-SUM", "metadata"),
    RelationSpec("O017-U05-REL-037", "O017-U05", "contains", "O017-U05-SEG-GUIDED-AUDIT", "metadata"),
    RelationSpec("O017-U05-REL-038", "O017-U05", "contains", "O017-U05-SEG-SEMINAR", "metadata"),
    RelationSpec("O017-U05-REL-039", "O017-U05", "contains", "O017-U05-SEG-PREFLIGHT", "metadata"),
    RelationSpec("O017-U05-REL-040", "O017-U05", "contains", "O017-U05-SEG-EXERCISES", "metadata"),
    RelationSpec("O017-U05-REL-041", "O017-U05", "contains", "O017-U05-SEG-GUIDANCE", "metadata"),
    RelationSpec("O017-U05-REL-042", "O017-U05", "contains", "O017-U05-SEG-COMPLETION", "metadata"),
    RelationSpec("O017-U05-REL-043", "O017-U05", "contains", "O017-U05-SEG-COMPLETION-PACKET", "metadata"),
    RelationSpec("O017-U05-REL-044", "O017-U05", "contains", "O017-U05-SEG-RUBRIC", "metadata"),
    RelationSpec("O017-U05-REL-045", "O017-U05", "contains", "O017-U05-SEG-BOUNDARY", "metadata"),
    RelationSpec("O017-U05-REL-046", "O017-U05", "contains", "O017-U05-SEG-PROVENANCE", "metadata"),
    RelationSpec("O017-U05-REL-047", "O017-U05", "contains", "O017-U05-D01", "metadata"),
    RelationSpec("O017-U05-REL-048", "O017-U05", "contains", "O017-U05-LEMMA-PRIME-DIVISOR", "metadata"),
    RelationSpec("O017-U05-REL-049", "O017-U05", "contains", "O017-U05-PROOF-PRIME-DIVISOR", "metadata"),
    RelationSpec("O017-U05-REL-050", "O017-U05", "contains", "O017-U05-THEOREM-INFINITE-PRIMES", "metadata"),
    RelationSpec("O017-U05-REL-051", "O017-U05", "contains", "O017-U05-PROOF-INFINITE-PRIMES", "metadata"),
    RelationSpec("O017-U05-REL-052", "O017-U05", "contains", "O017-U05-EXAMPLE-EUCLID", "metadata"),
    RelationSpec("O017-U05-REL-053", "O017-U05", "contains", "O017-U05-COUNTEREXAMPLE-EUCLID-PRIME", "metadata"),
    RelationSpec("O017-U05-REL-054", "O017-U05", "contains", "O017-U05-FLAWED-DRAFT", "metadata"),
    RelationSpec("O017-U05-REL-055", "O017-U05", "contains", "O017-U05-PKT-DEF01", "metadata"),
    RelationSpec("O017-U05-REL-056", "O017-U05", "contains", "O017-U05-PKT-LEM01", "metadata"),
    RelationSpec("O017-U05-REL-057", "O017-U05", "contains", "O017-U05-PKT-LEM02", "metadata"),
    RelationSpec("O017-U05-REL-058", "O017-U05", "contains", "O017-U05-PKT-LEM03", "metadata"),
    RelationSpec("O017-U05-REL-059", "O017-U05", "contains", "O017-U05-PKT-EXM01", "metadata"),
    RelationSpec("O017-U05-REL-060", "O017-U05", "contains", "O017-U05-PKT-CTR01", "metadata"),
    RelationSpec("O017-U05-REL-061", "O017-U05", "contains", "O017-U05-PKT-CTR02", "metadata"),
    RelationSpec("O017-U05-REL-062", "O017-U05", "contains", "O017-U05-E01", "metadata"),
    RelationSpec("O017-U05-REL-063", "O017-U05", "contains", "O017-U05-H01", "metadata"),
    RelationSpec("O017-U05-REL-064", "O017-U05", "contains", "O017-U05-E02", "metadata"),
    RelationSpec("O017-U05-REL-065", "O017-U05", "contains", "O017-U05-H02", "metadata"),
    RelationSpec("O017-U05-REL-066", "O017-U05", "contains", "O017-U05-E03", "metadata"),
    RelationSpec("O017-U05-REL-067", "O017-U05", "contains", "O017-U05-H03", "metadata"),
    RelationSpec("O017-U05-REL-068", "O017-U05", "contains", "O017-U05-E04", "metadata"),
    RelationSpec("O017-U05-REL-069", "O017-U05", "contains", "O017-U05-H04", "metadata"),
    RelationSpec("O017-U05-REL-070", "O017-U05", "contains", "O017-U05-E05", "metadata"),
    RelationSpec("O017-U05-REL-071", "O017-U05", "contains", "O017-U05-H05", "metadata"),
    RelationSpec("O017-U05-REL-072", "O017-U05", "contains", "O017-U05-E06", "metadata"),
    RelationSpec("O017-U05-REL-073", "O017-U05", "contains", "O017-U05-H06", "metadata"),
    RelationSpec("O017-U05-REL-074", "O017-U05-LEMMA-PRIME-DIVISOR", "proved-by", "O017-U05-PROOF-PRIME-DIVISOR", "mathematical-proof"),
    RelationSpec("O017-U05-REL-075", "O017-U05-THEOREM-INFINITE-PRIMES", "proved-by", "O017-U05-PROOF-INFINITE-PRIMES", "mathematical-proof"),
    RelationSpec("O017-U05-REL-076", "O017-U05-EXAMPLE-EUCLID", "illustrates", "O017-U05-THEOREM-INFINITE-PRIMES", "mathematical-example"),
    RelationSpec("O017-U05-REL-077", "O017-U05-COUNTEREXAMPLE-EUCLID-PRIME", "illustrates", "O017-CONCEPT-EXPOSITION-SCOPE-AUDIT", "mathematical-counterexample"),
    RelationSpec("O017-U05-REL-078", "O017-U05-FLAWED-DRAFT", "audited-by", "O017-U05-SEG-DEPENDENCY-REVISION", "editorial-evidence"),
    RelationSpec("O017-U05-REL-079", "O017-U05-SEG-COMPLETION-PACKET", "contains", "O017-U05-PKT-DEF01", "metadata"),
    RelationSpec("O017-U05-REL-080", "O017-U05-SEG-COMPLETION-PACKET", "contains", "O017-U05-PKT-LEM01", "metadata"),
    RelationSpec("O017-U05-REL-081", "O017-U05-SEG-COMPLETION-PACKET", "contains", "O017-U05-PKT-LEM02", "metadata"),
    RelationSpec("O017-U05-REL-082", "O017-U05-SEG-COMPLETION-PACKET", "contains", "O017-U05-PKT-LEM03", "metadata"),
    RelationSpec("O017-U05-REL-083", "O017-U05-SEG-COMPLETION-PACKET", "contains", "O017-U05-PKT-EXM01", "metadata"),
    RelationSpec("O017-U05-REL-084", "O017-U05-SEG-COMPLETION-PACKET", "contains", "O017-U05-PKT-CTR01", "metadata"),
    RelationSpec("O017-U05-REL-085", "O017-U05-SEG-COMPLETION-PACKET", "contains", "O017-U05-PKT-CTR02", "metadata"),
    RelationSpec("O017-U05-REL-086", "O017-U05-E01", "guided-by", "O017-U05-H01", "metadata"),
    RelationSpec("O017-U05-REL-087", "O017-U05-E02", "guided-by", "O017-U05-H02", "metadata"),
    RelationSpec("O017-U05-REL-088", "O017-U05-E03", "guided-by", "O017-U05-H03", "metadata"),
    RelationSpec("O017-U05-REL-089", "O017-U05-E04", "guided-by", "O017-U05-H04", "metadata"),
    RelationSpec("O017-U05-REL-090", "O017-U05-E05", "guided-by", "O017-U05-H05", "metadata"),
    RelationSpec("O017-U05-REL-091", "O017-U05-E06", "guided-by", "O017-U05-H06", "metadata"),
    RelationSpec("O017-U05-REL-092", "O017-CONCEPT-READER-CONTRACT", "developed-in", "O017-U05-SEG-READER-CONTRACT", "metadata"),
    RelationSpec("O017-U05-REL-093", "O017-CONCEPT-EXPOSITION-SCOPE-AUDIT", "developed-in", "O017-U05-SEG-SCOPE-TESTS", "metadata"),
    RelationSpec("O017-U05-REL-094", "O017-CONCEPT-CLAIM-ARCHITECTURE", "developed-in", "O017-U05-SEG-CLAIM-ARCHITECTURE", "metadata"),
    RelationSpec("O017-U05-REL-095", "O017-CONCEPT-HONEST-CITATION", "developed-in", "O017-U05-SEG-HONEST-CITATION", "metadata"),
    RelationSpec("O017-U05-REL-096", "O017-CONCEPT-NOTATION-DISCIPLINE", "developed-in", "O017-U05-SEG-NOTATION-DISCIPLINE", "metadata"),
    RelationSpec("O017-U05-REL-097", "O017-CONCEPT-LOCAL-SIGNPOSTING", "developed-in", "O017-U05-SEG-LOCAL-SIGNPOSTING", "metadata"),
    RelationSpec("O017-U05-REL-098", "O017-CONCEPT-PARAGRAPH-LOAD", "developed-in", "O017-U05-SEG-PARAGRAPH-LOAD", "metadata"),
    RelationSpec("O017-U05-REL-099", "O017-CONCEPT-DEPENDENCY-REVISION", "developed-in", "O017-U05-SEG-DEPENDENCY-REVISION", "metadata"),
    RelationSpec("O017-U05-REL-100", "O017-CONCEPT-SEMINAR-EXPOSITION", "developed-in", "O017-U05-SEG-SEMINAR", "metadata"),
    RelationSpec("O017-U05-REL-101", "O017-U05-QA-01", "verifies", "O017-U05-ARTIFACT-HTML", "metadata"),
    RelationSpec("O017-U05-REL-102", "O017-U05-SEG-HONEST-CITATION", "adapted-from", "O017-SOURCE-TTW-C98A", "component-rights"),
)


UNIT5_SOURCE_ANCHORS = frozenset(
    {
        "o017-u05-outcomes",
        "o017-u05-exposition-interface",
        "o017-u05-original-bridge",
        "o017-u05-reader-contract",
        "o017-u05-scope-tests",
        "o017-u05-claim-architecture",
        "o017-u05-honest-citation",
        "o017-u05-notation-discipline",
        "def-o017-u05-prime",
        "o017-u05-worked-exposition",
        "o017-u05-prime-divisor-section",
        "lem-o017-u05-prime-divisor",
        "prf-o017-u05-prime-divisor",
        "o017-u05-infinitude-section",
        "thm-o017-u05-infinitely-many-primes",
        "prf-o017-u05-infinitely-many-primes",
        "o017-u05-example-euclid-number",
        "o017-u05-example-01",
        "o017-u05-counterexample-euclid-number",
        "o017-u05-counterexample-01",
        "o017-u05-worked-scope-close",
        "o017-u05-local-signposting",
        "o017-u05-paragraph-load",
        "o017-u05-dependency-revision",
        "o017-u05-flawed-draft",
        "o017-u05-guided-practice",
        "o017-u05-guided-model",
        "eq-o017-u05-gs",
        "o017-u05-guided-audit",
        "o017-u05-seminar-exposition",
        "o017-u05-preflight",
        "o017-u05-exercises",
        *{f"o017-u05-e{index:02d}" for index in range(1, 7)},
        "o017-u05-guidance",
        *{f"o017-u05-h{index:02d}" for index in range(1, 7)},
        "o017-u05-completion-task",
        "o017-u05-completion-packet",
        "o017-u05-pkt-def01",
        "o017-u05-pkt-lem01",
        "o017-u05-pkt-lem02",
        "o017-u05-pkt-lem03",
        "o017-u05-pkt-exm01",
        "o017-u05-pkt-ctr01",
        "o017-u05-pkt-ctr02",
        "o017-u05-completion-rubric",
        "o017-u05-boundary",
        "o017-u05-provenance",
    }
)


UNIT5 = UnitSpec(
    id="O017-U05",
    ordinal=5,
    title="Menulis Eksposisi Matematika yang Dapat Diaudit",
    source_path=SOURCE / "units" / "05-eksposisi-matematika.qmd",
    html_relative_path=Path("units/05-eksposisi-matematika.html"),
    required_section_ids=UNIT5_SOURCE_ANCHORS,
    required_entity_fragments=UNIT5_SOURCE_ANCHORS,
    exercise_solution_pairs=tuple(
        (f"O017-U05-E{index:02d}", f"O017-U05-H{index:02d}")
        for index in range(1, 7)
    ),
    computations=(),
    records_factory=unit5_records,
    relations=UNIT5_RELATIONS,
    manifest_inputs=(),
    scope_notes=(
        "Unit 5 uses original O017 mathematical exposition, proofs, examples, counterexamples, exercises, and assessment material; only general citation/version-placement concepts are limited attributed adaptations from the frozen TTW witness.",
        "The reader contract, claim architecture, notation dictionary, local signposting, paragraph load, and dependency audit keep every mathematical assertion locatable and reviewable.",
        "Finite exact certificates are distinguished from empirical computation, while implementation and computational tooling remain B80 scope.",
        "Unit 5 does not repeat source search, proof reconstruction, source-ledger design, reproducible-computation packaging, erratum formulation, or review-response process.",
        "Unit 5 admission is not full-course completion.",
    ),
    admission_filename="UNIT_05_ADMISSION.md",
    qa_filename="UNIT_05_QA.json",
    visual_qa_filename="UNIT_05_VISUAL_QA.json",
    visual_qa_script_filename="visual_qa_unit.cjs",
    expected_source_sha256="ef5779b009bf1fe32b66af53ea64a89fd7eb51a240f7288bc4328c64d16a7006",
    expected_id_type_sha256="d0a9a78882a5d52def3300ff23f35ac38521eb33e5c1416f0d3d0e96f49a238b",
    expected_relation_map_sha256="a334d77011f53bce4d40fb9af47d3e519da0143cb4bf994bb39257777dbfa615",
)


UNIT6_SEGMENTS = (
    ("O017-U06-SEG-OUTCOMES", "o017-u06-outcomes"),
    ("O017-U06-SEG-ORIGINAL-BRIDGE", "o017-u06-original-bridge"),
    ("O017-U06-SEG-RERUN-NOT-PROOF", "o017-u06-rerun-is-not-proof"),
    ("O017-U06-SEG-FIVE-ROLES", "o017-u06-five-roles"),
    ("O017-U06-SEG-FREEZE-CLAIM", "o017-u06-freeze-claim"),
    ("O017-U06-SEG-PROTOCOL", "o017-u06-protocol"),
    ("O017-U06-SEG-PROTOCOL-CLAIM", "o017-u06-protocol-claim"),
    ("O017-U06-SEG-PROTOCOL-ARTIFACTS", "o017-u06-protocol-artifacts"),
    ("O017-U06-SEG-PROTOCOL-ENVIRONMENT", "o017-u06-protocol-environment"),
    ("O017-U06-SEG-PROTOCOL-INPUTS", "o017-u06-protocol-inputs"),
    ("O017-U06-SEG-PROTOCOL-RUN", "o017-u06-protocol-run"),
    ("O017-U06-SEG-PROTOCOL-VERIFY", "o017-u06-protocol-verify"),
    ("O017-U06-SEG-PROTOCOL-FALSIFY", "o017-u06-protocol-falsify"),
    ("O017-U06-SEG-WORKED-CASE", "o017-u06-worked-case"),
    ("O017-U06-SEG-WITNESS-CONTRACT", "o017-u06-witness-contract"),
    ("O017-U06-SEG-WITNESS-ARTIFACTS", "o017-u06-witness-artifacts"),
    ("O017-U06-SEG-WITNESS-OUTPUT", "o017-u06-witness-output"),
    ("O017-U06-SEG-OBSERVED-RUNS", "o017-u06-observed-runs"),
    ("O017-U06-SEG-IMPLEMENTATION-AUDIT", "o017-u06-implementation-audit"),
    ("O017-U06-SEG-UNIVERSAL-PROOF", "o017-u06-universal-proof"),
    ("O017-U06-SEG-WORKED-DECISIONS", "o017-u06-worked-decisions"),
    ("O017-U06-SEG-AUDIT-MATRIX", "o017-u06-audit-matrix"),
    ("O017-U06-SEG-NONDETERMINISM", "o017-u06-nondeterminism"),
    ("O017-U06-SEG-APPROXIMATE-CONTRACT", "o017-u06-approximate-contract"),
    ("O017-U06-SEG-SEED-BOUNDARY", "o017-u06-seed-boundary"),
    ("O017-U06-SEG-FAILURE-STATUS", "o017-u06-failure-status"),
    ("O017-U06-SEG-ACCESSIBILITY", "o017-u06-accessibility"),
    ("O017-U06-SEG-PREFLIGHT", "o017-u06-preflight"),
    ("O017-U06-SEG-EXERCISES", "o017-u06-exercises"),
    ("O017-U06-SEG-GUIDANCE", "o017-u06-guidance"),
    ("O017-U06-SEG-COMPLETION", "o017-u06-completion-task"),
    ("O017-U06-SEG-RUBRIC", "o017-u06-completion-rubric"),
    ("O017-U06-SEG-BOUNDARY", "o017-u06-boundary"),
    ("O017-U06-SEG-PROVENANCE", "o017-u06-provenance"),
)


UNIT6_CONCEPTS = (
    ("O017-CONCEPT-COMPUTATIONAL-CLAIM-LADDER", "tangga klaim komputasional"),
    ("O017-CONCEPT-COMPUTATIONAL-ROLES", "lima peran komputasi matematika"),
    ("O017-CONCEPT-FROZEN-CLAIM-CONTRACT", "kontrak klaim yang dibekukan"),
    ("O017-CONCEPT-REPRO-PACKAGE-PROTOCOL", "protokol paket reproduksibilitas"),
    ("O017-CONCEPT-ORACLE-INTEGRITY", "integritas oracle beku"),
    ("O017-CONCEPT-COMPUTATIONAL-FALSIFICATION", "falsifikasi komputasional"),
    ("O017-CONCEPT-FINITE-UNIVERSAL-BOUNDARY", "batas bukti berhingga dan universal"),
    ("O017-CONCEPT-NONDETERMINISM-CONTRACT", "kontrak ketidakdeterministikan"),
    ("O017-CONCEPT-ACCESSIBLE-MACHINE-EVIDENCE", "bukti mesin yang dapat diakses"),
)


def unit6_records(hashes: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = [
        record(
            "unit",
            "O017-U06",
            ordinal=6,
            title="Komputasi Matematika yang Dapat Direproduksi",
            locale="id-ID",
        ),
        record(
            "definition",
            "O017-U06-DEF-FIBONACCI",
            unit="O017-U06",
            html_fragment="def-o017-u06-fibonacci",
            title="Barisan Fibonacci",
        ),
        record(
            "theorem",
            "O017-U06-THM-CASSINI",
            unit="O017-U06",
            html_fragment="thm-o017-u06-cassini",
            title="Identitas Cassini",
            claim_status="proved",
        ),
        record(
            "proof",
            "O017-U06-PRF-CASSINI",
            unit="O017-U06",
            html_fragment="prf-o017-u06-cassini",
            proves="O017-U06-THM-CASSINI",
            method="induction using D[n+1] = -D[n]",
        ),
        record(
            "theorem",
            "O017-U06-C-FINITE-01",
            unit="O017-U06",
            html_fragment="o017-u06-witness-contract",
            title="Saksi berhingga identitas Cassini untuk n = 1..24",
            claim_status="verified-finite",
            scope="integers n with 1 <= n <= 24; exact arithmetic",
        ),
        record(
            "theorem",
            "O017-U06-C-FALSE-01",
            unit="O017-U06",
            html_fragment="o017-u06-counterexample-search",
            title="Klaim prima universal untuk n^2+n+41",
            claim_status="refuted",
        ),
        record(
            "counterexample",
            "O017-U06-COUNTEREXAMPLE-POLYNOMIAL-40",
            unit="O017-U06",
            html_fragment="o017-u06-counterexample-search",
            witness="n = 40; n^2+n+41 = 1681 = 41^2",
            refutes="O017-U06-C-FALSE-01",
        ),
        record(
            "asset",
            "O017-U06-CODE-01",
            path="source/code/u06_recurrence_witness.py",
            sha256=hashes["code"],
            media_type="text/x-python",
        ),
        record(
            "asset",
            "O017-U06-OUT-EXPECTED-01",
            path="source/code/u06-expected-output.txt",
            sha256=hashes["result"],
            media_type="application/json",
            encoding="UTF-8; canonical ASCII subset; trailing LF",
        ),
        record(
            "qa_event",
            "O017-U06-RUN-001",
            status="pass-byte",
            output_sha256=hashes["result"],
            exit_code=0,
            stderr_bytes=0,
        ),
        record(
            "qa_event",
            "O017-U06-RUN-002",
            status="pass-byte",
            output_sha256=hashes["result"],
            exit_code=0,
            stderr_bytes=0,
        ),
        record(
            "qa_event",
            "O017-U06-QA-01",
            status="pass",
            checks=[
                "source-hash-lock",
                "mathematical-computation",
                "oracle-byte-equality",
                "validator-negative-controls",
                "html-structure",
                "offline-mathml",
                "local-link-closure",
                "exercise-solution-correspondence",
                "rights-attribution",
                "backend-referential-integrity",
            ],
        ),
        record(
            "artifact",
            "O017-U06-ARTIFACT-HTML",
            path="build/html/units/06-komputasi-dapat-direproduksi.html",
            sha256=hashes["html"],
            media_type="text/html",
        ),
    ]
    records.extend(
        record("concept", identifier, label_id=label, unit="O017-U06")
        for identifier, label in UNIT6_CONCEPTS
    )
    records.extend(
        record("segment", identifier, unit="O017-U06", html_fragment=fragment)
        for identifier, fragment in UNIT6_SEGMENTS
    )
    for index in range(1, 7):
        records.extend(
            (
                record(
                    "exercise",
                    f"O017-U06-EX{index:02d}",
                    unit="O017-U06",
                    ordinal=index,
                    html_fragment=f"o017-u06-ex{index:02d}",
                ),
                record(
                    "solution",
                    f"O017-U06-H{index:02d}",
                    unit="O017-U06",
                    ordinal=index,
                    solution_kind="guidance",
                    html_fragment=f"o017-u06-h{index:02d}",
                ),
            )
        )
    return tuple(records)


def _u6_relation(
    number: int,
    source: str,
    predicate: str,
    target: str,
    evidence_kind: str = "metadata",
) -> RelationSpec:
    """Return one explicitly numbered, already-issued Unit 6 relation."""

    return RelationSpec(
        f"O017-U06-REL-{number:03d}",
        source,
        predicate,
        target,
        evidence_kind,
    )


UNIT6_RELATIONS = (
    _u6_relation(1, "O017-EDITION-01", "contains", "O017-U06"),
    _u6_relation(2, "O017-U06", "authored-from", "O017-SOURCE-ORIGINAL"),
    _u6_relation(3, "O017-U06", "cites", "O017-CIT-TTW"),
    _u6_relation(4, "O017-U06", "cites", "O017-CIT-PYRSE"),
    _u6_relation(5, "O017-U06", "adapted-from", "O017-SOURCE-TTW-C98A"),
    _u6_relation(6, "O017-U06", "adapted-from", "O017-SOURCE-PYRSE-6221"),
    _u6_relation(7, "O017-U06", "licensed-by", "O017-RIGHTS-ORIGINAL-TEXT"),
    _u6_relation(8, "O017-U06", "verified-by", "O017-U06-QA-01"),
    _u6_relation(9, "O017-U06", "has-artifact", "O017-U06-ARTIFACT-HTML"),
    _u6_relation(10, "O017-U06", "has-asset", "O017-U06-CODE-01"),
    _u6_relation(11, "O017-U06", "has-asset", "O017-U06-OUT-EXPECTED-01"),
    _u6_relation(12, "O017-U06-CODE-01", "licensed-by", "O017-RIGHTS-ORIGINAL-CODE", "component-rights"),
    _u6_relation(13, "O017-U06-OUT-EXPECTED-01", "generated-by", "O017-U06-CODE-01", "computational-evidence"),
    _u6_relation(14, "O017-U06-OUT-EXPECTED-01", "licensed-by", "O017-RIGHTS-GENERATED-DATA", "component-rights"),
    _u6_relation(15, "O017-U06-QA-01", "verifies", "O017-U06-ARTIFACT-HTML"),
    _u6_relation(16, "O017-U06-RUN-001", "executes", "O017-U06-CODE-01", "computational-evidence"),
    _u6_relation(17, "O017-U06-RUN-002", "executes", "O017-U06-CODE-01", "computational-evidence"),
    _u6_relation(18, "O017-U06-RUN-001", "matches", "O017-U06-OUT-EXPECTED-01", "computational-evidence"),
    _u6_relation(19, "O017-U06-RUN-002", "matches", "O017-U06-OUT-EXPECTED-01", "computational-evidence"),
    _u6_relation(20, "O017-U06-C-FINITE-01", "verified-by", "O017-U06-OUT-EXPECTED-01", "finite-computational-evidence"),
    _u6_relation(21, "O017-U06-THM-CASSINI", "proved-by", "O017-U06-PRF-CASSINI", "mathematical-proof"),
    _u6_relation(22, "O017-U06-COUNTEREXAMPLE-POLYNOMIAL-40", "refutes", "O017-U06-C-FALSE-01", "mathematical-counterexample"),
    _u6_relation(23, "O017-U06", "teaches", "O017-CONCEPT-COMPUTATIONAL-CLAIM-LADDER"),
    _u6_relation(24, "O017-U06", "teaches", "O017-CONCEPT-COMPUTATIONAL-ROLES"),
    _u6_relation(25, "O017-U06", "teaches", "O017-CONCEPT-FROZEN-CLAIM-CONTRACT"),
    _u6_relation(26, "O017-U06", "teaches", "O017-CONCEPT-REPRO-PACKAGE-PROTOCOL"),
    _u6_relation(27, "O017-U06", "teaches", "O017-CONCEPT-ORACLE-INTEGRITY"),
    _u6_relation(28, "O017-U06", "teaches", "O017-CONCEPT-COMPUTATIONAL-FALSIFICATION"),
    _u6_relation(29, "O017-U06", "teaches", "O017-CONCEPT-FINITE-UNIVERSAL-BOUNDARY"),
    _u6_relation(30, "O017-U06", "teaches", "O017-CONCEPT-NONDETERMINISM-CONTRACT"),
    _u6_relation(31, "O017-U06", "teaches", "O017-CONCEPT-ACCESSIBLE-MACHINE-EVIDENCE"),
    _u6_relation(32, "O017-CONCEPT-COMPUTATIONAL-CLAIM-LADDER", "developed-in", "O017-U06-SEG-RERUN-NOT-PROOF"),
    _u6_relation(33, "O017-CONCEPT-COMPUTATIONAL-ROLES", "developed-in", "O017-U06-SEG-FIVE-ROLES"),
    _u6_relation(34, "O017-CONCEPT-FROZEN-CLAIM-CONTRACT", "developed-in", "O017-U06-SEG-FREEZE-CLAIM"),
    _u6_relation(35, "O017-CONCEPT-REPRO-PACKAGE-PROTOCOL", "developed-in", "O017-U06-SEG-PROTOCOL"),
    _u6_relation(36, "O017-CONCEPT-ORACLE-INTEGRITY", "developed-in", "O017-U06-SEG-PROTOCOL-VERIFY"),
    _u6_relation(37, "O017-CONCEPT-COMPUTATIONAL-FALSIFICATION", "developed-in", "O017-U06-SEG-AUDIT-MATRIX"),
    _u6_relation(38, "O017-CONCEPT-FINITE-UNIVERSAL-BOUNDARY", "developed-in", "O017-U06-SEG-UNIVERSAL-PROOF"),
    _u6_relation(39, "O017-CONCEPT-NONDETERMINISM-CONTRACT", "developed-in", "O017-U06-SEG-NONDETERMINISM"),
    _u6_relation(40, "O017-CONCEPT-ACCESSIBLE-MACHINE-EVIDENCE", "developed-in", "O017-U06-SEG-ACCESSIBILITY"),
    *tuple(
        _u6_relation(41 + index, "O017-U06", "contains", identifier)
        for index, (identifier, _fragment) in enumerate(UNIT6_SEGMENTS)
    ),
    _u6_relation(75, "O017-U06", "contains", "O017-U06-DEF-FIBONACCI"),
    _u6_relation(76, "O017-U06", "contains", "O017-U06-THM-CASSINI"),
    _u6_relation(77, "O017-U06", "contains", "O017-U06-PRF-CASSINI"),
    _u6_relation(78, "O017-U06", "contains", "O017-U06-C-FINITE-01"),
    _u6_relation(79, "O017-U06", "contains", "O017-U06-C-FALSE-01"),
    _u6_relation(80, "O017-U06", "contains", "O017-U06-COUNTEREXAMPLE-POLYNOMIAL-40"),
    _u6_relation(81, "O017-U06", "contains", "O017-U06-CODE-01"),
    _u6_relation(82, "O017-U06", "contains", "O017-U06-OUT-EXPECTED-01"),
    _u6_relation(83, "O017-U06", "contains", "O017-U06-RUN-001"),
    _u6_relation(84, "O017-U06", "contains", "O017-U06-RUN-002"),
    *tuple(
        _u6_relation(83 + 2 * index, "O017-U06", "contains", f"O017-U06-EX{index:02d}")
        for index in range(1, 7)
    ),
    *tuple(
        _u6_relation(84 + 2 * index, "O017-U06", "contains", f"O017-U06-H{index:02d}")
        for index in range(1, 7)
    ),
    *tuple(
        _u6_relation(96 + index, f"O017-U06-EX{index:02d}", "guided-by", f"O017-U06-H{index:02d}")
        for index in range(1, 7)
    ),
    _u6_relation(103, "O017-U06-SEG-PROTOCOL", "adapted-from", "O017-SOURCE-TTW-C98A", "component-rights"),
    _u6_relation(104, "O017-U06-SEG-PROTOCOL-ARTIFACTS", "adapted-from", "O017-SOURCE-PYRSE-6221", "component-rights"),
)


UNIT6_SOURCE_ANCHORS = frozenset(
    {
        *(fragment for _identifier, fragment in UNIT6_SEGMENTS),
        "def-o017-u06-fibonacci",
        "thm-o017-u06-cassini",
        "prf-o017-u06-cassini",
        "o017-u06-counterexample-search",
        *{f"o017-u06-ex{index:02d}" for index in range(1, 7)},
        *{f"o017-u06-h{index:02d}" for index in range(1, 7)},
    }
)


UNIT6 = UnitSpec(
    id="O017-U06",
    ordinal=6,
    title="Komputasi Matematika yang Dapat Direproduksi",
    source_path=SOURCE / "units" / "06-komputasi-dapat-direproduksi.qmd",
    html_relative_path=Path("units/06-komputasi-dapat-direproduksi.html"),
    required_section_ids=UNIT6_SOURCE_ANCHORS,
    required_entity_fragments=UNIT6_SOURCE_ANCHORS,
    exercise_solution_pairs=tuple(
        (f"O017-U06-EX{index:02d}", f"O017-U06-H{index:02d}")
        for index in range(1, 7)
    ),
    computations=(
        ComputationSpec(
            code_path=SOURCE / "code" / "u06_recurrence_witness.py",
            expected_stdout_path=SOURCE / "code" / "u06-expected-output.txt",
            result_path=SOURCE / "code" / "u06-expected-output.txt",
            expected_result=EXPECTED_U06_RESULT,
            expected_code_sha256="9effb4dd4d17ce6b26fd108585ff0adc5110d8903c9c283b56a909613e7aa93d",
            expected_stdout_sha256="4c76da43510f9991b7197ddb0354a366136327b6d2ddfefb6516098eaa096112",
        ),
    ),
    records_factory=unit6_records,
    relations=UNIT6_RELATIONS,
    manifest_inputs=(SOURCE / "code" / "u06_recurrence_witness.py",),
    scope_notes=(
        "Unit 6 is an original O017 mathematics-specific bridge around limited attributed TTW and py-rse concepts; no donor sentence, code, exercise, or example is copied or directly translated.",
        "The executable witness establishes byte-repeatability and exact finite evidence for n = 1..24; the separate induction proof establishes the universal Cassini identity.",
        "B80 owns programming, environments, testing, version control, containers, and automation mechanics; Unit 6 owns the epistemic use and bounded interpretation of those tools in mathematical research.",
        "Unit 6 admission is not full-course completion.",
    ),
    admission_filename="UNIT_06_ADMISSION.md",
    qa_filename="UNIT_06_QA.json",
    visual_qa_filename="UNIT_06_VISUAL_QA.json",
    visual_qa_script_filename="visual_qa_unit.cjs",
    expected_source_sha256="64ba7458df5cb1b1c923c6a4f6a56a55003fb03b21f7903b3ac94a97b3a98122",
    expected_id_type_sha256="06a17d81da9a5fbdebb745515f5d115709e111eb3915ec1cd8d213c1ca84ddf1",
    expected_relation_map_sha256="375b0a8fd6578b6940702aa3181acf735af479dc8a2e1920991aaea9b04de5e5",
)


UNIT7_SEGMENTS = (
    ("O017-U07-SEG-OUTCOMES", "o017-u07-outcomes"),
    ("O017-U07-SEG-ERRATUM-BOUNDED-CLAIM", "o017-u07-erratum-as-bounded-claim"),
    ("O017-U07-SEG-ORIGINAL-BRIDGE", "o017-u07-original-bridge"),
    ("O017-U07-SEG-DEFECT-TAXONOMY", "o017-u07-defect-taxonomy"),
    ("O017-U07-SEG-STATUS-VERSUS-CAUSE", "o017-u07-status-versus-cause"),
    ("O017-U07-SEG-TYPO-WITH-IMPACT", "o017-u07-typo-with-impact"),
    ("O017-U07-SEG-EXPOSITION-DEFECT-LIMIT", "o017-u07-exposition-defect-limit"),
    ("O017-U07-SEG-SEVERITY-CONFIDENCE", "o017-u07-severity-and-confidence"),
    ("O017-U07-SEG-NO-PRODUCT-SCORE", "o017-u07-no-product-score"),
    ("O017-U07-SEG-ACTION-MATRIX", "o017-u07-action-matrix"),
    ("O017-U07-SEG-FREEZE-BEFORE-DIAGNOSIS", "o017-u07-freeze-before-diagnosis"),
    ("O017-U07-SEG-MINIMAL-REPRODUCER", "o017-u07-minimal-reproducer"),
    ("O017-U07-SEG-REPRODUCER-TESTS", "o017-u07-reproducer-tests"),
    ("O017-U07-SEG-WORKED-CASE", "o017-u07-worked-case"),
    ("O017-U07-SEG-WORKED-VERSION", "o017-u07-worked-version"),
    ("O017-U07-SEG-MISSING-CONNECTEDNESS", "o017-u07-missing-connectedness"),
    ("O017-U07-SEG-WORKED-TRIAGE", "o017-u07-worked-triage"),
    ("O017-U07-SEG-HISTORY-PRESERVING", "o017-u07-history-preserving-correction"),
    ("O017-U07-SEG-WORKED-EVENT-LEDGER", "o017-u07-worked-event-ledger"),
    ("O017-U07-SEG-CORRECTION-FIELDS", "o017-u07-correction-record-fields"),
    ("O017-U07-SEG-CONCISE-DRAFT", "o017-u07-concise-draft"),
    ("O017-U07-SEG-SIX-SENTENCE-TEMPLATE", "o017-u07-six-sentence-template"),
    ("O017-U07-SEG-ACCESSIBLE-REPORT", "o017-u07-accessible-report"),
    ("O017-U07-SEG-UNCERTAINTY-LEDGER", "o017-u07-uncertainty-ledger"),
    ("O017-U07-SEG-CERTAINTY-LANGUAGE", "o017-u07-certainty-language"),
    ("O017-U07-SEG-STOP-AND-ESCALATE", "o017-u07-stop-and-escalate"),
    ("O017-U07-SEG-STOP-BEFORE-CLAIM", "o017-u07-stop-before-claim"),
    ("O017-U07-SEG-ESCALATION-RULE", "o017-u07-escalation-rule"),
    ("O017-U07-SEG-CLOSURE-CONDITIONS", "o017-u07-closure-conditions"),
    ("O017-U07-SEG-CORRECTION-PROTOCOL", "o017-u07-correction-protocol"),
    ("O017-U07-SEG-GUIDED-PRACTICE", "o017-u07-guided-practice"),
    ("O017-U07-SEG-PREFLIGHT", "o017-u07-preflight"),
    ("O017-U07-SEG-EXERCISES", "o017-u07-exercises"),
    ("O017-U07-SEG-GUIDANCE", "o017-u07-guidance"),
    ("O017-U07-SEG-COMPLETION", "o017-u07-completion-task"),
    ("O017-U07-SEG-RUBRIC", "o017-u07-completion-rubric"),
    ("O017-U07-SEG-BOUNDARY", "o017-u07-boundary"),
    ("O017-U07-SEG-PROVENANCE", "o017-u07-provenance"),
)


UNIT7_ENTITY_FRAGMENTS = frozenset(
    {
        "o017-u07-packet-v1",
        "o017-u07-two-point-counterexample",
        "o017-u07-packet-v2",
        "o017-u07-connected-proof",
        "o017-u07-minimal-repair",
        "o017-u07-draft-only",
        "o017-u07-completion-metadata",
        "o017-u07-completion-statement",
        "o017-u07-completion-proof",
        "o017-u07-completion-typo",
        "o017-u07-completion-locator",
        "o017-u07-completion-computation",
    }
)


UNIT7_CONCEPTS = (
    ("O017-CONCEPT-DEFECT-TAXONOMY", "taksonomi cacat dua lapis"),
    ("O017-CONCEPT-STATUS-CAUSE-SEPARATION", "pemisahan status dan penyebab"),
    ("O017-CONCEPT-SEVERITY-CONFIDENCE-SEPARATION", "pemisahan keparahan dan keyakinan"),
    ("O017-CONCEPT-FROZEN-ERRATUM-TARGET", "target erratum yang dibekukan"),
    ("O017-CONCEPT-MINIMAL-ERRATUM-REPRODUCER", "reproducer erratum minimal"),
    ("O017-CONCEPT-HISTORY-PRESERVING-CORRECTION", "koreksi yang mempertahankan sejarah"),
    ("O017-CONCEPT-CONCISE-ERRATUM-DRAFT", "draf erratum ringkas"),
    ("O017-CONCEPT-ERRATUM-UNCERTAINTY-LEDGER", "buku besar ketidakpastian errata"),
    ("O017-CONCEPT-ERRATUM-STOP-ESCALATION", "gerbang berhenti dan eskalasi errata"),
    ("O017-CONCEPT-MISSING-HYPOTHESIS", "diagnosis hipotesis yang hilang"),
)


def unit7_records(hashes: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = [
        record(
            "unit",
            "O017-U07",
            ordinal=7,
            title="Errata, Koreksi, dan Batas Kepastian",
            locale="id-ID",
        ),
        record("resource", "O017-U07-W01", unit="O017-U07", title="Paket Topologi Sintetis", role="synthetic worked source"),
        record("edition", "O017-U07-V01", unit="O017-U07", html_fragment="o017-u07-packet-v1", status="historical-refuted", version="1.0-sintetis"),
        record("source", "O017-U07-CP01", unit="O017-U07", html_fragment="o017-u07-packet-v1", role="complete embedded synthetic copy"),
        record(
            "theorem",
            "O017-U07-C01",
            unit="O017-U07",
            html_fragment="o017-u07-packet-v1",
            title="Klaim tanda tetap tanpa keterhubungan",
            claim_status="false-as-written",
        ),
        record(
            "counterexample",
            "O017-U07-CE01",
            unit="O017-U07",
            html_fragment="o017-u07-two-point-counterexample",
            witness="X={-1,1} with subspace topology and f(x)=x",
            refutes="O017-U07-C01",
        ),
        record(
            "correction",
            "O017-U07-F01",
            unit="O017-U07",
            html_fragment="o017-u07-missing-connectedness",
            target_claim="O017-U07-C01",
            statement_status="false_as_written",
            defect_kind="missing_hypothesis",
            severity="S2",
            confidence="C3",
        ),
        record("edition", "O017-U07-V02", unit="O017-U07", html_fragment="o017-u07-packet-v2", status="candidate-correction", version="1.1-calon"),
        record(
            "theorem",
            "O017-U07-C02",
            unit="O017-U07",
            html_fragment="o017-u07-packet-v2",
            title="Klaim tanda tetap pada domain terhubung",
            claim_status="proved",
        ),
        record("proof", "O017-U07-PRF-C02", unit="O017-U07", html_fragment="o017-u07-connected-proof", proves="O017-U07-C02"),
        record(
            "theorem",
            "O017-U07-THM-CONNECTED-IFF-SIGN",
            unit="O017-U07",
            html_fragment="o017-u07-minimal-repair",
            title="Karakterisasi keterhubungan melalui fungsi kontinu yang tidak pernah nol",
            claim_status="proved",
        ),
        record("proof", "O017-U07-PRF-CONNECTED-IFF-SIGN", unit="O017-U07", html_fragment="o017-u07-minimal-repair", proves="O017-U07-THM-CONNECTED-IFF-SIGN"),
        record(
            "artifact",
            "O017-U07-DRAFT-LOCAL-01",
            unit="O017-U07",
            html_fragment="o017-u07-draft-only",
            status="draft-local-not-sent",
            media_type="text/plain-in-html",
        ),
        *tuple(
            record("qa_event", f"O017-U07-EVT{index:02d}", unit="O017-U07", status=status)
            for index, status in enumerate(
                ("observed", "refuted", "classified", "proposed", "proved", "bounded"),
                start=1,
            )
        ),
        record("resource", "O017-U07-PKT-W01", unit="O017-U07", html_fragment="o017-u07-completion-metadata", title="Catatan Ekstrem pada Interval", role="synthetic completion source"),
        record("edition", "O017-U07-PKT-V1", unit="O017-U07", html_fragment="o017-u07-completion-metadata", version="1.2-sintetis"),
        record("source", "O017-U07-PKT-CP1", unit="O017-U07", html_fragment="o017-u07-completion-metadata", role="complete embedded five-excerpt copy"),
        record("theorem", "O017-U07-PKT-S01", unit="O017-U07", html_fragment="o017-u07-completion-statement", claim_status="completion-input"),
        record("proof", "O017-U07-PKT-P01", unit="O017-U07", html_fragment="o017-u07-completion-proof", method="completion-input flawed proof"),
        record("example", "O017-U07-PKT-T01", unit="O017-U07", html_fragment="o017-u07-completion-typo", example_kind="completion-input typo"),
        record("example", "O017-U07-PKT-L01", unit="O017-U07", html_fragment="o017-u07-completion-locator", example_kind="completion-input ambiguous locator"),
        record("example", "O017-U07-PKT-C01", unit="O017-U07", html_fragment="o017-u07-completion-computation", example_kind="completion-input computation record"),
        record(
            "qa_event",
            "O017-U07-QA-01",
            status="pass",
            checks=[
                "source-hash-lock",
                "mathematical-counterexample",
                "corrected-proof",
                "history-preserving-correction",
                "html-structure",
                "offline-mathml",
                "local-link-closure",
                "exercise-solution-correspondence",
                "rights-attribution",
                "backend-referential-integrity",
            ],
        ),
        record(
            "artifact",
            "O017-U07-ARTIFACT-HTML",
            path="build/html/units/07-errata-koreksi-batas-kepastian.html",
            sha256=hashes["html"],
            media_type="text/html",
        ),
    ]
    records.extend(
        record("concept", identifier, label_id=label, unit="O017-U07")
        for identifier, label in UNIT7_CONCEPTS
    )
    records.extend(
        record("segment", identifier, unit="O017-U07", html_fragment=fragment)
        for identifier, fragment in UNIT7_SEGMENTS
    )
    for index in range(1, 7):
        records.extend(
            (
                record("exercise", f"O017-U07-X{index:02d}", unit="O017-U07", ordinal=index, html_fragment=f"o017-u07-x{index:02d}"),
                record("solution", f"O017-U07-H{index:02d}", unit="O017-U07", ordinal=index, solution_kind="guidance", html_fragment=f"o017-u07-h{index:02d}"),
            )
        )
    return tuple(records)


def _u7_relation(
    number: int,
    source: str,
    predicate: str,
    target: str,
    evidence_kind: str = "metadata",
) -> RelationSpec:
    """Return one explicitly numbered, already-issued Unit 7 relation."""

    return RelationSpec(f"O017-U07-REL-{number:03d}", source, predicate, target, evidence_kind)


UNIT7_RELATIONS = (
    _u7_relation(1, "O017-EDITION-01", "contains", "O017-U07"),
    _u7_relation(2, "O017-U07", "authored-from", "O017-SOURCE-ORIGINAL"),
    _u7_relation(3, "O017-U07", "licensed-by", "O017-RIGHTS-ORIGINAL-TEXT"),
    _u7_relation(4, "O017-U07", "verified-by", "O017-U07-QA-01"),
    _u7_relation(5, "O017-U07", "has-artifact", "O017-U07-ARTIFACT-HTML"),
    _u7_relation(6, "O017-U07-QA-01", "verifies", "O017-U07-ARTIFACT-HTML"),
    _u7_relation(7, "O017-U07", "contains", "O017-U07-W01"),
    _u7_relation(8, "O017-U07-W01", "has-edition", "O017-U07-V01"),
    _u7_relation(9, "O017-U07-W01", "has-edition", "O017-U07-V02"),
    _u7_relation(10, "O017-U07-V01", "has-copy", "O017-U07-CP01"),
    _u7_relation(11, "O017-U07-V01", "contains", "O017-U07-C01"),
    _u7_relation(12, "O017-U07-CE01", "refutes", "O017-U07-C01", "mathematical-counterexample"),
    _u7_relation(13, "O017-U07-F01", "corrects", "O017-U07-C01", "correction-evidence"),
    _u7_relation(14, "O017-U07-F01", "proposes", "O017-U07-C02", "correction-evidence"),
    _u7_relation(15, "O017-U07-V02", "contains", "O017-U07-C02"),
    _u7_relation(16, "O017-U07-C02", "proved-by", "O017-U07-PRF-C02", "mathematical-proof"),
    _u7_relation(17, "O017-U07-THM-CONNECTED-IFF-SIGN", "proved-by", "O017-U07-PRF-CONNECTED-IFF-SIGN", "mathematical-proof"),
    _u7_relation(18, "O017-U07-CE01", "illustrates", "O017-U07-THM-CONNECTED-IFF-SIGN", "mathematical-counterexample"),
    _u7_relation(19, "O017-U07-F01", "diagnosed-as", "O017-CONCEPT-MISSING-HYPOTHESIS", "correction-evidence"),
    _u7_relation(20, "O017-U07", "contains", "O017-U07-V01"),
    _u7_relation(21, "O017-U07", "contains", "O017-U07-CP01"),
    _u7_relation(22, "O017-U07", "contains", "O017-U07-C01"),
    _u7_relation(23, "O017-U07", "contains", "O017-U07-CE01"),
    _u7_relation(24, "O017-U07", "contains", "O017-U07-F01"),
    _u7_relation(25, "O017-U07", "contains", "O017-U07-V02"),
    _u7_relation(26, "O017-U07", "contains", "O017-U07-C02"),
    _u7_relation(27, "O017-U07", "contains", "O017-U07-PRF-C02"),
    _u7_relation(28, "O017-U07", "contains", "O017-U07-THM-CONNECTED-IFF-SIGN"),
    _u7_relation(29, "O017-U07", "contains", "O017-U07-PRF-CONNECTED-IFF-SIGN"),
    _u7_relation(30, "O017-U07", "contains", "O017-U07-DRAFT-LOCAL-01"),
    _u7_relation(31, "O017-U07-DRAFT-LOCAL-01", "licensed-by", "O017-RIGHTS-ORIGINAL-TEXT", "component-rights"),
    *tuple(_u7_relation(31 + index, "O017-U07", "contains", f"O017-U07-EVT{index:02d}") for index in range(1, 7)),
    _u7_relation(38, "O017-U07-EVT01", "observes", "O017-U07-CP01", "source-evidence"),
    _u7_relation(39, "O017-U07-EVT02", "refutes", "O017-U07-C01", "mathematical-counterexample"),
    _u7_relation(40, "O017-U07-EVT03", "classifies", "O017-U07-F01", "correction-evidence"),
    _u7_relation(41, "O017-U07-EVT04", "proposes", "O017-U07-C02", "correction-evidence"),
    _u7_relation(42, "O017-U07-EVT05", "verifies", "O017-U07-C02", "mathematical-proof"),
    _u7_relation(43, "O017-U07-EVT06", "bounds", "O017-U07-F01", "correction-evidence"),
    _u7_relation(44, "O017-U07", "contains", "O017-U07-PKT-W01"),
    _u7_relation(45, "O017-U07", "contains", "O017-U07-PKT-V1"),
    _u7_relation(46, "O017-U07", "contains", "O017-U07-PKT-CP1"),
    _u7_relation(47, "O017-U07", "contains", "O017-U07-PKT-S01"),
    _u7_relation(48, "O017-U07", "contains", "O017-U07-PKT-P01"),
    _u7_relation(49, "O017-U07", "contains", "O017-U07-PKT-T01"),
    _u7_relation(50, "O017-U07", "contains", "O017-U07-PKT-L01"),
    _u7_relation(51, "O017-U07", "contains", "O017-U07-PKT-C01"),
    _u7_relation(52, "O017-U07-PKT-W01", "has-edition", "O017-U07-PKT-V1"),
    _u7_relation(53, "O017-U07-PKT-V1", "has-copy", "O017-U07-PKT-CP1"),
    _u7_relation(54, "O017-U07-PKT-CP1", "contains", "O017-U07-PKT-S01"),
    _u7_relation(55, "O017-U07-PKT-CP1", "contains", "O017-U07-PKT-P01"),
    _u7_relation(56, "O017-U07-PKT-CP1", "contains", "O017-U07-PKT-T01"),
    _u7_relation(57, "O017-U07-PKT-CP1", "contains", "O017-U07-PKT-L01"),
    _u7_relation(58, "O017-U07-PKT-CP1", "contains", "O017-U07-PKT-C01"),
    _u7_relation(59, "O017-U07", "contains", "O017-U07-QA-01"),
    _u7_relation(60, "O017-U07", "contains", "O017-U07-ARTIFACT-HTML"),
    _u7_relation(61, "O017-U07-F01", "preserves", "O017-U07-V01", "correction-evidence"),
    _u7_relation(62, "O017-U07-C02", "replaces", "O017-U07-C01", "correction-evidence"),
    *tuple(_u7_relation(63 + index, "O017-U07", "teaches", identifier) for index, (identifier, _label) in enumerate(UNIT7_CONCEPTS)),
    _u7_relation(73, "O017-CONCEPT-DEFECT-TAXONOMY", "developed-in", "O017-U07-SEG-DEFECT-TAXONOMY"),
    _u7_relation(74, "O017-CONCEPT-STATUS-CAUSE-SEPARATION", "developed-in", "O017-U07-SEG-STATUS-VERSUS-CAUSE"),
    _u7_relation(75, "O017-CONCEPT-SEVERITY-CONFIDENCE-SEPARATION", "developed-in", "O017-U07-SEG-SEVERITY-CONFIDENCE"),
    _u7_relation(76, "O017-CONCEPT-FROZEN-ERRATUM-TARGET", "developed-in", "O017-U07-SEG-FREEZE-BEFORE-DIAGNOSIS"),
    _u7_relation(77, "O017-CONCEPT-MINIMAL-ERRATUM-REPRODUCER", "developed-in", "O017-U07-SEG-MINIMAL-REPRODUCER"),
    _u7_relation(78, "O017-CONCEPT-HISTORY-PRESERVING-CORRECTION", "developed-in", "O017-U07-SEG-HISTORY-PRESERVING"),
    _u7_relation(79, "O017-CONCEPT-CONCISE-ERRATUM-DRAFT", "developed-in", "O017-U07-SEG-CONCISE-DRAFT"),
    _u7_relation(80, "O017-CONCEPT-ERRATUM-UNCERTAINTY-LEDGER", "developed-in", "O017-U07-SEG-UNCERTAINTY-LEDGER"),
    _u7_relation(81, "O017-CONCEPT-ERRATUM-STOP-ESCALATION", "developed-in", "O017-U07-SEG-STOP-AND-ESCALATE"),
    _u7_relation(82, "O017-CONCEPT-MISSING-HYPOTHESIS", "developed-in", "O017-U07-SEG-MISSING-CONNECTEDNESS"),
    *tuple(_u7_relation(83 + index, "O017-U07", "contains", identifier) for index, (identifier, _fragment) in enumerate(UNIT7_SEGMENTS)),
    *tuple(_u7_relation(119 + 2 * index, "O017-U07", "contains", f"O017-U07-X{index:02d}") for index in range(1, 7)),
    *tuple(_u7_relation(120 + 2 * index, "O017-U07", "contains", f"O017-U07-H{index:02d}") for index in range(1, 7)),
    *tuple(_u7_relation(132 + index, f"O017-U07-X{index:02d}", "guided-by", f"O017-U07-H{index:02d}") for index in range(1, 7)),
)


UNIT7_SOURCE_ANCHORS = frozenset(
    {
        *(fragment for _identifier, fragment in UNIT7_SEGMENTS),
        *UNIT7_ENTITY_FRAGMENTS,
        *{f"o017-u07-x{index:02d}" for index in range(1, 7)},
        *{f"o017-u07-h{index:02d}" for index in range(1, 7)},
    }
)


UNIT7 = UnitSpec(
    id="O017-U07",
    ordinal=7,
    title="Errata, Koreksi, dan Batas Kepastian",
    source_path=SOURCE / "units" / "07-errata-koreksi-batas-kepastian.qmd",
    html_relative_path=Path("units/07-errata-koreksi-batas-kepastian.html"),
    required_section_ids=UNIT7_SOURCE_ANCHORS,
    required_entity_fragments=UNIT7_SOURCE_ANCHORS,
    exercise_solution_pairs=tuple((f"O017-U07-X{index:02d}", f"O017-U07-H{index:02d}") for index in range(1, 7)),
    computations=(),
    records_factory=unit7_records,
    relations=UNIT7_RELATIONS,
    manifest_inputs=(),
    scope_notes=(
        "Unit 7 is wholly original O017 material and uses only synthetic local source packets; no external donor is adapted.",
        "The two-point counterexample refutes the historical claim, while the connected-domain theorem and the iff characterization are proved separately and preserve the old version in the correction ledger.",
        "All issue and erratum text remains a local draft; no upstream contact, submission, acknowledgment, or publication is claimed.",
        "B80 owns implementation and debugging mechanics; Unit 7 owns bounded mathematical diagnosis, correction, uncertainty, and escalation decisions.",
        "Unit 7 admission is not full-course completion.",
    ),
    admission_filename="UNIT_07_ADMISSION.md",
    qa_filename="UNIT_07_QA.json",
    visual_qa_filename="UNIT_07_VISUAL_QA.json",
    visual_qa_script_filename="visual_qa_unit.cjs",
    expected_source_sha256="5ba8f9051a059ab1f9b83588e9fd66a0e5c548bc0265a0592226782f3c32622f",
    expected_id_type_sha256="2f7cc7f9ce52f27bc5ce8bfb62d84aea25004a4f987417c3c563f97d93c51c11",
    expected_relation_map_sha256="64e5d5510d9db6e9889b59924ee7814b5ca801e8f28d8a5f549a12274ceb31c6",
)


UNIT8_SEGMENTS = (
    ("O017-U08-SEG-OUTCOMES", "o017-u08-outcomes"),
    ("O017-U08-SEG-REVIEW-EVIDENCE", "o017-u08-review-as-evidence-contract"),
    ("O017-U08-SEG-ORIGINAL-BRIDGE", "o017-u08-original-bridge"),
    ("O017-U08-SEG-RECORDING-CONTRACT", "o017-u08-recording-contract"),
    ("O017-U08-SEG-ENTRY-KINDS", "o017-u08-four-entry-types"),
    ("O017-U08-SEG-SEVERITY-CONFIDENCE-STATUS", "o017-u08-severity-confidence-status"),
    ("O017-U08-SEG-SEMINAR-NOTE-TEMPLATE", "o017-u08-seminar-note-template"),
    ("O017-U08-SEG-MISSING-SEGMENT", "o017-u08-missing-segment-rule"),
    ("O017-U08-SEG-SEMINAR-CASE", "o017-u08-seminar-case"),
    ("O017-U08-SEG-NOTES-TO-REVIEW", "o017-u08-from-notes-to-review"),
    ("O017-U08-SEG-RESPECTFUL-SPECIFICITY", "o017-u08-respectful-specificity"),
    ("O017-U08-SEG-WORKED-MANUSCRIPT", "o017-u08-worked-manuscript"),
    ("O017-U08-SEG-WORKED-REVIEW", "o017-u08-worked-review-comment"),
    ("O017-U08-SEG-RELATED-COMMENTS", "o017-u08-worked-related-comments"),
    ("O017-U08-SEG-AUTHOR-RESPONSE", "o017-u08-author-response"),
    ("O017-U08-SEG-WORKED-AUTHOR-RESPONSE", "o017-u08-worked-author-response"),
    ("O017-U08-SEG-MINIMAL-REVISION", "o017-u08-minimally-revised-result"),
    ("O017-U08-SEG-REFEREE-REPORT", "o017-u08-writing-referee-report"),
    ("O017-U08-SEG-REPORT-SCOPE", "o017-u08-report-scope"),
    ("O017-U08-SEG-REPORT-SUMMARY", "o017-u08-report-summary"),
    ("O017-U08-SEG-REPORT-ASSESSMENT", "o017-u08-report-assessment"),
    ("O017-U08-SEG-MAJOR-MINOR", "o017-u08-major-minor-comments"),
    ("O017-U08-SEG-REPORT-RECOMMENDATION", "o017-u08-report-recommendation"),
    ("O017-U08-SEG-REPORT-TEMPLATE", "o017-u08-referee-report-template"),
    ("O017-U08-SEG-RECOMMENDATION-GATES", "o017-u08-recommendation-gates"),
    ("O017-U08-SEG-WITHHOLD", "o017-u08-withhold-recommendation"),
    ("O017-U08-SEG-DISAGREEMENT", "o017-u08-disagreement"),
    ("O017-U08-SEG-DEFENSIVE-PATTERNS", "o017-u08-defensive-patterns"),
    ("O017-U08-SEG-END-TO-END", "o017-u08-end-to-end-protocol"),
    ("O017-U08-SEG-PREFLIGHT", "o017-u08-preflight"),
    ("O017-U08-SEG-EXERCISES", "o017-u08-exercises"),
    ("O017-U08-SEG-GUIDANCE", "o017-u08-guidance"),
    ("O017-U08-SEG-COMPLETION", "o017-u08-completion-task"),
    ("O017-U08-SEG-RUBRIC", "o017-u08-completion-rubric"),
    ("O017-U08-SEG-BOUNDARY", "o017-u08-boundary"),
    ("O017-U08-SEG-PROVENANCE", "o017-u08-provenance"),
)


UNIT8_CONCEPTS = (
    ("O017-U08-CPT-NOTE-CONTRACT", "kontrak catatan seminar"),
    ("O017-U08-CPT-ENTRY-KIND", "jenis entri ringkasan verifikasi pertanyaan keberatan"),
    ("O017-U08-CPT-MISSING-SEGMENT", "aturan segmen rekaman yang hilang"),
    ("O017-U08-CPT-STATUS-SEVERITY-CONFIDENCE", "pemisahan status keparahan dan keyakinan"),
    ("O017-U08-CPT-EVIDENCE-BOUNDED-REVIEW", "penelaahan berbatas bukti"),
    ("O017-U08-CPT-RESPECTFUL-CRITIQUE", "kritik matematis yang hormat dan spesifik"),
    ("O017-U08-CPT-NONDEFENSIVE-RESPONSE", "tanggapan penulis yang tidak defensif"),
    ("O017-U08-CPT-RESPONSE-MATRIX", "matriks komentar tindakan bukti lokasi status"),
    ("O017-U08-CPT-MINIMAL-REVISION", "revisi matematis minimal"),
    ("O017-U08-CPT-RECOMMENDATION-GATE", "gerbang rekomendasi penelaah"),
    ("O017-U08-CPT-UNRESOLVED-ITEM", "register masalah belum selesai"),
    ("O017-U08-CPT-REVIEW-PROTOCOL", "protokol seminar laporan tanggapan"),
)


UNIT8_CORE_RECORD_IDS = (
    "O017-U08-TALK-01",
    "O017-U08-TALK-C01",
    "O017-U08-TALK-NOTES-01",
    *(f"O017-U08-N{index:02d}" for index in range(1, 7)),
    "O017-U08-MS-W01",
    "O017-U08-MS-V1",
    "O017-U08-MS-V1-THM1",
    "O017-U08-MS-V1-THM1-EXISTENCE",
    "O017-U08-MS-V1-THM1-UNIQUENESS",
    "O017-U08-MS-V1-PRF1",
    "O017-U08-MS-V1-P1",
    "O017-U08-MS-V1-P2",
    "O017-U08-MS-V1-P3",
    "O017-U08-DEF-UNSUPPORTED-INCREMENT",
    "O017-U08-CE-IDENTITY-MAP",
    "O017-U08-MS-V1-COR2",
    *(f"O017-U08-R1-C{index:02d}" for index in range(1, 5)),
    "O017-U08-RESP-R1-C01",
    "O017-U08-MS-V2",
    "O017-U08-MS-V2-THM1",
    "O017-U08-MS-V2-PRF1",
    "O017-U08-UNRESOLVED-REGISTER",
    "O017-U08-RESPONSE-MATRIX",
    "O017-U08-PKT-META",
    "O017-U08-PKT-W01",
    "O017-U08-PKT-V1",
    "O017-U08-PKT-C01",
    "O017-U08-PKT-P01",
    "O017-U08-STATE-NO-CONTACT",
    "O017-U08-REC-ACCEPT",
    "O017-U08-REC-MINOR",
    "O017-U08-REC-MAJOR",
    "O017-U08-REC-REJECT",
    "O017-U08-REC-WITHHOLD",
    "O017-U08-QA-01",
    "O017-U08-ARTIFACT-HTML",
)


def unit8_records(hashes: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = [
        record(
            "unit",
            "O017-U08",
            ordinal=8,
            title="Catatan Seminar, Laporan Penelaah, dan Tanggapan terhadap Kritik",
            locale="id-ID",
        ),
        record("resource", "O017-U08-TALK-01", unit="O017-U08", html_fragment="o017-u08-talk-metadata", title="Titik Tetap pada Interval", role="synthetic seminar packet", synthetic=True),
        record("theorem", "O017-U08-TALK-C01", unit="O017-U08", html_fragment="o017-u08-talk-claim-v1", claim_status="false-as-written"),
        record("artifact", "O017-U08-TALK-NOTES-01", unit="O017-U08", html_fragment="o017-u08-seminar-case-notes", status="bounded-local-notes"),
        *tuple(record("qa_event", f"O017-U08-N{index:02d}", unit="O017-U08", html_fragment="o017-u08-seminar-case-notes", event_kind="seminar-note-entry", local_alias=f"N{index:02d}") for index in range(1, 7)),
        record("resource", "O017-U08-MS-W01", unit="O017-U08", html_fragment="o017-u08-manuscript-v1", title="Naskah Titik Tetap", role="synthetic manuscript", synthetic=True),
        record("edition", "O017-U08-MS-V1", unit="O017-U08", html_fragment="o017-u08-manuscript-v1", version="1.0-sintetis", status="reviewed-defective"),
        record("theorem", "O017-U08-MS-V1-THM1", unit="O017-U08", html_fragment="o017-u08-ms-v1-theorem", claim_status="partly-false"),
        record("theorem", "O017-U08-MS-V1-THM1-EXISTENCE", unit="O017-U08", html_fragment="o017-u08-ms-v1-theorem", claim_status="proved"),
        record("theorem", "O017-U08-MS-V1-THM1-UNIQUENESS", unit="O017-U08", html_fragment="o017-u08-ms-v1-theorem", claim_status="false-as-written"),
        record("proof", "O017-U08-MS-V1-PRF1", unit="O017-U08", html_fragment="o017-u08-ms-v1-proof", proof_status="defective-proof-attempt"),
        *tuple(record("proof", f"O017-U08-MS-V1-P{index}", unit="O017-U08", html_fragment="o017-u08-ms-v1-proof", proof_kind="proof-step", local_alias=f"P{index}") for index in range(1, 4)),
        record("correction", "O017-U08-DEF-UNSUPPORTED-INCREMENT", unit="O017-U08", html_fragment="o017-u08-ms-v1-proof", correction_kind="proof-defect", status="diagnosed"),
        record("counterexample", "O017-U08-CE-IDENTITY-MAP", unit="O017-U08", html_fragment="o017-u08-review-c01", witness="f(x)=x on [0,1]", refutes="O017-U08-MS-V1-THM1-UNIQUENESS"),
        record("theorem", "O017-U08-MS-V1-COR2", unit="O017-U08", html_fragment="o017-u08-manuscript-v1", claim_status="unavailable-and-withheld"),
        *tuple(record("correction", f"O017-U08-R1-C{index:02d}", unit="O017-U08", html_fragment=f"o017-u08-review-c{index:02d}", correction_kind="review-comment", status="issued-locally", local_alias=f"R1-C{index:02d}") for index in range(1, 5)),
        record("artifact", "O017-U08-RESP-R1-C01", unit="O017-U08", html_fragment="o017-u08-response-r1-c01", status="synthetic-local-author-response"),
        record("edition", "O017-U08-MS-V2", unit="O017-U08", html_fragment="o017-u08-minimally-revised-result", version="candidate-v2", status="candidate-local-revision"),
        record("theorem", "O017-U08-MS-V2-THM1", unit="O017-U08", html_fragment="o017-u08-ms-v2-theorem", claim_status="proved"),
        record("proof", "O017-U08-MS-V2-PRF1", unit="O017-U08", html_fragment="o017-u08-ms-v2-proof", proof_status="valid"),
        record("qa_event", "O017-U08-UNRESOLVED-REGISTER", unit="O017-U08", html_fragment="o017-u08-worked-unresolved-items", status="open-items-preserved"),
        record("artifact", "O017-U08-RESPONSE-MATRIX", unit="O017-U08", html_fragment="o017-u08-response-matrix", status="local-review-closure-matrix"),
        record("artifact", "O017-U08-PKT-META", unit="O017-U08", html_fragment="o017-u08-completion-metadata", status="synthetic-completion-metadata"),
        record("resource", "O017-U08-PKT-W01", unit="O017-U08", html_fragment="o017-u08-completion-metadata", title="Limit Fungsi Kontinu", role="synthetic completion work", synthetic=True),
        record("edition", "O017-U08-PKT-V1", unit="O017-U08", html_fragment="o017-u08-completion-metadata", version="1.0-sintetis", status="completion-input"),
        record("theorem", "O017-U08-PKT-C01", unit="O017-U08", html_fragment="o017-u08-completion-claim", claim_status="false-as-written"),
        record("proof", "O017-U08-PKT-P01", unit="O017-U08", html_fragment="o017-u08-completion-proof", proof_status="defective-proof-attempt"),
        record("qa_event", "O017-U08-STATE-NO-CONTACT", unit="O017-U08", html_fragment="o017-u08-boundary", status="no-real-external-contact"),
        record("qa_event", "O017-U08-REC-ACCEPT", unit="O017-U08", html_fragment="o017-u08-recommendation-gates", status="recommendation-state-definition", value="accept"),
        record("qa_event", "O017-U08-REC-MINOR", unit="O017-U08", html_fragment="o017-u08-recommendation-gates", status="recommendation-state-definition", value="minor-revision"),
        record("qa_event", "O017-U08-REC-MAJOR", unit="O017-U08", html_fragment="o017-u08-recommendation-gates", status="recommendation-state-definition", value="major-revision"),
        record("qa_event", "O017-U08-REC-REJECT", unit="O017-U08", html_fragment="o017-u08-recommendation-gates", status="recommendation-state-definition", value="reject"),
        record("qa_event", "O017-U08-REC-WITHHOLD", unit="O017-U08", html_fragment="o017-u08-withhold-recommendation", status="recommendation-state-definition", value="withhold"),
        record(
            "qa_event",
            "O017-U08-QA-01",
            status="pass",
            checks=[
                "source-hash-lock",
                "fixed-point-counterexample",
                "minimal-theorem-revision",
                "missing-segment-epistemics",
                "review-response-closure",
                "html-structure",
                "offline-mathml",
                "local-link-closure",
                "exercise-solution-correspondence",
                "rights-attribution",
                "backend-referential-integrity",
            ],
        ),
        record("artifact", "O017-U08-ARTIFACT-HTML", path="build/html/units/08-seminar-penelaah-tanggapan-kritik.html", sha256=hashes["html"], media_type="text/html"),
    ]
    records.extend(record("concept", identifier, label_id=label, unit="O017-U08") for identifier, label in UNIT8_CONCEPTS)
    records.extend(record("segment", identifier, unit="O017-U08", html_fragment=fragment) for identifier, fragment in UNIT8_SEGMENTS)
    for index in range(1, 7):
        records.extend(
            (
                record("exercise", f"O017-U08-E{index:02d}", unit="O017-U08", ordinal=index, html_fragment=f"o017-u08-e{index:02d}"),
                record("solution", f"O017-U08-H{index:02d}", unit="O017-U08", ordinal=index, solution_kind="guidance", html_fragment=f"o017-u08-h{index:02d}"),
            )
        )
    return tuple(records)


def _u8_relation(number: int, source: str, predicate: str, target: str, evidence_kind: str = "metadata") -> RelationSpec:
    """Return one explicitly numbered, already-issued Unit 8 relation."""

    return RelationSpec(f"O017-U08-REL-{number:03d}", source, predicate, target, evidence_kind)


UNIT8_RELATIONS = (
    _u8_relation(1, "O017-EDITION-01", "contains", "O017-U08"),
    _u8_relation(2, "O017-U08", "authored-from", "O017-SOURCE-ORIGINAL"),
    _u8_relation(3, "O017-U08", "licensed-by", "O017-RIGHTS-ORIGINAL-TEXT", "component-rights"),
    _u8_relation(4, "O017-U08", "verified-by", "O017-U08-QA-01"),
    _u8_relation(5, "O017-U08", "has-artifact", "O017-U08-ARTIFACT-HTML"),
    _u8_relation(6, "O017-U08-QA-01", "verifies", "O017-U08-ARTIFACT-HTML"),
    _u8_relation(7, "O017-U08", "external-contact-state", "O017-U08-STATE-NO-CONTACT"),
    _u8_relation(8, "O017-U08", "provenance-stated-at", "O017-U08-SEG-PROVENANCE"),
    _u8_relation(9, "O017-U08-STATE-NO-CONTACT", "documents-no-external-contact-for", "O017-U08"),
    *tuple(_u8_relation(10 + index, "O017-U08", "contains", identifier) for index, identifier in enumerate(UNIT8_CORE_RECORD_IDS)),
    *tuple(_u8_relation(54 + index, "O017-U08", "teaches", identifier) for index, (identifier, _label) in enumerate(UNIT8_CONCEPTS)),
    *tuple(_u8_relation(66 + index, identifier, "developed-in", UNIT8_SEGMENTS[(0, 4, 7, 5, 1, 10, 14, 15, 16, 24, 11, 28)[index]][0]) for index, (identifier, _label) in enumerate(UNIT8_CONCEPTS)),
    *tuple(_u8_relation(78 + index, "O017-U08", "contains", identifier) for index, (identifier, _fragment) in enumerate(UNIT8_SEGMENTS)),
    *tuple(_u8_relation(112 + 2 * index, "O017-U08", "contains", f"O017-U08-E{index:02d}") for index in range(1, 7)),
    *tuple(_u8_relation(113 + 2 * index, "O017-U08", "contains", f"O017-U08-H{index:02d}") for index in range(1, 7)),
    *tuple(_u8_relation(125 + index, f"O017-U08-E{index:02d}", "guided-by", f"O017-U08-H{index:02d}") for index in range(1, 7)),
    _u8_relation(132, "O017-U08-TALK-01", "contains-claim", "O017-U08-TALK-C01"),
    *tuple(_u8_relation(132 + index, "O017-U08-TALK-01", "has-note", f"O017-U08-N{index:02d}") for index in range(1, 7)),
    _u8_relation(139, "O017-U08-N05", "documents", "O017-U08-CE-IDENTITY-MAP", "mathematical-counterexample"),
    _u8_relation(140, "O017-U08-MS-W01", "has-version", "O017-U08-MS-V1"),
    _u8_relation(141, "O017-U08-MS-W01", "has-candidate-version", "O017-U08-MS-V2"),
    _u8_relation(142, "O017-U08-MS-V1", "contains", "O017-U08-MS-V1-THM1"),
    _u8_relation(143, "O017-U08-MS-V1", "contains", "O017-U08-MS-V1-PRF1"),
    _u8_relation(144, "O017-U08-MS-V1", "contains", "O017-U08-MS-V1-COR2"),
    _u8_relation(145, "O017-U08-MS-V1-THM1", "comprises", "O017-U08-MS-V1-THM1-EXISTENCE"),
    _u8_relation(146, "O017-U08-MS-V1-THM1", "comprises", "O017-U08-MS-V1-THM1-UNIQUENESS"),
    _u8_relation(147, "O017-U08-MS-V1-THM1", "has-proof-attempt", "O017-U08-MS-V1-PRF1"),
    *tuple(_u8_relation(147 + index, "O017-U08-MS-V1-PRF1", "contains-step", f"O017-U08-MS-V1-P{index}") for index in range(1, 4)),
    _u8_relation(151, "O017-U08-MS-V1-P1", "supports", "O017-U08-MS-V1-THM1-EXISTENCE", "mathematical-proof"),
    _u8_relation(152, "O017-U08-MS-V1-P2", "supports", "O017-U08-MS-V1-THM1-EXISTENCE", "mathematical-proof"),
    _u8_relation(153, "O017-U08-MS-V1-P3", "contains-defect", "O017-U08-DEF-UNSUPPORTED-INCREMENT", "mathematical-diagnosis"),
    _u8_relation(154, "O017-U08-CE-IDENTITY-MAP", "refutes", "O017-U08-MS-V1-THM1-UNIQUENESS", "mathematical-counterexample"),
    _u8_relation(155, "O017-U08-DEF-UNSUPPORTED-INCREMENT", "diagnosed-by", "O017-U08-R1-C01", "review-evidence"),
    _u8_relation(156, "O017-U08-R1-C01", "requests-revision-of", "O017-U08-MS-V1-THM1-UNIQUENESS", "review-evidence"),
    _u8_relation(157, "O017-U08-R1-C02", "requests-preservation-of", "O017-U08-MS-V1-THM1-EXISTENCE", "review-evidence"),
    _u8_relation(158, "O017-U08-R1-C03", "suggests-optional-condition-for", "O017-U08-MS-V2-THM1", "review-evidence"),
    _u8_relation(159, "O017-U08-R1-C04", "requests-audit-of", "O017-U08-MS-V1-COR2", "review-evidence"),
    _u8_relation(160, "O017-U08-RESP-R1-C01", "responds-to", "O017-U08-R1-C01", "review-response"),
    *tuple(_u8_relation(160 + index, "O017-U08-RESPONSE-MATRIX", "tracks", f"O017-U08-R1-C{index:02d}", "review-response") for index in range(1, 5)),
    _u8_relation(165, "O017-U08-MS-V2-THM1", "revises", "O017-U08-MS-V1-THM1", "mathematical-correction"),
    _u8_relation(166, "O017-U08-MS-V2-THM1", "preserves-supported-part-of", "O017-U08-MS-V1-THM1-EXISTENCE", "mathematical-correction"),
    _u8_relation(167, "O017-U08-MS-V2-PRF1", "proves", "O017-U08-MS-V2-THM1", "mathematical-proof"),
    _u8_relation(168, "O017-U08-UNRESOLVED-REGISTER", "constrains-closure-of", "O017-U08-MS-V2", "review-evidence"),
    _u8_relation(169, "O017-U08-MS-V1", "has-recommendation", "O017-U08-REC-MAJOR", "review-evidence"),
    *tuple(_u8_relation(170 + index, "O017-U08-SEG-RECOMMENDATION-GATES", "defines", identifier) for index, identifier in enumerate(("O017-U08-REC-ACCEPT", "O017-U08-REC-MINOR", "O017-U08-REC-MAJOR", "O017-U08-REC-REJECT"))),
    _u8_relation(174, "O017-U08-SEG-WITHHOLD", "defines", "O017-U08-REC-WITHHOLD"),
    _u8_relation(175, "O017-U08-STATE-NO-CONTACT", "documents-no-external-contact-for", "O017-U08-RESP-R1-C01"),
    _u8_relation(176, "O017-U08-TALK-01", "synthetic-component-of", "O017-U08"),
    _u8_relation(177, "O017-U08-MS-W01", "synthetic-component-of", "O017-U08"),
    _u8_relation(178, "O017-U08-PKT-W01", "synthetic-component-of", "O017-U08"),
    _u8_relation(179, "O017-U08-PKT-W01", "has-version", "O017-U08-PKT-V1"),
    _u8_relation(180, "O017-U08-PKT-V1", "described-by", "O017-U08-PKT-META"),
    _u8_relation(181, "O017-U08-PKT-V1", "contains-claim", "O017-U08-PKT-C01"),
    _u8_relation(182, "O017-U08-PKT-C01", "has-proof-attempt", "O017-U08-PKT-P01"),
    _u8_relation(183, "O017-U08", "part-of", "O017-D120"),
    _u8_relation(184, "O017-U08", "bounded-from", "B80"),
    _u8_relation(185, "O017-U08-RESPONSE-MATRIX", "closure-record-for", "O017-U08-MS-V2"),
    _u8_relation(186, "O017-U08-MS-V2", "contains", "O017-U08-MS-V2-THM1"),
    _u8_relation(187, "O017-U08-MS-V2", "contains", "O017-U08-MS-V2-PRF1"),
    *tuple(_u8_relation(187 + index, "O017-U08-TALK-NOTES-01", "contains", f"O017-U08-N{index:02d}") for index in range(1, 7)),
    _u8_relation(194, "O017-U08-TALK-01", "has-notes", "O017-U08-TALK-NOTES-01"),
)


UNIT8_SOURCE_ANCHORS = frozenset(
    {
        *(fragment for _identifier, fragment in UNIT8_SEGMENTS),
        "o017-u08-talk-metadata",
        "o017-u08-talk-claim-v1",
        "o017-u08-seminar-case-notes",
        "o017-u08-manuscript-v1",
        "o017-u08-ms-v1-theorem",
        "o017-u08-ms-v1-proof",
        *(f"o017-u08-review-c{index:02d}" for index in range(1, 5)),
        "o017-u08-response-r1-c01",
        "o017-u08-ms-v2-theorem",
        "o017-u08-ms-v2-proof",
        "o017-u08-worked-unresolved-items",
        "o017-u08-response-matrix",
        "o017-u08-completion-metadata",
        "o017-u08-completion-claim",
        "o017-u08-completion-proof",
        *(f"o017-u08-e{index:02d}" for index in range(1, 7)),
        *(f"o017-u08-h{index:02d}" for index in range(1, 7)),
    }
)


UNIT8 = UnitSpec(
    id="O017-U08",
    ordinal=8,
    title="Catatan Seminar, Laporan Penelaah, dan Tanggapan terhadap Kritik",
    source_path=SOURCE / "units" / "08-seminar-penelaah-tanggapan-kritik.qmd",
    html_relative_path=Path("units/08-seminar-penelaah-tanggapan-kritik.html"),
    required_section_ids=UNIT8_SOURCE_ANCHORS,
    required_entity_fragments=UNIT8_SOURCE_ANCHORS,
    exercise_solution_pairs=tuple((f"O017-U08-E{index:02d}", f"O017-U08-H{index:02d}") for index in range(1, 7)),
    computations=(),
    records_factory=unit8_records,
    relations=UNIT8_RELATIONS,
    manifest_inputs=(),
    scope_notes=(
        "Unit 8 is wholly original O017 material built around synthetic local seminar, manuscript, review, and completion packets; no external donor is adapted.",
        "The identity-map counterexample refutes only the uniqueness clause of V1, while the endpoint/IVT existence argument remains valid and the candidate V2 theorem has a complete proof.",
        "Missing recording segments are recorded as missing rather than reconstructed, and every recommendation is bounded by the evidence actually available.",
        "All seminar, review, response, and manuscript exchange is synthetic and local; no real message, report, submission, or contact was sent.",
        "B80 owns software mechanics; Units 4, 5, and 7 own provenance design, exposition architecture, and erratum diagnosis respectively; Unit 8 owns evidence-bounded seminar/referee communication and response closure.",
        "Unit 8 admission is not full-course completion.",
    ),
    admission_filename="UNIT_08_ADMISSION.md",
    qa_filename="UNIT_08_QA.json",
    visual_qa_filename="UNIT_08_VISUAL_QA.json",
    visual_qa_script_filename="visual_qa_unit.cjs",
    expected_source_sha256="340ed58452642f29cf4ce608ce6fde01068f460f2100878c913d9a0987e154a9",
    expected_id_type_sha256="65505dd9b19894fc1530da8ae5438a4e97631b7ff0f8c63c74848d283950ffbe",
    expected_relation_map_sha256="e5fab3f8cf5cd4614b9d584d96849f68f6968a90c11a0e3bf3c3c6dd29b07e2e",
)


UNIT9_SEGMENTS = (
    ("O017-U09-SEG-OUTCOMES", "o017-u09-outcomes"),
    ("O017-U09-SEG-BOUNDED-CONTRIBUTION", "o017-u09-bounded-contribution"),
    ("O017-U09-SEG-SEVEN-STATES", "o017-u09-seven-states"),
    ("O017-U09-SEG-SIDE-STATES", "o017-u09-terminal-and-side-states"),
    ("O017-U09-SEG-STATE-MACHINE", "o017-u09-state-machine"),
    ("O017-U09-SEG-SELECTION-GATE", "o017-u09-selection-gate"),
    ("O017-U09-SEG-WORKED-CONTRIBUTION", "o017-u09-worked-contribution"),
    ("O017-U09-SEG-MINIMAL-REPRODUCER", "o017-u09-minimal-reproducer"),
    ("O017-U09-SEG-PROOF-REPAIR", "o017-u09-proof-repair"),
    ("O017-U09-SEG-BEFORE-AFTER", "o017-u09-before-after-validation"),
    ("O017-U09-SEG-MINIMAL-PATCH", "o017-u09-minimal-patch"),
    ("O017-U09-SEG-SCOPE-UNCERTAINTY", "o017-u09-scope-and-uncertainty"),
    ("O017-U09-SEG-RIGHTS", "o017-u09-rights-and-attribution"),
    ("O017-U09-SEG-CONTRIBUTION-PACKET", "o017-u09-contribution-packet"),
    ("O017-U09-SEG-PACKET-CHECKLIST", "o017-u09-packet-checklist"),
    ("O017-U09-SEG-WORKED-STATE-LEDGER", "o017-u09-worked-state-ledger"),
    ("O017-U09-SEG-SINGLE-MESSAGE", "o017-u09-single-message"),
    ("O017-U09-SEG-ROLLBACK", "o017-u09-rollback-withdrawal"),
    ("O017-U09-SEG-WITHDRAWAL-TRIGGERS", "o017-u09-worked-withdrawal-triggers"),
    ("O017-U09-SEG-PORTFOLIO-EVIDENCE", "o017-u09-portfolio-as-evidence-map"),
    ("O017-U09-SEG-PORTFOLIO-ARCHITECTURE", "o017-u09-portfolio-architecture"),
    ("O017-U09-SEG-U01-U08-MAP", "o017-u09-u01-u08-evidence-map"),
    ("O017-U09-SEG-PORTFOLIO-MANIFEST", "o017-u09-portfolio-manifest"),
    ("O017-U09-SEG-ACCESSIBILITY", "o017-u09-accessibility"),
    ("O017-U09-SEG-EVIDENCE-REFLECTION", "o017-u09-evidence-based-reflection"),
    ("O017-U09-SEG-EXERCISES", "o017-u09-exercises"),
    ("O017-U09-SEG-GUIDANCE", "o017-u09-guidance"),
    ("O017-U09-SEG-CAPSTONE", "o017-u09-capstone"),
    ("O017-U09-SEG-CAPSTONE-RUBRIC", "o017-u09-capstone-rubric"),
    ("O017-U09-SEG-BOUNDARY", "o017-u09-boundary"),
    ("O017-U09-SEG-PROVENANCE", "o017-u09-provenance"),
)


UNIT9_CONCEPTS = (
    ("O017-U09-CPT-BOUNDED-CONTRIBUTION", "kontribusi komunitas terbatas"),
    ("O017-U09-CPT-LIFECYCLE-STATUS", "status daur hidup kontribusi"),
    ("O017-U09-CPT-TRANSITION-EVIDENCE", "bukti transisi status"),
    ("O017-U09-CPT-SELECTION-GATE", "gerbang pemilihan kontribusi"),
    ("O017-U09-CPT-MINIMUM-REPRODUCER", "reproducer minimum"),
    ("O017-U09-CPT-MINIMAL-PROOF-REPAIR", "perbaikan bukti minimal"),
    ("O017-U09-CPT-BEFORE-AFTER-VALIDATION", "validasi sebelum dan sesudah"),
    ("O017-U09-CPT-COMPONENT-RIGHTS", "hak dan atribusi per komponen"),
    ("O017-U09-CPT-CONTRIBUTION-PACKET", "paket kontribusi lengkap"),
    ("O017-U09-CPT-ONE-UNSENT-DRAFT", "satu draf keluar yang belum dikirim"),
    ("O017-U09-CPT-ROLLBACK-HISTORY", "pemulihan tanpa menghapus sejarah"),
    ("O017-U09-CPT-PORTFOLIO-EVIDENCE-MAP", "peta klaim ke bukti portofolio"),
)


UNIT9_CORE_RECORD_IDS = (
    "O017-U09-SEG-ORIGINAL-BRIDGE",
    "O017-U09-UP-W01",
    "O017-U09-UP-V1",
    "O017-U09-DEST-01",
    "O017-U09-LOC001",
    "O017-U09-THM001",
    "O017-U09-PROOF001",
    "O017-U09-DEFECT001",
    "O017-U09-WITNESS001",
    "O017-U09-PATCH001",
    "O017-U09-PROOF002",
    "O017-U09-UP-V2C",
    "O017-U09-ERRATUM-DRAFT-01",
    "O017-U09-PACKET001",
    "O017-U09-MSG001",
    "O017-U09-ROLLBACK001",
    "O017-U09-PORTMAP001",
    "O017-U09-CAPSTONE001",
    "O017-U09-RIGHTS001",
    "O017-U09-NOCONTACT001",
    "O017-U09-STATE-DRAFT",
    "O017-U09-STATE-PREPARED",
    "O017-U09-STATE-SUBMITTED",
    "O017-U09-STATE-ACKNOWLEDGED",
    "O017-U09-STATE-ACCEPTED",
    "O017-U09-STATE-MERGED",
    "O017-U09-STATE-PUBLISHED",
    "O017-U09-EVT001",
    "O017-U09-EVT002",
    "O017-U09-QA-01",
    "O017-U09-ARTIFACT-HTML",
)


def unit9_records(hashes: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = [
        record("unit", "O017-U09", ordinal=9, title="Kontribusi Komunitas Terbatas dan Portofolio yang Dapat Diaudit", locale="id-ID"),
        record("segment", "O017-U09-SEG-ORIGINAL-BRIDGE", unit="O017-U09", html_fragment="o017-u09-original-bridge"),
        record("resource", "O017-U09-UP-W01", unit="O017-U09", html_fragment="o017-u09-target-metadata", title="Lembar Induksi untuk Jumlah Ganjil", role="synthetic contribution target", synthetic=True),
        record("edition", "O017-U09-UP-V1", unit="O017-U09", html_fragment="o017-u09-target-metadata", version="1.2-sintetis", status="frozen-defective-target"),
        record("artifact", "O017-U09-DEST-01", unit="O017-U09", html_fragment="o017-u09-target-metadata", status="synthetic-local-destination", external=False),
        record("segment", "O017-U09-LOC001", unit="O017-U09", html_fragment="o017-u09-upstream-snippet", locator="Lemma 2, proof lines L3-L5"),
        record("theorem", "O017-U09-THM001", unit="O017-U09", html_fragment="o017-u09-upstream-snippet", title="Jumlah n bilangan ganjil pertama", claim_status="true"),
        record("proof", "O017-U09-PROOF001", unit="O017-U09", html_fragment="o017-u09-upstream-snippet", proof_status="defective-proof-attempt", local_locators=["L1", "L2", "L3", "L4", "L5"]),
        record("correction", "O017-U09-DEFECT001", unit="O017-U09", html_fragment="o017-u09-upstream-snippet", correction_kind="wrong-new-term-index", status="diagnosed"),
        record("counterexample", "O017-U09-WITNESS001", unit="O017-U09", html_fragment="o017-u09-minimal-reproducer", witness="n=1 gives V1 S_2=2 while definition gives S_2=4", target_kind="proof-step-not-theorem"),
        record("correction", "O017-U09-PATCH001", unit="O017-U09", html_fragment="o017-u09-repaired-lines", correction_kind="minimal-proof-repair", status="validated-locally", changed_locators=["L3", "L4"], preserved_locators=["L1", "L2", "L5"]),
        record("proof", "O017-U09-PROOF002", unit="O017-U09", html_fragment="o017-u09-repaired-lines", proof_status="valid-corrected-induction"),
        record("edition", "O017-U09-UP-V2C", unit="O017-U09", html_fragment="o017-u09-proof-repair", version="candidate-v2", status="candidate-local-unpublished"),
        record("artifact", "O017-U09-ERRATUM-DRAFT-01", unit="O017-U09", html_fragment="o017-u09-erratum-draft", status="internal-technical-draft-not-outbound"),
        record("artifact", "O017-U09-PACKET001", unit="O017-U09", html_fragment="o017-u09-contribution-packet", status="prepared-locally-not-submitted"),
        record("artifact", "O017-U09-MSG001", unit="O017-U09", html_fragment="o017-u09-outbound-draft", status="draft-local-not-sent", message_count=1),
        record("artifact", "O017-U09-ROLLBACK001", unit="O017-U09", html_fragment="o017-u09-rollback-withdrawal", status="local-recovery-protocol"),
        record("artifact", "O017-U09-PORTMAP001", unit="O017-U09", html_fragment="o017-u09-u01-u08-evidence-map", status="course-evidence-map"),
        record("artifact", "O017-U09-CAPSTONE001", unit="O017-U09", html_fragment="o017-u09-capstone", status="local-capstone-specification"),
        record("rights", "O017-U09-RIGHTS001", unit="O017-U09", html_fragment="o017-u09-provenance", license="CC BY-SA 4.0", license_url="https://creativecommons.org/licenses/by-sa/4.0/", scope="original synthetic Unit 9 text and components"),
        record("qa_event", "O017-U09-NOCONTACT001", unit="O017-U09", html_fragment="o017-u09-worked-state-ledger", status="no-contact-no-submission-no-publication"),
        *tuple(record("qa_event", f"O017-U09-STATE-{identifier}", unit="O017-U09", html_fragment="o017-u09-seven-states", event_kind="lifecycle-state-definition", value=value) for identifier, value in (("DRAFT", "draft"), ("PREPARED", "prepared"), ("SUBMITTED", "submitted"), ("ACKNOWLEDGED", "acknowledged"), ("ACCEPTED", "accepted"), ("MERGED", "merged"), ("PUBLISHED", "published"))),
        record("qa_event", "O017-U09-EVT001", unit="O017-U09", html_fragment="o017-u09-worked-state-ledger", status="draft", local_alias="EVT-01", external=False),
        record("qa_event", "O017-U09-EVT002", unit="O017-U09", html_fragment="o017-u09-worked-state-ledger", status="prepared", local_alias="EVT-02", external=False),
        record(
            "qa_event",
            "O017-U09-QA-01",
            status="pass",
            checks=[
                "source-hash-lock",
                "odd-sum-proof-defect",
                "minimal-corrected-proof",
                "before-after-validation",
                "lifecycle-state-honesty",
                "single-unsent-message",
                "component-rights",
                "portfolio-evidence-map",
                "html-structure",
                "offline-mathml",
                "local-link-closure",
                "exercise-solution-correspondence",
                "backend-referential-integrity",
            ],
        ),
        record("artifact", "O017-U09-ARTIFACT-HTML", path="build/html/units/09-kontribusi-komunitas-portofolio.html", sha256=hashes["html"], media_type="text/html"),
    ]
    records.extend(record("concept", identifier, label_id=label, unit="O017-U09") for identifier, label in UNIT9_CONCEPTS)
    records.extend(record("segment", identifier, unit="O017-U09", html_fragment=fragment) for identifier, fragment in UNIT9_SEGMENTS)
    for index in range(1, 7):
        records.extend(
            (
                record("exercise", f"O017-U09-E{index:02d}", unit="O017-U09", ordinal=index, html_fragment=f"o017-u09-e{index:02d}"),
                record("solution", f"O017-U09-H{index:02d}", unit="O017-U09", ordinal=index, solution_kind="guidance", html_fragment=f"o017-u09-h{index:02d}"),
            )
        )
    return tuple(records)


def _u9_relation(number: int, source: str, predicate: str, target: str, evidence_kind: str = "metadata") -> RelationSpec:
    """Return one explicitly numbered, already-issued Unit 9 relation."""

    return RelationSpec(f"O017-U09-REL-{number:03d}", source, predicate, target, evidence_kind)


UNIT9_RELATIONS = (
    _u9_relation(1, "O017-EDITION-01", "contains", "O017-U09"),
    _u9_relation(2, "O017-U09", "authored-from", "O017-SOURCE-ORIGINAL"),
    _u9_relation(3, "O017-U09", "licensed-by", "O017-RIGHTS-ORIGINAL-TEXT", "component-rights"),
    _u9_relation(4, "O017-U09", "governed-by", "O017-U09-RIGHTS001", "component-rights"),
    _u9_relation(5, "O017-U09", "verified-by", "O017-U09-QA-01"),
    _u9_relation(6, "O017-U09", "has-artifact", "O017-U09-ARTIFACT-HTML"),
    _u9_relation(7, "O017-U09-QA-01", "verifies", "O017-U09-ARTIFACT-HTML"),
    _u9_relation(8, "O017-U09", "external-contact-state", "O017-U09-NOCONTACT001"),
    _u9_relation(9, "O017-U09", "provenance-stated-at", "O017-U09-SEG-PROVENANCE"),
    _u9_relation(10, "O017-U09", "part-of", "O017-D120"),
    _u9_relation(11, "O017-U09", "bounded-from", "B80"),
    *tuple(_u9_relation(12 + index, "O017-U09", "contains", identifier) for index, identifier in enumerate(UNIT9_CORE_RECORD_IDS)),
    *tuple(_u9_relation(43 + index, "O017-U09", "teaches", identifier) for index, (identifier, _label) in enumerate(UNIT9_CONCEPTS)),
    *tuple(_u9_relation(55 + index, identifier, "developed-in", UNIT9_SEGMENTS[(1, 2, 4, 5, 7, 8, 9, 12, 13, 16, 17, 19)[index]][0]) for index, (identifier, _label) in enumerate(UNIT9_CONCEPTS)),
    *tuple(_u9_relation(67 + index, "O017-U09", "contains", identifier) for index, (identifier, _fragment) in enumerate(UNIT9_SEGMENTS)),
    *tuple(_u9_relation(96 + 2 * index, "O017-U09", "contains", f"O017-U09-E{index:02d}") for index in range(1, 7)),
    *tuple(_u9_relation(97 + 2 * index, "O017-U09", "contains", f"O017-U09-H{index:02d}") for index in range(1, 7)),
    *tuple(_u9_relation(109 + index, f"O017-U09-E{index:02d}", "guided-by", f"O017-U09-H{index:02d}") for index in range(1, 7)),
    _u9_relation(116, "O017-U09-UP-V1", "version-of", "O017-U09-UP-W01"),
    _u9_relation(117, "O017-U09-UP-V2C", "candidate-revision-of", "O017-U09-UP-V1", "correction-evidence"),
    _u9_relation(118, "O017-U09-LOC001", "locator-in", "O017-U09-UP-V1"),
    _u9_relation(119, "O017-U09-PROOF001", "proof-attempt-for", "O017-U09-THM001", "mathematical-proof"),
    _u9_relation(120, "O017-U09-PROOF001", "contained-in", "O017-U09-UP-V1"),
    _u9_relation(121, "O017-U09-DEFECT001", "defect-in", "O017-U09-PROOF001", "mathematical-diagnosis"),
    _u9_relation(122, "O017-U09-WITNESS001", "witnesses-failure-of", "O017-U09-PROOF001", "mathematical-counterexample"),
    _u9_relation(123, "O017-U09-WITNESS001", "demonstrates", "O017-U09-DEFECT001", "mathematical-counterexample"),
    _u9_relation(124, "O017-U09-PATCH001", "repairs", "O017-U09-DEFECT001", "mathematical-correction"),
    _u9_relation(125, "O017-U09-PATCH001", "preserves-statement", "O017-U09-THM001", "mathematical-correction"),
    _u9_relation(126, "O017-U09-PROOF002", "corrected-version-of", "O017-U09-PROOF001", "mathematical-correction"),
    _u9_relation(127, "O017-U09-PROOF002", "incorporates", "O017-U09-PATCH001", "mathematical-correction"),
    _u9_relation(128, "O017-U09-PROOF002", "proves", "O017-U09-THM001", "mathematical-proof"),
    _u9_relation(129, "O017-U09-PROOF002", "contained-in", "O017-U09-UP-V2C"),
    _u9_relation(130, "O017-U09-PACKET001", "targets", "O017-U09-UP-V1"),
    _u9_relation(131, "O017-U09-PACKET001", "uses-locator", "O017-U09-LOC001"),
    *tuple(_u9_relation(132 + index, "O017-U09-PACKET001", "includes", identifier) for index, identifier in enumerate(("O017-U09-DEFECT001", "O017-U09-WITNESS001", "O017-U09-PATCH001", "O017-U09-PROOF002", "O017-U09-MSG001", "O017-U09-RIGHTS001", "O017-U09-ROLLBACK001", "O017-U09-ERRATUM-DRAFT-01"))),
    _u9_relation(140, "O017-U09-PACKET001", "intended-for", "O017-U09-DEST-01"),
    _u9_relation(141, "O017-U09-PACKET001", "has-proven-state", "O017-U09-STATE-PREPARED", "local-state-evidence"),
    _u9_relation(142, "O017-U09-MSG001", "part-of", "O017-U09-PACKET001"),
    _u9_relation(143, "O017-U09-MSG001", "has-state", "O017-U09-STATE-DRAFT", "local-state-evidence"),
    _u9_relation(144, "O017-U09-MSG001", "intended-for", "O017-U09-DEST-01"),
    _u9_relation(145, "O017-U09-EVT001", "establishes", "O017-U09-STATE-DRAFT", "local-state-evidence"),
    _u9_relation(146, "O017-U09-EVT002", "establishes", "O017-U09-STATE-PREPARED", "local-state-evidence"),
    _u9_relation(147, "O017-U09-NOCONTACT001", "documents-no-external-contact-for", "O017-U09-PACKET001", "negative-event-evidence"),
    _u9_relation(148, "O017-U09-NOCONTACT001", "documents-no-external-contact-for", "O017-U09-MSG001", "negative-event-evidence"),
    _u9_relation(149, "O017-U09-ROLLBACK001", "governs", "O017-U09-PACKET001"),
    *tuple(_u9_relation(150 + index, source, "canonical-next-on-common-route", target, "non-exhaustive-state-route-definition") for index, (source, target) in enumerate((("O017-U09-STATE-DRAFT", "O017-U09-STATE-PREPARED"), ("O017-U09-STATE-PREPARED", "O017-U09-STATE-SUBMITTED"), ("O017-U09-STATE-SUBMITTED", "O017-U09-STATE-ACKNOWLEDGED"), ("O017-U09-STATE-ACKNOWLEDGED", "O017-U09-STATE-ACCEPTED"), ("O017-U09-STATE-ACCEPTED", "O017-U09-STATE-MERGED"), ("O017-U09-STATE-MERGED", "O017-U09-STATE-PUBLISHED")))),
    *tuple(_u9_relation(155 + index, "O017-U09-PORTMAP001", "maps-evidence-from", f"O017-U{index:02d}") for index in range(1, 9)),
    *tuple(_u9_relation(164 + index, "O017-U09-CAPSTONE001", "requires", identifier) for index, identifier in enumerate(("O017-U09-PACKET001", "O017-U09-PORTMAP001", "O017-U09-ROLLBACK001", "O017-U09-RIGHTS001", "O017-U09-NOCONTACT001"))),
    _u9_relation(169, "O017-U09-RIGHTS001", "derives-permissions-from", "O017-RIGHTS-ORIGINAL-TEXT", "component-rights"),
    _u9_relation(170, "O017-U09-UP-V1", "contains", "O017-U09-THM001"),
    _u9_relation(171, "O017-U09-UP-V1", "contains", "O017-U09-PROOF001"),
    _u9_relation(172, "O017-U09-UP-V2C", "contains", "O017-U09-THM001"),
    _u9_relation(173, "O017-U09-UP-V2C", "contains", "O017-U09-PROOF002"),
    _u9_relation(174, "O017-U09-ERRATUM-DRAFT-01", "diagnoses", "O017-U09-DEFECT001", "correction-evidence"),
    _u9_relation(175, "O017-U09-MSG001", "describes", "O017-U09-PATCH001", "correction-evidence"),
    _u9_relation(176, "O017-U09", "has-completion-task", "O017-U09-CAPSTONE001"),
    *tuple(_u9_relation(177 + index, "O017-U09-RIGHTS001", "applies-to", identifier, "component-rights") for index, identifier in enumerate(("O017-U09-UP-W01", "O017-U09-UP-V1", "O017-U09-UP-V2C", "O017-U09-PATCH001", "O017-U09-PROOF002", "O017-U09-MSG001", "O017-U09-PACKET001", "O017-U09-PORTMAP001", "O017-U09-CAPSTONE001"))),
)


UNIT9_SOURCE_ANCHORS = frozenset(
    {
        *(fragment for _identifier, fragment in UNIT9_SEGMENTS),
        "o017-u09-original-bridge",
        "o017-u09-target-metadata",
        "o017-u09-upstream-snippet",
        "o017-u09-repaired-lines",
        "o017-u09-erratum-draft",
        "o017-u09-outbound-draft",
        *(f"o017-u09-e{index:02d}" for index in range(1, 7)),
        *(f"o017-u09-h{index:02d}" for index in range(1, 7)),
    }
)


UNIT9 = UnitSpec(
    id="O017-U09",
    ordinal=9,
    title="Kontribusi Komunitas Terbatas dan Portofolio yang Dapat Diaudit",
    source_path=SOURCE / "units" / "09-kontribusi-komunitas-portofolio.qmd",
    html_relative_path=Path("units/09-kontribusi-komunitas-portofolio.html"),
    required_section_ids=UNIT9_SOURCE_ANCHORS,
    required_entity_fragments=UNIT9_SOURCE_ANCHORS,
    exercise_solution_pairs=tuple((f"O017-U09-E{index:02d}", f"O017-U09-H{index:02d}") for index in range(1, 7)),
    computations=(),
    records_factory=unit9_records,
    relations=UNIT9_RELATIONS,
    manifest_inputs=(),
    scope_notes=(
        "Unit 9 is wholly original O017 material built around one synthetic local contribution target; no external donor, repository, maintainer, or platform is used.",
        "The n=1 witness rejects the defective V1 induction step, not the true odd-number-sum theorem; the minimal patch changes only L3 and L4, preserves L5, and gives a complete general induction repair.",
        "Lifecycle labels are independently evidenced event predicates and the displayed chain is only a non-exhaustive canonical route; the ledger proves only draft and prepared-local while submitted, acknowledged, accepted, merged, and published remain definitions without corresponding events.",
        "There is exactly one local outward-message draft, marked not sent; no real contact, issue, submission, merge, or publication is claimed.",
        "B80 owns Git, APIs, programming, software testing, environments, and deployment; Unit 9 owns bounded contribution packaging, lifecycle evidence, recovery, rights, and the Unit 1-8 evidence portfolio.",
        "Unit 9 admission closes the declared unit sequence but is not full-reader publication or course completion until full-package QA and authorized Zenodo readback pass.",
    ),
    admission_filename="UNIT_09_ADMISSION.md",
    qa_filename="UNIT_09_QA.json",
    visual_qa_filename="UNIT_09_VISUAL_QA.json",
    visual_qa_script_filename="visual_qa_unit.cjs",
    expected_source_sha256="7a2072c10f1714715856177e7e83f968baa1f079eaad92d138a71a05a01cc906",
    expected_id_type_sha256="922cf333c7e18116cd3de44b49c206db3dd28a17a521c9951027388d11d7f95e",
    expected_relation_map_sha256="481a066391cefe3eaea491b1232cd0f029d63f5d8e00db1c5cb97845928c36b7",
)


COURSE = CourseSpec(
    lane_id="O017-D120-ID",
    entity_classes=ENTITY_CLASSES,
    common_records=COMMON_RECORDS,
    common_relations=(),
    # Register units in the live course only through the current admission
    # candidate so unadmitted downstream units cannot leak into earlier
    # reader/backend evidence.
    units=(UNIT1, UNIT2, UNIT3, UNIT4, UNIT5, UNIT6, UNIT7, UNIT8, UNIT9),
)
