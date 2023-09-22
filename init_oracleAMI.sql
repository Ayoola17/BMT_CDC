CREATE TABLE CUSREADS (
    rowno RAW(16) PRIMARY KEY,
    cust NUMBER(10,0),
    loc NUMBER(10,0),
    meter VARCHAR2(32),
    consumption NUMBER(7,2),
    consumdt TIMESTAMP,
    rdrtype CHAR(1)
);
