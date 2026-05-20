"""
backend/core/generation/templates.py
──────────────────────────────────────
Prompt templates for each report section.
Kept separate from agent logic for easy iteration.
"""

SYSTEM_PROMPT = """You are an elite executive business analyst AI.
Your job is to generate structured, evidence-grounded executive reports.

CRITICAL RULES:
1. ALWAYS cite sources using [SOURCE N] notation matching the context block.
2. NEVER invent facts, statistics, or claims not present in the context.
3. If context is insufficient for a section, state: "Insufficient data in provided sources."
4. Write in a precise, executive-appropriate tone — concise, no fluff.
5. Every factual claim must have at least one [SOURCE N] citation.
"""

QUERY_ANSWER_PROMPT = """Answer the following business question using ONLY the context below.
Cite every factual claim with [SOURCE N].

QUESTION: {query}

CONTEXT:
{context}

Provide a clear, cited answer (3–5 sentences). If context is insufficient, say so."""


SECTION_PROMPTS = {
    "executive_summary": """Write a 4–6 sentence Executive Summary answering: {query}

Use ONLY information from the context. Cite sources as [SOURCE N].
Include: the core answer, key evidence, and business implication.

CONTEXT:
{context}

EXECUTIVE SUMMARY:""",

    "key_findings": """Extract 5–7 Key Findings relevant to: {query}

Format as numbered list. Each finding must:
- Be a single concrete, specific insight
- Cite its source as [SOURCE N]
- Include a quantitative detail where available

CONTEXT:
{context}

KEY FINDINGS:""",

    "data_table": """Extract all quantitative data points relevant to: {query}

Format as a Markdown table with columns: Metric | Value | Source | Notes
Include only data explicitly stated in the context.
Cite each row with [SOURCE N].

CONTEXT:
{context}

DATA TABLE:""",

    "market_context": """Write a Market Context section (4–6 sentences) on: {query}

Focus on industry trends, external benchmarks, and market dynamics.
Prioritise web sources over internal documents for this section.
Cite sources as [SOURCE N].

CONTEXT:
{context}

MARKET CONTEXT:""",

    "risk_factors": """Identify 4–6 Risk Factors relevant to: {query}

Format as numbered list. Each risk must include:
- Risk name (bold)
- Description (1–2 sentences)
- Likelihood: Low/Medium/High
- Source citation [SOURCE N]

CONTEXT:
{context}

RISK FACTORS:""",

    "recommendations": """Based on the context, write 4–5 actionable Recommendations for: {query}

Format as numbered list. Each recommendation:
- Starts with an action verb
- Is specific and implementable
- References supporting evidence with [SOURCE N]

CONTEXT:
{context}

RECOMMENDATIONS:""",
}


SECTION_DISPLAY_NAMES = {
    "executive_summary": "Executive Summary",
    "key_findings": "Key Findings",
    "data_table": "Data & Metrics",
    "market_context": "Market Context",
    "risk_factors": "Risk Factors",
    "recommendations": "Recommendations",
}


def get_section_prompt(section: str, query: str, context: str) -> str:
    """Format the appropriate prompt template for a report section."""
    template = SECTION_PROMPTS.get(section)
    if not template:
        raise ValueError(f"Unknown section: {section}")
    return template.format(query=query, context=context)
