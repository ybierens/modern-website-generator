'use client';

import Image from 'next/image';
import { cn } from '@/lib/utils';

interface SmartImageProps {
  src: string;
  alt: string;
  ratio?: '16/9' | '4/3' | '1/1';
  className?: string;
  priority?: boolean;
}

export function SmartImage({ 
  src, 
  alt, 
  ratio = '16/9', 
  className,
  priority = false 
}: SmartImageProps) {
  const aspectRatioMap = {
    '16/9': 'aspect-[16/9]',
    '4/3': 'aspect-[4/3]',
    '1/1': 'aspect-square',
  };

  return (
    <div className={cn('relative overflow-hidden rounded-2xl', aspectRatioMap[ratio], className)}>
      <Image
        src={src}
        alt={alt}
        fill
        className="object-cover"
        priority={priority}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        onError={(e) => {
          // Fallback to placeholder on error
          const target = e.target as HTMLImageElement;
          target.src = `data:image/svg+xml;base64,${btoa(`
            <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
              <rect width="100%" height="100%" fill="#f3f4f6"/>
              <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#9ca3af" font-family="system-ui" font-size="14">
                ${alt || 'Image'}
              </text>
            </svg>
          `)}`;
        }}
      />
    </div>
  );
}
