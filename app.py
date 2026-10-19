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
    # Set theme to dark and primary color to AWS orange
    st.set_option('theme.base', 'dark')
    st.set_option('theme.primaryColor', '#FF9900')

    # Page configuration
    st.set_page_config(
        page_title="Sentry-Gate Telemetry",
        page_layout="wide"
    )

    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""
    if 'submit_requested' not in st.session_state:
        st.session_state.submit_requested = False

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
        st.text("Active Inference Profile: us.amazon.nova-lite-v1:0")
        st.text("Region: us-east-1 (default)")
        st.text("Routing: Dual-System (Local/Cloud)")

        st.header("Query History")
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
        if st.session_state.history:
            total_queries = len(st.session_state.history)
            total_saved = sum(
                entry['result'].get('metrics', {}).get('cost_saved_usd', 0)
                for entry in st.session_state.history
                if "error" not in entry['result']
            )
            st.sidebar.metric("Total Queries Routed", total_queries)
            st.sidebar.metric("Total Savings", f"${total_saved:.4f}")
        else:
            st.sidebar.metric("Total Queries Routed", 0)
            st.sidebar.metric("Total Savings", "$0.0000")

        st.divider()
        st.header("Quick Test Buttons")
        if st.button("Test Local System 1"):
            st.session_state.prompt = "Hello, how are you?"
            st.session_state.submit_requested = True
            st.rerun()
        if st.button("Test Bedrock System 2"):
            st.session_state.prompt = "Explain the architecture of a high-performance decision gate that routes simple tasks locally and complex workloads to cloud LLMs, including latency optimization and cost-benefit analysis."
            st.session_state.submit_requested = True
            st.rerun()

        st.divider()
        st.sidebar.caption("Apache License 2.0")

    # Main content
    if not backend_healthy:
        st.stop()

    st.title("AWS Bedrock Operational Telemetry")
    st.caption("Enterprise Telemetry Dashboard • Apache License 2.0")

    st.subheader("Query Submission")

    # Input form
    prompt = st.text_area(
        label="Enter your query",
        placeholder="Type your question or request here...",
        height=100,
        key="prompt_input"
    )

    # Update session state from the text area widget
    st.session_state.prompt = st.session_state.prompt_input

    # Submit button
    submit_button = st.button("Route Query", type="primary", use_container_width=True)
    if submit_button:
        st.session_state.submit_requested = True

    # Process submission if requested
    if st.session_state.submit_requested and st.session_state.prompt.strip():
        with st.spinner("Routing query..."):
            start_time = time.time()
            result = route_prompt(st.session_state.prompt.strip())
            end_time = time.time()

            # Add to history
            st.session_state.history.append({
                "timestamp": start_time,
                "prompt": st.session_state.prompt,
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

                # Optional: show raw JSON in an expander
                with st.expander("View Raw Response"):
                    st.json(result)
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
                if 'detail' in result:
                    st.info(f"Detail: {result['detail']}")

            # Reset submit request after processing
            st.session_state.submit_requested = False
            # Clear the prompt after processing? Optional: we can keep it for reference.
            # st.session_state.prompt = ""

    # Footer (minimal, just attribution)
    st.divider()
    st.caption("Sentry-Gate Enterprise Telemetry Dashboard • Powered by Streamlit and FastAPI")

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

if __name__ == "__main__":
    main()