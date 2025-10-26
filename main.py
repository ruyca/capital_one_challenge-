from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import re
from query_chatgpt import create_prompt_from_parameters, query_chatgpt_function, validate_html

app = FastAPI(title="Brand Content Generator API")

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
    
    try:
        # Create the enhanced prompt using the brand parameters
        prompt = create_prompt_from_parameters(brand_parameters)
        
        # Query ChatGPT with the prompt
        html_content = query_chatgpt_function(prompt, verbose=True)
        
        # Validate the HTML
        if not validate_html(html_content):
            print("Warning: HTML validation failed, but continuing...")
        
        # TODO: Save the response to S3
        # s3_key = f"{request.company_name.lower().replace(' ', '_')}_{datetime.now().isoformat()}.html"
        # s3_url = upload_to_s3(html_content, s3_key, brand_parameters)
        # This is where the S3 upload logic would be implemented
        
        return {
            "status": "success",
            "message": "Brand website generated successfully",
            "parameters_used": brand_parameters,
            "html_length": len(html_content),
            "html_content": html_content
            # "s3_url": s3_url,  # Would return S3 URL in production
            # For testing, you might want to return the HTML directly:
            # "html_preview": html_content[:500] + "..." if len(html_content) > 500 else html_content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")

@app.post("/generate-brand-content-preview", response_class=HTMLResponse)
async def generate_brand_content_preview(request: BrandingRequest):
    """
    Endpoint to generate and preview the brand website directly (for testing).
    Returns the HTML directly so you can view it in a browser.
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
    
    try:
        # Create the enhanced prompt using the brand parameters
        prompt = create_prompt_from_parameters(brand_parameters)
        
        # Query ChatGPT with the prompt
        html_content = query_chatgpt_function(prompt, verbose=True)
        
        # Return the HTML directly for preview
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")

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