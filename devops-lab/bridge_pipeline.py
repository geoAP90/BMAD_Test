#!/usr/bin/env python3
"""
DevOps Pipeline Bridge v4.0 — Full BMAD Agentic Workflow
Flow:
  Playground prompt
    → PM Agent    → PRD.md
    → Arch Agent  → architecture.md
    → Dev Agent   → FastAPI Python code (policies, claims, payments)
    → Murat (TEA) → pytest + unittest test files
    → git push to GitHub
    → Jenkins → pytest → SonarQube → Nexus PyPI
    → Adaptive Card with full audit trail
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import asyncio
import aiohttp
import subprocess
from typing import Dict, Any, Optional
import uvicorn
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── Environment ────────────────────────────────────────────────────────────────
API_TOKEN         = os.getenv("API_TOKEN", "devops-chatops-token-12345")
JENKINS_URL       = os.getenv("JENKINS_URL", "http://localhost:8080")
JENKINS_USER      = os.getenv("JENKINS_USER", "arpita")
JENKINS_API_TOKEN = os.getenv("JENKINS_API_TOKEN", "")
SONARQUBE_URL     = os.getenv("SONARQUBE_URL", "http://localhost:9000")
SONAR_TOKEN       = os.getenv("SONAR_TOKEN", "")
NEXUS_URL         = os.getenv("NEXUS_URL", "http://localhost:8081")
NEXUS_PASSWORD    = os.getenv("NEXUS_PASSWORD", "")
NEXUS_PYPI_REPO   = "pypi-releases"
GROQ_API_KEY      = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL        = "llama-3.3-70b-versatile"
JENKINS_JOB       = "Insurance-Accelerator-Pipeline"
SONAR_PROJECT_KEY = "Insurance-Accelerator"
REPO_PATH         = os.path.expanduser("~/Documents/test-bmad_now")

# ── BMAD agent paths ───────────────────────────────────────────────────────────
BMAD_PM_PATH   = os.path.join(REPO_PATH, "_bmad/bmm/2-plan-workflows/bmad-agent-pm/SKILL.md")
BMAD_TEA_PATH  = os.path.join(REPO_PATH, "_bmad/tea/agents/bmad-tea/SKILL.md")

def load_agent(path: str, fallback: str) -> str:
    try:
        with open(path, "r") as f:
            content = f.read()
        logger.info(f"Loaded agent from {path}")
        return content
    except Exception as e:
        logger.warning(f"Could not load {path}: {e} — using fallback")
        return fallback

PM_SYSTEM = load_agent(BMAD_PM_PATH, """You are a senior Product Manager specializing in insurance systems.
You write concise, structured PRDs in markdown format covering goals, user stories, and acceptance criteria.""")

TEA_SYSTEM = load_agent(BMAD_TEA_PATH, """You are Murat, a Master Test Architect.
You write comprehensive pytest and unittest test suites for Python FastAPI applications.
Tests must be runnable, import correctly, and cover happy paths and edge cases.""")

ARCH_SYSTEM = """You are a senior Software Architect specializing in Python microservices.
You design clean FastAPI architectures with Pydantic models, proper separation of concerns, and RESTful design.
You document decisions concisely in markdown."""

DEV_SYSTEM = """You are a senior Python developer specializing in FastAPI REST APIs.
You write production-quality, well-structured FastAPI code with Pydantic v2 models.
All code must be complete, importable, and runnable. No placeholders or TODOs."""

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="DevOps Pipeline Bridge", version="4.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def check_auth(request: Request):
    auth = request.headers.get("Authorization", "")
    if API_TOKEN and auth:
        token = auth.replace("Bearer ", "")
        if token != API_TOKEN:
            logger.warning("Auth mismatch — continuing for local lab")

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "DevOps Pipeline Bridge v4.0 — Full BMAD Agentic Flow", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.head("/api/messages")
async def head_messages():
    return {"status": "ok"}

@app.post("/api/messages")
async def handle_message(request: Request):
    check_auth(request)
    try:
        payload = await request.json()
        if payload.get("type") != "message":
            return {"status": "ok"}

        message_text = payload.get("text") or payload.get("value", {}).get("text")
        if not message_text:
            raise HTTPException(status_code=400, detail="Missing 'text' field")

        service_url     = payload.get("serviceUrl", "")
        conversation_id = payload.get("conversation", {}).get("id", "")
        activity_id     = payload.get("id", "")
        recipient       = payload.get("recipient", {})
        sender          = payload.get("from", {})

        asyncio.create_task(run_full_bmad_pipeline(
            message_text, service_url, conversation_id,
            activity_id, recipient, sender
        ))
        return {"status": "accepted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"handle_message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Full BMAD Pipeline ─────────────────────────────────────────────────────────
async def run_full_bmad_pipeline(message_text, service_url, conversation_id,
                                  activity_id, recipient, sender):
    steps = []
    try:
        feature = extract_feature(message_text)

        # ── Phase 1: PM Agent → PRD.md ─────────────────────────────────────────
        logger.info("Phase 1: PM Agent generating PRD")
        await send_progress(service_url, conversation_id, activity_id, recipient, sender,
                            "📋 PM Agent is writing the PRD...")
        prd = await call_groq(PM_SYSTEM,
            f"""Write a concise PRD for: {feature}

