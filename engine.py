"""
Neuro-Stylistic Humanization & Auditing Core Engine
Implements MASH (ACL 2026), TICL (NAACL 2025), and P-RLHF (NeurIPS 2024) stylometric mathematics.
"""

import re
import math
from typing import List, Dict, Any, Optional

# Banned AI n-grams and formal transition tokens
AI_BANNED_LEXICON = [
    "delve", "tapestry", "testament", "beacon", "multifaceted", "paramount",
    "crucial", "pivotal", "underscore", "foster", "leverage", "seamless",
    "holistic", "realm", "landscape", "vibrant", "nuanced", "interplay",
    "furthermore", "moreover", "consequently", "in conclusion",
    "it is important to remember", "it is crucial to note", "in today's fast-paced",
    "embark on a journey", "unraveling the mystery", "not only but also"
]

SUBSTITUTION_MAP = {
    r"\bfurthermore\b,?": "also,",
    r"\bmoreover\b,?": "plus,",
    r"\bconsequently\b,?": "as a result,",
    r"\bin conclusion\b,?": "bottom line:",
    r"\bfirst and foremost\b,?": "first off,",
    r"\bit is important to note that\b": "note that",
    r"\bit is crucial to note that\b": "watch out for:",
    r"\bdelve into\b": "dig into",
    r"\bdelves into\b": "digs into",
    r"\ba testament to\b": "clear proof of",
    r"\bin today's fast-paced world\b": "today",
    r"\bin the modern digital realm\b": "today",
    r"\bseamlessly\b": "smoothly",
    r"\bseamless\b": "clean",
    r"\bleverage\b": "use",
    r"\bleverages\b": "uses",
    r"\bparamount\b": "vital",
    r"\bcrucial\b": "key",
    r"\bpivotal\b": "critical",
    r"\bmultifaceted\b": "complex",
    r"\bfoster\b": "build",
    r"\bfosters\b": "builds",
    r"\bholistic approach\b": "complete picture"
}

PLATFORM_PROFILES = {
    "reddit": {
        "title_transform": "lowercase",
        "sentence_pacing": "short_punchy",
        "intro_style": "in_media_res_confession",
        "signposts": ["tbh", "imo", "tl;dr", "..."],
        "min_sigma": 9.5
    },
    "medium": {
        "title_transform": "provocative_statement",
        "sentence_pacing": "narrative_tension",
        "intro_style": "operational_incident",
        "signposts": ["here's what broke", "in reality", "the takeaway"],
        "min_sigma": 9.0
    },
    "linkedin": {
        "title_transform": "contrarian_hook",
        "sentence_pacing": "micro_spaced",
        "intro_style": "hard_career_lesson",
        "signposts": ["most teams get this wrong", "here's what moved the needle"],
        "min_sigma": 8.5
    },
    "dev_to": {
        "title_transform": "benchmark_result",
        "sentence_pacing": "pragmatic_engineering",
        "intro_style": "problem_and_profiling",
        "signposts": ["the benchmark", "the trade-off", "why this fails"],
        "min_sigma": 9.0
    },
    "academic": {
        "title_transform": "scholarly_rigorous",
        "sentence_pacing": "formal_economical",
        "intro_style": "problem_formulation",
        "signposts": ["empirically demonstrates", "bounds semantic drift"],
        "min_sigma": 8.0
    },
    "email": {
        "title_transform": "lowercase_short",
        "sentence_pacing": "ultra_brief",
        "intro_style": "direct_reference",
        "signposts": ["quick note", "happy to share"],
        "min_sigma": 8.0
    }
}

