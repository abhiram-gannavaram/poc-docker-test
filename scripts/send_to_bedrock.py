#!/usr/bin/env python3
"""
scripts/send_to_bedrock.py

Reads a Trivy JSON report and either:
 - In mock mode: writes a sample unified diff patch to --out
 - In real mode: calls AWS Bedrock Runtime (boto3) to generate a suggested unified diff,
   validates that the model output looks like a unified diff, and writes it to --out.

Usage (examples):
  python3 scripts/send_to_bedrock.py --report artifacts/trivy-report.json --model-arn "my-model-id-or-arn" --mock true --out artifacts/suggested_patch.diff
  python3 scripts/send_to_bedrock.py --report artifacts/trivy-report.json --model-arn "my-model-id-or-arn" --mock false --out artifacts/suggested_patch.diff
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Optional

# Optional import; only needed when mock==false and boto3 available
try:
    import boto3  # type: ignore
except Exception:
    boto3 = None  # type: ignore

# Prompt template for Bedrock model. Keep it concise and strict.
PROMPT_TEMPLATE = """
You are a conservative code assistant. Input: a Trivy JSON vulnerability summary.
Your output MUST BE ONLY a git unified diff (a patch) that modifies textual files in the repo
(Dockerfile, package.json, requirements.txt, Pipfile, etc.) to reduce or fix HIGH/CRITICAL
vulnerabilities found by Trivy.

Rules:
- Return ONLY a unified diff (for example with '@@' hunks, or 'diff --git a/... b/...' markers).
- Do NOT include any explanations, reasoning, thinking process, or commentary.
- Do NOT invent binary patches or include secrets.
- Make minimal safe changes and include a short one-line comment in the diff header describing the change.
- If you cannot safely produce a textual patch, return an empty string.
- Start your response immediately with the patch content. Do not include any preamble.

Trivy summary:
{trivy_summary}

