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
import json


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


def select_template_for_website(scraped_data: Dict[str, Any]) -> str:
    """
    Use LLM to analyze scraped website and select the best template.
    
    Args:
        scraped_data: Dictionary containing scraped website data
        
    Returns:
        Template ID identifier (e.g., 'restaurant')
    """
    from .website_generator_templates import get_template_metadata, get_template_ids
    
    try:
        print("🤔 Analyzing website to select best template...")
        
        # Setup OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY not found in environment variables")
        
        client = OpenAI(api_key=api_key)
        
        # Get template metadata for selection
        template_metadata = get_template_metadata()
        available_ids = get_template_ids()
        
        # Build template options for the prompt
        template_options = []
        for template_id, metadata in template_metadata.items():
            template_options.append(
                f"- {template_id}: {metadata['name']}\n"
                f"  {metadata['description']}"
            )
        
        prompt = f"""Analyze this website and determine which template type would be most appropriate.

WEBSITE DATA:
Title: {scraped_data.get('title', 'N/A')}
URL: {scraped_data.get('url', 'N/A')}
Meta Description: {scraped_data.get('meta_description', 'N/A')}
Content Preview: {scraped_data.get('content', '')[:1500]}

AVAILABLE TEMPLATES:
{chr(10).join(template_options)}

Based on the website's content, purpose, and industry, select the SINGLE most appropriate template.

Respond with ONLY a JSON object in this exact format:
{{"template_id": "template_name"}}

Where template_name is one of: {', '.join(available_ids)}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper/faster model for selection
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing websites and categorizing them. You respond with only valid JSON containing the template_id that best matches the website."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=100,
            temperature=0.3  # Lower temperature for more consistent selection
        )
        
        # Parse JSON response
        response_text = response.choices[0].message.content.strip()
        response_data = json.loads(response_text)
        selected_template = response_data.get("template_id", "").strip().lower()
        
        # Validate selection
        if selected_template not in available_ids:
            print(f"⚠️ Invalid template selection '{selected_template}', defaulting to 'restaurant'")
            selected_template = "restaurant"
        
        print(f"✅ Selected template: {selected_template}")
        return selected_template
        
    except Exception as e:
        print(f"❌ Error selecting template: {e}")
        return "restaurant"  # Safe default fallback


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
            
            # Convert to Cloudinary URL (let Cloudinary handle broken URLs)
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


def generate_optimized_html(scraped_data: Dict[str, Any], template_id: str = "restaurant") -> str:
    """
    Generate optimized HTML using OpenAI GPT with selected template guidance.
    
    Args:
        scraped_data: Dictionary containing scraped website data
        template_id: The template identifier to use for generation (default: "restaurant")
        
    Returns:
        Generated HTML string following selected template specifications
    """
    from .website_generator_templates import get_template_content, template_exists
    
    try:
        print(f"🤖 Generating HTML with GPT using '{template_id}' template...")
        
        # Validate template exists
        if not template_exists(template_id):
            print(f"⚠️ Template '{template_id}' not found, falling back to 'restaurant'")
            template_id = "restaurant"
        
        # Setup OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY not found in environment variables")
        
        client = OpenAI(api_key=api_key)
        
        # Get template content for selected template
        template_content = get_template_content(template_id)
        
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

=== AVAILABLE IMAGES (USE THESE EXACT URLs) ===
{chr(10).join(image_list)}

"""

        # Build comprehensive template-guided prompt
        prompt = f"""{template_content}

=== BUSINESS DATA TO CUSTOMIZE ===

Business Name: {scraped_data['title']}
Original Website: {scraped_data['url']}
Meta Description: {scraped_data.get('meta_description', 'Professional business with quality service')}{image_info}

Content to integrate with template:
{scraped_data['content'][:2500]}

=== GENERATION INSTRUCTIONS ===

You must create a complete, professional website that EXACTLY follows the template specification above while customizing all content for this specific business.

CRITICAL REQUIREMENTS:
1. Follow the template architecture precisely - every layout specification must be implemented
2. Use the business's actual data to populate all content sections
3. Implement the exact visual design system specified (typography, colors, spacing, components)
4. Include all accessibility and SEO requirements as detailed
5. Generate ONLY the complete HTML code - no explanations or markdown formatting
6. Start with <!DOCTYPE html> and end with </html>
7. Make all CSS and JavaScript inline within the HTML document

OUTPUT FORMAT REQUIREMENTS:
- Output ONLY raw HTML code - absolutely NO markdown code blocks, NO explanations, NO ``` markers
- Start immediately with <!DOCTYPE html> - no preamble, no commentary
- End with </html> - nothing after it
- Ensure the HTML is properly formatted and indented for readability
- Include ALL functionality inline (CSS and JavaScript within the HTML)

The result must be a beautiful, professional website that matches the template's quality while showcasing this business's unique content and branding. The website should look polished, modern, and ready for production use.
"""

        # Use GPT-5.1 with Responses API for high-quality code generation
        print(f"🤖 Generating HTML with GPT-5.1 (high reasoning)...")
        
        # System prompt for expert frontend developer
        system_prompt = "You are an expert frontend developer specializing in creating beautiful, modern, production-ready HTML documents using Tailwind CSS. You excel at implementing professional templates with Tailwind utility classes and inline JavaScript. You are a master of Tailwind's utility-first approach and use it for ALL styling (layout, colors, typography, spacing, responsive design, hover states, transitions). You ALWAYS output only raw HTML code - no markdown, no code blocks, no explanations. Your HTML is clean, semantic, accessible, visually stunning, and leverages Tailwind CSS via CDN for all styling needs."
        
        # Combine system prompt and user prompt into input
        full_input = f"{system_prompt}\n\n{prompt}"
        
        # Log the exact prompt being sent
        print("📝 OpenAI Prompt Input:")
        print("=" * 80)
        print(full_input[:1000] + ("..." if len(full_input) > 1000 else ""))
        print("=" * 80)
        
        # Call GPT-5.1 using Responses API
        response = client.responses.create(
            model="gpt-5.1",
            input=full_input,
            reasoning={"effort": "high"},  # High reasoning for complex code generation
            text={"verbosity": "high"},    # High verbosity for complete HTML
            max_output_tokens=16000        # Increased for larger HTML files
        )
        
        html_content = response.output_text.strip()
        model_used = "gpt-5.1"
        
        # Log the exact response content from OpenAI
        print(f"📥 OpenAI Response Output from gpt-5.1:")
        print("=" * 80)
        print(html_content[:1000] + ("..." if len(html_content) > 1000 else ""))
        print("=" * 80)
        print(f"✅ gpt-5.1 generated {len(html_content)} characters of HTML!")
        
        # Validate that we got substantial content
        if not html_content or len(html_content) < 200 or "<!DOCTYPE html>" not in html_content:
            print("❌ GPT-5.1 returned invalid content, generating fallback HTML")
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
