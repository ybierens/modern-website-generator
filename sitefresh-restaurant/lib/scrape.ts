import * as cheerio from 'cheerio';
import { RestaurantSite } from './schema';

export interface ScrapedData {
  name?: string;
  tagline?: string;
  phone?: string;
  email?: string;
  address?: {
    street?: string;
    city?: string;
    state?: string;
    postalCode?: string;
    country?: string;
  };
  hours?: string;
  heroImage?: string;
  logo?: string;
  images: string[];
  sections: Array<{ title: string; body: string; image?: string }>;
  menu: Array<{ name: string; items: Array<{ name: string; description?: string; price?: string; image?: string }> }>;
  social: {
    instagram?: string;
    facebook?: string;
    tiktok?: string;
    x?: string;
  };
  reviews: Array<{ source?: string; text: string; rating?: number; author?: string }>;
}

export async function scrapeRestaurant(url: string): Promise<ScrapedData> {
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; SiteFresh/1.0)',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const html = await response.text();
    const $ = cheerio.load(html);
    
    // Extract JSON-LD structured data
    const jsonLdData = extractJsonLd($);
    
    // Extract OpenGraph data
    const ogData = extractOpenGraph($);
    
    // Extract basic info
    const name = extractName($, jsonLdData, ogData);
    const tagline = extractTagline($, jsonLdData, ogData);
    const phone = extractPhone($, jsonLdData);
    const email = extractEmail($, jsonLdData);
    const address = extractAddress($, jsonLdData);
    const hours = extractHours($, jsonLdData);
    const heroImage = extractHeroImage($, ogData);
    const logo = extractLogo($, jsonLdData);
    const images = extractImages($);
    const sections = extractSections($);
    const menu = extractMenu($);
    const social = extractSocial($);
    const reviews = extractReviews($);
    
    return {
      name,
      tagline,
      phone,
      email,
      address,
      hours,
      heroImage,
      logo,
      images,
      sections,
      menu,
      social,
      reviews,
    };
  } catch (error) {
    console.error('Scraping error:', error);
    throw new Error(`Failed to scrape ${url}: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

function extractJsonLd($: cheerio.CheerioAPI): any {
  const jsonLdScripts = $('script[type="application/ld+json"]');
  for (let i = 0; i < jsonLdScripts.length; i++) {
    try {
      const content = $(jsonLdScripts[i]).html();
      if (content) {
        const data = JSON.parse(content);
        if (data['@type'] === 'Restaurant' || data['@type'] === 'LocalBusiness') {
          return data;
        }
      }
    } catch (e) {
      // Continue to next script
    }
  }
  return null;
}

function extractOpenGraph($: cheerio.CheerioAPI): any {
  const ogData: any = {};
  $('meta[property^="og:"]').each((_, el) => {
    const property = $(el).attr('property');
    const content = $(el).attr('content');
    if (property && content) {
      const key = property.replace('og:', '').replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
      ogData[key] = content;
    }
  });
  return ogData;
}

function extractName($: cheerio.CheerioAPI, jsonLd: any, og: any): string | undefined {
  // Try JSON-LD first
  if (jsonLd?.name) return jsonLd.name;
  
  // Try OpenGraph
  if (og.title) return og.title;
  
  // Try page title
  const title = $('title').text();
  if (title) return title;
  
  // Try h1
  const h1 = $('h1').first().text().trim();
  if (h1) return h1;
  
  return undefined;
}

function extractTagline($: cheerio.CheerioAPI, jsonLd: any, og: any): string | undefined {
  if (jsonLd?.description) return jsonLd.description;
  if (og.description) return og.description;
  
  // Look for meta description
  const metaDesc = $('meta[name="description"]').attr('content');
  if (metaDesc) return metaDesc;
  
  return undefined;
}

function extractPhone($: cheerio.CheerioAPI, jsonLd: any): string | undefined {
  if (jsonLd?.telephone) return jsonLd.telephone;
  
  // Look for phone patterns in text
  const phoneRegex = /(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})/;
  const text = $('body').text();
  const match = text.match(phoneRegex);
  if (match) return match[0];
  
  return undefined;
}

function extractEmail($: cheerio.CheerioAPI, jsonLd: any): string | undefined {
  if (jsonLd?.email) return jsonLd.email;
  
  // Look for email patterns
  const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
  const text = $('body').text();
  const match = text.match(emailRegex);
  if (match) return match[0];
  
  return undefined;
}

function extractAddress($: cheerio.CheerioAPI, jsonLd: any): any {
  if (jsonLd?.address) {
    return {
      street: jsonLd.address.streetAddress,
      city: jsonLd.address.addressLocality,
      state: jsonLd.address.addressRegion,
      postalCode: jsonLd.address.postalCode,
      country: jsonLd.address.addressCountry,
    };
  }
  
  return undefined;
}

function extractHours($: cheerio.CheerioAPI, jsonLd: any): string | undefined {
  if (jsonLd?.openingHours) return jsonLd.openingHours;
  
  // Look for hours patterns in text
  const hoursRegex = /(mon|tue|wed|thu|fri|sat|sun)[\w\s]*:?\s*\d{1,2}:\d{2}\s*(am|pm)?[\s-]*\d{1,2}:\d{2}\s*(am|pm)?/gi;
  const text = $('body').text();
  const match = text.match(hoursRegex);
  if (match) return match[0];
  
  return undefined;
}

function extractHeroImage($: cheerio.CheerioAPI, og: any): string | undefined {
  if (og.image) return og.image;
  
  // Look for large images that might be hero images
  const images = $('img').toArray();
  let largestImage = '';
  let largestSize = 0;
  
  for (const img of images) {
    const $img = $(img);
    const src = $img.attr('src');
    const width = parseInt($img.attr('width') || '0');
    const height = parseInt($img.attr('height') || '0');
    const size = width * height;
    
    if (src && size > largestSize && size > 10000) {
      largestImage = src;
      largestSize = size;
    }
  }
  
  return largestImage || undefined;
}

function extractLogo($: cheerio.CheerioAPI, jsonLd: any): string | undefined {
  if (jsonLd?.logo) return jsonLd.logo;
  
  // Look for logo images
  const logoSelectors = [
    'img[alt*="logo" i]',
    'img[class*="logo" i]',
    'img[id*="logo" i]',
    '.logo img',
    '#logo img',
  ];
  
  for (const selector of logoSelectors) {
    const logo = $(selector).attr('src');
    if (logo) return logo;
  }
  
  return undefined;
}

function extractImages($: cheerio.CheerioAPI): string[] {
  const images: string[] = [];
  $('img').each((_, el) => {
    const src = $(el).attr('src');
    if (src && !src.startsWith('data:')) {
      images.push(src);
    }
  });
  return [...new Set(images)]; // Remove duplicates
}

function extractSections($: cheerio.CheerioAPI): Array<{ title: string; body: string; image?: string }> {
  const sections: Array<{ title: string; body: string; image?: string }> = [];
  
  // Look for common section patterns
  const sectionSelectors = [
    'section',
    '.section',
    '.content',
    '.about',
    '.story',
    '.history',
  ];
  
  for (const selector of sectionSelectors) {
    $(selector).each((_, el) => {
      const $section = $(el);
      const title = $section.find('h1, h2, h3').first().text().trim();
      const body = $section.text().trim();
      const image = $section.find('img').first().attr('src');
      
      if (title && body && body.length > 50) {
        sections.push({ title, body, image });
      }
    });
  }
  
  return sections;
}

function extractMenu($: cheerio.CheerioAPI): Array<{ name: string; items: Array<{ name: string; description?: string; price?: string; image?: string }> }> {
  const menu: Array<{ name: string; items: Array<{ name: string; description?: string; price?: string; image?: string }> }> = [];
  
  // Look for menu sections
  const menuSelectors = [
    '.menu',
    '#menu',
    '.menu-section',
    '.menu-category',
  ];
  
  for (const selector of menuSelectors) {
    $(selector).each((_, el) => {
      const $section = $(el);
      const categoryName = $section.find('h2, h3, .category-name').first().text().trim();
      
      if (categoryName) {
        const items: Array<{ name: string; description?: string; price?: string; image?: string }> = [];
        
        $section.find('.menu-item, .item, li').each((_, itemEl) => {
          const $item = $(itemEl);
          const name = $item.find('.name, .item-name, strong').first().text().trim();
          const description = $item.find('.description, .item-desc').first().text().trim();
          const price = $item.find('.price, .item-price').first().text().trim();
          const image = $item.find('img').first().attr('src');
          
          if (name) {
            items.push({ name, description, price, image });
          }
        });
        
        if (items.length > 0) {
          menu.push({ name: categoryName, items });
        }
      }
    });
  }
  
  return menu;
}

function extractSocial($: cheerio.CheerioAPI): { instagram?: string; facebook?: string; tiktok?: string; x?: string } {
  const social: { instagram?: string; facebook?: string; tiktok?: string; x?: string } = {};
  
  $('a[href*="instagram.com"]').each((_, el) => {
    const href = $(el).attr('href');
    if (href) social.instagram = href;
  });
  
  $('a[href*="facebook.com"]').each((_, el) => {
    const href = $(el).attr('href');
    if (href) social.facebook = href;
  });
  
  $('a[href*="tiktok.com"]').each((_, el) => {
    const href = $(el).attr('href');
    if (href) social.tiktok = href;
  });
  
  $('a[href*="twitter.com"], a[href*="x.com"]').each((_, el) => {
    const href = $(el).attr('href');
    if (href) social.x = href;
  });
  
  return social;
}

function extractReviews($: cheerio.CheerioAPI): Array<{ source?: string; text: string; rating?: number; author?: string }> {
  const reviews: Array<{ source?: string; text: string; rating?: number; author?: string }> = [];
  
  // Look for review patterns
  const reviewSelectors = [
    '.review',
    '.testimonial',
    '.customer-review',
    '.rating',
  ];
  
  for (const selector of reviewSelectors) {
    $(selector).each((_, el) => {
      const $review = $(el);
      const text = $review.text().trim();
      const rating = $review.find('.rating, .stars').text().match(/\d+/)?.[0];
      const author = $review.find('.author, .name').text().trim();
      
      if (text && text.length > 20) {
        reviews.push({
          text,
          rating: rating ? parseInt(rating) : undefined,
          author: author || undefined,
        });
      }
    });
  }
  
  return reviews;
}
