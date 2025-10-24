import { NextRequest, NextResponse } from 'next/server';
import { scrapeRestaurant } from '@/lib/scrape';
import { normalizeRestaurantData } from '@/lib/normalize';
import { rewriteContent } from '@/lib/rewrite';
import { downloadAllImages } from '@/lib/images';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

export async function POST(request: NextRequest) {
  try {
    const { url, useAI = false } = await request.json();

    if (!url) {
      return NextResponse.json(
        { error: 'URL is required' },
        { status: 400 }
      );
    }

    // Validate URL
    let targetUrl: URL;
    try {
      targetUrl = new URL(url);
    } catch {
      return NextResponse.json(
        { error: 'Invalid URL format' },
        { status: 400 }
      );
    }

    // Step 1: Scrape the website
    console.log(`Scraping ${url}...`);
    const rawData = await scrapeRestaurant(url);

    // Step 2: Normalize the data
    console.log('Normalizing data...');
    let normalized = normalizeRestaurantData(rawData, url);

    // Step 3: Optionally rewrite content with AI
    if (useAI && process.env.OPENAI_API_KEY) {
      console.log('Rewriting content with AI...');
      try {
        normalized = await rewriteContent(normalized);
      } catch (error) {
        console.error('AI rewrite failed, using normalized data:', error);
      }
    }

    // Step 4: Download images
    console.log('Downloading images...');
    const withImages = await downloadAllImages(normalized);

    // Step 5: Save to content directory
    const contentDir = join(process.cwd(), 'content');
    mkdirSync(contentDir, { recursive: true });
    const contentPath = join(contentDir, `${withImages.slug}.json`);
    writeFileSync(contentPath, JSON.stringify(withImages, null, 2));

    console.log(`✅ Site generated successfully: ${withImages.slug}`);

    return NextResponse.json({
      success: true,
      slug: withImages.slug,
      url: `/${withImages.slug}`,
    });
  } catch (error) {
    console.error('Generation error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to generate website',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

