# Capital One Challenge - Brand Content Generator API 🚀

API de FastAPI que genera contenido de marca personalizado usando OpenAI y lo sube automáticamente a AWS S3.

## 📋 Características

- ✨ Generación de sitios web HTML personalizados usando GPT-5
- 🎨 Personalización de tono, estilo de diseño y colores de marca
- 💾 Guardado local automático de archivos HTML
- ☁️ Subida automática a AWS S3 con URLs pre-firmadas (pre-signed URLs)
- 🔒 Validación de parámetros de entrada
- 📊 Endpoints de salud y monitoreo
- ⏰ URLs pre-firmadas con expiración configurable (por defecto 7 días)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/ruyca/capital_one_challenge-.git
cd capital_one_challenge-
```

### 2. Instalar dependencias
```bash
pip3 install -r requirements.txt
```

### 3. Configurar variables de entorno

Edita el archivo `.env` con tus credenciales:

```env
# OpenAI Configuration
OPENAI_API_KEY=tu-openai-api-key

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=tu-aws-access-key
AWS_SECRET_ACCESS_KEY=tu-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=tu-bucket-name
```

### 4. Configurar tu bucket de S3

Asegúrate de que tu bucket de S3:
- Tenga permisos de escritura configurados
- Permita ACL públicas para los objetos (si deseas URLs públicas)
- Esté en la región especificada en `.env`

## 🚀 Uso

### Iniciar el servidor
```bash
uvicorn main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

### Documentación interactiva
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📡 Endpoints

### 1. Generar contenido de marca y subir a S3
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
    "public_url": "https://tu-bucket.s3.us-east-1.amazonaws.com/brand-websites/techcorp_20251025_223854.html",
    "s3_key": "brand-websites/techcorp_20251025_223854.html",
    "bucket": "tu-bucket",
    "region": "us-east-1"
  },
  "company_name": "TechCorp",
  "timestamp": "20251025_223854"
}
```

### 2. Vista previa del contenido (sin guardar)
```bash
POST /generate-brand-content-preview
```
Devuelve el HTML directamente para previsualización en el navegador.

### 3. Descargar archivo local
```bash
GET /download/{filename}
```

### 4. Verificar configuración de S3
```bash
GET /s3/config
```

### 5. Listar archivos en S3
```bash
GET /s3/files?max_items=100
```

### 6. Health Check
```bash
GET /health
```

## 🎨 Parámetros de personalización

### Tone (Tono)
- `formal`: Sofisticado, elegante, profesional
- `semiformal`: Equilibrado, moderno, cercano
- `casual`: Amigable, relajado, acogedor
- `playful`: Divertido, enérgico, creativo

### Design Style (Estilo de diseño)
- `modern`: Gradientes, glassmorphism, sombras suaves
- `minimalistic`: Líneas limpias, espacios generosos, tipografía
- `corporate`: Layouts estructurados, esquemas profesionales
- `artistic`: Layouts creativos, tipografía audaz, formas únicas

### Primary Color
- Formato HEX: `#FF5733` o `#F57`

## 📁 Estructura del proyecto

```
capital_one_challenge-/
├── main.py                    # FastAPI app principal
├── query_chatgpt.py          # Lógica de generación con OpenAI
├── s3_uploader.py            # Módulo de subida a S3
├── requirements.txt          # Dependencias de Python
├── .env                      # Variables de entorno
├── README.md                 # Documentación
└── generated_websites/       # Archivos HTML generados localmente
    └── *.html
```

## 🔐 Seguridad

- ⚠️ **Nunca** subas el archivo `.env` al repositorio
- 🔑 Mantén tus credenciales de AWS y OpenAI seguras
- 🛡️ Usa IAM roles con permisos mínimos para S3

## 📝 Ejemplo de uso con curl

```bash
curl -X POST "http://localhost:8000/generate-brand-content" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Mi Empresa",
    "brand_identity": "Soluciones innovadoras para el futuro",
    "tone": "modern",
    "design_style": "modern",
    "primary_color": "#6366F1"
  }'
```

## 🐛 Troubleshooting

### Error: "AWS credentials not found"
- Verifica que las variables `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` estén configuradas en `.env`

### Error: "Bucket not accessible"
- Verifica que el nombre del bucket sea correcto
- Verifica que tus credenciales tengan permisos para acceder al bucket

### Error: "OpenAI API key not found"
- Verifica que `OPENAI_API_KEY` esté configurada en `.env`

## 🤝 Contribución

Este proyecto fue desarrollado para el HackMTY - Capital One Challenge.

## 📄 Licencia

MIT License

---

Desarrollado con ❤️ para HackMTY
