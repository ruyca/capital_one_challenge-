import os 
import re
from dotenv import load_dotenv
from openai import OpenAI

# load environment variables from a .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)


def clean_html_response(html_content: str) -> str:
    """
    Clean the HTML response from ChatGPT by removing markdown code blocks
    and excessive line breaks.
    """
    # Remove markdown code block markers (```html, ```, etc.)
    cleaned = re.sub(r'^```(?:html)?[\r\n]*', '', html_content, flags=re.MULTILINE)
    cleaned = re.sub(r'[\r\n]*```$', '', cleaned, flags=re.MULTILINE)
    
    # Remove excessive consecutive line breaks (keep max 2)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Remove any remaining backticks
    cleaned = cleaned.replace('`', '')
    
    # Trim whitespace from start and end
    cleaned = cleaned.strip()
    
    return cleaned


def create_prompt_from_parameters(params: dict) -> str:
    """
    Create an enhanced prompt string from the brand parameters for more creative websites.
    params: Dictionary containing brand parameters.
    Returns a formatted prompt string.
    """
    # Map tone to specific design characteristics
    tone_mappings = {
        'formal': 'sophisticated, elegant, professional with subtle animations',
        'semiformal': 'balanced, modern, approachable with smooth transitions',
        'casual': 'friendly, relaxed, inviting with playful hover effects',
        'playful': 'fun, energetic, creative with bold animations and interactions'
    }
    
    # Map design style to specific CSS features
    style_mappings = {
        'modern': 'gradients, glassmorphism, CSS Grid, flexbox, smooth shadows, parallax effects',
        'minimalistic': 'clean lines, generous whitespace, subtle animations, focus on typography',
        'corporate': 'structured layouts, professional color schemes, hover effects, card designs',
        'artistic': 'creative layouts, bold typography, animated backgrounds, unique shapes, CSS art'
    }
    
    tone_description = tone_mappings.get(params['tone'], params['tone'])
    style_features = style_mappings.get(params['design_style'], params['design_style'])
    
    prompt = f"""
    Create a stunning, modern, and highly interactive single-page website for {params['company_name']}.
    
    STRICT REQUIREMENTS:
    1. Return ONLY pure HTML code with embedded CSS. No explanations, no markdown, no comments.
    2. Start directly with <!DOCTYPE html> and end with </html>
    3. Do not add escape characters or backslashes.
    4. Return only the HTML and CSS content. 
    5. No images. All visuals must be created using CSS only.
    6. The whole website must fit within a single HTML file with embedded CSS.
    
    BRAND PARAMETERS:
    - Company Name: {params['company_name']} 
    - Brand Identity: {params['brand_identity']}
    - Tone: {tone_description}
    - Design Style: {style_features}
    - Primary Color: {params['primary_color']} (use this as the main accent color)
    
    ADVANCED CSS REQUIREMENTS - BE CREATIVE AND IMPRESSIVE:
    1. Create a sophisticated color palette based on {params['primary_color']}:
       - Use color theory to generate complementary, analogous, and accent colors
       - Implement CSS custom properties (variables) for all colors
       - Add gradient overlays and color transitions

    Make this website visually stunning, memorable, and unique. Maintain usability and brand consistency. The website should feel {tone_description} and showcase {style_features}.
    
    IMPORTANT: Output ONLY the HTML code starting with <!DOCTYPE html>. No markdown, no backticks, no explanations, no break.
    """

    print(f"Enhanced prompt created for {params['company_name']}")

    return prompt


def query_chatgpt_function(prompt: str, verbose: bool = True) -> str:
    """
    Function to query ChatGPT with enhanced parameters for better output.
    """
    try:
        response = client.responses.create(
            model="gpt-5",
            reasoning={"effort": "high"},  # Use high effort for best quality output
            input=[
                {
                    "role": "system", 
                    "content": """You are an elite web developer and CSS artist who creates visually stunning, 
                    highly interactive websites. You excel at CSS techniques, like creative layouts. You always output pure HTML with embedded CSS, 
                    never using markdown code blocks or backticks. Your websites are memorable, beautiful, and 
                    push the boundaries of what's possible with CSS while maintaining perfect functionality.
                    You strictly follow user instructions and brand guidelines to create unique web experiences.
                    Your responses never include explanations or extra text—only the requested HTML code. 
                    You ensure the HTML starts with <!DOCTYPE html> and ends with </html>.
                    Your response contains no escape characters or backslashes. And you never reference images; all visuals are created using CSS only."""
                },
                {"role": "user", "content": prompt}
            ]
        )
        
        # Get the response content using the correct attribute
        html_content = response.output_text
        
        # Clean the response
        cleaned_html = clean_html_response(html_content)
        
        if verbose:
            print(f"Response received: {len(cleaned_html)} characters")
            print("HTML content cleaned successfully")
        
        return cleaned_html
        
    except Exception as e:
        print(f"Error querying ChatGPT: {str(e)}")
        raise


def validate_html(html_content: str) -> bool:
    """
    Basic validation to ensure the HTML content is properly formatted.
    """
    # Check if it starts with DOCTYPE and ends with </html>
    has_doctype = html_content.strip().lower().startswith('<!doctype html>') or \
                  html_content.strip().lower().startswith('<html')
    has_closing = html_content.strip().lower().endswith('</html>')
    
    if not has_doctype:
        print("Warning: HTML doesn't start with DOCTYPE")
    if not has_closing:
        print("Warning: HTML doesn't end with </html>")
    
    return has_doctype and has_closing


# Example usage (can be removed in production)
if __name__ == "__main__":
    # Test parameters
    test_params = {
        'company_name': 'TechVision Pro',
        'brand_identity': 'Cutting-edge AI solutions for modern businesses',
        'tone': 'modern',
        'design_style': 'modern',
        'primary_color': '#6366F1'
    }
    
    # Create prompt
    prompt = create_prompt_from_parameters(test_params)
    
    # Query ChatGPT
    html_result = query_chatgpt_function(prompt)
    
    # Validate result
    if validate_html(html_result):
        print("HTML validation passed!")
        # Save to file for testing
        with open('test_output.html', 'w', encoding='utf-8') as f:
            f.write(html_result)
        print("Test HTML saved to test_output.html")