"""
app.py — Streamlit Demo UI
Αρμόδιο άτομο: Άτομο 4

Οπτικοποιεί το pipeline με interactive UI.
Τρέξε με: streamlit run src/pipeline/app.py
"""

import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from classifier.predict import predict_email
from responder.responder import generate_reply, detect_scam_type

# ── Page config ──
st.set_page_config(
    page_title="ScamAI — Scam Detector & Responder",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ ScamAI — Spam Detection & Scambaiting System")
st.caption("MSc Project | Advanced AI and Cybersecurity")

# ── Sidebar ──
with st.sidebar:
    st.header("⚙️ Settings")
    threshold = st.slider("Scam Detection Threshold", 0.1, 0.9, 0.5, 0.05)
    provider  = st.selectbox("AI Provider", ["anthropic", "openai"])
    st.divider()
    st.info("ℹ️ This tool is for academic research and defensive security purposes only.")

# ── Session state για multi-turn ──
if "history" not in st.session_state:
    st.session_state.history = []
if "turns" not in st.session_state:
    st.session_state.turns = []

# ── Main area ──
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📧 Input Email")
    email_text = st.text_area(
        "Paste email body here:",
        height=250,
        placeholder="Dear Beloved Friend, I am Prince Adebayo from Nigeria...",
    )

    col_a, col_b = st.columns(2)
    analyze_btn = col_a.button("🔍 Analyze", type="primary", use_container_width=True)
    reset_btn   = col_b.button("🔄 Reset Session", use_container_width=True)

    if reset_btn:
        st.session_state.history = []
        st.session_state.turns   = []
        st.success("Session reset!")

with col2:
    st.subheader("📊 Results")

    if analyze_btn and email_text.strip():
        with st.spinner("Analyzing email..."):
            # Classification
            clf_result = predict_email(email_text)
            is_scam    = clf_result["confidence"] >= threshold

        # ── Classification result ──
        if is_scam:
            st.error(f"🚨 SCAM DETECTED — {clf_result['confidence']:.1%} confidence")
            scam_type = detect_scam_type(email_text)
            st.caption(f"Scam type: `{scam_type.replace('_', ' ').title()}`")
        else:
            st.success(f"✅ LEGITIMATE — {1 - clf_result['confidence']:.1%} confidence")

        # Feature breakdown
        with st.expander("🔎 Feature Breakdown"):
            feats = clf_result["features"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Scam Keywords",   feats["scam_keyword_count"])
            c2.metric("Money Mentions",  feats["money_mentions"])
            c3.metric("CAPS Ratio",      f"{feats['caps_ratio']:.1%}")
            c4.metric("Exclamations",    feats["exclamation_count"])

        # ── Generate reply if scam ──
        if is_scam:
            st.divider()
            with st.spinner("Generating scambaiting reply..."):
                try:
                    resp = generate_reply(
                        email_text,
                        conversation_history=st.session_state.history,
                        provider=provider,
                    )
                    st.session_state.history = resp["history"]
                    turn_data = {"email": email_text[:80] + "...", "reply": resp["reply"], "turn": resp["turn"]}
                    st.session_state.turns.append(turn_data)

                    st.subheader(f"💬 Generated Reply (Turn #{resp['turn']})")
                    st.info(resp["reply"])
                except Exception as e:
                    st.warning(f"⚠️ Could not generate reply: {e}\n\nMake sure your API key is set in `.env`")

    elif analyze_btn:
        st.warning("Please paste an email first.")

# ── Conversation history ──
if st.session_state.turns:
    st.divider()
    st.subheader("🔄 Multi-Turn Conversation History")
    for t in st.session_state.turns:
        with st.expander(f"Turn #{t['turn']} — {t['email']}"):
            st.markdown(f"**Our Reply:**\n\n{t['reply']}")
