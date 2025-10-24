'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { WebsiteInput } from '@/components/WebsiteInput';

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerate = async (url: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, useAI: false }),
      });

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Non-JSON response:', text.substring(0, 200));
        throw new Error('Server returned invalid response. Please check the console for details.');
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.details || 'Failed to generate website');
      }

      // Redirect to the generated site
      window.location.href = data.url;
    } catch (error) {
      console.error('Error generating website:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate website';
      alert(`Error: ${errorMessage}`);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            SiteFresh Restaurant
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Transform any restaurant's existing website into a clean, modern site using our fixed, high-quality template.
          </p>
        </div>

        {/* Website Input Form */}
        <div className="mb-16">
          <WebsiteInput onGenerate={handleGenerate} isLoading={isLoading} />
        </div>

        <div className="text-center mb-16">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg">
              <Link href="/example-wohop">
                View Example Site
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <a href="https://github.com/your-repo/sitefresh-restaurant" target="_blank" rel="noopener noreferrer">
                View on GitHub
              </a>
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <Card>
            <CardHeader>
              <CardTitle>🎨 Fixed Template</CardTitle>
              <CardDescription>
                Uses a beautiful, responsive template instead of AI-generated HTML
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Every site looks professional and consistent with our carefully designed components.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>🤖 Smart AI</CardTitle>
              <CardDescription>
                AI only for content normalization, not HTML generation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Reliable results with AI used only for cleaning and standardizing content.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>⚡ Fast Performance</CardTitle>
              <CardDescription>
                Optimized images, clean code, and modern architecture
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Achieves excellent Lighthouse scores with fast loading times.
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">
            Try It Out
          </h2>
          <div className="bg-white rounded-2xl p-8 shadow-lg max-w-2xl mx-auto">
            <h3 className="text-xl font-semibold mb-4">Example Restaurant</h3>
            <p className="text-gray-600 mb-6">
              Check out our example restaurant site built with SiteFresh:
            </p>
            <Button asChild size="lg" className="w-full">
              <Link href="/example-wohop">
                View Wo Hop Restaurant Example
              </Link>
            </Button>
          </div>
        </div>

      </div>
    </div>
  );
}
