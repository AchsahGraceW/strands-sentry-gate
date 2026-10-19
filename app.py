"""
Sentry-Gate: Enterprise Telemetry Dashboard
A minimalist, professional interface for monitoring the AI decision gate system.
"""

import streamlit as st
import requests
import time

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"

def check_backend_health():
    """Check if the FastAPI backend is healthy."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200 and response.json().get("status") == "healthy"
    except Exception:
        return False

def route_prompt(prompt):
    """Send prompt to the FastAPI backend and return the response."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/route",
            json={"prompt": prompt},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Backend error: {response.status_code}", "detail": response.text}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Ensure the FastAPI server is running."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The backend may be overloaded."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    # Page configuration
    st.set_page_config(
        page_title="Sentry-Gate Telemetry",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Header
    st.title("Sentry-Gate AI Routing System")
    st.caption("Enterprise Telemetry Dashboard • Apache License 2.0")

    # Backend health check
    backend_healthy = check_backend_health()

    # Sidebar
    with st.sidebar:
        st.header("System Status")
        if backend_healthy:
            st.success("Backend: Online")
        else:
            st.error("Backend: Offline")
            st.warning("Start the FastAPI backend: `python sentry_gate.py`")

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

        # Example buttons in a row
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.form_submit_button("Simple Greeting", use_container_width=True):
                prompt = "Hello, how are you?"
        with col2:
            if st.form_submit_button("Complex System Architecture", use_container_width=True):
                prompt = "Explain the architecture of a high-performance decision gate that routes simple tasks locally and complex workloads to cloud LLMs, including latency optimization and cost-benefit analysis."

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
                    routing_color = "green"
                else:
                    routing_label = "System 2: AWS Bedrock Cloud"
                    routing_color = "blue"

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