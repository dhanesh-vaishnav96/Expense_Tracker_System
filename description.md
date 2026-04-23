# 💰 Antigravity Expense Tracker - Comprehensive Project Detail

## 📌 1. Project Overview

The **Antigravity Expense Tracker** is a production-ready, full-stack web application meticulously engineered to empower users to efficiently monitor, analyze, and manage their personal finances (Income and Expenses) in Indian Rupees (₹). 

What sets this application apart is its **"Antigravity UI Concept"**—a premium, modern aesthetic that leverages glassmorphism, dynamic animations, and floating interactive charts to transform mundane financial tracking into an engaging visual experience. It offers a secure, intuitive environment for logging daily transactions, managing custom categories, and deriving insights from powerful monthly and global analytics.

---

## 🛠 2. Complete Technology Stack

The project embraces a modern, robust, and scalable stack, distinctly separated into backend API and frontend presentation layers, tied together via Server-Side Rendering (SSR) templating.

### ⚙️ Backend Technologies
*   **Python (v3.10+)**: The core programming language powering the server logic.
*   **FastAPI**: A modern, high-performance web framework for building the backend APIs and routing. Chosen for its speed, automatic interactive documentation, and asynchronous capabilities.
*   **SQLAlchemy (v2.0)**: The Python SQL toolkit and Object-Relational Mapper (ORM) used to interact with the database using Python objects instead of raw SQL queries.
*   **Alembic**: A lightweight database migration tool for usage with SQLAlchemy, allowing for seamless database schema evolutions.
*   **PostgreSQL**: The robust, open-source relational database used in production (specifically via Neon serverless Postgres). SQLite is used for local development.
*   **psycopg2-binary**: The PostgreSQL database adapter for Python, enabling FastAPI to communicate with the Neon database.
*   **Uvicorn & Gunicorn**: `Uvicorn` acts as the lightning-fast ASGI server, while `Gunicorn` is utilized as the production-grade WSGI HTTP Server process manager.
*   **Passlib & Bcrypt**: Utilized for cryptographic hashing of user passwords to ensure database security.
*   **Python-JOSE (JWT)**: Used for generating and verifying JSON Web Tokens (JWT) to manage secure, stateless user authentication.
*   **Jinja2**: A modern and designer-friendly templating language for Python, used by FastAPI to render dynamic HTML pages.

### 🎨 Frontend Technologies
*   **HTML5 & CSS3**: Formats the structural foundation and styling. Custom Vanilla CSS is extensively used to build the "Antigravity" aesthetic (glassmorphism, gradients, hover micro-interactions, responsive grids).
*   **Vanilla JavaScript**: Handles client-side interactivity, form validations, dynamic DOM updates, and asynchronous API calls (AJAX/Fetch) without the overhead of heavy frameworks.
*   **Chart.js**: A powerful, responsive JavaScript charting library utilized to render the floating Bar Graphs and Line Charts on the analytics dashboard.

### 🔧 Tools & Deployment
*   **Git & GitHub**: Version control system and repository hosting.
*   **Render**: The cloud platform utilized for seamless deployment and hosting of the FastAPI web service (`render.yaml` orchestration).
*   **Neon**: A fully managed serverless Postgres database provider used for production data storage.
*   **Dotenv**: Manages environment variables securely across different development environments.

---

## 🏗 3. Architecture & How It Works

The application operates on a **Monolithic Client-Server Architecture with Server-Side Rendering (SSR)**.

### Request/Response Lifecycle
1.  **Client Interaction**: The user interacts with the browser UI (e.g., clicks "Add Expense").
2.  **Routing & Middleware**: The request is sent to the FastAPI backend (`backend/main.py`). The CORS middleware intercepts and allows the request.
3.  **Authentication Guard**: The system checks for a valid `token` inside HTTP-only cookies. If missing, it redirects to the login page.
4.  **Business Logic & DB**: FastAPI routes the request to specific module routers (`routes/expenses.py`, `routes/dashboard.py`). The router utilizes SQLAlchemy `Session` to interact with the database via models.
5.  **Data Serialization/Rendering**: The backend retrieves data, structures it, and injects it into Jinja2 templates (`frontend/templates/*.html`).
6.  **Response Delivery**: A fully hydrated HTML page is sent back to the client, along with CSS (`frontend/css/`) and JavaScript to provide the final interactive experience.

