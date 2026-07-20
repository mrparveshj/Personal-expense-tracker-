from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import mysql.connector 


username = "parvesh"
password = "810607"

top = Tk()
top.title("Personal Expenses Tracker")
top.geometry("1366x786")
top.configure(bg="red")

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="trayaldetails"
    )
def setup_expenses_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date VARCHAR(20),
            purpose VARCHAR(100),
            category VARCHAR(50),
            amount FLOAT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

setup_expenses_table()

expense_id = 1
total_expense = 0
total_entries = 0

LOGIN_IMAGE_PATH = r"C:\Users\mrpar\OneDrive\Desktop\b3da90ee-cec3-4798-b9f3-11fb529009e0.jpg"

SECOND_PAGE_IMAGE_PATH = r"C:\Users\mrpar\OneDrive\Desktop\3475053.jpg"

def add_expense():

    global expense_id
    global total_expense
    global total_entries

    date = date_entry.get()
    purpose = purpose_entry.get()
    amount = amount_entry.get()

    if date == "" or purpose == "" or amount == "":
        messagebox.showerror("Error", "Please fill all fields")
        return

    try:
        amount_value = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a valid number")
        return
    
    
    display_id = len(expense_table.get_children()) + 1

    expense_table.insert(
        "",
        "end",
        iid=expense_id,
        values=(display_id, date, purpose, category.get(), amount_value)
    )
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (date, purpose, category, amount) VALUES (%s, %s, %s, %s)",
        (date, purpose, category.get(), amount_value)
    )
    conn.commit()
    cursor.close()
    conn.close()

    expense_id += 1
    total_expense += amount_value
    total_entries += 1

    total_label.config(text=f"💰 Total Expense : ₹{total_expense}")
    entries_label.config(text=f"📋 Total Entries : {total_entries}")

    clear_fields()

    messagebox.showinfo("Success", "Expense Added Successfully!")


def clear_fields():

    date_entry.delete(0, END)
    purpose_entry.delete(0, END)
    amount_entry.delete(0, END)

    category.set("Food")


def renumber_table():
    rows = expense_table.get_children()
    for index, item_id in enumerate(rows, start=1):
        values = list(expense_table.item(item_id, "values"))
        values[0] = index
        expense_table.item(item_id, values=values)

def load_selected_row(event):
    # ✅ User table-la oru row click pannumbothu idhu run aagும்
    # andha row-oda data Entry boxes-la fill aagும், user edit panna easy-a
    selected_items = expense_table.selection()
    if not selected_items:
        return

    item_id = selected_items[0]
    row_values = expense_table.item(item_id, "values")

    date_entry.delete(0, END)
    date_entry.insert(0, row_values[1])

    purpose_entry.delete(0, END)
    purpose_entry.insert(0, row_values[2])

    category.set(row_values[3])

    amount_entry.delete(0, END)
    amount_entry.insert(0, row_values[4])


