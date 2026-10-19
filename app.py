"""
Sentry-Gate: Enterprise Telemetry Dashboard
A minimalist, professional interface for monitoring the AI decision gate system.
"""

import streamlit as st
import requests
import time

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"

def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count.
    Using simple approximation: 1 token ≈ 0.75 words
    """
    words = len(text.split())
    return int(words / 0.75)

def main():
    # Page configuration
    st.set_page_config(
        page_title="Sentry-Gate Telemetry",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for AWS Bedrock dark slate aesthetic
    st.markdown("""
    <style>
        /* Dark slate background */
        .stApp {
            background-color: #0F172A;
            color: #FFFFFF;
        }
        /* Main container */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            background-color: #0F172A;
        }
        /* Headers and text */
        h1, h2, h3, h4, h5, h6, p, label, .st-caption {
            color: #FFFFFF !important;
        }
        /* Sidebar styling */
        .css-1d391kg, .css-1lcbmhc, .css-1l02zno {
            background-color: #111827 !important;
        }
        .css-1d391kg .stHeader {
            color: #FFFFFF !important;
        }
        /* Button styling */
        .stButton>button {
            background-color: #FF9900;
            color: #0F172A;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #FFB84D;
        }
        /* Secondary button style for quick prompts */
        .stButton>button[kind="secondary"] {
            background-color: #1F2937;
            color: #FFFFFF;
            border: 1px solid #374151;
        }
        .stButton>button[kind="secondary"]:hover {
            background-color: #374151;
            border-color: #FF9900;
        }
        /* Text area */
        .stTextArea>div>div>textarea {
            background-color: #1F2937;
            color: #FFFFFF;
            border: 1px solid #374151;
        }
        .stTextArea>div>div>textarea:focus {
            border-color: #FF9900;
            box-shadow: 0 0 0 2px rgba(255, 153, 0, 0.2);
        }
        /* Metric containers */
        [data-testid="stMetric"] {
            background-color: #1F2937;
            border: 1px solid #374151;
            padding: 1rem;
            border-radius: 4px;
        }
        [data-testid="stMetric"] label {
            color: #9CA3AF !important;
        }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
        }
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #1F2937;
            color: #FFFFFF;
            border: 1px solid #374151;
        }
        .streamlit-expanderContent {
            background-color: #111827;
            color: #FFFFFF;
        }
        /* Divider */
        hr {
            border-color: #374151;
        }
        /* Success/error/warning messages */
        .stAlert {
            background-color: #1F2937;
            border-left: 4px solid #FF9900;
        }
        .stAlert[data-baseweb="alert"] {
            background-color: #1F2937;
        }
        /* Info, success, warning, error specific colors */
        .stAlert [data-baseweb="notification"] {
            background-color: #1F2937;
        }
        /* Specifically for success */
        .st-success {
            background-color: #1F2937;
            border-left-color: #10B981;
        }
        .st-error {
            background-color: #1F2937;
            border-left-color: #EF4444;
        }
        .st-warning {
            background-color: #1F2937;
            border-left-color: #FBBF24;
        }
        .st-info {
            background-color: #1F2937;
            border-left-color: #60A5FA;
        }
        /* Footer */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #111827;
            color: #9CA3AF;
            text-align: center;
            padding: 1rem;
            font-size: 0.875rem;
            border-top: 1px solid #374151;
        }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("Sentry-Gate AI Routing System")
    st.caption("Enterprise Telemetry Dashboard • Apache License 2.0")

    # Backend health check
    def check_backend_health():
        """Check if the FastAPI backend is healthy."""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            return response.status_code == 200 and response.json().get("status") == "healthy"
        except Exception:
            return False

    backend_healthy = check_backend_health()

    # Sidebar
    with st.sidebar:
        st.header("System Status")
        if backend_healthy:
            st.success("Backend: Online")
        else:
            st.error("Backend: Offline")
            st.warning("Start the FastAPI backend: `python sentry_gate.py`")

        st.header("AWS Bedrock Status")
        st.text("Inference Profile: us.amazon.nova-lite-v1:0")
        st.text("Region: us-east-1 (default)")
        st.text("Routing: Dual-System (Local/Cloud)")

        st.header("Query History")
        if 'history' not in st.session_state:
            st.session_state.history = []

        if st.session_state.history:
            for i, entry in enumerate(reversed(st.session_state.history[-5:]), 1):
                with st.expander(f"Query {len(st.session_state.history)-i+1}"):
                    st.code(entry['prompt'], language=None)
                    if "error" not in entry['result']:
                        st.text(f"Source: {entry['result'].get('source')}")
                        st.text(f"Latency: {entry['result'].get('metrics', {}).get('latency_ms', 0):.2f} ms")
                    else:
                        st.text(f"Error: {entry['result'].get('error')}")
        else:
            st.text("No queries yet.")

        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()

        st.divider()
        st.header("Cumulative Metrics")
        if 'history' in st.session_state and st.session_state.history:
            total_queries = len(st.session_state.history)
            total_tokens_saved = 0
            total_cost_saved = 0.0
            latencies = []
            cloud_latencies = []  # to estimate average cloud latency
            for entry in st.session_state.history:
                result = entry['result']
                if "error" not in result:
                    source = result.get('source', '')
                    metrics = result.get('metrics', {})
                    latency = metrics.get('latency_ms', 0)
                    cost_saved = metrics.get('cost_saved_usd', 0)
                    total_cost_saved += cost_saved
                    latencies.append(latency)
                    if source == 'local_system_one':
                        # Tokens saved: estimate tokens of prompt + response
                        prompt_tokens = estimate_tokens(entry['prompt'])
                        response_tokens = estimate_tokens(result.get('response', ''))
                        total_tokens_saved += prompt_tokens + response_tokens
                    else:
                        cloud_latencies.append(latency)
            avg_cloud_latency = sum(cloud_latencies) / len(cloud_latencies) if cloud_latencies else 0
            total_latency_saved = 0
            for entry in st.session_state.history:
                result = entry['result']
                if "error" not in result:
                    source = result.get('source', '')
                    metrics = result.get('metrics', {})
                    latency = metrics.get('latency_ms', 0)
                    if source == 'local_system_one' and avg_cloud_latency > 0:
                        latency_saved = avg_cloud_latency - latency
                        if latency_saved > 0:
                            total_latency_saved += latency_saved
            net_latency_reduction = (total_latency_saved / (total_queries * avg_cloud_latency)) * 100 if avg_cloud_latency > 0 and total_queries > 0 else 0
        else:
            total_queries = 0
            total_tokens_saved = 0
            total_cost_saved = 0.0
            net_latency_reduction = 0.0

        st.metric("Total Queries", total_queries)
        st.metric("Total Tokens Saved", f"{total_tokens_saved:,}")
        st.metric("Net Latency Reduction %", f"{net_latency_reduction:.1f}%")
        st.metric("Total USD Cost Savings", f"${total_cost_saved:.2f}")

        st.divider()
        st.caption("Licensed under Apache License 2.0")
        st.caption("https://www.apache.org/licenses/LICENSE-2.0")

    # Main content
    if not backend_healthy:
        st.stop()

    st.subheader("Query Submission")

    # Input form
    with st.form(key="query_form", clear_on_submit=False):
        prompt = st.text_area(
            label="Enter your query",
            placeholder="Type your question or request here...",
            height=100,
            label_visibility="collapsed"
        )

        # Quick-launch buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.form_submit_button("Simple Ping (System 1)", use_container_width=True):
                prompt = "ping"
        with col2:
            if st.form_submit_button("Complex AWS Architecture Spec (System 2)", use_container_width=True):
                prompt = "Provide a detailed specification for a fault-tolerant, scalable AWS architecture supporting a serverless microservices application with API Gateway, Lambda, DynamoDB, S3, and CloudFront, including security, monitoring, and cost optimization strategies."
        # Note: We use the secondary button style for these via CSS

        # Submit button
        submit = st.form_submit_button("Route Query", type="primary", use_container_width=True)

    # Process form submission
    if submit and prompt.strip():
        with st.spinner("Routing query..."):
            start_time = time.time()
            result = route_prompt(prompt.strip())
            end_time = time.time()

            # Add to history
            st.session_state.history.append({
                "timestamp": start_time,
                "prompt": prompt,
                "result": result,
                "processing_time": end_time - start_time
            })

            # Display results
            if "error" not in result:
                st.success("Query processed successfully")

                # Routing decision
                source = result.get("source", "")
                if source == "local_system_one":
                    routing_label = "System 1: Fast Local Edge"
                else:
                    routing_label = "System 2: AWS Bedrock Cloud"

                st.subheader("Routing Decision")
                st.markdown(f"**{routing_label}**")

                # Response
                st.subheader("Response")
                st.text_area(
                    label="Generated Response",
                    value=result.get("response", ""),
                    height=150,
                    disabled=True
                )

                # Metrics table
                st.subheader("Performance Metrics")
                metrics = result.get("metrics", {})
                latency = metrics.get("latency_ms", 0)
                cost_saved = metrics.get("cost_saved_usd", 0)

                # Create a table-like display using columns
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Latency",
                        value=f"{latency:.2f} ms"
                    )
                with col2:
                    st.metric(
                        label="Estimated Cost Saved",
                        value=f"${cost_saved:.4f}" if cost_saved < 0.01 else f"${cost_saved:.2f}"
                    )

                # Optional: show raw JSON in an expander
                with st.expander("View Raw Response"):
                    st.json(result)
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
                if 'detail' in result:
                    st.info(f"Detail: {result['detail']}")

    # Footer
    st.divider()
    st.caption("Sentry-Gate Enterprise Telemetry Dashboard • Powered by Streamlit and FastAPI")

if __name__ == "__main__":
    main()