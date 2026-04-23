# 💰 Antigravity Expense Tracker - Professional Financial Analytics System

## 📌 1. Project Vision & Overview
The **Antigravity Expense Tracker** is a high-performance, full-stack financial management ecosystem designed to bring clarity and "gravity-defying" aesthetics to personal finance. It is not just a logging tool; it is a **visual analytics platform** built for speed, security, and absolute responsiveness.

### ✨ The "Antigravity" Philosophy
The application is built on a unique design system characterized by:
*   **Glassmorphism**: Semi-transparent, blurred layers that create a sense of depth and modernity.
*   **Dynamic Motion**: Floating animations (`ag-float`) and smooth transitions (`ag-hover`) that make the UI feel "alive."
*   **Mobile-First Precision**: Specialized optimizations for high-density mobile displays like the **Realme C75 (412px)**, ensuring a premium experience on any device.

---

## 🛠 2. The Core Technology Stack

The system is architected using a modern, decoupled philosophy that prioritizes performance and developer experience.

### 🚀 Backend: The Engine (FastAPI & SQLAlchemy)
*   **FastAPI**: A high-performance ASGI framework that provides lightning-fast request handling and automatic OpenAPI documentation.
*   **SQLAlchemy 2.0**: Utilizing the latest ORM features for clean, expressive database queries and robust relationship mapping.
*   **Neon Serverless Postgres**: The production database layer, offering scalable, low-latency storage with instant branching.
*   **Alembic**: Manages database migrations, ensuring the schema evolves seamlessly without data loss.
*   **JWT Authentication**: Secure, stateless session management using JSON Web Tokens stored in **HTTP-Only Cookies** to prevent XSS attacks.

### 🎨 Frontend: The Experience (Vanilla JS & CSS3)
*   **Vanilla CSS (Antigravity Design System)**: A custom-built design system leveraging CSS Variables, Flexbox, and CSS Grid for maximum flexibility without the bloat of frameworks like Tailwind.
*   **Chart.js**: Integrated for interactive, responsive data visualizations including Daily Trends and Category Distributions.
*   **Jinja2 Templating**: Powerful server-side rendering that allows for dynamic, SEO-friendly HTML generation with zero client-side lag.

---

## 🏗 3. System Architecture & Workflow

The application follows a **Modular Monolith** pattern with a clear separation of concerns.

### 🔐 Secure Authentication Flow
1.  **Registration**: Passwords are cryptographically hashed using **Bcrypt** before storage.
2.  **Stateless Sessions**: On login, the server issues a JWT.
3.  **Security Measures**: The token is stored as an `samesite=lax`, `secure` (in production) cookie, protecting against CSRF and ensuring consistent redirects.

### 📊 Data Analysis Lifecycle
1.  **Input**: Users log entries via a custom **Category Picker** that allows for inline category creation without page reloads.
2.  **Persistence**: Data is saved to Postgres (Production) or SQLite (Local) with strict Foreign Key constraints.
3.  **Aggregation**: Backend routes perform real-time aggregations (Sum, Group By) for the requested month/year.
4.  **Rendering**: Aggregated metrics are injected into Jinja2 templates and rendered as interactive charts.

---

## 📱 4. Responsive Engineering (Realme C75 Optimization)
We have implemented a tiered breakpoint system to ensure pixel-perfect rendering across all viewports:
*   **Desktop (1200px+)**: Multi-column grid with full side-by-side analytics.
*   **Tablet (768px)**: Optimized stacking for metric cards and simplified navigation.
*   **Standard Mobile (480px)**: Compact layouts with touch-friendly tap targets.
*   **Specialized Mobile (412px)**: Custom fine-tuning for devices like the **Realme C75**, featuring full-width stacked headers and responsive chart height adjustments.

---

## 🗄 5. Database Relationship Model
The database schema is designed for high integrity and extensibility:
*   **Users**: Central authority for all data.
*   **Categories**: Two-tier system—**Global Defaults** (System-wide) and **User-Specific Custom Categories**.
*   **Expenses & Incomes**: Atomic transactions linked to both a User and a Category, supporting notes and specific timestamps.

---

## ⚙️ 6. Getting Started (Local Development)

### Prerequisites
*   Python 3.10+
*   Virtual Environment (`venv`)

### Installation
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/dhanesh-vaishnav96/Expense_Tracker_System.git
    cd Expense_Tracker_System
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Setup**:
    Create a `.env` file in the root:
    ```env
    SECRET_KEY=your_super_secret_key
    DATABASE_URL=sqlite:///./test.db
    ```
4.  **Run the Application**:
    ```bash
    uvicorn backend.main:app --reload
    ```
    Access at: `http://localhost:8000`

---

## ✅ 7. Key Features
*   ✅ **Real-time Balance Tracking**: Instant calculation of total wealth across all logged income and expenses.
*   ✅ **Monthly Filters**: Drill down into specific months and years to see historical trends.
*   ✅ **Interactive Charts**: Hoverable data points for daily spending and category breakdowns.
*   ✅ **Custom Category Management**: Add, Edit, or Delete categories directly within the entry form.
*   ✅ **Glassmorphic UI**: A state-of-the-art visual theme designed for dark mode enthusiasts.

---

## 🤝 Conclusion
The **Antigravity Expense Tracker** represents a fusion of robust backend engineering and artistic frontend design. It serves as a benchmark for how modern financial tools should feel: fast, intuitive, and visually empowering.
