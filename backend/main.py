"""
FastAPI application for the Website Generator.

This is the main application file that defines all API endpoints,
handles async processing, and serves the web interface.
"""

import asyncio
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .database import db
from .models import (
    WebsiteRequest, WebsiteResponse, JobRequest, JobResponse, 
    JobStatus, HealthResponse
)
from .utils import (
    extract_identifier, scrape_website, generate_optimized_html, 
    ensure_unique_identifier
)

# Create FastAPI application
app = FastAPI(
    title="Website Generator",
    description="Scrape websites and generate optimized HTML using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global job storage for tracking async tasks
active_jobs = {}


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    await db.connect()
    print("🚀 Website Generator API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connection on shutdown."""
    await db.disconnect()
    print("👋 Website Generator API stopped")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        db_healthy = await db.health_check()
        return HealthResponse(
            status="healthy" if db_healthy else "unhealthy",
            timestamp=datetime.now(),
            database="connected" if db_healthy else "disconnected"
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            database=f"error: {str(e)}"
        )


async def process_website_async(job_id: UUID, url: str):
    """
    Async background task to process website.
    
    Args:
        job_id: The job ID to track progress
        url: The URL to process
    """
    try:
        print(f"🔄 Starting job {job_id} for URL: {url}")
        
        # Update job status to processing
        await db.update_job_status(job_id, "processing")
        active_jobs[str(job_id)] = {"status": "processing", "error": None}
        
        # Step 1: Extract identifier and check uniqueness
        base_identifier = extract_identifier(url)
        identifier = base_identifier
        counter = 1
        
        while await db.website_exists(identifier):
            identifier = f"{base_identifier}{counter}"
            counter += 1
            if counter > 100:  # Safety break
                identifier = f"{base_identifier}_{str(uuid4())[:8]}"
                break
        
        print(f"📋 Using identifier: {identifier}")
        
        # Step 2: Scrape the website
        print(f"🌐 Scraping website: {url}")
        scraped_data = scrape_website(url)
        
        # Step 3: Create website record
        website_id = await db.create_website(
            identifier=identifier,
            original_url=url,
            original_html=scraped_data['original_html']
        )
        
        # Update job with website ID
        await db.update_job_status(job_id, "processing", website_id=website_id)
        active_jobs[str(job_id)]["website_id"] = str(website_id)
        active_jobs[str(job_id)]["identifier"] = identifier
        
        print(f"💾 Created website record: {website_id}")
        
        # Step 4: Generate optimized HTML
        print(f"🤖 Generating HTML with AI...")
        generated_html = generate_optimized_html(scraped_data)
        
        # Step 5: Update website with generated HTML
        await db.update_website_html(website_id, generated_html)
        
        # Step 6: Mark job as completed
        await db.update_job_status(job_id, "completed", website_id=website_id)
        active_jobs[str(job_id)] = {
            "status": "completed", 
            "error": None,
            "website_id": str(website_id),
            "identifier": identifier
        }
        
        print(f"✅ Job {job_id} completed successfully")
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Job {job_id} failed: {error_msg}")
        
        # Update job status to failed
        await db.update_job_status(job_id, "failed", error_message=error_msg)
        active_jobs[str(job_id)] = {"status": "failed", "error": error_msg}


@app.post("/generate", response_model=JobResponse)
async def generate_website(
    request: JobRequest, 
    background_tasks: BackgroundTasks
):
    """
    Start website generation process.
    
    Args:
        request: Job request containing URL to process
        background_tasks: FastAPI background tasks
        
    Returns:
        Job response with job ID for tracking
    """
    try:
        # Create a new job
        job_id = await db.create_job()
        
        # Add to active jobs tracking
        active_jobs[str(job_id)] = {"status": "pending", "error": None}
        
        # Start background processing
        background_tasks.add_task(process_website_async, job_id, str(request.url))
        
        print(f"🎯 Created job {job_id} for URL: {request.url}")
        
        return JobResponse(
            id=job_id,
            status="pending",
            created_at=datetime.now()
        )
        
    except Exception as e:
        print(f"❌ Failed to create job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


@app.get("/status/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: UUID):
    """
    Get the status of a processing job.
    
    Args:
        job_id: The job ID to check
        
    Returns:
        Job status information
    """
    try:
        # Check active jobs first for real-time status
        job_id_str = str(job_id)
        if job_id_str in active_jobs:
            job_info = active_jobs[job_id_str]
            return JobResponse(
                id=job_id,
                website_id=UUID(job_info["website_id"]) if job_info.get("website_id") else None,
                status=job_info["status"],
                error_message=job_info.get("error"),
                created_at=datetime.now(),
                identifier=job_info.get("identifier")
            )
        
        # Fallback to database
        job = await db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # If job is completed, get identifier from website
        identifier = None
        if job.status == "completed" and job.website_id:
            website = await db.get_website_by_id(job.website_id)
            if website:
                identifier = website.identifier
        
        return JobResponse(
            id=job.id,
            website_id=job.website_id,
            status=job.status,
            error_message=job.error_message,
            created_at=job.created_at,
            identifier=identifier
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@app.get("/raw/{identifier}", response_class=HTMLResponse)
async def get_raw_website(identifier: str):
    """
    Serve the raw generated website HTML for iframe embedding.
    
    Args:
        identifier: The website identifier
        
    Returns:
        Raw HTML response without security headers
    """
    try:
        website = await db.get_website(identifier)
        if not website:
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Website Not Found</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: #e74c3c; }
                    </style>
                </head>
                <body>
                    <h1 class="error">Website Not Found</h1>
                    <p>The requested website could not be found.</p>
                    <p>Please check the URL and try again.</p>
                </body>
                </html>
                """,
                status_code=404
            )
        
        if not website.generated_html:
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Website Processing</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .processing { color: #3498db; }
                    </style>
                </head>
                <body>
                    <h1 class="processing">Website Processing</h1>
                    <p>This website is still being processed.</p>
                    <p>Please try again in a few moments.</p>
                </body>
                </html>
                """,
                status_code=202
            )
        
        # Serve raw HTML without restrictive security headers for iframe embedding
        return HTMLResponse(content=website.generated_html)
        
    except Exception as e:
        print(f"❌ Failed to serve raw website {identifier}: {e}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Server Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: #e74c3c; }}
                </style>
            </head>
            <body>
                <h1 class="error">Server Error</h1>
                <p>An error occurred while loading this website.</p>
                <p>Error: {str(e)[:200]}</p>
            </body>
            </html>
            """,
            status_code=500
        )


@app.get("/website/{identifier}", response_class=HTMLResponse)
async def get_website(identifier: str):
    """
    Serve the website viewer page with sandboxed iframe.
    
    Args:
        identifier: The website identifier
        
    Returns:
        HTML response with iframe viewer
    """
    try:
        # Check if website exists
        website = await db.get_website(identifier)
        if not website:
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Website Not Found</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: #e74c3c; }
                    </style>
                </head>
                <body>
                    <h1 class="error">Website Not Found</h1>
                    <p>The requested website could not be found.</p>
                    <p>Please check the URL and try again.</p>
                </body>
                </html>
                """,
                status_code=404
            )
        
        # Serve iframe viewer page
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Website Viewer - {identifier}</title>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: #f5f5f5;
                        display: flex;
                        flex-direction: column;
                        height: 100vh;
                    }}
                    
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 15px 20px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    
                    .header h1 {{
                        font-size: 1.2rem;
                        font-weight: 600;
                    }}
                    
                    .header .url {{
                        font-size: 0.9rem;
                        opacity: 0.9;
                        background: rgba(255,255,255,0.2);
                        padding: 5px 12px;
                        border-radius: 20px;
                        max-width: 300px;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                    }}
                    
                    .iframe-container {{
                        flex: 1;
                        padding: 0;
                        background: white;
                    }}
                    
                    .website-frame {{
                        width: 100%;
                        height: 100%;
                        border: none;
                        display: block;
                    }}
                    
                    .security-notice {{
                        position: fixed;
                        bottom: 10px;
                        right: 10px;
                        background: rgba(0,0,0,0.8);
                        color: white;
                        padding: 8px 12px;
                        border-radius: 6px;
                        font-size: 0.8rem;
                        opacity: 0.7;
                        z-index: 1000;
                    }}
                    
                    @media (max-width: 768px) {{
                        .header {{
                            flex-direction: column;
                            gap: 10px;
                            text-align: center;
                        }}
                        
                        .header .url {{
                            max-width: 100%;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🌐 Generated Website</h1>
                    <div class="url">{website.original_url}</div>
                </div>
                
                <div class="iframe-container">
                    <iframe 
                        src="/raw/{identifier}"
                        class="website-frame"
                        sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-top-navigation-by-user-activation"
                        loading="lazy"
                        title="Generated website for {identifier}">
                    </iframe>
                </div>
                
                <div class="security-notice">
                    🔒 Sandboxed Content
                </div>
            </body>
            </html>
            """,
            headers={
                "X-Frame-Options": "DENY",
                "Content-Security-Policy": "default-src 'self'; style-src 'self' 'unsafe-inline'; frame-src 'self';",
                "X-Content-Type-Options": "nosniff"
            }
        )
        
    except Exception as e:
        print(f"❌ Failed to serve website viewer {identifier}: {e}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Server Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: #e74c3c; }}
                </style>
            </head>
            <body>
                <h1 class="error">Server Error</h1>
                <p>An error occurred while loading this website.</p>
                <p>Error: {str(e)[:200]}</p>
            </body>
            </html>
            """,
            status_code=500
        )


# Serve the main web interface
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main web interface."""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.2);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 40px;
            font-size: 1.2rem;
        }
        
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        
        input[type="url"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        input[type="url"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            display: none;
        }
        
        .status.processing {
            background: #e3f2fd;
            color: #1976d2;
            border: 1px solid #bbdefb;
            display: block;
        }
        
        .status.success {
            background: #e8f5e8;
            color: #2e7d32;
            border: 1px solid #c8e6c9;
            display: block;
        }
        
        .status.error {
            background: #ffebee;
            color: #d32f2f;
            border: 1px solid #ffcdd2;
            display: block;
        }
        
        .result {
            margin-top: 20px;
            display: none;
        }
        
        .result.show {
            display: block;
        }
        
        .result-btn {
            background: #4caf50;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: background 0.3s ease;
        }
        
        .result-btn:hover {
            background: #45a049;
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #1976d2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .preview-section {
            margin-top: 25px;
        }
        
        .preview-title {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1rem;
            font-weight: 600;
            text-align: center;
        }
        
        .preview-container {
            width: 100%;
            aspect-ratio: 1;
            border: 2px solid #e1e5e9;
            border-radius: 15px;
            overflow: hidden;
            position: relative;
            background: #f8f9fa;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .preview-iframe {
            position: absolute;
            top: 0;
            left: 0;
            border: none;
            transform-origin: top left;
            background: white;
        }
        
        @media (min-width: 769px) {
            .preview-iframe {
                width: 1200px;
                height: 800px;
                transform: scale(0.5);
            }
        }
        
        @media (min-width: 481px) and (max-width: 768px) {
            .preview-iframe {
                width: 768px;
                height: 1024px;
                transform: scale(0.6);
            }
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 30px 20px;
                margin: 10px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .preview-iframe {
                width: 375px;
                height: 667px;
                transform: scale(1.2);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Website Generator</h1>
        <p class="subtitle">Transform any website into a modern, optimized version using AI</p>
        
        <form id="websiteForm">
            <div class="form-group">
                <label for="url">Website URL:</label>
                <input type="url" id="url" name="url" placeholder="https://example.com" required>
            </div>
            
            <button type="submit" class="btn" id="generateBtn">
                Generate Optimized Website
            </button>
        </form>
        
        <div id="status" class="status"></div>
        <div id="result" class="result"></div>
    </div>

    <script>
        const form = document.getElementById('websiteForm');
        const urlInput = document.getElementById('url');
        const generateBtn = document.getElementById('generateBtn');
        const statusDiv = document.getElementById('status');
        const resultDiv = document.getElementById('result');
        
        let currentJobId = null;
        let pollInterval = null;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const url = urlInput.value.trim();
            if (!url) return;
            
            // Reset UI
            generateBtn.disabled = true;
            generateBtn.textContent = 'Processing...';
            statusDiv.className = 'status processing';
            statusDiv.innerHTML = '<div class="spinner"></div>Starting website generation...';
            resultDiv.className = 'result';
            resultDiv.innerHTML = '';
            
            try {
                // Start generation
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const job = await response.json();
                currentJobId = job.id;
                
                // Start polling for status
                pollJobStatus();
                
            } catch (error) {
                showError(`Failed to start generation: ${error.message}`);
                resetForm();
            }
        });
        
        async function pollJobStatus() {
            if (!currentJobId) return;
            
            try {
                const response = await fetch(`/status/${currentJobId}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const job = await response.json();
                
                switch (job.status) {
                    case 'pending':
                        statusDiv.innerHTML = '<div class="spinner"></div>Job queued, waiting to start...';
                        break;
                        
                    case 'processing':
                        statusDiv.innerHTML = '<div class="spinner"></div>Processing website with AI...';
                        break;
                        
                    case 'completed':
                        statusDiv.className = 'status success';
                        statusDiv.innerHTML = '✅ Website generation completed successfully!';
                        
                        resultDiv.className = 'result show';
                        resultDiv.innerHTML = `
                            <p style="margin-bottom: 15px;">Your optimized website is ready!</p>
                            <a href="/website/${job.identifier}" target="_blank" class="result-btn">
                                🌐 View Website
                            </a>
                            
                            <div class="preview-section">
                                <h3 class="preview-title">Preview:</h3>
                                <div class="preview-container">
                                    <iframe 
                                        src="/raw/${job.identifier}"
                                        class="preview-iframe"
                                        sandbox="allow-scripts allow-same-origin allow-forms"
                                        loading="lazy"
                                        title="Website Preview">
                                    </iframe>
                                </div>
                            </div>
                        `;
                        
                        clearInterval(pollInterval);
                        resetForm();
                        break;
                        
                    case 'failed':
                        throw new Error(job.error_message || 'Generation failed');
                        
                    default:
                        throw new Error(`Unknown job status: ${job.status}`);
                }
                
                // Continue polling if still processing
                if (job.status === 'pending' || job.status === 'processing') {
                    pollInterval = setTimeout(pollJobStatus, 2000);
                }
                
            } catch (error) {
                showError(`Status check failed: ${error.message}`);
                clearInterval(pollInterval);
                resetForm();
            }
        }
        
        function showError(message) {
            statusDiv.className = 'status error';
            statusDiv.innerHTML = `❌ ${message}`;
        }
        
        function resetForm() {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Optimized Website';
            currentJobId = null;
        }
    </script>
</body>
</html>
    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
