# Roberts Heating & Air Website

A modern, responsive single-page React website for Roberts Heating & Air, LLC.

## 🚀 Quick Start

**No build step required!** Just open `index.html` in your browser.

```bash
# Open directly in browser
open index.html

# Or serve with a simple server
python -m http.server 8080
# Then visit http://localhost:8080
```

## 📝 How to Edit Content

All website content is managed through `data.json`. No code changes needed!

### Common Edits

**Change phone numbers:**
```json
"phones": ["859-873-9861", "859-785-7597"]
```

**Update service areas:**
```json
"serviceAreas": ["Versailles", "Lawrenceburg", "Georgetown", ...]
```

**Add/edit services:**
```json
"services": [
  {"title": "New Service", "desc": "Description here"}
]
```

**Update contact info:**
```json
"emails": ["info@robertsheatair.com"],
"addresses": {
  "business": "380 A Crossfield Drive, Versailles, KY 40383"
}
```

**Add customer reviews:**
```json
"reviews": [
  {"name": "John D.", "rating": 5, "text": "Great service!"}
]
```

### Structure of data.json

- **`company`** - Business information (name, phones, emails, addresses, license)
- **`nav`** - Navigation menu items
- **`hero`** - Homepage hero section content
- **`services`** - List of services offered
- **`financing`** - Financing and payment options
- **`maintenanceProgram`** - Maintenance program details
- **`contact`** - Contact form and information
- **`faqs`** - Frequently asked questions
- **`reviews`** - Customer testimonials
- **`legal`** - Copyright and legal information

## 🎨 Customization

### Change Colors

Edit CSS variables in `styles.css`:

```css
:root {
  --brand: #0ea5e9;  /* Primary brand color */
  --brand-ink: #041319;  /* Dark brand color */
  /* ... */
}
```

### Add New Sections

1. Add data to `data.json`
2. Create a new component in `app.jsx` following existing patterns
3. Add the component to the main `App` component
4. Add navigation link to `nav` array in `data.json`

**Example - Adding a "Team" section:**

In `data.json`:
```json
"team": [
  {"name": "John Roberts", "title": "Owner", "bio": "30 years experience"}
]
```

In `app.jsx`:
```javascript
function Team({ data }) {
  return (
    <section id="team">
      <div className="container">
        <h2>Our Team</h2>
        <div className="grid grid-3">
          {data.team.map((member, idx) => (
            <div key={idx} className="card">
              <h3>{member.name}</h3>
              <p><strong>{member.title}</strong></p>
              <p>{member.bio}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

Then add `<Team data={data} />` to the `App` component.

## 🌓 Dark Mode

The site includes automatic dark mode support. Users can toggle between light/dark themes using the button in the top bar. Theme preference is saved to localStorage.

## ♿ Accessibility

- Semantic HTML5 structure
- WCAG AA color contrast
- Keyboard navigation support
- ARIA labels on interactive elements
- Focus visible indicators
- "Skip to content" link
- 44px minimum touch targets for mobile

## 📱 Responsive Design

- Mobile-first design approach
- Breakpoints: 768px (tablet), 1024px (desktop)
- Touch-friendly mobile navigation
- Sticky CTA buttons on mobile
- Flexible grid layouts

## 🔧 Technical Details

- **Framework:** React 18 (via esm.sh CDN)
- **Build:** None required (runs directly in browser)
- **Styling:** Pure CSS with CSS variables
- **Data:** JSON-based content management
- **Dependencies:** Zero (React loaded from CDN)

## 📊 Performance

- Lighthouse scores target: 95+ across all metrics
- No external dependencies (except React CDN)
- Lazy loading for images
- Smooth scroll behavior
- Minimal JavaScript footprint

## 🚀 Deployment

### Netlify (Recommended)
1. Drag and drop the `roberts-hvac` folder to Netlify
2. Done! The `netlify.toml` handles SPA routing

### Other Platforms
- Works on any static hosting (Vercel, GitHub Pages, etc.)
- No build process required
- Just upload all files

## 🔄 Migrating to a Build System (Future)

When ready to add a build step:

1. Convert to Vite/Create React App
2. Split `app.jsx` into separate component files
3. Add TypeScript if desired
4. Keep the same `data.json` structure
5. Add server-side form handling

The content contract (data.json structure) remains the same.

## 📧 Form Handling

Currently uses `mailto:` links. To upgrade:

1. Add a backend endpoint (e.g., Netlify Forms, FormSpree, custom API)
2. Update the `handleSubmit` function in `Contact` component
3. Add reCAPTCHA if needed

## 🐛 Troubleshooting

**React not loading?**
- Check internet connection (React loads from CDN)
- Check browser console for errors

**Styling looks wrong?**
- Clear browser cache
- Ensure `styles.css` is in the same folder as `index.html`

**Data not showing?**
- Verify `data.json` is valid JSON (use a JSON validator)
- Check browser console for parsing errors

**Form not working?**
- Ensure email client is configured on the device
- Consider upgrading to a backend form handler

## 📄 License

Copyright © 2025 Roberts Heating & Air, LLC. All rights reserved.

---

## Quick Reference: File Structure

```
roberts-hvac/
├── index.html        # HTML shell
├── app.jsx          # All React components
├── styles.css       # Complete styling
├── data.json        # All content (EDIT THIS!)
├── main.js          # React bootstrap
├── favicon.svg      # Logo
├── netlify.toml     # Deployment config
└── README.md        # This file
```

**To edit content:** Modify `data.json`  
**To edit styling:** Modify `styles.css`  
**To add features:** Modify `app.jsx`  

Questions? Contact the development team.

