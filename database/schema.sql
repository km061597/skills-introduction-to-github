-- SmartAmazon Database Schema
-- PostgreSQL 15+

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS price_history CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS search_cache CASCADE;
DROP TABLE IF EXISTS category_stats CASCADE;
DROP TABLE IF EXISTS user_searches CASCADE;

-- Products table - Core product information
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(10) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(255),
    current_price DECIMAL(10, 2),
    list_price DECIMAL(10, 2),
    unit_price DECIMAL(10, 4),
    unit_type VARCHAR(10),
    unit_quantity DECIMAL(10, 2),
    discount_pct DECIMAL(5, 2),
    rating DECIMAL(3, 2),
    review_count INTEGER DEFAULT 0,
    verified_review_count INTEGER DEFAULT 0,
    image_url TEXT,
    amazon_url TEXT,
    is_prime BOOLEAN DEFAULT FALSE,
    is_sponsored BOOLEAN DEFAULT FALSE,
    subscribe_save_pct DECIMAL(5, 2),
    in_stock BOOLEAN DEFAULT TRUE,
    last_scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hidden_gem_score INTEGER,
    deal_quality_score INTEGER
);

-- Create indexes for products table
CREATE INDEX idx_products_asin ON products(asin);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_unit_price ON products(unit_price);
CREATE INDEX idx_products_rating ON products(rating);
CREATE INDEX idx_products_is_prime ON products(is_prime);
CREATE INDEX idx_products_is_sponsored ON products(is_sponsored);
CREATE INDEX idx_products_discount_pct ON products(discount_pct);

-- Price history table - Track price changes over time
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    asin VARCHAR(10) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 4),
    is_prime BOOLEAN DEFAULT FALSE,
    is_sponsored BOOLEAN DEFAULT FALSE,
    in_stock BOOLEAN DEFAULT TRUE,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for price_history table
CREATE INDEX idx_price_history_product_id ON price_history(product_id);
CREATE INDEX idx_price_history_asin ON price_history(asin);
CREATE INDEX idx_price_history_recorded_at ON price_history(recorded_at);

