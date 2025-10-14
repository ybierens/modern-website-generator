"""
Utility functions for the Website Generator.

This module contains helper functions for URL processing, identifier extraction,
web scraping, and GPT-based HTML generation.
"""

import re
import hashlib
from urllib.parse import urlparse
from typing import Dict, Any, Tuple
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os


def extract_identifier(url: str) -> str:
    """
    Extract a meaningful identifier from a URL.
    
    Args:
        url: The URL to extract identifier from
        
    Returns:
        A clean identifier suitable for use in URLs
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove common prefixes
        domain = re.sub(r'^www\.', '', domain)
        
        # Extract main part before TLD
        parts = domain.split('.')
        if len(parts) >= 2:
            # Take the main domain name
            identifier = parts[-2]  # Second to last part (before .com, .org, etc.)
        else:
            identifier = parts[0]
        
        # Clean the identifier
        identifier = re.sub(r'[^a-zA-Z0-9]', '', identifier)
        
        # Ensure it's not empty and has reasonable length
        if not identifier or len(identifier) < 2:
            # Fallback to hash of the full URL
            identifier = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # Limit length
        if len(identifier) > 50:
            identifier = identifier[:50]
            
        return identifier.lower()
        
    except Exception as e:
        print(f"⚠️ Error extracting identifier from {url}: {e}")
        # Fallback to hash
        return hashlib.md5(url.encode()).hexdigest()[:8]


def ensure_unique_identifier(base_identifier: str, existing_check_func) -> str:
    """
    Ensure identifier is unique by appending numbers if needed.
    
    Args:
        base_identifier: The base identifier to check
        existing_check_func: Async function to check if identifier exists
        
    Returns:
        A unique identifier
    """
    import asyncio
    
    async def _check_unique():
        identifier = base_identifier
        counter = 1
        
        while await existing_check_func(identifier):
            identifier = f"{base_identifier}{counter}"
            counter += 1
            
            # Prevent infinite loops
            if counter > 1000:
                identifier = f"{base_identifier}{hashlib.md5(str(counter).encode()).hexdigest()[:4]}"
                break
                
        return identifier
    
    # For synchronous usage, we'll return the base and let caller handle uniqueness
    return base_identifier


def scrape_website(url: str) -> Dict[str, Any]:
    """
    Scrape content from a website.
    
    Args:
        url: The URL to scrape
        
    Returns:
        Dictionary with title, content, meta_description, and original HTML
    """
    try:
        print(f"🌐 Scraping content from: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Store original HTML
        original_html = response.text
        
        soup = BeautifulSoup(original_html, 'html.parser')
        
        # Extract title
        title_elem = soup.find('title')
        title = title_elem.text.strip() if title_elem else "Untitled Page"
        
        # Remove script and style elements for content extraction
        content_soup = BeautifulSoup(original_html, 'html.parser')
        for element in content_soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Extract main content
        content_selectors = ['main', 'article', '.content', '#content', '.main-content', 'body']
        content_element = None
        
        for selector in content_selectors:
            content_element = content_soup.select_one(selector)
            if content_element:
                break
        
        if not content_element:
            content_element = content_soup
        
        # Get text content
        content = content_element.get_text()
        
        # Clean up the content
        lines = (line.strip() for line in content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Truncate if too long (for GPT processing)
        max_length = 3000
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc.get('content', '') if meta_desc else ""
        
        return {
            'title': title,
            'content': content,
            'meta_description': meta_description,
            'original_html': original_html,
            'url': url
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping website: {e}")
        raise Exception(f"Failed to scrape website: {str(e)}")
    except Exception as e:
        print(f"❌ Error parsing content: {e}")
        raise Exception(f"Failed to parse website content: {str(e)}")


def generate_optimized_html(scraped_data: Dict[str, Any]) -> str:
    """
    Generate optimized HTML using OpenAI GPT.
    
    Args:
        scraped_data: Dictionary containing scraped website data
        
    Returns:
        Generated HTML string
    """
    try:
        print("🤖 Generating optimized HTML with GPT...")
        
        # Setup OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY not found in environment variables")
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
Create a complete, modern, responsive HTML document based on this website content:

Original Website: {scraped_data['title']} ({scraped_data['url']})
Meta Description: {scraped_data.get('meta_description', '')}

Content to redesign and optimize:
{scraped_data['content'][:2500]}

Requirements:
- Generate a COMPLETE HTML document with inline CSS and JavaScript
- Make it modern, beautiful, and responsive (mobile-first design)
- Use CSS Grid/Flexbox for layout
- Include smooth animations and transitions
- Use a professional color scheme with good contrast
- Add hover effects and micro-interactions
- Ensure accessibility (proper semantic HTML, alt attributes, ARIA labels)
- Include proper meta tags for SEO
- Make it work perfectly as a standalone HTML file
- Use modern web design trends (clean design, good typography, whitespace)
- Transform the original content into an engaging, visual experience
- Include a hero section with the main message
- Organize content in logical sections
- Add a subtle background pattern or gradient

Generate ONLY the complete HTML code - nothing else. Start with <!DOCTYPE html> and end with </html>.
Make sure all CSS and JavaScript is inline within the HTML document.
"""

        # Try different models with fallbacks
        models_to_try = ["gpt-4o", "gpt-4-turbo", "gpt-4"]
        
        html_content = ""
        model_used = ""
        
        for model in models_to_try:
            try:
                print(f"🔍 Trying model: {model}")
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert frontend developer who creates beautiful, complete HTML documents with inline CSS and JavaScript. Always respond with only HTML code, no explanations or markdown formatting."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.7
                )
                
                html_content = response.choices[0].message.content.strip()
                model_used = model
                print(f"✅ {model} generated {len(html_content)} characters of HTML!")
                
                # Validate that we got substantial content
                if len(html_content) > 200 and "<!DOCTYPE html>" in html_content:
                    break
                else:
                    print(f"⚠️ {model} returned minimal/invalid content, trying next model...")
                    
            except Exception as e:
                print(f"❌ {model} failed: {e}")
                continue
        
        if not html_content or len(html_content) < 200:
            print("❌ All models failed, generating fallback HTML")
            return generate_fallback_html(scraped_data)
        
        # Clean up any markdown formatting if present
        html_content = html_content.strip()
        if html_content.startswith('```html'):
            html_content = html_content[7:]
        if html_content.startswith('```'):
            html_content = html_content[3:]
        if html_content.endswith('```'):
            html_content = html_content[:-3]
        
        print(f"🎉 Successfully used {model_used} to generate HTML!")
        return html_content.strip()
        
    except Exception as e:
        print(f"❌ Error generating HTML with GPT: {e}")
        return generate_fallback_html(scraped_data)


