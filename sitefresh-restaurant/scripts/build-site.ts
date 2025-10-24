#!/usr/bin/env tsx

import { execSync } from 'child_process';
import { createSlugFromUrl } from '../lib/slug';

async function main() {
  const url = process.argv[2];
  const useAI = process.argv.includes('--ai');
  
  if (!url) {
    console.error('Usage: pnpm build-site <url> [--ai]');
    process.exit(1);
  }
  
  const slug = createSlugFromUrl(url);
  
  try {
    // Step 1: Run the scrape script
    console.log('🔨 Building site...');
    const scrapeCommand = useAI ? `pnpm scrape "${url}" --ai` : `pnpm scrape "${url}"`;
    execSync(scrapeCommand, { stdio: 'inherit' });
    
    // Step 2: Check if dev server is running
    try {
      execSync('curl -s http://localhost:3000 > /dev/null', { stdio: 'ignore' });
      console.log('✅ Dev server is running');
    } catch {
      console.log('🚀 Starting dev server...');
      console.log('Run `pnpm dev` in another terminal to start the development server');
    }
    
    console.log(`\n🎉 Site built successfully!`);
    console.log(`📁 Content saved to: content/${slug}.json`);
    console.log(`🌐 View at: http://localhost:3000/${slug}`);
    
  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
}

main();
