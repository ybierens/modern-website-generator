"""
Utility functions for the Website Generator.

This module contains helper functions for URL processing, identifier extraction,
web scraping, and GPT-based HTML generation.
"""

import re
import hashlib
from urllib.parse import urlparse, urljoin
from typing import Dict, Any, Tuple, List
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
        
        # Extract images
        images = extract_images_from_html(original_html, url)
        
        return {
            'title': title,
            'content': content,
            'meta_description': meta_description,
            'original_html': original_html,
            'images': images,
            'url': url
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping website: {e}")
        raise Exception(f"Failed to scrape website: {str(e)}")
    except Exception as e:
        print(f"❌ Error parsing content: {e}")
        raise Exception(f"Failed to parse website content: {str(e)}")


def extract_images_from_html(html: str, base_url: str) -> List[Dict[str, str]]:
    """
    Extract image URLs and metadata from HTML content.
    Captures regular img tags, lazy-loaded images, CSS background images, and SVGs.
    
    Args:
        html: The HTML content to parse
        base_url: The base URL for converting relative URLs
        
    Returns:
        List of dictionaries containing image data
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        images = []
        seen_urls = set()  # Prevent duplicates
        
        def normalize_url(url):
            """Convert relative URLs to absolute URLs."""
            if not url or url.startswith('data:'):
                return None
                
            # Convert relative URLs to absolute
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                parsed_base = urlparse(base_url)
                url = f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
            elif not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url)
            
            return url
        
        def add_image(src, alt='', title='', source='img'):
            """Add an image to the list if it's valid and not duplicate."""
            if not src:
                return
                
            normalized_src = normalize_url(src)
            if not normalized_src or normalized_src in seen_urls:
                return
                
            # Skip very small images likely to be tracking pixels or tiny icons
            if 'pixel' in normalized_src.lower() or '1x1' in normalized_src.lower():
                return
                
            seen_urls.add(normalized_src)
            images.append({
                'src': normalized_src,
                'alt': alt,
                'title': title,
                'width': '',
                'height': '',
                'source': source  # Track where we found it
            })
        
        # 1. Find all img tags with src attribute
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src')
            if src:
                add_image(src, img.get('alt', ''), img.get('title', ''), 'img-src')
        
        # 2. Find lazy-loaded images with data-src attributes
        lazy_imgs = soup.find_all(attrs={'data-src': True})
        for img in lazy_imgs:
            data_src = img.get('data-src')
            if data_src:
                add_image(data_src, img.get('alt', ''), img.get('title', ''), 'data-src')
        
        # 3. Find other common lazy loading attributes
        for attr in ['data-lazy-src', 'data-original', 'data-bg']:
            lazy_elements = soup.find_all(attrs={attr: True})
            for element in lazy_elements:
                lazy_src = element.get(attr)
                if lazy_src:
                    add_image(lazy_src, element.get('alt', ''), element.get('title', ''), attr)
        
        # 4. Find CSS background images in style attributes
        style_elements = soup.find_all(attrs={'style': True})
        for element in style_elements:
            style = element.get('style', '')
            # Extract background-image URLs using regex
            import re
            bg_matches = re.findall(r'background-image:\s*url\(["\']?([^"\'()]+)["\']?\)', style, re.IGNORECASE)
            for bg_url in bg_matches:
                add_image(bg_url.strip(), '', '', 'css-background')
        
        # 5. Find srcset attributes (responsive images)
        srcset_elements = soup.find_all(attrs={'srcset': True})
        for element in srcset_elements:
            srcset = element.get('srcset', '')
            # Parse srcset: "url1 1x, url2 2x" or "url1 480w, url2 800w"
            srcset_urls = re.findall(r'([^\s,]+)(?:\s+[0-9.]+[wx])?', srcset)
            for srcset_url in srcset_urls:
                srcset_url = srcset_url.strip()
                if srcset_url and not srcset_url.startswith('data:'):
                    add_image(srcset_url, element.get('alt', ''), element.get('title', ''), 'srcset')
        
        # 6. Find picture elements with source tags
        picture_elements = soup.find_all('picture')
        for picture in picture_elements:
            sources = picture.find_all('source')
            for source in sources:
                if source.get('srcset'):
                    srcset_urls = re.findall(r'([^\s,]+)(?:\s+[0-9.]+[wx])?', source.get('srcset'))
                    for srcset_url in srcset_urls:
                        add_image(srcset_url.strip(), '', '', 'picture-source')
        
        # 7. Include SVG images (previously excluded)
        svg_imgs = soup.find_all('img', src=re.compile(r'\.svg', re.IGNORECASE))
        for svg in svg_imgs:
            src = svg.get('src')
            if src:
                add_image(src, svg.get('alt', ''), svg.get('title', ''), 'svg')
        
        print(f"🖼️ Extracted {len(images)} images from HTML ({len(seen_urls)} unique URLs)")
        
        # Debug: Show breakdown by source type
        source_counts = {}
        for img in images:
            source = img.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        if source_counts:
            breakdown = ', '.join([f"{count} {source}" for source, count in source_counts.items()])
            print(f"📊 Image sources: {breakdown}")
        
        return images
        
    except Exception as e:
        print(f"⚠️ Error extracting images: {e}")
        return []


def convert_to_cloudinary_url(original_url: str) -> str:
    """
    Convert an image URL to Cloudinary auto-fetch URL.
    
    Args:
        original_url: The original image URL
        
    Returns:
        Cloudinary auto-fetch URL or None if cloud name not configured
    """
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    if not cloud_name:
        print("⚠️ CLOUDINARY_CLOUD_NAME not configured")
        return None
        
    return f"https://res.cloudinary.com/{cloud_name}/image/fetch/{original_url}"


def test_url_accessibility(url: str) -> bool:
    """
    Test if an image URL is accessible.
    
    Args:
        url: The URL to test
        
    Returns:
        True if accessible, False otherwise
    """
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except Exception:
        return False


async def process_images(scraped_data: Dict[str, Any], website_id: str) -> Dict[str, Any]:
    """
    Process images by converting to Cloudinary URLs and updating HTML.
    
    Args:
        scraped_data: The scraped website data
        website_id: The website ID for database storage
        
    Returns:
        Updated scraped data with processed images and modified HTML
    """
    from .database import db
    
    try:
        images = scraped_data.get('images', [])
        if not images:
            print("📷 No images found to process")
            return scraped_data
        
        print(f"🔄 Processing {len(images)} images...")
        
        # Process each image
        processed_images = []
        url_mappings = {}
        
        for img_data in images:
            original_url = img_data['src']
            
            # Test if URL is accessible
            if not test_url_accessibility(original_url):
                print(f"⚠️ Skipping inaccessible image: {original_url}")
                continue
            
            # Convert to Cloudinary URL
            cloudinary_url = convert_to_cloudinary_url(original_url)
            if not cloudinary_url:
                print(f"⚠️ Could not create Cloudinary URL for: {original_url}")
                continue
            
            # Store mapping in database
            try:
                await db.create_image_mapping(
                    website_id=website_id,
                    original_url=original_url,
                    cloudinary_url=cloudinary_url,
                    alt_text=img_data.get('alt', '')
                )
                
                url_mappings[original_url] = cloudinary_url
                processed_images.append({
                    **img_data,
                    'cloudinary_url': cloudinary_url
                })
                
                print(f"✅ Processed image: {original_url} → Cloudinary")
                
            except Exception as e:
                print(f"❌ Error storing image mapping: {e}")
                continue
        
        # Replace URLs in HTML
        updated_html = scraped_data['original_html']
        for original_url, cloudinary_url in url_mappings.items():
            updated_html = updated_html.replace(original_url, cloudinary_url)
        
        # Update scraped data
        scraped_data['original_html'] = updated_html
        scraped_data['processed_images'] = processed_images
        scraped_data['image_mappings'] = url_mappings
        
        print(f"🎉 Successfully processed {len(processed_images)} images")
        return scraped_data
        
    except Exception as e:
        print(f"❌ Error processing images: {e}")
        return scraped_data


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
        
        # Prepare image information for the prompt
        image_info = ""
        if scraped_data.get('processed_images'):
            image_list = []
            for img in scraped_data['processed_images']:
                img_line = f"- {img.get('cloudinary_url', img['src'])}"
                if img.get('alt'):
                    img_line += f" (alt: {img['alt']})"
                image_list.append(img_line)
            image_info = f"""

Available Images (USE THESE EXACT URLs):
{chr(10).join(image_list)}"""

        prompt = f"""
Create a complete, modern, responsive HTML document based on this website content:

Original Website: {scraped_data['title']} ({scraped_data['url']})
Meta Description: {scraped_data.get('meta_description', '')}{image_info}

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

CONTENT PRESERVATION GUIDELINES:
- PRESERVE the core business messaging, value propositions, and key taglines from the original content
- MAINTAIN any strategic wording, calls-to-action, and marketing copy that the business has carefully chosen
- RESPECT the original brand voice and tone while modernizing the visual presentation
- Transform the design and layout to be engaging and modern, but keep the essential business messaging intact
- Include a hero section with the main message from the original content

IMAGE USAGE GUIDELINES:
- IMPORTANT: If images are provided above, use the EXACT URLs shown - they are already optimized and hosted
- ONLY use images where they contextually make sense for the content and support the business purpose
- Ensure each image adds value and relevance to the section where it's placed
- Do not use images purely for decoration if they don't relate to the business or content
- Consider the business context when positioning images within the layout

LAYOUT & ORGANIZATION:
- Organize content in logical sections that reflect the original business structure
- Add a subtle background pattern or gradient that complements the brand
- Maintain content hierarchy that supports the business goals

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