def generate_fallback_html(scraped_data: Dict[str, Any]) -> str:
    """
    Generate a simple fallback HTML when GPT generation fails.
    
    Args:
        scraped_data: Dictionary containing scraped website data
        
    Returns:
        Fallback HTML string
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{scraped_data['title']} - Optimized</title>
    <meta name="description" content="{scraped_data.get('meta_description', '')[:160]}">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 80px 20px;
            text-align: center;
            margin-bottom: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .hero h1 {{
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .hero p {{
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }}
        
        .content {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .content h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 2rem;
        }}
        
        .content p {{
            font-size: 1.1rem;
            line-height: 1.8;
            color: #555;
            margin-bottom: 20px;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            .hero {{
                padding: 60px 20px;
            }}
            
            .content {{
                padding: 30px 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>{scraped_data['title']}</h1>
            <p>Optimized and modernized website experience</p>
        </div>
        
        <div class="content">
            <h2>Content</h2>
            <p>{scraped_data['content'][:1500]}{'...' if len(scraped_data['content']) > 1500 else ''}</p>
        </div>
        
        <div class="footer">
            <p>Generated by Website Generator • Original: <a href="{scraped_data['url']}" target="_blank" style="color: #667eea;">{scraped_data['url']}</a></p>
        </div>
    </div>
</body>
</html>"""
