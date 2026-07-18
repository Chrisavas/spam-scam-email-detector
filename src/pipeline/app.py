"""
app.py — Streamlit demo UI για το ScamAI pipeline
(Task 6: interactive οπτικοποίηση classifier -> responder -> multi-turn)

Τρέξε με: streamlit run src/pipeline/app.py

Χαρακτηριστικά UI:
  • Safety status badge ανά turn (λίστα issues + flag αν έγινε sanitize)
  • Λήψη transcript (markdown) από το sidebar
  • Scam-type badge με χρωματικό κωδικό
  • Multi-turn conversation panel (τρέχον + αρχείο παλαιών sessions)
"""

import sys
import os

# Adding  src/ in path in order the rest packages to be found
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from classifier.predict import predict_email
from responder.responder import generate_reply, detect_scam_type
from responder.transcript import history_to_markdown

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ScamAI — Scam Detector & Responder",
    page_icon="🛡️",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
.safety-badge-ok   { background:#1a7a1a; color:#fff; border-radius:6px;
                     padding:2px 10px; font-size:0.82em; font-weight:600; }
.safety-badge-warn { background:#7a4a00; color:#fff; border-radius:6px;
                     padding:2px 10px; font-size:0.82em; font-weight:600; }
.scam-badge        { background:#6b2fa0; color:#fff; border-radius:6px;
                     padding:2px 10px; font-size:0.82em; font-weight:600; }

[data-testid="stTooltipHoverTarget"] svg {
    display: none !important;
}
[data-testid="stTooltipHoverTarget"]::after {
    content: "ⓘ";
    font-size: 1.1em;
    vertical-align: middle;
    color: inherit;
    opacity: 0.8;
}
</style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align: center;'>ScamAI — Spam Detection & Scambaiting System</h1>", 
    unsafe_allow_html=True
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("logo_dark.png", width=200) 
    st.divider()
    st.header("⚙️ Settings")
    threshold = st.slider("Scam Detection Threshold", 0.1, 0.9, 0.5, 0.05,
                          help="Confidence above this → treat as scam")
    provider = st.selectbox(
        "AI Provider",
        ["mock", "anthropic", "openai", "gemini"],  # mock = offline default, χωρίς API key
        help="'mock' runs fully offline, 'gemini' is free!"
    )
    show_safety_details = st.checkbox("Show safety details", value=True,
                                      help="Display the output guardrail status per reply")
    st.divider()
    st.info("ℹ️ This tool is for academic research and defensive security purposes only.")

    # ── Transcript download ──
    st.divider()
    st.subheader("📄 Export Transcript")
    if st.session_state.get("history") and st.session_state.get("last_scam_type"):
        md = history_to_markdown(
            st.session_state["history"],
            scam_type=st.session_state["last_scam_type"],
        )
        st.download_button(
            label="⬇️ Download Transcript (.md)",
            data=md,
            file_name="scambaiting_transcript.md",
            mime="text/markdown",
        )
    else:
        st.caption("Run at least one scam analysis to export a transcript.")
        
    st.markdown("<br><br><br>", unsafe_allow_html=True) 
    st.caption("🎓 **MSc Project** | Advanced AI and Cybersecurity")

# ── Session state ─────────────────────────────────────────────────────────────
#  Streamlit re runs the script in every interaction· session_state
# keeps the state (history, turns, ενεργό session) between reruns.
if "history" not in st.session_state:
    st.session_state.history = []
if "turns" not in st.session_state:
    st.session_state.turns = []
if "last_scam_type" not in st.session_state:
    st.session_state.last_scam_type = None
# Θυμάται αν το session έχει ήδη χαρακτηριστεί scam (κρίσιμο για multi-turn)
if "active_scam_session" not in st.session_state:
    st.session_state.active_scam_session = False
if "past_sessions" not in st.session_state:
    st.session_state.past_sessions = []

# ── Main layout ───────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")


# ── Left: Email input ─────────────────────────────────────────────────────────
with col1:
    st.subheader("📧 Input Email")
    
    # ← Callback function
    def reset_email():
        st.session_state.email_input = ""
    
    email_text = st.text_area(
        "Paste email body here:",
        height=260,
        placeholder="Dear Beloved Friend, I am Prince Adebayo from Nigeria...",
        key="email_input"
    )

    col_a, col_b = st.columns(2)
    analyze_btn = col_a.button("🔍 Analyze", type="primary", use_container_width=True)
    reset_btn   = col_b.button("🔄 Reset Session", use_container_width=True, on_click=reset_email)  # ← on_click callback

    if reset_btn:
        if st.session_state.turns:
            st.session_state.past_sessions.append({
                "scam_type": st.session_state.last_scam_type,
                "turns": list(st.session_state.turns)
            })
        st.session_state.history = []
        st.session_state.turns   = []
        st.session_state.last_scam_type = None
        st.session_state.active_scam_session = False
        
        st.success("Session reset!")
        st.rerun()

