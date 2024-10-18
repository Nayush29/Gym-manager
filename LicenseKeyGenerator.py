import csv
from datetime import datetime, timedelta
import random
import string
import subprocess
import os
import tkinter as tk
from tkinter import messagebox


class LicenseKeyGenerator:
    CSV_FILE_NAME = "License_keys.csv"
    GITHUB_REPO_PATH = (
        r"C:\Users\mayan\OneDrive\Documents\VS\Python Scripts\Gym Manager"
    )

    # Constants for messages
    INPUT_ERROR = (
        "Please enter a valid positive number for the expiration duration in months."
    )
    UNEXPECTED_ERROR = "An unexpected error occurred:\n{}"

    def __init__(self, root):
        self.root = root
        self.root.title("License Key Generator")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface components."""
        self.expiration_label = tk.Label(
            self.root,
            text="Enter the expiration duration in months.",
            font=("Arial", 13, "bold"),
        )
        self.expiration_label.pack(pady=10)

        self.expiration_entry = tk.Entry(self.root, font=("Arial", 16, "bold"))
        self.expiration_entry.pack(pady=5)

        self.output_label = tk.Label(self.root, text="", font=("Arial", 10, "bold"))
        self.output_label.pack(pady=10)

        self.generate_button = tk.Button(
            self.root,
            text="Generate Key",
            command=self.generate_key,
            bg="green",
            font=("Arial", 13, "bold"),
            fg="white",
        )
        self.generate_button.pack(pady=20)

    def generate_license_key(self):
        """Generate a random license key in the format AAAA-1234-BBBB-1234."""
        letters = "".join(random.choices(string.ascii_uppercase, k=4))
        numbers1 = "".join(random.choices(string.digits, k=4))
        letters2 = "".join(random.choices(string.ascii_uppercase, k=4))
        numbers2 = "".join(random.choices(string.digits, k=4))
        return f"{letters}-{numbers1}-{letters2}-{numbers2}"

    def save_key_to_csv(self, license_key, months):
        """Save the license key and its expiration type to a CSV file."""
        expiration_date = (datetime.now() + timedelta(days=30 * months)).date()
        csv_file_path = os.path.join(self.GITHUB_REPO_PATH, self.CSV_FILE_NAME)

        # Check if the file exists to decide whether to write headers
        file_exists = os.path.isfile(csv_file_path)

        with open(csv_file_path, mode="a", newline="") as file:
            writer = csv.writer(file)

            # Write headers if the file is new
            if not file_exists:
                writer.writerow(["License Key", "Expiration Date"])  # Write the header

            # Write the license key and expiration date
            writer.writerow([license_key, expiration_date])

    def git_commit_and_push(self):
        """Add, commit, and push the License_keys.csv file to the GitHub repository."""
        try:
            os.chdir(self.GITHUB_REPO_PATH)

            subprocess.run(["git", "add", self.CSV_FILE_NAME], check=True)
            subprocess.run(["git", "commit", "-m", "Add new license key"], check=True)
            subprocess.run(["git", "push", "origin", "master"], check=True)

        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Error", f"An error occurred while pushing to GitHub:\n{e}"
            )

    def generate_key(self):
        """Generate a key and perform all operations."""
        self.output_label.config(text="Generating key... Please wait.")
        self.generate_button.config(
            state="disabled"
        )  # Disable the button during processing

        try:
            # Get the number of months from the entry field and validate input
            months = self.validate_input(self.expiration_entry.get())

            # Generate the license key
            license_key = self.generate_license_key()
            self.save_key_to_csv(license_key, months)
            self.git_commit_and_push()  # Uncomment if you want to push to GitHub

            # Show generated key message box
            messagebox.showinfo(
                "Generated Key",
                f"License Key: {license_key}\nExpiration: {months} month{'s' if months > 1 else ''}",
            )

            self.root.quit()  # Use destroy to close the window safely

        except ValueError:
            messagebox.showerror("Input Error", self.INPUT_ERROR)
            self.output_label.config(text="")
            self.generate_button.config(
                state="normal"
            )  # Clear the output label on error
        except Exception as e:
            messagebox.showerror("Error", self.UNEXPECTED_ERROR.format(str(e)))
            self.output_label.config(text="")
            self.generate_button.config(
                state="normal"
            )  # Clear the output label on error

    def validate_input(self, input_value):
        """Validate the input and return the number of months."""
        if not input_value.strip().isdigit():
            raise ValueError(self.INPUT_ERROR)

        months = int(input_value)
        if months <= 0:
            raise ValueError(self.INPUT_ERROR)
        return months


if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseKeyGenerator(root)
    root.mainloop()
