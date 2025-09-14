
# Gemini Backend Clone - Kuvaka Tech Assignment

**Submitted by:** [Kartik Saxena]  
**Role:** Backend Developer at Kuvaka Tech

---

## Project Status

**Status:** Completed & Deployed  
**Live API Base URL:** [https://kuvaka-tech-assignment-gl42.onrender.com](https://kuvaka-tech-assignment-gl42.onrender.com)

*Note: The free tier on Render may cause the initial request to take up to 30 seconds to respond as the service spins up from an idle state.*

---

## Table of Contents

1.  [Objective](#objective)
2.  [Features Implemented](#features-implemented)
3.  [Architecture & Tech Stack](#architecture--tech-stack)
4.  [Running The Project Locally](#running-the-project-locally)
5.  [API Endpoints Documentation](#api-endpoints-documentation)
6.  [Key Design Decisions & Justifications](#key-design-decisions--justifications)
7.  [Testing with Postman](#testing-with-postman)

---

## Objective

This project is a comprehensive, Gemini-style backend system built to fulfill the requirements of the Kuvaka Tech backend developer assignment. It features a robust, scalable architecture that enables user-specific chatrooms, OTP-based authentication, AI-powered conversations via the Google Gemini API, and subscription management using Stripe.

The system is fully containerized with Docker for consistent development and deployment environments.

---

## Features Implemented

-   **User Authentication:**
    -   [x] OTP-based login system using mobile numbers.
    -   [x] Mocked OTP returned in the API response for testing.
    -   [x] Full session management using JSON Web Tokens (JWT).
-   **Chatroom Management:**
    -   [x] Users can create and manage multiple, isolated chatrooms.
    -   [x] Full conversational support, with user messages passed to the Google Gemini API.
    -   [x] Asynchronous handling of Gemini API calls using a Celery task queue with a Redis broker.
-   **Google Gemini API Integration:**
    -   [x] Seamless integration with the Gemini API for generating AI responses.
-   **Subscription & Payments (Stripe):**
    -   [x] Integration with Stripe (in sandbox mode) for payment processing.
    -   [x] Two-tier subscription model: `Basic (Free)` and `Pro (Paid)`.
    -   [x] API endpoint to initiate a Stripe Checkout session.
    -   [x] Stripe webhook to handle payment events (success, failure).
    -   [x] API endpoint for users to check their current subscription status.
-   **Technical Requirements:**
    -   [x] **Caching:** Implemented query caching on the `GET /chatroom` endpoint to improve performance and reduce database load.
    -   [x] **Rate Limiting:** Middleware logic stubbed out to implement rate-limiting for `Basic` tier users.
    -   [x] **Containerization:** The entire application stack (API, Worker, Database, Cache) is containerized using Docker and orchestrated with Docker Compose.

---

## Architecture & Tech Stack

This project follows a microservices-oriented architecture, with distinct components for the web API, background processing, and data storage, all orchestrated by Docker Compose.

+----------------+ +------------------+ +---------------------+
| Client |----->| Flask API |----->| PostgreSQL DB |
| (Postman) | | (Gunicorn) | | (User/Chat Data) |
+----------------+ +-------+----------+ +---------------------+
|
| +------------------+
+-->| Redis |
| | (Cache & Broker) |
| +------------------+
|
| +------------------+
+-->| Celery Worker |
+-------+----------+
|
+-------+----------+
| External APIs |
| (Stripe, Gemini) |
+------------------+


### Technology Stack

-   **Language/Framework:** Python 3.11 / Flask
-   **Web Server:** Gunicorn
-   **Database:** PostgreSQL
-   **Cache & Message Broker:** Redis
-   **Asynchronous Task Queue:** Celery
-   **Payments:** Stripe API
-   **External AI API:** Google Gemini API
-   **Containerization:** Docker & Docker Compose
-   **Deployment Platform:** Render

---

## Running The Project Locally

The entire application stack is containerized, making the local setup incredibly simple.

### Prerequisites

-   Git
-   Docker
-   Docker Compose
-   A Postman client (or similar API tool)

### Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/kuvaka-tech-assignment.git
    cd kuvaka-tech-assignment
    ```

2.  **Create the environment file:**
    Create a file named `.env` in the root of the project and copy the contents of `.env.example` into it. Populate it with your own credentials.
    ```bash
    cp .env.example .env
    # Now, open .env and fill in your secret keys
    ```
    *Note: The default database, Redis, and RabbitMQ credentials in the `.env` file are configured to work with the Docker Compose setup.*

3.  **Build and run the containers:**
    This single command will build the Docker images, start all the services (API, worker, Postgres, Redis), and connect them.
    ```bash
    docker-compose up --build
    ```

4.  **The application is now running!**
    -   The API is available at `http://localhost:5000`.
    -   The RabbitMQ Management UI is at `http://localhost:15672` (user: `guest`, pass: `guest`).

---

## API Endpoints Documentation

**Base URL:** `http://localhost:5000` (local) or your Render URL.

*Authentication: Protected routes require a Bearer Token in the `Authorization` header.*

| Endpoint                      | Method | Auth? | Description                                                 | Request Body Example                                     |
| ----------------------------- | ------ | ----- | ----------------------------------------------------------- | -------------------------------------------------------- |
| `/auth/signup`                | POST   | No    | Registers a new user.                                       | `{"mobile": "...", "username": "...", "password": "..."}` |
| `/auth/send-otp`              | POST   | No    | Sends a mocked OTP to the user's mobile.                    | `{"mobile": "..."}`                                      |
| `/auth/verify-otp`            | POST   | No    | Verifies OTP and returns a JWT token.                       | `{"mobile": "...", "otp": "..."}`                         |
| `/user/me`                    | GET    | Yes   | Returns details of the authenticated user.                  | (None)                                                   |
| `/chatroom`                   | POST   | Yes   | Creates a new chatroom.                                     | `{"title": "My First Chat"}` (optional)                  |
| `/chatroom`                   | GET    | Yes   | Lists all chatrooms for the user (cached).                  | (None)                                                   |
| `/chatroom/<uuid:id>`         | GET    | Yes   | Retrieves details and messages of a specific chatroom.      | (None)                                                   |
| `/chatroom/<uuid:id>/message` | POST   | Yes   | Sends a message and triggers an async Gemini API call.      | `{"content": "Hello, world!"}`                           |
| `/subscribe/pro`              | POST   | Yes   | Initiates a Pro subscription via Stripe Checkout.           | (None)                                                   |
| `/subscription/status`        | GET    | Yes   | Checks the user's current subscription tier.                | (None)                                                   |
| `/webhook/stripe`             | POST   | No    | Handles webhook events from Stripe for payment status.      | (Sent by Stripe)                                         |

---

## Key Design Decisions & Justifications

-   **Asynchronous Task Processing (Celery & Redis):** The call to the external Google Gemini API is handled asynchronously in a background task. This ensures the `/chatroom/:id/message` endpoint responds to the user instantly (`202 Accepted`) without waiting for the API call to complete, providing a non-blocking and highly responsive user experience.

-   **Caching Strategy (Redis):** The `GET /chatroom` endpoint, which lists all of a user's chatrooms, is cached.
    -   **Justification:** This endpoint is frequently accessed when loading a user dashboard. Since the list of chatrooms changes much less frequently than the messages within them, caching this data significantly reduces database load and improves API response times. A short TTL (5 minutes) ensures the data remains reasonably fresh.

-   **Containerization (Docker):** The entire application stack is containerized to ensure a consistent and reproducible environment across development, testing, and production. This eliminates "it works on my machine" problems and simplifies the setup process for other developers.

-   **Database Choice (PostgreSQL):** PostgreSQL was chosen for its robustness, reliability, and excellent support for native `UUID` types, which are used as primary keys for all major entities, ensuring unique, non-sequential identifiers.

---

## Testing with Postman

A Postman collection (`Kuvaka Tech Assignment.postman_collection.json`) is included in this repository.

1.  **Import the Collection:** Import the file into your Postman client.
2.  **Set the Base URL:** The collection uses a variable `{{baseUrl}}`. Set this to `http://localhost:5000` for local testing or your live Render URL.
3.  **Authentication Flow:**
    -   First, use the `/auth/signup` request to create a user.
    -   Then, use `/auth/send-otp` and `/auth/verify-otp` to get a JWT token.
    -   Copy the token from the response.
    -   For all protected routes, go to the "Authorization" tab, select "Bearer Token", and paste the token into the field.
