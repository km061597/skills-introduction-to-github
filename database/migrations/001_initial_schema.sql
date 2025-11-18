-- SmartAmazon Database Migration: Initial Schema
-- Version: 001
-- Date: 2025-01-18
-- Description: Create initial database schema with products, price history, and category stats

-- =============================================================================
-- EXTENSIONS
-- =============================================================================

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for faster text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =============================================================================
-- TABLES
-- =============================================================================

-- Products table: Core product information
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(10) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(255),
    current_price DECIMAL(10, 2),
    list_price DECIMAL(10, 2),
    unit_price DECIMAL(10, 4),
    unit_type VARCHAR(50),
    quantity DECIMAL(10, 2),
    discount_pct DECIMAL(5, 2),
    rating DECIMAL(3, 2) CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER DEFAULT 0 CHECK (review_count >= 0),
    verified_review_count INTEGER DEFAULT 0 CHECK (verified_review_count >= 0),
    image_url TEXT,
    amazon_url TEXT,
    is_prime BOOLEAN DEFAULT FALSE,
    is_sponsored BOOLEAN DEFAULT FALSE,
    subscribe_save_pct DECIMAL(5, 2),
    in_stock BOOLEAN DEFAULT TRUE,
    hidden_gem_score INTEGER CHECK (hidden_gem_score >= 0 AND hidden_gem_score <= 100),
    deal_quality_score INTEGER CHECK (deal_quality_score >= 0 AND deal_quality_score <= 100),
    last_scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Price history table: Track price changes over time
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 4),
    is_prime BOOLEAN DEFAULT FALSE,
    is_sponsored BOOLEAN DEFAULT FALSE,
    in_stock BOOLEAN DEFAULT TRUE,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Category statistics table: Aggregate stats per category
CREATE TABLE IF NOT EXISTS category_stats (
    id SERIAL PRIMARY KEY,
    category VARCHAR(255) UNIQUE NOT NULL,
    median_price DECIMAL(10, 2),
    median_unit_price DECIMAL(10, 4),
    avg_rating DECIMAL(3, 2),
    product_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Products indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_products_asin ON products(asin);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_unit_price ON products(unit_price) WHERE unit_price IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating) WHERE rating IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_discount ON products(discount_pct) WHERE discount_pct IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_prime ON products(is_prime) WHERE is_prime = TRUE;
CREATE INDEX IF NOT EXISTS idx_products_in_stock ON products(in_stock) WHERE in_stock = TRUE;
CREATE INDEX IF NOT EXISTS idx_products_updated_at ON products(updated_at);

-- Full-text search index on product title
CREATE INDEX IF NOT EXISTS idx_products_title_trgm ON products USING gin(title gin_trgm_ops);

-- Price history indexes
CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_recorded_at ON price_history(recorded_at);
CREATE INDEX IF NOT EXISTS idx_price_history_product_time ON price_history(product_id, recorded_at DESC);

-- Category stats indexes
CREATE INDEX IF NOT EXISTS idx_category_stats_category ON category_stats(category);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at on products
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update category stats when products change
CREATE OR REPLACE FUNCTION update_category_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update stats for the affected category
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        INSERT INTO category_stats (category, median_price, median_unit_price, avg_rating, product_count, last_updated)
        SELECT
            NEW.category,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY current_price) as median_price,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY unit_price) as median_unit_price,
            AVG(rating) as avg_rating,
            COUNT(*) as product_count,
            CURRENT_TIMESTAMP as last_updated
        FROM products
        WHERE category = NEW.category AND current_price IS NOT NULL
        ON CONFLICT (category) DO UPDATE SET
            median_price = EXCLUDED.median_price,
            median_unit_price = EXCLUDED.median_unit_price,
            avg_rating = EXCLUDED.avg_rating,
            product_count = EXCLUDED.product_count,
            last_updated = EXCLUDED.last_updated;
    END IF;

    -- Handle deletion
    IF TG_OP = 'DELETE' THEN
        UPDATE category_stats
        SET product_count = product_count - 1,
            last_updated = CURRENT_TIMESTAMP
        WHERE category = OLD.category;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update category stats
CREATE TRIGGER update_category_stats_trigger
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_category_stats();

-- =============================================================================
-- VIEWS
-- =============================================================================

