import OpenAI from 'openai';
import { RestaurantSite } from './schema';

export async function rewriteContent(raw: RestaurantSite): Promise<RestaurantSite> {
  if (!process.env.OPENAI_API_KEY) {
    console.log('No OpenAI API key found, skipping content rewrite');
    return raw;
  }

  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });

  try {
    const prompt = `You are a content normalizer. Return ONLY minified JSON matching this TypeScript zod schema (no markdown, no commentary).

Rules:
- Improve clarity and grammar but keep the restaurant's voice if visible.
- Do not invent menu items, hours, or addresses that were not parsed; you may only clean them.
- For missing images' alt text, infer short neutral alt from filename (e.g., "Beef chow mein").
- Keep prices as strings.
- Output UTF-8 JSON, no trailing commas, no code fences.

Schema:
{
  slug: string,
  name: string,
  tagline?: string,
  heroImage?: string,
  logo?: string,
  phone?: string,
  email?: string,
  address?: {
    street?: string,
    city?: string,
    state?: string,
    postalCode?: string,
    country?: string,
    googleMapsUrl?: string
  },
  hours?: Array<{day: string, open: string, close: string}>,
  reservationUrl?: string,
  orderOnlineUrl?: string,
  social?: {
    instagram?: string,
    facebook?: string,
    tiktok?: string,
    x?: string
  },
  sections?: Array<{title: string, body: string, image?: string}>,
  reviews?: Array<{source?: string, text: string, rating?: number, author?: string}>,
  menu?: Array<{name: string, items: Array<{name: string, description?: string, price?: string, image?: string, dietary?: Array<string>}>}>,
  images?: Array<string>,
  theme?: {primary: string, accent: string, heroOverlay: string},
  sourceUrl: string,
  lastScrapedAt: string
}

Current data to normalize:
${JSON.stringify(raw, null, 2)}`;

    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: 'You are a content normalizer. Return ONLY valid JSON matching the provided schema. Do not add explanations or markdown formatting.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      max_tokens: 4000,
      temperature: 0.2,
    });

    const content = response.choices[0]?.message?.content;
    if (!content) {
      throw new Error('No content returned from OpenAI');
    }

    // Parse the JSON response
    const cleaned = JSON.parse(content);
    
    // Validate with zod schema
    const { RestaurantSite: RestaurantSiteSchema } = await import('./schema');
    const validated = RestaurantSiteSchema.parse(cleaned);
    
    console.log('Content successfully rewritten and validated');
    return validated;
    
  } catch (error) {
    console.error('Content rewrite failed:', error);
    console.log('Falling back to original content');
    return raw;
  }
}
