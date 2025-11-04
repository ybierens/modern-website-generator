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

Generate a complete, professional, standalone HTML file with inline CSS and JavaScript.

CORE LAYOUT STRUCTURE:

Header (Sticky):
- 64px height, white background with backdrop blur, 20px horizontal padding
- Logo section: 32px logo image + restaurant name (20px bold)
- Navigation: 14px medium links with 24px spacing
- CTA buttons: Primary "Order Online" + outline "Reservations"
- Mobile: Hamburger menu with smooth slide animations

Hero Section (80vh min):
- Background image with 35% dark overlay for text contrast
- Centered content: max-width 1024px, 20px padding
- Main heading: 56-72px responsive (clamp), bold, white
- Subheading: 20-24px, 90% opacity white, max-width 600px
- Two CTA buttons with 16px gap

Main Content:
- Sections: 64px vertical padding, 1200px max-width
- Grid: 1-col mobile, 2-col tablet, 3-col desktop
- Headings: 48px sections, 24px subsections
- Body: 20px text with 1.6 line-height

Popular Dishes Grid:
- Light gray background (#f9fafb)
- Cards: white, 16px radius, 24px padding, subtle shadow
- Dish images: 192px height, object-fit cover, lazy loading
- Typography: 18px name (semibold), 14px description, 16px price
- Hover: 2px vertical lift transform

Hours & Contact Cards:
- Two-column layout with 32px gap
- Cards: white, 16px radius, 24px padding
- Hours: Clock icon + structured day/time format
- Contact: Location icon + address + map integration

Footer:
- Centered, 40px vertical padding, light background
- Contact info: phone, email, address with separators
- Social links with hover effects and accessibility labels

DESIGN SYSTEM:

Typography:
- Font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
- Scale: 56-72px hero, 48px sections, 24px subsections, 20px body, 16px captions, 14px small

Colors:
- Primary: Customizable brand color (default: #dc2626)
- Text: #111827 primary, gray-600 secondary, white on dark
- Backgrounds: White, light gray (#f9fafb) for section separation
- Overlays: rgba(0,0,0,0.35) hero backgrounds

Interactive Elements:
- Buttons: 12-24px padding, 8px radius, 600 weight, smooth transitions
- Primary: Brand color bg + white text + hover darken
- Secondary: Transparent bg + brand border/text
- Hover: 2px lift transform + enhanced shadow
- Links: Brand color with underline on hover

Responsive:
- Breakpoints: 480px, 768px, 1024px
- 8px spacing grid system
- Flexible typography with clamp()
- Mobile hamburger menu
- Lazy loading images with srcset
- 44px minimum touch targets

Accessibility:
- Semantic HTML5 (header, nav, main, section, footer)
- Proper heading hierarchy (h1 → h2 → h3)
- Alt attributes for all images
- ARIA labels for interactive elements
- WCAG AA color contrast (4.5:1 minimum)
- Keyboard navigation support

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

HTML:
- Complete standalone document with <!DOCTYPE html>
- Inline CSS and JavaScript (no external files)
- Semantic HTML5 elements throughout
- Meaningful class names (e.g., "hero-section", "menu-grid")

CSS:
- Modern features: Flexbox, Grid, custom properties
- Mobile-first with media queries
- Smooth transitions (0.3s ease)
- Efficient selectors, organized structure

JavaScript:
- Mobile menu toggle
- Smooth scroll behavior
- Image lazy loading
- Vanilla JS only (no dependencies)

Performance:
- Lazy load images below fold
- Minimize CSS/JS complexity
- Optimize for Core Web Vitals

SEO:
- Title tag: restaurant name + location
- Meta description (160 chars max)
- Open Graph tags
- JSON-LD structured data for local business

Quality Standards:
- Clean, indented code with comments
- 8px grid system spacing
- Hover effects on interactive elements
- Visual hierarchy with size/color/position
- Ample whitespace for readability
- Rounded corners (8-16px) for modern aesthetics

OUTPUT: Complete, functional, professional website ready for immediate use.

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

