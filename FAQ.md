# FAQ - Frequently Asked Questions

## Development Environment

### Q: What is the command to restart Docker?
**Date:** 2025-09-01

**Answer:** On Windows, you can restart Docker Desktop using these methods:

1. **From System Tray**
   - Right-click Docker icon in system tray
   - Click "Restart"

2. **From PowerShell/CMD (as Administrator)**
   ```powershell
   # Stop Docker
   net stop com.docker.service
   
   # Start Docker
   net start com.docker.service
   ```

3. **Using Docker Desktop CLI**
   ```bash
   # Quit Docker Desktop
   "C:\Program Files\Docker\Docker\DockerCli.exe" -SwitchDaemon
   
   # Or simply restart Windows Service
   Restart-Service *docker*
   ```

4. **Easiest: Open Docker Desktop App**
   - Open Docker Desktop from Start Menu
   - It will start automatically

Once Docker is running, start your containers:
```bash
docker-compose up -d
```

---

### Q: How to install Docker Desktop on Windows 11 and macOS?
**Date:** 2025-09-01

**Answer:** 

#### Windows 11 Installation

1. **System Requirements:**
   - Windows 11 64-bit: Pro, Enterprise, or Education
   - 64-bit processor with SLAT
   - 4GB RAM minimum
   - BIOS virtualization enabled

2. **Installation Steps:**
   - Download Docker Desktop from https://www.docker.com/products/docker-desktop/
   - Run the installer `Docker Desktop Installer.exe`
   - Keep "Use WSL 2 instead of Hyper-V" option selected
   - Click "Ok" to install
   - Restart Windows when prompted
   - Launch Docker Desktop from Start menu

3. **Post-Installation:**
   ```powershell
   # Verify installation
   docker --version
   docker run hello-world
   ```

#### macOS Installation

1. **System Requirements:**
   - macOS 11 or newer
   - Apple Silicon or Intel chip
   - 4GB RAM minimum

2. **Installation Steps:**
   - Download Docker Desktop from https://www.docker.com/products/docker-desktop/
   - Choose correct version (Apple Silicon or Intel)
   - Open the `.dmg` file
   - Drag Docker.app to Applications folder
   - Launch Docker from Applications
   - Accept the license agreement

3. **Post-Installation:**
   ```bash
   # Verify installation
   docker --version
   docker run hello-world
   ```

---

### Q: How to add support for Google models using Google Cloud?
**Date:** 2025-09-01

**Answer:**

