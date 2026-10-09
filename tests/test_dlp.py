import random

from shadow_ai_sim.dlp import dlp_hit, luhn_ok
from shadow_ai_sim.payloads import luhn_card, make_payload


def test_luhn_known_values():
    assert luhn_ok("4539578763621486")     
    assert not luhn_ok("4539578763621487")


def test_generated_cards_are_luhn_valid():
    r = random.Random(1)
    assert all(luhn_ok(luhn_card(r)) for _ in range(200))


def test_each_marked_class_is_detected():
    r = random.Random(2)
    for kind in ("secret", "card"):
        assert all(dlp_hit(make_payload(kind, r)) for _ in range(50))


def test_benign_text_is_not_flagged():
    assert not dlp_hit("Please translate this paragraph to Hindi.")
    assert not dlp_hit("Order 1234567890123456 shipped") 


def test_invoice_lookalike_is_a_known_false_positive():
    assert dlp_hit("Invoice 1234 5678 9012 please check.")
