"""
transcript.py — Multi-turn Transcript Exporter
(supports the Task 6 demo & the Task 8 report: exporting conversations to markdown)

WHAT IT DOES:
  Takes the conversation_history returned by responder.generate_reply() and writes
  it out as clean markdown, ready to be included as an example in the report or
  the slides.

USAGE:
    from responder.responder import generate_reply
    from responder.transcript import export_markdown

    history = []
    for email in scam_emails:
        res = generate_reply(email, conversation_history=history, provider="mock")
        history = res["history"]
    export_markdown(history, "outputs/transcript_nigerian.md",
                    scam_type=res["scam_type"])
"""

import os
import re
from datetime import datetime


def _strip_tags(content: str) -> str:
    """
    Cleans up the internal service markers/tags so that the transcript reads
    nicely (removes '[Scam email received]:' and the <scam_email> tags).
    """
    content = content.replace("[Scam email received]:", "").strip()
    content = re.sub(r"</?scam_email>", "", content).strip()
    return content


def history_to_markdown(history: list, scam_type: str = "unknown",
                        title: str = "Scambaiting Transcript") -> str:
    """Converts the conversation_history into a markdown string (without writing a file)."""
    # Header + metadata (type, date, number of turns).
    lines = [
        f"# {title}",
        "",
        f"- **Scam type:** `{scam_type}`",
        f"- **Generated:** {datetime.now():%Y-%m-%d %H:%M}",
        f"- **Turns (our replies):** "
        f"{len([m for m in history if m.get('role') == 'assistant'])}",
        "",
        # Disclaimer — important for the academic/ethics framing.
        "> ⚠️ Academic scambaiting demo. All targets/content are simulated; "
        "no real personal data, money, or contact details are exchanged.",
        "",
        "---",
        "",
    ]

    # We walk through the history and print scammer / our reply alternately.
    turn = 0
    for msg in history:
        role = msg.get("role")
        body = _strip_tags(msg.get("content", ""))
        if role == "user":          # the scammer's message
            turn += 1
            lines += [f"### 🎯 Scammer — message {turn}", "", "```", body, "```", ""]
        elif role == "assistant":   # our (safe) reply
            lines += [f"### 🤖 Responder (our reply)", "", body, "", "---", ""]

    return "\n".join(lines)


def export_markdown(history: list, path: str, scam_type: str = "unknown",
                    title: str = "Scambaiting Transcript") -> str:
    """Writes the transcript to a markdown file and returns the path."""
    # Create the destination folder if it does not exist.
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    md = history_to_markdown(history, scam_type=scam_type, title=title)
    # encoding="utf-8" so that Greek characters/emoji are written correctly.
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[✓] Transcript saved: {path}")
    return path


if __name__ == "__main__":
    # Mini self-demo: produces a 3-turn transcript offline (mock provider).
    import sys
    # Add src/ to the path so that the responder package can be found.
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from responder.responder import generate_reply   # when run as a package
    except ModuleNotFoundError:
        from responder import generate_reply              # when run as a plain script

    emails = [
        "Dear Friend, I am Prince Adebayo from Nigeria with $15 million dollars "
        "to transfer. I will give you 30%. Reply urgently!",
        "Thank you! Please send your full name and bank account number to proceed.",
        "We need a $500 processing fee via Western Union to release the funds.",
    ]
    history, res = [], None
    for e in emails:
        res = generate_reply(e, conversation_history=history, provider="mock")
        history = res["history"]

    export_markdown(history, "outputs/transcript_demo.md",
                    scam_type=res["scam_type"])
