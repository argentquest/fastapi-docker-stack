-- Create environment-specific databases
-- This script should be run as the postgres superuser

CREATE DATABASE poc_local OWNER pocuser;
CREATE DATABASE poc_dev OWNER pocuser;
CREATE DATABASE poc_prod OWNER pocuser;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE poc_local TO pocuser;
GRANT ALL PRIVILEGES ON DATABASE poc_dev TO pocuser;
GRANT ALL PRIVILEGES ON DATABASE poc_prod TO pocuser;