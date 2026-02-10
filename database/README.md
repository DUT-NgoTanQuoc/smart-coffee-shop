# Database Setup Instructions

## PostgreSQL Setup

### 1. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

### 2. Create Database
```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE coffee_shop;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE coffee_shop TO postgres;
\q
```

### 3. Run Schema
```bash
psql -U postgres -d coffee_shop -f database/schema.sql
```

### 4. Configure Django
Create `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials.

## Django Migrations

After setting up PostgreSQL, run Django migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Create Superuser

```bash
python manage.py createsuperuser
```

## Load Sample Data (Optional)

If you have sample data fixtures:

```bash
python manage.py loaddata database/sample_data.json
```
