import { RestaurantSite, Address, Hour } from './schema';
import { ScrapedData } from './scrape';
import { createSlugFromUrl } from './slug';

export function normalizeRestaurantData(
  scrapedData: ScrapedData,
  sourceUrl: string
): RestaurantSite {
  const slug = createSlugFromUrl(sourceUrl);
  
  // Parse hours from string format
  const hours = parseHours(scrapedData.hours);
  
  // Build address object
  const address: Address | undefined = scrapedData.address ? {
    street: scrapedData.address.street,
    city: scrapedData.address.city,
    state: scrapedData.address.state,
    postalCode: scrapedData.address.postalCode,
    country: scrapedData.address.country,
  } : undefined;
  
  // Convert menu items to proper format
  const menu = scrapedData.menu.map(category => ({
    name: category.name,
    items: category.items.map(item => ({
      name: item.name,
      description: item.description,
      price: item.price,
      image: item.image,
    })),
  }));
  
  // Convert sections
  const sections = scrapedData.sections.map(section => ({
    title: section.title,
    body: section.body,
    image: section.image,
  }));
  
  // Convert reviews
  const reviews = scrapedData.reviews.map(review => ({
    source: review.source,
    text: review.text,
    rating: review.rating,
    author: review.author,
  }));
  
  return {
    slug,
    name: scrapedData.name || 'Restaurant',
    tagline: scrapedData.tagline,
    heroImage: scrapedData.heroImage,
    logo: scrapedData.logo,
    phone: scrapedData.phone,
    email: scrapedData.email,
    address,
    hours,
    reservationUrl: scrapedData.reservationUrl,
    orderOnlineUrl: scrapedData.orderOnlineUrl,
    social: scrapedData.social,
    sections,
    reviews,
    menu,
    images: scrapedData.images,
    theme: {
      primary: '#b91c1c',
      accent: '#111827',
      heroOverlay: 'rgba(0,0,0,0.35)',
    },
    sourceUrl,
    lastScrapedAt: new Date().toISOString(),
  };
}

function parseHours(hoursString?: string): Hour[] | undefined {
  if (!hoursString) return undefined;
  
  const hours: Hour[] = [];
  const lines = hoursString.split('\n').map(line => line.trim()).filter(line => line);
  
  for (const line of lines) {
    // Try to parse common hour formats
    const patterns = [
      // "Monday: 11am-10pm"
      /(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)[\s:]*(\d{1,2}:\d{2}\s*(am|pm)?)[\s-]*(\d{1,2}:\d{2}\s*(am|pm)?)/i,
      // "Mon-Fri: 9am-5pm"
      /(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)[\s-]*(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)[\s:]*(\d{1,2}:\d{2}\s*(am|pm)?)[\s-]*(\d{1,2}:\d{2}\s*(am|pm)?)/i,
    ];
    
    for (const pattern of patterns) {
      const match = line.match(pattern);
      if (match) {
        const day = match[1].toLowerCase();
        const open = match[2] || match[3];
        const close = match[4] || match[5];
        
        if (open && close) {
          hours.push({
            day: day.charAt(0).toUpperCase() + day.slice(1),
            open: normalizeTime(open),
            close: normalizeTime(close),
          });
          break;
        }
      }
    }
  }
  
  return hours.length > 0 ? hours : undefined;
}

function normalizeTime(time: string): string {
  // Convert to 24-hour format if needed
  const cleanTime = time.trim().toLowerCase();
  
  if (cleanTime.includes('am') || cleanTime.includes('pm')) {
    return cleanTime;
  }
  
  // Assume 24-hour format if no am/pm
  return cleanTime;
}
