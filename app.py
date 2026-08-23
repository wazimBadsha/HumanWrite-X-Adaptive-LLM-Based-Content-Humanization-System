#!/usr/bin/env python3
"""
Neuro-Humanizer MCP & REST API Server
Universal AI Plugin & Action Endpoint for ChatGPT, Gemini, Claude, Cursor, Copilot, and Grok.
"""

import os
import json
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from engine import audit_content, humanize_content, compute_stylometrics, build_ticl_exemplar

app = FastAPI(
    title="Neuro-Stylistic LLM Humanizer & Auditing MCP",
    description="Universal MCP Tool & API for 100% humanized, anti-detector LLM generation across ChatGPT, Gemini, Claude, Cursor, Copilot, and Grok.",
    version="4.0.0",
    servers=[
        {"url": "http://localhost:8000", "description": "Local Development Server"},
        {"url": "https://neuro-humanizer-mcp.onrender.com", "description": "Render Free Cloud Instance"}
    ]
)

# Enable CORS for all AI clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas for Request/Response Validation
class AuditRequest(BaseModel):
    text: str = Field(..., description="The text to audit for AI detection signatures and stylometric balance.")

class HumanizeRequest(BaseModel):
    text: str = Field(..., description="The AI or draft text to mutate and humanize.")
    platform: Optional[str] = Field("medium", description="Target platform: reddit, medium, linkedin, dev_to, academic, email, speech")

class TICLRequest(BaseModel):
    task_objective: str = Field(..., description="The prompt or goal of the generation task.")
    ai_trial: str = Field(..., description="The raw, generic AI generation illustrating failure modes.")
    human_gold: str = Field(..., description="The authentic human-written gold standard example.")

class StylometricsRequest(BaseModel):
    text: str = Field(..., description="Text for computing raw burstiness, sentence standard deviation, and n-gram entropy.")

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Neuro-Stylistic Humanizer MCP Server",
        "version": "4.0.0",
        "documentation": "/docs",
        "openapi_spec": "/openapi.json",
        "mcp_sse_endpoint": "/sse",
        "supported_clients": ["ChatGPT Custom Actions", "Claude Desktop MCP", "Google Gemini Extensions", "Cursor AI", "Grok", "Copilot"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "neuro-humanizer-mcp"}

@app.post("/api/audit", summary="Audit text for AI detection markers")
def api_audit(req: AuditRequest):
    """
    Evaluates text against 4-dimensional stylometric matrix:
    - Perplexity Burstiness (σ ≥ 8.5)
    - Token Rank Entropy (Banned AI Lexicon)
    - Syntactic Symmetry
    - Cognitive Anchoring
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    return audit_content(req.text)

@app.post("/api/humanize", summary="Mutate and humanize text for zero-shot detector evasion")
def api_humanize(req: HumanizeRequest):
    """
    Executes MASH Stage 4 Sentence-Level Mutation and Token Neutralization.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    return humanize_content(req.text, platform=req.platform or "medium")

@app.post("/api/ticl/generate-prompt", summary="Generate a TICL In-Context prompt block")
def api_ticl(req: TICLRequest):
    """
    Generates a Trial-Error-Explain prompt block containing negative trials, critiques, and gold benchmarks.
    """
    block = build_ticl_exemplar(req.task_objective, req.ai_trial, req.human_gold)
    return {
        "ticl_exemplar_block": block,
        "instructions": "Copy this block into your ChatGPT Project, Custom GPT, or Claude Project instructions/knowledge."
    }

@app.post("/api/stylometrics", summary="Calculate raw burstiness and token entropy")
def api_stylometrics(req: StylometricsRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    return compute_stylometrics(req.text)

# MCP Tool Discovery Endpoint for Model Context Protocol clients
@app.get("/mcp/tools", summary="List available MCP tools")
def list_mcp_tools():
    return {
        "tools": [
            {
                "name": "audit_text",
                "description": "Audits text for AI detection signatures, sentence burstiness (sigma), banned RLHF tokens, and structural symmetry.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "The text to audit."}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "humanize_text",
                "description": "Mutates and humanizes text using MASH/TICL algorithms to eliminate AI detection and enforce organic cadence.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "The text to humanize."},
                        "platform": {"type": "string", "enum": ["reddit", "medium", "linkedin", "dev_to", "academic", "email"], "description": "Platform adapter."}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "generate_ticl_prompt",
                "description": "Constructs a Trial-Error-Explain (TICL) few-shot in-context learning block with negative sample critiques.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_objective": {"type": "string", "description": "Task description."},
                        "ai_trial": {"type": "string", "description": "Negative AI generation."},
                        "human_gold": {"type": "string", "description": "Gold human benchmark."}
                    },
                    "required": ["task_objective", "ai_trial", "human_gold"]
                }
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