#### Prerequisites
1. **Google Cloud Account**: Create one at https://console.cloud.google.com
2. **Project**: Create or select a Google Cloud project
3. **Billing**: Enable billing (required for API usage, though there's a free tier)

#### Step 1: Enable Required APIs

1. **Navigate to API Library:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Select your project
   - Go to **APIs & Services → Library**

2. **Enable These APIs:**
   - **Generative Language API** (for Gemini models)
   - **Vertex AI API** (for advanced features)
   - Search and click "ENABLE" for each

#### Step 2: Authentication Setup

**Option A: API Key (Simple, Less Secure)**
1. Go to **APIs & Services → Credentials**
2. Click **"+ CREATE CREDENTIALS" → API Key**
3. Restrict the key to specific APIs for security
4. Copy the API key

**Option B: Service Account (Production, More Secure)**
1. Go to **IAM & Admin → Service Accounts**
2. Click **"+ CREATE SERVICE ACCOUNT"**
3. Name it (e.g., "gemini-api-access")
4. Grant role: **"Vertex AI User"** or **"AI Platform Developer"**
5. Create and download JSON key file
6. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   ```

#### Step 3: Install Required Libraries

```bash
# For Gemini via Google AI
pip install google-generativeai

# For Vertex AI (more features)
pip install google-cloud-aiplatform

# For other Google Cloud services
pip install google-cloud-storage google-cloud-translate
```

#### Step 4: Implementation in Code

**Using Google AI (Gemini Direct):**
```python
import google.generativeai as genai

# Configure with API key
genai.configure(api_key="YOUR_API_KEY")

# Initialize model
model = genai.GenerativeModel('gemini-1.5-pro')

# Generate response
response = model.generate_content("Explain quantum computing")
print(response.text)
```

**Using Vertex AI (More Advanced):**
```python
from vertexai.generative_models import GenerativeModel
import vertexai

# Initialize Vertex AI
vertexai.init(
    project="your-project-id",
    location="us-central1"
)

# Create model instance
model = GenerativeModel("gemini-1.5-pro")

# Generate response
response = model.generate_content("Explain quantum computing")
print(response.text)
```

#### Step 5: Environment Configuration

Add to your `.env` file:
```env
# For Google AI (Gemini)
GOOGLE_API_KEY=your-api-key-here
GOOGLE_DEFAULT_MODEL=gemini-1.5-flash

# For Vertex AI (if using)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

#### Step 6: Available Models

**Google AI (Gemini) Models:**
- `gemini-1.5-flash` - Fast, efficient, 1M context
- `gemini-1.5-pro` - Most capable, 2M context
- `gemini-2.0-flash-exp` - Latest experimental

**Vertex AI Models:**
- All Gemini models
- PaLM 2 models
- Codey for code generation
- Imagen for image generation
- Chirp for speech

#### Step 7: Cost Considerations

**Free Tier (Google AI):**
- 60 requests per minute
- 1 million tokens per month

**Paid Usage:**
- Gemini 1.5 Flash: $0.075 per 1M tokens
- Gemini 1.5 Pro: $1.25 per 1M tokens
- Vertex AI has different pricing

#### Step 8: Common Issues & Solutions

1. **"API not enabled" error**: Enable the API in Cloud Console
2. **"Quota exceeded"**: Check quotas in IAM & Admin → Quotas
3. **"Authentication failed"**: Verify credentials and permissions
4. **"Model not found"**: Check model name and region availability

#### Best Practices

1. **Use Service Accounts** for production
2. **Implement rate limiting** to avoid quota issues
3. **Cache responses** when possible
4. **Monitor usage** in Cloud Console
5. **Set up alerts** for quota limits
6. **Use appropriate models** for your use case (Flash for speed, Pro for quality)

---

### Q: What is Gemini 2.5 Flash Image and how can we use it?
**Date:** 2025-09-01

**Answer:**

Gemini 2.5 Flash Image (API name: `gemini-2.5-flash-image-preview`) is a multimodal AI model that can both generate images and function as a normal text AI. This makes it uniquely versatile for applications requiring both visual and textual content.

#### Key Capabilities

##### 1. Image Generation
The model can create new images from text descriptions with several advanced features:

- **Text-to-Image**: Create images solely from text prompts
  - Example: "Generate an image of a red car driving on a winding road"
  
- **Image Editing**: Modify existing images based on text instructions
  - Examples: "blur the background of this image", "add a hat to the person in this photo"
  
- **Multi-Image Fusion**: Combine elements from multiple input images into a new one
  
- **Iterative Refinement**: Have a conversation with the model to refine images over several turns
  
- **Character Consistency**: Maintain the appearance of a character or object across different generations or scenes (useful for storytelling or consistent branding)
  
- **High-Fidelity Text Rendering**: Accurately generate images that contain legible and well-placed text

##### 2. Normal Text AI (Multimodal Output)
Gemini 2.5 Flash Image can generate both images and text in its responses:

- **Interleave Images and Text**: Ask for "Generate an illustrated recipe for lasagna" and receive text steps with relevant images for each step
  
- **Respond with Text Only**: Functions as a regular language model when prompts ask for text-based information
  
- **Use World Knowledge**: Integrates Gemini's general world knowledge and reasoning capabilities into both text and image generation

#### Implementation Example

```python
import google.generativeai as genai

# Configure API
genai.configure(api_key="YOUR_API_KEY")

# Initialize the image-capable model
model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

# Text-to-Image generation
image_response = model.generate_content(
    "Generate an image of a futuristic city at sunset with flying cars"
)

# Multimodal response (text + images)
recipe_response = model.generate_content(
    "Create an illustrated step-by-step guide for making chocolate chip cookies"
)

# Image editing with existing image
from PIL import Image
existing_image = Image.open("photo.jpg")
edited_response = model.generate_content([
    "Add a rainbow in the sky of this image",
    existing_image
])

# Text-only response (works like regular Gemini)
text_response = model.generate_content(
    "Explain the theory of relativity in simple terms"
)
```

#### Use Cases in Our Application

1. **Enhanced Content Creation**: Generate blog posts with inline illustrations
2. **Product Visualization**: Create product images from descriptions
3. **Interactive Tutorials**: Step-by-step guides with visual aids
4. **Creative Storytelling**: Maintain character consistency across scenes
5. **UI/UX Mockups**: Generate interface designs from descriptions
6. **Data Visualization**: Create charts and infographics from data

#### Important Notes

- **Model Variant**: While `gemini-2.5-flash` is optimized for text, `gemini-2.5-flash-image-preview` extends capabilities to include robust image generation
- **API Costs**: Image generation typically costs more than text-only operations
- **Response Time**: Image generation takes longer than text-only responses
- **Content Filtering**: Google applies safety filters to both text and image outputs
- **Preview Status**: As indicated by "preview" in the name, this model may have changes before general availability

#### Configuration for Our Project

To add support in our existing Google AI service:

```python
# In config.py, add:
GOOGLE_IMAGE_MODEL = "gemini-2.5-flash-image-preview"

# In google_ai_service.py, add method:
async def generate_with_image(
    self,
    prompt: str,
    generate_image: bool = False,
    existing_image: Optional[bytes] = None
) -> dict:
    """Generate text, images, or both based on the prompt."""
    model = genai.GenerativeModel(settings.GOOGLE_IMAGE_MODEL)
    
    inputs = []
    if existing_image:
        inputs.append(Image.open(io.BytesIO(existing_image)))
    inputs.append(prompt)
    
    response = await model.generate_content_async(inputs)
    
    return {
        "text": response.text if hasattr(response, 'text') else None,
        "images": response.images if hasattr(response, 'images') else []
    }
```

This multimodal capability makes Gemini 2.5 Flash Image a powerful tool for applications requiring both visual and textual AI generation in a single unified model.

---
