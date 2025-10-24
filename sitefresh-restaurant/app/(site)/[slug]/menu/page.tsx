import { notFound } from 'next/navigation';
import { HeaderNav } from '@/components/HeaderNav';
import { MenuGrid } from '@/components/MenuGrid';
import { Footer } from '@/components/Footer';
import { RestaurantSite } from '@/lib/schema';
import fs from 'fs';
import path from 'path';

interface PageProps {
  params: {
    slug: string;
  };
}

async function getSiteData(slug: string): Promise<RestaurantSite | null> {
  try {
    const filePath = path.join(process.cwd(), 'content', `${slug}.json`);
    const fileContents = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(fileContents);
  } catch (error) {
    return null;
  }
}

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params;
  const site = await getSiteData(slug);
  
  if (!site) {
    return {
      title: 'Restaurant Not Found',
    };
  }

  return {
    title: `${site.name} Menu`,
    description: `Browse our delicious menu at ${site.name}`,
  };
}

export default async function MenuPage({ params }: PageProps) {
  const { slug } = await params;
  const site = await getSiteData(slug);
  
  if (!site) {
    notFound();
  }

  return (
    <div className="min-h-screen">
      <HeaderNav site={site} />
      
      <main className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Our Menu
            </h1>
            <p className="text-xl text-gray-600">
              Delicious dishes made with love
            </p>
          </div>
          
          {site.menu && site.menu.length > 0 ? (
            <MenuGrid categories={site.menu} />
          ) : (
            <div className="text-center py-16">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Menu Coming Soon
              </h2>
              <p className="text-gray-600 mb-8">
                We're working on updating our menu. Please check back soon!
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                {site.orderOnlineUrl && (
                  <a 
                    href={site.orderOnlineUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
                  >
                    Order Online
                  </a>
                )}
                {site.reservationUrl && (
                  <a 
                    href={site.reservationUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-6 py-3 border border-primary text-primary rounded-lg hover:bg-primary hover:text-white transition-colors"
                  >
                    Make Reservation
                  </a>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
      
      <Footer site={site} />
    </div>
  );
}
