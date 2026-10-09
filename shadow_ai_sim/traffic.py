import math
import random
from dataclasses import dataclass
from typing import List

from .config import (API_HOSTS, KNOWN_CHATBOTS, LONGTAIL_APPS, NON_AI_SITES,
                     SANCTIONED_HOST, SENSITIVE_KINDS, SENSITIVE_WEIGHTS, SimConfig)
from .payloads import make_payload


@dataclass(slots=True)
class Event:
    """One simulated proxy event."""
    user: int
    host: str
    is_ai: bool 
    is_shadow: bool      
    is_sanctioned: bool
    streaming: bool      
    is_post: bool
    bytes_up: int
    prompt_schema: bool    
    text: str              
    kind: str             


def _ai_destination(x: float, r: random.Random, cfg: SimConfig):
    """Map one uniform draw to (host, is_shadow). Draw order matters."""
    if x < cfg.mix_sanctioned:
        return SANCTIONED_HOST, False
    if x < cfg.mix_chatbot:
        return r.choice(KNOWN_CHATBOTS), True
    if x < cfg.mix_longtail:
        return r.choice(LONGTAIL_APPS), True
    if x < cfg.mix_api:
        return r.choice(API_HOSTS), True

    return "10.%d.%d.%d" % (r.randint(0, 255), r.randint(0, 255), r.randint(1, 254)), True


def generate_events(cfg: SimConfig, seed: int) -> List[Event]:
    """Generate `cfg.days` of traffic for `cfg.employees` employees."""
    r = random.Random(seed)
    events: List[Event] = []
    ai_users = {u for u in range(cfg.employees) if r.random() < cfg.ai_user_share}

    for u in range(cfg.employees):
        for _day in range(cfg.days):
            for _ in range(max(0, int(r.gauss(cfg.non_ai_events_mean, cfg.non_ai_events_sd)))):
                host = r.choice(NON_AI_SITES)
                streaming = r.random() < cfg.non_ai_streaming_prob
                is_post = r.random() < cfg.non_ai_post_prob
                bytes_up = int(math.exp(r.gauss(6.5, 1.6)))
                schema = r.random() < cfg.non_ai_prompt_schema_prob
                events.append(Event(u, host, False, False, False, streaming, is_post,
                                    bytes_up, schema, "", "none"))
            if u in ai_users:
                for _ in range(max(0, int(r.gauss(cfg.ai_events_mean, cfg.ai_events_sd)))):
                    host, shadow = _ai_destination(r.random(), r, cfg)
                    kind = r.choices(SENSITIVE_KINDS, SENSITIVE_WEIGHTS)[0]
                    streaming = r.random() < cfg.ai_streaming_prob
                    bytes_up = int(r.uniform(250, 40000))
                    schema = r.random() < cfg.ai_prompt_schema_prob
                    text = make_payload(kind, r)
                    events.append(Event(u, host, True, shadow, not shadow, streaming, True,
                                        bytes_up, schema, text, kind))
    return events