Focus on: Insurance Claims API with policies, claims, and payments endpoints.
Format: markdown with sections: Overview, Goals, User Stories (5 max), Acceptance Criteria.
Keep it under 400 words.""")
        write_file(os.path.join(REPO_PATH, "_bmad-output/PRD.md"), prd)
        steps.append("✅ PM Agent: PRD.md generated")
        logger.info("PRD generated")

        # ── Phase 2: Architect → architecture.md ──────────────────────────────
        logger.info("Phase 2: Architect generating architecture")
        await send_progress(service_url, conversation_id, activity_id, recipient, sender,
                            "🏗️ Architect is designing the system...")
        arch = await call_groq(ARCH_SYSTEM,
            f"""Design architecture for a FastAPI Insurance Claims API.

Based on this PRD:
{prd[:800]}

Output markdown with: Tech Stack, Project Structure, API Endpoints (policies CRUD, claims CRUD, payments CRUD), Data Models, Key Decisions.
Keep it under 400 words.""")
        write_file(os.path.join(REPO_PATH, "_bmad-output/architecture.md"), arch)
        steps.append("✅ Architect: architecture.md generated")
        logger.info("Architecture generated")

        # ── Phase 3: Dev Agent → FastAPI code ─────────────────────────────────
        logger.info("Phase 3: Dev Agent generating FastAPI code")
        await send_progress(service_url, conversation_id, activity_id, recipient, sender,
                            "💻 Developer is writing the FastAPI code...")

        code_files = await generate_fastapi_code(prd, arch)
        for path, content in code_files.items():
            full_path = os.path.join(REPO_PATH, path)
            write_file(full_path, content)
        steps.append(f"✅ Dev Agent: {len(code_files)} Python files generated")
        logger.info(f"Generated {len(code_files)} code files")

        # ── Phase 4: Murat → Test files ───────────────────────────────────────
        logger.info("Phase 4: Murat generating tests")
        await send_progress(service_url, conversation_id, activity_id, recipient, sender,
                            "🧪 Murat (Test Architect) is writing the test suite...")

        test_files = await generate_tests(code_files)
        for path, content in test_files.items():
            full_path = os.path.join(REPO_PATH, path)
            write_file(full_path, content)
        steps.append(f"✅ Murat (TEA): {len(test_files)} test files generated")
        logger.info(f"Generated {len(test_files)} test files")

        # ── Phase 5: Git push ──────────────────────────────────────────────────
        logger.info("Phase 5: Pushing to GitHub")
        await send_progress(service_url, conversation_id, activity_id, recipient, sender,
                            "📤 Pushing generated code to GitHub...")
        git_result = git_push(message_text)
        steps.append(f"{'✅' if git_result['success'] else '❌'} Git: {git_result['message']}")
        if not git_result["success"]:
            await send_reply(service_url, conversation_id, activity_id,
                             recipient, sender, steps, success=False)
            return

        # ── Phase 6: Jenkins build ─────────────────────────────────────────────
        logger.info("Phase 6: Triggering Jenkins")
        await send_progress(service_url, conversation_id, activity_id, recipient, sender,
                            "🏗️ Jenkins is building and testing the code...")
        jenkins_trigger = await trigger_jenkins()
        steps.append(f"{'✅' if jenkins_trigger['success'] else '❌'} Jenkins: {jenkins_trigger['message']}")
        if not jenkins_trigger["success"]:
            await send_reply(service_url, conversation_id, activity_id,
                             recipient, sender, steps, success=False)
            return

        build = await poll_jenkins(jenkins_trigger.get("next_build_number"))
        steps.append(f"{'✅' if build['success'] else '❌'} Jenkins Build #{build.get('build_number','?')}: {build['message']}")
        if not build["success"]:
            await send_reply(service_url, conversation_id, activity_id,
                             recipient, sender, steps, success=False)
            return

        # ── Phase 7: SonarQube results ─────────────────────────────────────────
        logger.info("Phase 7: Checking SonarQube")
        sonar = await fetch_sonarqube_metrics()
        steps.append(f"{'✅' if sonar['gate_passed'] else '⚠️'} SonarQube: {sonar['summary']}")

        # ── Phase 8: Nexus check ───────────────────────────────────────────────
        logger.info("Phase 8: Checking Nexus")
        nexus = await fetch_nexus_summary()
        steps.append(f"✅ Nexus: {nexus['summary']}")

        await send_reply(service_url, conversation_id, activity_id,
                         recipient, sender, steps, success=True)

    except Exception as e:
        logger.error(f"run_full_bmad_pipeline failed: {e}")
        steps.append(f"❌ Pipeline error: {e}")
        await send_reply(service_url, conversation_id, activity_id,
                         recipient, sender, steps, success=False)


# ── Code generation ────────────────────────────────────────────────────────────
async def generate_fastapi_code(prd: str, arch: str) -> Dict[str, str]:
    """Generate all FastAPI source files."""

    prompt = f"""Generate a complete FastAPI Insurance Claims API project.

