import streamlit as st
import requests

API_URL = "http://api:8000"

st.set_page_config(page_title="HealthOps AI Platform", page_icon="🏥", layout="wide")
st.title("🏥 HealthOps AI Platform")
st.caption("Cloud-Native Healthcare AI Operations on AWS")

tab1, tab2, tab3 = st.tabs(["💬 Healthcare Q&A", "📊 Anomaly Detection", "🔒 Governance Check"])

# --- Tab 1: RAG Query ---
with tab1:
    st.subheader("Bedrock RAG — Healthcare Document Q&A")
    question = st.text_input("Ask a healthcare question:", placeholder="What are prior auth requirements for MRI?")
    if st.button("Ask", key="ask"):
        if question:
            with st.spinner("Querying..."):
                resp = requests.post(f"{API_URL}/query", json={"question": question})
            if resp.ok:
                data = resp.json()
                st.success(data["answer"])
                with st.expander("📄 Sources"):
                    for s in data["sources"]:
                        st.write(f"- {s}")
                st.caption(f"Model: {data['model']}")
            else:
                st.error(f"Error: {resp.text}")

# --- Tab 2: Anomaly Detection ---
with tab2:
    st.subheader("SageMaker — Health KPI Anomaly Detection")
    col1, col2 = st.columns(2)
    with col1:
        denial_rate = st.slider("Claims Denial Rate", 0.0, 1.0, 0.12)
        processing_days = st.slider("Avg Processing Days", 1.0, 60.0, 14.0)
    with col2:
        satisfaction = st.slider("Member Satisfaction", 1.0, 5.0, 4.2)
        readmission = st.slider("Readmission Rate", 0.0, 1.0, 0.10)

    if st.button("Detect Anomalies", key="detect"):
        payload = {
            "claims_denial_rate": denial_rate,
            "avg_processing_days": processing_days,
            "member_satisfaction": satisfaction,
            "readmission_rate": readmission,
        }
        resp = requests.post(f"{API_URL}/anomaly", json=payload)
        if resp.ok:
            data = resp.json()
            if data["is_anomaly"]:
                st.error("🚨 ANOMALY DETECTED — KPIs are outside normal range!")
            else:
                st.success("✅ Normal — All KPIs within expected range.")
            st.json(data)

# --- Tab 3: Governance ---
with tab3:
    st.subheader("OPA Policy — HIPAA Access Control")
    col1, col2 = st.columns(2)
    with col1:
        user = st.text_input("Username", value="john_doe")
        role = st.selectbox("Role", ["member", "clinician", "admin"])
    with col2:
        hipaa_trained = st.checkbox("HIPAA Trained", value=False)
        resource = st.selectbox("Resource", ["/query", "/members", "/admin"])

    if st.button("Check Access", key="check"):
        payload = {"user": user, "role": role, "hipaa_trained": hipaa_trained, "resource": resource}
        resp = requests.post(f"{API_URL}/governance/check", json=payload)
        if resp.ok:
            data = resp.json()
            if data["allowed"]:
                st.success(f"✅ ACCESS GRANTED for {user}")
            else:
                st.error(f"🚫 ACCESS DENIED for {user}")
                for d in data["denials"]:
                    st.warning(d)
