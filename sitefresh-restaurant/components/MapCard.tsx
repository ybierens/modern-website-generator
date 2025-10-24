import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MapPin, ExternalLink } from 'lucide-react';
import { Address } from '@/lib/schema';

interface MapCardProps {
  address?: Address;
}

export function MapCard({ address }: MapCardProps) {
  if (!address) {
    return null;
  }

  const fullAddress = [
    address.street,
    address.city,
    address.state,
    address.postalCode,
    address.country,
  ].filter(Boolean).join(', ');

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MapPin className="h-5 w-5" />
          Location
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-gray-600">
          {fullAddress}
        </p>
        
        {address.googleMapsUrl && (
          <Button asChild variant="outline" className="w-full">
            <a 
              href={address.googleMapsUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-2"
            >
              <ExternalLink className="h-4 w-4" />
              View on Google Maps
            </a>
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
