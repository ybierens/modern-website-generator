import fs from 'fs';
import path from 'path';
import { createSlugFromUrl } from './slug';

export async function downloadImage(url: string, slug: string, filename?: string): Promise<string | null> {
  try {
    // Create directory if it doesn't exist
    const dir = path.join(process.cwd(), 'public', '_imports', slug);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    // Generate filename if not provided
    const finalFilename = filename || path.basename(new URL(url).pathname) || 'image.jpg';
    const filePath = path.join(dir, finalFilename);
    
    // Download the image
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const buffer = await response.arrayBuffer();
    fs.writeFileSync(filePath, Buffer.from(buffer));
    
    // Return the public path
    return `/_imports/${slug}/${finalFilename}`;
  } catch (error) {
    console.error(`Failed to download image ${url}:`, error);
    return null;
  }
}

export async function downloadAllImages(
  site: any,
  slug: string
): Promise<any> {
  const updatedSite = { ...site };
  
  // Download hero image
  if (site.heroImage && !site.heroImage.startsWith('/')) {
    const localPath = await downloadImage(site.heroImage, slug, 'hero.jpg');
    if (localPath) {
      updatedSite.heroImage = localPath;
    }
  }
  
  // Download logo
  if (site.logo && !site.logo.startsWith('/')) {
    const localPath = await downloadImage(site.logo, slug, 'logo.jpg');
    if (localPath) {
      updatedSite.logo = localPath;
    }
  }
  
  // Download menu item images
  if (site.menu) {
    for (const category of site.menu) {
      for (const item of category.items) {
        if (item.image && !item.image.startsWith('/')) {
          const filename = `${slugify(item.name)}.jpg`;
          const localPath = await downloadImage(item.image, slug, filename);
          if (localPath) {
            item.image = localPath;
          }
        }
      }
    }
  }
  
  // Download section images
  if (site.sections) {
    for (const section of site.sections) {
      if (section.image && !section.image.startsWith('/')) {
        const filename = `${slugify(section.title)}.jpg`;
        const localPath = await downloadImage(section.image, slug, filename);
        if (localPath) {
          section.image = localPath;
        }
      }
    }
  }
  
  return updatedSite;
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
