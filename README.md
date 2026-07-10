# NC Plus One

## Overview

NC Plus One is an event management application developed as part of the Northcoders Data Engineering, AI & Machine Learning Bootcamp.

The project explores modern software engineering and data engineering practices by modelling an event management platform using a relational PostgreSQL database and exposing data through a RESTful API built with FastAPI. As the project develops, it will continue to evolve with additional functionality and technologies introduced throughout the bootcamp, providing an end-to-end application for exploring database design, API development, authentication, testing and modern engineering practices.

---

## Current Features

- Relational PostgreSQL database designed from an Entity Relationship Diagram (ERD)
- Automated database creation and seeding using Python
- RESTful API built with FastAPI
- User registration with secure password hashing using bcrypt
- User authentication using JWT bearer tokens
- Protected API endpoints using FastAPI dependency injection (`Depends`)
- Event RSVP endpoint for authenticated users
- SQL joins to retrieve related event and venue data
- Integration testing with pytest
- Git feature branch workflow
- Application health check endpoint (`GET /api/health`)

---

## Currently in Development

- RSVP cancellation
- Event creation, editing and management
- Organiser-only endpoints and authorisation
- Event attendee management
- User event dashboards using SQL window functions
- Organiser statistics and analytics

---

## Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.14 | Programming language |
| PostgreSQL | 17 | Relational database |
| FastAPI | 0.138.0 | REST API framework |
| Uvicorn | 0.49.0 | ASGI server |
| psycopg2 | 2.9.12 | PostgreSQL database adapter |
| pytest | 9.1.1 | Integration testing |
| PyJWT | 2.13.0 | JSON Web Token authentication |
| bcrypt | 5.0.0 | Password hashing |
| python-dotenv | 1.2.2 | Environment variable management |
| httpx2 | 2.4.0 | HTTP client for API testing |

---

## Installation

Clone the repository and navigate into the project directory:

```bash
git clone <repository-url>
cd nc-plus-one
```

---

### Installing Python Dependencies

Install all required Python packages inside a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

---

## Environment Configuration

This project uses environment variables to configure the PostgreSQL connection and JWT authentication.

1. Copy the example configuration:

```bash
cp .env.example .env
```

2. Update `.env` with your local PostgreSQL and JWT values:

```text
PGHOST=
PGPORT=
PGDATABASE=
PGUSER=
PGPASSWORD=
JWT_SECRET=
```

| Variable | Description |
|----------|-------------|
| `PGHOST` | PostgreSQL server hostname |
| `PGPORT` | PostgreSQL server port |
| `PGDATABASE` | PostgreSQL database name |
| `PGUSER` | PostgreSQL username |
| `PGPASSWORD` | PostgreSQL password |
| `JWT_SECRET` | Secret used to sign JWTs |

> `.env.example` contains the required variable names only and can be safely committed to the repository. Your `.env` file contains your local configuration and must **not** be committed.

---
## Infrastructure

### Terraform

Terraform stores its state remotely in an S3 backend.

### Bootstrap the backend

1. Create a globally unique S3 bucket to store the Terraform state.
2. Update `terraform/backend.tf` with your bucket name.
3. Ensure the bucket exists before running:

```bash
terraform -chdir=terraform init
```

Terraform will configure the S3 backend and use it to store the project's state.

### EC2

Terraform provisions an Amazon EC2 instance using:

- Instance type: `t2.micro`
- Operating system: Latest Ubuntu Server LTS (selected dynamically using the Terraform `aws_ami` data source)

### RDS PostgreSQL

Terraform provisions a private PostgreSQL RDS instance using:

- **Instance class:** `db.t4g.micro`
- **Allocated storage:** `20 GiB`
- **Public access:** disabled
- **Database port:** `5432`
- **Network access:** permitted only from the EC2 application security group

Database credentials are supplied through a local, gitignored
`terraform.tfvars` file and are not committed to the repository.

---
## Database Design

The database has been designed using relational modelling principles and normalisation techniques. Relationships between entities are enforced using primary and foreign keys.

<p align="center">
  <img src="images/ERD.png" width="700" alt="Entity Relationship Diagram">
</p>

---
## Project Setup & Database Seeding

Create the project database:

```bash
psql -d postgres -f db/setup.sql && python db/seed.py
```

The seed script tears down any existing tables before recreating and repopulating the database.

## Running the API

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

Once the server is running, the API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation can be accessed at:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc


## Running Tests

Run the full integration test suite:

```bash
PYTHONPATH=$PWD pytest
```