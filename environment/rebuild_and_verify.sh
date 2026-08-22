#!/usr/bin/env bash
set -euo pipefail

project_root="${1:-/work}"
stage="$(mktemp -d /tmp/o017-rebuild.XXXXXXXX)"
trap 'rm -rf -- "$stage"' EXIT

test -f "$project_root/source/_quarto.yml"
test -f "$project_root/source/_quarto-pdf.yml"
cp -a -- "$project_root/source" "$stage/source"

python "$stage/source/code/verify_mst_uniqueness.py" > "$stage/mst.stdout"
diff -u "$stage/source/code/expected-output.txt" "$stage/mst.stdout"
python "$stage/source/code/u06_recurrence_witness.py" > "$stage/u06.stdout"
diff -u "$stage/source/code/u06-expected-output.txt" "$stage/u06.stdout"

(
  cd "$stage/source"
  quarto render
  quarto render --profile pdf --to pdf
)

python /opt/o017/verify_rebuild.py "$stage"
