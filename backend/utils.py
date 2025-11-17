"""
Utility functions for the Website Generator.

This module contains helper functions for URL processing, identifier extraction,
web scraping, and GPT-based HTML generation.
"""

import re
import hashlib
from urllib.parse import urlparse, urljoin
from typing import Dict, Any, Tuple, List, Optional
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


def generate_version_instructions(scraped_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Use GPT-5 thinking mode to generate 3 different creative directions for website generation.
    
    Args:
        scraped_data: Dictionary containing scraped website data
        
    Returns:
        Dictionary with version_1, version_2, version_3 instruction strings
    """
    try:
        print("🤔 Generating 3 creative directions with GPT-5 thinking mode...")
        
        # Setup OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY not found in environment variables")
        
        client = OpenAI(api_key=api_key)
        
        # Prepare image information
        image_info = ""
        if scraped_data.get('processed_images'):
            image_count = len(scraped_data['processed_images'])
            image_info = f"\n{image_count} images available for use in designs."
        
        # Build prompt for instruction generation
        prompt = f"""You are an expert web designer tasked with creating 3 different creative directions for redesigning a website.

ORIGINAL WEBSITE DATA:
Title: {scraped_data.get('title', 'N/A')}
URL: {scraped_data.get('url', 'N/A')}
Meta Description: {scraped_data.get('meta_description', 'N/A')}
Content Preview: {scraped_data.get('content', '')[:2000]}{image_info}

YOUR TASK:
Generate 3 distinct creative directions for redesigning this website. Each direction should be detailed enough to guide a developer in creating a professional, modern website using Tailwind CSS.

REQUIREMENTS FOR EACH VERSION:

Version 1 - "Faithful Optimization":
- Stay very close to the original website's style, brand, and personality
- Modernize the UI with better spacing, typography, and layout
- Improve user experience while maintaining familiar feel
- Optimize for responsiveness and accessibility
- Keep the same general color scheme and visual tone

Version 2 - "Visual Reimagining":
- Take creative freedom with visual style (colors, typography, design system)
- Choose a distinctly different aesthetic (modern, elegant, bold, minimalist, etc.)
- Maintain the core content and structure but with fresh visual treatment
- All designs should still look professional and polished
- Consider what visual style would best serve this business

Version 3 - "Layout Revolution":
- Take creative freedom with page layout and information architecture
- Reimagine how content is organized and presented
- Experiment with different section orders, grid systems, or layouts
- Could be single-page scroll, multi-section, card-based, etc.
- All layouts should be user-friendly and purposeful

CRITICAL REQUIREMENTS:
- All 3 versions must be professional, modern, and polished
- All must use Tailwind CSS for styling
- All must be fully responsive (mobile, tablet, desktop)
- All must preserve the core business information and content
- Each direction should be unique and distinguishable from the others

OUTPUT FORMAT - CRITICAL:
You MUST respond with ONLY a valid JSON object. No explanations, no markdown, no code blocks.
Just pure JSON starting with {{ and ending with }}.

Use this EXACT structure:
{{
  "version_1": "Your detailed instructions here...",
  "version_2": "Your detailed instructions here...",
  "version_3": "Your detailed instructions here..."
}}

IMPORTANT JSON RULES:
- Use double quotes for all strings
- Properly escape any quotes within the instruction text using backslash
- Each instruction should be 3-5 paragraphs in a single string
- No line breaks within JSON values - keep each instruction as one continuous string
- Make sure all curly braces and quotes are properly closed

Each instruction string should describe:
- Overall design approach and philosophy
- Key visual elements (colors, typography, spacing)
- Layout structure and organization
- Specific features or components to emphasize
- How it differs from the other versions

REMEMBER: Output ONLY the JSON object, nothing else."""

        # Use Chat Completions API with JSON mode for structured output
        # (Responses API doesn't support JSON mode - it's for open-ended text like HTML)
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Use gpt-4-turbo for best JSON mode support
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert web designer who creates detailed, actionable creative directions for website redesigns. You respond with only valid JSON containing three distinct design approaches."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},  # This ensures valid JSON output
            temperature=0.7,  # Some creativity
            max_tokens=4000
        )
        
        # Get response text from Chat Completions API
        response_text = response.choices[0].message.content.strip()
        
        # Log raw response for debugging
        print(f"📥 Raw response length: {len(response_text)} chars")
        print(f"📥 First 500 chars: {response_text[:500]}")
        
        # Clean up potential markdown or extra text
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        elif response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Find JSON object boundaries
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            raise Exception("No JSON object found in response")
        
        # Extract just the JSON part
        json_text = response_text[start_idx:end_idx + 1]
        
        # Parse JSON with better error handling
        try:
            instructions = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"📄 Attempted to parse: {json_text[:1000]}...")
            raise Exception(f"Failed to parse JSON from GPT response: {e}")
        
        # Validate that we got all 3 versions
        if not all(key in instructions for key in ['version_1', 'version_2', 'version_3']):
            missing_keys = [k for k in ['version_1', 'version_2', 'version_3'] if k not in instructions]
            raise Exception(f"GPT response missing required keys: {missing_keys}. Got keys: {list(instructions.keys())}")
        
        # Validate that values are strings and not empty
        for key in ['version_1', 'version_2', 'version_3']:
            if not isinstance(instructions[key], str) or len(instructions[key].strip()) < 50:
                raise Exception(f"{key} is invalid: too short or not a string")
        
        print(f"✅ Generated 3 creative directions successfully")
        print(f"   Version 1 length: {len(instructions['version_1'])} chars")
        print(f"   Version 2 length: {len(instructions['version_2'])} chars")
        print(f"   Version 3 length: {len(instructions['version_3'])} chars")
        
        return instructions
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR generating version instructions: {e}")
        print(f"❌ This should not happen - instruction generation failed completely")
        # Re-raise the error instead of using fallback - let the job fail
        raise


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


def generate_optimized_html(scraped_data: Dict[str, Any], instructions: str) -> str:
    """
    Generate optimized HTML using OpenAI GPT with creative direction instructions.
    
    Args:
        scraped_data: Dictionary containing scraped website data
        instructions: Creative direction and design instructions for this version
        
    Returns:
        Generated HTML string following the provided instructions
    """
    try:
        print(f"🤖 Generating HTML with GPT-5.1...")
        
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

=== AVAILABLE IMAGES (USE THESE EXACT URLs) ===
{chr(10).join(image_list)}

"""

        # Build comprehensive prompt with creative instructions
        prompt = f"""=== CREATIVE DIRECTION ===

{instructions}

=== BUSINESS DATA TO IMPLEMENT ===

Business Name: {scraped_data['title']}
Original Website: {scraped_data['url']}
Meta Description: {scraped_data.get('meta_description', 'Professional business with quality service')}{image_info}

Content to integrate:
{scraped_data['content'][:2500]}

=== TECHNICAL REQUIREMENTS ===

You must create a complete, professional website following the creative direction above.

CRITICAL REQUIREMENTS:
1. Follow the creative direction precisely - implement the specified design philosophy and visual style
2. Use the business's actual data to populate all content sections
3. Use Tailwind CSS (via CDN) for ALL styling - no custom CSS unless absolutely necessary
4. Include proper semantic HTML5 structure (header, nav, main, section, footer)
5. Implement responsive design for mobile, tablet, and desktop
6. Generate ONLY the complete HTML code - no explanations or markdown formatting
7. Start with <!DOCTYPE html> and end with </html>
8. Make all JavaScript inline within the HTML document

OUTPUT FORMAT REQUIREMENTS:
- Output ONLY raw HTML code - absolutely NO markdown code blocks, NO explanations, NO ``` markers
- Start immediately with <!DOCTYPE html> - no preamble, no commentary
- End with </html> - nothing after it
- Ensure the HTML is properly formatted and indented for readability
- Include Tailwind CSS CDN in the head: <script src="https://cdn.tailwindcss.com"></script>
- Use Tailwind utility classes for all styling (colors, spacing, typography, layout, etc.)

The result must be a beautiful, professional website that perfectly executes the creative direction while showcasing this business's content. The website should look polished, modern, and ready for production use.
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


async def generate_three_versions_parallel(scraped_data: Dict[str, Any], instructions_dict: Dict[str, str]) -> Dict[str, Optional[str]]:
    """
    Generate 3 HTML versions in parallel using asyncio.
    
    Args:
        scraped_data: Dictionary containing scraped website data
        instructions_dict: Dictionary with version_1, version_2, version_3 instruction strings
        
    Returns:
        Dictionary with version_1, version_2, version_3 HTML strings (or None if generation failed)
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    print("🚀 Starting parallel generation of 3 website versions...")
    
    # Define async wrapper for the synchronous generate_optimized_html function
    async def generate_version(version_name: str, instructions: str):
        """Generate a single version asynchronously."""
        try:
            print(f"   Starting {version_name}...")
            
            # Run the synchronous function in a thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                html = await loop.run_in_executor(
                    executor,
                    generate_optimized_html,
                    scraped_data,
                    instructions
                )
            
            print(f"   ✅ {version_name} completed ({len(html)} chars)")
            return html
            
        except Exception as e:
            print(f"   ❌ {version_name} failed: {str(e)}")
            return None
    
    # Create tasks for all 3 versions
    tasks = [
        generate_version("Version 1", instructions_dict.get('version_1', '')),
        generate_version("Version 2", instructions_dict.get('version_2', '')),
        generate_version("Version 3", instructions_dict.get('version_3', ''))
    ]
    
    # Execute all 3 generations in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results and handle exceptions
    version_htmls = {
        'version_1': results[0] if not isinstance(results[0], Exception) else None,
        'version_2': results[1] if not isinstance(results[1], Exception) else None,
        'version_3': results[2] if not isinstance(results[2], Exception) else None
    }
    
    # Count successes
    success_count = sum(1 for html in version_htmls.values() if html is not None)
    print(f"🎉 Parallel generation complete: {success_count}/3 versions succeeded")
    
    if success_count == 0:
        raise Exception("All 3 versions failed to generate")
    
    return version_htmls


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
