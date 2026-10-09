from typing import Dict, List

from .config import SimConfig
from .detectors import METHODS, detect
from .dlp import dlp_hit
from .traffic import Event


def evaluate(events: List[Event], cfg: SimConfig) -> Dict:
    """Compute event-level precision/recall/F1 and sensitive-prompt coverage."""
    dlp = [dlp_hit(e.text) if e.text else False for e in events]   # computed once

    out: Dict = {
        "events": len(events),
        "shadow": sum(e.is_shadow for e in events),
    }
    sens = [i for i, e in enumerate(events) if e.is_shadow and e.kind != "none"]
    out["sens_shadow"] = len(sens)
    out["shadow_users"] = len({e.user for e in events if e.is_shadow})

    for m in METHODS:
        tp = fp = fn = sens_det = fp_dlp = 0
        users = set()
        for i, e in enumerate(events):
            flagged = detect(e, m, cfg)
            if flagged and e.is_shadow:
                tp += 1
                users.add(e.user)
            elif flagged and not e.is_shadow:
                fp += 1
            elif not flagged and e.is_shadow:
                fn += 1
            if flagged and e.is_shadow and e.kind != "none" and dlp[i]:
                sens_det += 1
            if flagged and e.is_ai and e.kind == "none" and dlp[i]:
                fp_dlp += 1
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn)
        f1 = 2 * precision * recall / (precision + recall)
        out[m] = dict(tp=tp, fp=fp, fn=fn, prec=precision, rec=recall, f1=f1,
                      users=len(users), sens_det=sens_det, fp_dlp=fp_dlp)

    out["dlp_ceiling"] = sum(1 for i in sens if dlp[i])
    out["dlp_total_fp"] = sum(1 for i, e in enumerate(events)
                              if e.is_shadow and e.kind == "none" and dlp[i])
    return out
