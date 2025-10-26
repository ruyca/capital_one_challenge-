import os 
from dotenv import load_dotenv
from openai import OpenAI

# load environment variables from a .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)


def create_prompt_from_parameters(params: dict) -> str:
    """
    Create a prompt string from the brand parameters.
    params: Dictionary containing brand parameters.
    Returns a formatted prompt string.
    """
    prompt = (
        f"Create a complete, single-file HTML website with inline CSS and JavaScript \
            based on these parameters:"
        f"Create a website content for a company named '{params['company_name']}' "
        f"with the following brand identity: {params['brand_identity']}. "
        f"The tone should be '{params['tone']}', the design style should be '{params['design_style']}', "
        f"and the primary color should be '{params['primary_color']}'. Return only the HTML code, no explanations or extra text."
    )

    print(prompt)

    return prompt

def query_chatgpt_function(prompt: str) -> str:
    """
    Function to query ChatGPT with a given prompt.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert web developer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7,
    )
    
    return response.choices[0].message.content