# ── Right: Results ────────────────────────────────────────────────────────────
with col2:
    st.subheader("📊 Results")

    if not (analyze_btn and email_text.strip()):
        st.info(
            """
            ### 👋 Welcome to ScamAI!
            
            **How to use:**
            1. 📧 Paste an email in the left panel
            2. 🔍 Click "Analyze"
            3. 📊 View results here (classification, metrics, charts)
            4. 💬 Read the AI-generated response
            
            """
        )


    if analyze_btn and email_text.strip():

        # ── Step 1: Classification ──
        with st.spinner("Classifying email…"):
            clf_result = predict_email(email_text)

            is_scam    = clf_result["confidence"] >= threshold

        # When scam is detected, the session is locked as active. 
        # The next messages will recieve answer even if they seem  legit (multi-turn).
        if is_scam:
            st.session_state.active_scam_session = True

        if is_scam:
            st.error(f"🚨 SCAM DETECTED — {clf_result['confidence']:.1%} confidence")
            scam_type = detect_scam_type(email_text)
            st.markdown(
                f'<span class="scam-badge">🎭 {scam_type.replace("_", " ").title()}</span>',
                unsafe_allow_html=True,
            )
        else:
            st.success(f"✅ LEGITIMATE — {1 - clf_result['confidence']:.1%} legitimate confidence")
            # Ενημέρωση χρήστη: συνεχίζουμε τη συνομιλία λόγω ενεργού session
            if st.session_state.active_scam_session:
                st.warning("⚠️ This message looks legitimate, but we created a response because it belongs to a Scambaiting session!")

        # Feature breakdown
        with st.expander("🔎 Feature Breakdown"):
            feats = clf_result["features"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Scam Keywords",  feats["scam_keyword_count"])
            c2.metric("Money Mentions", feats["money_mentions"])
            c3.metric("CAPS Ratio",     f"{feats['caps_ratio']:.1%}")
            c4.metric("Exclamations",   feats["exclamation_count"])

        # ── Βήμα 2: Παραγωγή απάντησης ──
        # Απαντάμε αν είναι scam Ή αν το session είναι ήδη ενεργό (multi-turn).
        if is_scam or st.session_state.active_scam_session:
            st.divider()
            with st.spinner("Generating scambaiting reply…"):
                try:
                    resp = generate_reply(
                        email_text,
                        conversation_history=st.session_state.history,
                        provider=provider,
                    )
                    st.session_state.history        = resp["history"]
                    st.session_state.last_scam_type = resp["scam_type"]

                    # ── Safety status badge ──────────────────────────────────
                    safety = resp.get("safety", {})
                    is_safe = safety.get("safe", True)
                    issues  = safety.get("issues", [])

                    if show_safety_details:
                        safety_info_clean = (
                            "Safety Check (Guardrails):&#10;&#10;"
                            "This system scans the AI's response to ensure it does not contain:&#10;"
                            "• Real PII (IBAN, credit cards, Crypto wallets)&#10;"
                            "• Escalation Risks (physical addresses, meetups)&#10;"
                            "• Abuse (offensive or threatening language)&#10;&#10;"
                            "If detected, dangerous information is redacted."
                        )

                        if is_safe:
                            st.markdown(
                                f'<span class="safety-badge-ok" title="{safety_info_clean}">'
                                f'🛡️ Safety: PASS — no issues ⓘ</span>',
                                unsafe_allow_html=True,
                            )
                        else:
                            issues_str = ", ".join(issues) if issues else "unknown"
                            st.markdown(
                                f'<span class="safety-badge-warn" title="{safety_info_clean}">'
                                f'⚠️ Safety: flagged — {issues_str} (reply sanitized) ⓘ</span>',
                                unsafe_allow_html=True,
                            )
                        st.write("")  # vertical spacer

                    st.subheader(f"💬 Generated Reply (Turn #{resp['turn']})")
                    st.info(resp["reply"])

                    # Store for conversation history panel
                    st.session_state.turns.append({
                        "email":      email_text,
                        "reply":      resp["reply"],
                        "turn":       resp["turn"],
                        "scam_type":  resp["scam_type"],
                        "safety":     safety,
                    })

                except Exception as e:
                    st.warning(
                        f"⚠️ Could not generate reply: {e}\n\n"
                        f"Make sure your API key is set in `.env` "
                        f"(or use provider=mock for offline demo)."
                    )

    elif analyze_btn:
        st.warning("Please paste an email first.")


# ── Past Sessions Archive  ──────────────────────────────
if st.session_state.get("past_sessions"):
    st.divider()
    st.subheader("🗄️ Past Sessions Archive")
    
    for i, past_session in enumerate(st.session_state.past_sessions, 1):
        p_scam_type = past_session["scam_type"].replace('_', ' ').title() if past_session["scam_type"] else "Unknown"
        p_turns = past_session["turns"]
        
        # Κλειστό expander για κάθε παλιό session
        with st.expander(f"📁 Past Session #{i}: {p_scam_type} ({len(p_turns)} turns)", expanded=False):
            for t in p_turns:
                st.markdown(f"**🎯 Scammer (Turn #{t['turn']}):**")
                st.info(t['email'])
                st.markdown(f"**🤖 Our Reply:**")
                st.success(t['reply'])
                st.divider()

# ── Current Conversation  ─────────────────────────────
if st.session_state.turns:
    if not st.session_state.get("past_sessions"):
        st.divider()
    st.subheader("🔄 Current Conversation")
    
    scam_type_str = st.session_state.last_scam_type.replace('_', ' ').title() if st.session_state.last_scam_type else "Scam"
    
    # Ανοιχτό expander για το τρέχον session
    with st.expander(f"💬 Active Session: {scam_type_str} ({len(st.session_state.turns)} turns)", expanded=True):
        
        for t in st.session_state.turns:
            safety  = t.get("safety", {})
            s_icon  = "🛡️" if safety.get("safe", True) else "⚠️"
            
            st.markdown(f"**🎯 Scammer (Turn #{t['turn']}):**")
            st.info(t['email'])
            
            st.markdown(f"**🤖 Our Reply {s_icon}:**")
            st.success(t['reply'])
            
            if show_safety_details and not safety.get("safe", True):
                st.caption(f"⚠️ Guardrail triggered: {', '.join(safety.get('issues', []))} (Reply was sanitized)")
            
            st.divider()