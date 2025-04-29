"""Functions for generating key takeaways from research papers."""

from openai import OpenAI

def generate_key_takeaways(client: OpenAI, text: str, title: str, model: str) -> str:
    """Generate a structured Key Takeaways section to enhance reader understanding."""
    # Create a prompt that will generate well-structured key takeaways
    prompt = f"""Based on the research paper titled '{title}', create an exciting "Key Takeaways" section that highlights what makes this research valuable and interesting.

Your response should be formatted with these clear subsections:
1. Breakthrough Insights: The 3-4 most surprising or innovative aspects of this research
2. Why It Matters: How this research could change engineering practices or solve real problems
3. What's New: The specific innovations or improvements over previous approaches
4. Bottom Line: A one-paragraph summary of what an engineer should remember about this paper

Format each subsection with clear headings and concise bullet points. Use plain language and focus on the exciting possibilities rather than academic details.
"""
    
    # Use a shorter excerpt of the text to avoid token limits
    text_sample = text[:50000]  # Use first ~50k chars
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at translating technical research into exciting insights for engineers."},
                {"role": "user", "content": prompt + "\n\nHere is an excerpt of the paper:\n\n" + text_sample}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating Key Takeaways: {e}")
        return "Error generating Key Takeaways section."