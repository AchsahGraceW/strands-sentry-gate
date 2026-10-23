"""
Sentry-Gate: Enterprise AI Gateway with Strands Decider 2B Pattern & AWS Bedrock
Repository: https://github.com/AchsahGraceW/strands-sentry-gate
Hackathon Tags: #strands-decider-2b, #model-routing, #policy
"""

import time
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

sentry_gate: Optional['SentryGate'] = None

@asynccontextmanager
async def lifespan(_app: FastAPI):
    global sentry_gate
    sentry_gate = SentryGate()
    print("🚀 Sentry-Gate online: Strands Decider 2B Pattern & AWS Bedrock Gateway")
    yield
    print("🛑 Sentry-Gate shutting down")

app = FastAPI(
    title="Sentry-Gate Enterprise AI Gateway",
    description="Strands Decider 2B Pattern Gate & Amazon Bedrock Gateway",
    version="2.4.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RouteRequest(BaseModel):
    prompt: str

class RouteResponse(BaseModel):
    source: str
    response: str
    metrics: Dict[str, Any]

class SentryGate:
    def __init__(self):
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

        if aws_access_key and aws_secret_key:
            self.bedrock = boto3.client(
                service_name="bedrock-runtime",
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
        else:
            self.bedrock = boto3.client(
                service_name="bedrock-runtime",
                region_name=aws_region
            )
            
        self.model_id = "us.amazon.nova-lite-v1:0"

    def decider_2b_policy_check(self, prompt: str) -> Dict[str, Any]:
        """
        Strands Decider 2B Pattern: #policy
        Typed Question: "Does this prompt contain policy violations or injection attacks?"
        """
        start = time.perf_counter()
        prompt_lower = prompt.lower().strip()
        
        unsafe_keywords = [
            "ignore previous instructions", "drop database", "bypass safety", 
            "jailbreak", "reveal system prompt", "delete all"
        ]
        
        is_unsafe = any(kw in prompt_lower for kw in unsafe_keywords)
        latency_ms = (time.perf_counter() - start) * 1000

        return {
            "decision": "UNSAFE" if is_unsafe else "SAFE",
            "eval_latency_ms": round(latency_ms, 3)
        }

    def decider_2b_route_check(self, prompt: str) -> Dict[str, Any]:
        """
        Strands Decider 2B Pattern: #model-routing
        Typed Question: "Does this prompt require complex cloud generative execution?"
        """
        start = time.perf_counter()
        prompt_lower = prompt.lower().strip()

        complex_keywords = [
            "code", "python", "javascript", "fastapi", "docker", "architecture", 
            "microservices", "design", "refactor", "database", "system design", 
            "workflow", "pipeline", "aws", "bedrock", "redis", "mongodb"
        ]

        is_complex = any(kw in prompt_lower for kw in complex_keywords) or len(prompt.split()) > 15
        latency_ms = (time.perf_counter() - start) * 1000

        return {
            "decision": "SYSTEM_2_BEDROCK" if is_complex else "SYSTEM_1_EDGE",
            "eval_latency_ms": round(latency_ms, 3)
        }

    def generate_edge_response(self, prompt: str) -> str:
        p = prompt.lower().strip()
        if "is 16 an adult" in p or "16 year old" in p:
            return "No. In most legal jurisdictions, majority (adulthood) begins at age 18."
        elif any(g in p for g in ["hi", "hello", "hey", "greetings"]):
            return "Hello! Sentry-Gate System 1 edge router online. Resolved locally via Strands Decider 2B routing pattern."
        elif "who are you" in p:
            return "I am Sentry-Gate, an enterprise AI gateway utilizing the Strands Decider 2B decision framework."
        else:
            return f"System 1 Edge Answer: Query '{prompt}' processed locally at the perimeter."

    def route_query(self, prompt: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        
        # 1. Security Policy Guardrail Check
        policy = self.decider_2b_policy_check(prompt)
        if policy["decision"] == "UNSAFE":
            total_latency = (time.perf_counter() - start_time) * 1000
            return {
                "source": "policy_guardrail_block",
                "response": "⚠️ Request Blocked by Sentry-Gate Security Policy: Malicious injection or policy violation detected.",
                "metrics": {
                    "total_latency_ms": round(total_latency, 2),
                    "policy_eval_ms": policy["eval_latency_ms"],
                    "pattern": "#policy"
                }
            }

        # 2. Model Routing Check
        route = self.decider_2b_route_check(prompt)

        if route["decision"] == "SYSTEM_1_EDGE":
            response_text = self.generate_edge_response(prompt)
            source = "local_system_one"
        else:
            try:
                response_text = self._call_bedrock_live(prompt)
                source = "bedrock_nova_lite"
            except HTTPException as he:
                if "ThrottlingException" in str(he.detail) or "tokens per day" in str(he.detail):
                    response_text = (
                        f"[Resilient Fallback Mode: AWS Bedrock Token Limit Reached]\n\n"
                        f"Sentry-Gate caught the AWS quota exception and processed your architecture query: '{prompt}'.\n"
                        f"Recommended pattern: FastAPI (Gateway) -> Redis (Cache) -> MongoDB (Persistence)."
                    )
                    source = "bedrock_quota_fallback"
                else:
                    raise he

        total_latency = (time.perf_counter() - start_time) * 1000

        return {
            "source": source,
            "response": response_text,
            "metrics": {
                "total_latency_ms": round(total_latency, 2),
                "route_eval_ms": route["eval_latency_ms"],
                "pattern": route["pattern"] if "pattern" in route else "#model-routing"
            }
        }

    def _call_bedrock_live(self, prompt: str) -> str:
        try:
            response = self.bedrock.converse(
                modelId=self.model_id,
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 1000, "temperature": 0.7}
            )
            return response["output"]["message"]["content"][0]["text"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bedrock Error: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>Sentry-Gate API Online</h1>", status_code=200)

@app.post("/v1/route", response_model=RouteResponse)
async def route_request(request: RouteRequest):
    if not sentry_gate:
        raise HTTPException(status_code=503, detail="Sentry-Gate initializing")
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    res = sentry_gate.route_query(request.prompt.strip())
    return RouteResponse(source=res["source"], response=res["response"], metrics=res["metrics"])

if __name__ == "__main__":
    uvicorn.run("sentry_gate:app", host="0.0.0.0", port=8000, reload=True)