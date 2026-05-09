#!/usr/bin/env python3
"""
Prompt builder for GPT‑based transcript summarization.
Provides a reusable function that creates a ready‑to‑copy ChatGPT prompt.
"""


def build_summary_prompt(transcript_text: str, source_name: str) -> str:
    """
    Build a ChatGPT prompt for summarizing a cleaned transcript.

    Parameters
    ----------
    transcript_text : str
        The full transcript text.
    source_name : str
        Name of the transcript file (for context).

    Returns
    -------
    str
        A complete prompt that can be copied into ChatGPT.
    """
    return f"""You are an expert educational content analyst. Below is a cleaned transcript from a course or tutorial titled "{source_name}".

Please analyze the transcript and return a markdown answer with the following sections:

# GPT Summary: {source_name}

## Short Summary
A concise summary of the transcript (2–3 sentences).

## Key Ideas
Main useful ideas from the transcript (bullet points).

## Practical Actions
Concrete actions the learner should take after studying this material (bullet points).

## Important Terms
Important terms, tools, technologies, names, or links mentioned (bullet points).

## Noise / Low-value Content
Parts that are mostly intro, promo, repetition, or low-value information (bullet points).

## Study Recommendation
Whether this material should be:
- studied fully;
- skimmed;
- skipped;
- saved as reference.

Also include a short reason.

---
Transcript:
{transcript_text}
---
Please respond with the markdown sections as requested. Do not add extra commentary before or after the sections."""


if __name__ == "__main__":
    # Simple test: build a prompt with dummy text
    dummy_text = "This is a test transcript about Python programming."
    prompt = build_summary_prompt(dummy_text, "test.txt")
    print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
