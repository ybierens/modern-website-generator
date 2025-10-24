import { SmartImage } from '@/components/SmartImage';
import { Card, CardContent } from '@/components/ui/card';

interface SectionProps {
  title: string;
  body: string;
  image?: string;
}

export function Section({ title, body, image }: SectionProps) {
  return (
    <section className="py-16">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
              {title}
            </h2>
            <div className="prose prose-lg text-gray-600 max-w-none">
              {body.split('\n').map((paragraph, index) => (
                <p key={index} className="mb-4">
                  {paragraph}
                </p>
              ))}
            </div>
          </div>
          
          {image && (
            <div className="order-first lg:order-last">
              <SmartImage
                src={image}
                alt={title}
                ratio="4/3"
                className="w-full"
              />
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
