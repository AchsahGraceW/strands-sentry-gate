"""
Sentry-Gate: Streamlit Web Frontend
A sleek, modern interface for the high-performance decision gate system.
"""

import streamlit as st
import requests
import time
from typing import Dict, Any
import json

# Page configuration
st.set_page_config(
    page_title="Sentry-Gate AI Router",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for sleek, modern design
st.markdown("""
<style>
    /* Main theme and colors */
    :root {
        --primary-color: #0066ff;
        --secondary-color: #00b3ff;
        --success-color: #00c853;
        --warning-color: #ffbb33;
        --background-color: #f8f9fa;
        --card-background: #ffffff;
        --border-radius: 12px;
        --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #0066ff, #00b3ff);
        color: white;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        box-shadow: var(--box-shadow);
    }

    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }

    /* Input section */
    .input-section {
        background: var(--card-background);
        padding: 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        margin-bottom: 2rem;
    }

    /* Example buttons */
    .example-button {
        margin: 0.25rem;
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 20px;
        background: linear-gradient(to right, #e3f2fd, #bbdefb);
        color: #0066ff;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .example-button:hover {
        background: linear-gradient(to right, #bbdefb, #90caf9);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }

    /* System indicator badges */
    .system-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        text-align: center;
        min-width: 180px;
        margin: 0.5rem;
    }

    .system-1-badge {
        background: linear-gradient(to right, #e8f5e8, #c8e6c9);
        color: #2e7d32;
        border: 2px solid #4caf50;
    }

    .system-2-badge {
        background: linear-gradient(to right, #e3f2fd, #bbdefb);
        color: #1565c0;
        border: 2px solid #2196f3;
    }

    /* Response card */
    .response-card {
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--box-shadow);
        border-left: 4px solid var(--primary-color);
        margin: 1.5rem 0;
    }

    /* Metrics cards */
    .metrics-container {
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }

    .metric-card {
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--box-shadow);
        text-align: center;
        flex: 1;
        min-width: 120px;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Latency and cost styling */
    .latency-value {
        color: var(--primary-color);
    }

    .cost-value {
        color: var(--success-color);
    }

    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .status-healthy {
        background: #e8f5e8;
        color: #2e7d32;
    }

    .status-unhealthy {
        background: #ffebee;
        color: #c62828;
    }

    /* Example prompt styling */
    .example-prompt {
        background: #f5f5f5;
        border-left: 3px solid var(--primary-color);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
        font-style: italico;
    }

    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }

    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }

        .main-header p {
            font-size: 1rem;
        }

        .metrics-container {
            flex-direction: column;
            align-items: stretch;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'backend_healthy' not in st.session_state:
    st.session_state.backend_healthy = False

# Constants
BACKEND_URL = "http://127.0.0.1:8000"

def check_backend_health() -> bool:
    """Check if the FastAPI backend is healthy."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "healthy"
    except Exception:
        pass
    return False

def route_prompt(prompt: str) -> Dict[str, Any]:
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
            return {
                "error": f"Backend error: {response.status_code}",
                "detail": response.text
            }
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Please ensure the FastAPI server is running."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The backend may be overloaded."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def render_system_badge(source: str):
    """Render a visual badge indicating the routing system."""
    if source == "local_system_one":
        st.markdown(
            '<span class="system-badge system-1-badge">⚡ System 1 (Fast Local Edge)</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="system-badge system-2-badge">☁️ System 2 (AWS Bedrock Cloud)</span>',
            unsafe_allow_html=True
        )

def render_metrics(metrics: Dict[str, Any]):
    """Render latency and cost metrics."""
    col1, col2 = st.columns(2)

    with col1:
        latency = metrics.get("latency_ms", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Latency</div>
            <div class="metric-value latency-value">{latency:.2f} ms</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        cost_saved = metrics.get("cost_saved_usd", 0)
        # Format cost with appropriate precision
        if cost_saved < 0.01:
            cost_display = f"${cost_saved:.4f}"
        else:
            cost_display = f"${cost_saved:.2f}"

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Estimated Cost Saved</div>
            <div class="metric-value cost-value">{cost_display}</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚡ Sentry-Gate AI Router</h1>
        <p>High-Performance Decision Gate: Local Edge Intelligence Routing to Cloud AI</p>
    </div>
    """, unsafe_allow_html=True)

    # Backend health check
    st.session_state.backend_healthy = check_backend_health()

    # Status indicator
    if st.session_state.backend_healthy:
        st.markdown(
            '<div class="status-indicator status-healthy">✅ Backend Connected & Healthy</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-indicator status-unhealthy">❌ Backend Disconnected</div>',
            unsafe_allow_html=True
        )
        st.warning("Please start the FastAPI backend first: `python sentry_gate.py`")

    # Only show the main interface if backend is healthy
    if st.session_state.backend_healthy:
        # Input section
        with st.container():
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.subheader("💬 Enter Your Query")

            # Text input
            prompt = st.text_area(
                label="Prompt",
                placeholder="Enter your question or request here...",
                height=100,
                label_visibility="collapsed"
            )

            # Example buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("Simple Greeting", key="example1", help="Click to load a simple greeting example"):
                    st.session_state.example_prompt = "Hello, how are you?"
                    st.rerun()
            with col2:
                if st.button("Complex System Architecture", key="example2", help="Click to load a complex system architecture example"):
                    st.session_state.example_prompt = "Explain the architecture of a high-performance decision gate that routes simple tasks locally and complex workloads to cloud LLMs, including latency optimization and cost-benefit analysis."
                    st.rerun()

            # Handle example prompt selection
            if 'example_prompt' in st.session_state:
                prompt = st.session_state.example_prompt
                del st.session_state.example_prompt
                # Update the text area value (this requires a rerun which we already triggered)

            # Submit button
            submit_button = st.button(
                "🚀 Route Query",
                type="primary",
                use_container_width=True,
                disabled=not prompt.strip()
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # Process submission
        if submit_button and prompt.strip():
            # Add a spinner for loading state
            with st.spinner("Routing your query through Sentry-Gate..."):
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
                    st.success("Query processed successfully!")

                    # System indicator badge
                    st.subheader("🎯 Routing Decision")
                    render_system_badge(result.get("source", ""))

                    # Response
                    st.markdown('<div class="response-card">', unsafe_allow_html=True)
                    st.subheader("📝 Response")
                    st.write(result.get("response", "No response received"))
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Metrics
                    st.subheader("📊 Performance Metrics")
                    render_metrics(result.get("metrics", {}))

                    # Additional info
                    with st.expander("🔍 Technical Details"):
                        st.json({
                            "source": result.get("source"),
                            "backend_latency_ms": result.get("metrics", {}).get("latency_ms"),
                            "estimated_cost_saved_usd": result.get("metrics", {}).get("cost_saved_usd"),
                            "total_processing_time_ms": (end_time - start_time) * 1000
                        })
                else:
                    st.error(f"Error processing query: {result.get('error', 'Unknown error')}")
                    if 'detail' in result:
                        st.info(f"Detail: {result['detail']}")

        # Display history
        if st.session_state.history:
            st.subheader("📜 Query History")
            # Show last 5 entries
            for i, entry in enumerate(reversed(st.session_state.history[-5:])):
                with st.expander(f"Query {len(st.session_state.history)-i}: {entry['prompt'][:50]}{'...' if len(entry['prompt']) > 50 else ''}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("**Prompt:**", entry['prompt'])
                        if "error" not in entry['result']:
                            st.write("**Response:**", entry['result'].get('response', 'No response'))
                            render_system_badge(entry['result'].get('source', ''))
                            render_metrics(entry['result'].get('metrics', {}))
                        else:
                            st.error(f"Error: {entry['result'].get('error')}")
                    with col2:
                        st.caption(f"Time: {time.strftime('%H:%M:%S', time.localtime(entry['timestamp']))}")
                        st.caption(f"Latency: {entry['result'].get('metrics', {}).get('latency_ms', 0):.2f}ms")

    # Sidebar with information
    with st.sidebar:
        st.header("📋 About Sentry-Gate")
        st.info("""
        **Sentry-Gate** is a high-performance decision gate that intelligently routes queries:

        - **System 1 (Local)**: Fast edge computing for simple tasks
        - **System 2 (Cloud)**: AWS Bedrock with Amazon Nova Lite for complex queries

        This hybrid approach optimizes for both latency and cost.
        """)

        st.header("🔧 System Status")
        if st.session_state.backend_healthy:
            st.success("Backend: Online")
            # Try to get version info
            try:
                health_resp = requests.get(f"{BACKEND_URL}/health", timeout=2)
                if health_resp.status_code == 200:
                    health_data = health_resp.json()
                    st.info(f"Version: {health_data.get('version', 'Unknown')}")
            except:
                pass
        else:
            st.error("Backend: Offline")

        st.header("⚡ Performance Features")
        st.markdown("""
        - ⚡ Sub-millisecond local routing
        - ☁️ Intelligent cloud fallback
        - 💰 Cost optimization engine
        - 📊 Real-time telemetry
        - 🛡️ Graceful error handling
        """)

        if st.button("Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()

if __name__ == "__main__":
    main()