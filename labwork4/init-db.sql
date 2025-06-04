SELECT 'CREATE DATABASE library_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'library_db')\gexec

\c library_db;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";