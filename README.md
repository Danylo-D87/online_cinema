# Online Cinema Backend

## 🎬 Project Description

This project is the backend service for an "Online Cinema" application, built using FastAPI. It provides a robust and scalable API for managing movies, user authentication, favorite movies, user reviews, and more. The goal is to offer a comprehensive set of functionalities required for a modern online streaming platform.

## ✨ Features

* **User Authentication & Authorization:** Secure user registration, login (JWT-based), and role-based access control.
* **Movie Management:** CRUD operations for movies, including details like title, description, release date, rating, poster URL, trailer URL, and genres.
* **Genre Management:** Define and manage movie genres.
* **Favorite Movies:** Users can add and remove movies from their personal favorites list.
* **Search & Filtering:** Functionality to search for movies and filter them by various criteria (e.g., genre, title).
* **Admin Panel (future consideration/manual access):** Tools for administrators to manage content and users.
* **Scalable Architecture:** Designed with FastAPI and SQLAlchemy (Async ORM) for asynchronous operations and performance.
* **User Reviews & Ratings:**


## 🚀 Technologies Used

* **Python:** The core programming language.
* **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
* **SQLAlchemy:** The Python SQL toolkit and Object Relational Mapper (ORM) for interacting with the database.
* **Alembic:** Lightweight database migration tool for SQLAlchemy.
* **PostgreSQL:** The primary relational database for storing application data.
* **Pydantic:** Data validation and settings management using Python type hints.
* **PyJWT:** JSON Web Token implementation for Python for secure authentication.
* **Passlib:** Cryptographic hashing framework for password security.
* **python-multipart:** For handling form data and file uploads.
* **uvicorn:** ASGI server for running the FastAPI application.
* **pytest:** Testing framework for writing and running unit and integration tests.
