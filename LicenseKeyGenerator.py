import csv
import random
import string
from datetime import datetime, timedelta
import subprocess
import os
import tkinter as tk
from tkinter import messagebox


class LicenseKeyGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("License Key Generator")
        self.root.geometry("300x150")
        self.root.resizable(False, False)  # Prevent resizing the window

        # Input for the expiration type (months)
        self.expiration_label = tk.Label(root, text="Expiration type (in months):")
        self.expiration_label.pack(pady=10)

        self.expiration_entry = tk.Entry(root)
        self.expiration_entry.pack(pady=5)

        # Button to generate key
        self.generate_button = tk.Button(
            root, text="Generate Key", command=self.generate_key
        )
        self.generate_button.pack(pady=20)

        self.output_label = tk.Label(root, text="", wraplength=300)
        self.output_label.pack(pady=10)

    def generate_license_key(self):
        """Generate a random license key in the format AAAA-1234-BBBB-1234."""
        letters = "".join(random.choices(string.ascii_uppercase, k=4))
        numbers1 = "".join(random.choices(string.digits, k=4))
        letters2 = "".join(random.choices(string.ascii_uppercase, k=4))
        numbers2 = "".join(random.choices(string.digits, k=4))
        return f"{letters}-{numbers1}-{letters2}-{numbers2}"

    def save_key_to_csv(self, license_key, months, file_path):
        """Save the license key and its expiration type to a CSV file."""
        expiration_date = (
            datetime.now() + timedelta(days=30 * months)
        ).date()  # Expiration based on months
        expiration_type = (
            f"{months} month{'s' if months > 1 else ''}"  # Handle singular/plural
        )

        # Write the license key and expiration type to the CSV file
        with open(file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([license_key, expiration_type])  # Write the new entry

    def git_commit_and_push(self, file_path):
        """Add, commit, and push the file to the GitHub repository."""
        try:
            # Change directory to your GitHub repository
            os.chdir(
                r"C:\Users\mayan\OneDrive\Documents\VS\Python Scripts\Gym Manager"
            )  # Use your specified path

            # Check the git status
            subprocess.run(["git", "status"], check=True)

            # Add the License_keys.csv file
            subprocess.run(["git", "add", file_path], check=True)

            # Commit the changes
            subprocess.run(
                ["git", "commit", "-m", f"Add new license key {file_path}"], check=True
            )

            # Push to the repository (assuming 'main' branch)
            subprocess.run(["git", "push", "origin", "main"], check=True)

            # Show success message
            messagebox.showinfo(
                "Success", "New license key added and pushed to GitHub successfully."
            )
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Error", f"An error occurred while pushing to GitHub:\n{e}"
            )

    def generate_key(self):
        """Generate a key and perform all operations."""
        try:
            months = int(self.expiration_entry.get())
            if months <= 0:
                raise ValueError("Months must be positive.")

            # Generate a single license key
            license_key = self.generate_license_key()
            csv_file_name = "License_keys.csv"
            csv_file_path = os.path.join(
                r"C:\Users\mayan\OneDrive\Documents\VS\Python Scripts\Gym Manager",
                csv_file_name,
            )

            # Save the key to CSV
            self.save_key_to_csv(license_key, months, csv_file_path)

            # Commit and push the CSV file to GitHub
            self.git_commit_and_push(csv_file_path)

            self.output_label.config(
                text=f"Generated Key: {license_key}\nExpiration: {months} month{'s' if months > 1 else ''}"
            )

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseKeyGenerator(root)
    root.mainloop()
