-- Drop the user if it already exists
-- DROP USER IF EXISTS 'auth_user'@'localhost';

-- create a initial user for auth service  database
CREATE USER 'auth_user'@'localhost' IDENTIFIED BY "Aauth123"; 

-- Create the database if it doesn't exist
-- CREATE DATABASE IF NOT EXISTS auth;


GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'localhost';  -- give access to all tables in auth database to the auth_user

USE auth;

-- Drop the table if it exists
--DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email  VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

INSERT INTO users (email, password) VALUES ('abhi@gmail.com','Admin123');
