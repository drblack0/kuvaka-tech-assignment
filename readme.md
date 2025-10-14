
# 🧠 Thoughtflow — AI Conversational Backend

**Author:** Kartik Saxena
**Status:** 🚀 Deployed & Open Source
**Live API:** [https://thoughtflow.onrender.com](https://thoughtflow.onrender.com) ( I have switched off the deployment for now since it isnt being used )

> *Thoughtflow is a scalable backend platform for building intelligent, user-specific chat experiences — powered by AI, secured with OTP authentication, and monetizable through subscriptions.*

---

## 🌟 Features

* 🔐 **Authentication & Sessions**

  * OTP-based login system with JWT session tokens.
  * Mock OTP in API response for testing.

* 💬 **Chatroom Management**

  * Users can create and manage multiple chatrooms.
  * Asynchronous Gemini AI integration for real-time responses.

* 🧠 **AI Integration**

  * Uses Google Gemini API to generate AI-powered answers.
  * Background processing with Celery and Redis.

* 💳 **Subscriptions & Payments**

  * Integrated with Stripe in sandbox mode.
  * Basic (Free) and Pro (Paid) tiers.
  * Webhooks for real-time subscription updates.

* ⚡ **Performance & Infra**

  * Caching layer with Redis for hot endpoints.
  * Rate limiting for free-tier users.
  * Fully containerized with Docker & Docker Compose.
  * Deployed on Render.

---

## 🏗️ Architecture Overview

```
+-----------+        +-------------+        +---------------+
|  Client   |  -->   | Flask API   |  -->   | PostgreSQL DB |
+-----------+        +-------------+        +---------------+
                         |
                         v
                +----------------+
                | Redis Cache    |
                | (Broker + TTL) |
                +----------------+
                         |
                         v
                 +---------------+
                 | Celery Worker |
                 +---------------+
                         |
                         v
               +---------------------+
               | Stripe / Gemini API |
               +---------------------+
```

---

## 🧰 Tech Stack

* **Backend Framework:** Flask
* **Language:** Python 3.11
* **Database:** PostgreSQL
* **Cache / Queue:** Redis + Celery
* **Payments:** Stripe
* **AI:** Google Gemini API
* **Containerization:** Docker & Docker Compose
* **Deployment:** Render
* **Testing:** Postman

---

## 🚀 Getting Started

### 1. Prerequisites

* Git
* Docker & Docker Compose
* Postman or similar API tool

### 2. Clone & Setup

```bash
git clone https://github.com/drblack0/thoughtflow.git
cd thoughtflow
cp .env.example .env
# fill in your credentials
```

### 3. Run with Docker

```bash
docker-compose up --build
```

* API: `http://localhost:5000`
* RabbitMQ: `http://localhost:15672` (guest/guest)

---

## 📡 API Endpoints

| Endpoint                 | Method | Auth | Description                        |
| ------------------------ | ------ | ---- | ---------------------------------- |
| `/auth/signup`           | POST   | ❌    | Register a new user                |
| `/auth/send-otp`         | POST   | ❌    | Send a mocked OTP                  |
| `/auth/verify-otp`       | POST   | ❌    | Verify OTP and get JWT             |
| `/user/me`               | GET    | ✅    | Get current user                   |
| `/chatroom`              | GET    | ✅    | List all chatrooms (cached)        |
| `/chatroom`              | POST   | ✅    | Create a chatroom                  |
| `/chatroom/<id>/message` | POST   | ✅    | Send message & trigger AI response |
| `/subscribe/pro`         | POST   | ✅    | Start Pro checkout via Stripe      |
| `/subscription/status`   | GET    | ✅    | Get subscription tier              |
| `/webhook/stripe`        | POST   | ❌    | Handle Stripe webhooks             |

---

## 🧠 Key Design Choices

* **Async AI Calls:** Decouples user response from AI latency.
* **Redis Caching:** Speeds up high-traffic endpoints.
* **UUID-based IDs:** Secure & non-sequential entity identifiers.
* **Tiered Plans:** Scalable for monetization.

---

## 🧪 Testing

* Import `Thoughtflow.postman_collection.json` into Postman.
* Set `{{baseUrl}}` to your local or Render URL.
* Run signup → OTP flow → authenticated requests.

---

## 🛠️ Roadmap

* [ ] Real OTP provider (e.g. Twilio)
* [ ] WebSocket-based real-time messaging
* [ ] Admin dashboard
* [ ] User analytics & conversation insights
* [ ] Fine-tuning / custom AI agents

---

Would you like me to tailor this README more **like a developer tool** (for other devs to use the backend) or **like a product landing page** (if you want to make it public)?
👉 This will change the tone and sections (e.g., API docs vs. marketing pitch).
