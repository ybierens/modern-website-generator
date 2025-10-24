import { Button } from '@/components/ui/button';
import { SmartImage } from '@/components/SmartImage';
import { RestaurantSite } from '@/lib/schema';

interface HeroProps {
  site: RestaurantSite;
}

export function Hero({ site }: HeroProps) {
  return (
    <section className="relative h-[80vh] min-h-[600px] flex items-center justify-center overflow-hidden">
      {site.heroImage ? (
        <SmartImage
          src={site.heroImage}
          alt={`${site.name} restaurant`}
          ratio="16/9"
          className="absolute inset-0 w-full h-full"
          priority
        />
      ) : (
        <div 
          className="absolute inset-0 w-full h-full"
          style={{
            background: `linear-gradient(135deg, ${site.theme.primary} 0%, ${site.theme.accent} 100%)`,
          }}
        />
      )}
      
      {/* Overlay */}
      <div 
        className="absolute inset-0"
        style={{ backgroundColor: site.theme?.heroOverlay || 'rgba(0,0,0,0.35)' }}
      />
      
      {/* Content */}
      <div className="relative z-10 text-center text-white max-w-4xl mx-auto px-4">
        <h1 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight">
          {site.name}
        </h1>
        
        {site.tagline && (
          <p className="text-xl md:text-2xl mb-8 text-white/90 max-w-2xl mx-auto">
            {site.tagline}
          </p>
        )}
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button asChild size="lg" className="bg-white text-gray-900 hover:bg-gray-100">
            <a href={`/${site.slug}/menu`}>
              View Menu
            </a>
          </Button>
          
          {site.orderOnlineUrl && (
            <Button asChild variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-gray-900">
              <a href={site.orderOnlineUrl} target="_blank" rel="noopener noreferrer">
                Order Online
              </a>
            </Button>
          )}
        </div>
      </div>
    </section>
  );
}
