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
    },
    "salon": {
        "name": "Salon & Barbershop",
        "description": "Contemporary template for hair salons, barbershops, grooming studios, and beauty lounges. Highlights stylist portfolios, service menus, pricing tiers, booking CTAs, testimonials, and location/hours in a luxurious, high-trust presentation tailored to personal care brands.",
        "content": """=== MODERN SALON & BARBERSHOP WEBSITE TEMPLATE ===

Generate a complete, premium, standalone HTML document with inline CSS and JavaScript tailored to upscale salons and grooming studios.

CORE LAYOUT STRUCTURE:

Header (Sticky, Glassmorphism):
- 72px height, translucent backdrop (rgba(255,255,255,0.75)) with blur(18px), subtle border-bottom
- Logo lockup (square mark + salon name) on left, stylist tagline beneath in small caps
- Navigation (About, Services, Stylists, Gallery, Reviews, Book Now) centered with 18px gap
- Primary CTA button on right: "Book Appointment" (brand gradient), secondary ghost button "Call Now"
- Mobile: centered logo, hamburger menu with slide-down panel and CTA duplication

Hero Section (Full viewport):
- Background: full-bleed hero image (hair styling scene) with 30% soft black gradient overlay
- Layered content card (max-width 640px) with glass effect and soft shadow
- Heading: clamp(2.75rem, 6vw, 4.5rem) high-contrast serif or modern display font
- Subheading: 1.15rem copy emphasizing signature experience with 80% white opacity
- Dual CTAs: "Schedule Visit" (solid) and "Meet the Stylists" (outline) with hover transitions
- Include floating badge element for "Award-Winning Stylists" or similar differentiator

Services Section:
- 1200px max-width, 80px vertical rhythm, cream backdrop (#f5f2ed)
- Populate directly from scraped service data (menus, price lists, treatment descriptions)—never invent offerings. If only partial data exists, present what is available and clearly indicate omissions when necessary
- Three-column responsive cards (1col mobile, 2col tablet, 3col desktop)
- Each card: icon circle, service title, luxe description, bullet list, starting price
- Use soft drop shadows, 18px radius, and hover elevation with gentle scale

Stylist Spotlight:
- Two-column split layout (image + biography) with alternating orientation for multiple stylists
- Include stylist headshots (circular frames), specialties, certifications, and social links
- Utilize quote overlays or pull quotes to reinforce expertise

Experience Timeline / Process:
- Horizontal timeline (desktop) → vertical stacked (mobile) detailing consultation → service → aftercare
- Each step: number badge, heading, descriptive copy, iconography

Team / Stylists Section (conditional):
- Render ONLY when scraped data includes stylist or staff details, biographies, or testimonials
- Use a responsive slider or tabbed controls so visitors can browse all provided team members (prev/next buttons, pagination dots, or filters)—never cap the list at three when more profiles exist
- Each profile card: headshot, full name, role/title, specialties, certifications, social and booking links, plus notable accolades
- Include quote snippets or signature styles when provided; omit cards lacking meaningful content
- If no staff data is present, gracefully skip this entire section without placeholder or dummy content

Gallery Section:
- Masonry-inspired grid with mixed image heights, lightbox interaction (JS)
- Images use provided Cloudinary URLs; ensure retina-ready and lazy loaded
- Hover overlay with style name, stylist credit, and service type

Testimonials:
- Carousel (JS) with 3-up layout on desktop, single slide on mobile
- Include rating stars, client names, service received, and pull quote
- Background gradient (brand color → deep charcoal) with white text for contrast

Pricing & Membership:
- Pricing table comparing Classic Cuts, Signature Styles, Premium Packages
- Highlight memberships or grooming plans with savings callouts and CTA
- Ensure accessible table markup and responsive stacking

Location & Hours:
- Card layout with embedded map iframe fallback, contact methods, parking info
- Hours listed in two-column grid with accent icons
- Include "Get Directions" and "Call Salon" buttons (mobile friendly)

Footer:
- Rich footer with appointment CTA banner, newsletter signup, social icons, and service categories
- Dark background (#1f1b24) with muted gold accents (#c6a87d)
- Include business license or compliance text if provided

DESIGN SYSTEM:

Typography:
- Primary: 'Playfair Display' or similar elegant serif for headings (fallback to Georgia)
- Secondary: 'Inter', 'Poppins', or system sans-serif for body copy
- Hierarchy: 72/48/32/24/18/16 sizing with fluid clamp usage

Color Palette (customize to brand when possible):
- Primary accent: rich amber/gold (#c6a87d) or warm copper (#d67f4b)
- Secondary: deep plum (#3a1c32) or charcoal (#1f1b24)
- Neutrals: ivory (#fdfaf5), stone (#e8e2d9), soft gray (#6b6b73)
- Text: #1f1b24 primary, #4d4a52 secondary, white on dark sections

Interactive Elements:
- Buttons: 16px vertical padding, 24px horizontal, 999px pill radius
- Hover states: color shifts, shadow depth, gentle scale 1.02
- Links underline on hover, with focus outlines meeting WCAG AA

Responsive Behavior:
- Breakpoints at 480px, 768px, 1024px, 1280px
- Mobile menu overlay with focus trap, swipe-friendly carousel
- Gallery collapses to 2-up then single column
- Maintain minimum 44px touch targets for controls

Accessibility & UX:
- Semantic HTML, ARIA labels for interactive elements, skip-link navigation
- Alt text for all images describing hairstyles or context
- Visible focus rectangles and high contrast for color pairings
- Ensure carousel and lightbox are keyboard navigable and announce slide changes

CONTENT REQUIREMENTS:

Messaging Preservation:
- Maintain salon's unique voice, signature phrases, and differentiators
- Convert scraped copy into polished, on-brand storytelling
- Include mission statement, stylist expertise, and assurance messaging

Service Details:
- Categorize services (Cuts, Color, Treatments, Grooming, Special Events) strictly according to scraped information
- Show pricing tiers or "Starting at" values only when they appear in the source; never invent numbers
- Surface promotional offers or bundles if mentioned in scraped data and omit them otherwise

Booking & Conversion:
- Prominent CTAs throughout (Schedule, Call, Gift Cards)
- Integrate booking links or phone numbers exactly as provided in the source; if none exist, present the CTA in a disabled state or omit it entirely
- Provide trust builders: certifications, awards, professional products used
- When a staff section exists, wire “Book with <Stylist Name>” actions to actual booking URLs or phone references from the source data; suppress the button when no direct link is available

Image Integration:
- Use provided Cloudinary URLs; favor hero-quality, stylist portraits, and before/after examples
- Maintain consistent aspect ratios and add soft overlays for text legibility
- Avoid stock-looking placeholders; prioritize real imagery from scraped content

TECHNICAL REQUIREMENTS:

HTML:
- Full document with <!DOCTYPE html>, lang attribute, structured head metadata (OG tags, JSON-LD for LocalBusiness / HairSalon)
- Sectioning: header, main, section, article, aside, footer
- Descriptive class names (e.g., "stylist-card", "service-tier")

CSS:
- Custom properties for color palette and spacing scale
- Blend of CSS Grid and Flexbox, layered backgrounds, gradients
- Keyframe animations for subtle fade/slide reveals
- Maintain performance (avoid >150KB inline CSS target)

JavaScript:
- Mobile nav toggle with accessibility (aria-expanded)
- Carousel logic (auto-play with pause on hover, manual controls)
- Lightbox gallery with ESC close and focus management
- Smooth scroll for anchor links, lazy loading for off-screen images

Performance & SEO:
- Lazy load non-critical imagery, preconnect for fonts if used
- Meta description tailored to salon + location
- Structured data includes name, image, priceRange, telephone, address, openingHours
- Use canonical link referencing original URL if appropriate

QUALITY BAR:
- Luxurious, high-end feel with polished animation and typography
- Clear differentiation between feminine, masculine, and gender-neutral services if provided
- Balanced whitespace, layered depth, and editorial photography treatment
- When staff info is available, ensure profiles feel authentic and avoid filler copy; otherwise omit
- Ready for production deployment with consistent spacing and alignment

OUTPUT: Deliver ONLY the complete HTML document (inline CSS/JS) following these specifications exactly—no markdown, no commentary.
"""
    },
    "mechanic": {
        "name": "Automotive Repair & Service",
        "description": "Robust template for independent mechanics, auto repair shops, and service centers. Emphasizes diagnostic capabilities, certified technicians, service categories, financing options, transparent pricing, and appointment scheduling with a trustworthy, high-contrast aesthetic.",
        "content": """=== PROFESSIONAL AUTO REPAIR WEBSITE TEMPLATE ===

Generate a complete, production-ready HTML document with inline CSS and JavaScript tailored to automotive service businesses.

CORE LAYOUT STRUCTURE:

Header (Sticky Utility Bar):
- 72px sticky top bar with dark background (#111827), lit logo/wordmark left-aligned
- Contact cluster (phone, text, email) and emergency CTA (“Call for Roadside”) on right with contrasting accent
- Sub-header service categories (Maintenance, Repair, Diagnostics, Tires, Fleet) using pill buttons that anchor-scroll to sections
- Mobile: collapsible menu with service shortcuts and pinned “Book Service” CTA

Hero Section:
- Full-width hero featuring garage imagery or customer vehicle provided via Cloudinary (fallback to solid gradient if no image)
- Overlay gradient (rgba(17,24,39,0.65)) with left-aligned content block
- Headline clamp(2.75rem, 6vw, 4rem) emphasizing trust (“Certified ASE Technicians” etc.)
- Secondary tagline 1.1rem with 85% white opacity describing core value proposition
- Dual CTAs: solid “Schedule Service” and outlined “View Service Packages”
- Include quick stats badges (e.g., “24/7 Towing”, “Same-Day Brake Repair”) using scraped data when available

Service Overview:
- Four-column (desktop) / two-column (tablet) grid of core service categories
- Each card pulls directly from scraped service entries (title, description, price notes). Absolutely no fabricated services
- Iconography: outlined automotive icons (SVG inline) with accent glow on hover
- Show callouts for warranties, OEM parts usage, or specializations when present in source data

Detailed Service Sections:
- Create anchored subsections for each verified service group (e.g., “Brake Repair”, “Diagnostics”). Use scraped copy verbatim with minimal paraphrasing for clarity
- When pricing is provided, display exact phrases (“Starting at $129”) and highlight financing/discounts verbatim; never invent amounts
- Include comparison table (maintenance intervals, package tiers) only if data exists—otherwise omit gracefully

Diagnostic & Certifications Strip:
- Horizontal band highlighting diagnostic equipment, ASE certifications, OEM authorizations. Use logos only when corresponding image URLs provided; otherwise list text badges
- Showcase guarantee text or mission statements from source copy

Customer Testimonials (Conditional):
- Carousel slider using scraped testimonials/reviews. If none available, omit section entirely without placeholder content
- Each slide: five-star rating visual, quote, customer name, vehicle type if provided

Booking & Financing CTA:
- High-contrast panel with appointment form (name, phone, vehicle, preferred date) and secondary CTA for “Request Estimate”
- Include financing badge (Synchrony, Snap, etc.) if mentioned; otherwise remove financing row
- Display shop operating hours exactly as scraped (use business_hours list) with status indicator (“Open Now”)

Fleet & Commercial Services (Conditional):
- Render only when source mentions fleet/commercial support. Provide support contact pathway, maintenance plans, and response times directly from scraped content

Gallery / Before & After:
- Two-column masonry grid featuring shop photos or repairs from provided images. Include lightbox viewer with captions (vehicle model + service) using actual metadata where available

Map & Contact Footer:
- Split layout: embedded map iframe (with safe fallback message if no map URL), contact cards (address, phone, email, text), service radius list pulled from data if mentioned
- Footer bar with policy links (privacy, warranty, terms), social icons, and partner logos (OEM, tire brands) sourced from the original site only

DESIGN SYSTEM:

Typography:
- Headings: 'Bebas Neue', 'Oswald', or similar condensed uppercase display (fallback to 'Impact', sans-serif)
- Body: 'Inter', 'Roboto', or system sans-serif with 1.6 line-height
- Robotic mono accent for diagnostic data blocks

Color Palette:
- Primary: Deep steel (#1f2937) and asphalt black (#0f172a)
- Accent: Safety yellow (#facc15) and electric blue (#2563eb)
- Neutral backgrounds: #f8fafc for contrast; use #0b1120 for footer
- Ensure AAA contrast for text/buttons

Interactions:
- Buttons with 12px corner radius, high-contrast hover states, subtle 2px lift
- Card hover reveals detail overlays; ensure reduces motion preference disables large animation
- Sticky “Book Service” floating button on mobile with subtle pulse animation (respect prefers-reduced-motion)

Responsive Behavior:
- Breakpoints at 480px, 768px, 1024px, 1280px
- Service grids collapse to single column on mobile, hero copy center-aligned
- Diagnostics strip converts to vertical stack with icon chips

ACCESSIBILITY & UX:
- Semantic structure (header, nav with aria-labels, main, sections, footer)
- Table markup for service comparisons with scope attributes
- Live region updates for booking form success/error states
- Ensure all images include meaningful alt text; for decorative background, use CSS only
- Keyboard navigable carousels and modals with ESC close and focus trapping

CONTENT REQUIREMENTS:

Service Data:
- Use scraped services verbatim. Categorize by theme (Maintenance, Engine, Tires, Electrical) without altering names
- Retain exact pricing verbiage (“$89.99”, “Call for quote”) and disclaimers
- Highlight specials, coupons, seasonal offers only if provided—omit otherwise

Business Hours & Contact:
- Display hours exactly as scraped in clean schedule table; show “Closed” or “By Appointment Only” when present
- Offer click-to-call, click-to-text, and email actions with real data (no placeholders)
- Include emergency or towing numbers if mentioned; otherwise skip

Staff & Certifications (Conditional):
- If technicians or team bios exist, include horizontal cards with headshot, certifications (ASE L1, Master Tech), years of experience, and specialties
- When absent, do not fabricate staff content

Testimonials & Reviews (Conditional):
- Use real customer quotes from scraped data. Include source attribution (Google, Yelp) if noted
- Do not create fictional reviews; omit section when no testimonials exist

TECHNICAL REQUIREMENTS:

HTML:
- Complete document with <!DOCTYPE html>, lang attribute, meta viewport, OG tags, JSON-LD using schema.org/AutoRepair
- Structured data must include business name, address, telephone, priceRange, serviceType list derived from scraped services
- Use descriptive class names (e.g., "service-card", "diagnostic-strip", "appointment-form")

CSS:
- Define CSS variables for colors, spacing, shadows
- Employ CSS Grid for service layouts and flexbox for header/footer alignment
- Include subtle motion via keyframes for CTA pulses; respect prefers-reduced-motion
- Keep inline CSS organized with comments marking sections (/* Header */, /* Services */)

JavaScript:
- Implement mobile nav toggle with aria-expanded support
- Appointment form validation and submission stub (no network request) with success state
- Carousel logic for testimonials and gallery (auto-play with manual controls, pause on hover)
- Scroll-based highlights for service category pills (IntersectionObserver fallback to scroll events)

PERFORMANCE & SEO:
- Lazy-load below-the-fold images; preload hero image when available
- Use real meta description from scraped data; set canonical link to original URL
- Include structured FAQ section only when Q&A exists in source content

QUALITY BAR:
- Convey trustworthy, high-tech aesthetic with precise alignment and consistent spacing
- Ensure every section uses genuine shop data; never add filler or generic content
- Provide clear conversion paths (book, call, quote) on every viewport
- Output must be ready for deployment without additional modification

OUTPUT: Return ONLY the raw HTML document with inline CSS/JS—no markdown, no commentary.
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