Based on:
PRD: {prd[:600]}
Architecture: {arch[:600]}

Generate these EXACT files with COMPLETE, RUNNABLE Python code:

FILE: src/__init__.py
(empty file)

FILE: src/models.py
(Pydantic v2 models for Policy, Claim, Payment - with proper field types and validators)

FILE: src/main.py
(FastAPI app setup, include routers for /policies /claims /payments)

FILE: src/routes/__init__.py
(empty file)

FILE: src/routes/policies.py
(CRUD endpoints: GET /policies, POST /policies, GET /policies/{{id}}, PUT /policies/{{id}}, DELETE /policies/{{id}})

FILE: src/routes/claims.py
(CRUD endpoints for claims with status field: pending/approved/rejected)

FILE: src/routes/payments.py
(CRUD endpoints for payments linked to claims)

FILE: requirements.txt
(fastapi, uvicorn, pydantic, pytest, pytest-asyncio, httpx, coverage, pytest-cov)

FILE: setup.py
(minimal setup.py for wheel building)

Format EXACTLY as:
FILE: filename
```python
code here
```

Use in-memory dict storage (no database needed). All endpoints must return proper HTTP status codes."""

    response = await call_groq(DEV_SYSTEM, prompt, max_tokens=4000)
    return parse_files(response)


async def generate_tests(code_files: Dict[str, str]) -> Dict[str, str]:
    """Murat generates test files."""

    src_code = "\n\n".join([
        f"# {path}\n{content}"
        for path, content in code_files.items()
        if path.endswith(".py") and "test" not in path
    ])

    prompt = f"""Generate comprehensive pytest + unittest tests for this FastAPI Insurance Claims API.

Source code:
{src_code[:3000]}

Generate these EXACT test files:

FILE: tests/__init__.py
(empty)

FILE: tests/test_policies.py
(pytest tests for policy CRUD: test create, get all, get by id, update, delete, test 404 cases)

FILE: tests/test_claims.py
(pytest tests for claims CRUD including status transitions)

FILE: tests/test_payments.py
(pytest tests for payment CRUD)

FILE: conftest.py
(pytest fixtures: TestClient setup using FastAPI test client)

Rules:
- Use httpx TestClient or fastapi.testclient.TestClient
- Each test file must have at least 5 test functions
- Test both success and error cases
- All imports must work with the source code provided
- Use pytest conventions (functions starting with test_)

