import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { RestaurantSite } from '@/lib/schema';

interface HeaderNavProps {
  site: RestaurantSite;
}

export function HeaderNav({ site }: HeaderNavProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <Link href={`/${site.slug}`} className="flex items-center space-x-2">
          {site.logo ? (
            <img 
              src={site.logo} 
              alt={`${site.name} logo`}
              className="h-8 w-8 rounded"
            />
          ) : (
            <div className="h-8 w-8 rounded bg-primary flex items-center justify-center text-primary-foreground font-bold">
              {site.name.charAt(0)}
            </div>
          )}
          <span className="font-bold text-xl">{site.name}</span>
        </Link>
        
        <nav className="hidden md:flex items-center space-x-6">
          <Link 
            href={`/${site.slug}`} 
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            Home
          </Link>
          <Link 
            href={`/${site.slug}/menu`} 
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            Menu
          </Link>
          <Link 
            href={`/${site.slug}#hours`} 
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            Hours
          </Link>
          <Link 
            href={`/${site.slug}#contact`} 
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            Contact
          </Link>
        </nav>
        
        <div className="flex items-center space-x-2">
          {site.orderOnlineUrl && (
            <Button asChild size="sm">
              <a href={site.orderOnlineUrl} target="_blank" rel="noopener noreferrer">
                Order Online
              </a>
            </Button>
          )}
          {site.reservationUrl && (
            <Button asChild variant="outline" size="sm">
              <a href={site.reservationUrl} target="_blank" rel="noopener noreferrer">
                Reservations
              </a>
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
