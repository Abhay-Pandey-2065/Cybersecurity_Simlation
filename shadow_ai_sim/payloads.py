import random

BASE = "Please summarise and improve the following text for me. "
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEY_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def luhn_card(r: random.Random) -> str:
    """Return a 16-digit string whose last digit is a valid Luhn check digit."""
    digits = [r.randint(0, 9) for _ in range(15)]
    total = 0
    for i, d in enumerate(reversed(digits)):
        d = d * 2 if i % 2 == 0 else d
        total += d - 9 if d > 9 else d
    return "".join(map(str, digits)) + str((10 - total % 10) % 10)


def make_payload(kind: str, r: random.Random) -> str:
    """Build a prompt of the given sensitivity class.

    kinds: none | secret | id | card | code | confidential
    Some sensitive prompts are deliberately hard to recognise (unmarked
    confidential text, code without internal package names) so that content
    inspection cannot reach 100 %.
    """
    if kind == "none":
        ticket = (f"Ticket ref {r.randint(10**11, 10**12 - 1)}."
                  if r.random() < 0.08 else "Explain this concept simply.")
        # Look-alike for national-ID patterns, to provoke DLP false positives.
        invoice = ("Invoice %04d %04d %04d please check."
                   % (r.randint(0, 9999), r.randint(0, 9999), r.randint(0, 9999))
                   if r.random() < 0.05 else "Translate to Hindi.")
        extra = r.choice([
            "Meeting agenda for Monday.",
            "Draft a polite email to a vendor.",
            ticket,
            "This is not confidential, it is a public blog post.",
            invoice,
        ])
    elif kind == "secret":
        extra = "config: aws_key=AKIA" + "".join(r.choice(KEY_ALPHABET) for _ in range(16))
    elif kind == "id":
        pan = "Customer PAN %s%04d%s" % (
            "".join(r.choice(UPPER) for _ in range(5)),
            r.randint(0, 9999),
            r.choice("ABCDEFGH"),
        )
        aadhaar = "Aadhaar %04d %04d %04d" % (
            r.randint(0, 9999), r.randint(0, 9999), r.randint(0, 9999))
        extra = r.choice([pan, aadhaar])
    elif kind == "card":
        extra = "Card on file: " + luhn_card(r)
    elif kind == "code":
        extra = (r.choice(["import com.acme.internal.billing.RateEngine; // fix this",
                           "class PaymentRouter extends acme_internal.Base:"])
                 if r.random() < 0.75
                 else "def route(x): return x.apply(rules)  # proprietary pricing logic")
    elif kind == "confidential":
        extra = ("CONFIDENTIAL - Acme Internal: Q3 acquisition shortlist ..."
                 if r.random() < 0.6
                 else "Our board is planning to acquire two smaller rivals next quarter ...")
    else:
        raise ValueError(f"unknown payload kind: {kind!r}")
    return BASE + extra