-- Search cache table - Cache search results for performance
CREATE TABLE search_cache (
    id SERIAL PRIMARY KEY,
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    results JSON,
    total_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create index for search_cache table
CREATE INDEX idx_search_cache_query_hash ON search_cache(query_hash);
CREATE INDEX idx_search_cache_expires_at ON search_cache(expires_at);

-- Category stats table - Aggregate statistics by category
CREATE TABLE category_stats (
    category VARCHAR(255) PRIMARY KEY,
    median_price DECIMAL(10, 2),
    median_unit_price DECIMAL(10, 4),
    avg_rating DECIMAL(3, 2),
    product_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User searches table - Save user searches (future feature)
CREATE TABLE user_searches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    name VARCHAR(255),
    query TEXT,
    filters JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for user_searches table
CREATE INDEX idx_user_searches_user_id ON user_searches(user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO products (asin, title, brand, category, current_price, list_price, unit_price, unit_type, unit_quantity, discount_pct, rating, review_count, image_url, amazon_url, is_prime, is_sponsored) VALUES
('B000001', 'Optimum Nutrition Gold Standard 100% Whey Protein Powder, 5 lb', 'Optimum Nutrition', 'Protein Powder', 54.99, 79.99, 0.69, 'oz', 80, 31.25, 4.7, 45231, 'https://m.media-amazon.com/images/I/sample1.jpg', 'https://amazon.com/dp/B000001', TRUE, FALSE),
('B000002', 'MuscleTech Nitro-Tech Whey Protein Powder, 4 lb', 'MuscleTech', 'Protein Powder', 49.99, 69.99, 0.78, 'oz', 64, 28.57, 4.5, 23412, 'https://m.media-amazon.com/images/I/sample2.jpg', 'https://amazon.com/dp/B000002', TRUE, FALSE),
('B000003', 'Dymatize ISO100 Hydrolyzed Protein Powder, 3 lb', 'Dymatize', 'Protein Powder', 59.99, 84.99, 1.25, 'oz', 48, 29.42, 4.8, 18945, 'https://m.media-amazon.com/images/I/sample3.jpg', 'https://amazon.com/dp/B000003', TRUE, FALSE),
('B000004', 'BSN Syntha-6 Protein Powder, 5 lb', 'BSN', 'Protein Powder', 44.99, 59.99, 0.56, 'oz', 80, 25.00, 4.6, 34567, 'https://m.media-amazon.com/images/I/sample4.jpg', 'https://amazon.com/dp/B000004', TRUE, TRUE),
('B000005', 'Garden of Life Raw Organic Protein Powder, 1.25 lb', 'Garden of Life', 'Protein Powder', 29.99, 39.99, 1.50, 'oz', 20, 25.00, 4.4, 12890, 'https://m.media-amazon.com/images/I/sample5.jpg', 'https://amazon.com/dp/B000005', TRUE, FALSE),
('B000006', 'Vega Sport Premium Protein Powder, 1.7 lb', 'Vega', 'Protein Powder', 39.99, 49.99, 1.47, 'oz', 27.2, 20.00, 4.3, 9876, 'https://m.media-amazon.com/images/I/sample6.jpg', 'https://amazon.com/dp/B000006', TRUE, FALSE),
('B000007', 'Isopure Zero Carb Protein Powder, 3 lb', 'Isopure', 'Protein Powder', 54.99, 74.99, 1.15, 'oz', 48, 26.67, 4.6, 15678, 'https://m.media-amazon.com/images/I/sample7.jpg', 'https://amazon.com/dp/B000007', TRUE, FALSE),
('B000008', 'Cellucor Whey Sport Protein Powder, 2 lb', 'Cellucor', 'Protein Powder', 24.99, 34.99, 0.78, 'oz', 32, 28.57, 4.5, 8901, 'https://m.media-amazon.com/images/I/sample8.jpg', 'https://amazon.com/dp/B000008', TRUE, TRUE),
('B000009', 'MusclePharm Combat Protein Powder, 4 lb', 'MusclePharm', 'Protein Powder', 42.99, 59.99, 0.67, 'oz', 64, 28.33, 4.7, 27890, 'https://m.media-amazon.com/images/I/sample9.jpg', 'https://amazon.com/dp/B000009', TRUE, FALSE),
('B000010', 'Quest Nutrition Protein Powder, 2 lb', 'Quest', 'Protein Powder', 32.99, 44.99, 1.03, 'oz', 32, 26.67, 4.5, 11234, 'https://m.media-amazon.com/images/I/sample10.jpg', 'https://amazon.com/dp/B000010', TRUE, FALSE);

-- Insert category stats
INSERT INTO category_stats (category, median_price, median_unit_price, avg_rating, product_count) VALUES
('Protein Powder', 47.49, 0.93, 4.56, 10);

-- Insert sample price history
INSERT INTO price_history (asin, price, unit_price, recorded_at) VALUES
('B000001', 54.99, 0.69, CURRENT_TIMESTAMP - INTERVAL '1 day'),
('B000001', 59.99, 0.75, CURRENT_TIMESTAMP - INTERVAL '7 days'),
('B000001', 64.99, 0.81, CURRENT_TIMESTAMP - INTERVAL '14 days'),
('B000002', 49.99, 0.78, CURRENT_TIMESTAMP - INTERVAL '1 day'),
('B000002', 54.99, 0.86, CURRENT_TIMESTAMP - INTERVAL '7 days');

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Confirmation message
DO $$
BEGIN
    RAISE NOTICE '✅ SmartAmazon database schema created successfully!';
    RAISE NOTICE '📊 Sample data inserted';
    RAISE NOTICE '🔍 Ready to search!';
END $$;
