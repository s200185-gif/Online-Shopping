import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import zipfile
from io import BytesIO
import re
import datetime
import traceback

zip_path = "productimage.zip"
try:
    zip_file = zipfile.ZipFile(zip_path, "r")
    zip_contents = zip_file.namelist()
except FileNotFoundError:
    print(f"Warning: {zip_path} not found")
    zip_file = None
    zip_contents = []

connection = sqlite3.connect('online_shop.db3')
cursor = connection.cursor()
current_user = None

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_product_image(productimage, pname):
    if zip_file is not None:
        if productimage:
            for path in [f"product_images/{productimage}", productimage]:
                try:
                    with zip_file.open(path) as file:
                        return Image.open(BytesIO(file.read())).resize((200, 200))
                except Exception:
                    continue
        if pname:
            for ext in ['.jpg', '.jpeg', '.png', '.webp', '']:
                for path in [f"product_images/{pname}{ext}", f"{pname}{ext}"]:
                    try:
                        with zip_file.open(path) as file:
                            return Image.open(BytesIO(file.read())).resize((200, 200))
                    except Exception:
                        continue
        try:
            with zip_file.open("no.jpg") as file:
                return Image.open(BytesIO(file.read())).resize((200, 200))
        except Exception:
            pass
    return Image.new('RGB', (200, 200), color='lightgray')


def login_page():
    loginroot = tk.Toplevel()
    loginroot.title("Login Page")
    loginroot.geometry("400x300")
    loginroot.configure(bg="#f9f9f9")
    loginroot.transient(root)
    loginroot.grab_set()

    def login():
        top = tk.Toplevel(loginroot)
        top.title("Login")
        top.geometry("300x200")
        top.configure(bg="#f9f9f9")
        top.transient(loginroot)
        top.grab_set()

        tk.Label(top, text="UID:", bg="#f9f9f9").pack(pady=5)
        entry_user = tk.Entry(top)
        entry_user.pack(pady=5)
        tk.Label(top, text="PASSWORD:", bg="#f9f9f9").pack(pady=5)
        entry_pass = tk.Entry(top, show="*")
        entry_pass.pack(pady=5)

        def do_login():
            global current_user
            uid = entry_user.get().strip()
            pw = entry_pass.get().strip()

            try:
                cursor.execute('SELECT UID, password FROM USER WHERE UID = ?', (uid,))
                result = cursor.fetchone()
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {e}")
                return

            if not result or result[1] != pw:
                messagebox.showerror("Error", "Wrong UID or password")
                return

            current_user = result[0]
            messagebox.showinfo("Success", f"Welcome back {uid}!")
            top.destroy()
            loginroot.destroy()
            try:
                ui()
            except Exception as e:
                traceback.print_exc()
                messagebox.showerror("UI Error", f"Failed to load UI: {e}")

        tk.Button(top, text="Login", command=do_login, bg="#4CAF50").pack(pady=10)

    def register():
        top = tk.Toplevel(loginroot)
        top.title("Register")
        top.geometry("400x500")
        top.configure(bg="#f9f9f9")
        top.transient(loginroot)
        top.grab_set()

        tk.Label(top, text="Account (Email or Phone):", bg="#f9f9f9").pack(pady=5)
        entry_user = tk.Entry(top, width=30)
        entry_user.pack(pady=5)
        tk.Label(top, text="Name:", bg="#f9f9f9").pack(pady=5)
        entry_name = tk.Entry(top, width=30)
        entry_name.pack(pady=5)
        tk.Label(top, text="Birth (YYYY-MM-DD):", bg="#f9f9f9").pack(pady=5)
        entry_birth = tk.Entry(top, width=30)
        entry_birth.pack(pady=5)
        tk.Label(top, text="Gender (M/F):", bg="#f9f9f9").pack(pady=5)
        entry_gender = tk.Entry(top, width=30)
        entry_gender.pack(pady=5)
        tk.Label(top, text="Password:", bg="#f9f9f9").pack(pady=5)
        entry_pass = tk.Entry(top, show="*", width=30)
        entry_pass.pack(pady=5)

        def do_register():
            global current_user
            cursor.execute("SELECT COUNT(*) FROM USER")
            count = cursor.fetchone()[0]
            uid = "U" + str(count + 1).zfill(3)

            register_acc = entry_user.get().strip()
            name = entry_name.get().strip()
            birth = entry_birth.get().strip()
            gender = entry_gender.get().strip().upper()
            pw = entry_pass.get().strip()

            if not (("@" in register_acc and "." in register_acc) or re.match(r"^\+\d{1,3}\d{6,}$", register_acc)):
                messagebox.showerror("Error", "Account must be a valid Email or phone number with country code")
                return
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", birth):
                messagebox.showerror("Error", "Birth must be in YYYY-MM-DD format")
                return
            if len(pw) < 10:
                messagebox.showerror("Error", "Password must be at least 10 characters")
                return
            if not re.search(r"[A-Z]", pw):
                messagebox.showerror("Error", "Password must contain at least one uppercase letter")
                return
            if not re.search(r"[a-z]", pw):
                messagebox.showerror("Error", "Password must contain at least one lowercase letter")
                return
            if not re.search(r"\d", pw):
                messagebox.showerror("Error", "Password must contain at least one number")
                return
            if not re.search(r"[\w]", pw):
                messagebox.showerror("Error", "Password must contain at least one symbol")
                return
            if gender not in ['M', 'F']:
                messagebox.showerror("Error", "Gender must be M or F")
                return

            try:
                cursor.execute(
                    "INSERT INTO USER (UID, Register, Birth, Gender, Password, Name, VIP) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (uid, register_acc, 0, birth, gender, pw, name, 0)
                )
                connection.commit()
                current_user = uid
                messagebox.showinfo("Success", f"Register {uid} registered successfully!")
                top.destroy()
                loginroot.destroy()
                try:
                    ui()
                except Exception as e:
                    traceback.print_exc()
                    messagebox.showerror("UI Error", f"Failed to load UI: {e}")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Registration failed: {e}")

        tk.Button(top, text="Register", command=do_register, bg="#2196F3").pack(pady=10)

    tk.Label(loginroot, text="Good Taste Fashion", font=('Georgia', 20, "bold"),
             fg="#F4D10B", bg="#f9f9f9").pack(pady=20)
    tk.Button(loginroot, text="Login", command=login, width=15, height=2,
              bg="#4CAF50", font=('Arial', 12)).pack(pady=10)
    tk.Button(loginroot, text="Register", command=register, width=15, height=2,
              bg="#2196F3", font=('Arial', 12)).pack(pady=10)

