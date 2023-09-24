-- Connect as a privileged user
CONNECT SYSTEM/oracle;

-- Drop the user if it already exists (this is optional and is just for the sake of idempotency)
DROP USER oracleami CASCADE;

-- Create a new user and grant required privileges
CREATE USER oracleami IDENTIFIED BY oracleamipassword;
GRANT CONNECT, RESOURCE TO oracleami;
GRANT CREATE SESSION TO oracleami;
GRANT UNLIMITED TABLESPACE TO oracleami;

-- Now, let's switch to the new user and create the table
CONNECT oracleami/oracleamipassword;

CREATE TABLE CUSREADS (
    rowno RAW(16) PRIMARY KEY,
    cust NUMBER(10,0),
    loc NUMBER(10,0),
    meter VARCHAR2(32),
    consumption NUMBER(7,2),
    consumdt TIMESTAMP,
    rdrtype CHAR(1)
);
