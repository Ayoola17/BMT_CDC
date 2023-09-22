CREATE TABLE MREADS (
    rid UUID PRIMARY KEY,
    cust INTEGER,
    loc INTEGER,
    meter VARCHAR(32),
    cosum DECIMAL(7, 2),
    cosdt TIMESTAMP,
    costy CHAR(1)
);
