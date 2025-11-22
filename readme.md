# Auto-fix Docker Vulnerabilities Workflow

This repository demonstrates an automated flow for detecting and auto-fixing Docker image vulnerabilities using Trivy and AWS Bedrock (Anthropic Sonnet).

High level flow
- Build a Docker image (the repo includes a deliberately old base image to produce OS-level vulnerabilities)
- Scan it with Trivy
- Send findings to AWS Bedrock for suggested fixes (mock mode available for testing)
- Apply suggested patch in a new branch
- Rebuild and rescan the patched image
- Open a Pull Request if fixes are applied

Important notes
- The repository uses `MOCK_BEDROCK=true` by default so you can test the full flow without calling AWS Bedrock.
- To call real Bedrock, set `MOCK_BEDROCK=false` and set `BEDROCK_MODEL_ARN` in the workflow to the exact model ARN.
- IAM role: `arn:aws:iam::362015461740:role/bedrock-test-role` has been created and the required policy is already attached — no further IAM changes are necessary in this repo.

Files
- `Dockerfile`: a deliberately vulnerable image using Ubuntu 16.04 (EOL, with many known CVEs) and pinned outdated packages (curl 7.47, wget 1.17, openssh-server 7.3, git 2.7).
- `.github/workflows/auto-fix-vulns.yml`: the workflow that runs the scan/fix flow (it uses the role `arn:aws:iam::362015461740:role/bedrock-test-role`).
- `scripts/send_to_bedrock.py`: script that either mocks suggestions or (placeholder) would call Bedrock to get a unified-diff patch. In mock mode it suggests updating the Dockerfile base image and package versions.

How the mock suggestion works
- `send_to_bedrock.py` will produce a unified diff patch that updates the Dockerfile: changes Ubuntu 16.04 to 22.04 (current LTS) and removes pinned package versions to allow the package manager to pull patched versions.

How to test locally
1. Build the image:

```bash
docker build -t vuln-sample:latest .
```

2. Run Trivy locally (install Trivy first):

```bash
trivy image --format json -o trivy-report.json vuln-sample:latest
python3 scripts/send_to_bedrock.py --report trivy-report.json --mock true --out suggested_patch.diff
cat suggested_patch.diff
```

3. Apply the patch locally

```bash
git checkout -b test-auto-fix
# if the patch is in unified diff format, use `git apply`:
# git apply suggested_patch.diff
```

Enabling real Bedrock
- Replace `BEDROCK_MODEL_ARN` in `.github/workflows/auto-fix-vulns.yml` with the exact model ARN from the Bedrock console.
- Set `MOCK_BEDROCK` to `false`.
- Implement the Bedrock calling logic in `scripts/send_to_bedrock.py` (see comments). The workflow already assumes the role `arn:aws:iam::362015461740:role/bedrock-test-role` to perform the Bedrock invocation.

Security
- Do NOT commit AWS credentials to the repository. Use GitHub Secrets and an assumable role (the repo uses `arn:aws:iam::362015461740:role/bedrock-test-role`).

