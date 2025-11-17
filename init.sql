-- Database initialization script for Website Generator
-- This script creates the websites table with proper schema and indexes

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create websites table
CREATE TABLE IF NOT EXISTS websites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identifier VARCHAR(100) NOT NULL UNIQUE,
    original_url TEXT NOT NULL,
    original_html TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_websites_identifier ON websites(identifier);
CREATE INDEX IF NOT EXISTS idx_websites_original_url ON websites(original_url);
CREATE INDEX IF NOT EXISTS idx_websites_created_at ON websites(created_at DESC);

-- Create website_versions table to store multiple generated versions
CREATE TABLE IF NOT EXISTS website_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    website_id UUID NOT NULL REFERENCES websites(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL CHECK (version_number IN (1, 2, 3)),
    generation_instructions TEXT NOT NULL,
    generated_html TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(website_id, version_number)
);

-- Create indexes for website_versions
CREATE INDEX IF NOT EXISTS idx_website_versions_website_id ON website_versions(website_id);
CREATE INDEX IF NOT EXISTS idx_website_versions_version_number ON website_versions(version_number);
CREATE INDEX IF NOT EXISTS idx_website_versions_created_at ON website_versions(created_at DESC);

-- Create jobs table for async processing
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    website_id UUID REFERENCES websites(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on jobs
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);

-- Create image_mappings table for Cloudinary URL mappings
CREATE TABLE IF NOT EXISTS image_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    website_id UUID REFERENCES websites(id) ON DELETE CASCADE,
    original_url TEXT NOT NULL,
    cloudinary_url TEXT NOT NULL,
    alt_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on image_mappings
CREATE INDEX IF NOT EXISTS idx_image_mappings_website_id ON image_mappings(website_id);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_websites_updated_at 
    BEFORE UPDATE ON websites 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_website_versions_updated_at 
    BEFORE UPDATE ON website_versions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at 
    BEFORE UPDATE ON jobs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
