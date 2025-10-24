'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, ExternalLink } from 'lucide-react';

interface WebsiteInputProps {
  onGenerate: (url: string) => void;
  isLoading: boolean;
}

export function WebsiteInput({ onGenerate, isLoading }: WebsiteInputProps) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onGenerate(url.trim());
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-center">
          Generate Restaurant Website
        </CardTitle>
        <CardDescription className="text-center">
          Enter any restaurant website URL to transform it into a clean, modern site
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="website-url" className="text-sm font-medium">
              Restaurant Website URL
            </label>
            <input
              id="website-url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.example-restaurant.com"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
              required
            />
          </div>
          
          <Button 
            type="submit" 
            className="w-full" 
            size="lg"
            disabled={isLoading || !url.trim()}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Website...
              </>
            ) : (
              <>
                <ExternalLink className="mr-2 h-4 w-4" />
                Generate Website
              </>
            )}
          </Button>
        </form>
        
        {isLoading && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-center gap-3 text-blue-800">
              <Loader2 className="h-5 w-5 animate-spin" />
              <div className="text-sm">
                <p className="font-semibold">Generating your website...</p>
                <p className="text-xs mt-1">This may take 30-60 seconds. Please wait.</p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
