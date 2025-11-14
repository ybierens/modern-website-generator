"""
FastAPI application for the Website Generator.

This is the main application file that defines all API endpoints,
handles async processing, and serves the web interface.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
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
    ensure_unique_identifier, process_images, select_template_for_website
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
        
        # Step 4: Process images and convert to Cloudinary URLs
        print(f"🖼️ Processing images...")
        scraped_data = await process_images(scraped_data, website_id)
        
        # Step 5: Select appropriate template using AI router
        print(f"🎯 Selecting appropriate template...")
        template_id = select_template_for_website(scraped_data)
        
        # Store template selection in database
        await db.update_website_template(website_id, template_id)
        print(f"💾 Stored template selection: {template_id}")
        
        # Step 6: Generate optimized HTML with selected template
        print(f"🤖 Generating HTML with AI using '{template_id}' template...")
        generated_html = generate_optimized_html(scraped_data, template_id)
        
        # Step 7: Update website with generated HTML
        await db.update_website_html(website_id, generated_html)
        
        # Step 8: Mark job as completed
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


@app.get("/websites")
async def get_recent_websites():
    """
    Get the 10 most recent generated websites.
    
    Returns:
        List of recent websites with basic information
    """
    try:
        websites = await db.get_recent_websites(10)
        return [
            {
                "id": str(website.id),
                "identifier": website.identifier,
                "original_url": website.original_url,
                "created_at": website.created_at.isoformat(),
                "has_generated_html": website.generated_html is not None
            }
            for website in websites
        ]
    except Exception as e:
        print(f"❌ Failed to get recent websites: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent websites: {str(e)}")


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


# Demo website path
demo_website_path = Path(__file__).parent.parent / "demo-website" / "roberts-hvac"

@app.get("/demo/{file_path:path}")
async def serve_demo_file(file_path: str):
    """Serve files from the demo website."""
    try:
        full_path = demo_website_path / file_path
        # Security: ensure file is within demo directory
        if not str(full_path.resolve()).startswith(str(demo_website_path.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine content type
        content_type = "text/html"
        if file_path.endswith(".js"):
            content_type = "text/javascript"
        elif file_path.endswith(".css"):
            content_type = "text/css"
        elif file_path.endswith(".json"):
            content_type = "application/json"
        elif file_path.endswith(".svg"):
            content_type = "image/svg+xml"
        
        with open(full_path, "rb") as f:
            content = f.read()
        
        return HTMLResponse(content=content, media_type=content_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demo")
async def serve_demo_index():
    """Serve the demo website index page."""
    index_path = demo_website_path / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Demo website not found")
    
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        # Add base tag to make relative paths work correctly
        html_content = html_content.replace('<head>', '<head><base href="/demo/">')
        return HTMLResponse(content=html_content, media_type="text/html")

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
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 40px 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.2);
            padding: 40px;
            max-width: 900px;
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
            display: none;
            text-align: center;
            color: #333;
            font-size: 1rem;
        }
        
        .status.show {
            display: block;
        }
        
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .btn.loading {
            background: transparent !important;
            color: #333 !important;
            box-shadow: none !important;
            border: 2px solid #e1e5e9 !important;
        }
        
        .btn.loading:hover {
            transform: none !important;
            box-shadow: none !important;
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
            body {
                padding: 20px 10px;
            }
            
            .container {
                padding: 30px 20px;
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
        
        /* Website List Styles */
        .websites-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.2);
            padding: 40px;
            max-width: 900px;
            width: 100%;
            margin: 30px 0 0 0;
            display: none;
        }
        
        .websites-container.show {
            display: block;
        }
        
        .websites-container h2 {
            color: #333;
            margin-bottom: 30px;
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
        }
        
        .websites-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .website-item {
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .website-item:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        }
        
        .website-header {
            padding: 15px 20px;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.3s ease;
        }
        
        .website-header-left {
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
            cursor: pointer;
        }
        
        .website-header-right {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .expand-arrow {
            font-size: 1.2rem;
            color: #667eea;
            transition: transform 0.3s ease;
            user-select: none;
            cursor: pointer;
        }
        
        /* Hide View Website button by default - use !important to ensure it works */
        .website-btn-expanded-only {
            display: none !important;
        }
        
        /* Show View Website button only when expanded */
        .website-item.expanded .website-btn-expanded-only {
            display: inline-block !important;
        }
        
        .website-header:hover {
            background: #e9ecef;
        }
        
        .website-name {
            font-weight: 600;
            color: #333;
            font-size: 1rem;
        }
        
        
        .website-item.expanded .expand-arrow {
            transform: rotate(180deg);
        }
        
        .website-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            padding: 0 20px;
        }
        
        .website-item.expanded .website-content {
            max-height: 650px;
            padding: 20px;
        }
        
        .view-website-btn {
            border: none;
            padding: 8px 15px;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            position: relative;
            z-index: 10;
        }
        
        .view-website-btn:active {
            transform: scale(0.95);
        }
        
        .view-website-btn.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
        }
        
        .view-website-btn.primary:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
        }
        
        .view-website-btn.secondary {
            background: transparent;
            color: #666;
            border: 1px solid #ddd;
            font-weight: 500;
        }
        
        .view-website-btn.secondary:hover {
            background: #f5f5f5;
            color: #333;
            border-color: #bbb;
        }
        
        .website-preview {
            width: 100%;
            height: 450px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            overflow: hidden;
            background: #f8f9fa;
            position: relative;
            transition: all 0.3s ease;
        }
        
        .website-preview:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            transform: translateY(-2px);
        }
        
        .website-preview iframe {
            width: 1200px;
            height: 800px;
            border: none;
            background: white;
            transform-origin: top left;
            position: absolute;
            top: 0;
            left: 0;
        }
        
        /* Calculate scale based on container width */
        @media (min-width: 901px) {
            .website-preview iframe {
                transform: scale(calc((900px - 80px) / 1200px)); /* 900px container - 40px padding each side */
            }
        }
        
        @media (max-width: 900px) {
            .website-preview iframe {
                transform: scale(calc((100vw - 120px) / 1200px)); /* viewport width - padding and margins */
            }
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #666;
            font-size: 1.1rem;
        }
        
        .empty-state.hidden {
            display: none;
        }
        
        /* Mobile responsive scaling for previews */
        @media (max-width: 768px) {
            .website-preview {
                height: 375px;
            }
            
            .website-preview iframe {
                width: 768px;
                height: 1024px;
                transform: scale(calc((100vw - 80px) / 768px));
            }
        }
        
        @media (max-width: 480px) {
            .websites-container {
                padding: 30px 20px;
            }
            
            .websites-container h2 {
                font-size: 1.5rem;
            }
            
            .website-header {
                padding: 12px 15px;
            }
            
            .website-item.expanded .website-content {
                padding: 15px;
            }
            
            .website-preview {
                height: 300px;
            }
            
            .website-preview iframe {
                width: 375px;
                height: 667px;
                transform: scale(calc((100vw - 60px) / 375px));
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
            
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px; padding: 12px; background: #f8f9fa; border-radius: 8px;">
                <input type="checkbox" id="demoCheckbox" style="width: 18px; height: 18px; cursor: pointer;">
                <label for="demoCheckbox" style="margin: 0; cursor: pointer; color: #333; font-size: 0.95rem;">
                    View demo website instead
                </label>
            </div>
            
            <button type="submit" class="btn" id="generateBtn">
                Generate Optimized Website
            </button>
        </form>
        
        <div id="status" class="status"></div>
        <div id="result" class="result"></div>
    </div>

    <!-- Website List Container -->
    <div class="websites-container" id="websitesContainer">
        <h2>Generated Websites</h2>
        <div id="websitesList" class="websites-list">
            <!-- Website items will be populated by JavaScript -->
        </div>
        <div id="emptyState" class="empty-state">
            <p>No websites generated yet. Generate your first website above!</p>
        </div>
    </div>

    <script>
        const form = document.getElementById('websiteForm');
        const urlInput = document.getElementById('url');
        const generateBtn = document.getElementById('generateBtn');
        const statusDiv = document.getElementById('status');
        const resultDiv = document.getElementById('result');
        const websitesContainer = document.getElementById('websitesContainer');
        const websitesList = document.getElementById('websitesList');
        const emptyState = document.getElementById('emptyState');
        
        let currentJobId = null;
        let pollInterval = null;
        let websites = [];

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            loadWebsites();
        });

        // Load websites from API
        async function loadWebsites() {
            try {
                const response = await fetch('/websites');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                websites = await response.json();
                renderWebsites();
                
            } catch (error) {
                console.error('Failed to load websites:', error);
                // Show empty state on error
                showEmptyState();
            }
        }

        // Render websites list
        function renderWebsites() {
            if (websites.length === 0) {
                showEmptyState();
                return;
            }

            hideEmptyState();
            websitesList.innerHTML = '';
            
            websites.forEach((website, index) => {
                const websiteItem = createWebsiteItem(website, index === 0 && website.isNew);
                websitesList.appendChild(websiteItem);
            });
        }

        // Create individual website item
        function createWebsiteItem(website, isExpanded = false) {
            const item = document.createElement('div');
            item.className = `website-item${isExpanded ? ' expanded' : ''}`;
            item.dataset.identifier = website.identifier;
            
            item.innerHTML = `
                <div class="website-header">
                    <div class="website-header-left" onclick="toggleWebsiteItem('${website.identifier}')">
                        <span class="website-name">${website.identifier}</span>
                    </div>
                    <div class="website-header-right">
                        <a href="/website/${website.identifier}" target="_blank" class="view-website-btn primary website-btn-expanded-only" onclick="event.stopPropagation()">
                            ✨ View New Website
                        </a>
                        <a href="${website.original_url}" target="_blank" class="view-website-btn secondary website-btn-expanded-only" onclick="event.stopPropagation()" style="margin-right: 10px;">
                            View Old Website
                        </a>
                        <span class="expand-arrow" onclick="toggleWebsiteItem('${website.identifier}')">▼</span>
                    </div>
                </div>
                <div class="website-content">
                    ${website.has_generated_html ? `
                        <div class="website-preview" onclick="openWebsite('${website.identifier}')" style="cursor: pointer;">
                            <iframe 
                                src="/raw/${website.identifier}"
                                sandbox="allow-scripts allow-same-origin allow-forms"
                                loading="lazy"
                                title="Website Preview for ${website.identifier}"
                                style="pointer-events: none;">
                            </iframe>
                        </div>
                    ` : `
                        <div class="website-preview">
                            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">
                                Still processing...
                            </div>
                        </div>
                    `}
                </div>
            `;
            
            return item;
        }

        // Open website in new tab
        function openWebsite(identifier) {
            window.open(`/website/${identifier}`, '_blank');
        }

        // Toggle website item expand/collapse with accordion behavior
        function toggleWebsiteItem(identifier) {
            const clickedItem = document.querySelector(`[data-identifier="${identifier}"]`);
            if (!clickedItem) return;
            
            const isCurrentlyExpanded = clickedItem.classList.contains('expanded');
            
            // Close all expanded items first
            const allItems = document.querySelectorAll('.website-item');
            allItems.forEach(item => {
                item.classList.remove('expanded');
            });
            
            // If the clicked item wasn't expanded, expand it
            if (!isCurrentlyExpanded) {
                clickedItem.classList.add('expanded');
            }
        }

        // Show empty state
        function showEmptyState() {
            emptyState.classList.remove('hidden');
            websitesList.innerHTML = '';
            websitesContainer.classList.remove('show');
        }

        // Hide empty state
        function hideEmptyState() {
            emptyState.classList.add('hidden');
            websitesContainer.classList.add('show');
        }

        // Add new website to top of list
        function addNewWebsite(websiteData) {
            // Mark as new for auto-expansion
            websiteData.isNew = true;
            
            // Add to beginning of array
            websites.unshift(websiteData);
            
            // Keep only 10 most recent
            if (websites.length > 10) {
                websites = websites.slice(0, 10);
            }
            
            // Re-render (this will automatically expand the new item and close others)
            renderWebsites();
            
            // Scroll to show the new expanded preview in the middle of the screen
            setTimeout(() => {
                const newWebsiteItem = document.querySelector(`[data-identifier="${websiteData.identifier}"]`);
                if (newWebsiteItem) {
                    const rect = newWebsiteItem.getBoundingClientRect();
                    const viewportHeight = window.innerHeight;
                    const targetScrollTop = window.scrollY + rect.top - (viewportHeight / 2) + (newWebsiteItem.offsetHeight / 2);
                    
                    window.scrollTo({
                        top: targetScrollTop,
                        behavior: 'smooth'
                    });
                }
            }, 100); // Small delay to ensure rendering is complete
        }
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Check if demo checkbox is checked
            const demoCheckbox = document.getElementById('demoCheckbox');
            if (demoCheckbox && demoCheckbox.checked) {
                // Show loading state
                generateBtn.disabled = true;
                generateBtn.className = 'btn loading';
                generateBtn.innerHTML = '<span class="spinner"></span>Building modern website, this takes up to 20 seconds';
                statusDiv.className = 'status show';
                statusDiv.innerHTML = 'Generating demo website...';
                
                // Wait 15 seconds before redirecting
                setTimeout(() => {
                    window.location.href = '/demo';
                }, 15000);
                return;
            }
            
            const url = urlInput.value.trim();
            if (!url) return;
            
            // Reset UI
            generateBtn.disabled = true;
            generateBtn.className = 'btn loading';
            generateBtn.innerHTML = '<span class="spinner"></span>Building modern website, this takes up to 20 seconds';
            statusDiv.className = 'status';
            statusDiv.innerHTML = '';
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
                    case 'processing':
                        // Keep button text as is, no status updates during processing
                        break;
                        
                    case 'completed':
                        statusDiv.className = 'status show';
                        statusDiv.innerHTML = 'Website created successfully!';
                        
                        // Add new website to the list (will appear in expanded view)
                        const newWebsiteData = {
                            id: job.website_id,
                            identifier: job.identifier,
                            original_url: urlInput.value.trim(),
                            created_at: new Date().toISOString(),
                            has_generated_html: true
                        };
                        addNewWebsite(newWebsiteData);
                        
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
            statusDiv.className = 'status show';
            statusDiv.innerHTML = `Error: ${message}`;
            generateBtn.className = 'btn';
        }
        
        function resetForm() {
            generateBtn.disabled = false;
            generateBtn.className = 'btn';
            generateBtn.textContent = 'Generate Optimized Website';
            statusDiv.className = 'status';
            statusDiv.innerHTML = '';
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
