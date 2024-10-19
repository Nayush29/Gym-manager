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
        # Expiration label
        tk.Label(
            self.root,
            text="Enter expiration duration in months.",
            font=("Arial", 12, "bold"),
        ).pack(pady=10)

        # Expiration entry
        self.expiration_entry = tk.Entry(self.root, font=("Arial", 14))
        self.expiration_entry.pack(pady=5)

        # Output label
        self.output_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.output_label.pack(pady=10)

        # Generate button
        self.generate_button = tk.Button(
            self.root,
            text="Generate Key",
            command=self.generate_key,
            bg="green",
            font=("Arial", 12, "bold"),
            fg="white",
        )
        self.generate_button.pack(pady=20)

    def generate_license_key(self):
        """Generate a random license key in the format AAAA-1234-BBBB-1234."""
        return "-".join(
            [
                "".join(random.choices(string.ascii_uppercase, k=4)),
                "".join(random.choices(string.digits, k=4)),
                "".join(random.choices(string.ascii_uppercase, k=4)),
                "".join(random.choices(string.digits, k=4)),
            ]
        )

    def save_key_to_csv(self, license_key, months):
        """Save the license key and expiration type to a CSV file."""
        expiration_date = (datetime.now() + timedelta(days=30 * months)).date()
        csv_file_path = os.path.join(self.GITHUB_REPO_PATH, self.CSV_FILE_NAME)

        try:
            # Check if the file exists to decide whether to write headers
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
        self.generate_button.config(
            state="disabled"
        )  # Disable the button during processing

        try:
            # Validate input
            months = self.validate_input(self.expiration_entry.get())

            # Generate the license key
            license_key = self.generate_license_key()

            # Save the license key to CSV
            self.save_key_to_csv(license_key, months)
            self.output_label.config(text="Key generated and saved successfully.")

            # Commit and push to GitHub
            self.git_commit_and_push()

            # Show the generated key in a messagebox
            messagebox.showinfo(
                "Generated Key",
                f"License Key: {license_key}\nExpiration: {months} month{'s' if months > 1 else ''}",
            )

            # Close the window after successful generation and saving
            self.root.quit()

        except ValueError:
            messagebox.showerror("Input Error", self.INPUT_ERROR)
            self.output_label.config(text="")
            self.generate_button.config(
                state="normal"
            )  # Re-enable the button if there's an error

        except Exception as e:
            messagebox.showerror("Error", self.UNEXPECTED_ERROR.format(str(e)))
            self.output_label.config(text="")
            self.generate_button.config(state="normal")  # Re-enable the button if error

    def validate_input(self, input_value):
        """Validate the input and return the number of months."""
        if not input_value.strip().isdigit() or int(input_value) <= 0:
            raise ValueError(self.INPUT_ERROR)
        return int(input_value)


if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseKeyGenerator(root)
    root.mainloop()
