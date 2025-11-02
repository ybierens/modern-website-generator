"""
Professional Template Guidance for AI Website Generation.

This module provides detailed, industry-standard web design specifications
extracted from high-quality template patterns. Used to guide AI generation
toward consistent, professional results.
"""

def get_template_guidance() -> str:
    """
    Return comprehensive template guidance using professional web design terminology.
    
    Returns:
        String containing detailed template specifications for AI generation
    """
    return """
=== PROFESSIONAL RESTAURANT WEBSITE TEMPLATE SPECIFICATION ===

IMPORTANT: You must create a complete, working, standalone HTML file that looks professional and modern. Every section must be fully implemented with proper styling and functionality.

You must follow this exact template architecture while customizing content for the specific restaurant.

LAYOUT ARCHITECTURE:

Header Structure:
- Sticky positioned header with 64px height, white background with backdrop-blur effect
- Horizontal flex container with space-between justification and 20px horizontal padding
- Left section: Logo area with 32px height logo image and restaurant name in 20px bold font
- Center section: Navigation menu with 14px medium-weight links, 24px horizontal spacing
- Right section: Primary CTA button (Order Online) and secondary outline button (Reservations)
- Mobile: Collapsible hamburger menu with smooth slide animations and backdrop blur

Hero Section:
- Full-viewport section with minimum 80vh height using flex centering
- Background image with object-fit: cover and 35% dark rgba overlay for text contrast
- Content container with 1024px max-width, centered alignment, and 20px horizontal padding
- Main heading: 56-72px responsive font size using clamp(), bold weight, white color
- Subheading: 20-24px font size, slightly transparent white (90% opacity), max-width 600px
- Two-button CTA layout with 16px gap: primary white button and outline secondary button
- Button specifications: 12px vertical padding, 24px horizontal padding, 8px border-radius

Main Content Structure:
- Content sections with 64px vertical padding and 1200px max-width containers
- Alternating left-right content layouts with 48px gap between text and image columns
- Section headings: 48px font size, proper hierarchy with margin-bottom spacing
- Body text: 20px font size with 1.6 line-height for optimal readability
- Grid-based components using 1-column mobile, 2-column tablet, 3-column desktop breakpoints

Popular Dishes Section:
- Background color: light gray (#f9fafb) for visual separation
- Grid layout: 1-column mobile, 2-column tablet, 3-column desktop with 24px gaps
- Each dish card: white background, 16px border-radius, 8px subtle drop shadow
- Card padding: 24px internal spacing with hover effect (2px vertical lift transform)
- Dish images: 192px height with object-fit cover and lazy loading attributes
- Typography: 18px dish name (semibold), 14px description, 16px price (primary color)

Hours & Contact Section:
- Two-column card layout with 32px gap between cards
- Each card: white background, 16px border-radius, 24px padding, subtle shadow
- Hours card: Clock icon with business hours in structured day/time format
- Contact card: Location icon with full address and Google Maps integration
- Typography: 18px card titles (semibold), 16px content text, proper contrast ratios

Footer Structure:
- Centered layout with 40px vertical padding and light background color
- Contact information: phone, email, address in horizontal layout with separators
- Social media links with hover effects and proper accessibility labels
- Copyright and source attribution in 14px font size with reduced opacity

VISUAL DESIGN SYSTEM:

Typography Hierarchy:
- Font stack: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
- Hero heading: 56-72px (clamp function for responsive scaling)
- Section headings: 48px with 1.2 line-height and proper margin spacing
- Subsection headings: 24px with medium font weight
- Body text: 20px with 1.6 line-height for optimal readability
- Caption text: 16px with medium weight for labels and metadata
- Small text: 14px for disclaimers and secondary information

Color System:
- Primary brand color: Customizable based on restaurant branding (default: #dc2626)
- Accent color: Neutral gray-900 (#111827) for text and secondary elements
- Background colors: White primary, light gray (#f9fafb) for section separation
- Text hierarchy: Black primary text, gray-600 secondary text, white on dark backgrounds
- Overlay systems: rgba(0,0,0,0.35) for hero backgrounds, rgba(255,255,255,0.95) for headers

Interactive Elements:
- Button styles: 12-24px padding, 8px border-radius, 600 font-weight, smooth transitions
- Primary buttons: Brand color background with white text and hover darkening
- Secondary buttons: Transparent background with brand color border and text
- Hover states: 2px vertical transform lift with enhanced shadow depth
- Focus states: Proper accessibility with visible focus indicators and ARIA labels
- Link styles: Brand color with underline on hover, smooth color transitions

Responsive Design:
- Mobile-first approach with breakpoints: 480px, 768px, 1024px
- Consistent 8px spacing grid system throughout all components
- Flexible typography using clamp() functions for smooth scaling
- Collapsible navigation with hamburger menu and slide animations
- Responsive images with srcset attributes and lazy loading
- Touch-friendly interactive elements with minimum 44px touch targets

Card Components:
- Base styling: 16px border-radius, 8px subtle drop shadow, 24px internal padding
- Hover effects: Enhanced shadow depth and subtle scale transform
- Content organization: Proper heading hierarchy and consistent spacing
- Image handling: Aspect ratio preservation with object-fit cover
- Loading states: Skeleton screens with smooth content transitions

Accessibility Standards:
- Semantic HTML structure with proper heading hierarchy (h1, h2, h3)
- Alt attributes for all images with descriptive text
- ARIA labels for interactive elements and navigation
- Keyboard navigation support with visible focus indicators
- Color contrast ratios meeting WCAG AA standards (4.5:1 minimum)
- Screen reader compatible with proper landmark roles

COMPONENT SPECIFICATIONS:

Navigation Component:
- Desktop: Horizontal menu with 14px medium-weight links, 24px spacing
- Mobile: Hamburger icon triggering full-screen overlay menu
- Smooth animations: 300ms ease transitions for all state changes
- Active states: Brand color highlighting for current page/section
- Sticky behavior: Backdrop blur effect with subtle border bottom

Hero Component:
- Background image implementation with proper fallback colors
- Content overlay with optimal text contrast and readability
- Responsive text scaling using CSS clamp() functions
- Call-to-action buttons with clear visual hierarchy
- Mobile optimization with adjusted padding and font sizes

Content Cards:
- Consistent aspect ratios for visual harmony (4:3 for images)
- Internal spacing following 8px grid system
- Subtle border treatments with proper shadow elevation
- Hover interactions with smooth transforms and shadow changes
- Content organization with proper typography hierarchy

Image Handling:
- Responsive sizing with srcset attributes for different screen densities
- Lazy loading implementation for performance optimization
- Proper alt attributes generated from content context
- Object-fit cover for consistent aspect ratios
- Progressive loading with skeleton placeholders

Form Elements (if applicable):
- Proper labeling with associated input elements
- Validation styling with clear error state indicators
- Accessible error messaging with ARIA attributes
- Consistent styling matching the overall design system
- Touch-friendly sizing for mobile interactions

TECHNICAL REQUIREMENTS:

- Generate complete HTML document with inline CSS and JavaScript
- Mobile-first responsive design with proper viewport meta tag
- SEO optimization with proper meta tags and structured data
- Performance optimization with lazy loading and efficient CSS
- Accessibility compliance with semantic HTML and ARIA attributes
- Cross-browser compatibility with modern web standards
- Clean, maintainable code structure with proper commenting

QUALITY REQUIREMENTS:

Code Quality:
- Write clean, semantic HTML5 with proper indentation
- Use meaningful class names that describe purpose (e.g., "hero-section", "menu-grid", not "div1", "box2")
- Include comments for major sections to improve readability
- Ensure all CSS is organized logically (base styles, layout, components, utilities)
- Keep JavaScript minimal but functional - only what's needed for interactions

Visual Polish:
- Add subtle animations and transitions to enhance user experience (fade-ins, slide-ins on scroll)
- Use consistent spacing throughout (8px grid system)
- Ensure proper visual hierarchy with contrasting colors and sizes
- Include hover effects on interactive elements (buttons, cards, links)
- Add depth with shadows, borders, and background variations

Content Presentation:
- Break up long text blocks with proper paragraph spacing
- Use bullet points or lists when appropriate for readability
- Include visual separators between sections
- Add meaningful section titles that describe content
- Ensure important information stands out (contact info, hours, CTA buttons)

Performance & Best Practices:
- Minimize CSS and JavaScript complexity
- Use efficient selectors (avoid deep nesting)
- Include proper DOCTYPE and meta tags
- Test that the HTML renders correctly in all modern browsers
- Ensure the layout adapts smoothly across all breakpoints

The AI must follow this template architecture precisely while customizing all content, colors, and branding to match the specific restaurant's identity and scraped data. The output MUST be a complete, functional, professional website ready for immediate use.

===
"""


