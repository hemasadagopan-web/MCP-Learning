USE master;
GO

-- Drop and recreate the 'DataWarehouse' database
IF EXISTS (SELECT 1 FROM sys.databases WHERE name = 'customers')
BEGIN
    ALTER DATABASE customers SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE customers;
END;
GO


-- Create database
CREATE DATABASE customers;
GO

-- Select the database
USE customers;
GO

-- Create table
CREATE TABLE details (
    name VARCHAR(100),
    gender VARCHAR(20),
    country VARCHAR(100)
);


