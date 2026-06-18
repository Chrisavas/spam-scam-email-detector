"""
responder.py — Generative AI Scam Responder
Αρμόδιο άτομο: Άτομο 3

Παράγει αυτόματες απαντήσεις σε scam emails
με σκοπό να κρατάει τον scammer απασχολημένο.

Υποστηρίζει multi-turn συνομιλία.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Scam type detection keywords ──
SCAM_TYPES = {
    "nigerian_prince": [
        "prince", "nigeria", "inheritance", "next of kin",
        "million dollars", "dying", "widow", "transfer funds",
    ],
    "lottery": [
        "lottery", "winner", "prize", "claim", "selected",
        "winning ticket", "congratulations",
    ],
    "romance": [
        "beloved", "my dear", "i love you", "lonely", "meet",
        "send money", "stranded", "emergency",
    ],
    "investment": [
        "investment", "profit", "returns", "trading", "crypto",
        "double your money", "guaranteed returns",
    ],
}

# ── System prompt για τον AI ──
SYSTEM_PROMPT = """You are playing the role of an extremely gullible, 
enthusiastic, but also wonderfully confused person responding to scam emails.

Your goal is to:
1. Sound genuinely interested and excited
2. Ask lots of questions that waste the scammer's time
3. Invent ridiculous personal details and complications
4. Never send money, but ALWAYS seem like you're about to
5. Keep the scammer engaged with absurd but believable excuses

Rules:
- Never reveal you know it's a scam
- Be hilariously incompetent (wrong bank details, confuse currencies, etc.)
- Add fictional family drama and complications
- Keep responses 100–200 words
- Sound like an elderly, technologically confused person
"""


def detect_scam_type(text: str) -> str:
    """Ανιχνεύει τον τύπο του scam για να προσαρμόσει την απάντηση."""
    text_lower = text.lower()
    scores = {}
    for scam_type, keywords in SCAM_TYPES.items():
        scores[scam_type] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "generic"


def get_type_context(scam_type: str) -> str:
    """Επιπλέον context για κάθε τύπο scam."""
    contexts = {
        "nigerian_prince": "You are excited about the inheritance. You keep mentioning your late husband Gerald who also had a Nigerian connection.",
        "lottery": "You are convinced you've won many lotteries before but never received the money. You think this one is finally real.",
        "romance": "You are a lonely widower who is very eager to meet someone. You have a complicated family situation with your nephew Kevin.",
        "investment": "You have $47 saved and want to invest it all. You keep confusing Bitcoin with 'Bitchoin' and ask about it repeatedly.",
        "generic": "You are a very confused elderly person who is very excited about this unexpected opportunity.",
    }
    return contexts.get(scam_type, contexts["generic"])


def generate_reply(
    scam_email: str,
    conversation_history: list = None,
    provider: str = None,
) -> dict:
    """
    Παράγει απάντηση στο scam email.

    Args:
        scam_email: Το τελευταίο email από τον scammer
        conversation_history: Λίστα από {"role": ..., "content": ...}
        provider: "anthropic" ή "openai" (default: από .env)

    Returns:
        dict με reply text, scam_type, updated history
    """
    if conversation_history is None:
        conversation_history = []

    provider = provider or os.getenv("AI_PROVIDER", "anthropic")
    scam_type = detect_scam_type(scam_email)
    type_context = get_type_context(scam_type)

    full_system = f"{SYSTEM_PROMPT}\n\nContext for this conversation: {type_context}"

    # Προσθήκη νέου μηνύματος στο history
    conversation_history.append({
        "role": "user",
        "content": f"[Scam email received]:\n{scam_email}"
    })

    if provider == "anthropic":
        reply = _call_anthropic(full_system, conversation_history)
    elif provider == "openai":
        reply = _call_openai(full_system, conversation_history)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    # Προσθήκη απάντησης στο history για multi-turn
    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    return {
        "reply": reply,
        "scam_type": scam_type,
        "turn": len([m for m in conversation_history if m["role"] == "assistant"]),
        "history": conversation_history,
    }


def _call_anthropic(system: str, messages: list) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=system,
        messages=messages,
    )
    return response.content[0].text


def _call_openai(system: str, messages: list) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    full_messages = [{"role": "system", "content": system}] + messages
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=300,
        messages=full_messages,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────
# Quick demo
# ─────────────────────────────────────────
if __name__ == "__main__":
    sample = """
    Dear Friend,
    I am Prince Adebayo from Nigeria. I have $15 million dollars
    that I need to transfer urgently. I need your help and will
    give you 30% for your assistance. Please reply immediately.
    """

    print("[*] Generating reply...\n")
    result = generate_reply(sample)

    print(f"Scam Type : {result['scam_type']}")
    print(f"Turn      : {result['turn']}")
    print(f"\n--- AI Reply ---\n{result['reply']}")
