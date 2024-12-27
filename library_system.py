import psycopg2
from datetime import datetime, timedelta
from typing import List, Tuple, Dict


class LibrarySystem:
    def __init__(self):
        self.LOAN_PERIOD_DAYS = 30
        self.MAX_BOOKS_PER_STUDENT = 5
        self.FINE_RATE = 1.0  # Rs per day
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                database="general",
                user="postgres",
                password="Ak@14267",
                port=5432
            )
            self.cursor = self.conn.cursor()
            self.setup_database()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to database: {error}")
            raise

    def setup_database(self):
        """Initialize database tables if they don't exist."""
        try:
            # Books table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS books(
                    isbn TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    available INTEGER NOT NULL
                )
            ''')

            # Students table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS students(
                    sid TEXT PRIMARY KEY,
                    fname TEXT NOT NULL,
                    lname TEXT NOT NULL,
                    department TEXT NOT NULL,
                    branch TEXT NOT NULL
                )
            ''')

            # Transactions table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions(
                    id SERIAL PRIMARY KEY,
                    isbn TEXT REFERENCES books(isbn),
                    member_id TEXT REFERENCES students(sid),
                    issue_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    return_date DATE,
                    fine_amount DECIMAL(10,2) DEFAULT 0.0,
                    status TEXT NOT NULL
                )
            ''')
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Error setting up database: {e}")
            self.conn.rollback()
            raise

    def add_books(self, books: List[Dict]) -> bool:
        """Add new books or update existing ones in the library."""
        try:
            for book in books:
                self.cursor.execute('''
                    INSERT INTO books (isbn, title, author, quantity, available)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (isbn)
                    DO UPDATE SET
                        quantity = books.quantity + %s,
                        available = books.available + %s
                ''', (
                    book['isbn'], book['title'], book['author'],
                    book['quantity'], book['quantity'],
                    book['quantity'], book['quantity']
                ))
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error adding books: {e}")
            self.conn.rollback()
            return False

    def add_students(self, students: List[Dict]) -> bool:
        """Register new students in the library system."""
        try:
            for student in students:
                self.cursor.execute('''
                    INSERT INTO students(sid, fname, lname, department, branch)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    student['sid'], student['fname'], student['lname'],
                    student['department'], student['branch']
                ))
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error adding students: {e}")
            self.conn.rollback()
            return False

    def get_all_books(self) -> List[Tuple]:
        """Retrieve all books from the library."""
        try:
            self.cursor.execute('''
                SELECT isbn, title, author, quantity, available
                FROM books
            ''')
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error retrieving all books: {e}")
            return []

    def has_outstanding_loan(self, member_id: str, isbn: str) -> bool:
        """Check if a member already has an unreturned loan for a specific book."""
        try:
            self.cursor.execute('''
                SELECT COUNT(*) 
                FROM transactions 
                WHERE member_id = %s AND isbn = %s AND status = 'issued'
            ''', (member_id, isbn))
            return self.cursor.fetchone()[0] > 0
        except psycopg2.Error as e:
            print(f"Error checking outstanding loan: {e}")
            return False

    def issue_book(self, member_id: str, search_term: str) -> Tuple[bool, str]:
        """Issue a book to a member using either ISBN or title."""
        try:
            # Check if student has reached maximum limit
            current_count = self.get_current_borrowed_count(member_id)
            if current_count >= self.MAX_BOOKS_PER_STUDENT:
                return False, f"Cannot issue book. Maximum limit of {self.MAX_BOOKS_PER_STUDENT} books reached."

            # Search for book by ISBN or title
            self.cursor.execute('''
                SELECT isbn, title, available 
                FROM books 
                WHERE isbn = %s OR title ILIKE %s
            ''', (search_term, f'%{search_term}%'))

            result = self.cursor.fetchone()
            if not result:
                return False, "Book not found"

            isbn, title, available = result
            if available <= 0:
                return False, f"Book '{title}' is not available"

            # Check if member already has this book issued
            if self.has_outstanding_loan(member_id, isbn):
                return False, f"Cannot issue book '{title}'. You already have this book issued and not returned."

            # Issue the book
            issue_date = datetime.now().date()
            due_date = issue_date + timedelta(days=self.LOAN_PERIOD_DAYS)

            self.cursor.execute('BEGIN')

            # Update book availability
            self.cursor.execute('''
                UPDATE books 
                SET available = available - 1 
                WHERE isbn = %s
            ''', (isbn,))

            # Create transaction record
            self.cursor.execute('''
                INSERT INTO transactions 
                (isbn, member_id, issue_date, due_date, status)
                VALUES (%s, %s, %s, %s, 'issued')
            ''', (isbn, member_id, issue_date, due_date))

            self.conn.commit()
            return True, f"Book '{title}' issued successfully. Due date: {due_date}"

        except psycopg2.Error as e:
            #print(f"Error issuing book: {e}")
            self.conn.rollback()
            return False, "Database error occurred"

    def get_current_borrowed_count(self, member_id: str) -> int:
        """Get the number of books currently borrowed by a member."""
        try:
            self.cursor.execute('''
                SELECT COUNT(*)
                FROM transactions
                WHERE member_id = %s AND status = 'issued'
            ''', (member_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except psycopg2.Error as e:
            print(f"Error getting borrowed count: {e}")
            return 0

    def return_book(self, member_id: str, search_term: str) -> Tuple[bool, str, float]:
        """Return a book and calculate any applicable fines."""
        try:
            # Find the transaction
            self.cursor.execute('''
                SELECT t.id, t.due_date, b.title, t.isbn
                FROM transactions t
                JOIN books b ON t.isbn = b.isbn
                WHERE t.member_id = %s 
                AND (b.isbn = %s OR b.title ILIKE %s)
                AND t.status = 'issued'
            ''', (member_id, search_term, f'%{search_term}%'))

            result = self.cursor.fetchone()
            if not result:
                return False, "No such book issued to member", 0.0

            transaction_id, due_date, title, isbn = result
            return_date = datetime.now().date()

            # Calculate fine if book is overdue
            fine_amount = 0.0
            if return_date > due_date:
                days_overdue = (return_date - due_date).days
                fine_amount = days_overdue * self.FINE_RATE

            self.cursor.execute('BEGIN')

            # Update book availability
            self.cursor.execute('''
                UPDATE books 
                SET available = available + 1 
                WHERE isbn = %s
            ''', (isbn,))

            # Update transaction record
            self.cursor.execute('''
                UPDATE transactions 
                SET return_date = %s,
                    status = 'returned',
                    fine_amount = %s
                WHERE id = %s
            ''', (return_date, fine_amount, transaction_id))

            self.conn.commit()
            return True, f"Book '{title}' returned successfully", fine_amount

        except psycopg2.Error as e:
            print(f"Error returning book: {e}")
            self.conn.rollback()
            return False, "Database error occurred", 0.0

    def get_member_books(self, member_id: str) -> List[Tuple]:
        """Get all books currently issued to a member with current fine calculations."""
        try:
            self.cursor.execute('''
                SELECT b.isbn, b.title, b.author, 
                       t.issue_date, t.due_date,
                       CASE 
                           WHEN CURRENT_DATE > t.due_date THEN 
                               (CURRENT_DATE - t.due_date) * %s
                           ELSE 0 
                       END as current_fine
                FROM books b
                JOIN transactions t ON b.isbn = t.isbn
                WHERE t.member_id = %s AND t.status = 'issued'
            ''', (self.FINE_RATE, member_id))
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error getting member books: {e}")
            return []

    def display_member_books(self, member_id: str):
        books = self.get_member_books(member_id)

        if not books:
            print("No books currently issued to this member.")
            return

        print("\nCurrently Borrowed Books:")
        print("-" * 100)
        print(f"{'Title':<30} {'Author':<20} {'Issue Date':<12} {'Due Date':<12} {'Current Fine':<12}")
        print("-" * 100)

        for book in books:
            title, author, issue_date, due_date, fine = book[1], book[2], book[3], book[4], book[5]

            # Convert string dates to formatted strings
            issue_date_str = issue_date.strftime('%Y-%m-%d') if issue_date else "N/A"
            due_date_str = due_date.strftime('%Y-%m-%d') if due_date else "N/A"

            print(f"{title[:28]:<30} {author[:18]:<20} {issue_date_str:<12} "
                  f"{due_date_str:<12} Rs {float(fine):.2f}")

    def search_books(self, term: str) -> List[Tuple]:
        """Search for books by title, author, or ISBN."""
        try:
            self.cursor.execute('''
                SELECT isbn, title, author, quantity, available
                FROM books 
                WHERE title ILIKE %s 
                OR author ILIKE %s 
                OR isbn ILIKE %s
            ''', (f'%{term}%', f'%{term}%', f'%{term}%'))
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error searching books: {e}")
            return []



    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")
