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
    ensure_unique_identifier, process_images, generate_version_instructions,
    generate_three_versions_parallel
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
        
        # Step 5: Generate creative instructions using GPT-5 thinking mode
        print(f"🎨 Generating 3 creative directions with GPT-5 thinking mode...")
        instructions = generate_version_instructions(scraped_data)
        
        # Step 6: Generate 3 versions in parallel
        print(f"🚀 Generating 3 website versions in parallel...")
        version_htmls = await generate_three_versions_parallel(scraped_data, instructions)
        
        # Step 7: Store all successful versions in database
        versions_created = 0
        for version_num, version_key in enumerate([('version_1', 1), ('version_2', 2), ('version_3', 3)], start=1):
            key, num = version_key
            html = version_htmls.get(key)
            instruction = instructions.get(key, '')
            
            if html:
                try:
                    await db.create_website_version(
                        website_id=website_id,
                        version_number=num,
                        generation_instructions=instruction,
                        generated_html=html
                    )
                    versions_created += 1
                    print(f"✅ Stored version {num} ({len(html)} chars)")
                except Exception as e:
                    print(f"⚠️ Failed to store version {num}: {e}")
        
        # Step 8: Mark job as completed if at least 1 version succeeded
        if versions_created > 0:
            await db.update_job_status(job_id, "completed", website_id=website_id)
            active_jobs[str(job_id)] = {
                "status": "completed", 
                "error": None,
                "website_id": str(website_id),
                "identifier": identifier,
                "versions_generated": versions_created
            }
            print(f"✅ Job {job_id} completed successfully with {versions_created}/3 versions")
        else:
            raise Exception("All 3 versions failed to generate")
        
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
    Get the 10 most recent generated websites with version information.
    
    Returns:
        List of recent websites with basic information and available versions
    """
    try:
        websites = await db.get_recent_websites(10)
        result = []
        
        for website in websites:
            # Get available versions for this website
            available_versions = await db.get_available_versions(website.id)
            
            result.append({
                "id": str(website.id),
                "identifier": website.identifier,
                "original_url": website.original_url,
                "created_at": website.created_at.isoformat(),
                "has_generated_html": len(available_versions) > 0,
                "available_versions": available_versions,
                "default_version": 1 if 1 in available_versions else (available_versions[0] if available_versions else None)
            })
        
        return result
    except Exception as e:
        print(f"❌ Failed to get recent websites: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent websites: {str(e)}")


@app.get("/raw/{identifier}/{version_number}", response_class=HTMLResponse)
@app.get("/raw/{identifier}", response_class=HTMLResponse)
async def get_raw_website(identifier: str, version_number: int = 1):
    """
    Serve the raw generated website HTML for iframe embedding.
    
    Args:
        identifier: The website identifier
        version_number: The version number (1, 2, or 3), defaults to 1
        
    Returns:
        Raw HTML response without security headers
    """
    try:
        # Get the specific version
        version = await db.get_website_version(identifier, version_number)
        
        if not version:
            # Try to get the website to see if it exists
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
            else:
                # Website exists but version doesn't - try version 1 as fallback
                if version_number != 1:
                    version = await db.get_website_version(identifier, 1)
                    if version and version.generated_html:
                        return HTMLResponse(content=version.generated_html)
                
                return HTMLResponse(
                    content=f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Version Not Found</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                            .error {{ color: #e74c3c; }}
                        </style>
                    </head>
                    <body>
                        <h1 class="error">Version {version_number} Not Found</h1>
                        <p>This version is still being processed or failed to generate.</p>
                        <p>Please try another version or try again later.</p>
                    </body>
                    </html>
                    """,
                    status_code=404
                )
        
        if not version.generated_html:
            return HTMLResponse(
                content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Website Processing</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                        .processing {{ color: #3498db; }}
                    </style>
                </head>
                <body>
                    <h1 class="processing">Version {version_number} Processing</h1>
                    <p>This version is still being generated.</p>
                    <p>Please try again in a few moments.</p>
                </body>
                </html>
                """,
                status_code=202
            )
        
        # Serve raw HTML without restrictive security headers for iframe embedding
        return HTMLResponse(content=version.generated_html)
        
    except Exception as e:
        print(f"❌ Failed to serve raw website {identifier} version {version_number}: {e}")
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
        
        # Get available versions
        available_versions = await db.get_available_versions(website.id)
        default_version = 1 if 1 in available_versions else (available_versions[0] if available_versions else 1)
        
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
                    
                    .version-control-wrapper {{
                        background: #f8f9fa;
                        padding: 15px 20px;
                        border-bottom: 1px solid #dee2e6;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }}
                    
                    .version-control {{
                        display: flex;
                        gap: 0;
                        background: white;
                        border-radius: 8px;
                        padding: 4px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    
                    .version-btn {{
                        padding: 10px 24px;
                        border: none;
                        background: transparent;
                        color: #495057;
                        font-size: 0.95rem;
                        font-weight: 500;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        border-radius: 6px;
                    }}
                    
                    .version-btn:hover:not(:disabled) {{
                        background: #f8f9fa;
                        color: #667eea;
                    }}
                    
                    .version-btn.active {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                    }}
                    
                    .version-btn:disabled {{
                        opacity: 0.4;
                        cursor: not-allowed;
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
                
                <div class="version-control-wrapper">
                    <div class="version-control">
                        <button class="version-btn{'  active' if default_version == 1 else ''}" data-version="1" {'disabled' if 1 not in available_versions else ''}>
                            Version 1
                        </button>
                        <button class="version-btn{' active' if default_version == 2 else ''}" data-version="2" {'disabled' if 2 not in available_versions else ''}>
                            Version 2
                        </button>
                        <button class="version-btn{' active' if default_version == 3 else ''}" data-version="3" {'disabled' if 3 not in available_versions else ''}>
                            Version 3
                        </button>
                    </div>
                </div>
                
                <div class="iframe-container">
                    <iframe 
                        id="website-frame"
                        src="/raw/{identifier}/{default_version}"
                        class="website-frame"
                        sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-top-navigation-by-user-activation"
                        loading="lazy"
                        title="Generated website for {identifier}">
                    </iframe>
                </div>
                
                <div class="security-notice">
                    🔒 Sandboxed Content
                </div>
                
                <script>
                    // Handle version switching
                    const versionButtons = document.querySelectorAll('.version-btn');
                    const iframe = document.getElementById('website-frame');
                    const identifier = '{identifier}';
                    
                    // Load version from URL hash on page load
                    function loadVersionFromHash() {{
                        const hash = window.location.hash.substring(1); // Remove #
                        if (hash.startsWith('v')) {{
                            const versionNum = parseInt(hash.substring(1));
                            if (versionNum >= 1 && versionNum <= 3) {{
                                switchToVersion(versionNum);
                            }}
                        }}
                    }}
                    
                    function switchToVersion(versionNum) {{
                        // Update iframe src
                        iframe.src = `/raw/${{identifier}}/${{versionNum}}`;
                        
                        // Update button states
                        versionButtons.forEach(btn => {{
                            const btnVersion = parseInt(btn.dataset.version);
                            if (btnVersion === versionNum) {{
                                btn.classList.add('active');
                            }} else {{
                                btn.classList.remove('active');
                            }}
                        }});
                        
                        // Update URL hash without reloading
                        window.location.hash = `v${{versionNum}}`;
                    }}
                    
                    // Add click handlers to version buttons
                    versionButtons.forEach(button => {{
                        button.addEventListener('click', () => {{
                            if (button.disabled) return;
                            const version = parseInt(button.dataset.version);
                            switchToVersion(version);
                        }});
                    }});
                    
                    // Load version from hash on initial load
                    window.addEventListener('DOMContentLoaded', loadVersionFromHash);
                    
                    // Handle hash changes (browser back/forward)
                    window.addEventListener('hashchange', loadVersionFromHash);
                </script>
            </body>
            </html>
            """,
            headers={
                "X-Frame-Options": "DENY",
                "Content-Security-Policy": "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-src 'self';",
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
            gap: 20px;
        }
        
        /* Collapsed header is fully clickable */
        .website-item:not(.expanded) .website-header {
            cursor: pointer;
        }
        
        /* Expanded header is not clickable (buttons handle their own clicks) */
        .website-item.expanded .website-header {
            cursor: default;
        }
        
        .website-header-left {
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 0 0 auto;
        }
        
        .website-header-center {
            display: flex;
            align-items: center;
            justify-content: center;
            flex: 1;
        }
        
        .website-header-right {
            display: flex;
            align-items: center;
            gap: 10px;
            flex: 0 0 auto;
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
            transition: none; /* No fade when switching versions */
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
        
        /* Version control styles for list view */
        .version-control-list {
            display: flex;
            justify-content: center;
            gap: 0;
        }
        
        /* Version control in header (no extra padding/border) */
        .website-header-center .version-control-list {
            margin: 0;
            padding: 0;
            border: none;
        }
        
        .version-control-list .version-control {
            display: flex;
            gap: 0;
            background: white;
            border-radius: 6px;
            padding: 3px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid #e1e5e9;
        }
        
        .version-control-list .version-btn {
            padding: 8px 15px;
            border: none;
            background: transparent;
            color: #495057;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            border-radius: 6px;
        }
        
        .version-control-list .version-btn:hover:not(:disabled) {
            background: #f8f9fa;
            color: #667eea;
        }
        
        .version-control-list .version-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        
        .version-control-list .version-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
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
        
        @media (max-width: 768px) {
            .website-header {
                flex-wrap: wrap;
            }
            
            .website-header-center {
                order: 3;
                flex-basis: 100%;
                margin-top: 10px;
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
            
            .version-control-list .version-btn {
                padding: 7px 12px;
                font-size: 0.85rem;
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
            item.dataset.activeVersion = website.default_version || 1; // Store active version
            
            const availableVersions = website.available_versions || [];
            const defaultVersion = website.default_version || 1;
            
            // Generate version control buttons HTML for header
            const versionControlHTML = website.has_generated_html ? `
                <div class="version-control-list">
                    <div class="version-control">
                        <button class="version-btn${defaultVersion === 1 ? ' active' : ''}" 
                                data-version="1" 
                                data-identifier="${website.identifier}"
                                ${availableVersions.includes(1) ? '' : 'disabled'}
                                onclick="switchVersion('${website.identifier}', 1, event)">
                            Version 1
                        </button>
                        <button class="version-btn${defaultVersion === 2 ? ' active' : ''}" 
                                data-version="2" 
                                data-identifier="${website.identifier}"
                                ${availableVersions.includes(2) ? '' : 'disabled'}
                                onclick="switchVersion('${website.identifier}', 2, event)">
                            Version 2
                        </button>
                        <button class="version-btn${defaultVersion === 3 ? ' active' : ''}" 
                                data-version="3" 
                                data-identifier="${website.identifier}"
                                ${availableVersions.includes(3) ? '' : 'disabled'}
                                onclick="switchVersion('${website.identifier}', 3, event)">
                            Version 3
                        </button>
                    </div>
                </div>
            ` : '';
            
            item.innerHTML = `
                <div class="website-header" onclick="handleHeaderClick('${website.identifier}', event)">
                    <div class="website-header-left">
                        <span class="website-name">${website.identifier}</span>
                    </div>
                    <div class="website-header-center website-btn-expanded-only">
                        ${versionControlHTML}
                    </div>
                    <div class="website-header-right">
                        <a href="${website.original_url}" target="_blank" class="view-website-btn secondary website-btn-expanded-only" onclick="event.stopPropagation()">
                            View Original
                        </a>
                        <span class="expand-arrow" onclick="toggleWebsiteItem('${website.identifier}'); event.stopPropagation();">▼</span>
                    </div>
                </div>
                <div class="website-content">
                    ${website.has_generated_html ? `
                        <div class="website-preview" onclick="openWebsiteWithVersion('${website.identifier}')" style="cursor: pointer;">
                            <iframe 
                                id="iframe-${website.identifier}"
                                src="/raw/${website.identifier}/${defaultVersion}"
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
        
        // Switch version in list preview
        function switchVersion(identifier, version, event) {
            event.stopPropagation(); // Prevent triggering collapse/expand
            
            const iframe = document.getElementById(`iframe-${identifier}`);
            if (iframe) {
                // Switch immediately without fade
                iframe.style.opacity = '1';
                iframe.src = `/raw/${identifier}/${version}`;
            }
            
            // Update button states and store active version
            const item = document.querySelector(`[data-identifier="${identifier}"]`);
            if (item) {
                // Store the active version in the data attribute
                item.dataset.activeVersion = version;
                
                const buttons = item.querySelectorAll('.version-btn');
                buttons.forEach(btn => {
                    const btnVersion = parseInt(btn.dataset.version);
                    if (btnVersion === version) {
                        btn.classList.add('active');
                    } else {
                        btn.classList.remove('active');
                    }
                });
            }
        }

        // Open website in new tab with the currently active version
        function openWebsiteWithVersion(identifier) {
            const item = document.querySelector(`[data-identifier="${identifier}"]`);
            const activeVersion = item ? item.dataset.activeVersion : 1;
            window.open(`/website/${identifier}#v${activeVersion}`, '_blank');
        }

        // Handle header click - entire header is clickable when collapsed
        function handleHeaderClick(identifier, event) {
            const clickedItem = document.querySelector(`[data-identifier="${identifier}"]`);
            if (!clickedItem) return;
            
            const isExpanded = clickedItem.classList.contains('expanded');
            
            // If expanded, only toggle when clicking the arrow area, not buttons/links
            if (isExpanded) {
                // Check if click was on a button or link (which have stopPropagation)
                // If we get here and it's expanded, it means they clicked non-interactive area
                // Don't do anything - let buttons handle their own clicks
                return;
            }
            
            // If collapsed, entire header is clickable - expand it
            toggleWebsiteItem(identifier);
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
            generateBtn.innerHTML = '<span class="spinner"></span>Building modern website, this will take a minute or two';
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
