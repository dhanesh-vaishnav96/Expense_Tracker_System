# 💰 Expense Tracker with Antigravity Visualization

## 📌 Project Overview

The **Expense Tracker** is a full-stack web application built using **Python (FastAPI), HTML, CSS, and JavaScript**, designed to help users efficiently track, analyze, and manage their daily expenses in **Indian Rupees (₹)**.

This project introduces a unique **"Antigravity UI Concept"**, where financial trends are visually represented using dynamic, floating chart animations that create a modern and engaging dashboard experience.

Users can:

* Add daily expenses with categories
* Track monthly spending trends
* Analyze savings vs expenses
* Manage and edit entry history
* View global and month-wise analytics

---

## 🎯 Objectives

* Track daily expenses with date and category
* Provide clear financial insights via dashboards (Month-wise)
* Compare monthly and total spending patterns
* Enable secure JWT-based authentication
* Deliver a visually modern UI using Antigravity concepts

---

## 🧠 Core Features

### 🔐 Authentication System

* User Signup & Login
* JWT-based authentication
* Secure password hashing

---

### 💸 Expense Management (Dedicated Entries View)

* Add expense with:
  * Amount (₹ INR)
  * Category
  * Date
  * Notes (optional)
* Edit expense entry
* Delete incorrect entries
* History table with all entries

---

### 📊 Dashboard (Antigravity UI)

#### 🟢 Key Metrics
* Total Balance (Global Income - Total Expense)
* Total Expense (Global)
* This Month Expense (Selected Month)

#### 📉 Analytics
* **Line Chart (Daily Trend)**
  * Shows daily expenses for specifically selected month
* **Bar Graph (Monthly Comparison)**
  * Global comparison of monthly spending totals

#### ✨ Global Controls
* Month selector to filter dashboard data
* Income updater to set starting budget/balance

---

### 🗂 Category Management

* Add new categories dynamically
* Manage global categories

---

## 🛠 Tech Stack

### Backend
* Python
* FastAPI
* SQLite (SQLAlchemy ORM)
* JWT Authentication

### Frontend
* HTML5
* CSS3
* JavaScript (Vanilla JS)
* Chart.js (for analytics)

---

## 🗄 Database Design

### Users Table
| Field        | Type      |
| ------------ | --------- |
| id           | Integer   |
| name         | String    |
| email        | String    |
| password     | String    |
| total_income | Float     |
| created_at   | Timestamp |

### Expenses Table
| Field       | Type         |
| ----------- | ------------ |
| id          | Integer      |
| user_id     | Integer (FK) |
| amount      | Float        |
| category_id | Integer (FK) |
| date        | Date         |
| note        | Text         |
| created_at  | Timestamp    |

---

## 🔄 Workflow

1. User registers/logs in
2. Navigates to **Entries** to add/edit/delete daily expenses
3. **Dashboard** fetches aggregated data based on month selection
4. Visualizations render specifically for selected range

---

## ✅ Conclusion

This project is a **production-ready Expense Tracker** that combines strong backend architecture with a clean, modern UI and advanced analytics.
