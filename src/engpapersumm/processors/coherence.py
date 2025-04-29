"""Functions for ensuring coherence between paper sections."""

from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def ensure_content_coherence(sections: List[dict]) -> List[dict]:
    """
    Ensure coherence between sections by using text similarity.
    Removes outlier sections that don't match the overall content theme.
    """
    if len(sections) <= 2:
        return sections  # Need more than 2 sections to detect outliers
    
    # Create combined text for each section
    section_texts = [section['content'] for section in sections]
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(section_texts)
        
        # Calculate mean similarity of each section to all other sections
        section_scores = []
        for i in range(len(sections)):
            other_indices = [j for j in range(len(sections)) if j != i]
            similarities = [
                cosine_similarity(tfidf_matrix[i:i+1], tfidf_matrix[j:j+1])[0][0]
                for j in other_indices
            ]
            mean_similarity = sum(similarities) / len(similarities) if similarities else 0
            section_scores.append((i, mean_similarity))
            print(f"Section '{sections[i]['title']}' - Mean Similarity to Others: {mean_similarity:.3f}")
        
        # Identify potential outliers (sections with much lower similarity)
        sorted_scores = sorted(section_scores, key=lambda x: x[1])
        if len(sorted_scores) >= 3:
            lowest_score = sorted_scores[0][1]
            second_lowest = sorted_scores[1][1]
            
            # If the lowest score is significantly lower than others, it may be an outlier
            if lowest_score < 0.3 * second_lowest:
                outlier_index = sorted_scores[0][0]
                print(f"Detected outlier section: '{sections[outlier_index]['title']}' with similarity {lowest_score:.3f}")
                
                # Remove the outlier
                coherent_sections = [sections[i] for i in range(len(sections)) if i != outlier_index]
                return coherent_sections
    
    except Exception as e:
        print(f"Error in coherence analysis: {e}")
    
    return sections