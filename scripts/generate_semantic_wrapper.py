#!/usr/bin/env python3
"""Generate the versioned O017 semantic/assessment wrapper deterministically.

This script never writes the pre-existing backend record stream, active graph,
relation ledger, or descriptive schema.  Its own relation ledger is write-once
and prefix-preserving: changing an issued relation requires a new wrapper
version rather than rewriting history.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SCHEMA_PATH = BACKEND / "semantic-wrapper-v1.schema.json"
BASELINE_PATH = BACKEND / "semantic-wrapper-v1.baseline.json"
RECORDS_PATH = BACKEND / "semantic-wrapper-v1.records.jsonl"
LOCALIZATIONS_PATH = BACKEND / "semantic-wrapper-v1.localizations.jsonl"
RELATIONS_PATH = BACKEND / "semantic-wrapper-v1.relations-ledger.csv"
DATASET_PATH = BACKEND / "semantic-wrapper-v1.dataset.json"

SEMANTIC_SCHEMA = "o017-semantic-wrapper-record-v1"
LOCALIZATION_SCHEMA = "o017-localized-text-record-v1"
DATASET_SCHEMA = "o017-semantic-wrapper-dataset-v1"
MODEL_VERSION = "1.0.0"
RELEASE_VERSION = "2026.08.24"

CURRENT_EDITION_VERSION = "2026.08.24"
CURRENT_ADMISSION_EVIDENCE = (
    "nine unit admissions plus authentic-delivery wrapper, semantic-backend, "
    "final-reader, and release QA receipts"
)
HISTORICAL_STABLE_RECORD_PROJECTION_SHA256 = (
    "976e51eca78ba290b3c9c55e9dd30cfc4eb0a17fbf800fb54d72303edb42f590"
)
PERMITTED_BASELINE_RECORD_DELTAS = {
    "O017-EDITION-01": frozenset(
        {
            "version",
            "admission_evidence",
            "creator",
            "production_system",
            "production_disclosure",
        }
    ),
    **{
        f"O017-U{unit:02d}-ARTIFACT-HTML": frozenset({"sha256"})
        for unit in range(1, 10)
    },
    "O017-RIGHTS-ORIGINAL-TEXT": frozenset({"licensor"}),
    "O017-RIGHTS-ORIGINAL-CODE": frozenset({"licensor"}),
    "O017-RIGHTS-GENERATED-DATA": frozenset({"licensor"}),
    "O017-U01-THEOREM-01": frozenset({"title"}),
}

DELIVERY_WRAPPER_PATH = "source/wrapper/index.qmd"
DELIVERY_DEFINITIONS_PATH = "delivery/definitions/o017-delivery-definitions.json"
DELIVERY_SCHEMA_PATH = "delivery/schema/o017-delivery.schema.json"
DELIVERY_CALIBRATION_PACKAGE_PATH = "delivery/calibration/calibration-package.json"

DELIVERY_BINDINGS = {
    "REAL-SOURCE-SEARCH": ("O017-WRAP-A01", "O017-WRAP-CAL-A01", "o017-wrap-a01-real-source-search"),
    "LIVE-SEMINAR": ("O017-WRAP-A02", "O017-WRAP-CAL-A02", "o017-wrap-a02-seminar"),
    "INDEPENDENT-REFEREE-CYCLE": ("O017-WRAP-A03", "O017-WRAP-CAL-A03", "o017-wrap-a03-referee-cycle"),
    "REAL-ERRATUM-DOSSIER": ("O017-WRAP-A04", "O017-WRAP-CAL-A04", "o017-wrap-a04-erratum"),
    "BOUNDED-COMMUNITY-TRANSACTION": ("O017-WRAP-A05", "O017-WRAP-CAL-A05", "o017-wrap-a05-community"),
}

UNIT_FILES = {
    1: "01-membaca-argumen.qmd",
    2: "02-menelusuri-sumber.qmd",
    3: "03-merekonstruksi-pembuktian.qmd",
    4: "04-sitasi-provenance-catatan-sumber.qmd",
    5: "05-eksposisi-matematika.qmd",
    6: "06-komputasi-dapat-direproduksi.qmd",
    7: "07-errata-koreksi-batas-kepastian.qmd",
    8: "08-seminar-penelaah-tanggapan-kritik.qmd",
    9: "09-kontribusi-komunitas-portofolio.qmd",
}

COMPETENCIES = {
    1: (
        "READ_ARGUMENT_NETWORKS",
        "Membaca argumen sebagai jejaring klaim",
        "Memisahkan klaim, asumsi, dukungan, batas, dan ketidakpastian dalam argumen matematika.",
    ),
    2: (
        "SOURCE_AUTHORITY",
        "Menelusuri sumber dan menilai otoritas",
        "Menemukan, membekukan, membandingkan, dan membatasi otoritas sumber matematika yang tepat.",
    ),
    3: (
        "PROOF_RECONSTRUCTION",
        "Merekonstruksi pembuktian",
        "Menutup atau melaporkan celah pembuktian melalui kuantor, kontrak lemma, dan graf ketergantungan.",
    ),
    4: (
        "SCHOLARLY_PROVENANCE",
        "Merawat sitasi dan provenance",
        "Menghubungkan klaim ke karya, versi, salinan, lokator, bukti, keputusan, dan ketidakpastian.",
    ),
    5: (
        "AUDITABLE_EXPOSITION",
        "Menulis eksposisi yang dapat diaudit",
        "Mengubah argumen yang sah menjadi jalur baca dan penyajian lisan yang jelas serta dapat diperiksa.",
    ),
    6: (
        "COMPUTATIONAL_EVIDENCE",
        "Menempatkan bukti komputasional",
        "Mereproduksi dan mengkritik bukti komputasional tanpa mengubahnya menjadi pembuktian universal.",
    ),
    7: (
        "ERRATA_AND_CORRECTION",
        "Mendiagnosis errata dan koreksi",
        "Membuktikan cacat, membatasi dampak, dan mengusulkan koreksi tanpa menghapus sejarah.",
    ),
    8: (
        "SEMINAR_AND_REVIEW",
        "Berpartisipasi dalam seminar dan penelaahan",
        "Mencatat seminar, menelaah karya, menanggapi kritik, dan mempertahankan masalah yang belum selesai.",
    ),
    9: (
        "BOUNDED_CONTRIBUTION",
        "Menyiapkan kontribusi komunitas terbatas",
        "Membatasi, memvalidasi, mengomunikasikan, dan mencatat status satu kontribusi tanpa melebihkan bukti.",
    ),
}

EVALUATOR_ROLES = [
    (
        "COURSE-ASSESSOR",
        "COURSE_ASSESSOR",
        "Penilai kursus",
        "Menilai tugas lokal terhadap rubrik yang diterbitkan dan mempertahankan bukti keputusan.",
        "course_assessor",
        False,
    ),
    (
        "SEMINAR-SUPERVISOR",
        "SEMINAR_SUPERVISOR",
        "Supervisor seminar",
        "Mengesahkan kehadiran atau penyampaian seminar nyata dan batas bukti peristiwa.",
        "event_supervisor",
        False,
    ),
    (
        "INDEPENDENT-REFEREE",
        "INDEPENDENT_REFEREE",
        "Penelaah independen",
        "Menilai artefak sebagai orang yang berbeda dari pembelajar atau penulis artefak tersebut.",
        "independent_from_learner",
        False,
    ),
    (
        "INDEPENDENT-MATH-CHECKER",
        "INDEPENDENT_MATH_CHECKER",
        "Pemeriksa matematika independen",
        "Memeriksa diagnosis atau koreksi matematika secara terpisah dan menyimpan dasar penilaiannya.",
        "independent_from_learner",
        False,
    ),
    (
        "AUTHORIZED-TRANSACTION-VERIFIER",
        "AUTHORIZED_TRANSACTION_VERIFIER",
        "Pemeriksa transaksi berwenang",
        "Memeriksa bukti kewenangan dan peristiwa eksternal tanpa menyimpulkan penerimaan dari pengiriman saja.",
        "authorized_external_event_verifier",
        False,
    ),
]


AUTHENTIC_ASSESSMENTS = [
    {
        "slug": "REAL-SOURCE-SEARCH",
        "label": "Penelusuran sumber nyata",
        "description": "Penelusuran tanpa daftar calon yang telah disemai terhadap satu makalah atau monograf matematika nyata yang dibekukan versinya.",
        "instructions": "Simpan pertanyaan, kueri, waktu pengambilan, aturan berhenti, versi, hak, perbandingan otoritas, keputusan, dan ketidakpastian.",
        "authenticity": "real_source",
        "competency_units": [1, 2, 4],
        "evaluator_roles": ["COURSE-ASSESSOR"],
        "completion_modes": ["authentic_direct"],
        "external_authority": "not_applicable",
        "criteria": [
            ("Target dan versi nyata", "Satu makalah atau monograf matematika nyata dibekukan dengan identitas karya, versi, salinan, lokator, tanggal pengambilan, dan dasar hak yang dapat diperiksa.", True, True, False, False),
            ("Penelusuran tanpa semaian", "Pertanyaan, semua kueri, lintasan temu, hasil negatif yang relevan, dan aturan berhenti dicatat tanpa menerima daftar calon yang telah disediakan sebagai pengganti penelusuran.", True, False, False, False),
            ("Perbandingan otoritas", "Sedikitnya dua permukaan atau sumber calon dibandingkan terhadap pertanyaan tertentu; reputasi dan urutan hasil tidak dipakai sebagai pembuktian.", False, False, False, False),
            ("Audit klaim", "Pernyataan bahwa sumber memuat klaim dipisahkan dari keputusan bahwa klaim benar, dengan lokator, dasar, dan batas inferensi yang eksplisit.", False, False, False, False),
            ("Ketidakpastian dan jejak keputusan", "Bidang yang hilang, konflik versi, keputusan inklusi, dan alasan berhenti dipertahankan tanpa tebakan.", True, False, False, False),
        ],
    },
    {
        "slug": "LIVE-SEMINAR",
        "label": "Seminar nyata",
        "description": "Kehadiran atau penyampaian seminar matematika nyata, atau padanan tersupervisi yang aksesibel, dengan rekaman bukti yang jujur.",
        "instructions": "Simpan bukti peristiwa, catatan berwaktu, peta ketergantungan, log pertanyaan, bagian yang tidak tersedia, koreksi, dan permukaan aksesibilitas.",
        "authenticity": "real_event",
        "competency_units": [1, 5, 8],
        "evaluator_roles": ["SEMINAR-SUPERVISOR", "COURSE-ASSESSOR"],
        "completion_modes": ["authentic_direct"],
        "external_authority": "not_applicable",
        "criteria": [
            ("Bukti peristiwa", "Identitas peristiwa, waktu, peran pembelajar, bukti kehadiran atau penyampaian, dan batas rekaman dapat diperiksa.", True, False, True, False),
            ("Catatan berwaktu", "Catatan membedakan observasi, verifikasi, pertanyaan, keberatan, dan bagian yang tidak terdengar atau tidak tersedia tanpa mengarang isi.", True, False, False, False),
            ("Peta ketergantungan", "Klaim utama, definisi, asumsi, lemma, bukti, dan masalah terbuka dipetakan dengan lokator atau waktu yang cukup tepat.", False, False, False, False),
            ("Pertanyaan dan koreksi", "Log pertanyaan serta catatan final yang telah dikoreksi mempertahankan perubahan, dasar, dan butir yang belum selesai.", True, False, False, False),
            ("Padanan aksesibel", "Jika audio atau video langsung tidak tersedia, padanan tersupervisi mempertahankan tujuan pembelajaran dan diberi label sebagai padanan, bukan peristiwa yang tidak terjadi.", False, False, False, False),
        ],
    },
    {
        "slug": "INDEPENDENT-REFEREE-CYCLE",
        "label": "Siklus penulis–penelaah independen",
        "description": "Satu siklus penelaahan dengan dua orang berbeda yang menjalankan peran penulis dan penelaah.",
        "instructions": "Pertahankan artefak awal, laporan, tanggapan, tabel disposisi, revisi, bukti sebelum/sesudah, identitas atau ID privat, dan masalah yang belum selesai.",
        "authenticity": "two_person_independent",
        "competency_units": [3, 4, 5, 8],
        "evaluator_roles": ["INDEPENDENT-REFEREE", "COURSE-ASSESSOR"],
        "completion_modes": ["authentic_direct"],
        "external_authority": "not_applicable",
        "criteria": [
            ("Independensi peran", "Pembelajar atau penulis dan penelaah adalah dua orang berbeda; identitas nyata atau ID privat dapat diaudit oleh penilai kursus.", True, False, True, False),
            ("Paket versi lengkap", "Artefak awal, laporan penelaah, tanggapan penulis, dan revisi akhir dibekukan sebagai versi terpisah tanpa menimpa sejarah.", True, True, False, False),
            ("Laporan berbukti", "Setiap komentar penting menyebut target, lokator, diagnosis, bukti, keparahan, keyakinan, dan tindakan yang dapat dilaksanakan.", False, False, True, False),
            ("Tabel disposisi", "Setiap komentar dipetakan ke keputusan, tindakan, bukti, lokasi perubahan, status, dan alasan bila ditolak atau ditahan.", False, False, True, False),
            ("Bukti sebelum/sesudah", "Perubahan penting diperiksa terhadap artefak awal dan akhir; dampak serta masalah yang belum selesai tetap terlihat.", True, True, True, False),
        ],
    },
    {
        "slug": "REAL-ERRATUM-DOSSIER",
        "label": "Dossier erratum sumber nyata",
        "description": "Audit satu sumber terbuka nyata yang dibekukan versinya, dengan diagnosis dapat direproduksi, koreksi minimal, dan pemeriksaan matematika independen.",
        "instructions": "Pengiriman bukan syarat dan tidak boleh disimpulkan. Simpan versi, hak, reproducer, koreksi, validasi, pemeriksaan independen, dampak, dan ketidakpastian.",
        "authenticity": "real_source_independently_checked",
        "competency_units": [2, 3, 4, 6, 7],
        "evaluator_roles": ["INDEPENDENT-MATH-CHECKER", "COURSE-ASSESSOR"],
        "completion_modes": ["authentic_direct"],
        "external_authority": "not_applicable",
        "criteria": [
            ("Sumber terbuka beku", "Karya, versi, salinan, lokator, redaksi, tanggal pemeriksaan, dan hak sumber nyata dapat diperiksa.", True, True, False, False),
            ("Diagnosis dapat direproduksi", "Reproducer atau rekonstruksi memeriksa seluruh hipotesis, menunjukkan kegagalan secara minimal, dan memisahkan observasi dari pembuktian.", True, True, False, False),
            ("Koreksi minimal", "Usulan koreksi merupakan perubahan terkecil yang cukup dan dibenarkan oleh argumen matematika, dengan cakupan yang tidak dilebihkan.", False, True, False, False),
            ("Pemeriksaan independen", "Orang yang berbeda memeriksa diagnosis dan koreksi, dengan keputusan, dasar, identitas atau ID privat, serta ketidaksetujuan yang tersisa.", True, False, True, False),
            ("Status dan dampak jujur", "Dossier membedakan disiapkan, diperiksa, dan dikirim; pengiriman tidak diklaim tanpa bukti, dan dampak di luar cakupan tetap belum diketahui.", True, False, False, False),
        ],
    },
    {
        "slug": "BOUNDED-COMMUNITY-TRANSACTION",
        "label": "Transaksi komunitas terbatas atau padanan lokal yang ditelaah eksternal",
        "description": "Satu kontribusi kecil, tidak duplikatif, dan dapat ditinjau yang hanya dikirim dengan kewenangan manusia terpisah; bila tindakan eksternal tidak aman atau tidak tersedia, gunakan penelaahan lokal independen dan label yang lebih lemah.",
        "instructions": "Catat keadaan sebenarnya: prepared, submitted, acknowledged, accepted, merged, published, rejected, withdrawn, unknown, atau externally_reviewed_local. Penerimaan tidak disyaratkan dan tidak boleh disimpulkan.",
        "authenticity": "authorized_external_or_reviewed_local",
        "competency_units": [4, 7, 8, 9],
        "evaluator_roles": ["INDEPENDENT-MATH-CHECKER", "AUTHORIZED-TRANSACTION-VERIFIER", "COURSE-ASSESSOR"],
        "completion_modes": ["community_transaction", "externally_reviewed_local"],
        "external_authority": "separate_specific_human_authorization_required",
        "criteria": [
            ("Lingkup dan nonduplikasi", "Satu target, satu kontribusi, versi, lokator, pencarian duplikasi, hak, dan hal yang tidak disentuh dinyatakan secara sempit.", True, True, False, False),
            ("Kualitas paket", "Diagnosis, perubahan minimal, validasi, atribusi, batas, jalur penarikan, dan satu pesan ringkas dapat ditinjau sebagai satu paket.", False, True, True, False),
            ("Kewenangan tindakan", "Setiap tindakan eksternal mempunyai kewenangan manusia terpisah untuk target tertentu; tanpa kewenangan, paket berhenti secara lokal.", True, False, True, True),
            ("Status berbukti", "Setiap transisi eksternal mempunyai bukti peristiwa; prepared tidak disebut submitted dan submitted tidak disebut accepted, merged, atau published.", True, False, True, False),
            ("Jalur alternatif jujur", "Jika tindakan eksternal tidak aman atau tidak tersedia, pemeriksa independen menilai paket nyata dan hasil diberi label externally_reviewed_local tanpa klaim partisipasi komunitas.", True, False, True, False),
        ],
    },
]


def fail(message: str) -> None:
    raise SystemExit(message)


def canonical_json(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
    else:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (text + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_identity(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(payload),
        "sha256": sha256_bytes(payload),
    }


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def parse_markdown_list(block: str, *, ordered: bool) -> list[str]:
    marker = re.compile(r"^(\d+\.\s+|-\s+)(.*)$" if ordered else r"^(-\s+)(.*)$")
    values: list[str] = []
    current: list[str] = []
    for line in block.splitlines():
        match = marker.match(line)
        if match:
            if current:
                values.append(compact_text(" ".join(current)))
            current = [match.group(2)]
        elif current and (line.startswith("   ") or line.startswith("  ")):
            current.append(line.strip())
        elif current and not line.strip():
            values.append(compact_text(" ".join(current)))
            current = []
        elif current:
            break
    if current:
        values.append(compact_text(" ".join(current)))
    return values


def extract_outcomes(text: str) -> tuple[str, list[str]]:
    match = re.search(r"(?ms)^## Hasil belajar \{#([^}]+)\}\s*(.*?)(?=^:::)", text)
    if not match:
        fail("missing outcomes section")
    outcomes = parse_markdown_list(match.group(2), ordered=True)
    if not outcomes:
        fail(f"no outcomes parsed for {match.group(1)}")
    return match.group(1), outcomes


def extract_unit_title(text: str) -> str:
    match = re.search(r'(?m)^title:\s*"([^"]+)"', text)
    if not match:
        fail("missing unit title")
    return match.group(1)


def extract_completion_block(text: str, unit: int) -> tuple[str, str, str | None]:
    if unit == 9:
        pattern = r"(?ms)^## Tugas akhir:[^\n]*\{#([^}]+)\}\s*(.*?)(?=^## |\Z)"
    else:
        pattern = r"(?ms)^## Tugas penyelesaian unit \{#([^}]+)\}\s*(.*?)(?=^## |\Z)"
    match = re.search(pattern, text)
    if not match:
        fail(f"missing completion block for Unit {unit}")
    block = match.group(2)
    rubric_match = re.search(r"(?m)^### Rubrik(?: analitik)? \{#([^}]+)\}", block)
    return match.group(1), block, rubric_match.group(1) if rubric_match else None


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def extract_existing_rubric(unit: int, block: str) -> dict[str, Any]:
    if unit == 1:
        if "Memo lulus jika:" not in block:
            fail("Unit 1 pass list not found")
        criteria = parse_markdown_list(block.split("Memo lulus jika:", 1)[1], ordered=False)
        return {
            "criteria": [(f"Kriteria {index}", text) for index, text in enumerate(criteria, 1)],
            "scoring": {"mode": "binary_all_required", "passing_value": "met"},
            "pass_rule": "Semua lima syarat pada daftar 'Memo lulus jika' harus dipenuhi.",
        }

    rubric_block = re.split(r"(?m)^### Rubrik(?: analitik)? \{#[^}]+\}\s*$", block, maxsplit=1)
    if len(rubric_block) != 2:
        fail(f"rubric heading not found for Unit {unit}")
    table_lines = [line for line in rubric_block[1].splitlines() if line.startswith("|")]
    if len(table_lines) < 3:
        fail(f"rubric table not found for Unit {unit}")
    rows = [split_table_row(line) for line in table_lines]
    data_rows = [row for row in rows[2:] if len(row) >= 4]
    # A few mathematical cells contain literal vertical bars (for absolute
    # value) that Markdown leaves unescaped.  The first three boundaries are
    # still stable; join the remainder back into the passing anchor.
    criteria = [(row[0], "|".join(row[3:])) for row in data_rows]
    if not criteria:
        fail(f"no rubric criteria parsed for Unit {unit}")
    pass_match = re.search(
        r"(?ms)Nilai lulus (?:adalah )?(?:sekurang-kurangnya )?(\d+) dari (\d+),(.*?)(?=\n\n|\Z)",
        block,
    )
    if not pass_match:
        fail(f"pass threshold not found for Unit {unit}")
    minimum = int(pass_match.group(1))
    maximum = int(pass_match.group(2))
    tail = compact_text(pass_match.group(0))
    required_names = re.findall(r"\*\*([^*]+)\*\*", tail)
    name_to_ordinal = {name: index for index, (name, _) in enumerate(criteria, 1)}
    missing = [name for name in required_names if name not in name_to_ordinal]
    if missing:
        fail(f"unmatched required rubric names for Unit {unit}: {missing}")
    return {
        "criteria": criteria,
        "minimum": minimum,
        "maximum": maximum,
        "required_ordinals": [name_to_ordinal[name] for name in required_names],
        "pass_rule": tail,
    }


def localization_id(subject_id: str, field: str) -> str:
    suffix = subject_id.removeprefix("O017-")
    return f"O017-L10N-ID-{suffix}-{field.replace('_', '-').upper()}"


def build_payloads() -> tuple[dict[str, bytes], dict[str, Any]]:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    verify_baseline(baseline)

    parsed_units: dict[int, dict[str, Any]] = {}
    source_inputs: list[dict[str, Any]] = []
    for unit, filename in UNIT_FILES.items():
        path = ROOT / "source" / "units" / filename
        text = path.read_text(encoding="utf-8")
        outcomes_fragment, outcomes = extract_outcomes(text)
        completion_fragment, completion_block, rubric_fragment = extract_completion_block(text, unit)
        parsed_units[unit] = {
            "path": path.relative_to(ROOT).as_posix(),
            "title": extract_unit_title(text),
            "outcomes_fragment": outcomes_fragment,
            "outcomes": outcomes,
            "completion_fragment": completion_fragment,
            "rubric_fragment": rubric_fragment,
            "rubric": extract_existing_rubric(unit, completion_block),
        }
        source_inputs.append(file_identity(path))

    delivery_input_paths = [
        ROOT / DELIVERY_WRAPPER_PATH,
        ROOT / DELIVERY_DEFINITIONS_PATH,
        ROOT / DELIVERY_SCHEMA_PATH,
        ROOT / "delivery/definitions/evidence-types.csv",
        ROOT / "delivery/definitions/lifecycle-statuses.csv",
        ROOT / "delivery/definitions/rubric-criteria.csv",
        ROOT / "delivery/calibration/01-real-source-search.md",
        ROOT / "delivery/calibration/02-seminar-supervised-equivalent.md",
        ROOT / "delivery/calibration/03-independent-referee-cycle.md",
        ROOT / "delivery/calibration/04-real-source-erratum-dossier.md",
        ROOT / "delivery/calibration/05-externally-reviewed-local.md",
        ROOT / DELIVERY_CALIBRATION_PACKAGE_PATH,
        ROOT / "delivery/calibration/evidence-manifest.csv",
        ROOT / "delivery/README.md",
        ROOT / "delivery/VALIDATION.json",
    ]
    for path in delivery_input_paths:
        if not path.is_file():
            fail(f"missing delivery integration input: {path.relative_to(ROOT).as_posix()}")
        source_inputs.append(file_identity(path))

    delivery_definitions = json.loads((ROOT / DELIVERY_DEFINITIONS_PATH).read_text(encoding="utf-8"))
    delivery_assessments = {
        item["assessment_id"]: item for item in delivery_definitions["assessment_families"]
    }
    calibration_package = json.loads(
        (ROOT / DELIVERY_CALIBRATION_PACKAGE_PATH).read_text(encoding="utf-8")
    )
    calibration_exemplars = {
        item["exemplar_id"]: item for item in calibration_package["exemplars"]
    }

    records: list[dict[str, Any]] = []
    localizations: list[dict[str, Any]] = []

    def add_semantic(
        entity_type: str,
        identifier: str,
        record_state: str,
        localized: list[tuple[str, str, str]],
        **fields: Any,
    ) -> dict[str, Any]:
        loc_ids: list[str] = []
        for field, text, text_format in localized:
            loc_id = localization_id(identifier, field)
            loc_ids.append(loc_id)
            localizations.append(
                {
                    "entity_type": "localized_text",
                    "field": field,
                    "format": text_format,
                    "id": loc_id,
                    "language": "id",
                    "locale": "id-ID",
                    "rights_id": "O017-RIGHTS-ORIGINAL-TEXT",
                    "schema": LOCALIZATION_SCHEMA,
                    "subject_id": identifier,
                    "text": text,
                }
            )
        record = {
            "entity_type": entity_type,
            "id": identifier,
            "localization_ids": loc_ids,
            "record_state": record_state,
            "rights_id": "O017-RIGHTS-GENERATED-DATA",
            "schema": SEMANTIC_SCHEMA,
            **fields,
        }
        records.append(record)
        return record

    outcome_ids_by_unit: dict[int, list[str]] = {}
    for unit, parsed in parsed_units.items():
        comp_id = f"O017-COMP-U{unit:02d}"
        outcome_ids: list[str] = []
        for sequence, text in enumerate(parsed["outcomes"], 1):
            outcome_id = f"O017-LO-U{unit:02d}-{sequence:02d}"
            outcome_ids.append(outcome_id)
            add_semantic(
                "learning_outcome",
                outcome_id,
                "active",
                [("description", text, "markdown_inline")],
                competency_ids=[comp_id],
                locators=[
                    {
                        "canonical_identity": False,
                        "fragment": parsed["outcomes_fragment"],
                        "path": parsed["path"],
                        "role": "outcomes_section",
                        "surface": "source_qmd",
                    }
                ],
                sequence=sequence,
                unit_id=f"O017-U{unit:02d}",
            )
        outcome_ids_by_unit[unit] = outcome_ids

    unit_assessment_specs: list[dict[str, Any]] = []
    for unit, parsed in parsed_units.items():
        slug = f"U{unit:02d}-COMPLETION" if unit < 9 else "U09-CAPSTONE"
        assessment_id = f"O017-ASMT-{slug}"
        locators = [
            {
                "canonical_identity": False,
                "fragment": parsed["completion_fragment"],
                "path": parsed["path"],
                "role": "assessment_prompt",
                "surface": "source_qmd",
            }
        ]
        if parsed["rubric_fragment"]:
            locators.append(
                {
                    "canonical_identity": False,
                    "fragment": parsed["rubric_fragment"],
                    "path": parsed["path"],
                    "role": "rubric",
                    "surface": "source_qmd",
                }
            )
        unit_assessment_specs.append(
            {
                "slug": slug,
                "id": assessment_id,
                "label": f"Penyelesaian Unit {unit}" if unit < 9 else "Capstone O017",
                "description": f"Penilaian yang diterbitkan dalam {parsed['title']}.",
                "instructions": "Gunakan prompt, bukti, gerbang wajib, dan rubrik pada lokator sumber yang terikat pada rekaman ini.",
                "kind": "coursebook_unit_completion" if unit < 9 else "coursebook_capstone",
                "authenticity": "bounded_local_or_synthetic",
                "competency_units": [unit],
                "outcome_ids": outcome_ids_by_unit[unit],
                "evaluator_roles": ["COURSE-ASSESSOR"],
                "completion_modes": ["coursebook_local"],
                "external_authority": "not_applicable",
                "calibration_required": False,
                "locators": locators,
                "rubric_source": parsed["rubric"],
            }
        )

    authentic_specs: list[dict[str, Any]] = []
    for spec in AUTHENTIC_ASSESSMENTS:
        copied = dict(spec)
        copied["id"] = f"O017-ASMT-{spec['slug']}"
        copied["kind"] = "authentic_delivery"
        copied["outcome_ids"] = sorted(
            {outcome for unit in spec["competency_units"] for outcome in outcome_ids_by_unit[unit]}
        )
        copied["calibration_required"] = True
        delivery_id, calibration_id, assessment_fragment = DELIVERY_BINDINGS[spec["slug"]]
        if delivery_id not in delivery_assessments:
            fail(f"delivery assessment binding missing: {delivery_id}")
        if calibration_id not in calibration_exemplars:
            fail(f"calibration exemplar binding missing: {calibration_id}")
        if calibration_exemplars[calibration_id]["assessment_id"] != delivery_id:
            fail(f"calibration/assessment binding mismatch: {calibration_id}")
        copied["locators"] = [
            {
                "canonical_identity": False,
                "fragment": assessment_fragment,
                "path": DELIVERY_WRAPPER_PATH,
                "role": "assessment_prompt",
                "surface": "delivery_qmd",
            },
            {
                "canonical_identity": False,
                "fragment": "o017-wrap-gates",
                "path": DELIVERY_WRAPPER_PATH,
                "role": "rubric",
                "surface": "delivery_qmd",
            },
            {
                "canonical_identity": False,
                "fragment": "o017-wrap-calibration-sources",
                "path": DELIVERY_WRAPPER_PATH,
                "role": "calibration_exemplar",
                "surface": "delivery_qmd",
            },
            {
                "canonical_identity": False,
                "fragment": "o017-wrap-machine-package",
                "path": DELIVERY_WRAPPER_PATH,
                "role": "form_template",
                "surface": "delivery_qmd",
            },
        ]
        copied["delivery_definition_id"] = delivery_id
        copied["calibration_exemplar_id"] = calibration_id
        authentic_specs.append(copied)

    assessment_specs = unit_assessment_specs + authentic_specs
    assessment_ids_for_competency: dict[int, list[str]] = {unit: [] for unit in UNIT_FILES}
    for spec in assessment_specs:
        for unit in spec["competency_units"]:
            assessment_ids_for_competency[unit].append(spec["id"])

    for unit, (code, label, description) in COMPETENCIES.items():
        add_semantic(
            "competency",
            f"O017-COMP-U{unit:02d}",
            "active",
            [("label", label, "plain_text"), ("description", description, "plain_text")],
            assessment_ids=sorted(assessment_ids_for_competency[unit]),
            domain_code=code,
            outcome_ids=outcome_ids_by_unit[unit],
            unit_id=f"O017-U{unit:02d}",
        )

    for slug, code, label, description, independence, same_person in EVALUATOR_ROLES:
        add_semantic(
            "evaluator",
            f"O017-EVALUATOR-ROLE-{slug}",
            "role_definition",
            [("label", label, "plain_text"), ("description", description, "plain_text")],
            independence=independence,
            privacy_preserving_id_allowed=True,
            role_code=code,
            same_person_as_learner_allowed=same_person,
        )

    all_assessment_ids: list[str] = []
    for spec in assessment_specs:
        assessment_id = spec["id"]
        slug = spec["slug"]
        rubric_id = f"O017-RUBRIC-{slug}"
        submission_id = f"O017-SUBMISSION-TEMPLATE-{slug}"
        attempt_id = f"O017-ATTEMPT-TEMPLATE-{slug}"
        result_id = f"O017-RESULT-TEMPLATE-{slug}"
        comp_ids = [f"O017-COMP-U{unit:02d}" for unit in spec["competency_units"]]
        evaluator_ids = [f"O017-EVALUATOR-ROLE-{role}" for role in spec["evaluator_roles"]]

        if spec["kind"].startswith("coursebook"):
            rubric_source = spec["rubric_source"]
            raw_criteria = [
                (name, text, False, False, False, False)
                for name, text in rubric_source["criteria"]
            ]
        else:
            rubric_source = None
            raw_criteria = spec["criteria"]

        criterion_ids = [f"O017-CRIT-{slug}-{index:02d}" for index in range(1, len(raw_criteria) + 1)]
        evidence_ids = [f"O017-EVIDENCE-{slug}-{index:02d}" for index in range(1, len(raw_criteria) + 1)]

        add_semantic(
            "assessment",
            assessment_id,
            "active",
            [
                ("label", spec["label"], "plain_text"),
                ("description", spec["description"], "plain_text"),
                ("instructions", spec["instructions"], "plain_text"),
            ],
            assessment_kind=spec["kind"],
            attempt_template_id=attempt_id,
            authenticity=spec["authenticity"],
            calibration_exemplar_required=spec["calibration_required"],
            competency_ids=comp_ids,
            completion_modes=spec["completion_modes"],
            evaluator_role_ids=evaluator_ids,
            evidence_spec_ids=evidence_ids,
            external_action_authority=spec["external_authority"],
            locators=spec["locators"],
            noncompensable=True,
            outcome_ids=spec["outcome_ids"],
            required=True,
            result_template_id=result_id,
            rubric_id=rubric_id,
            submission_template_id=submission_id,
        )

        if rubric_source and "scoring" in rubric_source:
            scoring = rubric_source["scoring"]
            pass_rule = rubric_source["pass_rule"]
        elif rubric_source:
            scoring = {
                "mandatory_revision_overrides_total": True,
                "maximum_total": rubric_source["maximum"],
                "minimum_total": rubric_source["minimum"],
                "mode": "numeric_threshold_with_gates",
                "required_full_score_criterion_ids": [
                    criterion_ids[index - 1] for index in rubric_source["required_ordinals"]
                ],
                "scale": [0, 1, 2],
            }
            pass_rule = rubric_source["pass_rule"]
        else:
            scoring = {"mode": "binary_all_required", "passing_value": "met"}
            pass_rule = "Semua kriteria wajib harus berstatus terpenuhi; satu kriteria yang belum terpenuhi mewajibkan revisi."

        add_semantic(
            "rubric",
            rubric_id,
            "active",
            [
                ("label", f"Rubrik — {spec['label']}", "plain_text"),
                ("pass_rule", pass_rule, "markdown_inline"),
            ],
            assessment_id=assessment_id,
            criterion_ids=criterion_ids,
            locators=[locator for locator in spec["locators"] if locator["role"] == "rubric"],
            scoring=scoring,
        )

        for index, (criterion_label, criterion_text, timestamp, hash_required, independent, external) in enumerate(raw_criteria, 1):
            criterion_id = criterion_ids[index - 1]
            evidence_id = evidence_ids[index - 1]
            numeric = spec["kind"].startswith("coursebook") and rubric_source and "minimum" in rubric_source
            add_semantic(
                "criterion",
                criterion_id,
                "active",
                [
                    ("label", criterion_label, "plain_text"),
                    ("criterion_text", criterion_text, "markdown_inline"),
                ],
                evidence_spec_ids=[evidence_id],
                passing_threshold=2 if numeric else "met",
                required=True,
                rubric_id=rubric_id,
                scoring_mode="numeric_0_2" if numeric else "binary",
                sequence=index,
            )
            add_semantic(
                "evidence",
                evidence_id,
                "template",
                [
                    ("label", f"Bukti untuk {criterion_label}", "plain_text"),
                    ("description", criterion_text, "markdown_inline"),
                ],
                accepted_media_types=["application/json", "text/markdown", "text/plain"],
                assessment_id=assessment_id,
                criterion_id=criterion_id,
                evidence_code=f"{slug.replace('-', '_')}_{index:02d}",
                evidence_scope=(
                    "external_event" if external else "independent_evaluation" if independent else "learner_submission"
                ),
                external_event_required=external,
                hash_required=hash_required,
                independent_check_required=independent,
                required=True,
                timestamp_required=timestamp,
            )

        add_semantic(
            "submission",
            submission_id,
            "template",
            [
                ("label", f"Paket penyerahan — {spec['label']}", "plain_text"),
                ("instructions", "Gunakan ID upaya dan bukti yang baru; pertahankan semua versi terdahulu dan jangan menimpa artefak atau status.", "plain_text"),
            ],
            assessment_id=assessment_id,
            external_action_authority=spec["external_authority"],
            locators=[locator for locator in spec["locators"] if locator["role"] == "form_template"],
            preserves_prior_versions=True,
            required_evidence_spec_ids=evidence_ids,
            submission_statuses=["draft", "prepared", "submitted", "withdrawn", "superseded"],
        )
        add_semantic(
            "attempt",
            attempt_id,
            "template",
            [
                ("label", f"Upaya penilaian — {spec['label']}", "plain_text"),
                ("instructions", "Catat upaya sebagai peristiwa baru, hubungkan penyerahan dan penilai, dan pertahankan revisi serta masalah yang belum selesai.", "plain_text"),
            ],
            assessment_id=assessment_id,
            attempt_statuses=["not_started", "in_progress", "submitted_for_evaluation", "revision_required", "passed", "failed", "withheld"],
            evaluator_role_ids=evaluator_ids,
            preserves_attempt_history=True,
            requires_independent_evaluation=(spec["kind"] == "authentic_delivery"),
            submission_template_id=submission_id,
        )
        result_statuses = ["not_evaluated", "revise", "pass", "fail", "withheld"]
        if slug == "BOUNDED-COMMUNITY-TRANSACTION":
            result_statuses += ["prepared", "submitted", "acknowledged", "accepted", "merged", "published", "rejected", "withdrawn", "unknown", "externally_reviewed_local"]
        add_semantic(
            "result",
            result_id,
            "template",
            [
                ("label", f"Hasil penilaian — {spec['label']}", "plain_text"),
                ("instructions", "Simpan status, penilai, dasar rubrik, bukti, dan masalah yang belum selesai; status eksternal harus mempunyai bukti peristiwa.", "plain_text"),
            ],
            allowed_result_statuses=result_statuses,
            assessment_id=assessment_id,
            attempt_template_id=attempt_id,
            preserves_unresolved_items=True,
            requires_evaluator_identity=True,
            rubric_id=rubric_id,
        )
        all_assessment_ids.append(assessment_id)

    credential_states = [
        {
            "slug": "NOT-EVALUATED",
            "code": "NOT_EVALUATED",
            "label": "Belum dinilai",
            "description": "Tidak ada klaim penyelesaian atau partisipasi.",
            "terminal": False,
            "external": False,
            "required": [],
            "statuses": [],
            "predecessors": [],
        },
        {
            "slug": "IN-PROGRESS",
            "code": "IN_PROGRESS",
            "label": "Sedang berlangsung",
            "description": "Sedikitnya satu upaya telah dimulai, tetapi seluruh gerbang wajib belum ditutup.",
            "terminal": False,
            "external": False,
            "required": [],
            "statuses": [],
            "predecessors": ["NOT-EVALUATED"],
        },
        {
            "slug": "COURSEWORK-COMPLETE-BOUNDARY-OPEN",
            "code": "COURSEWORK_COMPLETE_BOUNDARY_OPEN",
            "label": "Kursus lokal selesai; batas eksternal masih terbuka",
            "description": "Semua pekerjaan selain jalur transaksi atau penelaahan alternatif selesai; tidak ada klaim partisipasi komunitas.",
            "terminal": False,
            "external": False,
            "required": [item for item in all_assessment_ids if not item.endswith("BOUNDED-COMMUNITY-TRANSACTION")],
            "statuses": ["pass"],
            "predecessors": ["IN-PROGRESS"],
        },
        {
            "slug": "COMPLETE-EXTERNALLY-REVIEWED-LOCAL",
            "code": "COMPLETE_EXTERNALLY_REVIEWED_LOCAL",
            "label": "Selesai melalui penelaahan lokal independen",
            "description": "Seluruh penilaian wajib lulus dan paket sumber nyata telah dinilai independen secara lokal; keadaan ini tidak mengklaim pengiriman atau partisipasi komunitas.",
            "terminal": True,
            "external": False,
            "required": all_assessment_ids,
            "statuses": ["pass", "externally_reviewed_local"],
            "predecessors": ["COURSEWORK-COMPLETE-BOUNDARY-OPEN", "IN-PROGRESS"],
        },
        {
            "slug": "COMPLETE-COMMUNITY-TRANSACTION-EVIDENCED",
            "code": "COMPLETE_COMMUNITY_TRANSACTION_EVIDENCED",
            "label": "Selesai dengan transaksi komunitas berbukti",
            "description": "Seluruh penilaian wajib lulus dan satu transaksi eksternal berwenang mempunyai bukti peristiwa; keadaan ini tidak menyatakan penerimaan kecuali status penerimaan sendiri dibuktikan.",
            "terminal": True,
            "external": True,
            "required": all_assessment_ids,
            "statuses": ["pass", "submitted", "acknowledged", "accepted", "merged", "published", "rejected", "withdrawn"],
            "predecessors": ["COURSEWORK-COMPLETE-BOUNDARY-OPEN", "IN-PROGRESS"],
        },
        {
            "slug": "WITHHELD",
            "code": "WITHHELD",
            "label": "Kredensial ditahan",
            "description": "Bukti tidak cukup, tidak konsisten, tidak berwenang, atau belum dapat diaudit; tidak ada klaim penyelesaian.",
            "terminal": False,
            "external": False,
            "required": [],
            "statuses": ["withheld"],
            "predecessors": ["IN-PROGRESS", "COURSEWORK-COMPLETE-BOUNDARY-OPEN"],
        },
    ]
    for state in credential_states:
        add_semantic(
            "credential_state",
            f"O017-CREDENTIAL-STATE-{state['slug']}",
            "state_definition",
            [("state_label", state["label"], "plain_text"), ("description", state["description"], "plain_text")],
            claims_external_participation=state["external"],
            external_event_required=state["external"],
            predecessor_state_ids=[f"O017-CREDENTIAL-STATE-{slug}" for slug in state["predecessors"]],
            required_assessment_ids=state["required"],
            required_result_statuses=state["statuses"],
            state_code=state["code"],
            terminal=state["terminal"],
        )

    records.sort(key=lambda item: item["id"])
    localizations.sort(key=lambda item: item["id"])

    relations: list[tuple[str, str, str, str]] = []

    def relate(source: str, predicate: str, target: str, evidence_kind: str = "semantic-wrapper-structure") -> None:
        row = (source, predicate, target, evidence_kind)
        if row not in relations:
            relations.append(row)

    for record in records:
        identifier = record["id"]
        for loc_id in record["localization_ids"]:
            relate(identifier, "localized-by", loc_id)
        kind = record["entity_type"]
        if kind == "learning_outcome":
            relate("O017-D120", "has-learning-outcome", identifier, "published-source-extraction")
            relate(record["unit_id"], "has-learning-outcome", identifier, "published-source-extraction")
            for target in record["competency_ids"]:
                relate(identifier, "aligns-to", target, "published-source-extraction")
        elif kind == "competency":
            relate(record["unit_id"], "develops", identifier)
            for target in record["assessment_ids"]:
                relate(identifier, "assessed-by", target)
        elif kind == "assessment":
            evidence_kind = "selected-delivery-architecture" if record["assessment_kind"] == "authentic_delivery" else "published-source-extraction"
            relate("O017-D120", "requires-assessment", identifier, evidence_kind)
            relate(identifier, "governed-by", record["rubric_id"], evidence_kind)
            relate(identifier, "accepts-submission", record["submission_template_id"])
            relate(identifier, "uses-attempt-template", record["attempt_template_id"])
            relate(identifier, "uses-result-template", record["result_template_id"])
            for target in record["competency_ids"]:
                relate(identifier, "measures", target, evidence_kind)
            for target in record["outcome_ids"]:
                relate(identifier, "measures-outcome", target, evidence_kind)
            for target in record["evaluator_role_ids"]:
                relate(identifier, "permits-evaluator-role", target, evidence_kind)
            for target in record["evidence_spec_ids"]:
                relate(identifier, "requires-evidence", target, evidence_kind)
        elif kind == "rubric":
            for target in record["criterion_ids"]:
                relate(identifier, "has-criterion", target)
        elif kind == "criterion":
            for target in record["evidence_spec_ids"]:
                relate(identifier, "requires-evidence", target)
        elif kind == "submission":
            relate(identifier, "submission-for", record["assessment_id"])
        elif kind == "attempt":
            relate(identifier, "attempt-for", record["assessment_id"])
            relate(identifier, "uses-submission-template", record["submission_template_id"])
            for target in record["evaluator_role_ids"]:
                relate(identifier, "evaluated-by-role", target)
        elif kind == "evidence":
            relate(identifier, "evidence-for", record["criterion_id"])
        elif kind == "result":
            relate(identifier, "result-for", record["assessment_id"])
            relate(identifier, "evaluates-attempt", record["attempt_template_id"])
            relate(identifier, "uses-rubric", record["rubric_id"])
        elif kind == "credential_state":
            for target in record["predecessor_state_ids"]:
                relate(target, "may-transition-to", identifier, "credential-state-policy")
            for target in record["required_assessment_ids"]:
                relate(identifier, "requires-passed-assessment", target, "credential-state-policy")

    relations.sort(key=lambda item: (item[0], item[1], item[2], item[3]))

    # These crosswalks are deliberately issued after the already frozen core
    # wrapper graph.  The extension therefore appends to the relation ledger
    # without renumbering or rewriting any previously issued wrapper row.
    integration_relations: list[tuple[str, str, str, str]] = []
    for spec in authentic_specs:
        delivery_id = spec["delivery_definition_id"]
        delivery_definition = delivery_assessments[delivery_id]
        integration_relations.append(
            (spec["id"], "implemented-by-delivery-definition", delivery_id, "delivery-definition-crosswalk")
        )
        integration_relations.append(
            (
                spec["id"],
                "has-calibration-exemplar",
                spec["calibration_exemplar_id"],
                "delivery-calibration-crosswalk",
            )
        )
        rubric_id = f"O017-RUBRIC-{spec['slug']}"
        for gate_id in delivery_definition["required_gate_ids"]:
            integration_relations.append(
                (rubric_id, "incorporates-delivery-gate", gate_id, "delivery-definition-crosswalk")
            )
        evidence_type_ids = list(delivery_definition["required_evidence_type_ids"])
        evidence_type_ids.extend(delivery_definition.get("community_transaction_additional_evidence", []))
        evidence_type_ids.extend(delivery_definition.get("externally_reviewed_local_additional_evidence", []))
        for evidence_type_id in sorted(set(evidence_type_ids)):
            integration_relations.append(
                (
                    spec["id"],
                    "requires-delivery-evidence-type",
                    evidence_type_id,
                    "delivery-definition-crosswalk",
                )
            )
    seen_triples = {(source, predicate, target) for source, predicate, target, _ in relations}
    for relation in sorted(integration_relations, key=lambda item: (item[0], item[1], item[2], item[3])):
        triple = relation[:3]
        if triple in seen_triples:
            fail(f"duplicate delivery integration triple: {triple}")
        seen_triples.add(triple)
        relations.append(relation)

    relation_rows = []
    for index, (source, predicate, target, evidence_kind) in enumerate(relations, 1):
        relation_rows.append(
            {
                "id": f"O017-WRAP-REL-{index:04d}",
                "source": source,
                "predicate": predicate,
                "target": target,
                "status": "active",
                "evidence_kind": evidence_kind,
                "superseded_by": "",
                "correction_id": "",
            }
        )

    records_payload = b"".join(canonical_json(record) for record in records)
    localizations_payload = b"".join(canonical_json(record) for record in localizations)
    relation_stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        relation_stream,
        fieldnames=["id", "source", "predicate", "target", "status", "evidence_kind", "superseded_by", "correction_id"],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(relation_rows)
    relations_payload = relation_stream.getvalue().encode("utf-8")

    payloads = {
        RECORDS_PATH.relative_to(ROOT).as_posix(): records_payload,
        LOCALIZATIONS_PATH.relative_to(ROOT).as_posix(): localizations_payload,
        RELATIONS_PATH.relative_to(ROOT).as_posix(): relations_payload,
    }
    file_entries = [
        {
            "path": path,
            "bytes": len(payload),
            "sha256": sha256_bytes(payload),
        }
        for path, payload in sorted(payloads.items())
    ]
    entity_counts = dict(sorted(Counter(record["entity_type"] for record in records).items()))
    dataset = {
        "schema": DATASET_SCHEMA,
        "model_version": MODEL_VERSION,
        "release_version": RELEASE_VERSION,
        "schema_path": SCHEMA_PATH.relative_to(ROOT).as_posix(),
        "schema_sha256": sha256_bytes(SCHEMA_PATH.read_bytes()),
        "baseline_path": BASELINE_PATH.relative_to(ROOT).as_posix(),
        "baseline_sha256": sha256_bytes(BASELINE_PATH.read_bytes()),
        "source_inputs": sorted(source_inputs, key=lambda item: item["path"]),
        "files": file_entries,
        "counts": {
            "semantic_records": len(records),
            "localized_text_records": len(localizations),
            "wrapper_relations_issued": len(relation_rows),
            "by_entity_type": entity_counts,
            "learning_outcomes": sum(len(values) for values in outcome_ids_by_unit.values()),
            "coursebook_assessments": len(unit_assessment_specs),
            "authentic_delivery_assessments": len(authentic_specs),
            "learner_submission_instances": 0,
            "learner_attempt_instances": 0,
            "learner_result_instances": 0,
            "credential_assertion_instances": 0,
        },
        "identity_policy": {
            "semantic_ids_are_locale_neutral": True,
            "localized_text_requires_locale_and_language": True,
            "renderer_fragments_are_noncanonical_locators": True,
            "html_fragment_is_forbidden_on_semantic_records": True,
        },
        "relation_policy": {
            "existing_ledger_path": "backend/relations-ledger.csv",
            "existing_ledger_mutated": False,
            "wrapper_ledger_path": RELATIONS_PATH.relative_to(ROOT).as_posix(),
            "wrapper_ledger_is_append_only": True,
        },
        "claim_boundary": {
            "contains_learner_completion_evidence": False,
            "contains_learner_credential_claims": False,
            "records_are_definitions_and_templates_only": True,
        },
        "delivery_integration": {
            "definition_set_id": delivery_definitions["definition_set_id"],
            "delivery_schema_id": delivery_definitions["schema_id"],
            "calibration_package_id": calibration_package["package_id"],
            "assessment_crosswalks": {
                spec["id"]: {
                    "delivery_definition_id": spec["delivery_definition_id"],
                    "calibration_exemplar_id": spec["calibration_exemplar_id"],
                }
                for spec in authentic_specs
            },
            "renderer_fragments_are_locators_only": True,
        },
    }
    dataset_payload = canonical_json(dataset, pretty=True)
    payloads[DATASET_PATH.relative_to(ROOT).as_posix()] = dataset_payload
    return payloads, dataset


def verify_baseline(baseline: dict[str, Any]) -> None:
    for relative, expected in baseline["files"].items():
        path = ROOT / relative
        payload = path.read_bytes()
        if relative == "backend/records.jsonl":
            continue
        if len(payload) != expected["bytes"] or sha256_bytes(payload) != expected["sha256"]:
            fail(f"baseline mismatch: {relative}")

    records = [json.loads(line) for line in (ROOT / "backend/records.jsonl").read_text(encoding="utf-8").splitlines()]
    record_expected = baseline["files"]["backend/records.jsonl"]
    ids_payload = ("\n".join(sorted(record["id"] for record in records)) + "\n").encode("utf-8")
    if len(records) != record_expected["record_count"] or sha256_bytes(ids_payload) != record_expected["id_set_sha256"]:
        fail("baseline record identity set mismatch")

    stable_projection = [
        {
            key: value
            for key, value in record.items()
            if key not in PERMITTED_BASELINE_RECORD_DELTAS.get(record["id"], frozenset())
        }
        for record in sorted(records, key=lambda item: item["id"])
    ]
    stable_payload = b"".join(canonical_json(record) for record in stable_projection)
    if sha256_bytes(stable_payload) != HISTORICAL_STABLE_RECORD_PROJECTION_SHA256:
        fail("a backend record changed outside the explicitly permitted release-specific fields")

    records_by_id = {record["id"]: record for record in records}
    edition = records_by_id["O017-EDITION-01"]
    if (
        edition.get("version") != CURRENT_EDITION_VERSION
        or edition.get("admission_evidence") != CURRENT_ADMISSION_EVIDENCE
    ):
        fail("backend edition record does not identify the current release")
    if (
        records_by_id["O017-U01-THEOREM-01"].get("title")
        != "Ketunggalan pohon merentang minimum"
    ):
        fail("backend theorem title does not preserve the frozen terminology correction")
    for unit, filename in UNIT_FILES.items():
        record_id = f"O017-U{unit:02d}-ARTIFACT-HTML"
        html_path = ROOT / "build" / "html" / "units" / filename.replace(".qmd", ".html")
        if not html_path.is_file():
            fail(f"current rendered unit artifact is missing: {html_path.relative_to(ROOT).as_posix()}")
        if records_by_id[record_id].get("sha256") != sha256_bytes(html_path.read_bytes()):
            fail(f"backend artifact hash is stale for {record_id}")

    with (ROOT / "backend/relations-ledger.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    relation_expected = baseline["files"]["backend/relations-ledger.csv"]
    relation_ids_payload = ("\n".join(sorted(row["id"] for row in rows)) + "\n").encode("utf-8")
    issued_map_payload = "".join(
        f"{row['id']}\t{row['source']}\t{row['predicate']}\t{row['target']}\t{row['status']}\n"
        for row in sorted(rows, key=lambda item: item["id"])
    ).encode("utf-8")
    if (
        len(rows) != relation_expected["relation_count"]
        or sha256_bytes(relation_ids_payload) != relation_expected["id_set_sha256"]
        or sha256_bytes(issued_map_payload) != relation_expected["issued_map_sha256"]
    ):
        fail("baseline relation identity/triple map mismatch")


def parse_relation_payload(payload: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8"))))


def write_or_check(payloads: dict[str, bytes], *, check: bool) -> None:
    for relative, payload in payloads.items():
        path = ROOT / relative
        if check:
            if not path.exists() or path.read_bytes() != payload:
                fail(f"generated artifact differs or is missing: {relative}")
            continue

        if path == RELATIONS_PATH and path.exists():
            existing = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
            expected = parse_relation_payload(payload)
            if existing != expected[: len(existing)]:
                fail("append-only wrapper relation ledger prefix differs; issue a new schema/data version")
            if len(existing) == len(expected):
                continue
            if len(existing) > len(expected):
                fail("append-only wrapper relation ledger has more issued rows than generator")
            with path.open("a", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=["id", "source", "predicate", "target", "status", "evidence_kind", "superseded_by", "correction_id"],
                    lineterminator="\n",
                )
                writer.writerows(expected[len(existing) :])
            continue

        # These are deterministic materialized views of this script and the
        # frozen inputs.  They may be refreshed byte-for-byte; only issued
        # relation rows are append-only and handled by the branch above.
        if not path.exists() or path.read_bytes() != payload:
            path.write_bytes(payload)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="compare generated bytes without writing")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payloads, dataset = build_payloads()
    write_or_check(payloads, check=args.check)
    mode = "CHECK" if args.check else "WRITE"
    print(
        f"PASS {mode}: {dataset['counts']['semantic_records']} semantic records, "
        f"{dataset['counts']['localized_text_records']} localized records, "
        f"{dataset['counts']['wrapper_relations_issued']} wrapper relations"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