-- View for best deals (high discount, good ratings, low unit price)
CREATE OR REPLACE VIEW best_deals AS
SELECT
    p.*,
    CASE
        WHEN p.discount_pct > 30 AND p.rating >= 4.5 AND p.unit_price IS NOT NULL THEN 'excellent'
        WHEN p.discount_pct > 20 AND p.rating >= 4.0 THEN 'good'
        WHEN p.discount_pct > 10 THEN 'fair'
        ELSE 'regular'
    END as deal_quality
FROM products p
WHERE p.discount_pct > 10
  AND p.in_stock = TRUE
ORDER BY p.discount_pct DESC, p.rating DESC;

-- View for hidden gems (great ratings but low review count)
CREATE OR REPLACE VIEW hidden_gems AS
SELECT
    p.*,
    (p.rating * 20 - (LOG(p.review_count + 1) * 5)) as gem_score
FROM products p
WHERE p.rating >= 4.5
  AND p.review_count BETWEEN 100 AND 5000
  AND p.in_stock = TRUE
ORDER BY gem_score DESC;

-- View for recent price drops
CREATE OR REPLACE VIEW recent_price_drops AS
SELECT
    p.asin,
    p.title,
    p.current_price,
    ph_old.price as old_price,
    (ph_old.price - p.current_price) as savings,
    ((ph_old.price - p.current_price) / ph_old.price * 100) as discount_pct,
    ph_old.recorded_at as price_drop_date
FROM products p
JOIN LATERAL (
    SELECT price, recorded_at
    FROM price_history
    WHERE product_id = p.id
      AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
    ORDER BY recorded_at ASC
    LIMIT 1
) ph_old ON true
WHERE ph_old.price > p.current_price
  AND ((ph_old.price - p.current_price) / ph_old.price * 100) >= 10
ORDER BY discount_pct DESC;

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Function to calculate unit price from title
CREATE OR REPLACE FUNCTION calculate_unit_price_from_title(title_text TEXT, current_price DECIMAL)
RETURNS TABLE(unit_price DECIMAL, unit_type VARCHAR, quantity DECIMAL) AS $$
DECLARE
    quantity_value DECIMAL;
    unit_text VARCHAR;
BEGIN
    -- Extract quantity and unit from title (e.g., "5 lb", "80 oz", "2.2 lb")
    -- This is a simplified version - the Python code has more comprehensive extraction

    -- Try to extract weight patterns
    SELECT
        (regexp_match(title_text, '(\d+\.?\d*)\s*(lb|pound|oz|ounce|kg|kilogram|g|gram)s?', 'i'))[1]::DECIMAL,
        (regexp_match(title_text, '(\d+\.?\d*)\s*(lb|pound|oz|ounce|kg|kilogram|g|gram)s?', 'i'))[2]
    INTO quantity_value, unit_text;

    IF quantity_value IS NOT NULL AND unit_text IS NOT NULL THEN
        -- Convert to standard units (oz for weight)
        CASE LOWER(unit_text)
            WHEN 'lb', 'pound' THEN
                quantity_value := quantity_value * 16; -- Convert lb to oz
                unit_text := 'oz';
            WHEN 'kg', 'kilogram' THEN
                quantity_value := quantity_value * 35.274; -- Convert kg to oz
                unit_text := 'oz';
            WHEN 'g', 'gram' THEN
                quantity_value := quantity_value / 28.35; -- Convert g to oz
                unit_text := 'oz';
            ELSE
                unit_text := 'oz';
        END CASE;

        -- Calculate unit price
        RETURN QUERY SELECT
            (current_price / quantity_value)::DECIMAL(10,4),
            unit_text::VARCHAR,
            quantity_value;
    END IF;

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- This will be populated by the application or data import scripts

-- =============================================================================
-- PERMISSIONS
-- =============================================================================

-- Grant appropriate permissions (adjust based on your user setup)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonlyuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO appuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO appuser;

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE products IS 'Core product information from Amazon';
COMMENT ON TABLE price_history IS 'Historical price tracking for products';
COMMENT ON TABLE category_stats IS 'Aggregated statistics per product category';

COMMENT ON COLUMN products.asin IS 'Amazon Standard Identification Number (unique)';
COMMENT ON COLUMN products.unit_price IS 'Price per unit of measurement ($/oz, $/count, etc.)';
COMMENT ON COLUMN products.hidden_gem_score IS 'Score indicating undiscovered quality products (0-100)';
COMMENT ON COLUMN products.deal_quality_score IS 'Overall deal quality score (0-100)';

-- =============================================================================
-- COMPLETION
-- =============================================================================

-- Mark migration as complete
-- INSERT INTO schema_migrations (version, applied_at) VALUES ('001', CURRENT_TIMESTAMP);
