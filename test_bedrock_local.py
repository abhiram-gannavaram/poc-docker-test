#!/usr/bin/env python3
import json
import boto3

def main():
    region = "us-east-1"
    model_id = "qwen.qwen3-coder-30b-a3b-v1:0"

    client = boto3.client("bedrock-runtime", region_name=region)

    print("Calling AWS Bedrock model:", model_id)

    # Qwen on Bedrock uses the messages[] chat schema
    body = {
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ],
        "max_tokens": 200,
        "temperature": 0.2
    }

    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())

    print("\n=== Bedrock Response ===")
    print(result.get("output_text", result))
    

if __name__ == "__main__":
    main()
