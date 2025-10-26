from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from query_chatgpt import query_chatgpt_function, create_prompt_from_parameters 
import re

app = FastAPI(title="Website API generator", version="1.0.0")

class BrandingRequest(BaseModel):
    company_name: str = Field(..., description="Name of the company")
    brand_identity: str = Field(..., description="Brand identity description")
    tone: str = Field(..., description="Tone of voice: formal, semiformal, casual, or playful")
    design_style: str = Field(..., description="Design style: modern, minimalistic, corporate, or artistic")
    primary_color: str = Field(..., description="Primary color in HEX format (e.g., #FF5733)")
    
    # Validate tone
    @classmethod
    def validate_tone(cls, v):
        valid_tones = ["formal", "semiformal", "casual", "playful"]
        if v.lower() not in valid_tones:
            raise ValueError(f"Tone must be one of: {', '.join(valid_tones)}")
        return v.lower()
    
    # Validate design_style
    @classmethod
    def validate_design_style(cls, v):
        valid_styles = ["modern", "minimalistic", "corporate", "artistic"]
        if v.lower() not in valid_styles:
            raise ValueError(f"Design style must be one of: {', '.join(valid_styles)}")
        return v.lower()
    
    # Validate HEX color
    @classmethod
    def validate_hex_color(cls, v):
        hex_pattern = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
        if not re.match(hex_pattern, v):
            raise ValueError("Primary color must be a valid HEX color (e.g., #FF5733 or #F57)")
        return v.upper()

@app.post("/generate-brand-content")
async def generate_brand_content(request: BrandingRequest):
    """
    Endpoint to generate brand content based on company parameters.
    """
    
    # Validate and normalize input
    try:
        tone = request.validate_tone(request.tone)
        design_style = request.validate_design_style(request.design_style)
        primary_color = request.validate_hex_color(request.primary_color)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Store the parameters
    brand_parameters = {
        "company_name": request.company_name,
        "brand_identity": request.brand_identity,
        "tone": tone,
        "design_style": design_style,
        "primary_color": primary_color
    }

    # Testing: return the received parameters
    # return brand_parameters
    

    # TODO: Create the prompt using the brand parameters
    prompt = create_prompt_from_parameters(brand_parameters)
    # This is where you will create your custom prompt
    
    # Query ChatGPT with the prompt
    chatgpt_response = query_chatgpt_function(prompt)  # Function call placeholder


    
    # TODO: Save the response to S3
    # s3_upload_logic(chatgpt_response, brand_parameters)
    # This is where the S3 upload logic would be implemented
    
    return {
        "status": "success",
        "message": "Brand content generated successfully",
        "parameters_received": brand_parameters,
        "chatgpt_response": chatgpt_response
        # In production, you might want to return an S3 URL or reference
    }

@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Brand Content Generator API is running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}