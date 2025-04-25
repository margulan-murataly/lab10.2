import psycopg2
import csv
import sys

DB_PARAMS = {
    'host': 'localhost',
    'database': 'phonebook_db',
    'user': 'postgres',
    'password': ''
}

def create_database_if_not_exists():
    dbname = DB_PARAMS['database']
    conn = psycopg2.connect(
        dbname='postgres',
        user=DB_PARAMS['user'],
        password=DB_PARAMS['password'],
        host=DB_PARAMS['host']
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f"CREATE DATABASE {dbname} ENCODING 'UTF8'")
        print(f"Database '{dbname}' created with UTF8 encoding.")
    else:
        print(f"Database '{dbname}' already exists.")

    cur.close()
    conn.close()

def connect():
    return psycopg2.connect(**DB_PARAMS)

def create_table():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) UNIQUE NOT NULL
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Table 'phonebook' is ready.")

def insert_contact(full_name, phone):
    conn = connect()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO phonebook (full_name, phone) VALUES (%s, %s)",
            (full_name, phone)
        )
        conn.commit()
        print(f"Inserted {full_name} ({phone}).")
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print(f"Error inserting {phone}: {e}")
    finally:
        cur.close()
        conn.close()

def insert_from_csv(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:
                full_name, phone = row
                insert_contact(full_name.strip(), phone.strip())
            else:
                print(f"Skipping invalid row: {row}")

def insert_from_console():
    full_name = input("Full name: ").strip()
    phone = input("Phone number: ").strip()
    insert_contact(full_name, phone)

def update_full_name_by_phone(phone, new_full_name):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "UPDATE phonebook SET full_name = %s WHERE phone = %s",
        (new_full_name, phone)
    )
    conn.commit()
    print(f"Updated full name for phone {phone} to {new_full_name}.")
    cur.close()
    conn.close()

def update_phone_by_full_name(full_name, new_phone):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "UPDATE phonebook SET phone = %s WHERE full_name = %s",
        (new_phone, full_name)
    )
    conn.commit()
    print(f"Updated phone for {full_name} to {new_phone}.")
    cur.close()
    conn.close()

def query_all_contacts():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT full_name, phone FROM phonebook ORDER BY full_name")
    rows = cur.fetchall()
    print("No | Full Name           | Phone")
    print("-----------------------------------------")
    for i, (full_name, phone) in enumerate(rows, start=1):
        print(f"{i:<2} | {full_name:<20} | {phone}")
    cur.close()
    conn.close()

def query_by_name_pattern(name_pattern):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT full_name, phone FROM phonebook WHERE full_name ILIKE %s ORDER BY full_name",
        (name_pattern,)
    )
    rows = cur.fetchall()
    print("No | Full Name           | Phone")
    print("-----------------------------------------")
    for i, (full_name, phone) in enumerate(rows, start=1):
        print(f"{i:<2} | {full_name:<20} | {phone}")
    cur.close()
    conn.close()

def query_by_phone_pattern(phone_pattern):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT full_name, phone FROM phonebook WHERE phone LIKE %s ORDER BY phone",
        (phone_pattern,)
    )
    rows = cur.fetchall()
    print("No | Full Name           | Phone")
    print("-----------------------------------------")
    for i, (full_name, phone) in enumerate(rows, start=1):
        print(f"{i:<2} | {full_name:<20} | {phone}")
    cur.close()
    conn.close()

def delete_by_full_name(full_name):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM phonebook WHERE full_name = %s",
        (full_name,)
    )
    conn.commit()
    print(f"Deleted contact with full name: {full_name}.")
    cur.close()
    conn.close()

def delete_by_phone(phone):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM phonebook WHERE phone = %s",
        (phone,)
    )
    conn.commit()
    print(f"Deleted contact with phone: {phone}.")
    cur.close()
    conn.close()

def print_menu():
    print("\nPhoneBook Menu:")
    print("1. Create table")
    print("2. Insert from CSV file")
    print("3. Insert via console")
    print("4. Update full name by phone")
    print("5. Update phone by full name")
    print("6. Query all contacts")
    print("7. Query by full name pattern")
    print("8. Query by phone pattern")
    print("9. Delete by full name")
    print("10. Delete by phone")
    print("0. Exit")

def main():
    create_database_if_not_exists()
    create_table()
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == '1':
            create_table()
        elif choice == '2':
            path = input("CSV file path: ").strip()
            insert_from_csv(path)
        elif choice == '3':
            insert_from_console()
        elif choice == '4':
            phone = input("Phone number to identify record: ").strip()
            new_name = input("New full name: ").strip()
            update_full_name_by_phone(phone, new_name)
        elif choice == '5':
            name = input("Full name: ").strip()
            new_phone = input("New phone number: ").strip()
            update_phone_by_full_name(name, new_phone)
        elif choice == '6':
            query_all_contacts()
        elif choice == '7':
            pat = input("Full name pattern (use % for wildcard): ").strip()
            query_by_name_pattern(pat)
        elif choice == '8':
            pat = input("Phone pattern (use % for wildcard): ").strip()
            query_by_phone_pattern(pat)
        elif choice == '9':
            name = input("Full name: ").strip()
            delete_by_full_name(name)
        elif choice == '10':
            phone = input("Phone number: ").strip()
            delete_by_phone(phone)
        elif choice == '0':
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice, please try again.")

if __name__ == '__main__':
    main()