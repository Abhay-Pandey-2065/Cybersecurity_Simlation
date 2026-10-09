from .config import CATALOGUE, M1_BLOCKLIST, SANCTIONED_HOST, SimConfig
from .traffic import Event

METHODS = ("M1", "M2", "M3")


def _suspicious_host(host: str) -> bool:
    """IP-literal destinations and unknown 'ai-tool*' style domains."""
    return host.startswith("10.") or host.startswith("ai-tool")


def heuristic_flag(e: Event, cfg: SimConfig) -> bool:
    """Behavioural evidence of AI use independent of the destination catalogue."""
    if e.prompt_schema:
        return True
    return (e.streaming and e.is_post
            and cfg.heuristic_min_body < e.bytes_up < cfg.heuristic_max_body
            and _suspicious_host(e.host))


def detect(e: Event, method: str, cfg: SimConfig) -> bool:
    """Return True if `method` flags the event as (shadow) AI traffic."""
    if e.host == SANCTIONED_HOST:       # sanctioned assistant is allow-listed
        return False
    if method == "M1":
        return e.host in M1_BLOCKLIST
    in_catalogue = e.host in CATALOGUE
    if method == "M2":
        return in_catalogue
    if method == "M3":
        return in_catalogue or heuristic_flag(e, cfg)
    raise ValueError(f"unknown method: {method!r}")
