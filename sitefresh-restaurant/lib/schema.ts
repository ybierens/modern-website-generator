import { z } from "zod";

export const Address = z.object({
  street: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  postalCode: z.string().optional(),
  country: z.string().optional(),
  googleMapsUrl: z.string().url().optional(),
});
export type Address = z.infer<typeof Address>;

export const Hour = z.object({ 
  day: z.string(), 
  open: z.string(), 
  close: z.string() 
});
export const Hours = z.array(Hour);

export const MenuItem = z.object({
  name: z.string(),
  description: z.string().optional(),
  price: z.string().optional(),        // keep as string to avoid parsing errors
  image: z.string().optional(),        // local or remote
  dietary: z.array(z.enum(["vegan","veg","gf","spicy","halal","kosher"])).optional(),
});
export const MenuCategory = z.object({
  name: z.string(),
  items: z.array(MenuItem),
});
export const Menu = z.array(MenuCategory);

export const Review = z.object({
  source: z.string().optional(), // Google, Yelp, etc.
  text: z.string(),
  rating: z.number().min(1).max(5).optional(),
  author: z.string().optional(),
});

export const RestaurantSite = z.object({
  slug: z.string(),
  name: z.string(),
  tagline: z.string().optional(),
  heroImage: z.string().optional(),
  logo: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().optional(),
  address: Address.optional(),
  hours: Hours.optional(),
  reservationUrl: z.string().url().optional(),
  orderOnlineUrl: z.string().url().optional(),
  social: z.object({
    instagram: z.string().url().optional(),
    facebook: z.string().url().optional(),
    tiktok: z.string().url().optional(),
    x: z.string().url().optional(),
  }).optional(),
  sections: z.array(z.object({
    title: z.string(),
    body: z.string(),
    image: z.string().optional(),
  })).optional(),
  reviews: z.array(Review).optional(),
  menu: Menu.optional(),
  images: z.array(z.string()).optional(),
  theme: z.object({
    primary: z.string().default("#b91c1c"),   // red-700
    accent: z.string().default("#111827"),    // gray-900
    heroOverlay: z.string().default("rgba(0,0,0,0.35)"),
  }).default({}),
  sourceUrl: z.string().url(),
  lastScrapedAt: z.string(),
});
export type RestaurantSite = z.infer<typeof RestaurantSite>;
