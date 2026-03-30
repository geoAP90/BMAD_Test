#!/usr/bin/env python3
"""
DevOps Pipeline Bridge v3.1 — BMAD Powered
Flow: Playground → Gather real data → Murat (BMAD/Groq) → Jenkins → SonarQube → Nexus
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import asyncio
import aiohttp
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
NEXUS_REPOSITORY  = os.getenv("NEXUS_REPOSITORY", "maven-releases_06")
GROQ_API_KEY      = os.getenv("GROQ_API_KEY", "")
JENKINS_JOB       = "Insurance-Accelerator-Pipeline"
SONAR_PROJECT_KEY = "Insurance-Accelerator"

BMAD_AGENT_PATH = os.path.expanduser(
    "~/Documents/test-bmad_now/_bmad/tea/agents/bmad-tea/SKILL.md"
)

# ── Load BMAD agent ────────────────────────────────────────────────────────────
def load_bmad_agent() -> str:
    try:
        with open(BMAD_AGENT_PATH, "r") as f:
            content = f.read()
        logger.info("BMAD agent (Murat) loaded successfully")
        return content
    except Exception as e:
        logger.warning(f"Could not load BMAD agent file: {e}")
        return """You are Murat, a Master Test Architect and Quality Advisor.
You specialize in risk-based testing, CI/CD governance, and scalable quality gates.
Always base your analysis on the real infrastructure data provided to you."""

BMAD_SYSTEM_PROMPT = load_bmad_agent()

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="DevOps Pipeline Bridge", version="3.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

def check_auth(request: Request):
    auth = request.headers.get("Authorization", "")
    if API_TOKEN and auth:
        token = auth.replace("Bearer ", "")
        if token != API_TOKEN:
            logger.warning("Auth token mismatch — continuing for local lab")

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "DevOps Pipeline Bridge v3.1 — real-data BMAD", "status": "healthy"}

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

        asyncio.create_task(run_pipeline(
            message_text, service_url, conversation_id,
            activity_id, recipient, sender
        ))
        return {"status": "accepted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"handle_message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Main pipeline ──────────────────────────────────────────────────────────────
async def run_pipeline(message_text, service_url, conversation_id,
                       activity_id, recipient, sender):
    try:
        steps = []

        # ── Step 1: Collect REAL data from all services ────────────────────────
        logger.info("Step 1: Collecting real infrastructure data")
        sonar_data, nexus_data, jenkins_data = await asyncio.gather(
            fetch_sonarqube_metrics(),
            fetch_nexus_summary(),
            fetch_last_jenkins_build(),
        )

        # ── Step 2: Murat analyses using REAL data ─────────────────────────────
        logger.info("Step 2: Murat analysing real infrastructure data")
        murat = await invoke_murat(message_text, sonar_data, nexus_data, jenkins_data)
        steps.append(f"🤖 **Murat (BMAD Test Architect) — data-driven assessment:**\n{murat}")

        # ── Step 3: Show real pre-build state ──────────────────────────────────
        steps.append(
            f"📊 **Pre-build snapshot:**\n"
            f"• SonarQube: {sonar_data['summary']}\n"
            f"• Last Jenkins build: {jenkins_data['summary']}\n"
            f"• Nexus: {nexus_data['summary']}"
        )

        # ── Step 4: Trigger Jenkins ────────────────────────────────────────────
        logger.info("Step 3: Triggering Jenkins")
        jenkins_trigger = await trigger_jenkins_build()
        steps.append(
            f"{'✅' if jenkins_trigger['success'] else '❌'} "
            f"Jenkins: {jenkins_trigger['message']}"
        )
        if not jenkins_trigger["success"]:
            await send_reply(service_url, conversation_id, activity_id,
                             recipient, sender, steps, success=False)
            return

        # ── Step 5: Poll until done ────────────────────────────────────────────
        logger.info("Step 4: Polling Jenkins build")
        build = await poll_jenkins_build(jenkins_trigger.get("next_build_number"))
        steps.append(
            f"{'✅' if build['success'] else '❌'} "
            f"Jenkins Build #{build.get('build_number','?')}: {build['message']}"
        )
        if not build["success"]:
            await send_reply(service_url, conversation_id, activity_id,
                             recipient, sender, steps, success=False)
            return

        # ── Step 6: Post-build SonarQube ──────────────────────────────────────
        logger.info("Step 5: Post-build SonarQube check")
        sonar_post = await fetch_sonarqube_metrics()
        steps.append(
            f"{'✅' if sonar_post['gate_passed'] else '⚠️'} "
            f"SonarQube (post-build): {sonar_post['summary']}"
        )

        # ── Step 7: Nexus artifact check ──────────────────────────────────────
        logger.info("Step 6: Nexus artifact check")
        nexus_post = await fetch_nexus_summary()
        steps.append(f"✅ Nexus: {nexus_post['summary']}")

        await send_reply(service_url, conversation_id, activity_id,
                         recipient, sender, steps, success=True)

    except Exception as e:
        logger.error(f"run_pipeline failed: {e}")


# ── Real data collectors ───────────────────────────────────────────────────────
async def fetch_sonarqube_metrics() -> Dict[str, Any]:
    """Fetch real SonarQube quality gate + measures."""
    gate_url     = f"{SONARQUBE_URL}/api/qualitygates/project_status?projectKey={SONAR_PROJECT_KEY}"
    measures_url = (f"{SONARQUBE_URL}/api/measures/component"
                    f"?component={SONAR_PROJECT_KEY}"
                    f"&metricKeys=bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density,reliability_rating,security_rating")
    try:
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(SONAR_TOKEN, "")
            async with session.get(gate_url, auth=auth,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                gate_data  = await r.json() if r.status == 200 else {}
            async with session.get(measures_url, auth=auth,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                meas_data  = await r.json() if r.status == 200 else {}

        gate_status = gate_data.get("projectStatus", {}).get("status", "NONE")
        gate_passed = gate_status in ("OK", "NONE")

        measures = {}
        for m in meas_data.get("component", {}).get("measures", []):
            measures[m["metric"]] = m.get("value", "N/A")

        summary = (
            f"Gate={gate_status} | "
            f"Bugs={measures.get('bugs','?')} | "
            f"Vulns={measures.get('vulnerabilities','?')} | "
            f"Smells={measures.get('code_smells','?')} | "
            f"Coverage={measures.get('coverage','?')}% | "
            f"Duplication={measures.get('duplicated_lines_density','?')}%"
        )
        return {"gate_passed": gate_passed, "gate_status": gate_status,
                "measures": measures, "summary": summary}

    except Exception as e:
        logger.error(f"SonarQube fetch failed: {e}")
        return {"gate_passed": False, "gate_status": "ERROR",
                "measures": {}, "summary": f"SonarQube unreachable: {e}"}


async def fetch_nexus_summary() -> Dict[str, Any]:
    """Fetch real Nexus artifact list."""
    url = f"{NEXUS_URL}/service/rest/v1/components?repository={NEXUS_REPOSITORY}"
    try:
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth("admin", NEXUS_PASSWORD)
            async with session.get(url, auth=auth,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                data = await r.json() if r.status == 200 else {}

        items   = data.get("items", [])
        count   = len(items)
        if count == 0:
            summary = f"Repository '{NEXUS_REPOSITORY}' empty — no artifacts yet"
            latest  = None
        else:
            latest  = f"{items[-1].get('name','?')} v{items[-1].get('version','?')}"
            summary = f"{count} artifact(s) in '{NEXUS_REPOSITORY}' — latest: {latest}"

        return {"count": count, "latest": latest, "summary": summary}

    except Exception as e:
        logger.error(f"Nexus fetch failed: {e}")
        return {"count": 0, "latest": None, "summary": f"Nexus unreachable: {e}"}


async def fetch_last_jenkins_build() -> Dict[str, Any]:
    """Fetch real last Jenkins build result + test counts."""
    url = f"{JENKINS_URL}/job/{JENKINS_JOB}/lastBuild/api/json"
    try:
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(JENKINS_USER, JENKINS_API_TOKEN)
            async with session.get(url, auth=auth,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                data = await r.json() if r.status == 200 else {}

        number   = data.get("number", "?")
        result   = data.get("result", "UNKNOWN")
        duration = round(data.get("duration", 0) / 1000, 1)
        summary  = f"Build #{number} → {result} ({duration}s)"
        return {"number": number, "result": result,
                "duration": duration, "summary": summary}

    except Exception as e:
        logger.error(f"Jenkins last build fetch failed: {e}")
        return {"number": "?", "result": "UNKNOWN",
                "duration": 0, "summary": f"Jenkins unreachable: {e}"}


# ── Murat with real data ───────────────────────────────────────────────────────
async def invoke_murat(user_request: str,
                       sonar: Dict, nexus: Dict, jenkins: Dict) -> str:
    if not GROQ_API_KEY:
        return "⚠️ GROQ_API_KEY not set — skipping BMAD analysis."

    groq_prompt = f"""You are performing a pre-pipeline quality gate review for the Insurance Accelerator.

