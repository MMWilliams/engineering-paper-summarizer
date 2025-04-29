"""Functions for generating Engineer's Corner content for research papers."""

from openai import OpenAI

def generate_engineers_corner(client: OpenAI, text: str, title: str, model: str) -> str:
    """Generate an Engineer's Corner section with practical applications and code examples."""
    # Create a prompt that will generate application-focused content for engineers
    prompt = f"""Based on the research paper titled '{title}', create an engaging "Engineer's Corner" section that makes this research exciting and actionable.

Your response should include these distinct subsections:
1. Practical Applications: 3-4 specific ways engineers could implement or benefit from this research right now
2. Future Possibilities: 2-3 exciting potential applications that could be developed in the future
3. Implementation Insights: Specific tips, pseudo-code, or implementation guidance for engineers wanting to apply these findings
4. Tools & Resources: Suggested tools, libraries, or resources for implementing these ideas

For each application, include:
- A clear, specific use case
- Why it matters/what problem it solves
- How engineers could start implementing it
- Any potential challenges or limitations

Make this technical but accessible, focusing on the "so what" factor for engineers. Use an excited, forward-looking tone that makes readers want to experiment with these ideas.
"""
    
    # Use a shorter excerpt of the text to avoid token limits
    text_sample = text[:50000]  # Use first ~50k chars
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an engineering consultant who specializes in translating academic research into practical applications."},
                {"role": "user", "content": prompt + "\n\nHere is an excerpt of the paper:\n\n" + text_sample}
            ],
            temperature=0.4,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating Engineer's Corner: {e}")
        return "Error generating Engineer's Corner section."