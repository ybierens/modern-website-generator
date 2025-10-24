import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Clock } from 'lucide-react';
import { Hours } from '@/lib/schema';

interface HoursCardProps {
  hours?: Hours;
}

export function HoursCard({ hours }: HoursCardProps) {
  if (!hours || hours.length === 0) {
    return null;
  }

  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Hours
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {hours.map((hour, index) => (
            <div key={index} className="flex justify-between items-center py-1">
              <span className="font-medium text-gray-900">
                {hour.day}
              </span>
              <span className="text-gray-600">
                {hour.open} - {hour.close}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
