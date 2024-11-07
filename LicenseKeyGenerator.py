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
    GITHUB_REPO_PATH = (r"C:\Users\mayan\OneDrive\Documents\VS\Python Scripts\Gym Manager")
    INPUT_ERROR = ("Please enter a valid positive number for the expiration duration in months.")

    def __init__(self, root):
        self.root = root
        self.root.title("License Key Generator")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface components."""
        tk.Label(self.root, text="Enter expiration duration in months.", font=("Arial", 12, "bold")).pack(pady=10)

        self.expiration_entry = tk.Entry(self.root, font=("Arial", 14))
        self.expiration_entry.pack(pady=5)
        self.expiration_entry.focus()

        self.output_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.output_label.pack(pady=10)

        self.generate_button = tk.Button(
            self.root,
            text="Generate Key",
            command=self.generate_key,
            bg="green",
            font=("Arial", 12, "bold"),
            fg="white")
        self.generate_button.pack(pady=20)

    def generate_license_key(self):
        """Generate a random license key in the format AAAA-1234-BBBB-1234."""
        return "-".join([
                "".join(random.choices(string.ascii_uppercase, k=4)),
                "".join(random.choices(string.digits, k=4)),
                "".join(random.choices(string.ascii_uppercase, k=4)),
                "".join(random.choices(string.digits, k=4))])

    def save_key_to_csv(self, license_key, months):
        """Save the license key and expiration type to a CSV file."""
        expiration_date = (datetime.now() + timedelta(days=30 * months)).strftime("%d-%m-%Y")
        csv_file_path = os.path.join(self.GITHUB_REPO_PATH, self.CSV_FILE_NAME)

        try:
            file_exists = os.path.isfile(csv_file_path)

            with open(csv_file_path, mode="a", newline="") as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["License Key", "Expiration Date"])
                writer.writerow([license_key, expiration_date])
        except IOError as e:
            raise Exception(f"Failed to write to CSV file: {e}")

    def git_commit_and_push(self):
        """Add, commit, and push the License_keys.csv file to the GitHub repository."""
        try:
            os.chdir(self.GITHUB_REPO_PATH)
            subprocess.run(["git", "add", self.CSV_FILE_NAME], check=True)
            subprocess.run(["git", "commit", "-m", "Add new license key"], check=True)
            subprocess.run(["git", "push", "origin", "master"], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git command failed: {e}")
        except Exception as e:
            raise Exception(f"Failed to push to GitHub: {e}")

    def generate_key(self):
        """Generate a key and perform all operations."""
        self.output_label.config(text="Generating key... Please wait.")
        self.generate_button.config(state="disabled")

        try:
            months = self.validate_input(self.expiration_entry.get())

            license_key = self.generate_license_key()

            self.save_key_to_csv(license_key, months)
            self.output_label.config(text="Key generated and saved successfully.")

            self.git_commit_and_push()

            messagebox.showinfo("Generated Key",
            f"License Key: {license_key}\nExpiration: {months} month{'s' if months > 1 else ''}")

            self.root.quit()

        except ValueError:
            messagebox.showerror("Input Error", self.INPUT_ERROR)
            self.output_label.config(text="")
            self.generate_button.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            self.output_label.config(text="")
            self.generate_button.config(state="normal")

    def validate_input(self, input_value):
        """Validate the input and return the number of months."""
        if not input_value.strip().isdigit() or int(input_value) <= 0:
            raise ValueError(self.INPUT_ERROR)
        return int(input_value)


if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseKeyGenerator(root)
    root.mainloop()