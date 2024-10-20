import os
import sqlite3
import sys
import time
from datetime import date, datetime, timedelta
import pandas as pd
import pywhatkit as kit
import requests
from dateutil.relativedelta import relativedelta
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import webbrowser
from io import StringIO
import babel.numbers


def adapt_date(date_obj):
    """Converts a date object to a string in ISO format for storage in SQLite."""
    return date_obj.isoformat()


def convert_date(date_text):
    """Converts a byte string from the database back into a date object."""
    return datetime.strptime(date_text.decode("utf-8"), "%Y-%m-%d").date()


sqlite3.register_adapter(date, adapt_date)
sqlite3.register_converter("date", convert_date)


class GymManagerApp:
    def __init__(self, root):
        """Initializes the Gym Manager application."""
        self.root = root
        self.root.state("zoomed")
        self.root.title("Gym Manager")
        self.db_path = os.path.join(os.path.dirname(sys.executable), "gym.db")
        self.config_path = os.path.join(
            os.path.dirname(sys.executable), "image_path.txt"
        )
        self.create_table()
        if self.update_expired_members():
            self.setup_ui()

    def create_table(self):
        """Creates the 'members' and 'app_data' tables in the database if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                duration TEXT NOT NULL,
                fees REAL NOT NULL,
                payment_method TEXT NOT NULL,
                date_of_activation TEXT NOT NULL,
                expiration_date TEXT,
                status TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive')),
                notified TEXT NOT NULL DEFAULT 'False' CHECK (notified IN ('True', 'False'))
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS app_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_count INTEGER DEFAULT 0,
                license_key_expiration TEXT DEFAULT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    def update_expired_members(self):
        """Checks and updates the status of members based on their expiration date."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            current_date = datetime.now().date()
            cursor.execute(
                "SELECT id, duration, date_of_activation FROM members WHERE status = 'Active'"
            )
            rows = cursor.fetchall()
            updates = []
            for member_id, duration_str, date_of_activation in rows:
                duration_months = int(duration_str.split()[0])
                activation_date = datetime.strptime(
                    date_of_activation, "%Y-%m-%d"
                ).date()
                expiration_date = activation_date + relativedelta(
                    months=duration_months
                )
                if current_date > expiration_date:
                    updates.append((expiration_date, "Inactive", member_id))
                else:
                    updates.append((expiration_date, "Active", member_id))
            if updates:
                cursor.executemany(
                    "UPDATE members SET expiration_date = ?, status = ? WHERE id = ?",
                    updates,
                )
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return False
        finally:
            conn.close()

    def setup_ui(self):
        """Sets up the user interface for the Gym Manager application."""
        self.background_image = tk.Label(self.root)
        self.background_image.pack(fill=tk.BOTH, expand=True)
        self.image_path = self.load_image_path()
        if not self.image_path:
            self.image_path = filedialog.askopenfilename(
                title="Select an Image File",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")],
            )
            if self.image_path:
                self.save_image_path(self.image_path)
            else:
                self.root.destroy()
                return
        self.photo = None
        self.root.bind("<Configure>", self.load_and_resize_image)
        self.create_buttons()

    def load_image_path(self):
        """Load the saved image path from the file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as file:
                return file.readline().strip()
        return None

    def save_image_path(self, path):
        """Save the image path to the file."""
        with open(self.config_path, "w") as file:
            file.write(path)

    def load_and_resize_image(self, event):
        """Update the background image to fit the window."""
        try:
            image = Image.open(self.image_path)
            width, height = self.root.winfo_width(), self.root.winfo_height()
            if self.photo:
                old_width, old_height = self.photo.width(), self.photo.height()
                if old_width == width and old_height == height:
                    return
            resized_image = image.resize((width, height), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_image)
            self.background_image.config(image=self.photo)
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load the image: {e}")

    def create_buttons(self):
        """Create and add buttons to the sidebar."""
        self.sidebar_frame = tk.Frame(self.background_image)
        self.sidebar_frame.pack(padx=30, side=tk.LEFT)
        button_data = ["Add Member", "View Member Details", "Gym Accounts", "Exit"]
        for label in button_data:
            if label == "Exit":
                button = tk.Button(
                    self.sidebar_frame,
                    text=label,
                    bg="white",
                    fg="black",
                    font=("Segoe UI", 20, "bold"),
                    width=20,
                    command=lambda: self.root.quit(),
                )
                button.pack()
            else:
                button = tk.Button(
                    self.sidebar_frame,
                    text=label,
                    bg="white",
                    fg="black",
                    font=("Segoe UI", 20, "bold"),
                    command=lambda l=label: self.show_content(l),
                    width=20,
                )
                button.pack()

    def show_content(self, label):
        """Clear previous content and display appropriate content based on the label."""
        self.clear_main_frame()
        content_functions = {
            "Add Member": self.show_add_member,
            "View Member Details": self.show_member_details,
            "Gym Accounts": self.show_gym_accounts,
        }
        if label in content_functions:
            content_functions[label]()
        self.back_button()

    def clear_main_frame(self):
        """Function to clear the main frame before loading new content."""
        for widget in self.background_image.winfo_children():
            widget.destroy()

    def back_button(self):
        """Creates and displays a back button to navigate to the previous menu."""
        back_button = tk.Button(
            self.background_image,
            text="Back",
            font=("Segoe UI", 12, "bold"),
            command=self.recreate_sidebar,
        )
        back_button.pack(padx=10, pady=10, side="bottom", anchor="e", ipadx=20)

    def recreate_sidebar(self):
        """Recreate the sidebar and restore the initial layout."""
        self.clear_main_frame()
        self.create_buttons()

    def show_add_member(self):
        """Display the Add Member interface."""
        BG_COLOR = "blue"
        BUTTON_BG_COLOR = "Forest Green"
        BUTTON_FG_COLOR = "white"
        ERROR_BG_COLOR = "#f2003c"
        FONT_LARGE = ("Segoe UI", 20, "bold")
        FONT_MEDIUM = ("Segoe UI", 16, "bold")
        FONT_SMALL = ("Segoe UI", 12)
        tk.Label(self.background_image, text="Add Member", font=FONT_LARGE).pack(
            pady=20
        )
        add_member_frame = tk.Frame(self.background_image, bd=2, relief=tk.SOLID)
        add_member_frame.pack()
        labels = [
            "Name:",
            "Age:",
            "Gender:",
            "Phone Number:",
            "Membership Duration (months):",
            "Membership Fees (Rs):",
            "Payment Method:",
        ]
        for i, text in enumerate(labels):
            tk.Label(add_member_frame, font=FONT_MEDIUM, text=text).grid(
                row=i, column=0, pady=10, padx=(20, 0), sticky=tk.E
            )
        vcmd_text = (add_member_frame.register(self.validate_input), "%P", "letters")
        vcmd_numeric = (add_member_frame.register(self.validate_input), "%P", "numeric")
        self.entry_name = tk.Entry(
            add_member_frame,
            width=25,
            font=FONT_MEDIUM,
            validate="key",
            validatecommand=vcmd_text,
        )
        self.entry_name.grid(row=0, column=1, padx=(0, 20))
        self.entry_name.focus()
        age_options = [str(i) for i in range(1, 101)]
        self.age_choice = tk.StringVar(add_member_frame)
        self.age_choice.set("Select Age")
        age_menu = tk.OptionMenu(add_member_frame, self.age_choice, *age_options)
        age_menu.grid(row=1, column=1, sticky=tk.W)
        age_menu.config(bg=BG_COLOR, fg="white", font=FONT_SMALL)
        self.gender = tk.StringVar(add_member_frame)
        self.gender.set("Select")
        gender_menu = tk.OptionMenu(add_member_frame, self.gender, "Male", "Female")
        gender_menu.grid(row=2, column=1, sticky=tk.W)
        gender_menu.config(bg=BG_COLOR, fg="white", font=FONT_SMALL)
        self.entry_number = tk.Entry(
            add_member_frame,
            width=25,
            font=FONT_MEDIUM,
            validate="key",
            validatecommand=vcmd_numeric,
        )
        self.entry_number.grid(row=3, column=1, padx=(0, 20))
        duration_options = [f"{i} months" for i in range(1, 13)]
        self.duration_choice = tk.StringVar(add_member_frame)
        self.duration_choice.set("Select")
        duration_menu = tk.OptionMenu(
            add_member_frame, self.duration_choice, *duration_options
        )
        duration_menu.grid(row=4, column=1, sticky=tk.W)
        duration_menu.config(bg=BG_COLOR, fg="white", font=FONT_SMALL)
        self.entry_fees = tk.Entry(
            add_member_frame,
            width=15,
            font=FONT_MEDIUM,
            validate="key",
            validatecommand=vcmd_numeric,
        )
        self.entry_fees.grid(row=5, column=1, sticky=tk.W)
        self.payment_method = tk.StringVar(add_member_frame)
        self.payment_method.set("Select")
        payment_menu = tk.OptionMenu(
            add_member_frame, self.payment_method, "Online", "Cash"
        )
        payment_menu.grid(row=6, column=1, sticky=tk.W)
        payment_menu.config(bg=BG_COLOR, fg="white", font=FONT_SMALL)
        buttons_frame = tk.Frame(add_member_frame)
        buttons_frame.grid(row=8, column=0, columnspan=2, pady=10)
        tk.Button(
            buttons_frame,
            text="Register",
            command=self.register_member,
            font=("Segoe UI", 13, "bold"),
            bg=BUTTON_BG_COLOR,
            fg=BUTTON_FG_COLOR,
        ).grid(row=0, column=0, padx=20)
        tk.Button(
            buttons_frame,
            text="Reset",
            command=self.reset_form,
            font=("Segoe UI", 13, "bold"),
            bg=ERROR_BG_COLOR,
            fg=BUTTON_FG_COLOR,
        ).grid(row=0, column=1)

    def reset_form(self):
        """Reset the form fields to their default state."""
        self.entry_name.delete(0, tk.END)
        self.age_choice.set("Select Age")
        self.gender.set("Select")
        self.entry_number.delete(0, tk.END)
        self.duration_choice.set("Select")
        self.entry_fees.delete(0, tk.END)
        self.payment_method.set("Select")

    def validate_input(self, input_str, mode):
        """Validates input based on the type specified."""
        if mode == "numeric":
            return input_str.isdigit() or input_str == ""
        elif mode == "letters":
            return all(char.isalpha() or char.isspace() for char in input_str)
        else:
            return False

    def register_member(self):
        """Registers a new member into the database with the provided details from the form."""
        member_name = self.entry_name.get()
        member_age = self.age_choice.get()
        member_gender = self.gender.get()
        member_number = self.entry_number.get()
        member_duration = self.duration_choice.get()
        member_fees = self.entry_fees.get()
        payment_method = self.payment_method.get()
        date_of_activation = datetime.now().strftime("%Y-%m-%d")
        if (
            not member_name
            or not member_age
            or not member_gender
            or not member_number
            or not member_duration
            or not member_fees
            or not payment_method
        ):
            self.reset_form()
            messagebox.showerror(
                "Input Error",
                "Please ensure all required fields are filled out before proceeding.",
            )
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO members
                (name, age, gender, phone_number, duration, fees, payment_method, date_of_activation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    member_name,
                    member_age,
                    member_gender,
                    member_number,
                    member_duration,
                    ("Rs " + member_fees),
                    payment_method,
                    date_of_activation,
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return
        finally:
            conn.close()
        self.reset_form()
        messagebox.showinfo(
            "Registration Successful!",
            f"{member_name} registered successfully with the following details:\n\n"
            f"• Age: {member_age}\n"
            f"• Gender: {member_gender}\n"
            f"• Phone Number: {member_number}\n"
            f"• Membership Duration: {member_duration} months\n"
            f"• Membership Fees: Rs {member_fees}\n"
            f"• Payment Method: {payment_method}",
        )

    def show_member_details(self):
        """Display member details in a table format."""
        title_label = tk.Label(
            self.background_image,
            text="View Member Details",
            font=("Segoe UI", 20, "bold"),
        )
        title_label.pack(pady=20)
        outer_frame = tk.Frame(self.background_image, bd=2, relief=tk.SOLID)
        outer_frame.pack(padx=10, fill=tk.BOTH, expand=True)
        inner_frame = tk.Frame(outer_frame)
        inner_frame.pack(padx=(15, 0), fill=tk.BOTH, expand=True)
        month_options = self.get_month_options() or ["No Data Available"]
        self.current_month = datetime.now().strftime("%B %Y")
        if self.current_month in month_options:
            self.selected_month = tk.StringVar(value=self.current_month)
        else:
            self.selected_month = tk.StringVar(value=month_options[0])
        month_dropdown = tk.OptionMenu(inner_frame, self.selected_month, *month_options)
        month_dropdown.pack(pady=5, anchor=tk.CENTER)
        month_dropdown.config(bg="Blue", fg="white", font=("Segoe UI", 10, "bold"))
        self.selected_month.trace_add("write", lambda *args: self.populate_treeview())
        self.tree = ttk.Treeview(
            inner_frame,
            columns=(
                "id",
                "name",
                "age",
                "gender",
                "phone_number",
                "duration",
                "fees",
                "Payment",
                "date_of_activation",
                "expiration_date",
                "status",
            ),
            show="headings",
            style="custom.Treeview",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("age", text="Age")
        self.tree.heading("gender", text="Gender")
        self.tree.heading("phone_number", text="Phone Number")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("fees", text="Fees")
        self.tree.heading("Payment", text="Payment")
        self.tree.heading("date_of_activation", text="Date of Activation")
        self.tree.heading("expiration_date", text="Expiration Date")
        self.tree.heading("status", text="Status")
        self.tree.column("id", width=10, anchor="center")
        self.tree.column("name", width=100, anchor="center")
        self.tree.column("age", width=20, anchor="center")
        self.tree.column("gender", width=30, anchor="center")
        self.tree.column("phone_number", width=100, anchor="center")
        self.tree.column("duration", width=50, anchor="center")
        self.tree.column("fees", width=30, anchor="center")
        self.tree.column("Payment", width=40, anchor="center")
        self.tree.column("date_of_activation", width=120, anchor="center")
        self.tree.column("expiration_date", width=120, anchor="center")
        self.tree.column("status", width=30, anchor="center")
        scrollbar = ttk.Scrollbar(
            inner_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.populate_treeview()
        base_frame = tk.Frame(outer_frame)
        base_frame.pack(side=tk.BOTTOM, anchor=tk.CENTER, pady=10)
        update_button = tk.Button(
            base_frame,
            bg="dark green",
            fg="white",
            font=("Segoe UI", 13, "bold"),
            text="Update",
            command=self.update_record,
        )
        update_button.pack(side=tk.LEFT, padx=20)
        delete_button = tk.Button(
            base_frame,
            bg="red",
            fg="white",
            font=("Segoe UI", 13, "bold"),
            text="Delete",
            command=self.delete_record,
        )
        delete_button.pack(side=tk.RIGHT)
        self.tree.bind("<Double-1>", self.on_click)
        style = ttk.Style()
        style.configure("custom.Treeview.Heading", font=("Segoe UI", 14, "bold"))
        style.configure("custom.Treeview", font=("Segoe UI", 14), rowheight=30)
        style.map("custom.Treeview", background=[("selected", "#347083")])

    def populate_treeview(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            selected_month_display = self.selected_month.get()
            if selected_month_display != "No Data Available":
                selected_month_db = datetime.strptime(
                    selected_month_display, "%B %Y"
                ).strftime("%Y-%m")
                cursor.execute(
                    """
                    SELECT id, name, age, gender, phone_number, duration, fees, payment_method, date_of_activation,expiration_date, status
                    FROM members
                    WHERE strftime('%Y-%m', date_of_activation) = ?
                    """,
                    (selected_month_db,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, name, age, gender, phone_number, duration, fees, payment_method, date_of_activation, expiration_date, status
                    FROM members
                    """
                )
            rows = cursor.fetchall()
            conn.close()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def update_record(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No record selected to update.")
        else:
            selected_item = self.tree.item(selected_items[0])
            self.show_update_member(selected_item)

    def show_update_member(self, item):
        self.create_member_window(
            "Update Member Details ", lambda: self.update_member(item)
        )
        values = item["values"]
        self.entry_name.insert(0, values[1])
        self.age_choice.set(values[2])
        self.gender.set(values[3])
        self.entry_number.insert(0, values[4])
        self.duration_choice.set(values[5])
        fees_value = values[6].replace("Rs", "").strip()
        self.entry_fees.insert(0, fees_value)
        self.payment_method.set(values[7])
        self.date_of_activation_entry.delete(0, tk.END)
        self.date_of_activation_entry.insert(0, values[8])
        self.status_choice.set(values[10])

    def create_member_window(self, title, submit_command):
        """Create a window for adding member details."""
        self.member_window = tk.Toplevel(self.root)
        self.member_window.title(title)
        self.member_window.resizable(False, False)
        self.member_window.geometry("+400+50")
        self.member_window.grab_set()
        self.member_window.focus()
        BG_COLOR = "blue"
        FONT_MEDIUM = ("Segoe UI", 16, "bold")
        FONT_SMALL = ("Segoe UI", 12)
        add_member_frame = tk.Frame(self.member_window, bd=2, relief=tk.SOLID)
        add_member_frame.pack(pady=10, padx=10)
        labels_text = [
            "Name:",
            "Phone Number:",
            "Membership Fees (Rs):",
            "Date of Activation:",
            "Age:",
            "Gender:",
            "Membership Duration (months):",
            "Status:",
            "Payment Method:",
        ]
        for i, text in enumerate(labels_text):
            tk.Label(add_member_frame, font=FONT_MEDIUM, text=text).grid(
                row=i, column=0, pady=10, padx=(20, 0), sticky=tk.E
            )
        vcmd_text = (add_member_frame.register(self.validate_input), "%P", "letters")
        vcmd_numeric = (add_member_frame.register(self.validate_input), "%P", "numeric")
        self.entry_name = tk.Entry(
            add_member_frame,
            width=25,
            font=FONT_MEDIUM,
            validate="key",
            validatecommand=vcmd_text,
        )
        self.entry_name.grid(row=0, column=1, padx=(0, 20))
        self.entry_name.focus()
        self.entry_number = tk.Entry(
            add_member_frame,
            width=25,
            font=FONT_MEDIUM,
            validate="key",
            validatecommand=vcmd_numeric,
        )
        self.entry_number.grid(row=1, column=1, padx=(0, 20))
        self.entry_fees = tk.Entry(
            add_member_frame,
            width=15,
            font=FONT_MEDIUM,
            validate="key",
            validatecommand=vcmd_numeric,
        )
        self.entry_fees.grid(row=2, column=1, sticky=tk.W)
        one_month_back = date.today() - timedelta(days=30)
        self.date_of_activation_entry = DateEntry(
            add_member_frame,
            font=("Segoe UI", 12),
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-MM-dd",
            mindate=one_month_back,
        )
        self.date_of_activation_entry.grid(row=3, column=1, sticky=tk.W)
        self.date_of_activation_entry.bind("<KeyPress>", self.disable_key_input)
        age_options = [str(i) for i in range(1, 101)]
        self.age_choice = tk.StringVar(add_member_frame)
        self.age_choice.set("Select Age")
        age_menu = tk.OptionMenu(add_member_frame, self.age_choice, *age_options)
        age_menu.grid(row=4, column=1, sticky=tk.W)
        age_menu.config(bg=BG_COLOR, fg="white", font=FONT_SMALL)
        self.gender = tk.StringVar(add_member_frame)
        self.gender.set("Select")
        gender_menu = tk.OptionMenu(add_member_frame, self.gender, "Male", "Female")
        gender_menu.grid(row=5, column=1, sticky=tk.W)
        gender_menu.config(bg=BG_COLOR, fg="white", font=FONT_SMALL)
        duration_options = [f"{i} months" for i in range(1, 13)]
        self.duration_choice = tk.StringVar(add_member_frame)
        self.duration_choice.set("Select")
        duration_menu = tk.OptionMenu(
            add_member_frame, self.duration_choice, *duration_options
        )
        duration_menu.grid(row=6, column=1, sticky=tk.W)
        duration_menu.config(bg=BG_COLOR, fg="white", font=FONT_SMALL)
        self.status_choice = tk.StringVar(value="Select")
        status_menu = tk.OptionMenu(
            add_member_frame, self.status_choice, "Active", "Inactive"
        )
        status_menu.grid(row=7, column=1, sticky=tk.W)
        status_menu.config(bg=BG_COLOR, fg="white", font=FONT_SMALL)
        self.payment_method = tk.StringVar(add_member_frame)
        self.payment_method.set("Select")
        payment_menu = tk.OptionMenu(
            add_member_frame, self.payment_method, "Online", "Cash"
        )
        payment_menu.grid(row=8, column=1, sticky=tk.W)
        payment_menu.config(bg=BG_COLOR, fg="white", font=FONT_SMALL)
        buttons_frame = tk.Frame(add_member_frame)
        buttons_frame.grid(row=9, column=0, columnspan=2, pady=15, padx=5)
        submit_button = tk.Button(
            buttons_frame,
            text="Submit",
            command=submit_command,
            font=("Segoe UI", 12, "bold"),
            bg="Forest Green",
            fg="white",
        )
        submit_button.grid(row=0, column=0, ipadx=10)

    def disable_key_input(self, event):
        """Disable key input for the DateEntry except for Backspace."""
        if event.keysym == "BackSpace":
            return
        return "break"

    def update_member(self, item):
        updated_values = (
            item["values"][0],
            self.entry_name.get(),
            self.age_choice.get(),
            self.gender.get(),
            self.entry_number.get(),
            self.duration_choice.get(),
            "Rs " + self.entry_fees.get(),
            self.payment_method.get(),
            self.status_choice.get(),
            self.date_of_activation_entry.get_date(),
        )
        try:
            if (
                any(field.strip() == "" for field in updated_values[1:9])
                or not self.entry_fees.get().strip()
            ):
                messagebox.showerror(
                    "Input Error",
                    "Please ensure all required fields are filled out before proceeding.",
                )
                return
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """ UPDATE members SET name=?, age=?, gender=?, phone_number=?, duration=?, fees=?,payment_method=?,status=?,date_of_activation=? WHERE id=? """,
                (*updated_values[1:], updated_values[0]),
            )
            conn.commit()
            conn.close()
            self.populate_treeview()
            self.member_window.destroy()
            messagebox.showinfo("Success", "Member updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update member: {str(e)}")

    def delete_record(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No record selected to delete.")
        else:
            confirm = messagebox.askyesno(
                "Confirm Deletion", "Are you sure you want to delete this member?"
            )
            if confirm:
                selected_item = self.tree.item(selected_items[0])
                record_id = selected_item["values"][0]
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM members WHERE id=?", (record_id,))
                    conn.commit()
                    conn.close()
                    self.populate_treeview()
                    messagebox.showinfo("Success", "Member deleted successfully.")
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"An error occurred: {e}")

    def on_click(self, event):
        """Event handler for clicking on a row in the treeview."""
        try:
            col = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            if not item or not col or col != "#2":
                return
            col_index = 1
            cell_data = self.tree.item(item, "values")[col_index]
            self.show_tooltip(cell_data)
        except IndexError:
            pass
        except Exception as e:
            messagebox.showerror(
                "Selection Error",
                "An unexpected error occurred while processing your selection.\n\n"
                f"Error details: {str(e)}",
            )

    def show_tooltip(self, text):
        """Displays a tooltip with the provided content near the selected row in the treeview."""
        try:
            if (
                hasattr(self, "tooltip")
                and isinstance(self.tooltip, tk.Toplevel)
                and self.tooltip.winfo_exists()
            ):
                self.tooltip.destroy()
            x, y, _, _ = self.tree.bbox(self.tree.focus())
            if x and y:
                self.tooltip = tk.Toplevel(self.root, bd=2, relief=tk.SOLID)
                self.tooltip.resizable(False, False)
                self.tooltip.geometry("500x50+15+40")
                self.tooltip.wm_overrideredirect(True)
                text_widget = tk.Label(
                    self.tooltip,
                    text=text,
                    bg="yellow",
                    font=("Segoe UI", 20, "bold"),
                    anchor="w",
                )
                text_widget.pack(fill=tk.BOTH, expand=True)
                self.tooltip.after(5000, self.tooltip.destroy)
        except Exception as e:
            messagebox.showerror(
                "Tooltip Error",
                "An error occurred while trying to display the tooltip.\n\n"
                f"Error details: {str(e)}",
            )

    def show_gym_accounts(self):
        """Display Gym Accounts information."""
        content_label = tk.Label(
            self.background_image, text="Gym Accounts", font=("Segoe UI", 20, "bold")
        )
        content_label.pack(pady=20)
        accounts_frame = tk.Frame(self.background_image)
        accounts_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        self.active_inactive_frame = tk.Frame(accounts_frame, bd=2, relief="solid")
        self.active_inactive_frame.grid(
            row=0, column=0, padx=20, pady=10, sticky="nsew"
        )
        self.Notification_frame = tk.Frame(accounts_frame, bd=2, relief="solid")
        self.Notification_frame.grid(
            row=0, column=1, padx=(0, 20), pady=10, sticky="nsew"
        )
        accounts_frame.grid_columnconfigure(0, weight=0)
        accounts_frame.grid_columnconfigure(1, weight=3)
        accounts_frame.grid_rowconfigure(0, weight=1)
        self.create_month_selection()
        self.view_inactive_members(self.Notification_frame)
        self.view_monthly_members()

    def create_month_selection(self):
        """Create a dropdown for selecting month and a button to view members."""
        content_label = tk.Label(
            self.active_inactive_frame,
            text="Member Details",
            font=("Segoe UI", 15, "bold"),
        )
        content_label.grid(row=0, column=0, pady=5)
        section_frame = tk.Frame(self.active_inactive_frame, bd=2, relief="solid")
        section_frame.grid(row=1, column=0, pady=10)
        month_label = tk.Label(
            section_frame, text="Select Month:", font=("Segoe UI", 16)
        )
        month_label.grid(row=0, column=0, padx=10, pady=5)
        month_options = self.get_month_options() or ["No Data Available"]
        self.current_month = datetime.now().strftime("%B %Y")
        if self.current_month in month_options:
            self.selected_month = tk.StringVar(value=self.current_month)
        else:
            self.selected_month = tk.StringVar(value=month_options[0])
        month_dropdown = tk.OptionMenu(
            section_frame, self.selected_month, *month_options
        )
        month_dropdown.grid(row=0, column=1, padx=10, pady=5)
        view_month_button = tk.Button(
            section_frame,
            text="View Members",
            font=("Segoe UI", 12),
            command=self.view_monthly_members,
        )
        view_month_button.grid(row=1, column=0, columnspan=2, pady=10)

    def get_month_options(self):
        """Returns a list of months available in the database for selecting."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT strftime('%Y-%m', date_of_activation) FROM members ORDER BY date_of_activation DESC"
        )
        months = [row[0] for row in cursor.fetchall()]
        conn.close()
        formatted_months = [
            datetime.strptime(month, "%Y-%m").strftime("%B %Y") for month in months
        ]
        return formatted_months

    def view_monthly_members(self):
        """Displays the active and inactive members for the selected month."""
        selected_month = self.selected_month.get()
        if selected_month == "No Data Available":
            return
        month_year = datetime.strptime(selected_month, "%B %Y").strftime("%Y-%m")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                COUNT(*) AS total_count,
                COALESCE(SUM(CAST(REPLACE(fees, 'Rs', '') AS REAL)), 0) AS total_fees
            FROM members
            WHERE strftime('%Y-%m', date_of_activation) = ?""",
            (month_year,),
        )
        new_members_details = cursor.fetchone() or (0, 0)
        cursor.execute(
            """SELECT COUNT(*) AS active_member_count
            FROM members
            WHERE status = 'Active'"""
        )
        active_member_count = cursor.fetchone()[0]
        cursor.execute(
            """SELECT COUNT(*)
            FROM members
            WHERE status = 'Inactive' AND strftime('%Y-%m', expiration_date) = ?""",
            (month_year,),
        )
        inactive_member_count = cursor.fetchone()[0] or 0
        conn.close()
        self.clear_sections()
        selected_month_display = (
            "Current Month" if selected_month == self.current_month else selected_month
        )
        self.create_members_section(
            self.active_inactive_frame,
            f"Members details for {selected_month_display}.",
            new_members_details,
            active_member_count,
            inactive_member_count,
            2,
        )

    def clear_sections(self):
        """Clear only the sections with 'Members details for'."""
        for widget in self.active_inactive_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        label_text = child.cget("text")
                        if "Members details for" in label_text:
                            widget.destroy()
                            break

    def create_members_section(
        self, parent, title, new_member_data, active_data, inactive_data, row
    ):
        """Create a section for displaying active and inactive member data."""
        section_frame = tk.Frame(parent, bd=2, relief="solid")
        section_frame.grid(row=row, column=0, pady=10, padx=10)
        title_label = tk.Label(section_frame, text=title, font=("Segoe UI", 18, "bold"))
        title_label.grid(row=0, column=0, padx=10, pady=5)
        total_members, total_fees = new_member_data
        total_label = tk.Label(
            section_frame,
            text=f"Members Added: {total_members}",
            font=("Segoe UI", 16),
        )
        total_label.grid(row=1, column=0, padx=10, pady=5)
        Total_fees_label = tk.Label(
            section_frame, text=f"Total Fees: Rs {total_fees}", font=("Segoe UI", 16)
        )
        Total_fees_label.grid(row=2, column=0, padx=10, pady=5)
        if "Members details for Current Month." in title:
            active_label = tk.Label(
                section_frame,
                text=f"Active Members Till Now: {active_data}",
                font=("Segoe UI", 16),
            )
            active_label.grid(row=3, column=0, padx=10, pady=5)
            inactive_label = tk.Label(
                section_frame,
                text=f"Inactive Members: {inactive_data}",
                font=("Segoe UI", 16),
            )
            inactive_label.grid(row=4, column=0, padx=10, pady=5)

    def view_inactive_members(self, Notification_frame):
        """Displays the inactive members."""
        inner_frame = tk.Frame(Notification_frame)
        inner_frame.pack(padx=(15, 0), fill=tk.BOTH, expand=True)
        label = tk.Label(
            inner_frame,
            text="Inactive Members Details",
            font=("Segoe UI", 15, "bold"),
        )
        label.pack(pady=10)
        self.tree = ttk.Treeview(
            inner_frame,
            columns=("id", "name", "phone_number", "duration", "Inactivation_date"),
            show="headings",
            style="Custom.Treeview",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("phone_number", text="Phone Number")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("Inactivation_date", text="Inactivation Date")
        self.tree.column("id", width=10, anchor="center")
        self.tree.column("name", width=60, anchor="center")
        self.tree.column("phone_number", width=80, anchor="center")
        self.tree.column("duration", width=50, anchor="center")
        self.tree.column("Inactivation_date", width=120, anchor="center")
        self.expiration_month = datetime.now().strftime("%Y-%m")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, name, phone_number , duration, expiration_date
                FROM members
                WHERE status = 'Inactive' AND strftime('%Y-%m', expiration_date) = ?""",
                (self.expiration_month,),
            )
            rows = cursor.fetchall()
            conn.close()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve members: {str(e)}")
        scrollbar = ttk.Scrollbar(
            inner_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        base_frame = tk.Frame(Notification_frame)
        base_frame.pack(side=tk.BOTTOM, anchor=tk.CENTER, pady=10)
        update_button = tk.Button(
            base_frame,
            bg="dark green",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            text="Update",
            command=self.update_inactive,
        )
        update_button.pack(side=tk.LEFT, padx=20, ipadx=10)
        update_button = tk.Button(
            base_frame,
            bg="red",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            text="Alert",
            command=self.send_whatsapp_message,
        )
        update_button.pack(side=tk.RIGHT, ipadx=11)
        self.tree.bind("<Double-1>", self.on_click)
        self.style = ttk.Style()
        self.style.configure("Custom.Treeview.Heading", font=("Segoe UI", 14, "bold"))
        self.style.configure("Custom.Treeview", font=("Segoe UI", 14), rowheight=31)
        self.style.map("Custom.Treeview", background=[("selected", "#347083")])

    def update_inactive(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No record selected to update.")
        else:
            selected_item = self.tree.item(selected_items[0])
            self.show_update_inactive(selected_item)

    def show_update_inactive(self, item):
        """Display the update window for an inactive member's details."""
        self.create_inactive_window(
            "Update Inactive Details", lambda: self.update_inactive_member(item)
        )
        values = item["values"]
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """SELECT name, phone_number, duration, fees, date_of_activation, status
                FROM members
                WHERE id = ?""",
                (values[0],),
            )
            row = cursor.fetchone()
            if row:
                self.entry_name.insert(0, row[0])
                self.entry_name.config(state=tk.DISABLED)
                self.entry_number.insert(0, row[1])
                self.entry_number.config(state=tk.DISABLED)
                self.duration_choice.set(row[2])
                fees_value = row[3].replace("Rs", "").strip()
                self.entry_fees.insert(0, fees_value)
                self.date_of_activation_entry.config(state=tk.NORMAL)
                self.date_of_activation_entry.delete(0, tk.END)
                self.date_of_activation_entry.insert(0, row[4])
                self.status_choice.set(row[5])
            else:
                messagebox.showerror("Error", "Member not found.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def create_inactive_window(self, title, submit_command):
        self.member_window = tk.Toplevel(self.root)
        self.member_window.title(title)
        self.member_window.resizable(False, False)
        self.member_window.geometry("+615+125")
        self.member_window.grab_set()
        self.member_window.focus()
        add_member_frame = tk.Frame(self.member_window, bd=2, relief=tk.SOLID)
        add_member_frame.pack(pady=10, padx=10)
        labels_text = [
            "Name:",
            "Phone Number:",
            "Membership Fees (Rs):",
            "Status:",
            "Membership Duration (months):",
            "Date of Activation:",
        ]
        for i, text in enumerate(labels_text):
            tk.Label(
                add_member_frame,
                font=("Segoe UI", 16, "bold"),
                text=text,
            ).grid(row=i, column=0, padx=(20, 0), pady=10, sticky=tk.E)
        vcmd_numeric = (add_member_frame.register(self.validate_input), "%P", "numeric")
        self.entry_name = tk.Entry(
            add_member_frame,
            font=("Segoe UI", 16, "bold"),
            validate="key",
            justify="center",
        )
        self.entry_number = tk.Entry(
            add_member_frame,
            font=("Segoe UI", 16, "bold"),
            validate="key",
            justify="center",
        )
        self.entry_fees = tk.Entry(
            add_member_frame,
            font=("Segoe UI", 14),
            validate="key",
            validatecommand=vcmd_numeric,
            width=10,
        )
        entries = [self.entry_name, self.entry_number, self.entry_fees]
        for i, entry in enumerate(entries):
            entry.grid(row=i, column=1, padx=(0, 20), sticky=tk.W)
        self.status_choice = tk.StringVar(value="Select")
        status_menu = tk.OptionMenu(
            add_member_frame, self.status_choice, "Active", "Inactive"
        )
        status_menu.config(bg="blue", fg="white", font=("Segoe UI", 12, "bold"))
        status_menu.grid(row=3, column=1, sticky=tk.W)
        duration_options = [f"{i} months" for i in range(1, 13)]
        self.duration_choice = tk.StringVar(value="Select")
        duration_menu = tk.OptionMenu(
            add_member_frame, self.duration_choice, *duration_options
        )
        duration_menu.config(bg="Blue", fg="white", font=("Segoe UI", 11, "bold"))
        duration_menu.grid(row=4, column=1, sticky=tk.W)
        date_back = date.today() - timedelta(days=10)
        self.date_of_activation_entry = DateEntry(
            add_member_frame,
            font=("Segoe UI", 12),
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-MM-dd",
            mindate=date_back,
        )
        self.date_of_activation_entry.grid(row=5, column=1, sticky=tk.W)
        self.date_of_activation_entry.bind("<KeyPress>", self.disable_key_input)
        self.update_date_entry_state()
        self.status_choice.trace_add(
            "write", lambda *args: self.update_date_entry_state()
        )
        buttons_frame = tk.Frame(add_member_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=15, padx=5)
        submit_button = tk.Button(
            buttons_frame,
            text="Submit",
            command=submit_command,
            font=("Segoe UI", 12, "bold"),
            bg="Forest Green",
            fg="white",
        )
        submit_button.grid(row=0, column=0, ipadx=10)

    def update_date_entry_state(self):
        status = self.status_choice.get()
        if status == "Inactive":
            self.date_of_activation_entry.config(state=tk.DISABLED)
        else:
            self.date_of_activation_entry.config(state=tk.NORMAL)

    def update_inactive_member(self, item):
        updated_values = (
            item["values"][0],
            self.duration_choice.get(),
            "Rs " + self.entry_fees.get(),
            self.status_choice.get(),
            self.date_of_activation_entry.get_date(),
        )
        try:
            if (
                any(field.strip() == "" for field in updated_values[1:4])
                or not updated_values[3]
                or not updated_values[4]
            ):
                messagebox.showerror("Error", "Please fill in all required fields.")
                self.member_window.grab_set()
                return
            if updated_values[3] != "Active":
                messagebox.showerror("Error", "Activation is required.")
                self.member_window.grab_set()
                return
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE members
                    SET duration = ?, fees = ?, status = ?, date_of_activation = ?
                    WHERE id = ?
                    """,
                    (
                        updated_values[1],
                        updated_values[2],
                        updated_values[3],
                        updated_values[4],
                        updated_values[0],
                    ),
                )
            self.member_window.destroy()
            self.show_content("Gym Accounts")
            messagebox.showinfo("Success", "Member activated successfully.")
        except Exception as e:
            self.member_window.destroy()
            messagebox.showerror("Error", f"Failed to update member: {str(e)}")

    def open_whatsapp_web(self):
        """Open WhatsApp Web in a new window and wait for user confirmation."""
        webbrowser.open("https://web.whatsapp.com/")
        time.sleep(10)

    def is_whatsapp_logged_in(self):
        """Check if logged into WhatsApp Web and provide an option to stop."""
        self.root.withdraw()
        try:
            self.open_whatsapp_web()
            if messagebox.askyesno(
                "WhatsApp Login", "Are you logged into WhatsApp Web?"
            ):
                return True
            else:
                self.root.deiconify()
                self.root.state("zoomed")
                return False
        except Exception as e:
            self.root.deiconify()
            self.root.state("zoomed")
            messagebox.showerror("Error", f"Login check failed: {str(e)}")
            return False

    def send_whatsapp_message(self):
        """Send WhatsApp messages to a list of users if logged in."""
        self.message_count = self.load_message_count()
        self.license_valid, expiration_date = self.load_license_key_status()
        if self.message_count >= 20:
            messagebox.showwarning(
                "License Required",
                "You've reached your free limit of 20 messages. To continue enjoying our services without interruption, please enter a valid license key.",
            )
            self.create_license_key_interface()
            return
        if not self.license_valid and expiration_date is not None:
            messagebox.showwarning(
                "License Required",
                f"Your license key has expired on {expiration_date}. To restore full functionality, please enter a valid license key to continue using our services.",
            )
            self.create_license_key_interface()
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, name, phone_number, duration, expiration_date FROM members
                WHERE status = 'Inactive' AND strftime('%Y-%m', expiration_date) = ?
                AND notified = 'False'""",
                (self.expiration_month,),
            )
            rows = cursor.fetchall()
            conn.close()
            if not rows:
                messagebox.showinfo(
                    "No Members to Notify",
                    "All inactive members have already been notified.",
                )
                return
            if not self.is_whatsapp_logged_in():
                messagebox.showerror(
                    "WhatsApp Login Error",
                    "WhatsApp Web is not logged in. Please log in and try again.",
                )
                return
            for row in rows:
                self.process_row_and_send_message(row)
                self.message_count += 1
                self.save_app_data(message_count=self.message_count)
            self.root.deiconify()
            self.root.state("zoomed")
            messagebox.showinfo(
                "All Inactive Members Notified!",
                "All inactive members have been successfully alerted about their membership status!",
            )
        except Exception as e:
            self.root.deiconify()
            self.root.state("zoomed")
            messagebox.showerror("Error", f"Failed to send messages: {str(e)}")

    def load_message_count(self):
        """Load the message count from the app_data table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT message_count FROM app_data ORDER BY id DESC LIMIT 1"
                )
                result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return 0

    def load_license_key_status(self):
        """Load the license key expiration date from the app_data table and check its validity."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT license_key_expiration FROM app_data ORDER BY id DESC LIMIT 1"
                )
                result = cursor.fetchone()
            expiration_date_str = result[0] if result else None
            if expiration_date_str is None:
                return False, None
            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d").date()
            is_valid = datetime.now().date() <= expiration_date
            return is_valid, expiration_date
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return False, None

    def save_app_data(self, message_count=None, license_key_expiration=None):
        """Save the message count and license_key_expiration to the app_data table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM app_data LIMIT 1")
                exists = cursor.fetchone()
                if exists:
                    cursor.execute(
                        """
                        UPDATE app_data
                        SET message_count = COALESCE(?, message_count),
                            license_key_expiration  = COALESCE(?, license_key_expiration)
                        WHERE id = ?
                        """,
                        (message_count, license_key_expiration, exists[0]),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO app_data (message_count, license_key_expiration)
                        VALUES (?, ?)
                        """,
                        (message_count, license_key_expiration),
                    )
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def create_license_key_interface(self):
        """Create the license key entry interface and display license expiration message."""
        self.clear_main_frame()
        self.center_frame = tk.Frame(self.background_image)
        self.center_frame.pack(expand=True, fill=tk.NONE)
        title_label = tk.Label(
            self.center_frame,
            text="License Key Information",
            font=("Arial", 25, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        message_label = tk.Label(
            self.center_frame,
            text="Your license for the WhatsApp API has expired. Please renew to continue using the service.",
            font=("Arial", 20, "bold"),
            fg="red",
            wraplength=700,
        )
        message_label.grid(row=1, column=0, padx=20, columnspan=2)
        license_label = tk.Label(
            self.center_frame, text="Enter License Key:", font=("Arial", 15, "bold")
        )
        license_label.grid(row=2, column=0, pady=10, sticky="e")
        self.license_entry = tk.Entry(self.center_frame, width=30, font=("Arial", 15))
        self.license_entry.grid(row=2, column=1, pady=10, sticky="w")
        self.license_entry.focus()
        self.license_entry.bind("<KeyRelease>", self.process_license_key)
        buttons_frame = tk.Frame(self.center_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=25)
        validate_button = tk.Button(
            buttons_frame,
            text="Validate",
            font=("Arial", 13, "bold"),
            bg="blue",
            fg="white",
            command=lambda: self.check_license_key(self.license_entry.get()),
        )
        validate_button.pack(side="left")
        Cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            font=("Arial", 13, "bold"),
            bg="red",
            fg="white",
            command=lambda: self.show_content("Gym Accounts"),
        )
        Cancel_button.pack(side="right", padx=20)

    def process_license_key(self, event):
        """Validate and format the license key with '-' after every 4 characters, allowing only alphanumeric characters."""
        value = self.license_entry.get().upper()
        allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        filtered_value = "".join(char for char in value if char in allowed_chars)
        limited_value = filtered_value[:16]
        formatted_value = "-".join(
            limited_value[i : i + 4] for i in range(0, len(limited_value), 4)
        )
        self.license_entry.delete(0, tk.END)
        self.license_entry.insert(0, formatted_value)

    def check_license_key(self, license_key):
        """Check the license key and its expiration date against a file hosted on GitHub."""
        if not license_key:
            messagebox.showerror("Error", "License key cannot be empty.")
            return
        cleaned_license_key = license_key.replace("-", "").strip()
        if len(cleaned_license_key) != 16:
            messagebox.showerror("Error", "License key must be 16 characters long.")
            return
        url = "https://raw.githubusercontent.com/Nayush29/Gym-manager/master/License_keys.csv"
        try:
            response = requests.get(url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            required_columns = {"License Key", "Expiration Date"}
            if not required_columns.issubset(df.columns):
                messagebox.showerror(
                    "Error",
                    "It seems some required information is missing from the license data. Please reach out to support for assistance to resolve this issue.",
                )
                return
            matching_license = df[df["License Key"].str.strip() == license_key.strip()]
            if matching_license.empty:
                messagebox.showerror(
                    "License Key Not Found",
                    f"Oops! The license key '{license_key}' you entered was not found in our records. Please double-check and try again or contact support if you need assistance.",
                )
                return
            expiration_date_str = matching_license.iloc[0]["Expiration Date"].strip()
            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d").date()
            current_date = datetime.now().date()
            if current_date <= expiration_date:
                messagebox.showinfo(
                    "License Key Valid",
                    f"Congratulations! Your license key '{license_key}' is valid until {expiration_date}. You can now send WhatsApp messages seamlessly!",
                )
                self.save_app_data(license_key_expiration=expiration_date)
                self.show_content("Gym Accounts")
            else:
                messagebox.showerror(
                    "License Key Expired",
                    f"Unfortunately, your license key '{license_key}' expired on {expiration_date}. Please renew your license to continue using the service.",
                )
        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Error", f"Failed to fetch the license file from GitHub: {e}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def process_row_and_send_message(self, row):
        """Process each row of data and send a message."""
        member_id, name, phone_number, duration, expiration_date = row
        message = (
            f"Hi {name} 🙏\n"
            f"Your {duration} membership ended on {expiration_date} 🗓️\n"
            "Please renew to keep enjoying our services! 😊\n"
            "Thank you!"
        )
        phone_number_with_code = f"+91{phone_number}"
        self.send_message(phone_number_with_code, message)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE members SET notified = 'True' WHERE id = ?""", (member_id,)
            )

    def send_message(self, phone_number, message):
        """Send a WhatsApp message and handle errors."""
        try:
            kit.sendwhatmsg_instantly(phone_number, message, 15, True)
        except Exception as e:
            messagebox.showerror(
                "Message Sending Error",
                f"Error sending message to {phone_number}: {str(e)}",
            )


def main():
    root = tk.Tk()
    GymManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
