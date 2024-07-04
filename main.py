import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import datetime

class BudgetPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Planner")

        self.conn = sqlite3.connect("budget_planner.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        
        self.amount_label = tk.Label(root, text="Amount:")
        self.amount_label.grid(row=0, column=0, padx=10, pady=5)
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=0, column=1, padx=10, pady=5)

        self.category_label = tk.Label(root, text="Category:")
        self.category_label.grid(row=1, column=0, padx=10, pady=5)
        self.category_entry = tk.Entry(root)
        self.category_entry.grid(row=1, column=1, padx=10, pady=5)

        self.date_label = tk.Label(root, text="Date (YYYY-MM-DD):")
        self.date_label.grid(row=2, column=0, padx=10, pady=5)
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=2, column=1, padx=10, pady=5)

        self.description_label = tk.Label(root, text="Description:")
        self.description_label.grid(row=3, column=0, padx=10, pady=5)
        self.description_entry = tk.Entry(root)
        self.description_entry.grid(row=3, column=1, padx=10, pady=5)

        self.add_button = tk.Button(root, text="Add Entry", command=self.add_entry)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.view_button = tk.Button(root, text="View Entries", command=self.view_entries)
        self.view_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(root, columns=("Amount", "Category", "Date", "Description"), show="headings")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Description", text="Description")
        self.tree.grid(row=6, column=0, columnspan=2, pady=10, padx=10)

        self.summary_label = tk.Label(root, text="")
        self.summary_label.grid(row=7, column=0, columnspan=2, pady=10)

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY,
                amount REAL,
                category TEXT,
                date TEXT,
                description TEXT
            )
        """)
        self.conn.commit()

    def add_entry(self):
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        date = self.date_entry.get()
        description = self.description_entry.get()

        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date format", "Please enter date in YYYY-MM-DD format")
            return

        if not amount or not category or not date:
            messagebox.showerror("Missing information", "Please fill out all fields")
            return

        self.cursor.execute("INSERT INTO budget (amount, category, date, description) VALUES (?, ?, ?, ?)",
                            (amount, category, date, description))
        self.conn.commit()

        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

        self.view_entries()

    def view_entries(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        self.cursor.execute("SELECT * FROM budget")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", tk.END, values=(row[1], row[2], row[3], row[4]))

        self.show_summary()

    def show_summary(self):
        self.cursor.execute("SELECT SUM(amount) FROM budget WHERE amount > 0")
        total_income = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT SUM(amount) FROM budget WHERE amount < 0")
        total_expenses = self.cursor.fetchone()[0] or 0

        balance = total_income + total_expenses

        summary_text = f"Total Income: ${total_income:.2f} | Total Expenses: ${total_expenses:.2f} | Balance: ${balance:.2f}"
        self.summary_label.config(text=summary_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetPlanner(root)
    root.mainloop()
