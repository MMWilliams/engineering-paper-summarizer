"""Topic extraction and similarity computation functions."""

from typing import Dict, List, Any, float
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI

def extract_paper_topic(client: OpenAI, title: str, abstract: str, model: str) -> Dict[str, float]:
    """
    Extract main topics and keywords from the paper title and abstract.
    Returns a dictionary of important terms and their weights.
    """
    prompt = f"""Analyze this research paper title and abstract to extract the main topics and relevant keywords.
Title: {title}
Abstract: {abstract[:2000]}  # Limit abstract length

List the top 10-15 most important topics and technical terms that define what this paper is about.
For each term, assign a relevance score from 0.0 to 1.0 where 1.0 is highest relevance.
Format the response as a JSON dictionary with terms as keys and scores as values.
"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a research paper analysis system that extracts key topics and terms."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        topics_json = response.choices[0].message.content.strip()
        topics_dict = eval(topics_json)  # Convert string to dictionary
        return topics_dict
    except Exception as e:
        print(f"Error parsing topic extraction response: {e}")
        # Return a basic dictionary with the title as the main topic
        return {title.lower(): 1.0}

def compute_topic_similarity(topic_dict: Dict[str, float], text: str) -> float:
    """
    Compute similarity between a text and the main topics of the paper.
    Returns a score from 0 to 1 indicating relevance to the paper's main topics.
    """
    # Convert topics to a weighted string, repeating important terms
    topic_text = " ".join([term.lower() * max(1, int(score * 10)) for term, score in topic_dict.items()])
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        # Handle empty text
        if not text or not topic_text:
            return 0.0
            
        # Compute TF-IDF vectors
        tfidf_matrix = vectorizer.fit_transform([topic_text, text.lower()])
        
        # Compute cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)
    except Exception as e:
        print(f"Error computing similarity: {e}")
        return 0.0

def filter_irrelevant_sections(sections: List[dict], topic_dict: Dict[str, float], 
                             similarity_threshold: float) -> List[dict]:
    """
    Filter out sections that are not relevant to the paper's main topics.
    Returns a list of sections that pass the relevance threshold.
    """
    relevant_sections = []
    
    for section in sections:
        similarity = compute_topic_similarity(topic_dict, section['content'])
        section['topic_similarity'] = similarity
        
        # Keep sections above the similarity threshold
        if similarity >= similarity_threshold:
            relevant_sections.append(section)
            print(f"Section '{section['title']}' - Similarity: {similarity:.3f} - INCLUDED")
        else:
            print(f"Section '{section['title']}' - Similarity: {similarity:.3f} - FILTERED OUT")
    
    # If we filtered out too many sections, adjust threshold to keep at least 3 most relevant sections
    if len(relevant_sections) < 3 and len(sections) >= 3:
        print("Too many sections filtered. Adjusting threshold to keep most relevant sections...")
        # Sort by similarity and take top 3
        sorted_sections = sorted(sections, key=lambda x: x.get('topic_similarity', 0), reverse=True)
        relevant_sections = sorted_sections[:3]
        print(f"Keeping top 3 sections with similarities: {[s.get('topic_similarity', 0) for s in relevant_sections]}")
    
    return relevant_sections