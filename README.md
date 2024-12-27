# Library Management System

## Overview
The Library Management System is a console-based application designed to manage library operations efficiently. It allows administrators to add books, register students, issue and return books, and view library records. The application is backed by a PostgreSQL database for data persistence.

---

## Features
- **Book Management**: Add new books, update existing inventory, and view all books.
- **Student Management**: Register new students and maintain their details.
- **Book Issuing**: Issue books to students with due date tracking.
- **Book Returning**: Return books and calculate overdue fines if applicable.
- **Search**: Search books by title, author, or ISBN.
- **Member Records**: View the books currently borrowed by a specific student.
- **Database Integration**: Uses PostgreSQL for persistent data storage.

---

## Prerequisites
1. **Python**: Ensure Python 3.x is installed.
2. **PostgreSQL**: Set up a PostgreSQL database server.
3. **Python Libraries**: Install required libraries:
   - `psycopg2`
   - `datetime`

---

## Installation
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Set Up PostgreSQL Database**:
   - Create a new database named `general`.
   - Update the database credentials in the `LibrarySystem` class:
     ```python
     self.conn = psycopg2.connect(
         host="localhost",
         database="general",
         user="postgres",
         password="<your-password>",
         port=5432
     )
     ```

3. **Install Python Dependencies**:
   ```bash
   pip install psycopg2
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

---

## Usage
1. **Main Menu Options**:
   - **1. Add Books**: Enter book details like title, author, ISBN, and quantity.
   - **2. Add Students**: Register students by providing their ID, name, and department details.
   - **3. Search Books**: Search by title, author, or ISBN.
   - **4. Issue Book**: Issue a book to a student using their ID and book title/ISBN.
   - **5. Return Book**: Return a borrowed book and calculate fines if overdue.
   - **6. View Member's Books**: Display books currently issued to a specific student.
   - **7. See All Books**: List all books in the library.
   - **8. Exit**: Close the application.

2. **Error Handling**:
   - Invalid inputs are flagged with appropriate error messages.
   - Database connection issues are logged, and transactions are rolled back.

---

## Database Schema
### Tables:
1. **books**:
   - `isbn`: Primary key, unique identifier for books.
   - `title`: Book title.
   - `author`: Author's name.
   - `quantity`: Total number of copies.
   - `available`: Number of available copies.

2. **students**:
   - `sid`: Primary key, unique student ID.
   - `fname`: First name.
   - `lname`: Last name.
   - `department`: Department name.
   - `branch`: Branch name.

3. **transactions**:
   - `id`: Primary key, transaction ID.
   - `isbn`: Foreign key referencing books.
   - `member_id`: Foreign key referencing students.
   - `issue_date`: Date the book was issued.
   - `due_date`: Expected return date.
   - `return_date`: Actual return date.
   - `fine_amount`: Fine for overdue books.
   - `status`: Current status (`issued` or `returned`).

---

## Fine Calculation
- **Loan Period**: 30 days.
- **Fine Rate**: Rs 1.0 per day for overdue books.
- **Calculation**:
  ```
  fine = (current_date - due_date).days * fine_rate
  ```

---

## Limitations
- Maximum of 5 books can be borrowed by a student at a time.

---

## Acknowledgments
- PostgreSQL for database management.
- Python for the backend logic.

