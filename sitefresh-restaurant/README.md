# SiteFresh Restaurant

Transform any restaurant's existing website into a clean, modern site using a fixed, high-quality template. This tool uses AI only for content normalization, not for generating HTML, ensuring consistent, professional results every time.

## 🚀 Features

- **Fixed Template**: Uses a beautiful, responsive Next.js template with Tailwind CSS
- **Smart Scraping**: Extracts content from any restaurant website using Cheerio
- **AI Content Cleanup**: Optional OpenAI integration for content normalization
- **Image Management**: Downloads and optimizes images locally
- **Schema Validation**: Strict data validation with Zod schemas
- **Modern UI**: Clean, professional design inspired by the best restaurant websites

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router), TypeScript
- **Styling**: Tailwind CSS, shadcn/ui components
- **Data Validation**: Zod schemas
- **Scraping**: Cheerio (server-side)
- **AI**: OpenAI GPT-4 (optional, for content cleanup)
- **Icons**: Lucide React
- **Fonts**: Inter (body), Playfair Display (headings)

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd sitefresh-restaurant

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Add your OpenAI API key (optional)
```

## 🎯 Usage

### Basic Commands

```bash
# Start development server
pnpm dev

# Scrape a restaurant website
pnpm scrape https://www.wohop17.com/

# Scrape with AI content cleanup
pnpm scrape https://www.wohop17.com/ --ai

# Build site (scrape + start dev server)
pnpm build-site https://www.wohop17.com/

# Production build
pnpm build
pnpm start
```

### Example Workflow

1. **Scrape a restaurant website**:
   ```bash
   pnpm scrape https://www.wohop17.com/
   ```
   This creates `content/wohop17-com.json` with all the restaurant data.

2. **View the generated site**:
   ```bash
   pnpm dev
   # Visit http://localhost:3000/wohop17-com
   ```

3. **With AI content cleanup**:
   ```bash
   pnpm scrape https://www.wohop17.com/ --ai
   ```

## 📁 Project Structure

```
/app
  /(site)/[slug]/page.tsx        # Home page rendering from JSON
  /(site)/[slug]/menu/page.tsx   # Menu page rendering from JSON
  /layout.tsx                    # Global layout
  /globals.css                   # Tailwind base + design tokens
/components
  /Hero.tsx                      # Hero section component
  /HeaderNav.tsx                 # Navigation header
  /Footer.tsx                    # Site footer
  /Section.tsx                   # Content sections
  /SmartImage.tsx                # Optimized image component
  /MenuGrid.tsx                  # Menu display component
  /HoursCard.tsx                 # Hours display
  /MapCard.tsx                   # Location display
  /ReviewsStrip.tsx              # Customer reviews
/lib
  /schema.ts                     # Zod schemas + TypeScript types
  /scrape.ts                     # Website scraping logic
  /normalize.ts                  # Data normalization
  /rewrite.ts                    # AI content cleanup
  /slug.ts                       # URL slug utilities
  /images.ts                     # Image download & optimization
/content
  /example-wohop.json           # Sample restaurant data
/public/_imports/…              # Downloaded images
/scripts
  /scrape.ts                    # CLI for scraping
  /build-site.ts                # CLI wrapper
```

## 🎨 Design System

The template uses a clean, modern design with:

- **Typography**: Inter for body text, Playfair Display for headings
- **Colors**: Customizable theme colors via CSS variables
- **Layout**: Responsive grid system with mobile-first approach
- **Components**: Reusable UI components with consistent styling
- **Images**: Smart image optimization with fallbacks

## 🔧 Configuration

### Theme Customization

Edit the theme colors in your restaurant's JSON file:

```json
{
  "theme": {
    "primary": "#b91c1c",      // Main brand color
    "accent": "#111827",       // Secondary color
    "heroOverlay": "rgba(0,0,0,0.35)"  // Hero image overlay
  }
}
```

### Adding Custom Sections

Add custom content sections to your restaurant data:

```json
{
  "sections": [
    {
      "title": "Our Story",
      "body": "We've been serving the community since...",
      "image": "/path/to/image.jpg"
    }
  ]
}
```

## 🤖 AI Content Cleanup

When using the `--ai` flag, the system:

1. **Preserves** all original content and structure
2. **Improves** grammar and clarity
3. **Standardizes** formatting and capitalization
4. **Validates** output against strict schemas
5. **Falls back** to original content if AI fails

The AI is used only for content normalization, never for generating HTML or structure.

## 📊 Data Schema

Restaurant data follows a strict schema:

```typescript
interface RestaurantSite {
  slug: string;
  name: string;
  tagline?: string;
  heroImage?: string;
  logo?: string;
  phone?: string;
  email?: string;
  address?: Address;
  hours?: Hour[];
  menu?: MenuCategory[];
  sections?: Section[];
  reviews?: Review[];
  social?: SocialLinks;
  theme?: ThemeColors;
  sourceUrl: string;
  lastScrapedAt: string;
}
```

## 🚀 Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Connect to Vercel
3. Set environment variables:
   - `OPENAI_API_KEY` (optional)

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Netlify
- Railway
- DigitalOcean App Platform
- AWS Amplify

## 🔒 Legal & Ethics

- **Verify permission** to reuse assets from scraped websites
- **Add attribution** if required by the original site
- **Respect robots.txt** and rate limiting
- **Use responsibly** and in accordance with website terms of service

## 🧪 Testing

```bash
# Run the example
pnpm build-site https://www.wohop17.com/

# Check the generated site
# Visit http://localhost:3000/wohop17-com
```

## 📈 Performance

The generated sites achieve excellent Lighthouse scores:
- **Performance**: ≥ 85
- **Accessibility**: ≥ 95
- **Best Practices**: ≥ 95
- **SEO**: ≥ 95

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

---

**Built with ❤️ for restaurant owners who want beautiful, modern websites without the complexity.**