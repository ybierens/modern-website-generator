"""
Website Generator Template Library.

This module contains all available templates for website generation,
organized as a dictionary structure for easy access and maintenance.
Each template includes metadata for AI-powered selection and detailed
specifications for professional website generation.
"""

from typing import Dict, Any, List


# Main template library - dict of dicts structure
TEMPLATES = {
    "restaurant": {
        "name": "Restaurant & Food Service",
        "description": "Professional template for restaurants, cafes, bars, food trucks, and catering services. Features menu displays, location/hours information, hero food imagery, reservation CTAs, and grid-based dish showcases. Optimized for food service businesses with emphasis on visual appeal and call-to-action buttons.",
        "content": """=== PROFESSIONAL RESTAURANT WEBSITE TEMPLATE ===

You are building a modern, professional website for a restaurant using Bootstrap 5. Apply your reasoning to create the optimal design for THIS specific restaurant based on its unique content, style, and brand.

TECHNICAL FOUNDATION:

Required Setup:
- Include Bootstrap 5 CSS: <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
- Include Bootstrap 5 JS Bundle: <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
- Include Bootstrap Icons: <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
- Single self-contained HTML file with inline JavaScript
- Use Bootstrap 5 components and utility classes for ALL styling
- Semantic HTML5 structure (header, nav, main, section, footer)

DESIGN GOALS:

Create a website that:
- Immediately captures the restaurant's atmosphere and personality
- Makes users want to visit or order (clear CTAs)
- Showcases food imagery beautifully and prominently
- Presents information in a scannable, intuitive hierarchy
- Feels premium and professional appropriate for the establishment
- Works flawlessly on mobile, tablet, and desktop

CORE SECTIONS TO INCLUDE:

1. Sticky Navigation
   - Use Bootstrap navbar component with fixed-top class
   - Always accessible while scrolling
   - Logo/name prominently displayed
   - Key navigation links (menu, hours, contact, reservations)
   - Call-to-action buttons for ordering/booking using Bootstrap btn classes
   - Mobile-friendly hamburger menu using Bootstrap navbar-toggler

2. Hero Section
   - Use Bootstrap carousel or jumbotron-style hero with container-fluid
   - Powerful first impression using best available image
   - Clear statement of what makes this restaurant special
   - Prominent action buttons (reserve, order, view menu) using Bootstrap btn-lg classes
   - Should occupy significant viewport height (use min-vh-100 or similar)

3. About/Story (if content available)
   - Restaurant's unique selling points
   - Chef background, philosophy, awards
   - What makes them different

4. Menu/Dishes Showcase
   - Use Bootstrap card components in a grid (row/col classes)
   - Highlight signature dishes or popular items
   - Use food imagery effectively with Bootstrap img-fluid class
   - Show prices clearly if available
   - Organized by category if applicable using Bootstrap tabs or accordion
   - Make items look appetizing and desirable with hover effects

5. Experience Section
   - Ambiance, dining room, bar, private dining
   - Special offerings (brunch, happy hour, events)
   - Any unique experiences or features

6. Location & Hours
   - Clear business hours in easy-to-read format
   - Address with map consideration
   - Contact information (phone, email)
   - Parking or transit information if available

7. Footer
   - Contact details, social links
   - Important links
   - Copyright and credits

DESIGN PRINCIPLES:

Visual Hierarchy:
- Use size, color, spacing, and contrast to guide attention
- Most important actions should be most prominent
- Create clear visual breaks between sections
- Use whitespace generously for breathing room

Typography:
- Choose appropriate scale for the brand (upscale = larger, cleaner / casual = varied)
- Ensure excellent readability
- Create rhythm with consistent spacing
- Use font weights to establish hierarchy

Color & Branding:
- Choose brand colors appropriate to the restaurant's style
- Consider cuisine type (e.g., red for Chinese, green for healthy, black for upscale)
- Maintain strong contrast for readability
- Use color strategically to draw attention

Imagery:
- Make food photos hero elements
- Use overlays on hero images for text legibility
- Ensure images are properly sized and optimized
- Consider aspect ratios that showcase food well

Interaction & Animation:
- Smooth hover states on all interactive elements
- Subtle transitions that feel polished
- Cards that lift or transform on hover
- Mobile menu that slides smoothly

Responsive Design:
- Mobile-first approach
- Touch-friendly targets on mobile (minimum 44px)
- Adapt layouts intelligently across breakpoints
- Optimize image sizes for different screens

CONTENT REQUIREMENTS:

Content Handling:
- Use ALL provided scraped content strategically
- Preserve key messaging and marketing copy
- Highlight unique features and specialties
- Show business information accurately (hours, location, contact)
- Use all provided images contextually where they add value
- Create compelling section headings and subheadings

Business Information:
- Display exactly as scraped: phone, email, address, hours
- Keep menu items, prices, descriptions accurate
- Maintain brand voice and terminology
- Preserve any awards, certifications, special mentions

Quality Standards:
- Professional, polished appearance
- Consistent design language throughout
- Appropriate for the restaurant's price point and style
- Modern without being trendy
- Focus on food and experience

ACCESSIBILITY & SEO:

Accessibility:
- Proper heading hierarchy (h1 → h2 → h3)
- Descriptive alt text for all images
- ARIA labels where needed
- Keyboard navigation support
- Focus indicators on interactive elements
- Sufficient color contrast ratios

SEO Optimization:
- Descriptive title tag with restaurant name and location
- Compelling meta description (150-160 chars)
- Semantic HTML structure
- Open Graph tags for social sharing
- Schema.org structured data for local business

Performance:
- Lazy load images below the fold
- Optimize for fast initial render
- Minimal JavaScript complexity
- Efficient Bootstrap 5 usage

CONTENT REQUIREMENTS:

Content Preservation:
- PRESERVE core business messaging, taglines, and marketing copy exactly
- MAINTAIN original brand voice while modernizing visual presentation
- INCLUDE hero section with main message prominently
- ORGANIZE content in logical sections
- EXTRACT and highlight unique selling points
- PRESENT menu items/specials attractively

Image Integration:
- USE ONLY provided Cloudinary URLs
- PLACE images contextually where they add value
- IMPLEMENT proper alt attributes
- USE 2-3+ images strategically (food, ambiance, key aspects)

Business Information:
- DISPLAY contact info (phone, email, address) exactly as scraped
- PRESENT business hours in clear format
- INCLUDE social media links
- MAINTAIN terminology, specialties, pricing
- HIGHLIGHT awards/certifications if mentioned

Enhancement:
- PARAPHRASE for better readability while preserving meaning
- ADD descriptive subheadings
- EMPHASIZE benefits in scannable format
- ENSURE clear, prominent CTAs

TECHNICAL REQUIREMENTS:

HTML Structure:
- Complete standalone document with <!DOCTYPE html>
- Include Bootstrap 5 CSS and JS CDN links in head and before </body>
- Include Bootstrap Icons CDN in head
- Inline JavaScript only (no external JS files beyond Bootstrap CDN)
- Semantic HTML5 elements throughout (header, nav, main, section, article, footer)
- Use Bootstrap component classes and utility classes throughout

Styling with Bootstrap 5:
- Use Bootstrap 5 utility classes for ALL styling (layout, colors, typography, spacing, etc.)
- Leverage Bootstrap components: navbar, cards, buttons, carousel, modals, accordions, tabs
- Use Bootstrap's grid system (container, row, col) for responsive layouts
- Only write custom CSS in a <style> tag if absolutely necessary for unique effects Bootstrap cannot achieve
- Mobile-first responsive design using Bootstrap breakpoints (sm, md, lg, xl, xxl)
- Use Bootstrap's built-in transitions and hover effects
- Leverage Bootstrap's color system (primary, secondary, success, danger, warning, info, light, dark) and customize with CSS variables if needed

JavaScript Requirements:
- Bootstrap 5 handles mobile hamburger menu toggle automatically
- Smooth scroll behavior for anchor links (Bootstrap scrollspy or custom)
- Image lazy loading with loading="lazy" attribute
- Use Bootstrap's JavaScript components (modals, carousels, dropdowns, etc.)
- Minimal custom JavaScript - leverage Bootstrap's built-in functionality
- Keep JavaScript minimal and clean

Performance Optimization:
- Use loading="lazy" for images below the fold
- Minimize custom CSS - rely on Bootstrap utilities and components
- Optimize for Core Web Vitals
- Keep JavaScript lightweight and efficient - use Bootstrap's optimized bundle

SEO & Meta Tags:
- Title tag: restaurant name + location + relevant keywords
- Meta description (150-160 chars, compelling and keyword-rich)
- Meta viewport tag for responsive design
- Open Graph tags (og:title, og:description, og:image, og:url)
- JSON-LD structured data for LocalBusiness/Restaurant schema

Quality Standards:
- Clean, well-indented HTML with appropriate comments
- Consistent use of Bootstrap's spacing utilities (p-3, p-4, p-5, mb-4, mt-5, etc.)
- Hover effects on all interactive elements using Bootstrap's built-in hover states
- Clear visual hierarchy using Bootstrap typography classes (display-1, h1, lead, etc.)
- Generous whitespace using Bootstrap spacing utilities
- Modern aesthetics with Bootstrap's rounded utilities (rounded, rounded-lg, rounded-circle)
- Smooth transitions on all interactive elements using Bootstrap's built-in transitions
- Use Bootstrap's shadow utilities (shadow, shadow-sm, shadow-lg) for depth

OUTPUT: Complete, functional, professional website ready for immediate use. The generated HTML must be a single, self-contained file that works perfectly when opened directly in a browser or loaded in an iframe.

===
"""
    }
}