USER REQUEST: "{user_request}"

REAL INFRASTRUCTURE DATA (fetched live right now):

SonarQube:
- Quality Gate: {sonar['gate_status']}
- Bugs: {sonar['measures'].get('bugs', 'N/A')}
- Vulnerabilities: {sonar['measures'].get('vulnerabilities', 'N/A')}
- Code Smells: {sonar['measures'].get('code_smells', 'N/A')}
- Test Coverage: {sonar['measures'].get('coverage', 'N/A')}%
- Code Duplication: {sonar['measures'].get('duplicated_lines_density', 'N/A')}%
- Security Rating: {sonar['measures'].get('security_rating', 'N/A')}
- Reliability Rating: {sonar['measures'].get('reliability_rating', 'N/A')}

Last Jenkins Build:
- Build #{jenkins['number']} — Result: {jenkins['result']}
- Duration: {jenkins['duration']}s

Nexus Repository ({NEXUS_REPOSITORY}):
- Artifacts deployed: {nexus['count']}
- Latest artifact: {nexus['latest'] or 'none yet'}

Based ONLY on this real data, provide:
1. A data-driven risk assessment (what the numbers actually tell you)
2. Your recommendation: PROCEED / PROCEED WITH CAUTION / BLOCK — with specific reason from the data
3. One concrete action to improve quality based on what you see

