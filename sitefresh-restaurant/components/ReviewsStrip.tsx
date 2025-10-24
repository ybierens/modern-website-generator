import { Card, CardContent } from '@/components/ui/card';
import { Star } from 'lucide-react';
import { Review } from '@/lib/schema';

interface ReviewsStripProps {
  reviews?: Review[];
}

export function ReviewsStrip({ reviews }: ReviewsStripProps) {
  if (!reviews || reviews.length === 0) {
    return null;
  }

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            What Our Customers Say
          </h2>
          <p className="text-lg text-gray-600">
            Real reviews from real customers
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reviews.slice(0, 6).map((review, index) => (
            <Card key={index} className="h-full">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  {review.rating && (
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`h-4 w-4 ${
                            i < review.rating! 
                              ? 'fill-yellow-400 text-yellow-400' 
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                  )}
                </div>
                
                <p className="text-gray-600 mb-4 italic">
                  "{review.text}"
                </p>
                
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span>{review.author || 'Anonymous'}</span>
                  {review.source && (
                    <span className="font-medium">{review.source}</span>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