Output (patch only):
"""

MOCK_PATCH_EXAMPLE = """*** Begin Patch
*** Update File: Dockerfile
@@
-FROM node:12-buster
+FROM node:18-bullseye
@@
-RUN npm install --production
+RUN npm ci --production
*** End Patch
*** Begin Patch
*** Update File: package.json
@@
-    "lodash": "4.17.19"
+    "lodash": "4.17.21"
*** End Patch
"""

def summarize_trivy(trivy: Dict[str, Any]) -> Dict[str, Any]:
    results = trivy.get("Results", []) or []
    summary = {"total": 0, "high": 0, "critical": 0, "targets": []}
    for r in results:
        target = r.get("Target", "<unknown>")
        vulns = r.get("Vulnerabilities") or []
        total = len(vulns)
        high = sum(1 for v in vulns if (v.get("Severity") or "").upper() == "HIGH")
        crit = sum(1 for v in vulns if (v.get("Severity") or "").upper() == "CRITICAL")
        summary["total"] += total
        summary["high"] += high
        summary["critical"] += crit
        summary["targets"].append({"target": target, "total": total, "high": high, "critical": crit})
    return summary

# Stop sequences to prevent the model from continuing with explanations
STOP_SEQUENCES = ["\n\nHuman:", "Explanation:", "Note:", "Reasoning:", "Here's why:"]

def write_patch_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    try:
        os.chmod(path, 0o644)
    except Exception:
        pass

def call_bedrock(model_arn: str, prompt: str, max_retries: int = 3, backoff: int = 2) -> str:
    if boto3 is None:
        raise RuntimeError("boto3 is required to call Bedrock but is not installed in this environment.")
    client = boto3.client("bedrock-runtime")
    
    # Prepare request body with parameters optimized for Claude models
    # Include stop sequences to prevent the model from continuing with explanations
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.0,  # Use deterministic output
        "stop_sequences": STOP_SEQUENCES
    }
    body_bytes = json.dumps(body).encode("utf-8")
    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            # Use modelId parameter; some deployments accept ARN or modelId string
            resp = client.invoke_model(modelId=model_arn, contentType="application/json", accept="application/json", body=body_bytes)
            b = resp.get("body")
            if hasattr(b, "read"):
                raw = b.read()
            else:
                raw = b
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="replace")
            return raw
        except Exception as e:
            if attempt >= max_retries:
                raise
            time.sleep(backoff * attempt)
    raise RuntimeError("Exhausted retries calling Bedrock")

def looks_like_unified_diff(text: str) -> bool:
    t = text.strip()
    # Accept common patterns: @@ hunks, diff --git, or the script's custom markers
    return ("@@ " in t) or ("diff --git" in t) or ("*** Begin Patch" in t) or (t.startswith("--- ") and "\n+++ " in t)

def extract_possible_text(raw: str) -> str:
    # Attempt to parse JSON wrappers (some model SDKs return JSON)
    raw_str = raw.strip()
    try:
        j = json.loads(raw_str)
        # Handle string wrapped in JSON first
        if isinstance(j, str):
            raw_str = j
        # Claude/Anthropic models return content in a specific format
        elif isinstance(j, dict):
            # Try to extract from Claude's response format
            if "content" in j:
                content = j["content"]
                # Handle both list and direct text formats
                if isinstance(content, list) and len(content) > 0:
                    # Claude returns content as a list of objects with "text" field
                    if isinstance(content[0], dict) and "text" in content[0]:
                        raw_str = content[0]["text"].strip()
                    else:
                        raw_str = str(content[0]).strip()
                elif isinstance(content, str):
                    raw_str = content.strip()
            # Try other common keys
            elif "text" in j and isinstance(j["text"], str):
                raw_str = j["text"].strip()
            elif "output" in j and isinstance(j["output"], str):
                raw_str = j["output"].strip()
            elif "body" in j and isinstance(j["body"], str):
                raw_str = j["body"].strip()
    except Exception:
        pass
    
    # Now strip out any thinking/reasoning text that might appear before the patch
    # Look for common patterns that indicate the start of actual patch content
    lines = raw_str.split('\n')
    patch_start_idx = -1
    
    for idx, line in enumerate(lines):
        # Check if this line looks like the start of a patch
        # Use more specific patterns to avoid false positives
        if (line.startswith('diff --git') or 
            line.startswith('*** Begin Patch') or
            line.startswith('@@') or
            (line.startswith('--- ') and '/' in line) or
            (line.startswith('+++') and idx > 0 and lines[idx-1].startswith('--- '))):
            patch_start_idx = idx
            break
    
    # If we found a patch start, return from that point onward
    if patch_start_idx >= 0:
        return '\n'.join(lines[patch_start_idx:])
    
    return raw_str

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, help="Trivy JSON report path")
    parser.add_argument("--model-arn", required=False, default="", help="Bedrock model Id or ARN")
    parser.add_argument("--mock", required=False, default="true", help="true/false")
    parser.add_argument("--out", required=True, help="Path to write suggested patch (diff)")

    args = parser.parse_args()
    mock = str(args.mock).lower() in ("1", "true", "yes")

    if not os.path.exists(args.report):
        print(f"Trivy report not found: {args.report}", file=sys.stderr)
        write_patch_file(args.out, "")
        sys.exit(0)

    with open(args.report, "r", encoding="utf-8") as fh:
        try:
            report = json.load(fh)
        except Exception as e:
            print(f"Failed to parse trivy report JSON: {e}", file=sys.stderr)
            write_patch_file(args.out, "")
            sys.exit(1)

    summary = summarize_trivy(report)
    print("Trivy summary:", json.dumps(summary, indent=2))

    # If no high/critical, skip (write empty file)
    if (summary.get("high", 0) + summary.get("critical", 0)) == 0:
        print("No HIGH/CRITICAL vulnerabilities found — skipping model call.")
        write_patch_file(args.out, "")
        sys.exit(0)

    # Mock mode: write example patch for testing pipeline behavior
    if mock:
        print("Mock mode enabled — writing example patch to", args.out)
        write_patch_file(args.out, MOCK_PATCH_EXAMPLE)
        sys.exit(0)

    # Real Bedrock invocation
    if not args.model_arn:
        print("ERROR: model-arn is required when --mock is false", file=sys.stderr)
        write_patch_file(args.out, "")
        sys.exit(1)

    prompt = PROMPT_TEMPLATE.format(trivy_summary=json.dumps(summary, indent=2))
    print("Calling Bedrock model:", args.model_arn)

    try:
        raw = call_bedrock(args.model_arn, prompt)
    except Exception as e:
        print("Bedrock call failed:", str(e), file=sys.stderr)
        write_patch_file(args.out, "")
        sys.exit(1)

    candidate = extract_possible_text(raw)

    if not candidate:
        print("Model returned empty output.", file=sys.stderr)
        write_patch_file(args.out, "")
        sys.exit(0)

    # Basic validation: ensure the model output resembles a unified diff
    if not looks_like_unified_diff(candidate):
        print("Model output does not look like a unified diff. Refusing to write patch.", file=sys.stderr)
        # keep a small debug snippet available in a side file for inspection
        debug_path = args.out + ".model_output_preview.txt"
        with open(debug_path, "w", encoding="utf-8") as dbg:
            dbg.write(candidate[:2000])
        print(f"Wrote model preview to {debug_path} (first 2000 chars).", file=sys.stderr)
        write_patch_file(args.out, "")
        sys.exit(1)

    # Save the validated patch
    write_patch_file(args.out, candidate)
    print("Wrote suggested patch to", args.out)
    sys.exit(0)

if __name__ == "__main__":
    main()
