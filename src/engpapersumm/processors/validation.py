"""Functions for validating and modeling section content."""

from typing import List, Dict, Any
from openai import OpenAI
import re

def validate_content_against_title(client: OpenAI, title: str, sections: List[dict], model: str) -> List[dict]:
    """
    Validate each section's relevance to the paper's title.
    Returns sections that are relevant to the title.
    """
    validated_sections = []
    
    for section in sections:
        # Prepare a sample of the section content (first 1000 chars)
        content_sample = section['content'][:1000]
        
        prompt = f"""Paper Title: {title}
Section Title: {section['title']}
Section Content Sample: {content_sample}

On a scale of 0 to 10, how relevant is this section content to the paper title?
Consider:
1. Direct topical relevance
2. Expected content for a section with this title in a paper about this topic
3. Use of terminology consistent with the paper title

Return ONLY a number from 0 to 10 representing the relevance score.
"""
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You assess the relevance of research paper sections to the paper's title."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            # Extract numeric score
            score_match = re.search(r'\d+(?:\.\d+)?', score_text)
            if score_match:
                score = float(score_match.group())
                section['title_relevance'] = score
                print(f"Section '{section['title']}' - Title Relevance: {score}/10")
                
                # Keep sections with score >= 6
                if score >= 6:
                    validated_sections.append(section)
                else:
                    print(f"  - Section filtered: Low relevance to title")
            else:
                print(f"Could not extract score for section '{section['title']}', including by default")
                validated_sections.append(section)
        except Exception as e:
            print(f"Error validating section '{section['title']}': {e}, including by default")
            validated_sections.append(section)
    
    # If we filtered out too many sections, keep at least 3 most relevant
    if len(validated_sections) < 3 and len(sections) >= 3:
        # Sort by title relevance and take top 3
        sorted_sections = sorted(sections, key=lambda x: x.get('title_relevance', 0), reverse=True)
        validated_sections = sorted_sections[:3]
        print(f"Keeping top 3 sections by title relevance")
    
    return validated_sections

def perform_topic_modeling(client: OpenAI, sections: List[dict], model: str, num_topics: int = 3) -> List[List[str]]:
    """
    Perform basic topic modeling to identify main themes across sections.
    Returns a list of topics, each represented as a list of key terms.
    """
    # Combine all section texts
    all_text = " ".join([section['content'] for section in sections])
    
    prompt = f"""Analyze this research paper text and identify the {num_topics} main topics or themes.
For each topic, list 5-7 keywords that best represent that topic.
Format the response as a JSON list of lists, where each inner list contains the keywords for one topic.

Text excerpt:
{all_text[:8000]}  # Limit text length
"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You perform topic modeling on research papers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        topics_json = response.choices[0].message.content.strip()
        topics_list = eval(topics_json)
        return topics_list.get('topics', [])
    except Exception as e:
        print(f"Error in topic modeling: {e}")
        return []