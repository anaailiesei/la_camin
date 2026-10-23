# La Cămin

**La Cămin** is a marketplace application designed for students living on or around a university campus. It brings together listings for second-hand items, services, and student-organized activities in one place, allowing students to buy, sell, and connect with one another.

> **Project note:** This README describes the intended architecture and feature scope documented in the project specification. Check the source repositories for the current implementation status.

## Features

The application is designed to support:

- **User accounts:** Registration, login, authorization, and profile management.
- **Listings:** Create, edit, delete, and browse listings for products, services, or events.
- **Search:** Find listings by keyword, category, title, or price.
- **Messaging:** Contact listing owners and store conversations.

Listings include a title, description, price, category, publication date, and author.

## Architecture

The system is organized into three services accessed through a single API gateway:

```text
                      Client
                        |
                  Kong API Gateway
                        |
          +-------------+-------------+
          |             |             |
     Auth Service  Listing Service  Message Service
          |             |             |
          +-------------+-------------+
                        |
                   PostgreSQL
```

- **Auth Service:** User registration, login, authorization, user management, and persistence.
- **Listing Service:** Listing CRUD operations, search, and the main marketplace business logic.
- **Message Service:** Sending, retrieving, and persisting conversations between users.

Services communicate primarily through synchronous HTTP REST APIs.

## Technology stack

| Area | Technology |
| --- | --- |
| Containerization and orchestration | Docker, Docker Compose, Docker Swarm |
| API gateway | Kong |
| Database | PostgreSQL |
| Database administration | Adminer |
| Container and service management | Portainer |
| Monitoring and dashboards | Prometheus, Grafana |
| Automated builds and deployment | GitLab CI/CD |
| Service communication | HTTP REST |

## Deployment and operations

The intended deployment uses Docker containers and a stack configured for Docker Compose and Docker Swarm. Kong routes requests to the relevant service, while Portainer supports service administration. Prometheus and Grafana provide metrics collection and dashboards.

The CI/CD pipeline is designed to build and push Docker images and deploy updated services after repository changes.

*Run commands and environment configuration should be added here once the repository's actual Compose/Swarm files and required variables are available.*

## Team contributions

This project was designed and developed collaboratively by two contributors. Responsibilities were divided as follows:

**Ana-Maria Ailiesei**
- Auth Service design and implementation, including registration, authentication, and authorization.
- User data models and database integration for user accounts.
- Kong API Gateway route configuration.
- CI/CD pipeline configuration for image build, push, and deployment.
- Integration and end-to-end testing of the authentication flow.

**Andreea Olteanu**
- Listing Service and Message Service design and implementation.
- Listing creation, editing, deletion, browsing, and search.
- Messaging functionality and database design for listings and conversations.
- Database administration and monitoring setup.

**Shared work**
- Overall system architecture.
- Docker containerization and Docker Compose/Docker Swarm stack configuration.
- End-to-end testing, debugging, integration, and documentation.

## Repositories

The project specification references separate repositories for Auth Service, Listing Service, and Message Service. Add their GitHub links here once published.
