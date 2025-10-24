import { notFound } from 'next/navigation';
import { HeaderNav } from '@/components/HeaderNav';
import { Hero } from '@/components/Hero';
import { Section } from '@/components/Section';
import { MenuGrid } from '@/components/MenuGrid';
import { HoursCard } from '@/components/HoursCard';
import { MapCard } from '@/components/MapCard';
import { ReviewsStrip } from '@/components/ReviewsStrip';
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
    title: site.name,
    description: site.tagline || `Visit ${site.name} for great food and service`,
    openGraph: {
      title: site.name,
      description: site.tagline,
      images: site.heroImage ? [site.heroImage] : [],
    },
  };
}

export default async function HomePage({ params }: PageProps) {
  const { slug } = await params;
  const site = await getSiteData(slug);
  
  if (!site) {
    notFound();
  }

  return (
    <div className="min-h-screen">
      <HeaderNav site={site} />
      <Hero site={site} />
      
      {/* Sections */}
      {site.sections && site.sections.map((section, index) => (
        <Section
          key={index}
          title={section.title}
          body={section.body}
          image={section.image}
        />
      ))}
      
      {/* Popular Dishes */}
      {site.menu && site.menu.length > 0 && (
        <section className="py-16 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Popular Dishes
              </h2>
              <p className="text-lg text-gray-600">
                Some of our most loved menu items
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {site.menu[0]?.items.slice(0, 6).map((item, index) => (
                <div key={index} className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {item.name}
                  </h3>
                  {item.description && (
                    <p className="text-gray-600 mb-3">
                      {item.description}
                    </p>
                  )}
                  {item.price && (
                    <p className="text-lg font-semibold text-primary">
                      {item.price}
                    </p>
                  )}
                </div>
              ))}
            </div>
            
            <div className="text-center mt-8">
              <a 
                href={`/${site.slug}/menu`}
                className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
              >
                View Full Menu
              </a>
            </div>
          </div>
        </section>
      )}
      
      {/* Hours & Location */}
      <section id="hours" className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <HoursCard hours={site.hours} />
            <MapCard address={site.address} />
          </div>
        </div>
      </section>
      
      {/* Reviews */}
      <ReviewsStrip reviews={site.reviews} />
      
      <Footer site={site} />
    </div>
  );
}
