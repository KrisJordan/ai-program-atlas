-- An official top-100 membership statement need not disclose an exact rank.
CREATE TABLE rankings_new (
 id INTEGER PRIMARY KEY,
 institution_id TEXT NOT NULL REFERENCES institutions(id),
 publisher TEXT NOT NULL, edition TEXT NOT NULL, category TEXT NOT NULL,
 rank INTEGER CHECK(rank IS NULL OR rank>0),
 source_url TEXT NOT NULL, verification_status TEXT NOT NULL DEFAULT 'secondary_reported',
 source_date TEXT, fetched_at TEXT, locator TEXT,
 rank_upper_bound INTEGER CHECK(rank_upper_bound IS NULL OR rank_upper_bound>0),
 CHECK(rank IS NOT NULL OR rank_upper_bound IS NOT NULL),
 CHECK(rank IS NULL OR rank_upper_bound IS NULL OR rank<=rank_upper_bound),
 UNIQUE(institution_id,publisher,edition,category)
);
INSERT INTO rankings_new(id,institution_id,publisher,edition,category,rank,source_url,verification_status,source_date,fetched_at,locator)
 SELECT id,institution_id,publisher,edition,category,rank,source_url,verification_status,source_date,fetched_at,locator FROM rankings;
DROP TABLE rankings;
ALTER TABLE rankings_new RENAME TO rankings;
