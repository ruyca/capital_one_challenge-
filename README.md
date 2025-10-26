# Capital One Challenge - Brand Content Generator API 🚀

A FastAPI-based API that generates personalized brand content using OpenAI and automatically uploads it to AWS S3.

## 📋 Features

- ✨ Generate personalized HTML websites using GPT-5  
- 🎨 Customize tone, design style, and brand colors  
- 💾 Automatically save generated HTML files locally  
- ☁️ Automatically upload files to AWS S3 with pre-signed URLs  
- 🔒 Validate input parameters  
- 📊 Include health and monitoring endpoints  
- ⏰ Pre-signed URLs with configurable expiration time (default: 7 days)  

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/ruyca/capital_one_challenge-.git
cd capital_one_challenge-
```

### 2. Install dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Configure environment variables
Edit the .env file with your credentials:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

### 4. Configure your S3 bucket
Make sure your S3 bucket:

- Has write permissions enabled
- Allows public ACLs for objects (if you want public URLs)
- Is in the region specified in your .env file

## 🚀 Usage
Start the server
```bash
uvicorn main:app --reload
```
The server will be available at: `http://localhost:8000`

__Interactive documentation__
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

  ## 📡 Endpoints

  ### 1. Generate brand content and upload to S3
  ```bash
  POST /generate-brand-content
  ```

**Request Body:**
```json
{
  "company_name": "TechCorp",
  "brand_identity": "Innovative technology solutions",
  "tone": "formal",
  "design_style": "modern",
  "primary_color": "#0066CC"
}
```
**Response:**
```json
{
  "success": true,
  "message": "Website generated and uploaded to S3 successfully",
  "local_file": {
    "filename": "techcorp_20251025_223854.html",
    "filepath": "/path/to/generated_websites/techcorp_20251025_223854.html"
  },
  "s3": {
    "public_url": "https://your-bucket.s3.us-east-1.amazonaws.com/brand-websites/techcorp_20251025_223854.html",
    "s3_key": "brand-websites/techcorp_20251025_223854.html",
    "bucket": "your-bucket",
    "region": "us-east-1"
  },
  "company_name": "TechCorp",
  "timestamp": "20251025_223854"
}
```

### 2. Preview content (without saving)
```bash
POST /generate-brand-content-preview
```
Returns the HTML directly for browser preview.

### 3. Download local file
```bash
GET /download/{filename}
```

### 4. Verify S3 configuration
```bash
GET /s3/config
```

### 5. List files in S3
```bash
GET /s3/files?max_items=100
```

### 6. Health Check
```bash
GET /health
```

## 🎨 Customization Parameters

### Tone
- formal: Sophisticated, elegant, professional
- semiformal: Balanced, modern, approachable
- casual: Friendly, relaxed, welcoming
- playful: Fun, energetic, creative

###Design Style
- modern: Gradients, glassmorphism, soft shadows
- minimalistic: Clean lines, generous spacing, typography-focused
- corporate: Structured layouts, professional schemes
- artistic: Creative layouts, bold typography, unique shapes

### Primary Color
- HEX format: `#FF5733` or `#F57`

## 📁 Project Structure
```bash
capital_one_challenge-/
├── main.py                    # Main FastAPI app
├── query_chatgpt.py           # OpenAI generation logic
├── s3_uploader.py             # AWS S3 upload module
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── README.md                  # Documentation
└── generated_websites/        # Locally generated HTML files
    └── *.html
```

## 🔐 Security
- ⚠️ Never commit the .env file to the repository
- 🔑 Keep your AWS and OpenAI credentials secure
- 🛡️ Use IAM roles with minimal permissions for S3

##📝 Example usage with curl
```bash
curl -X POST "http://localhost:8000/generate-brand-content" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "My Company",
    "brand_identity": "Innovative solutions for the future",
    "tone": "modern",
    "design_style": "modern",
    "primary_color": "#6366F1"
  }'
```
## 🐛 Troubleshooting
Error: "AWS credentials not found"
- Check that AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set in .env

Error: "Bucket not accessible"
- Make sure your bucket name is correct
- Ensure your credentials have permission to access the bucket

Error: "OpenAI API key not found"
- Check that OPENAI_API_KEY is set in .env

## 🤝 Contribution
This project was developed for the HackMTY - Capital One Challenge.

## 📄 License
MIT License



Developed with ❤️ for HackMTY



