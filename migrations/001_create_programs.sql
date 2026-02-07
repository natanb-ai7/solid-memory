PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    model_year INTEGER NOT NULL,
    term_months INTEGER NOT NULL,
    mileage INTEGER NOT NULL,
    region TEXT NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE NOT NULL,
    program_name TEXT,
    apr REAL,
    residual_value REAL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (make, model, model_year, term_months, mileage, region, effective_from, effective_to)
);

CREATE TRIGGER IF NOT EXISTS trg_programs_updated_at
AFTER UPDATE ON programs
FOR EACH ROW
BEGIN
    UPDATE programs SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
