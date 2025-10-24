#!/usr/bin/env tsx

import { scrapeRestaurant } from '../lib/scrape';
import { normalizeRestaurantData } from '../lib/normalize';
import { rewriteContent } from '../lib/rewrite';
import { downloadAllImages } from '../lib/images';
import { createSlugFromUrl } from '../lib/slug';
import fs from 'fs';
import path from 'path';

async function main() {
  const url = process.argv[2];
  const useAI = process.argv.includes('--ai');
  
  if (!url) {
    console.error('Usage: pnpm scrape <url> [--ai]');
    process.exit(1);
  }
  
  console.log(`🔍 Scraping ${url}...`);
  
  try {
    // Step 1: Scrape the website
    const scrapedData = await scrapeRestaurant(url);
    console.log('✅ Scraping completed');
    
    // Step 2: Normalize the data
    const normalizedData = normalizeRestaurantData(scrapedData, url);
    console.log('✅ Data normalized');
    
    // Step 3: Optionally rewrite with AI
    let finalData = normalizedData;
    if (useAI) {
      console.log('🤖 Rewriting content with AI...');
      finalData = await rewriteContent(normalizedData);
      console.log('✅ Content rewritten');
    }
    
    // Step 4: Download images
    console.log('📸 Downloading images...');
    const slug = createSlugFromUrl(url);
    finalData = await downloadAllImages(finalData, slug);
    console.log('✅ Images downloaded');
    
    // Step 5: Save to file
    const contentDir = path.join(process.cwd(), 'content');
    if (!fs.existsSync(contentDir)) {
      fs.mkdirSync(contentDir, { recursive: true });
    }
    
    const filePath = path.join(contentDir, `${slug}.json`);
    fs.writeFileSync(filePath, JSON.stringify(finalData, null, 2));
    
    console.log(`✅ Data saved to ${filePath}`);
    console.log(`🌐 View at: http://localhost:3000/${slug}`);
    
  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
}

main();
