import sqlite3
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import *

class connect_db:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connector = sqlite3.connect(self.db_name)
        self.cursor = self.connector.cursor()

    def execute_sql(self, sql_txt):
        try:
            self.sql_txt = sql_txt
            return self.cursor.execute(self.sql_txt)
        except:
            messagebox.showerror('Ошибка!', 'Невозможно получить данные')

    def close_db(self):
        self.connector.commit()
        self.cursor.close()
        self.connector.close()

class AuthWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Авторизация")
        self.root.geometry("300x200")

        self.style = Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 12))
        self.style.configure('TButton', font=('Arial', 12), padding=6)
        self.style.configure('TEntry', font=('Arial', 12), padding=6)

        self.create_database()
        self.create_widgets()

    def create_database(self):
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')

        # Добавление столбца genre, если он отсутствует
        cursor.execute('PRAGMA table_info(books)')
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        if 'genre' not in column_names:
            cursor.execute('ALTER TABLE books ADD COLUMN genre TEXT')

        # Добавление книг в базу данных
        cursor.execute('''
            INSERT INTO books (title, author, genre, price)
            VALUES
            ('1984', 'George Orwell', 'Dystopian', 10.99),
            ('To Kill a Mockingbird', 'Harper Lee', 'Fiction', 8.99),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 'Classic', 7.99),
            ('The Catcher in the Rye', 'J.D. Salinger', 'Fiction', 6.99),
            ('Moby-Dick', 'Herman Melville', 'Adventure', 12.99)
        ''')
        conn.commit()
        conn.close()

    def create_widgets(self):
        self.frame = Frame(self.root, padding="10 10 10 10")
        self.frame.pack(fill=BOTH, expand=True)

        self.lb_username = Label(self.frame, text='Имя пользователя:')
        self.lb_username.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        self.entry_username = Entry(self.frame, width=25)
        self.entry_username.grid(row=0, column=1, padx=10, pady=10)

        self.lb_password = Label(self.frame, text='Пароль:')
        self.lb_password.grid(row=1, column=0, padx=10, pady=10, sticky=W)
        self.entry_password = Entry(self.frame, show='*', width=25)
        self.entry_password.grid(row=1, column=1, padx=10, pady=10)

        self.btn_register = Button(self.frame, text='Регистрация', command=self.register_user)
        self.btn_register.grid(row=2, column=0, padx=10, pady=10, sticky=E+W)

        self.btn_login = Button(self.frame, text='Войти', command=self.login_user)
        self.btn_login.grid(row=2, column=1, padx=10, pady=10, sticky=E+W)

    def register_user(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if username and password:
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                messagebox.showinfo("Success", "Registration successful!")
                self.open_library_window(username)
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists!")
            conn.close()
        else:
            messagebox.showerror("Error", "Please enter both username and password!")

    def login_user(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if username and password:
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                messagebox.showinfo("Success", "Login successful!")
                self.open_library_window(username)
            else:
                messagebox.showerror("Error", "Invalid username or password!")
        else:
            messagebox.showerror("Error", "Please enter both username and password!")

    def open_library_window(self, username):
        self.root.destroy()
        library_window = Tk()
        library_app = LibraryWindow(library_window, username)
        library_app.mainloop()

class LibraryWindow:
    def __init__(self, root, username):
        self.root = root
        self.root.title("Виртуальная библиотека")
        self.root.geometry("1000x600")
        self.username = username

        self.style = Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 12))
        self.style.configure('TButton', font=('Arial', 12), padding=6)
        self.style.configure('TEntry', font=('Arial', 12), padding=6)
        self.style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))
        self.style.configure('Treeview', font=('Arial', 12))

        self.create_widgets()
        self.load_books()

    def create_widgets(self):
        self.search_frame = Frame(self.root, padding="10 10 10 10")
        self.search_frame.pack(fill=X, expand=False)

        self.lb_search = Label(self.search_frame, text='Поиск:')
        self.lb_search.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        self.entry_search = Entry(self.search_frame, width=30)
        self.entry_search.grid(row=0, column=1, padx=10, pady=10)
        self.btn_search = Button(self.search_frame, text='Найти', command=self.search_books)
        self.btn_search.grid(row=0, column=2, padx=10, pady=10)

        self.filter_frame = Frame(self.root, padding="10 10 10 10")
        self.filter_frame.pack(fill=X, expand=False)

        self.lb_genre = Label(self.filter_frame, text='Жанр:')
        self.lb_genre.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        self.genre_var = StringVar()
        self.genre_combobox = Combobox(self.filter_frame, textvariable=self.genre_var, width=20)
        self.genre_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.genre_combobox['values'] = self.get_genres()

        self.btn_filter = Button(self.filter_frame, text='Фильтр', command=self.filter_books)
        self.btn_filter.grid(row=0, column=2, padx=10, pady=10)

        self.book_frame = Frame(self.root, padding="10 10 10 10")
        self.book_frame.pack(fill=BOTH, expand=True)

        self.book_tree = Treeview(self.book_frame, columns=('Title', 'Author', 'Genre', 'Price'), show='headings')
        self.book_tree.heading('Title', text='Название')
        self.book_tree.heading('Author', text='Автор')
        self.book_tree.heading('Genre', text='Жанр')
        self.book_tree.heading('Price', text='Цена')
        self.book_tree.column('Title', width=200)
        self.book_tree.column('Author', width=200)
        self.book_tree.column('Genre', width=100)
        self.book_tree.column('Price', width=100)
        self.book_tree.pack(side=LEFT, fill=BOTH, expand=True)

        self.book_scrollbar = Scrollbar(self.book_frame, orient=VERTICAL, command=self.book_tree.yview)
        self.book_tree.configure(yscroll=self.book_scrollbar.set)
        self.book_scrollbar.pack(side=RIGHT, fill=Y)

        self.btn_add_to_cart = Button(self.book_frame, text='Добавить в корзину', command=self.add_to_cart)
        self.btn_add_to_cart.pack(pady=10)

        self.cart_frame = Frame(self.root, padding="10 10 10 10")
        self.cart_frame.pack(fill=BOTH, expand=True)

        self.cart_tree = Treeview(self.cart_frame, columns=('Title', 'Author', 'Price'), show='headings')
        self.cart_tree.heading('Title', text='Название')
        self.cart_tree.heading('Author', text='Автор')
        self.cart_tree.heading('Price', text='Цена')
        self.cart_tree.column('Title', width=200)
        self.cart_tree.column('Author', width=200)
        self.cart_tree.column('Price', width=100)
        self.cart_tree.pack(side=LEFT, fill=BOTH, expand=True)

        self.cart_scrollbar = Scrollbar(self.cart_frame, orient=VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscroll=self.cart_scrollbar.set)
        self.cart_scrollbar.pack(side=RIGHT, fill=Y)

        self.btn_remove_from_cart = Button(self.cart_frame, text='Удалить из корзины', command=self.remove_from_cart)
        self.btn_remove_from_cart.pack(pady=10)

        self.btn_purchase = Button(self.cart_frame, text='Купить', command=self.purchase)
        self.btn_purchase.pack(pady=10)

    def get_genres(self):
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT genre FROM books')
        genres = cursor.fetchall()
        conn.close()
        return [genre[0] for genre in genres]

    def load_books(self):
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books')
        books = cursor.fetchall()
        conn.close()

        for book in books:
            self.book_tree.insert('', 'end', values=(book[1], book[2], book[3], book[4]))

        self.load_cart()

    def search_books(self):
        query = self.entry_search.get().lower()
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ?', ('%' + query + '%', '%' + query + '%'))
        books = cursor.fetchall()
        conn.close()

        self.book_tree.delete(*self.book_tree.get_children())
        for book in books:
            self.book_tree.insert('', 'end', values=(book[1], book[2], book[3], book[4]))

    def filter_books(self):
        genre = self.genre_var.get()
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        query = 'SELECT * FROM books WHERE 1=1'
        params = []
        if genre:
            query += ' AND genre = ?'
            params.append(genre)
        cursor.execute(query, params)
        books = cursor.fetchall()
        conn.close()

        self.book_tree.delete(*self.book_tree.get_children())
        for book in books:
            self.book_tree.insert('', 'end', values=(book[1], book[2], book[3], book[4]))

    def add_to_cart(self):
        selected_item = self.book_tree.selection()
        if selected_item:
            book_title = self.book_tree.item(selected_item)['values'][0]
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', (self.username,))
            user_id = cursor.fetchone()[0]
            cursor.execute('SELECT id FROM books WHERE title = ?', (book_title,))
            book_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO cart (user_id, book_id) VALUES (?, ?)', (user_id, book_id))
            conn.commit()
            conn.close()
            self.load_cart()
        else:
            messagebox.showerror("Error", "Please select a book to add to the cart!")

    def load_cart(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (self.username,))
        user_id = cursor.fetchone()[0]
        cursor.execute('''
            SELECT books.title, books.author, books.price
            FROM cart
            JOIN books ON cart.book_id = books.id
            WHERE cart.user_id = ?
        ''', (user_id,))
        cart_items = cursor.fetchall()
        conn.close()

        for item in cart_items:
            self.cart_tree.insert('', 'end', values=item)

    def remove_from_cart(self):
        selected_item = self.cart_tree.selection()
        if selected_item:
            book_title = self.cart_tree.item(selected_item)['values'][0]
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', (self.username,))
            user_id = cursor.fetchone()[0]
            cursor.execute('''
                DELETE FROM cart
                WHERE user_id = ? AND book_id = (SELECT id FROM books WHERE title = ?)
            ''', (user_id, book_title))
            conn.commit()
            conn.close()
            self.load_cart()
        else:
            messagebox.showerror("Error", "Please select a book to remove from the cart!")

    def purchase(self):
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (self.username,))
        user_id = cursor.fetchone()[0]
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        self.load_cart()
        messagebox.showinfo("Success", "Purchase successful!")

if __name__ == "__main__":
    root = Tk()
    auth_app = AuthWindow(root)
    root.mainloop()
