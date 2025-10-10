#!/usr/bin/env python3
"""
Website Scraper and Frontend Optimizer
=====================================

This script scrapes a hardcoded URL and uses OpenAI's GPT-5 to generate 
an optimized HTML frontend that can be copy-pasted into CodePen.

Usage:
    python website_optimizer.py

Requirements:
    - OpenAI API key in .env file
    - Internet connection
    - Required packages: requests, beautifulsoup4, openai, python-dotenv
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configuration
HARDCODED_URL = "https://www.wohop17.com/"  # Change this to your target URL
MAX_CONTENT_LENGTH = 3000  # Limit content to avoid token limits

def setup_openai_client():
    """Initialize OpenAI client with API key from environment."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please:")
        print("1. Copy env.template to .env")
        print("2. Add your OpenAI API key to the .env file")
        sys.exit(1)
    
    return OpenAI(api_key=api_key)

def scrape_website(url):
    """
    Scrape content from the given URL.
    
    Args:
        url (str): The URL to scrape
        
    Returns:
        dict: Contains 'title', 'content', and 'meta' information
    """
    try:
        print(f"🌐 Scraping content from: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title = title.text.strip() if title else "Untitled Page"
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract main content
        content_selectors = ['main', 'article', '.content', '#content', 'body']
        content_element = None
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break
        
        if not content_element:
            content_element = soup
        
        # Get text content
        content = content_element.get_text()
        
        # Clean up the content
        lines = (line.strip() for line in content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Truncate if too long
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + "..."
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc['content'] if meta_desc else ""
        
        return {
            'title': title,
            'content': content,
            'meta_description': meta_description,
            'url': url
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping website: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error parsing content: {e}")
        sys.exit(1)

def generate_optimized_html(client, scraped_data):
    """
    Use GPT-5 to generate a complete HTML document with inline CSS and JS.
    
    Args:
        client: OpenAI client instance
        scraped_data (dict): Scraped website data
        
    Returns:
        str: Complete HTML document
    """
    try:
        print("🤖 Generating complete HTML with GPT-5...")
        
        prompt = f"""
Create a complete, modern, responsive HTML document based on this website content:

Original Website: {scraped_data['title']} ({scraped_data['url']})
Meta Description: {scraped_data['meta_description']}

Content to redesign and optimize:
{scraped_data['content'][:2000]}...

Requirements:
- Generate a COMPLETE HTML document with inline CSS and JavaScript
- Make it modern, beautiful, and responsive
- Use CSS Grid/Flexbox for layout
- Include smooth animations and transitions
- Use a professional color scheme
- Add hover effects and micro-interactions
- Ensure it works perfectly when copy-pasted into CodePen
- Include proper semantic HTML structure
- Make it mobile-friendly
- Use modern web design trends (glassmorphism, gradients, shadows)
- Transform the original content into an engaging, visual experience

Generate ONLY the complete HTML code - nothing else. Start with <!DOCTYPE html> and end with </html>.
"""

        print(f"🔍 Sending request to GPT-5...")
        
        # Test with available models - try GPT-5 first, fallback to GPT-4o
        models_to_try = ["gpt-5", "gpt-4o", "gpt-4-turbo"]
        
        html_content = ""
        model_used = ""
        
        for model in models_to_try:
            try:
                print(f"🔍 Trying model: {model}")
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert frontend developer who creates beautiful, complete HTML documents with inline CSS and JavaScript. Always respond with only HTML code, no explanations."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=4000
                )
                
                html_content = response.choices[0].message.content.strip()
                model_used = model
                print(f"✅ {model} generated {len(html_content)} characters of HTML!")
                
                if len(html_content) > 100:  # If we got substantial content, use it
                    break
                else:
                    print(f"⚠️ {model} returned minimal content, trying next model...")
                    
            except Exception as e:
                print(f"❌ {model} failed: {e}")
                continue
        
        if not html_content:
            print("❌ All models failed, using fallback")
            raise Exception("No models returned valid HTML")
        
        # Clean up any markdown formatting if present
        if html_content.startswith('```html'):
            html_content = html_content[7:]
        if html_content.startswith('```'):
            html_content = html_content[3:]
        if html_content.endswith('```'):
            html_content = html_content[:-3]
        
        print(f"🎉 Successfully used {model_used} to generate HTML!")
        return html_content.strip()
        
    except Exception as e:
        print(f"❌ Error generating HTML: {e}")
        # Simple fallback HTML
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{scraped_data['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #333; }}
        h1 {{ color: #2c3e50; }}
        .content {{ max-width: 800px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="content">
        <h1>{scraped_data['title']}</h1>
        <p>{scraped_data['content'][:500]}...</p>
        <p><em>Error occurred during optimization. This is a fallback version.</em></p>
    </div>
</body>
</html>"""

def build_html_from_structure(website_data):
    """
    Build complete HTML document from structured website data.
    
    Args:
        website_data (dict): Structured website data from GPT-5 function call
        
    Returns:
        str: Complete HTML document
    """
    try:
        colors = website_data['color_scheme']
        hero = website_data['hero_section']
        features = website_data.get('features', [])
        
        # Generate CSS based on layout style and features
        animations_css = ""
        if "animations" in features:
            animations_css = """
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-20px); }
            }
            .animate-fadein { animation: fadeInUp 0.8s ease-out; }
            .animate-float { animation: float 3s ease-in-out infinite; }
            """
        
        hover_effects_css = ""
        if "hover-effects" in features:
            hover_effects_css = """
            .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
            .card:hover { transform: translateY(-5px); box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
            """
        
        glassmorphism_css = ""
        if "glassmorphism" in features:
            glassmorphism_css = """
            .glass { 
                background: rgba(255,255,255,0.1); 
                backdrop-filter: blur(10px); 
                border: 1px solid rgba(255,255,255,0.2); 
            }
            """
        
        # Build main content sections
        content_sections = ""
        for section in website_data['main_content']:
            content_sections += f"""
            <section class="content-section animate-fadein">
                <div class="container">
                    <h2>{section['section_title']}</h2>
                    <div class="section-content">
                        {section['content']}
                    </div>
                </div>
            </section>
            """
        
        # Complete HTML template
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{website_data['page_title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary: {colors['primary']};
            --secondary: {colors['secondary']};
            --accent: {colors['accent']};
            --text: {colors['text']};
            --background: {colors['background']};
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--background);
            overflow-x: hidden;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        /* Hero Section */
        .hero {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            position: relative;
        }}
        
        .hero-content {{
            z-index: 2;
            color: white;
        }}
        
        .hero h1 {{
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .hero p {{
            font-size: clamp(1.1rem, 2vw, 1.3rem);
            margin-bottom: 2rem;
            opacity: 0.9;
        }}
        
        .btn {{
            display: inline-block;
            padding: 15px 30px;
            background: var(--accent);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        
        /* Content Sections */
        .content-section {{
            padding: 80px 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        }}
        
        .content-section:nth-child(even) {{
            background: rgba(0,0,0,0.02);
        }}
        
        .content-section h2 {{
            font-size: clamp(2rem, 4vw, 3rem);
            margin-bottom: 2rem;
            text-align: center;
            color: var(--primary);
        }}
        
        .section-content {{
            font-size: 1.1rem;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .card {{
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin: 2rem 0;
            transition: all 0.3s ease;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .hero {{
                padding: 2rem 0;
            }}
            
            .content-section {{
                padding: 60px 0;
            }}
            
            .container {{
                padding: 0 15px;
            }}
        }}
        
        {animations_css}
        {hover_effects_css}
        {glassmorphism_css}
    </style>
</head>
<body>
    <section class="hero">
        <div class="hero-content animate-fadein">
            <h1 class="animate-float">{hero['headline']}</h1>
            <p>{hero['subheadline']}</p>
            <a href="#content" class="btn">{hero['cta_text']}</a>
        </div>
    </section>
    
    <main id="content">
        {content_sections}
    </main>
    
    <script>
        // Intersection Observer for animations
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('animate-fadein');
                }}
            }});
        }});
        
        document.querySelectorAll('.content-section').forEach(section => {{
            observer.observe(section);
        }});
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});
    </script>
</body>
</html>"""
        
        return html_template
        
    except Exception as e:
        print(f"❌ Error building HTML structure: {e}")
        return f"<html><body><h1>Error building HTML: {e}</h1></body></html>"

def generate_simple_html(scraped_data, content):
    """
    Fallback function to generate simple HTML when function calling fails.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{scraped_data['title']} - Optimized</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6; color: #333; background: #f8f9fa;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 80px 0; text-align: center; min-height: 60vh;
            display: flex; align-items: center; justify-content: center;
        }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.2rem; opacity: 0.9; }}
        .content {{ padding: 60px 20px; }}
        .section {{ background: white; padding: 40px; margin: 20px 0; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="hero">
        <div>
            <h1>{scraped_data['title']}</h1>
            <p>Optimized modern website experience</p>
        </div>
    </div>
    <div class="container">
        <div class="content">
            <div class="section">
                <h2>Content</h2>
                <p>{scraped_data['content'][:1000]}...</p>
            </div>
            <div class="section">
                <h2>GPT-5 Response</h2>
                <div>{content if content else 'No content returned'}</div>
            </div>
        </div>
    </div>
</body>
</html>"""

def main():
    """Main execution function."""
    print("🚀 Website Optimizer - Scrape & Generate")
    print("=" * 50)
    
    # Setup OpenAI client
    client = setup_openai_client()
    
    # Scrape the website
    scraped_data = scrape_website(HARDCODED_URL)
    print(f"✅ Successfully scraped content from: {scraped_data['title']}")
    
    # Generate optimized HTML
    optimized_html = generate_optimized_html(client, scraped_data)
    
    print("✅ HTML generation completed!")
    # Save HTML to file for easy copying
    output_file = "optimized_website.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(optimized_html)
    
    print("\n" + "=" * 50)
    print(f"📄 HTML saved to: {output_file}")
    print("=" * 50)
    print("🎨 To use in CodePen:")
    print(f"1. Run: docker-compose exec website-optimizer cat {output_file}")
    print("2. Copy the output and paste into CodePen")
    print("💡 Or access the file directly from your host system")
    print("=" * 50)

if __name__ == "__main__":
    main()
