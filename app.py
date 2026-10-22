import streamlit as st
import requests
import time

# 1. Page Configuration
st.set_page_config(
    page_title="Sentry-Gate Enterprise Console",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Sleek Enterprise LLM Styling & WebGL Background
st.markdown("""
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.143.0/build/three.module.js",
    "three/examples/jsm/": "https://unpkg.com/three@0.143.0/examples/jsm/"
  }
}
</script>

<style>
:root {
  --bg: #04060f;
  --surface: rgba(12, 18, 38, 0.85);
  --ink: #f3f6ff;
  --muted: #9aa6c4;
  --accent: #5df0a8;
  --line: rgba(150, 175, 230, 0.15);
}

.stApp {
  background: var(--bg) !important;
  color: var(--ink);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Remove default Streamlit top whitespace */
header[data-testid="stHeader"] {
  background: transparent !important;
}
.block-container {
  padding-top: 1rem !important;
  padding-bottom: 5rem !important;
  max-width: 1000px;
}

/* Fixed WebGL Planet Canvas Background */
#planet-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  pointer-events: none;
  opacity: 0.6;
}

/* Sleek Sidebar */
section[data-testid="stSidebar"] {
  background: rgba(4, 6, 15, 0.95) !important;
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--line) !important;
}

/* Modern LLM Chat Bubble Design */
div[data-testid="stChatMessage"] {
  background: var(--surface) !important;
  backdrop-filter: blur(16px);
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  padding: 16px !important;
  margin-bottom: 14px;
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
}

/* Technical Telemetry Badges */
.metric-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  padding: 4px 10px;
  border-radius: 4px;
  margin-top: 10px;
  font-family: monospace;
}
.badge-system1 {
  background: rgba(93, 240, 168, 0.08);
  color: #5df0a8;
  border: 1px solid rgba(93, 240, 168, 0.25);
}
.badge-system2 {
  background: rgba(59, 130, 246, 0.08);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.25);
}

/* Quick prompt chip buttons */
.stButton button {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 13px;
  border-radius: 8px;
  transition: all 0.2s ease;
}
.stButton button:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--accent);
  color: var(--accent);
}
</style>

<canvas id="planet-canvas"></canvas>

<script type="module">
import * as THREE from 'three';
const canvas = document.getElementById('planet-canvas');
if (canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.z = 6;

  const geometry = new THREE.IcosahedronGeometry(2, 4);
  const material = new THREE.MeshBasicMaterial({ color: 0x3a6cff, wireframe: true, transparent: true, opacity: 0.15 });
  const sphere = new THREE.Mesh(geometry, material);
  scene.add(sphere);

  function animate() {
    requestAnimationFrame(animate);
    sphere.rotation.y += 0.001;
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}
</script>
""", unsafe_allow_html=True)

# Initialize Session State
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "system1_queries" not in st.session_state:
    st.session_state.system1_queries = 0
if "system2_queries" not in st.session_state:
    st.session_state.system2_queries = 0
if "total_saved" not in st.session_state:
    st.session_state.total_saved = 0.0

# Sidebar Telemetry & Config
st.sidebar.title("Sentry-Gate")
st.sidebar.caption("Enterprise Routing Gateway")

st.sidebar.markdown("---")
st.sidebar.markdown("### Telemetry")
st.sidebar.metric("Total Executions", st.session_state.total_queries)
st.sidebar.metric("System 1 (Edge)", st.session_state.system1_queries)
st.sidebar.metric("System 2 (Bedrock)", st.session_state.system2_queries)
st.sidebar.metric("Token Savings", f"${st.session_state.total_saved:.4f}")

st.sidebar.markdown("---")
st.sidebar.markdown("### Environment")
st.sidebar.markdown("**Model:** `us.amazon.nova-lite-v1:0`")
st.sidebar.markdown("**Security:** OAuth2 / Bearer Ready")
st.sidebar.markdown("**License:** Apache 2.0")

# Main Interface Header
st.markdown("## Sentry-Gate Command Center")
st.markdown("<p style='color: var(--muted); margin-bottom: 24px;'>Dynamic heuristic routing between high-speed local edge and AWS Bedrock.</p>", unsafe_allow_html=True)

# Quick Action Chips
cols = st.columns(3)
preset_prompt = None
with cols[0]:
    if st.button("Test Greeting (System 1)", use_container_width=True):
        preset_prompt = "hi"
with cols[1]:
    if st.button("Test Factual (System 1)", use_container_width=True):
        preset_prompt = "explain photosynthesis"
with cols[2]:
    if st.button("Test Architecture (System 2)", use_container_width=True):
        preset_prompt = "Design a microservices architecture using FastAPI, Redis, and AWS Bedrock"

st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

# Chat History Management
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Gateway initialized. Send a prompt to evaluate routing performance.", "metrics": None}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("metrics"):
            m = msg["metrics"]
            if m["source"] == "local_system_one":
                st.markdown(f'<span class="metric-badge badge-system1">SYSTEM 1 [EDGE] | Latency: {m["latency_ms"]}ms | Saved: ${m["cost_saved_usd"]}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="metric-badge badge-system2">SYSTEM 2 [AWS BEDROCK] | Latency: {m["latency_ms"]}ms | Profile: us.amazon.nova-lite-v1:0</span>', unsafe_allow_html=True)

# Input Handling
user_input = st.chat_input("Enter query or enterprise workload specification...")
active_prompt = user_input or preset_prompt

if active_prompt:
    st.session_state.messages.append({"role": "user", "content": active_prompt})
    with st.chat_message("user"):
        st.markdown(active_prompt)

    backend_url = "http://localhost:8000/v1/route"
    
    with st.chat_message("assistant"):
        with st.spinner("Evaluating heuristic routing rules..."):
            try:
                response = requests.post(
                    backend_url,
                    json={"prompt": active_prompt},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    res_text = data["response"]
                    source = data["source"]
                    metrics = data["metrics"]
                    metrics["source"] = source

                    st.markdown(res_text)

                    if source == "local_system_one":
                        st.markdown(f'<span class="metric-badge badge-system1">SYSTEM 1 [EDGE] | Latency: {metrics["latency_ms"]}ms | Saved: ${metrics["cost_saved_usd"]}</span>', unsafe_allow_html=True)
                        st.session_state.total_saved += metrics["cost_saved_usd"]
                        st.session_state.system1_queries += 1
                    else:
                        st.markdown(f'<span class="metric-badge badge-system2">SYSTEM 2 [AWS BEDROCK] | Latency: {metrics["latency_ms"]}ms | Profile: us.amazon.nova-lite-v1:0</span>', unsafe_allow_html=True)
                        st.session_state.system2_queries += 1

                    st.session_state.total_queries += 1

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": res_text,
                        "metrics": metrics
                    })
                else:
                    st.error(f"Routing Error ({response.status_code}): {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Gateway unreachable. Verify backend service is active on port 8000.")