### Directory Structure
```text
Expense Tracker/
│
├── backend/
│   ├── config/      # Database connection and environment setups (engine, session)
│   ├── models/      # SQLAlchemy ORM Data Models (User, Expense, Income, Category)
│   ├── routes/      # FastAPI endpoint controllers separated by domains
│   ├── schemas/     # Pydantic models for data validation (Input/Output shapes)
│   ├── services/    # Business logic, Auth handling, password hashing
│   └── main.py      # The core entry point of the FastAPI application
│
├── frontend/
│   ├── css/         # Global stylesheets and Antigravity UI themes
│   └── templates/   # Jinja2 HTML templates (dashboard.html, entries.html)
│
├── alembic/         # Database migration scripts
├── alembic.ini      # Alembic configuration
├── render.yaml      # Blueprint for Render cloud deployment
└── requirements.txt # Python dependencies
```

---

## 🔄 4. Detailed Application Workflow

### Phase 1: Onboarding & Authentication
*   **Signup**: A user submits their Name, Email, and Password. The backend (`services/auth.py`) uses `bcrypt` to salt and hash the password before saving the new user record in the `Users` table.
*   **Login**: The user enters credentials. The backend verifies the password hash. Upon success, a securely signed JSON Web Token (JWT) is generated. This token is planted in the user's browser as a secure cookie (`token`), eliminating the need for constant server-side session lookups.

### Phase 2: Category & Entry Management
*   **Contextual Categories**: The app distinguishes between "Expense" categories and "Income" categories. Users can dynamically add new custom categories inline via a dropdown modal without leaving the page.
*   **Adding Entries**: When an expense or credit is added in `entries.html`, the user submits the form. JavaScript optionally intercepts it for validation, then submits the payload via POST. The backend (`routes/expenses.py`) stores this record against the authenticated `user_id` alongside the date, category, and amount.
*   **History & Editing**: All entries are listed in a chronological, responsive table. Users can click to edit or delete any entry. Editing fetches the specific record via a dynamic route (e.g., `/edit-entry/{id}`), pre-fills the form, and updates the database via a `POST` update action.

### Phase 3: Analytics & Dashboard Rendering
*   **Data Aggregation**: When the user accesses `/dashboard`, the backend (`routes/dashboard.py`) runs complex SQLAlchemy aggregation queries. It calculates:
    1.  **Global Balance**: Sum of all historical income minus the sum of all historical expenses.
    2.  **Selected Month Data**: By default, it fetches data for the current month/year, but users can use filters to change this.
    3.  **Daily Trend**: It groups the selected month's expenses by individual day for the Line Chart.
    4.  **Category Totals**: It sums expenses per category for the selected month to populate the Bar Chart.
*   **Visualization**: This aggregated data is serialized into JSON format via a custom Jinja filter and injected directly into a `<script>` tag within `dashboard.html`. Chart.js reads this JSON object upon page load and dynamically animates the aesthetic graphs.

---

## 🗄 5. Database Schema & Relationships

The database is built strictly relationally using foreign keys to maintain data integrity.

1.  **Users Table**:
    *   Stores `id`, `name`, `email` (Unique), hashed `password`, and overall `total_income` snapshot.
2.  **Categories Table**:
    *   Stores `id`, `name`, `type` (Expense vs Income), and a self-referencing `created_by_id` (FK to Users) to allow for both system-default global categories and user-specific custom categories.
3.  **Expenses Table**:
    *   Stores `id`, `amount`, `date`, `note`, with Foreign Keys linking to the `user_id` and the `category_id`.
4.  **Incomes Table**:
    *   Mirrors the Expenses table but records positive cash flows, mapping to `user_id` and an Income-specific `category_id`.

---

## ✅ Conclusion

The Antigravity Expense Tracker is a holistically designed application. By pairing the speed and asynchronous capabilities of FastAPI with a robust PostgreSQL backend and a custom, animation-rich Vanilla JS frontend, it delivers a deeply integrated, performant, and visually stunning user experience tailored specifically for personal finance tracking.
