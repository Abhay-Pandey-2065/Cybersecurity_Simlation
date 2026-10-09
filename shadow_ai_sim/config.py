#This Files Contains all the Assumptions for the Simulations, changing the values below will result in different outputs

import random
from dataclasses import dataclass, field
from typing import List, Tuple

KNOWN_CHATBOTS: List[str] = [
    "chatgpt.com", "claude.ai", "gemini.google.com", "copilot.microsoft.com",
    "perplexity.ai", "chat.deepseek.com", "poe.com", "character.ai",
]
API_HOSTS: List[str] = [
    "api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com",
    "api.deepseek.com", "api.mistral.ai",
]
SANCTIONED_HOST = "assistant.corp.example"
LONGTAIL_APPS: List[str] = [f"ai-tool-{i}.app" for i in range(120)]
NON_AI_SITES: List[str] = [f"site-{i}.com" for i in range(300)]

CATALOGUE_SEED = 7
CATALOGUE_LONGTAIL_COUNT = 66
VENDOR_FEED_LONGTAIL = frozenset(
    random.Random(CATALOGUE_SEED).sample(LONGTAIL_APPS, CATALOGUE_LONGTAIL_COUNT)
)

M1_BLOCKLIST = frozenset(KNOWN_CHATBOTS)
CATALOGUE = frozenset(KNOWN_CHATBOTS) | frozenset(API_HOSTS) | VENDOR_FEED_LONGTAIL

SENSITIVE_KINDS: List[str] = ["none", "secret", "id", "card", "code", "confidential"]
SENSITIVE_WEIGHTS: List[float] = [0.88, 0.02, 0.03, 0.01, 0.03, 0.03]

DEFAULT_SEEDS: Tuple[int, ...] = (11, 22, 33, 44, 55)


@dataclass(frozen=True)
class SimConfig:
    """Population, volume and traffic-mix parameters."""

    employees: int = 400
    days: int = 30
    ai_user_share: float = 0.62 

    non_ai_events_mean: float = 40.0 
    non_ai_events_sd: float = 8.0
    ai_events_mean: float = 4.0 
    ai_events_sd: float = 2.0

    mix_sanctioned: float = 0.25
    mix_chatbot: float = 0.63
    mix_longtail: float = 0.85
    mix_api: float = 0.95

    # Traffic-feature probabilities
    ai_streaming_prob: float = 0.85
    ai_prompt_schema_prob: float = 0.90
    non_ai_streaming_prob: float = 0.06
    non_ai_post_prob: float = 0.30
    non_ai_prompt_schema_prob: float = 0.004

    # Heuristic (M3) thresholds
    heuristic_min_body: int = 300
    heuristic_max_body: int = 60_000