def get_content_integration_requirements() -> str:
    """
    Return specific requirements for integrating scraped content with the template.
    
    Returns:
        String containing content integration specifications
    """
    return """
CONTENT INTEGRATION REQUIREMENTS:

Content Preservation:
- PRESERVE core business messaging, value propositions, and key taglines exactly as scraped
- MAINTAIN strategic wording, calls-to-action, and marketing copy chosen by the business
- RESPECT original brand voice and tone while modernizing visual presentation only
- INCLUDE hero section with main message from original content prominently displayed
- ORGANIZE content in logical sections reflecting original business structure
- EXTRACT and highlight key unique selling points from the scraped content
- PRESENT menu items, specials, or featured offerings in an attractive format

Image Integration:
- USE ONLY the provided Cloudinary URLs - they are optimized and accessible
- PLACE images contextually where they support business purpose and content relevance
- ENSURE each image adds value to its section rather than being purely decorative
- CONSIDER business context when positioning images within the layout structure
- IMPLEMENT proper alt attributes based on image content and business context
- USE at least 2-3 images strategically throughout the website for visual appeal
- PRIORITIZE images that showcase food, ambiance, or key business aspects

Business Information Accuracy:
- DISPLAY contact information (phone, email, address) exactly as scraped
- PRESENT business hours in clear, structured format if available
- INCLUDE social media links with proper accessibility and hover states
- MAINTAIN any specific business terminology, specialties, or unique selling points
- PRESERVE pricing information and menu details with accurate formatting
- EXTRACT cuisine type, specialties, and key business attributes from content
- HIGHLIGHT any awards, certifications, or notable achievements mentioned

Content Enhancement:
- PARAPHRASE and restructure content while preserving core meaning for better readability
- ADD descriptive subheadings to break up content sections logically
- CREATE compelling introductions for each major section
- EMPHASIZE benefits and features in a scannable format (lists, highlights)
- ENSURE call-to-action buttons are clear, prominent, and action-oriented

Layout Organization:
- STRUCTURE content hierarchy to support business goals and user flow
- CREATE logical sections that guide visitors toward conversion actions
- BALANCE information density with visual breathing room and whitespace
- ENSURE critical business information is prominently featured and easily accessible
- IMPLEMENT clear navigation between different content sections and pages
- PLACE most important information above the fold in hero/main section
"""