def ui():
    for widget in root.winfo_children():
        widget.destroy()

    title_frame = tk.Frame(root, bg="#f9f9f9")
    title_frame.pack(fill="x", pady=10)

    tk.Label(title_frame, text="Good Taste Fashion",
             font=('Georgia', 26, "bold italic"),
             bg="#f9f9f9").pack(side="left", padx=20)

    user_frame = tk.Frame(title_frame, bg="#f9f9f9")
    user_frame.pack(side="right", padx=20)

    if current_user:
        cursor.execute("SELECT VIP FROM USER WHERE UID = ?", (current_user,))
        vip_result = cursor.fetchone()
        is_vip = vip_result[0] if vip_result else 0
        vip_text = " (VIP)" if is_vip else ""
        tk.Label(user_frame, text=f"Welcome, {current_user}{vip_text}",
                 font=('Arial', 12), bg="#f9f9f9").pack(side="top")
        try:
            trolley_img = Image.open("trolley.webp")
            trolley_img = trolley_img.resize((40, 40))
            trolley_photo = ImageTk.PhotoImage(trolley_img)
            trolley_btn = tk.Button(
                user_frame, image=trolley_photo, text="Cart",
                compound="top", bg="#FF9800", font=('Arial', 10),
                command=checkout
            )
            trolley_btn.image = trolley_photo
            trolley_btn.pack(side="top", pady=5)
        except Exception as e:
            print(f"Cannot load trolley.webp: {e}, using text button")
            tk.Button(user_frame, text="🛒 Cart", bg="#FF9800",
                      font=('Arial', 12), padx=20, pady=5,
                      command=checkout).pack(side="top", pady=5)

    style = ttk.Style()
    style.configure("Tab.TNotebook", tabposition="nw")
    note = ttk.Notebook(root, style="Tab.TNotebook")
    tabs(note)
    note.pack(expand=True, fill='both', padx=10, pady=10)


