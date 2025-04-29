"""Functions for generating hierarchical summaries of research paper sections."""

from typing import List, Dict
from openai import OpenAI

def map_summarize_section(client: OpenAI, section: dict, model: str) -> dict:
    """
    (Map Phase) Summarize a single section while emphasizing practical applications and insights.
    Returns the section title and its summarized content.
    """
    # Add topic guidance if available
    topic_guidance = section.get('topic_guidance', '')
    if topic_guidance:
        topic_instruction = f"\n\n{topic_guidance}"
    else:
        topic_instruction = ""
    
    # Modify the prompt to focus on exciting and practical aspects
    prompt = f"""Produce an engaging and insight-focused summary of this '{section['title']}' section from a research paper.
Your summary must:
1. Focus on what an engineer would find most interesting and useful
2. Prioritize practical applications, real-world impact, and actionable insights
3. Explain why this matters and how it could be used in practical engineering contexts
4. Keep technical terms but explain them in plain language where needed
5. Highlight the key findings and innovations, not just the methodology
6. Include concrete examples of how this research could be applied
7. Only briefly mention methodology - focus more on results and applications{topic_instruction}

Use an engaging style that makes the reader excited about the possibilities. Begin directly with the most interesting or surprising aspects, not with phrases like "This section discusses".
"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": section['content']}
            ],
            temperature=0.3,
            max_tokens=2500
        )
        
        summarized_content = response.choices[0].message.content.strip()
        return {
            'title': section['title'],
            'content': summarized_content
        }
    except Exception as e:
        print(f"Error summarizing section '{section['title']}': {e}")
        return {
            'title': section['title'],
            'content': f"Error generating summary: {e}"
        }

def reduce_summarize(client: OpenAI, section_summaries: List[dict], model: str) -> str:
    """
    (Reduce Phase) Fuse the individual section summaries into a coherent whole.
    Focuses on practical applications and excitement about the research.
    """
    # Concatenate all section summaries with their titles
    all_summaries = ""
    for section in section_summaries:
        all_summaries += f"## {section['title']}\n\n{section['content']}\n\n"
    
    prompt = """Synthesize these research paper section summaries into an engaging, application-focused document.
Your synthesis must:
1. Make this research exciting and relevant to engineers
2. Preserve the original section structure but focus on the most interesting parts
3. Highlight practical applications and real-world impact throughout
4. Connect the dots between sections to tell a compelling story
5. Ensure numerical data and technical details are explained in context of why they matter
6. Use concrete examples and analogies to make concepts accessible
7. Define acronyms and technical terms in plain language
8. Focus on what engineers can DO with this research

This is for engineers who care about applications more than academic details. Use an engaging style with clear explanations of why this research matters.
"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": all_summaries}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in reduce summarization phase: {e}")
        return "Error generating final summary."