def edit_expense():

    global total_expense

    selected_items = expense_table.selection()

    if not selected_items:
        messagebox.showwarning("No Selection", "Please click a row first to select it")
        return

    item_id = selected_items[0]
    old_values = expense_table.item(item_id, "values")
    old_amount = float(old_values[4])

    date = date_entry.get()
    purpose = purpose_entry.get()
    amount = amount_entry.get()

    if date == "" or purpose == "" or amount == "":
        messagebox.showerror("Error", "Please fill all fields")
        return

    try:
        amount_value = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a valid number")
        return
    
    display_id = old_values[0]
    expense_table.item(item_id, values=(display_id, date, purpose, category.get(), amount_value))

    total_expense = total_expense - old_amount + amount_value
    total_label.config(text=f"💰 Total Expense : ₹{total_expense}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE expenses SET date=%s, purpose=%s, category=%s, amount=%s WHERE date=%s AND purpose=%s AND amount=%s",
            (date, purpose, category.get(), amount_value, old_values[1], old_values[2], old_amount)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as db_error:
        messagebox.showerror("Database Error", f"Could not update database:\n{db_error}")
        return

    clear_fields()
    messagebox.showinfo("Success", "Expense Updated Successfully!")

def delete_expense():

    global total_expense
    global total_entries

    selected_items = expense_table.selection()

    if not selected_items:
        messagebox.showwarning("No Selection", "Please click a row first to select it")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Delete the selected expense(s)?")
    if not confirm:
        return

    for item_id in selected_items:
        row_values = expense_table.item(item_id, "values")
        amount_to_remove = float(row_values[4])

        total_expense -= amount_to_remove
        total_entries -= 1

        expense_table.delete(item_id)

    renumber_table()

    total_label.config(text=f"💰 Total Expense : ₹{total_expense}")
    entries_label.config(text=f"📋 Total Entries : {total_entries}")

    messagebox.showinfo("Deleted", "Selected expense(s) deleted successfully")


def show_second_page():

    global date_entry
    global purpose_entry
    global amount_entry
    global category
    global total_label
    global entries_label
    global expense_table

    for widget in top.winfo_children():
        widget.destroy()

    try:
        bg_image_raw = Image.open(SECOND_PAGE_IMAGE_PATH)
        bg_image_resized = bg_image_raw.resize((1366, 786))
        photo = ImageTk.PhotoImage(bg_image_resized)

        bg_label = Label(top, image=photo)
        bg_label.image = photo
        bg_label.place(x=0, y=0)
    except Exception:
        top.configure(bg="lightcoral")

    main_frame = Frame(top, bg="ivory", highlightbackground="darkblue",
                        highlightthickness=2)
    main_frame.place(x=60, y=20, width=1246, height=746)

    Label(
        main_frame,
        text="💰 PERSONAL EXPENSE TRACKER",
        font=("Arial", 20, "bold"),
        bg="ivory",
        fg="darkblue"
    ).place(x=290, y=15)

    Label(main_frame, text="📅 Date (DD-MM-YYYY)", font=("Arial", 12, "bold"),
          bg="ivory").place(x=40, y=70)

    date_entry = Entry(main_frame, width=25)
    date_entry.insert(0, "09-06-2026")
    date_entry.place(x=240, y=72)

    Label(main_frame, text="📝 Purpose", font=("Arial", 12, "bold"),
          bg="ivory").place(x=40, y=110)

    purpose_entry = Entry(main_frame, width=30)
    purpose_entry.place(x=240, y=112)

    Label(main_frame, text="📂 Category", font=("Arial", 12, "bold"),
          bg="ivory").place(x=40, y=150)

    category = StringVar()
    category.set("Food")

    OptionMenu(
        main_frame, category,
        "Food", "Travel", "Shopping", "Bills", "Education", "Entertainment", "Others"
    ).place(x=240, y=145)
    
    Label(main_frame, text="💵 Amount (₹)", font=("Arial", 12, "bold"),
          bg="ivory").place(x=40, y=190)

    amount_entry = Entry(main_frame, width=25)
    amount_entry.place(x=240, y=192)

    Button(main_frame, text="➕ Add Expense", bg="green", fg="white",
           width=15, command=add_expense).place(x=600, y=70)

    Button(main_frame, text="🧹 Clear", bg="orange", fg="white",
           width=15, command=clear_fields).place(x=780, y=70)

    Button(main_frame, text="🗑 Delete Selected", bg="red", fg="white",
           width=18, command=delete_expense).place(x=600, y=115)

    Button(main_frame, text="🚪 Logout", bg="black", fg="white",
           width=15, command=show_login_page).place(x=780, y=115)
    
    Button(main_frame, text="✏️ Edit", bg="blue", fg="white",
           width=15, command=edit_expense).place(x=960, y=115)
    
    Label(main_frame, text="Expense Records", font=("Arial", 14, "bold"),
          bg="ivory").place(x=40, y=250)

    columns = ("ID", "Date", "Purpose", "Category", "Amount")

    expense_table = ttk.Treeview(
        main_frame,
        columns=columns,
        show="headings",
        height=12
    )

    expense_table.heading("ID", text="ID")
    expense_table.heading("Date", text="Date")
    expense_table.heading("Purpose", text="Purpose")
    expense_table.heading("Category", text="Category")
    expense_table.heading("Amount", text="Amount (₹)")

    expense_table.column("ID", width=50, anchor="center")
    expense_table.column("Date", width=140, anchor="center")
    expense_table.column("Purpose", width=280, anchor="w")
    expense_table.column("Category", width=150, anchor="center")
    expense_table.column("Amount", width=120, anchor="center")

    expense_table.place(x=40, y=290, width=1160, height=280)
    expense_table.bind("<<TreeviewSelect>>", load_selected_row)

    total_label = Label(main_frame, text="💰 Total Expense : ₹0",
                         font=("Arial", 13, "bold"), bg="ivory", fg="red")
    total_label.place(x=40, y=600)

    entries_label = Label(main_frame, text="📋 Total Entries : 0",
                           font=("Arial", 13, "bold"), bg="ivory", fg="blue")
    entries_label.place(x=40, y=635)


def data():
    entered_name = e1.get()
    entered_password = e2.get()

    if entered_name == username:
        if entered_password == password:
            messagebox.showinfo("Success", "Login Successful!!!")
            show_second_page()
        else:
            messagebox.showerror("Error", "Incorrect password")
    else:
        messagebox.showerror("Error", "Login Failed!!!")


def show_login_page():
    for widget in top.winfo_children():
        widget.destroy()

    global e1, e2

    try:
        login_image_raw = Image.open(LOGIN_IMAGE_PATH)
        login_image_resized = login_image_raw.resize((1366, 786))
        photo = ImageTk.PhotoImage(login_image_resized)
        bg_label = Label(top, image=photo)
        bg_label.image = photo
        bg_label.place(x=0, y=0)
    except Exception:
        top.configure(bg="lightcoral")

    Label(top, text="💰 Personal Expenses Tracker",
          font=("Georgia", 18, "bold"),
          fg="darkslategray").place(x=683, y=150, anchor="center")

    Label(top, text="Please login to continue",
          font=("Georgia", 10, "italic"),
          fg="slategray").place(x=683, y=220, anchor="center")

    Label(top, text="Track🧑‍💻. save💵. Grow📈.",
          font=("Arial", 11, "italic"),
          fg="black").place(x=683, y=270, anchor="center")

    Label(top, text="Name:", font=("Georgia", 12, "bold"),
          bg="ivory", fg="darkslategray").place(x=570, y=320, anchor="center")

    e1 = Entry(top, width=25, bg="lightyellow", fg="black",
               relief="solid", bd=1, font=("Georgia", 11))
    e1.place(x=750, y=320, anchor="center")

    Label(top, text="Password:", font=("Georgia", 12, "bold"),
          bg="ivory", fg="darkslategray").place(x=570, y=380, anchor="center")

    e2 = Entry(top, width=25, bg="lightyellow", fg="black",
               relief="solid", bd=1, font=("Georgia", 11), show="*")
    e2.place(x=750, y=380, anchor="center")

    Button(top, text="🔑  LOGIN", font=("Georgia", 12, "bold"),
           background="darkgoldenrod", foreground="white",
           activebackground="goldenrod", activeforeground="white",
           padx=20, pady=6, relief="flat",
           command=data).place(x=683, y=500, anchor="center")


show_login_page()
top.mainloop()