def tabs(note):
    CATEGORY = ['Women', 'Men', 'Kids']

    for category in CATEGORY:
        frame = tk.Frame(note)
        note.add(frame, text=category)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(frame, bg="#f9f9f9", highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        inner_frame = tk.Frame(canvas, bg="#f9f9f9")
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        for col in range(4):
            inner_frame.columnconfigure(col, weight=1, uniform="equal")

        def on_configure(canvas=canvas):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_frame.bind("<Configure>", on_configure)

        cursor.execute('SELECT PID, PNAME, PRICE, PD, productimage FROM PRODUCT WHERE CATEGORY = ?', (category,))
        rows = cursor.fetchall()
        show_product_detail(inner_frame, rows)


def show_product_detail(inner_frame, rows):
    for index, (PID, PNAME, PRICE, PD, productimage) in enumerate(rows):
        row_pos = index // 4
        col_pos = index % 4

        img = load_product_image(productimage, PNAME)

        product_frame = tk.Frame(inner_frame, bg="white", relief=tk.RAISED, borderwidth=1)
        product_frame.grid(row=row_pos, column=col_pos, padx=10, pady=10, sticky="nsew")

        photo = ImageTk.PhotoImage(img)

        price_val = safe_float(PRICE)

        button = tk.Button(
            product_frame,
            image=photo,
            text=f"{PNAME}\n${price_val:.2f}",
            compound="top",
            bg="white",
            font=('Arial', 10),
            command=lambda pid=PID, pname=PNAME, price=price_val, pd=PD: trolley(pid, pname, price, pd)
        )
        button.image = photo
        button.pack(fill="both", expand=True, padx=5, pady=5)

def trolley(PID, PNAME, PRICE, PD):
    price_val = safe_float(PRICE)

    detail = tk.Toplevel()
    detail.title(PNAME)
    detail.geometry("500x550")
    detail.configure(bg="white")

    tk.Label(detail, text=PNAME, font=('Georgia', 18, 'bold'), bg="white").pack(pady=10)
    tk.Label(detail, text=f"Price: ${price_val:.2f}", font=('Arial', 14), bg="white").pack(pady=5)
    tk.Label(detail, text="Description:", font=('Arial', 12, 'bold'), bg="white").pack(pady=(10, 0))
    tk.Label(detail, text=PD, wraplength=350, justify="left", bg="white").pack(pady=10)

    cursor.execute("SELECT SIZE, AMOUNT FROM STOCK WHERE PID = ? AND AMOUNT > 0", (PID,))
    size_options = cursor.fetchall()

    if not size_options:
        tk.Label(detail, text="Out of Stock", font=('Arial', 12), fg="red", bg="white").pack(pady=10)
        return

    size_frame = tk.Frame(detail, bg="white")
    size_frame.pack(pady=10)

    tk.Label(size_frame, text="Select Size:", font=('Arial', 12, 'bold'), bg="white").pack(side="left", padx=5)

    selected_size = tk.StringVar(detail)
    selected_size.set(size_options[0][0])

    size_dropdown = ttk.Combobox(size_frame, textvariable=selected_size,
                                 values=[s[0] for s in size_options],
                                 state="readonly", width=15)
    size_dropdown.pack(side="left", padx=5)

    stock_label = tk.Label(size_frame, text=f"Stock: {size_options[0][1]}",
                           font=('Arial', 10), bg="white")
    stock_label.pack(side="left", padx=10)

    quantity_frame = tk.Frame(detail, bg="white")
    quantity_frame.pack(pady=10)
    tk.Label(quantity_frame, text="Quantity:", font=('Arial', 12, 'bold'), bg="white").pack(side="left", padx=5)

    quantity_var = tk.IntVar(value=1)
    quantity_spinbox = tk.Spinbox(quantity_frame, from_=1, to=min(10, size_options[0][1]),
                                  textvariable=quantity_var, width=5)
    quantity_spinbox.pack(side="left", padx=5)

    def update_stock_display(*args):
        selected = selected_size.get()
        for size, amount in size_options:
            if size == selected:
                stock_label.config(text=f"Stock: {amount}")
                max_qty = min(10, amount)
                quantity_spinbox.config(to=max_qty)
                if quantity_var.get() > max_qty:
                    quantity_var.set(max_qty)
                break

    selected_size.trace("w", update_stock_display)

    def add_to_trolley():
        if not current_user:
            messagebox.showerror("Error", "Please login first")
            return

        selected_size_val = selected_size.get()
        quantity_val = quantity_var.get()

        cursor.execute("SELECT AMOUNT FROM STOCK WHERE PID = ? AND SIZE = ?", (PID, selected_size_val))
        stock_result = cursor.fetchone()

        if not stock_result or stock_result[0] < quantity_val:
            messagebox.showerror("Error", "Not enough stock available")
            return

        try:
            for _ in range(quantity_val):
                cursor.execute('INSERT INTO trolley (uid, PNAME) VALUES (?, ?)',
                               (current_user, PNAME))
            connection.commit()
            messagebox.showinfo("Success", f"Added {quantity_val} x {PNAME} (Size: {selected_size_val}) to trolley!")
            detail.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add to trolley: {e}")

    tk.Button(detail, text="Add to Trolley", bg="green",
              font=('Arial', 12), command=add_to_trolley).pack(pady=20)

def checkout():
    if not current_user:
        messagebox.showerror("Error", "Please login first")
        return

    checkout_window = tk.Toplevel()
    checkout_window.title("Shopping Cart")
    checkout_window.geometry("800x500")
    checkout_window.configure(bg="white")

    tk.Label(checkout_window, text="Your Shopping Cart",
             font=('Georgia', 18, 'bold'), bg="white").pack(pady=10)

    cart_frame = tk.Frame(checkout_window, bg="white")
    cart_frame.pack(fill="both", expand=True, padx=20, pady=10)

    headers = ["Product", "Size", "Price", "Quantity", "Subtotal"]
    for i, header in enumerate(headers):
        tk.Label(cart_frame, text=header, font=('Arial', 12, 'bold'),
                 bg="white", relief="solid", width=12).grid(row=0, column=i, padx=2, pady=2, sticky="ew")

    try:
        cursor.execute('''
            SELECT t.PNAME, p.PRICE, COUNT(*) as quantity
            FROM trolley t
            JOIN PRODUCT p ON t.PNAME = p.PNAME
            WHERE t.uid = ?
            GROUP BY t.PNAME, p.PRICE
        ''', (current_user,))
        cart_items = cursor.fetchall()

        if not cart_items:
            tk.Label(cart_frame, text="Your cart is empty",
                     font=('Arial', 14), bg="white").grid(row=1, column=0, columnspan=5, pady=20)
            checkout_window.after(2000, checkout_window.destroy)
            return

        total_amount = 0.0
        row = 1

        for product_name, price, quantity in cart_items:
            price = safe_float(price)  # 关键修复
            quantity = int(quantity)

            cursor.execute("SELECT PID FROM PRODUCT WHERE PNAME = ?", (product_name,))
            pid_result = cursor.fetchone()
            pid = pid_result[0] if pid_result else None

            size = "M"
            if pid:
                cursor.execute("SELECT SIZE FROM STOCK WHERE PID = ? AND AMOUNT > 0 LIMIT 1", (pid,))
                size_row = cursor.fetchone()
                if size_row:
                    size = size_row[0]

            subtotal = price * quantity
            total_amount += subtotal

            tk.Label(cart_frame, text=product_name, bg="white", relief="solid",
                     width=12, wraplength=100).grid(row=row, column=0, padx=2, pady=2, sticky="ew")
            tk.Label(cart_frame, text=size, bg="white", relief="solid",
                     width=12).grid(row=row, column=1, padx=2, pady=2, sticky="ew")
            tk.Label(cart_frame, text=f"${price:.2f}", bg="white", relief="solid",
                     width=12).grid(row=row, column=2, padx=2, pady=2, sticky="ew")
            tk.Label(cart_frame, text=str(quantity), bg="white", relief="solid",
                     width=12).grid(row=row, column=3, padx=2, pady=2, sticky="ew")
            tk.Label(cart_frame, text=f"${subtotal:.2f}", bg="white", relief="solid",
                     width=12).grid(row=row, column=4, padx=2, pady=2, sticky="ew")
            row += 1

        cursor.execute("SELECT VIP FROM USER WHERE UID = ?", (current_user,))
        vip_result = cursor.fetchone()
        is_vip = vip_result[0] if vip_result else 0

        discount = total_amount * 0.1 if is_vip else 0.0
        final_amount = total_amount - discount
        discount_text = f"VIP Discount (10%): -${discount:.2f}" if is_vip else "VIP Discount: $0.00"

        summary_frame = tk.Frame(checkout_window, bg="white")
        summary_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(summary_frame, text=f"Subtotal: ${total_amount:.2f}",
                 font=('Arial', 12), bg="white").pack(anchor="e")
        tk.Label(summary_frame, text=discount_text,
                 font=('Arial', 12), bg="white").pack(anchor="e")
        tk.Label(summary_frame, text=f"Total: ${final_amount:.2f}",
                 font=('Arial', 14, 'bold'), bg="white").pack(anchor="e")

        def process_checkout():
            try:
                checkout_window.destroy()
                collect_delivery_info(final_amount, is_vip, discount)
            except Exception as e:
                traceback.print_exc()
                messagebox.showerror("Error", f"Checkout failed: {e}")

        tk.Button(checkout_window, text="Proceed to Checkout", bg="#4CAF50",
                  font=('Arial', 14), command=process_checkout).pack(pady=20)

    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Error", f"Failed to load cart: {e}")
        checkout_window.destroy()


def collect_delivery_info(final_amount, is_vip, discount):
    delivery_window = tk.Toplevel()
    delivery_window.title("Delivery Information")
    delivery_window.geometry("600x600")
    delivery_window.configure(bg="white")

    tk.Label(delivery_window, text="Delivery Details",
             font=('Georgia', 18, 'bold'), bg="white").pack(pady=10)

    cursor.execute('''
        SELECT t.PNAME, COUNT(*) as quantity, p.PID, p.PRICE
        FROM trolley t
        JOIN PRODUCT p ON t.PNAME = p.PNAME
        WHERE t.uid = ?
        GROUP BY t.PNAME, p.PID, p.PRICE
    ''', (current_user,))
    cart_items = cursor.fetchall()

    if not cart_items:
        messagebox.showerror("Error", "Your cart is empty")
        delivery_window.destroy()
        return

    summary_frame = tk.Frame(delivery_window, bg="white")
    summary_frame.pack(fill="x", padx=20, pady=10)
    tk.Label(summary_frame, text="Order Summary:",
             font=('Arial', 12, 'bold'), bg="white").pack(anchor="w", pady=5)

    order_items_with_size = []
    for product_name, quantity, pid, price in cart_items:
        price = safe_float(price)
        quantity = int(quantity)

        cursor.execute("SELECT SIZE FROM STOCK WHERE PID = ? AND AMOUNT > 0 LIMIT 1", (pid,))
        size_row = cursor.fetchone()
        size = size_row[0] if size_row else "M"

        order_items_with_size.append((product_name, size, price, quantity, pid))

        item_text = f"{product_name} (Size: {size}) - {quantity} x ${price:.2f} = ${price * quantity:.2f}"
        tk.Label(summary_frame, text=item_text,
                 font=('Arial', 10), bg="white").pack(anchor="w")

    subtotal = final_amount + discount if is_vip else final_amount
    tk.Label(summary_frame, text=f"Subtotal: ${subtotal:.2f}",
             font=('Arial', 11), bg="white").pack(anchor="w")
    if is_vip:
        tk.Label(summary_frame, text=f"VIP Discount (10%): -${discount:.2f}",
                 font=('Arial', 11), fg="green", bg="white").pack(anchor="w")
    tk.Label(summary_frame, text=f"Order Total: ${final_amount:.2f}",
             font=('Arial', 12, 'bold'), bg="white").pack(anchor="w", pady=5)

    address_frame = tk.Frame(delivery_window, bg="white")
    address_frame.pack(fill="x", padx=20, pady=20)
    tk.Label(address_frame, text="Delivery Address:",
             font=('Arial', 12, 'bold'), bg="white").pack(anchor="w")
    address_text = tk.Text(address_frame, height=4, width=50)
    address_text.pack(fill="x", pady=10)

    def confirm_delivery():
        destination = address_text.get("1.0", "end-1c").strip()
        if not destination:
            messagebox.showerror("Error", "Please enter a delivery address")
            return

        try:
            cursor.execute("SELECT COUNT(*) FROM RECORD")
            record_count = cursor.fetchone()[0]
            sales_id = "S" + str(record_count + 1).zfill(3)

            cursor.execute("SELECT COUNT(*) FROM DELIVER")
            deliver_count = cursor.fetchone()[0]
            did = "D" + str(deliver_count + 1).zfill(3)

            current_date = datetime.datetime.now().strftime("%Y-%m-%d")

            cursor.execute(
                "INSERT INTO RECORD (Sales_ID, SDATE, TPRICE, UID, DID, CID) VALUES (?, ?, ?, ?, ?, ?)",
                (sales_id, current_date, final_amount, current_user, '0', None)
            )
            cursor.execute(
                "INSERT INTO DELIVER (DID, Sales_ID, DESTINATION, ARRIVED) VALUES (?, ?, ?, ?)",
                (did, sales_id, destination, 0)
            )
            cursor.execute(
                "UPDATE RECORD SET DID = ? WHERE Sales_ID = ?",
                (did, sales_id)
            )

            for product_name, size, price, quantity, pid in order_items_with_size:
                cursor.execute(
                    "INSERT INTO ORDERITEM (Sales_ID, PID, QUANTITY, rates, PRICE, SIZE) VALUES (?, ?, ?, ?, ?, ?)",
                    (sales_id, pid, quantity, 0, price, size)
                )
                cursor.execute(
                    "UPDATE STOCK SET AMOUNT = AMOUNT - ? WHERE PID = ? AND SIZE = ?",
                    (quantity, pid, size)
                )

            cursor.execute("DELETE FROM trolley WHERE uid = ?", (current_user,))
            connection.commit()

            update_vip_status()

            messagebox.showinfo(
                "Order Confirmed",
                f"Order placed successfully!\n"
                f"Sales ID: {sales_id}\n"
                f"Delivery ID: {did}\n"
                f"Total Amount: ${final_amount:.2f}\n"
                f"Delivery to: {destination}"
            )
            delivery_window.destroy()

        except sqlite3.Error as e:
            connection.rollback()
            messagebox.showerror("Error", f"Failed to place order: {e}")

    tk.Button(delivery_window, text="Confirm Delivery Details",
              bg="#4CAF50", fg="white", font=('Arial', 12),
              command=confirm_delivery).pack(pady=10)


# ==================== VIP 升级 ====================
def update_vip_status():
    try:
        cursor.execute("SELECT UID FROM USER WHERE VIP = 0")
        non_vip_users = cursor.fetchall()
        upgraded = []
        for (uid,) in non_vip_users:
            cursor.execute("SELECT SUM(TPRICE) FROM RECORD WHERE UID = ?", (uid,))
            total_spent = cursor.fetchone()[0]
            if total_spent is not None and total_spent >= 10000:
                cursor.execute("UPDATE USER SET VIP = 1 WHERE UID = ?", (uid,))
                upgraded.append((uid, total_spent))
        connection.commit()
        for uid, total in upgraded:
            print(f"[VIP] {uid} upgraded (total: ${total:.2f})")
    except Exception as e:
        print(f"VIP update error: {e}")

def order_management(cursor):
    cursor.execute("SELECT UID FROM USER WHERE VIP = 0")
    non_vip_users = cursor.fetchall()
    for (uid,) in non_vip_users:
        cursor.execute("SELECT SUM(TPRICE) FROM RECORD WHERE UID = ?", (uid,))
        total_spent = cursor.fetchone()[0]
        if total_spent is not None and total_spent >= 10000:
            cursor.execute("UPDATE USER SET VIP = 1 WHERE UID = ?", (uid,))
    connection.commit()

    delete = input('input sales id that you want to delete:')
    cursor.execute("DELETE FROM ORDERITEM WHERE Sales_ID = ?", (delete,))
    connection.commit()

def analyse():
    core_function_two = pd.read_sql_query(
        "SELECT gender, COUNT(*) FROM USER GROUP BY GENDER", connection)
    plt.figure(figsize=(8, 6))
    plt.pie(core_function_two['COUNT(*)'], labels=['M', 'F'],
            colors=['#66b3ff', '#ff9999'], autopct='%1.1f%%', startangle=90)
    plt.title('proportion of customers by gender', fontsize=14)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

    cft = pd.read_sql_query(
        "SELECT strftime('%m',SDATE) AS Month, SUM(TPRICE) AS TPRICE "
        "FROM RECORD GROUP BY strftime('%m', SDATE) ORDER BY Month;", connection)
    plt.figure(figsize=(8, 6))
    plt.bar(cft['Month'], cft['TPRICE'],
            color=['#66b3ff', '#ff9999', '#FFF15C', '#95FF8A', '#00CCF5', '#AC00F5'])
    plt.title('total revenue across months', fontsize=14)
    plt.show()

    cff = pd.read_sql_query(
        "SELECT TYPE, COUNT(quantity) FROM product, orderitem "
        "WHERE ORDERITEM.pid = product.pid AND orderitem.Sales_id IN "
        "(SELECT Sales_id FROM RECORD WHERE SDATE LIKE '%-05-%') "
        "GROUP BY type", connection)
    plt.figure(figsize=(8, 6))
    plt.bar(cff['TYPE'], cff['COUNT(quantity)'])
    plt.title('sales of type of products in MAY', fontsize=14)
    plt.show()

    cffive = pd.read_sql_query(
        "SELECT SUM(RECORD.TPRICE) AS Total_Price FROM RECORD "
        "JOIN USER ON RECORD.UID = USER.UID AND RECORD.SDATE LIKE '%-05-%' "
        "GROUP BY USER.gender", connection)
    plt.figure(figsize=(8, 6))
    plt.pie(cffive['Total_Price'], labels=['M', 'F'],
            colors=['#66b3ff', '#ff9999'], autopct='%1.1f%%', startangle=90)
    plt.title('total revenue between male and female customer in MAY', fontsize=14)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

    cfs = pd.read_sql_query(
        "SELECT GENDER, AVG(RECORD.TPRICE) FROM RECORD, USER "
        "WHERE RECORD.UID = USER.UID GROUP BY USER.gender", connection)
    plt.figure(figsize=(8, 6))
    plt.bar(cfs['GENDER'], cfs['AVG(RECORD.TPRICE)'], color=['#ff9999', '#66b3ff'])
    plt.title('average sales between male and female customers')
    plt.show()

root = tk.Tk()
root.title("Good Taste Fashion")
root.geometry("1200x800")
root.resizable(True, True)
root.configure(bg="#f9f9f9")

login_page()
root.mainloop()
connection.close()