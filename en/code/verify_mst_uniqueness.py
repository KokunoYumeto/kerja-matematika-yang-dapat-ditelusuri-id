"""Check a finite family related to uniqueness of minimum spanning trees.

The computation is evidence about K4 and one weighted triangle. It is not a
proof of the universal theorem. It enumerates spanning trees directly rather
than calling an MST implementation whose correctness uses the same theorem.
"""

from __future__ import annotations

from itertools import combinations, permutations
import json
from pathlib import Path


def is_tree(vertices: tuple[int, ...], edges: tuple[tuple[int, int, int], ...]) -> bool:
    parent = {vertex: vertex for vertex in vertices}

    def find(vertex: int) -> int:
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for left, right, _weight in edges:
        root_left, root_right = find(left), find(right)
        if root_left == root_right:
            return False
        parent[root_left] = root_right

    root = find(vertices[0])
    return len(edges) == len(vertices) - 1 and all(find(vertex) == root for vertex in vertices)


def minimum_spanning_trees(
    vertices: tuple[int, ...], edges: tuple[tuple[int, int, int], ...]
) -> tuple[int, list[tuple[tuple[int, int, int], ...]]]:
    trees = [
        subset
        for subset in combinations(edges, len(vertices) - 1)
        if is_tree(vertices, subset)
    ]
    best_weight = min(sum(weight for _left, _right, weight in tree) for tree in trees)
    best = [
        tree
        for tree in trees
        if sum(weight for _left, _right, weight in tree) == best_weight
    ]
    return best_weight, best


def main() -> None:
    vertices = (0, 1, 2, 3)
    pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    checked = 0
    violations = 0

    for weights in permutations(range(1, 7)):
        edges = tuple((left, right, weight) for (left, right), weight in zip(pairs, weights))
        _weight, best = minimum_spanning_trees(vertices, edges)
        checked += 1
        violations += len(best) != 1

    triangle = ((0, 1, 1), (1, 2, 1), (0, 2, 1))
    triangle_weight, tied_best = minimum_spanning_trees((0, 1, 2), triangle)

    result = {
        "schema": "o017-unit-01-mst-check-v1",
        "claim_tested": "Distinct edge weights imply a unique MST.",
        "logical_status": "finite computational evidence; not a proof",
        "k4_distinct_weight_assignments_checked": checked,
        "k4_uniqueness_violations": violations,
        "equal_weight_triangle_mst_count": len(tied_best),
        "equal_weight_triangle_minimum_weight": triangle_weight,
    }
    output = Path(__file__).resolve().parents[2] / "build" / "unit-01-mst-check.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"k4_distinct_weight_assignments_checked: {checked}")
    print(f"k4_uniqueness_violations: {violations}")
    print(f"equal_weight_triangle_mst_count: {len(tied_best)}")


if __name__ == "__main__":
    main()
