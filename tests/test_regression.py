import json
from pathlib import Path

from shadow_ai_sim.config import SimConfig
from shadow_ai_sim.runner import run_seed
from shadow_ai_sim.traffic import generate_events

GOLDEN = json.loads((Path(__file__).parent / "golden_seed11.json").read_text())


def test_same_seed_is_deterministic():
    cfg = SimConfig(employees=20, days=3)
    a = [(e.host, e.kind, e.text) for e in generate_events(cfg, 5)]
    b = [(e.host, e.kind, e.text) for e in generate_events(cfg, 5)]
    assert a == b


def test_default_run_matches_golden_results_for_seed_11():
    assert run_seed(SimConfig(), 11) == GOLDEN


def test_layer_ordering_holds():
    r = run_seed(SimConfig(employees=100, days=10), 3)
    assert r["M1"]["rec"] < r["M2"]["rec"] < r["M3"]["rec"]
    assert r["M1"]["sens_det"] <= r["M2"]["sens_det"] <= r["M3"]["sens_det"] <= r["dlp_ceiling"]