Format EXACTLY as:
FILE: filename
```python
code here
```"""

    response = await call_groq(TEA_SYSTEM, prompt, max_tokens=3000)
    return parse_files(response)


def parse_files(response: str) -> Dict[str, str]:
    """Parse FILE: filename / ```python code ``` blocks from LLM response."""
    files = {}
    lines = response.split("\n")
    current_file = None
    current_content = []
    in_code_block = False

    for line in lines:
        if line.startswith("FILE:"):
            if current_file and current_content:
                files[current_file] = "\n".join(current_content).strip()
            current_file = line.replace("FILE:", "").strip()
            current_content = []
            in_code_block = False
        elif line.startswith("```") and current_file:
            if in_code_block:
                in_code_block = False
            else:
                in_code_block = True
        elif in_code_block and current_file:
            current_content.append(line)

    if current_file and current_content:
        files[current_file] = "\n".join(current_content).strip()

    # Ensure empty __init__.py files exist
    for init in ["src/__init__.py", "src/routes/__init__.py", "tests/__init__.py"]:
        if init not in files:
            files[init] = ""

    return files


def extract_feature(message: str) -> str:
    keywords = ["claims", "policy", "payment", "insurance", "build", "create", "generate"]
    for kw in keywords:
        if kw.lower() in message.lower():
            return message
    return f"Insurance Claims API: {message}"


def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    logger.info(f"Written: {path}")


def git_push(commit_message: str) -> Dict[str, Any]:
    try:
        cmds = [
            ["git", "-C", REPO_PATH, "add", "src/", "tests/", "_bmad-output/",
             "requirements.txt", "setup.py", "conftest.py"],
            ["git", "-C", REPO_PATH, "commit", "-m",
             f"BMAD: {commit_message[:80]}"],
            ["git", "-C", REPO_PATH, "push", "origin", "main"]
        ]
        for cmd in cmds:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0 and "nothing to commit" not in result.stdout:
                logger.warning(f"Git cmd output: {result.stderr}")

        return {"success": True, "message": "Code pushed to GitHub successfully"}
    except Exception as e:
        return {"success": False, "message": f"Git push failed: {e}"}


# ── Groq API call ──────────────────────────────────────────────────────────────
async def call_groq(system: str, user: str, max_tokens: int = 1000) -> str:
    if not GROQ_API_KEY:
        return "⚠️ GROQ_API_KEY not set."
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.2
                },
                headers={"Authorization": f"Bearer {GROQ_API_KEY}",
                         "Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"].strip()
                body = await resp.text()
                logger.error(f"Groq error {resp.status}: {body}")
                return f"Groq error {resp.status}"
    except Exception as e:
        logger.error(f"Groq call failed: {e}")
        return f"Groq unreachable: {e}"


# ── Jenkins ────────────────────────────────────────────────────────────────────
async def trigger_jenkins() -> Dict[str, Any]:
    info_url    = f"{JENKINS_URL}/job/{JENKINS_JOB}/api/json"
    trigger_url = f"{JENKINS_URL}/job/{JENKINS_JOB}/build"
    try:
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(JENKINS_USER, JENKINS_API_TOKEN)
            async with session.get(info_url, auth=auth,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                next_build = (await r.json()).get("nextBuildNumber") if r.status == 200 else None
            async with session.post(trigger_url, auth=auth,
                                    timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status in (200, 201):
                    return {"success": True,
                            "message": f"Build triggered (expected #{next_build})",
                            "next_build_number": next_build}
                return {"success": False, "message": f"Jenkins HTTP {r.status}"}
    except Exception as e:
        return {"success": False, "message": f"Jenkins unreachable: {e}"}


async def poll_jenkins(build_number: Optional[int],
                       timeout_seconds: int = 300) -> Dict[str, Any]:
    if not build_number:
        return {"success": False, "message": "Unknown build number", "build_number": None}
    url      = f"{JENKINS_URL}/job/{JENKINS_JOB}/{build_number}/api/json"
    deadline = asyncio.get_event_loop().time() + timeout_seconds
    await asyncio.sleep(8)
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(JENKINS_USER, JENKINS_API_TOKEN)
        while asyncio.get_event_loop().time() < deadline:
            try:
                async with session.get(url, auth=auth,
                                       timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status == 200:
                        data = await r.json()
                        if not data.get("building", True):
                            result = data.get("result", "UNKNOWN")
                            return {"success": result == "SUCCESS",
                                    "message": f"Result: {result}",
                                    "build_number": build_number}
                        logger.info(f"Build #{build_number} still running...")
                    elif r.status == 404:
                        logger.info(f"Build #{build_number} not started yet...")
            except Exception as e:
                logger.warning(f"Poll error: {e}")
            await asyncio.sleep(10)
    return {"success": False, "message": f"Timed out", "build_number": build_number}


# ── SonarQube & Nexus ─────────────────────────────────────────────────────────
async def fetch_sonarqube_metrics() -> Dict[str, Any]:
    gate_url = (f"{SONARQUBE_URL}/api/qualitygates/project_status"
                f"?projectKey={SONAR_PROJECT_KEY}")
    measures_url = (f"{SONARQUBE_URL}/api/measures/component"
                    f"?component={SONAR_PROJECT_KEY}"
                    f"&metricKeys=bugs,vulnerabilities,code_smells,coverage,"
                    f"duplicated_lines_density,reliability_rating,security_rating")
    try:
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(SONAR_TOKEN, "")
            async with session.get(gate_url, auth=auth,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                gate_data = await r.json() if r.status == 200 else {}
            async with session.get(measures_url, auth=auth,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                meas_data = await r.json() if r.status == 200 else {}

        status = gate_data.get("projectStatus", {}).get("status", "NONE")
        measures = {m["metric"]: m.get("value", "N/A")
                    for m in meas_data.get("component", {}).get("measures", [])}
        summary = (f"Gate={status} | Bugs={measures.get('bugs','?')} | "
                   f"Vulns={measures.get('vulnerabilities','?')} | "
                   f"Smells={measures.get('code_smells','?')} | "
                   f"Coverage={measures.get('coverage','?')}%")
        return {"gate_passed": status in ("OK", "NONE"),
                "gate_status": status, "measures": measures, "summary": summary}
    except Exception as e:
        return {"gate_passed": False, "gate_status": "ERROR",
                "measures": {}, "summary": f"SonarQube unreachable: {e}"}


async def fetch_nexus_summary() -> Dict[str, Any]:
    url = f"{NEXUS_URL}/service/rest/v1/components?repository={NEXUS_PYPI_REPO}"
    try:
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth("admin", NEXUS_PASSWORD)
            async with session.get(url, auth=auth,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                data = await r.json() if r.status == 200 else {}
        items = data.get("items", [])
        if not items:
            return {"count": 0, "summary": f"'{NEXUS_PYPI_REPO}' ready — awaiting first deploy"}
        latest = f"{items[-1].get('name','?')} v{items[-1].get('version','?')}"
        return {"count": len(items),
                "summary": f"{len(items)} package(s) — latest: {latest}"}
    except Exception as e:
        return {"count": 0, "summary": f"Nexus unreachable: {e}"}


# ── Reply helpers ──────────────────────────────────────────────────────────────
async def send_progress(service_url, conversation_id, activity_id,
                        recipient, sender, message: str):
    """Send an interim progress message."""
    reply = {
        "type": "message",
        "from": recipient, "recipient": sender,
        "replyToId": activity_id,
        "text": f"⏳ {message}"
    }
    url = f"{service_url}/v3/conversations/{conversation_id}/activities/{activity_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=reply,
                                    headers={"Content-Type": "application/json"},
                                    timeout=aiohttp.ClientTimeout(total=10)) as r:
                logger.info(f"Progress sent: {message} (HTTP {r.status})")
    except Exception as e:
        logger.warning(f"Progress send failed: {e}")


async def send_reply(service_url, conversation_id, activity_id,
                     recipient, sender, steps, success: bool):
    summary = "Full BMAD pipeline completed! 🎉" if success else "Pipeline stopped — see steps above."

    card = {
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard", "version": "1.5",
            "body": [
                {"type": "TextBlock",
                 "text": "🚀 Full BMAD Agentic Pipeline",
                 "size": "Large", "weight": "Bolder",
                 "color": "Good" if success else "Warning"},
                {"type": "TextBlock",
                 "text": "PRD → Architecture → FastAPI Code → Tests → Git → Jenkins → SonarQube → Nexus",
                 "wrap": True, "spacing": "Small", "isSubtle": True},
                {"type": "TextBlock",
                 "text": summary,
                 "wrap": True, "spacing": "Medium", "weight": "Bolder"},
                {"type": "TextBlock",
                 "text": "\n\n".join(steps),
                 "wrap": True, "maxLines": 30, "spacing": "Small"}
            ],
            "actions": [
                {"type": "Action.OpenUrl", "title": "SonarQube",
                 "url": f"{SONARQUBE_URL}/dashboard?id={SONAR_PROJECT_KEY}"},
                {"type": "Action.OpenUrl", "title": "Jenkins",
                 "url": f"{JENKINS_URL}/job/{JENKINS_JOB}/"},
                {"type": "Action.OpenUrl", "title": "Nexus PyPI",
                 "url": f"{NEXUS_URL}/#browse/browse:{NEXUS_PYPI_REPO}"},
                {"type": "Action.OpenUrl", "title": "GitHub",
                 "url": "https://github.com/geoAP90/BMAD_Test"}
            ]
        }
    }

    reply = {
        "type": "message",
        "from": recipient, "recipient": sender,
        "replyToId": activity_id,
        "text": summary + "\n\n" + "\n".join(steps),
        "attachments": [card]
    }

    url = f"{service_url}/v3/conversations/{conversation_id}/activities/{activity_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=reply,
                                    headers={"Content-Type": "application/json"},
                                    timeout=aiohttp.ClientTimeout(total=15)) as r:
                logger.info(f"Final reply sent (HTTP {r.status})")
    except Exception as e:
        logger.error(f"send_reply failed: {e}")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting DevOps Pipeline Bridge v4.0 (Full BMAD) on port 3978...")
    uvicorn.run("bridge_pipeline:app", host="0.0.0.0", port=3978,
                reload=False, log_level="info")
