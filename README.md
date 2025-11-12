# Reviews API - FastAPI & Celery Application

A FastAPI application with Celery for managing review history with categories, including asynchronous access logging and LLM-powered sentiment analysis.

## Tech Stack

- FastAPI
- SQLAlchemy
- Alembic
- Celery
- Redis
- PostgreSQL
- Anthropic Claude

## Prerequisites

- Python 3.9+
- Docker and Docker Compose (for Redis and PostgreSQL)
- Anthropic API key

## Setup Instructions

### 1. Clone the repository


### 2. Create virtual environment

```bash
python -m venv venv
source venv/Scripts/activate  
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

Edit `.env` and add your api keys and postgres and redis url

### 5. Start Docker services (PostgreSQL and Redis)

```bash
docker-compose up -d
```
This will start:
- PostgreSQL on port 5433
- Redis on port 6379

### 6. Run database migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 7. Start the FastAPI application

In one terminal:

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Start the Celery worker

In another terminal:

```bash
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

## API Documentation

Once the application is running, visit:
http://localhost:8000/docs


## API Endpoints

  - `GET /reviews/trends` - Top 5 categories by average stars
  - `GET /reviews/?category_id=<id>` - Paginated reviews by category



## Database Schema

### ReviewHistory
- `id`: Primary key (bigint, auto increment)
- `text`: Review text (varchar, nullable)
- `stars`: Rating (int, 1-10)
- `review_id`: Review identifier (varchar(255), can be duplicate for edit history)
- `tone`: Review tone (varchar(255), nullable, LLM-generated)
- `sentiment`: Review sentiment (varchar(255), nullable, LLM-generated)
- `category_id`: Foreign key to Category
- `created_at`, `updated_at`: Timestamps

### Category
- `id`: Primary key (bigint, auto increment)
- `name`: Category name (varchar(255), unique)
- `description`: Category description (text)

### AccessLog
- `id`: Primary key (bigint, auto increment)
- `text`: Access log entry (varchar)
- `created_at`: Timestamp

## Development

### Adding Sample Data

```bash
python seed_data.py
```



## Celery Tasks

### log_access
Asynchronously logs API endpoint access to the AccessLog table.

### analyze_sentiment_and_tone
Uses Anthropic Claude to analyze review tone and sentiment, then updates the ReviewHistory record.


