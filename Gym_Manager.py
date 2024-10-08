import os
import sqlite3
import sys
import tkinter as tk
import babel.numbers
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox, filedialog
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta


# Conversion functions
def adapt_date(date_obj):
    return date_obj.isoformat()


def convert_date(date_text):
    return datetime.strptime(date_text.decode("utf-8"), "%Y-%m-%d").date()


# Register conversion functions
sqlite3.register_adapter(date, adapt_date)
sqlite3.register_converter("date", convert_date)


class GymManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.state("zoomed")
        self.root.title("Gym Manager")

        self.db_path = os.path.join(os.path.dirname(sys.executable), "gym.db")
        self.config_path = os.path.join(
            os.path.dirname(sys.executable), "image_path.txt"
        )

        self.create_table()
        self.update_expired_members()
        self.setup_ui()

    def create_table(self):
        """Creates the 'members' and 'bills' table in the database if it doesn't exist."""
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
                address TEXT NOT NULL,
                duration TEXT NOT NULL,
                fees REAL NOT NULL,
                date_of_activation TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT Active CHECK (status IN ('Active', 'Inactive') )
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_type TEXT,
                amount REAL,
                date TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def update_expired_members(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            current_date = datetime.now().date()

            cursor.execute(
                "SELECT id, duration, date_of_activation FROM members WHERE status = 'Active'"
            )
            rows = cursor.fetchall()

            for member_id, duration_str, date_of_activation in rows:
                duration_months = int(duration_str.split()[0])
                activation_date = datetime.strptime(
                    date_of_activation, "%Y-%m-%d"
                ).date()
                expiration_date = activation_date + relativedelta(
                    months=duration_months
                )

                if current_date > expiration_date:
                    cursor.execute(
                        "UPDATE members SET status = 'Inactive' WHERE id = ?",
                        (member_id,),
                    )

            conn.commit()

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def setup_ui(self):
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
        self.load_and_resize_image()

        self.root.bind("<Configure>", self.on_resize)

        self.sidebar_frame = tk.Frame(self.background_image)
        self.sidebar_frame.pack(padx=30, side=tk.LEFT)

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

    def load_and_resize_image(self):
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
            self.background_image.image = self.photo
        except Exception as e:
            pass

    def on_resize(self, event):
        """Handle window resize events to adjust the background image."""
        self.load_and_resize_image()

    def create_buttons(self):
        """Create and add buttons to the sidebar."""
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
                    command=lambda: self.root.destroy(),
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
        """Function to clear the main frame before loading new content"""
        for widget in self.background_image.winfo_children():
            widget.destroy()

    def back_button(self):
        back_button = tk.Button(
            self.background_image,
            text="Back",
            font=("Segoe UI", 12, "bold"),
            command=self.recreate_sidebar,
        )
        back_button.pack(padx=10, pady=10, side="bottom", anchor="e", ipadx=20)

    def recreate_sidebar(self):
        """Recreate the sidebar and restore the initial layout."""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()

    def show_add_member(self):
        """Placeholder for Add Member."""
        tk.Label(
            self.background_image, text="Add Member", font=("Segoe UI", 20, "bold")
        ).pack(pady=30)

        add_member_frame = tk.Frame(self.background_image, bd=2, relief=tk.SOLID)
        add_member_frame.pack()

        labels = [
            "Name:",
            "Age:",
            "Gender:",
            "Phone Number:",
            "Membership Duration (months):",
            "Membership Fees (Rs):",
            "Address:",
        ]

        for i, text in enumerate(labels):
            tk.Label(add_member_frame, font=("Segoe UI", 14, "bold"), text=text).grid(
                row=i, column=0, pady=5, padx=5, sticky=tk.E
            )

        vcmd_text = (add_member_frame.register(self.validate_input), "%P", "letters")
        vcmd_numeric = (add_member_frame.register(self.validate_input), "%P", "numeric")

        self.entry_name = tk.Entry(
            add_member_frame,
            width=25,
            font=("Segoe UI", 16),
            validate="key",
            validatecommand=vcmd_text,
        )
        self.entry_name.grid(row=0, column=1, pady=20, padx=5)

        age_options = [str(i) for i in range(1, 101)]
        self.age_choice = tk.StringVar(add_member_frame)
        self.age_choice.set("Select Age")
        age_menu = tk.OptionMenu(add_member_frame, self.age_choice, *age_options)
        age_menu.grid(row=1, column=1, pady=5, padx=5)
        age_menu.config(bg="Blue", fg="white", font=("Segoe UI", 10, "bold"))

        self.gender = tk.StringVar()
        self.gender.set("Select")
        gender_menu = tk.OptionMenu(add_member_frame, self.gender, "Male", "Female")
        gender_menu.grid(row=2, column=1, pady=5, padx=5)
        gender_menu.config(bg="Blue", fg="white", font=("Segoe UI", 10, "bold"))

        self.entry_number = tk.Entry(
            add_member_frame,
            width=25,
            font=("Segoe UI", 16),
            validate="key",
            validatecommand=vcmd_numeric,
        )
        self.entry_number.grid(row=3, column=1, pady=5, padx=5)

        duration_options = [f"{i} months" for i in range(1, 13)]
        self.duration_choice = tk.StringVar(add_member_frame)
        self.duration_choice.set("Select")
        duration_menu = tk.OptionMenu(
            add_member_frame, self.duration_choice, *duration_options
        )
        duration_menu.grid(row=4, column=1, pady=5, padx=5)
        duration_menu.config(bg="Blue", fg="white", font=("Segoe UI", 10, "bold"))

        self.entry_fees = tk.Entry(
            add_member_frame,
            font=("Segoe UI", 16),
            validate="key",
            validatecommand=vcmd_numeric,
        )
        self.entry_fees.grid(row=5, column=1, pady=5, padx=5)

        self.entry_address = tk.Text(
            add_member_frame, height=5, width=30, font=("Segoe UI", 14)
        )
        self.entry_address.grid(row=6, column=1, pady=5, padx=10)
        self.entry_address.bind("<Key>", self.validate_text_input)

        buttons_frame = tk.Frame(add_member_frame)
        buttons_frame.grid(row=7, column=0, columnspan=2, pady=15, padx=5)

        tk.Button(
            buttons_frame,
            text="Register",
            command=self.register_member,
            font=("Segoe UI", 12, "bold"),
            bg="Forest Green",
            fg="white",
        ).grid(row=0, column=0, ipadx=10, padx=5)
        tk.Button(
            buttons_frame,
            text="Reset",
            command=self.reset_form,
            font=("Segoe UI", 12, "bold"),
            bg="#f2003c",
            fg="white",
        ).grid(row=0, column=1, ipadx=10, padx=5)

    def reset_form(self):
        """Reset the form fields to their default state."""
        self.entry_name.delete(0, tk.END)
        self.age_choice.set("Select Age")
        self.gender.set("Select")
        self.entry_number.delete(0, tk.END)
        self.entry_address.delete("1.0", tk.END)
        self.duration_choice.set("Select")
        self.entry_fees.delete(0, tk.END)

    def validate_input(self, input_str, mode):
        """Validates input based on the type specified."""
        if mode == "numeric":
            return input_str.isdigit() or input_str == ""
        elif mode == "letters":
            return all(char.isalpha() or char.isspace() for char in input_str)
        else:
            return False

    def validate_text_input(self, event):
        """Limits the text input to letters, numbers, spaces, backspace, dots, hyphens, commas, and equals signs."""
        allowed_chars = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,-="
        )

        input_str = event.char

        if input_str == "\b":
            return True
        elif input_str in allowed_chars:
            return True
        else:
            return "break"

    def register_member(self):
        """Registers a new member into the database with the provided details from the form."""
        member_name = self.entry_name.get()
        member_age = self.age_choice.get()
        member_gender = self.gender.get()
        member_number = self.entry_number.get()
        member_address = self.entry_address.get("1.0", tk.END).strip()
        member_duration = self.duration_choice.get()
        member_fees = self.entry_fees.get()
        date_of_activation = datetime.now().strftime("%Y-%m-%d")

        if (
            not member_name
            or not member_age
            or not member_gender
            or not member_number
            or not member_address
            or not member_duration
            or not member_fees
        ):
            self.reset_form()
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO members (name, age, gender, phone_number, address, duration, fees,date_of_activation) VALUES (?, ?, ?, ?, ?, ?, ? ,?)""",
            (
                member_name,
                member_age,
                member_gender,
                member_number,
                member_address,
                member_duration,
                ("Rs " + member_fees),
                date_of_activation,
            ),
        )
        conn.commit()
        conn.close()

        self.reset_form()

        messagebox.showinfo(
            "Registration",
            f"Registered {member_name} successfully!\nAge: {member_age}\nGender: {member_gender}\nPhone Number: {member_number}\nAddress: {member_address}\nMembership Duration:{member_duration}\nMembership Fees: Rs{member_fees}",
        )

    def show_member_details(self):
        """Display member details in a table format."""
        title_label = tk.Label(
            self.background_image,
            text="View Member Details",
            font=("Segoe UI", 20, "bold"),
        )
        title_label.pack(pady=(10, 0))

        outer_frame = tk.Frame(self.background_image, bd=2, relief=tk.SOLID)
        outer_frame.pack(pady=(10, 0), padx=10, fill=tk.BOTH, expand=True)

        inner_frame = tk.Frame(outer_frame)
        inner_frame.pack(pady=(10, 0), padx=(10, 0), fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            inner_frame,
            columns=(
                "id",
                "name",
                "age",
                "gender",
                "phone_number",
                "address",
                "duration",
                "fees",
                "date_of_activation",
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
        self.tree.heading("address", text="Address")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("fees", text="Fees")
        self.tree.heading("date_of_activation", text="Date of Activation")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=10, anchor="center")
        self.tree.column("name", width=100, anchor="center")
        self.tree.column("age", width=20, anchor="center")
        self.tree.column("gender", width=30, anchor="center")
        self.tree.column("phone_number", width=100, anchor="center")
        self.tree.column("address", width=200, anchor="w")
        self.tree.column("duration", width=50, anchor="center")
        self.tree.column("fees", width=50, anchor="center")
        self.tree.column("date_of_activation", width=120, anchor="center")
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
            font=("Segoe UI", 12, "bold"),
            text="Update",
            command=self.update_record,
        )
        update_button.pack(side=tk.LEFT, padx=20, ipadx=10)

        delete_button = tk.Button(
            base_frame,
            bg="red",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            text="Delete",
            command=self.delete_record,
        )
        delete_button.pack(side=tk.RIGHT, padx=(0, 18), ipadx=10)

        self.tree.bind("<Double-1>", self.on_click)

        style = ttk.Style()
        style.configure("custom.Treeview.Heading", font=("Segoe UI", 14, "bold"))
        style.configure("custom.Treeview", font=("Segoe UI", 14), rowheight=31)
        style.map("custom.Treeview", background=[("selected", "#347083")])

    def populate_treeview(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members")
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                self.tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve members: {str(e)}")

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
        self.entry_address.insert("1.0", values[5])
        self.duration_choice.set(values[6])
        fees_value = values[7].replace("Rs", "").strip()
        self.entry_fees.insert(0, fees_value)
        self.date_of_activation_entry.delete(0, tk.END)
        self.date_of_activation_entry.insert(0, values[8])
        self.status_choice.set(values[9])

    def update_member(self, item):
        updated_values = (
            item["values"][0],
            self.entry_name.get(),
            self.age_choice.get(),
            self.gender.get(),
            self.entry_number.get(),
            self.entry_address.get("1.0", tk.END).strip(),
            self.duration_choice.get(),
            "Rs " + self.entry_fees.get(),
            self.status_choice.get(),
            self.date_of_activation_entry.get_date(),
        )

        try:
            if (
                any(field.strip() == "" for field in updated_values[1:9])
                or self.entry_fees.get().strip() == ""
                or self.date_of_activation_entry.get_date() == ""
            ):
                self.member_window.destroy()
                messagebox.showerror("Error", "Please fill in all required fields.")
                return

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """ UPDATE members SET name=?, age=?, gender=?, phone_number=?, address=?, duration=?, fees=?,status=?,date_of_activation=? WHERE id=? """,
                (*updated_values[1:], updated_values[0]),
            )

            conn.commit()
            conn.close()
            self.populate_treeview()
            self.member_window.destroy()
            messagebox.showinfo("Success", "Member updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update member: {str(e)}")
            self.member_window.destroy()

    def create_member_window(self, title, submit_command):
        self.member_window = tk.Toplevel(self.root)
        self.member_window.title(title)
        self.member_window.resizable(False, False)
        self.member_window.geometry("+400+50")
        self.member_window.grab_set()
        self.member_window.focus()

        add_member_frame = tk.Frame(self.member_window, bd=2, relief=tk.SOLID)
        add_member_frame.pack(pady=10, padx=10)

        labels_text = [
            "Name:",
            "Phone Number:",
            "Membership Fees (Rs):",
            "Age:",
            "Gender:",
            "Membership Duration (months):",
            "Status:",
            "Date of Activation:",
            "Address:",
        ]

        for i, text in enumerate(labels_text):
            tk.Label(add_member_frame, font=("Segoe UI", 12, "bold"), text=text).grid(
                row=i, column=0, pady=5, padx=5, sticky=tk.E
            )

        vcmd_text = (add_member_frame.register(self.validate_input), "%P", "letters")
        vcmd_numeric = (add_member_frame.register(self.validate_input), "%P", "numeric")

        self.entry_name = tk.Entry(
            add_member_frame,
            font=("Segoe UI", 16),
            validate="key",
            validatecommand=vcmd_text,
        )
        self.entry_number = tk.Entry(
            add_member_frame,
            font=("Segoe UI", 16),
            validate="key",
            validatecommand=vcmd_numeric,
        )
        self.entry_fees = tk.Entry(
            add_member_frame,
            font=("Segoe UI", 16),
            validate="key",
            validatecommand=vcmd_numeric,
        )

        entries = [self.entry_name, self.entry_number, self.entry_fees]

        for i, entry in enumerate(entries):
            entry.grid(row=i, column=1, pady=5, padx=5)

        age_options = [str(i) for i in range(1, 101)]
        self.age_choice = tk.StringVar(value="Select Age")
        age_menu = tk.OptionMenu(add_member_frame, self.age_choice, *age_options)
        age_menu.grid(row=3, column=1, pady=5, padx=5)
        age_menu.config(bg="Blue", fg="white", font=("Segoe UI", 10, "bold"))

        self.gender = tk.StringVar(value="Select")
        gender_menu = tk.OptionMenu(add_member_frame, self.gender, "Male", "Female")
        gender_menu.config(bg="Blue", fg="white", font=("Segoe UI", 10, "bold"))
        gender_menu.grid(row=4, column=1, pady=5, padx=5)

        duration_options = [f"{i} months" for i in range(1, 13)]
        self.duration_choice = tk.StringVar(value="Select")
        duration_menu = tk.OptionMenu(
            add_member_frame, self.duration_choice, *duration_options
        )
        duration_menu.config(bg="Blue", fg="white", font=("Segoe UI", 10, "bold"))
        duration_menu.grid(row=5, column=1, pady=5, padx=5)

        self.status_choice = tk.StringVar(value="Select")
        status_menu = tk.OptionMenu(
            add_member_frame, self.status_choice, "Active", "Inactive"
        )
        status_menu.config(bg="blue", fg="white", font=("Segoe UI", 10, "bold"))
        status_menu.grid(row=6, column=1, pady=5, padx=5)

        one_month_back = date.today() - timedelta(days=30)
        self.date_of_activation_entry = DateEntry(
            add_member_frame,
            font=("Segoe UI", 12),
            background="darkblue",
            foreground="white",
            borderwidth=2,
            year=date.today().year,
            date_pattern="yyyy-MM-dd",
            mindate=one_month_back,
        )
        self.date_of_activation_entry.grid(row=7, column=1, pady=5, padx=5)
        self.date_of_activation_entry.bind("<KeyPress>", self.disable_key_input)

        self.entry_address = tk.Text(
            add_member_frame, height=3, width=30, font=("Segoe UI", 14)
        )
        self.entry_address.grid(row=8, column=1, pady=5, padx=10)
        self.entry_address.bind("<Key>", self.validate_text_input)

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
        if event.keysym == "BackSpace":
            return
        return "break"

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
                    messagebox.showerror("Error", f"Failed to delete member: {str(e)}")

    def on_click(self, event):
        """Event handler for clicking on a row in the treeview."""
        try:
            col = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            if col == "#2":
                col_index = 1
                cell_data = self.tree.item(item, "values")[col_index]
                self.show_tooltip(cell_data)
            elif col == "#6":
                col_index = 5
                cell_data = self.tree.item(item, "values")[col_index]
                self.show_tooltip(cell_data)
        except Exception as e:
            pass

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
                self.tooltip.geometry("520x60+830+25")
                self.tooltip.wm_overrideredirect(True)
                text_frame = tk.Frame(self.tooltip)
                text_frame.pack(fill=tk.BOTH, expand=True)
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
                text_widget = tk.Text(
                    text_frame,
                    wrap=tk.WORD,
                    yscrollcommand=scrollbar.set,
                    bg="yellow",
                    font=("Segoe UI", 14),
                    padx=5,
                    pady=5,
                )
                scrollbar.config(command=text_widget.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                text_widget.insert(tk.END, text)
                text_widget.config(state=tk.DISABLED)
                self.tooltip.after(5000, self.tooltip.destroy)
        except Exception as e:
            pass

    def show_gym_accounts(self):
        """Display Gym Accounts information."""
        content_label = tk.Label(
            self.background_image, text="Gym Accounts", font=("Segoe UI", 20, "bold")
        )
        content_label.pack(pady=10)

        accounts_frame = tk.Frame(self.background_image)
        accounts_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        active_count, inactive_count, total_bills_month = self.get_members_data()

        active_inactive_frame = tk.Frame(accounts_frame, bd=2, relief="solid")
        active_inactive_frame.grid(
            row=0, column=0, padx=(50, 0), pady=10, sticky="nsew"
        )

        self.create_members_section(
            active_inactive_frame, "Active Members", active_count, 0
        )
        self.create_members_section(
            active_inactive_frame, "Inactive Members", inactive_count, 1
        )
        self.create_members_section(
            active_inactive_frame, "Total Expense", total_bills_month, 2
        )

        bill_frame = tk.Frame(accounts_frame, bd=2, relief="solid")
        bill_frame.grid(row=0, column=1, padx=250, pady=10, sticky="nsew")

        self.create_bill_section(bill_frame)

    def get_members_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*),SUM(CAST(REPLACE(fees, 'Rs', '') AS REAL)) FROM members WHERE status = 'Active'"
        )
        active_count = cursor.fetchone()

        cursor.execute(
            "SELECT COUNT(*),SUM(CAST(REPLACE(fees, 'Rs', '') AS REAL)) FROM members WHERE status = 'Inactive'"
        )
        inactive_count = cursor.fetchone()

        cursor.execute(
            "SELECT SUM(CAST(REPLACE(amount, 'Rs ', '') AS REAL)) FROM bills WHERE strftime('%m', date) = strftime('%m', 'now')"
        )
        total_bills_month = cursor.fetchone()[0]

        conn.close()

        return active_count, inactive_count, total_bills_month

    def create_members_section(self, parent, title, count, row):
        section_frame = tk.Frame(parent, bd=2, relief="solid")
        section_frame.grid(row=row, column=0, pady=10, padx=10)

        if title == "Total Expense":
            total_bill_label = tk.Label(
                section_frame, text="Total Bill Expenses", font=("Segoe UI", 18, "bold")
            )
            total_bill_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

            bill_total_label = tk.Label(
                section_frame, text="Bill's Total", font=("Segoe UI", 18, "bold")
            )
            bill_total_label.grid(row=1, columnspan=2, padx=10, pady=5)

            if count is None:
                self.bill_total_count_label = tk.Label(
                    section_frame, text=f"Rs 0", font=("Segoe UI", 18)
                )
                self.bill_total_count_label.grid(row=2, column=0, columnspan=2)

            else:
                self.bill_total_count_label = tk.Label(
                    section_frame, text=f"Rs{count}", font=("Segoe UI", 18)
                )
                self.bill_total_count_label.grid(row=2, column=0, columnspan=2)
        else:

            title_label = tk.Label(
                section_frame, text=title, font=("Segoe UI", 18, "bold")
            )
            title_label.grid(row=0, column=0, padx=10, pady=5)

            count_label = tk.Label(
                section_frame, text=f"Count: {count[0]}", font=("Segoe UI", 16)
            )
            count_label.grid(row=1, column=0, padx=10, pady=5)

            if count[1] is None:
                total_fees_label = tk.Label(
                    section_frame, text=f"Total fees:Rs 0", font=("Segoe UI", 16)
                )
                total_fees_label.grid(row=2, column=0, padx=10, pady=5)

            else:
                total_fees_label = tk.Label(
                    section_frame,
                    text=f"Total fees:Rs {count[1]}",
                    font=("Segoe UI", 16),
                )
                total_fees_label.grid(row=2, column=0, padx=10, pady=5)

            if title == "Inactive Members":
                view_button = tk.Button(
                    section_frame,
                    bg="blue",
                    fg="white",
                    relief="raised",
                    text="View Inactive Members",
                    font=("Segoe UI", 12),
                    command=self.view_inactive_members,
                )
                view_button.grid(row=3, column=0, pady=10)

    def create_bill_section(self, parent):
        vcmd_text = (parent.register(self.validate_input), "%P", "letters")
        vcmd_numeric = (parent.register(self.validate_input), "%P", "numeric")

        bill_label = tk.Label(parent, text="Gym Bill's", font=("Segoe UI", 21, "bold"))
        bill_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        bill_type_label = tk.Label(
            parent, text="Bill Type", font=("Segoe UI", 16, "bold")
        )
        bill_type_label.grid(row=1, column=0, padx=5, pady=5)

        common_bill_types = ["Electricity", "Water", "Internet", "Custom"]
        self.bill_type_combobox = ttk.Combobox(
            parent,
            values=common_bill_types,
            font=("Segoe UI", 14),
            validate="key",
            validatecommand=vcmd_text,
        )
        self.bill_type_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.bill_type_combobox.set("Select or Enter Bill Type")

        amount_label = tk.Label(
            parent, text="Amount Rs.", font=("Segoe UI", 16, "bold")
        )
        amount_label.grid(row=2, column=0, padx=5, pady=5)

        self.amount_entry = tk.Entry(
            parent, font=("Segoe UI", 14), validate="key", validatecommand=vcmd_numeric
        )
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        date_label = tk.Label(parent, text="Date", font=("Segoe UI", 16, "bold"))
        date_label.grid(row=3, column=0, padx=5, pady=5)

        one_month_back = date.today() - timedelta(days=30)
        self.date_entry = DateEntry(
            parent,
            font=("Segoe UI", 12),
            background="darkblue",
            foreground="white",
            borderwidth=2,
            year=date.today().year,
            date_pattern="yyyy-MM-dd",
            mindate=one_month_back,
            validate="key",
            validatecommand=vcmd_numeric,
        )

        self.date_entry.grid(row=3, column=1, padx=5, pady=5)

        add_bill_button = tk.Button(
            parent,
            bg="blue",
            fg="white",
            relief="raised",
            text="Add Bill",
            font=("Segoe UI", 12),
            command=self.add_bill,
        )
        add_bill_button.grid(row=4, column=0, columnspan=2, pady=10, ipadx=10)

        bill_view_label = tk.Label(
            parent, text="Bill's view", font=("Segoe UI", 18, "bold")
        )
        bill_view_label.grid(row=5, columnspan=2, padx=5, pady=5)

        self.bills_treeview = ttk.Treeview(
            parent, columns=("ID", "Type", "Amount", "Date"), show="headings"
        )
        self.bills_treeview.heading("ID", text="ID")
        self.bills_treeview.heading("Type", text="Type")
        self.bills_treeview.heading("Amount", text="Amount")
        self.bills_treeview.heading("Date", text="Date")

        self.bills_treeview.column("ID", width=50, anchor="center")
        self.bills_treeview.column("Type", width=200, anchor="center")
        self.bills_treeview.column("Amount", width=150, anchor="center")
        self.bills_treeview.column("Date", width=150, anchor="center")

        self.bills_treeview.grid(row=6, column=0, columnspan=2, pady=5, padx=5)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 14, "bold"))
        style.configure("Treeview", font=("Segoe UI", 12))
        style.map("Treeview", background=[("selected", "#347083")])

        self.populate_bills_treeview()

    def populate_bills_treeview(self):
        for row in self.bills_treeview.get_children():
            self.bills_treeview.delete(row)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bills")
        bills = cursor.fetchall()
        conn.close()

        for bill in bills:
            self.bills_treeview.insert("", "end", values=bill)

    def add_bill(self):
        bill_type = self.bill_type_combobox.get()
        amount = self.amount_entry.get()
        date_value = self.date_entry.get()

        if bill_type in {"Select or Enter Bill Type", "Custom"} or not amount:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bills (bill_type, amount, date) VALUES (?, ?, ?)",
                (bill_type, f"Rs {amount}", date_value),
            )
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

        self.clear_main_frame()
        self.show_gym_accounts()
        self.back_button()
        messagebox.showinfo("Success", "Bill added successfully.")

        self.bill_type_combobox.set("Select or Enter Bill Type")
        self.amount_entry.delete(0, tk.END)
        self.date_entry.set_date(date.today())

    def view_inactive_members(self):
        if (
            hasattr(self, "top")
            and isinstance(self.top, tk.Toplevel)
            and self.top.winfo_exists()
        ):
            self.top.destroy()
        self.top = tk.Toplevel(self.root)
        self.top.title("View Inactive Members")
        self.top.geometry("1000x500+330+100")
        self.top.resizable(False, False)
        self.top.grab_set()
        self.top.focus()

        inner_frame = tk.Frame(self.top)
        inner_frame.pack(pady=(10, 0), padx=(10, 0), fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            inner_frame,
            columns=(
                "id",
                "name",
                "phone_number",
                "duration",
                "fees",
                "date_of_activation",
                "status",
            ),
            show="headings",
            style="Custom.Treeview",
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("phone_number", text="Phone Number")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("fees", text="Fees")
        self.tree.heading("date_of_activation", text="Date of Activation")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=10, anchor="center")
        self.tree.column("name", width=200, anchor="center")
        self.tree.column("phone_number", width=100, anchor="center")
        self.tree.column("duration", width=50, anchor="center")
        self.tree.column("fees", width=50, anchor="center")
        self.tree.column("date_of_activation", width=120, anchor="center")
        self.tree.column("status", width=30, anchor="center")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id,name,phone_number,duration,fees,date_of_activation,status FROM members WHERE status = 'Inactive'"
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

        base_frame = tk.Frame(self.top)
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

        close_button = tk.Button(
            base_frame,
            bg="red",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            text="Close",
            command=lambda: self.top.destroy(),
        )
        close_button.pack(side=tk.RIGHT, padx=(0, 18), ipadx=10)

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
        self.create_inactive_window(
            "Update inactive Details ", lambda: self.update_inactive_member(item)
        )
        values = item["values"]
        self.entry_name.insert(0, values[1])
        self.entry_name.config(state=tk.DISABLED)
        self.entry_number.insert(0, values[2])
        self.entry_number.config(state=tk.DISABLED)
        self.duration_choice.set(values[3])
        fees_value = values[4].replace("Rs", "").strip()
        self.entry_fees.insert(0, fees_value)
        self.date_of_activation_entry.config(state=tk.NORMAL)
        self.date_of_activation_entry.delete(0, tk.END)
        self.date_of_activation_entry.insert(0, values[5])
        self.status_choice.set(values[6])

    def create_inactive_window(self, title, submit_command):
        self.member_window = tk.Toplevel(self.root)
        self.member_window.title(title)
        self.member_window.resizable(False, False)
        self.member_window.geometry("+450+140")
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
            tk.Label(add_member_frame, font=("Segoe UI", 10, "bold"), text=text).grid(
                row=i, column=0, pady=5, padx=5, sticky=tk.E
            )

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
            entry.grid(row=i, column=1, pady=5, padx=5)

        self.status_choice = tk.StringVar(value="Select")
        status_menu = tk.OptionMenu(
            add_member_frame, self.status_choice, "Active", "Inactive"
        )
        status_menu.config(bg="blue", fg="white", font=("Segoe UI", 10, "bold"))
        status_menu.grid(row=3, column=1, pady=5, padx=5)

        duration_options = [f"{i} months" for i in range(1, 13)]
        self.duration_choice = tk.StringVar(value="Select")
        duration_menu = tk.OptionMenu(
            add_member_frame, self.duration_choice, *duration_options
        )
        duration_menu.config(bg="Blue", fg="white", font=("Segoe UI", 10, "bold"))
        duration_menu.grid(row=4, column=1, pady=5, padx=5)

        self.date_of_activation_entry = DateEntry(
            add_member_frame,
            font=("Segoe UI", 12),
            background="darkblue",
            foreground="white",
            borderwidth=2,
            year=date.today().year,
            date_pattern="yyyy-MM-dd",
            mindate=date.today(),
        )
        self.date_of_activation_entry.grid(row=5, column=1, pady=5, padx=5)
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

                cursor.execute(
                    """SELECT COUNT(*) FROM members WHERE status = 'Inactive'"""
                )
                inactive = cursor.fetchone()[0]

            self.member_window.destroy()
            self.clear_main_frame()
            self.show_gym_accounts()
            self.back_button()
            messagebox.showinfo("Success", "Member activated successfully.")

            if inactive > 0:
                self.view_inactive_members()
            else:
                self.top.destroy()

        except Exception as e:
            self.member_window.destroy()
            messagebox.showerror("Error", f"Failed to update member: {str(e)}")


def main():
    root = tk.Tk()
    GymManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
