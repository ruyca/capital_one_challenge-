from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
import re
from datetime import datetime
from pathlib import Path
from query_chatgpt import create_prompt_from_parameters, query_chatgpt_function, validate_html
from s3_uploader import upload_html_to_s3, check_s3_configuration, list_uploaded_files

app = FastAPI(title="Brand Content Generator API")

# Crear directorio para guardar archivos HTML si no existe
OUTPUT_DIR = Path("generated_websites")
OUTPUT_DIR.mkdir(exist_ok=True)

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
    Saves the HTML file and returns the file path.
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
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company_name = re.sub(r'[^\w\s-]', '', request.company_name).strip().replace(' ', '_').lower()
        filename = f"{safe_company_name}_{timestamp}.html"
        filepath = OUTPUT_DIR / filename
        
        # Save HTML to file locally
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML saved locally to: {filepath}")
        
        # Upload to S3 and get public URL
        try:
            s3_metadata = {
                "brand_identity": brand_parameters["brand_identity"],
                "tone": brand_parameters["tone"],
                "design_style": brand_parameters["design_style"],
                "primary_color": brand_parameters["primary_color"]
            }
            
            s3_result = upload_html_to_s3(
                html_content=html_content,
                company_name=request.company_name,
                metadata=s3_metadata
            )
            
            return {
                "success": True,
                "message": "Website generated and uploaded to S3 successfully",
                "local_file": {
                    "filename": filename,
                    "filepath": str(filepath)
                },
                "s3": {
                    "public_url": s3_result["public_url"],
                    "s3_key": s3_result["s3_key"],
                    "bucket": s3_result["bucket"],
                    "region": s3_result["region"]
                },
                "company_name": request.company_name,
                "timestamp": timestamp
            }
            
        except Exception as s3_error:
            # If S3 upload fails, still return success with local file info
            print(f"⚠️ S3 upload failed: {str(s3_error)}")
            return {
                "success": True,
                "message": "Website generated locally, but S3 upload failed",
                "local_file": {
                    "filename": filename,
                    "filepath": str(filepath)
                },
                "s3_error": str(s3_error),
                "company_name": request.company_name,
                "timestamp": timestamp
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Endpoint to download a generated HTML file.
    """
    filepath = OUTPUT_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=filepath,
        media_type="text/html",
        filename=filename
    )

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

@app.get("/s3/config")
async def check_s3_config():
    """
    Check S3 configuration status.
    """
    try:
        config_status = check_s3_configuration()
        return {
            "s3_configured": config_status["bucket_accessible"],
            "details": config_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking S3 config: {str(e)}")

@app.get("/s3/files")
async def list_s3_files(max_items: int = 100):
    """
    List uploaded files in S3.
    """
    try:
        files = list_uploaded_files(max_items=max_items)
        return {
            "success": True,
            "count": len(files),
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing S3 files: {str(e)}")