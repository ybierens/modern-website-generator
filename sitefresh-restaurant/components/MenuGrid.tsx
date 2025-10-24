import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SmartImage } from '@/components/SmartImage';
import { MenuCategory } from '@/lib/schema';

interface MenuGridProps {
  categories: MenuCategory[];
}

export function MenuGrid({ categories }: MenuGridProps) {
  return (
    <div className="space-y-16">
      {categories.map((category, categoryIndex) => (
        <div key={categoryIndex} className="space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              {category.name}
            </h2>
            <div className="w-24 h-1 bg-primary mx-auto rounded-full"></div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {category.items.map((item, itemIndex) => (
              <Card key={itemIndex} className="overflow-hidden hover:shadow-lg transition-shadow">
                {item.image && (
                  <div className="aspect-[4/3] overflow-hidden">
                    <SmartImage
                      src={item.image}
                      alt={item.name}
                      ratio="4/3"
                      className="w-full h-full"
                    />
                  </div>
                )}
                
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{item.name}</CardTitle>
                    {item.price && (
                      <span className="text-lg font-semibold text-primary">
                        {item.price}
                      </span>
                    )}
                  </div>
                  
                  {item.description && (
                    <p className="text-sm text-gray-600 mt-2">
                      {item.description}
                    </p>
                  )}
                  
                  {item.dietary && item.dietary.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {item.dietary.map((diet, dietIndex) => (
                        <Badge key={dietIndex} variant="secondary" className="text-xs">
                          {diet.toUpperCase()}
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