def get_design_guidance() -> str:
    """
    Return additional design guidance and best practices.
    
    Returns:
        String containing design-specific recommendations
    """
    return """
DESIGN INSPIRATION & BEST PRACTICES:

Modern Web Design Principles:
- Use ample whitespace to avoid visual clutter and improve readability
- Create clear visual hierarchy with size, color, and positioning
- Implement a cohesive color palette that complements the restaurant's brand
- Add subtle gradient backgrounds or textured elements for visual interest
- Use rounded corners (8-16px border-radius) for modern, friendly aesthetics

Interactive Elements:
- Include smooth transitions on all interactive elements (0.3s ease)
- Add hover effects that provide clear feedback (scale, shadow, color change)
- Implement scroll-triggered animations for content sections
- Ensure buttons have clear states: normal, hover, active, focus
- Use icons or graphics to break up text-heavy areas

Content Organization:
- Create multiple content sections to showcase different aspects (About, Menu, Location, Hours)
- Use cards or panels to group related information visually
- Implement a two-column layout for text/image combinations
- Add background color variations between sections for visual separation
- Include testimonials or reviews section if content supports it

Visual Elements:
- Use high-quality images as hero backgrounds with proper overlays
- Implement grid-based layouts for galleries or menu items
- Add decorative elements like subtle patterns or geometric shapes
- Use consistent iconography throughout the site
- Include social proof elements (star ratings, review counts, etc.)

User Experience:
- Make navigation intuitive and easy to understand
- Ensure call-to-action buttons are prominent and action-oriented
- Add breadcrumbs or clear page structure for orientation
- Implement mobile-responsive hamburger menu for small screens
- Provide multiple ways to contact (phone, email, form, map)
"""


def get_technical_constraints() -> str:
    """
    Return technical constraints and requirements for HTML generation.
    
    Returns:
        String containing technical specifications and constraints
    """
    return """
TECHNICAL CONSTRAINTS:

HTML Structure:
- Generate complete, standalone HTML document starting with <!DOCTYPE html>
- Include all CSS and JavaScript inline within the HTML document
- Use semantic HTML5 elements (header, nav, main, section, article, footer)
- Implement proper heading hierarchy (h1 for main title, h2 for sections, etc.)
- Ensure all interactive elements have proper accessibility attributes

CSS Requirements:
- Use modern CSS features (Flexbox, Grid, custom properties) for layout
- Implement mobile-first responsive design with proper media queries
- Include smooth transitions and animations for interactive elements
- Use efficient CSS selectors and avoid inline styles in HTML elements
- Ensure cross-browser compatibility with vendor prefixes where needed

JavaScript Functionality:
- Implement mobile menu toggle functionality with smooth animations
- Add scroll behavior for navigation links to page sections
- Include lazy loading for images to improve performance
- Ensure all JavaScript is vanilla JS (no external dependencies)
- Add error handling for any dynamic functionality

Performance Optimization:
- Minimize CSS and JavaScript for faster loading
- Implement lazy loading for images below the fold
- Use efficient image formats and proper sizing
- Optimize for Core Web Vitals (LCP, FID, CLS)
- Include proper caching headers and meta tags

SEO and Meta Tags:
- Include proper title tag with restaurant name and location
- Add meta description using scraped content (maximum 160 characters)
- Implement Open Graph tags for social media sharing
- Include structured data (JSON-LD) for local business information
- Add canonical URL and proper meta viewport tag

Accessibility Compliance:
- Ensure keyboard navigation works for all interactive elements
- Include proper ARIA labels and roles for complex components
- Maintain color contrast ratios meeting WCAG AA standards
- Provide alt text for all images based on content and context
- Use semantic HTML elements for screen reader compatibility

Browser Support:
- Support modern browsers (Chrome, Firefox, Safari, Edge)
- Include fallbacks for older browser versions where necessary
- Test responsive design on various screen sizes and orientations
- Ensure functionality works without JavaScript as fallback
- Validate HTML and CSS for standards compliance
"""
