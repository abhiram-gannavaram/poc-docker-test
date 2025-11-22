#!/usr/bin/env python3
"""
Simple script to send Trivy JSON report to Bedrock (or mock) and produce a suggested patch file.

Usage:
  python3 scripts/send_to_bedrock.py --report trivy-report.json --model-arn <ARN> --mock true --out suggested_patch.diff

If --mock is true, a sample patch will be written instead of calling Bedrock.

When integrating with Bedrock, replace the mock section with a call to AWS Bedrock runtime API
(e.g., boto3 client for bedrock-runtime or `aws bedrock-runtime invoke-model`), passing a prompt
that instructs the model to output a unified diff to fix the Dockerfile / package.json vulnerabilities.
"""
import argparse
import json
import os
import sys
from datetime import datetime


def make_sample_patch():
    # This sample patch upgrades lodash from 4.17.19 to 4.17.21 and pins Node base image
    patch = """
*** Begin Patch
*** Update File: Dockerfile
@@
-FROM node:12-buster
+FROM node:18-bullseye
@@
-RUN npm install --production
+RUN npm install --production
*** End Patch
*** Begin Patch
*** Update File: package.json
@@
-    "lodash": "4.17.19"
+    "lodash": "4.17.21"
*** End Patch
"""
    return patch


def write_patch_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
    os.chmod(path, 0o644)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', required=True)
    parser.add_argument('--model-arn', required=False)
    parser.add_argument('--mock', required=False, default='true')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    #!/usr/bin/env python3
    """
    Simple script to send Trivy JSON report to Bedrock (or mock) and produce a suggested patch file.

    Usage:
      python3 scripts/send_to_bedrock.py --report trivy-report.json --model-arn <ARN> --mock true --out suggested_patch.diff

    If --mock is true, a sample patch will be written instead of calling Bedrock.

    When integrating with Bedrock, replace the mock section with a call to AWS Bedrock runtime API
    (e.g., boto3 client for bedrock-runtime or `aws bedrock-runtime invoke-model`), passing a prompt
    that instructs the model to output a unified diff to fix the Dockerfile vulnerabilities.
    """
    import argparse
    import json
    import os
    import sys
    from datetime import datetime


def make_sample_patch():
    # This sample patch updates the base image from an outdated Ubuntu 16.04 to a current version
    patch = """
--- Dockerfile.old	2025-11-22 00:00:00.000000000 +0000
+++ Dockerfile	2025-11-22 00:00:00.000000000 +0000
@@ -1,14 +1,14 @@
 # Dockerfile with intentional vulnerabilities
-# Using an extremely outdated base image (Ubuntu 16.04) with known CVEs
-FROM ubuntu:16.04
+# Updated to current LTS base image
+FROM ubuntu:22.04
 
 RUN apt-get update && \\
     apt-get install -y --no-install-recommends \\
-    openssh-server=1:7.3p1-1ubuntu0.1 \\
-    curl=7.47.0-1ubuntu1 \\
-    wget=1.17.1-1ubuntu1.5 \\
-    git=1:2.7.4-0ubuntu1.9 && \\
+    openssh-server \\
+    curl \\
+    wget \\
+    git && \\
     rm -rf /var/lib/apt/lists/*
 
 EXPOSE 22
 
-CMD ["/bin/sh", "-c", "echo 'This image has known OS and library vulnerabilities from 2016'"]
+CMD ["/bin/sh", "-c", "echo 'This image has been patched with updated packages'"]
"""
    return patch
    def write_patch_file(path, content):
        with open(path, 'w') as f:
            f.write(content)
        os.chmod(path, 0o644)


    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument('--report', required=True)
        parser.add_argument('--model-arn', required=False)
        parser.add_argument('--mock', required=False, default='true')
        parser.add_argument('--out', required=True)
        args = parser.parse_args()

        if not os.path.exists(args.report):
            print(f"Trivy report not found: {args.report}")
            sys.exit(1)

        with open(args.report) as f:
            report = json.load(f)

        # Basic heuristic: count vulnerabilities
        vuln_count = 0
        for res in report.get('Results', []):
            vulns = res.get('Vulnerabilities') or []
            vuln_count += len(vulns)

        if vuln_count == 0:
            print("No vulnerabilities found in report. No patch required.")
            # write empty file
            write_patch_file(args.out, "")
            print(f"Wrote empty patch to {args.out}")
            return

        if args.mock.lower() == 'true':
            print(f"Mock mode enabled — generating sample patch for {vuln_count} vulnerabilities")
            patch = make_sample_patch()
            write_patch_file(args.out, patch)
            print(f"Wrote mock suggested patch to {args.out}")
            return

        # Real Bedrock integration (placeholder) — you must implement this to call Bedrock runtime
        # Example (pseudo):
        # prompt = build_prompt_from_trivy(report)
        # response = call_bedrock(model_arn=args.model_arn, prompt=prompt)
        # suggested_diff = extract_diff_from_response(response)
        # write_patch_file(args.out, suggested_diff)

        print("Real Bedrock integration is not implemented in this script. Enable --mock true to test.")
        sys.exit(1)


    if __name__ == '__main__':
        main()

