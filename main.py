from library_system import LibrarySystem


def main():
    """Main function to demonstrate the library system usage."""
    library = LibrarySystem()
    try:
        while True:
            print("\nLibrary Management System")
            print("1. Add Books")
            print("2. Add Students")
            print("3. Search Books")
            print("4. Issue Book")
            print("5. Return Book")
            print("6. View Member's Books")
            print("7. See All Books")
            print("8. Exit")
            choice = input("\nEnter your choice (1-8): ")

            if choice == '1':
                books = []
                while True:
                    print("\nEnter book details (press Enter without title to finish):")
                    title = input("Enter book title: ").strip()
                    if not title:
                        break

                    author = input("Enter author name: ").strip()
                    isbn = input("Enter ISBN: ").strip()
                    try:
                        quantity = int(input("Enter quantity: "))
                        if quantity <= 0:
                            print("Quantity must be positive!")
                            continue

                        books.append({
                            'title': title,
                            'author': author,
                            'isbn': isbn,
                            'quantity': quantity
                        })
                        print("Book added to batch. Add another book or press Enter at title to finish.")
                    except ValueError:
                        print("Please enter a valid number for quantity!")

                if books:
                    if library.add_books(books):
                        print(f"\nSuccessfully added {len(books)} books to the library!")
                    else:
                        print("\nFailed to add books. Please try again.")

            elif choice == '2':
                students = []
                while True:
                    print("\nEnter student details (press Enter without ID to finish):")
                    sid = input("Enter student ID: ").strip()
                    if not sid:
                        break

                    fname = input("Enter first name: ").strip()
                    lname = input("Enter last name: ").strip()
                    department = input("Enter department: ").strip()
                    branch = input("Enter branch: ").strip()

                    if all([sid, fname, lname, department, branch]):
                        students.append({
                            'sid': sid,
                            'fname': fname,
                            'lname': lname,
                            'department': department,
                            'branch': branch
                        })
                        print("Student added to batch. Add another student or press Enter at ID to finish.")
                    else:
                        print("All fields are required! Please try again.")

                if students:
                    if library.add_students(students):
                        print(f"\nSuccessfully added {len(students)} students to the system!")
                    else:
                        print("\nFailed to add students. Please try again.")

            elif choice == '3':
                search_term = input("\nEnter search term (title, author, or ISBN): ").strip()
                if search_term:
                    results = library.search_books(search_term)
                    if results:
                        print("\nSearch Results:")
                        print("-" * 80)
                        print(f"{'ISBN':<15} {'Title':<30} {'Author':<20} {'Total':<8} {'Available':<8}")
                        print("-" * 80)
                        for book in results:
                            print(f"{book[0]:<15} {book[1][:28]:<30} {book[2][:18]:<20} {book[3]:<8} {book[4]:<8}")
                    else:
                        print("\nNo books found matching your search.")

            elif choice == '4':
                member_id = input("\nEnter student ID: ").strip()
                search_term = input("Enter book title or ISBN: ").strip()

                if member_id and search_term:
                    success, message = library.issue_book(member_id, search_term)
                    print("Student with given id not found")
                else:
                    print("\nBoth student ID and book information are required!")

            elif choice == '5':
                member_id = input("\nEnter student ID: ").strip()
                search_term = input("Enter book title or ISBN: ").strip()

                if member_id and search_term:
                    success, message, fine = library.return_book(member_id, search_term)
                    print(f"\n{message}")
                    if success and fine > 0:
                        print(f"Fine amount: Rs {fine:.2f}")
                else:
                    print("\nBoth student ID and book information are required!")


            elif choice == '6':

                member_id = input("\nEnter student ID: ").strip()

                if member_id:

                    books = library.get_member_books(member_id)

                    if books:

                        print("\nCurrently Borrowed Books:")

                        print("-" * 100)

                        print(f"{'Title':<30} {'Author':<20} {'Issue Date':<12} {'Due Date':<12} {'Current Fine':<12}")

                        print("-" * 100)

                        for book in books:
                            title = book[1][:28]

                            author = book[2][:18]

                            issue_date = book[3].strftime('%Y-%m-%d') if book[3] else "N/A"

                            due_date = book[4].strftime('%Y-%m-%d') if book[4] else "N/A"

                            fine = float(book[5]) if book[5] is not None else 0.0

                            print(f"{title:<30} {author:<20} {issue_date:<12} "

                                  f"{due_date:<12} Rs {fine:<10.2f}")

                    else:

                        print("\nNo books currently issued to this member.")

                else:

                    print("\nPlease enter a valid student ID!")

            elif choice == '7':
                books = library.get_all_books()
                if books:
                    print("\nAll Books in Library:")
                    print("-" * 80)
                    print(f"{'ISBN':<15} {'Title':<30} {'Author':<20} {'Total':<8} {'Available':<8}")
                    print("-" * 80)
                    for book in books:
                        print(f"{book[0]:<15} {book[1][:28]:<30} {book[2][:18]:<20} {book[3]:<8} {book[4]:<8}")
                else:
                    print("\nNo books available in the library.")

            elif choice == '8':
                print("\nThank you for using the Library Management System!")
                break

            else:
                print("\nInvalid choice! Please enter a number between 1 and 8.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        library.close()


if __name__ == "__main__":
    main()