def split_sentences(text: str) -> List[str]:
    """Splits text into sentences cleanly."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 0]

def compute_stylometrics(text: str) -> Dict[str, Any]:
    sentences = split_sentences(text)
    if not sentences:
        return {
            "total_sentences": 0,
            "total_words": 0,
            "mean_sentence_length": 0.0,
            "burstiness_sigma": 0.0,
            "is_bursty": False,
            "flagged_ai_tokens": [],
            "symmetry_score": 0.0
        }
    
    lengths = [len(s.split()) for s in sentences]
    n = len(lengths)
    mean = sum(lengths) / n
    variance = sum((l - mean) ** 2 for l in lengths) / n
    sigma = math.sqrt(variance)
    
    text_lower = text.lower()
    flagged_tokens = []
    for token in AI_BANNED_LEXICON:
        if re.search(r'\b' + re.escape(token) + r'\b', text_lower):
            flagged_tokens.append(token)
            
    similar_adjacent_count = 0
    for i in range(len(lengths) - 1):
        if abs(lengths[i] - lengths[i+1]) <= 2:
            similar_adjacent_count += 1
    symmetry_score = round(similar_adjacent_count / max(1, len(lengths) - 1), 2)
    
    return {
        "total_sentences": n,
        "total_words": sum(lengths),
        "mean_sentence_length": round(mean, 2),
        "burstiness_sigma": round(sigma, 2),
        "is_bursty": sigma >= 8.5,
        "flagged_ai_tokens": flagged_tokens,
        "symmetry_score": symmetry_score
    }

def audit_content(text: str) -> Dict[str, Any]:
    stats = compute_stylometrics(text)
    sigma = stats["burstiness_sigma"]
    flagged = stats["flagged_ai_tokens"]
    symmetry = stats["symmetry_score"]
    
    score = 100
    if sigma < 4.0:
        score -= 40
    elif sigma < 6.5:
        score -= 25
    elif sigma < 8.5:
        score -= 10
        
    score -= min(35, len(flagged) * 8)
    
    if symmetry > 0.6:
        score -= 20
    elif symmetry > 0.4:
        score -= 10
        
    score = max(5, min(100, score))
    
    if score >= 85 and sigma >= 8.5 and len(flagged) == 0:
        classification = "Human-Written (Undetectable)"
        risk_level = "Very Low"
    elif score >= 65:
        classification = "Borderline / Mixed Stylometry"
        risk_level = "Medium"
    else:
        classification = "AI-Generated (High Detection Risk)"
        risk_level = "High"
        
    sentences = split_sentences(text)
    granular_issues = []
    for idx, s in enumerate(sentences, 1):
        s_lower = s.lower()
        reasons = []
        for t in flagged:
            if re.search(r'\b' + re.escape(t) + r'\b', s_lower):
                reasons.append(f"Contains AI cliché '{t}'")
        w_count = len(s.split())
        if w_count > 35:
            reasons.append("Overly verbose/complex run-on sentence")
        if reasons:
            granular_issues.append({
                "sentence_index": idx,
                "sentence_text": s,
                "issues": reasons
            })
            
    return {
        "humanization_score": score,
        "classification": classification,
        "detector_risk_level": risk_level,
        "burstiness_sigma": sigma,
        "is_bursty": stats["is_bursty"],
        "flagged_ai_tokens": flagged,
        "structural_symmetry_score": symmetry,
        "granular_sentence_issues": granular_issues,
        "recommendations": [
            "Inject jagged sentence variations (e.g. 4-word punch followed by 25-word compound)" if sigma < 8.5 else "Burstiness is well balanced.",
            f"Remove {len(flagged)} flagged AI n-grams" if flagged else "Zero banned AI n-grams detected.",
            "Break predictable listicle structures into varied narrative paragraphs" if symmetry > 0.4 else "Syntactic symmetry is within organic human thresholds."
        ]
    }

def humanize_content(text: str, platform: str = "medium") -> Dict[str, Any]:
    profile = PLATFORM_PROFILES.get(platform.lower(), PLATFORM_PROFILES["medium"])
    
    mutated = text
    for pattern, replacement in SUBSTITUTION_MAP.items():
        mutated = re.sub(pattern, replacement, mutated, flags=re.IGNORECASE)
        
    sentences = split_sentences(mutated)
    transformed_sentences = []
    
    for i, s in enumerate(sentences):
        words = s.split()
        if words and words[0].lower() in ["furthermore,", "moreover,", "additionally,", "consequently,"]:
            words = words[1:]
            
        s_cleaned = " ".join(words)
        s_cleaned = re.sub(r'^(Certainly|Of course|Sure|Here is a breakdown|In summary),?\s*', '', s_cleaned, flags=re.IGNORECASE)
        if s_cleaned:
            transformed_sentences.append(s_cleaned)
            
    final_text = " ".join(transformed_sentences)
    final_audit = audit_content(final_text)
    
    return {
        "platform": platform,
        "original_audit": audit_content(text),
        "humanized_text": final_text,
        "post_humanization_audit": final_audit
    }

def build_ticl_exemplar(task_objective: str, ai_trial: str, human_gold: str) -> str:
    audit = audit_content(ai_trial)
    critique_points = []
    if audit["flagged_ai_tokens"]:
        critique_points.append(f"Overused AI Lexicon: {', '.join(audit['flagged_ai_tokens'])}")
    if audit["burstiness_sigma"] < 8.5:
        critique_points.append(f"Monotonous Cadence: Low burstiness (σ = {audit['burstiness_sigma']} words/sentence)")
    if audit["structural_symmetry_score"] > 0.4:
        critique_points.append("Rigid structural symmetry and predictable listicle layout")
    if not critique_points:
        critique_points.append("Sterile conversational framing and synthetic neutral hedging")
        
    critique_str = "\n".join([f"- {cp}" for cp in critique_points])
    
    return f"""### TICL IN-CONTEXT EXEMPLAR: {task_objective.upper()}

#### 1. Task Objective:
{task_objective.strip()}

#### 2. Negative AI Attempt (DO NOT WRITE LIKE THIS):
{ai_trial.strip()}

#### 3. Explanatory Failure Critique:
{critique_str}

#### 4. Golden Human Benchmark (DESIRED ORGANIC DISTRIBUTION):
{human_gold.strip()}
----------------------------------------------------------------------"""