def get_all_templates() -> Dict[str, Dict[str, Any]]:
    """
    Get all available templates.
    
    Returns:
        Complete templates dictionary with all metadata and content
    """
    return TEMPLATES


def get_template_metadata() -> Dict[str, Dict[str, str]]:
    """
    Get template metadata (name and description) for all templates.
    Used by the router LLM to select appropriate template.
    
    Returns:
        Dictionary mapping template IDs to their name and description
    """
    return {
        template_id: {
            "name": template_data["name"],
            "description": template_data["description"]
        }
        for template_id, template_data in TEMPLATES.items()
    }


def get_template_content(template_id: str) -> str:
    """
    Get the full template specification content for a specific template.
    
    Args:
        template_id: The template identifier (e.g., "restaurant")
        
    Returns:
        Full template specification string
        
    Raises:
        KeyError: If template_id doesn't exist
    """
    if template_id not in TEMPLATES:
        raise KeyError(f"Template '{template_id}' not found. Available templates: {list(TEMPLATES.keys())}")
    
    return TEMPLATES[template_id]["content"]


def get_template_ids() -> List[str]:
    """
    Get list of all available template IDs.
    
    Returns:
        List of template identifier strings
    """
    return list(TEMPLATES.keys())


def template_exists(template_id: str) -> bool:
    """
    Check if a template exists.
    
    Args:
        template_id: The template identifier to check
        
    Returns:
        True if template exists, False otherwise
    """
    return template_id in TEMPLATES

