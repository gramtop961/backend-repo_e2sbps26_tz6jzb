import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Boyd Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    question: str

class RecommendResponse(BaseModel):
    answer: str
    suggestions: List[Dict[str, str]] | None = None

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.post("/api/recommend", response_model=RecommendResponse)
def recommend_tools(payload: RecommendRequest):
    q = payload.question.lower()

    catalog = {
        "general": [
            {"name": "ChatGPT", "why": "fast brainstorming, code help, content drafting"},
            {"name": "Claude", "why": "very long context research and review"},
            {"name": "Perplexity", "why": "answer engine with sources for quick research"},
        ],
        "developer": [
            {"name": "GitHub Copilot", "why": "inline coding assistance in IDE"},
            {"name": "Replit", "why": "collaborative coding workspace in the browser"},
            {"name": "Cursor", "why": "AI-first code editor for rapid prototyping"},
        ],
        "video": [
            {"name": "RunwayML", "why": "video editing, gen-erase, motion tools"},
            {"name": "Kapwing", "why": "creator-friendly editing and repurposing"},
            {"name": "Descript", "why": "edit video like a doc, voice cloning"},
        ],
        "design": [
            {"name": "Midjourney", "why": "high-quality image generation"},
            {"name": "Figma + Magician", "why": "AI-aided design flows"},
            {"name": "Canva", "why": "templates + AI for fast visuals"},
        ],
        "writer": [
            {"name": "Claude", "why": "structured writing with long references"},
            {"name": "Notion AI", "why": "docs, notes, summaries in your workspace"},
            {"name": "ChatGPT", "why": "tone shifting and rewrites"},
        ],
        "research": [
            {"name": "Perplexity", "why": "research with citations"},
            {"name": "Elicit", "why": "literature review and paper extraction"},
            {"name": "Semantic Scholar", "why": "paper search and alerts"},
        ],
        "marketing": [
            {"name": "Jasper", "why": "campaign copy and frameworks"},
            {"name": "Copy.ai", "why": "ads, landing pages, product copy"},
            {"name": "Typefully + GPT", "why": "social writing and scheduling"},
        ],
        "data": [
            {"name": "OpenAI o3/ChatGPT", "why": "reasoning on CSVs and dataframes"},
            {"name": "Hex", "why": "notebooks with AI + SQL + viz"},
            {"name": "Coalesce", "why": "analytics engineering with AI"},
        ],
        "audio": [
            {"name": "ElevenLabs", "why": "realistic voice synthesis"},
            {"name": "Whisper", "why": "accurate transcription"},
            {"name": "Krisp", "why": "noise cancellation for calls"},
        ],
        "product": [
            {"name": "Linear + AI", "why": "fast triage and spec drafting"},
            {"name": "Canny + AI", "why": "feedback clustering and summarization"},
            {"name": "Notion AI", "why": "PRDs, docs, and summaries"},
        ],
        "sales": [
            {"name": "Apollo + GPT", "why": "prospect research and outreach"},
            {"name": "Gong", "why": "call analysis and coaching"},
            {"name": "HubSpot AI", "why": "sequence writing and follow‑ups"},
        ],
    }

    keywords = {
        "developer": ["dev", "developer", "engineer", "code", "coding", "programmer", "software"],
        "video": ["video", "editor", "shorts", "tiktok", "reels", "yt"],
        "design": ["design", "designer", "mockup", "ui", "ux", "image", "art"],
        "writer": ["writer", "writing", "blog", "newsletter", "copy", "content"],
        "research": ["research", "paper", "citation", "study", "references"],
        "marketing": ["marketing", "ads", "campaign", "growth", "seo", "email"],
        "data": ["data", "analytics", "sql", "csv", "notebook"],
        "audio": ["audio", "podcast", "voice", "music", "sound"],
        "product": ["product", "pm", "product manager", "tickets", "spec"],
        "sales": ["sales", "outreach", "crm", "pipeline", "demo"],
    }

    matched = []
    for domain, keys in keywords.items():
        if any(k in q for k in keys):
            matched.append(domain)

    if not matched:
        matched = ["general"]

    # Build readable answer
    lines = ["Here are a few solid picks for you:"]
    suggestions: List[Dict[str, str]] = []

    for domain in matched:
        items = catalog.get(domain, [])
        if not items:
            continue
        lines.append(f"- {domain.title()} stack:")
        for it in items:
            lines.append(f"  • {it['name']} — {it['why']}")
            suggestions.append({"name": it["name"], "why": it["why"]})

    # Add a small CTA
    lines.append("If you share more about your workflow or tools you already use, I can refine this list.")

    return RecommendResponse(
        answer="\n".join(lines),
        suggestions=suggestions,
    )

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
