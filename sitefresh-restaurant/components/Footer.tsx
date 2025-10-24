import { RestaurantSite } from '@/lib/schema';
import { Phone, Mail, MapPin, Instagram, Facebook, Twitter } from 'lucide-react';

interface FooterProps {
  site: RestaurantSite;
}

export function Footer({ site }: FooterProps) {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Restaurant Info */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold">{site.name}</h3>
            {site.tagline && (
              <p className="text-gray-300">{site.tagline}</p>
            )}
            
            <div className="space-y-2">
              {site.phone && (
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4" />
                  <a href={`tel:${site.phone}`} className="hover:text-primary">
                    {site.phone}
                  </a>
                </div>
              )}
              
              {site.email && (
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  <a href={`mailto:${site.email}`} className="hover:text-primary">
                    {site.email}
                  </a>
                </div>
              )}
              
              {site.address && (
                <div className="flex items-start gap-2">
                  <MapPin className="h-4 w-4 mt-1" />
                  <div className="text-sm">
                    {site.address.street && <div>{site.address.street}</div>}
                    {site.address.city && site.address.state && (
                      <div>{site.address.city}, {site.address.state} {site.address.postalCode}</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold">Quick Links</h3>
            <div className="space-y-2">
              <a href={`/${site.slug}`} className="block hover:text-primary">
                Home
              </a>
              <a href={`/${site.slug}/menu`} className="block hover:text-primary">
                Menu
              </a>
              <a href={`/${site.slug}#hours`} className="block hover:text-primary">
                Hours
              </a>
              <a href={`/${site.slug}#contact`} className="block hover:text-primary">
                Contact
              </a>
            </div>
          </div>
          
          {/* Social & Actions */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold">Connect With Us</h3>
            
            {site.social && (
              <div className="flex gap-4">
                {site.social.instagram && (
                  <a 
                    href={site.social.instagram} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="hover:text-primary"
                  >
                    <Instagram className="h-6 w-6" />
                  </a>
                )}
                {site.social.facebook && (
                  <a 
                    href={site.social.facebook} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="hover:text-primary"
                  >
                    <Facebook className="h-6 w-6" />
                  </a>
                )}
                {site.social.x && (
                  <a 
                    href={site.social.x} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="hover:text-primary"
                  >
                    <Twitter className="h-6 w-6" />
                  </a>
                )}
              </div>
            )}
            
            <div className="space-y-2">
              {site.orderOnlineUrl && (
                <a 
                  href={site.orderOnlineUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="block bg-primary text-white px-4 py-2 rounded hover:bg-primary/90 text-center"
                >
                  Order Online
                </a>
              )}
              {site.reservationUrl && (
                <a 
                  href={site.reservationUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="block border border-white text-white px-4 py-2 rounded hover:bg-white hover:text-gray-900 text-center"
                >
                  Make Reservation
                </a>
              )}
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; {currentYear} {site.name}. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
