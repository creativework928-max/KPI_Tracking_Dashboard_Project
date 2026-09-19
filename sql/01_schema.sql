CREATE TABLE IF NOT EXISTS fact_sales (
    InvoiceNo TEXT NOT NULL,
    StockCode TEXT NOT NULL,
    Description TEXT,
    Quantity INTEGER NOT NULL,
    UnitPrice REAL NOT NULL,
    InvoiceDate TEXT NOT NULL,
    InvoiceDateDate TEXT NOT NULL,
    CustomerID REAL,
    Country TEXT,
    Revenue REAL NOT NULL,
    Year INTEGER,
    MonthNo INTEGER,
    Month TEXT,
    Quarter TEXT
);

CREATE INDEX IF NOT EXISTS ix_fact_date ON fact_sales(InvoiceDateDate);
CREATE INDEX IF NOT EXISTS ix_fact_customer ON fact_sales(CustomerID);
CREATE INDEX IF NOT EXISTS ix_fact_product ON fact_sales(StockCode);