Be specific to the actual numbers. Do not invent concerns not supported by the data."""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": BMAD_SYSTEM_PROMPT},
            {"role": "user",   "content": groq_prompt}
        ],
        "max_tokens": 400,
        "temperature": 0.2
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}",
                         "Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    analysis = data["choices"][0]["message"]["content"].strip()
                    logger.info("Murat real-data analysis received from Groq")
                    return analysis
                else:
                    body = await resp.text()
                    logger.error(f"Groq error {resp.status}: {body}")
                    return f"⚠️ Groq returned {resp.status} — proceeding."
    except Exception as e:
        logger.error(f"Groq call failed: {e}")
        return f"⚠️ Could not reach Groq: {e}"


# ── Jenkins trigger + poll ─────────────────────────────────────────────────────
async def trigger_jenkins_build() -> Dict[str, Any]:
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


async def poll_jenkins_build(build_number: Optional[int],
                             timeout_seconds: int = 300) -> Dict[str, Any]:
    if not build_number:
        return {"success": False, "message": "Unknown build number", "build_number": None}

    url      = f"{JENKINS_URL}/job/{JENKINS_JOB}/{build_number}/api/json"
    deadline = asyncio.get_event_loop().time() + timeout_seconds
    await asyncio.sleep(5)

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

    return {"success": False,
            "message": f"Timed out after {timeout_seconds}s",
            "build_number": build_number}


# ── Reply ──────────────────────────────────────────────────────────────────────
async def send_reply(service_url, conversation_id, activity_id,
                     recipient, sender, steps, success: bool):
    summary  = "Pipeline completed successfully! 🎉" if success else "Pipeline stopped."
    full_txt = summary + "\n\n" + "\n\n".join(steps)

    card = {
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard", "version": "1.5",
            "body": [
                {"type": "TextBlock", "text": "🚀 DevOps Pipeline — BMAD Powered",
                 "size": "Large", "weight": "Bolder",
                 "color": "Good" if success else "Warning"},
                {"type": "TextBlock",
                 "text": "Murat analyses REAL data → Jenkins → SonarQube → Nexus",
                 "wrap": True, "spacing": "Small", "isSubtle": True},
                {"type": "TextBlock", "text": summary,
                 "wrap": True, "spacing": "Medium", "weight": "Bolder"},
                {"type": "TextBlock", "text": "\n\n".join(steps),
                 "wrap": True, "maxLines": 30, "spacing": "Small"}
            ],
            "actions": [
                {"type": "Action.OpenUrl", "title": "SonarQube Report",
                 "url": f"{SONARQUBE_URL}/dashboard?id={SONAR_PROJECT_KEY}"},
                {"type": "Action.OpenUrl", "title": "Jenkins Build",
                 "url": f"{JENKINS_URL}/job/{JENKINS_JOB}/"},
                {"type": "Action.OpenUrl", "title": "Nexus Repository",
                 "url": f"{NEXUS_URL}/#browse/browse:{NEXUS_REPOSITORY}"}
            ]
        }
    }

    reply = {"type": "message", "from": recipient, "recipient": sender,
             "replyToId": activity_id, "text": full_txt, "attachments": [card]}

    url = f"{service_url}/v3/conversations/{conversation_id}/activities/{activity_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=reply,
                                    headers={"Content-Type": "application/json"},
                                    timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status in (200, 201, 202):
                    logger.info(f"Reply sent (HTTP {r.status})")
                else:
                    logger.error(f"Reply failed HTTP {r.status}: {await r.text()}")
    except Exception as e:
        logger.error(f"send_reply failed: {e}")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting DevOps Pipeline Bridge v3.1 (real-data BMAD) on port 3978...")
    uvicorn.run("bridge_pipeline:app", host="0.0.0.0", port=3978,
                reload=False, log_level="info")