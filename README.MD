# HumanWrite-X

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-009688)
![Deployment](https://img.shields.io/badge/Deployment-Render-black)
![Architecture](https://img.shields.io/badge/Architecture-Cloud--Native%20%7C%20Stateless-success)

**HumanWrite-X** is an API-first text analysis and rewriting service built around stylometric auditing, structural mutation, and platform-aware writing adapters.

The project is designed to take LLM-generated or machine-assisted drafts, inspect their stylistic characteristics, and produce revisions with more varied sentence structure, pacing, vocabulary, and platform-appropriate voice.

It exposes a small HTTP API that can be connected to agent workflows, custom actions, developer tools, or other applications that need programmatic text auditing and rewriting.

> **Note:** HumanWrite-X is intended to improve writing quality and stylistic variation. Detector scores are not a reliable proof of authorship, and no rewriting system can guarantee that text will bypass every AI-detection system.

---

## What HumanWrite-X Does

LLM-generated text often falls into recognizable writing patterns: similar sentence lengths, repetitive transitions, predictable paragraph structures, generic vocabulary, and excessive formal phrasing.

HumanWrite-X approaches that problem as a text-transformation pipeline.

The system can:

- Audit a piece of text for selected stylometric signals.
- Calculate sentence-length statistics and burstiness-related measures.
- Identify configured words and phrases associated with repetitive machine-like prose.
- Rewrite text using sentence-level structural mutations.
- Generate Trial-Error-Critique-Learn (TICL) prompt blocks.
- Adapt output for different publishing environments.
- Process requests without persistent application-level text storage.

The goal isn't to make every sentence sound "random."

The goal is to make the writing feel less mechanically uniform while preserving the original meaning and adapting the result to the intended audience.

---

## Core Components

### Stylometric Auditing

The audit layer examines several measurable properties of the supplied text.

Depending on the configured implementation, this can include:

- Sentence-length distribution
- Sentence-length standard deviation
- Burstiness-related statistics
- Token or n-gram characteristics
- Configured lexical patterns
- Structural repetition
- Humanization-oriented scoring

The `/api/audit` endpoint returns these measurements so that a caller can inspect the source text before deciding whether a rewrite is necessary.

---

### MASH Refinement Pipeline

The MASH component treats rewriting as a sequence of structural transformations.

The current design separates the process into four conceptual stages:

```text
┌──────────────────────┐
│ Stage 1              │
│ Data Construction    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Stage 2              │
│ Style Initialization │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Stage 3              │
│ Boundary Alignment   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Stage 4              │
│ Sentence Refinement  │
└──────────────────────┘
```

At inference time, the refinement stage can inspect individual sentences and modify:

- Sentence length
- Clause structure
- Paragraph rhythm
- Repetitive transitions
- Predictable vocabulary
- Mechanical phrasing
- Excessive syntactic symmetry

The implementation is intentionally modular so individual transformation stages can be changed without redesigning the API layer.

---

## TICL Prompt Generation

HumanWrite-X also supports a Trial-Error-Critique-Learn workflow.

Instead of supplying an LLM with only a task description and asking it to "sound human," the generated prompt can provide three additional pieces of context:

```text
Task
  │
  ├── Negative AI Attempt
  │
  ├── Failure Critique
  │
  └── Human Reference Example
```

The critique identifies specific problems in the trial output, such as:

- Repetitive sentence structures
- Generic introductions
- Formulaic transitions
- Excessive corporate terminology
- Lack of concrete experience
- Uniform paragraph rhythm

The resulting prompt can then be passed to an LLM as an in-context writing instruction.

This makes the feedback loop explicit rather than relying on a vague instruction such as "make this sound more natural."

---

## Platform Adapters

Different platforms reward different writing behaviors. A technical post aimed at Hacker News shouldn't read like a LinkedIn update, and an academic paper shouldn't use the same rhythm as a Reddit comment.

HumanWrite-X therefore keeps platform behavior separate from the core transformation engine.

Supported adapter styles include:

| Platform | Writing focus |
|---|---|
| Dev.to / Hacker News | Code-first, technical, benchmark-driven |
| Reddit | Conversational, direct, community-native |
| LinkedIn | Hook-driven, concise, professional |
| Instagram / Facebook | Story-first and conversational |
| Medium / Substack | Narrative, technical, case-study driven |
| Academic | Formal, precise, evidence-oriented |
| Executive Email | Short, specific, low-friction |
| Keynote / Speech | Spoken cadence and presentation cues |

The adapters define tone, formatting, pacing, and common failure patterns rather than changing the underlying API contract.

---

## API

HumanWrite-X exposes the following endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/audit` | `POST` | Analyze text and return configured stylometric signals |
| `/api/humanize` | `POST` | Rewrite text through the configured transformation pipeline |
| `/api/ticl/generate-prompt` | `POST` | Generate a TICL in-context prompt block |
| `/api/stylometrics` | `POST` | Return lower-level sentence and n-gram statistics |

### Example request

```http
POST /api/audit
Content-Type: application/json
```

A typical integration sends the text and the options required by the selected analysis or platform adapter.

The exact request and response schemas are exposed through FastAPI's generated OpenAPI specification.

---

## Architecture

The service is deliberately small.

```text
                    ┌───────────────────────┐
                    │      Client / Agent   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      FastAPI API      │
                    └───────────┬───────────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
       ┌───────────┐      ┌────────────┐     ┌─────────────┐
       │  Audit    │      │ Humanize   │     │    TICL     │
       │  Engine   │      │   / MASH   │     │  Generator  │
       └─────┬─────┘      └─────┬──────┘     └──────┬──────┘
             │                  │                   │
             └──────────────────┼───────────────────┘
                                ▼
                     ┌────────────────────┐
                     │ Platform Adapters  │
                     └────────────────────┘
```

### Stateless request processing

The intended deployment model is stateless.

Text is processed in memory during a request rather than being written to a persistent application database. The project does not require a text-content database for its core workflow.

That makes the service straightforward to deploy horizontally: multiple application instances can handle requests without sharing application state.

If you deploy this publicly, you should still review your hosting provider's request logs, reverse-proxy logs, monitoring configuration, and error-reporting settings. Application-level statelessness does not automatically mean that no infrastructure logs exist.

---

## Configuration

Routing is controlled through environment variables.

For local development:

```bash
export SERVER_URL="http://localhost:8000"
```

For a hosted deployment, set the variable to the public URL of your service.

The project can also resolve deployment-specific routing through environment configuration such as:

```text
SERVER_URL
RENDER_EXTERNAL_URL
```

Avoid hard-coding production URLs into application logic.

---

# Local Development

## 1. Clone the repository

```bash
git clone https://github.com/wazimBadsha/HumanWrite-X-Adaptive-LLM-Based-Content-Humanization-System.git

cd HumanWrite-X-Adaptive-LLM-Based-Content-Humanization-System
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

Using a virtual environment is recommended:

```bash
python -m venv .venv

source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

## 3. Configure the server URL

```bash
export SERVER_URL="http://localhost:8000"
```

If you use a `.env` file, keep secrets and deployment-specific configuration out of source control.

## 4. Start FastAPI

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API should now be available locally on port `8000`.

---

# OpenAPI Integration

FastAPI generates an OpenAPI document automatically.

After starting the service, inspect:

```text
/openapi.json
```

The generated schema can be used by API clients and agent platforms that support OpenAPI-based integrations.

For a ChatGPT Custom Action or similar integration, replace any placeholder server URL in the OpenAPI configuration with the URL of your deployed instance.

Do not point a production integration at `localhost`.

---

# Deployment

HumanWrite-X is designed for cloud deployment and can be hosted on platforms capable of running a Python/FastAPI application.

A typical deployment looks like:

```text
Client
  │
  │ HTTPS
  ▼
Cloud / Render
  │
  ▼
FastAPI
  │
  ├── Audit
  ├── Stylometrics
  ├── MASH
  └── TICL
```

Set the deployment URL through the environment configuration rather than embedding it in application code.

Before exposing the service publicly, configure:

- HTTPS
- Request-size limits
- Authentication where required
- Rate limiting
- Error logging
- Dependency pinning
- Appropriate infrastructure log retention

---

# Connecting AI Tools

Because the service exposes an OpenAPI schema, it can act as a backend action for applications that support HTTP/OpenAPI integrations.

Potential integration targets include:

- ChatGPT Custom Actions
- Claude Desktop / MCP workflows
- Cursor
- Gemini integrations
- Grok
- Internal agent systems
- Custom developer tooling

The integration pattern is simple:

```text
LLM / Agent
     │
     ▼
HumanWrite-X API
     │
     ├── audit
     ├── stylometrics
     ├── humanize
     └── TICL prompt generation
```

The API remains independent of the calling client.

---

# Example Workflow

A typical application can use the endpoints as a small pipeline:

```text
1. Receive draft
       │
       ▼
2. /api/audit
       │
       ▼
3. Inspect stylometric signals
       │
       ▼
4. /api/humanize
       │
       ▼
5. Apply platform adapter
       │
       ▼
6. Return revised text
```

For an LLM-driven workflow, TICL can be inserted before the final generation step:

```text
Task
  │
  ▼
Generate trial
  │
  ▼
Critique trial
  │
  ▼
Generate TICL prompt
  │
  ▼
LLM rewrite
  │
  ▼
Optional stylometric audit
```

---

# Design Decisions

### Why keep the service stateless?

The core transformation doesn't need a database.

Keeping request processing in memory reduces operational complexity and makes horizontal scaling easier. It also means the application has less application-level state to manage.

### Why separate platform adapters?

A Reddit comment and an academic paper have very different expectations around sentence structure, formatting, and tone.

Putting those rules into adapters keeps platform-specific behavior from leaking into the core transformation engine.

### Why expose raw stylometric measurements?

A single "humanization score" hides too much.

Sentence statistics, burstiness-related measurements, lexical flags, and other raw signals make it possible for callers to inspect *why* a piece of text was flagged or changed.

---

# Limitations

HumanWrite-X should not be treated as an authorship verifier or as a guarantee that rewritten text will evade a particular commercial detector.

AI-detection systems differ in their features, thresholds, model versions, and evaluation data. A score from one detector does not establish whether a person or an AI system wrote a document.

The same applies to stylometric thresholds used by this project. Values such as sentence-length standard deviation can be useful diagnostics, but they are not universal definitions of human writing.

Rewriting also has an unavoidable trade-off: aggressive stylistic changes can alter meaning, voice, terminology, or factual precision.

For technical, legal, academic, or otherwise sensitive material, review the generated output before publishing or submitting it.

---

# Security & Privacy Notes

The application is designed around stateless processing and does not require persistent storage for its core text-transformation workflow.

That does **not** mean a deployment automatically has zero data retention.

Depending on where the service is hosted, request metadata, application logs, proxy logs, crash reports, or monitoring systems may retain information.

If privacy is a requirement for your deployment:

1. Review your hosting provider's logging configuration.
2. Disable unnecessary request-body logging.
3. Avoid sending credentials or unnecessary personal information.
4. Add authentication before exposing administrative or internal endpoints.
5. Apply request-size and rate limits.
6. Keep production secrets in environment variables or a secrets manager.

---

# Project Structure

A typical implementation can be organized around the API, transformation engines, and platform adapters:

```text
.
├── app.py
├── requirements.txt
├── openapi.json
├── adapters/
│   ├── reddit/
│   ├── devto_hn/
│   ├── linkedin/
│   ├── social/
│   ├── medium/
│   ├── academic/
│   ├── executive/
│   └── keynote/
├── engines/
│   ├── audit/
│   ├── stylometrics/
│   ├── mash/
│   └── ticl/
└── README.md
```

Adjust the structure to match the actual repository layout if your implementation uses different module names.

---

# Engineering Notes

HumanWrite-X is intentionally API-first.

The HTTP layer should remain thin. Most of the interesting behavior belongs in independently testable components:

```text
API
 │
 ├── validation
 ├── routing
 │
 ▼
Domain logic
 │
 ├── stylometric analysis
 ├── sentence mutation
 ├── TICL generation
 └── platform adaptation
```

That separation makes it easier to benchmark individual stages instead of treating the entire rewriting operation as a black box.

For production work, add regression tests around semantic preservation, adapter behavior, malformed input, unusually short text, very long text, and Unicode-heavy content.

---

# Author

**Badhusha K**  
Senior Full Stack Web, Mobile & AI Software Engineer

9+ years of experience building web, mobile, AI, and distributed software systems.

- **LinkedIn:** https://linkedin.com/in/badhushak
- **GitHub / Portfolio:** https://github.com/wazimBadsha
- **X:** https://x.com/badhusha0071
- **Medium:** https://medium.com/@muhammadbadhusha
- **Email:** connectmemba@gmail.com

---

# 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. You are free to use, modify, and distribute this software in personal and commercial applications.


---

## A Note on the Project's Goal

The useful part of HumanWrite-X isn't a magic "human score."

It's the feedback loop.

Measure the draft. Identify repetitive structure. Rewrite the parts that actually need work. Measure again. Keep the meaning intact.

That makes the system useful even when an AI detector changes its scoring model tomorrow.
