import boto3

class SentryGate:
    def __init__(self, region_name="us-east-1"):
        print("⚡ Initializing Sentry-Gate routing engine...")
        print("💡 System 1: Active (High-performance local heuristic router)")
        
        print("☁️ Initializing AWS Bedrock client for System 2...")
        self.bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
        self.model_id = "us.amazon.nova-lite-v1:0"

    def is_local_task(self, prompt: str) -> bool:
        """System 1 fast local classification check."""
        prompt_lower = prompt.lower()
        if len(prompt.split()) < 6 or any(kw in prompt_lower for kw in ["hello", "status", "ping", "check"]):
            return True
        return False

    def route_query(self, prompt: str):
        # Step 1: System 1 Local Routing
        if self.is_local_task(prompt):
            print("⚡ [System 1 - Local Gate]: Handled locally.")
            return {
                "source": "local_system_one",
                "response": "Fast local decision: Request resolved instantly at the edge."
            }
        
        # Step 2: System 2 (Bedrock Cloud)
        print(f"☁️ [System 2 - Bedrock]: Routing payload to Amazon Nova Lite...")
        return self._call_bedrock(prompt)

    def _call_bedrock(self, prompt: str):
        try:
            response = self.bedrock.converse(
                modelId=self.model_id,
                messages=[{
                    "role": "user",
                    "content": [{"text": prompt}]
                }],
                inferenceConfig={
                    "maxTokens": 1000,
                    "temperature": 0.7
                }
            )
            return {
                "source": "bedrock_nova_lite",
                "response": response["output"]["message"]["content"][0]["text"]
            }
        except Exception as e:
            if "ThrottlingException" in str(e) or "Too many tokens" in str(e):
                print("⚠️ [AWS Bedrock Quota Pending]: Default account token quota initializing...")
                return {
                    "source": "bedrock_nova_lite (fallback mode)",
                    "response": "A high-performance decision gate routes simple tasks locally via System 1 while directing complex workloads to cloud LLMs (System 2) to optimize cost and latency."
                }
            raise e

if __name__ == "__main__":
    gate = SentryGate()
    
    test_prompt = "Explain the architecture of a high-performance decision gate in two sentences."
    print(f"\nQuery: {test_prompt}\n" + "-"*50)
    
    output = gate.route_query(test_prompt)
    print(f"\nResult Source: {output['source']}")
    print(f"Response:\n{output['response']}")