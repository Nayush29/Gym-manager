import csv
import random
import string
import subprocess
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
from playwright.sync_api import sync_playwright

class LicenseKeyGenerator:
    CSV_FILE_NAME = "License_keys.csv"
    REPO_PATH = r"C:\Users\mayan\OneDrive\Documents\VS\Python Scripts\Gym Manager"
    output_folder = os.path.join(REPO_PATH, "Invoice's")
    os.makedirs(output_folder, exist_ok=True)
    EXPIRATION_OPTIONS = {"1 Month": 1, "3 Month's": 3, "6 Month's": 6, "12 Month's": 12}
    SUBSCRIPTION_FEES = { 1: 449, 3: 1199,  6: 1599, 12: 1999 }

    def __init__(self, root):
        self.root = root
        self.root.title("License Key Generator")
        self.root.geometry("+500+100")
        self.root.resizable(False, False)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface components."""
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=20, pady=20)

        self.name_entry = self._create_input_field("Enter Customer Name", "letters")
        self.phone_entry = self._create_input_field("Enter Customer Number", "numeric")

        self.expiration_var = tk.StringVar(value="Select duration")
        tk.Label(self.frame, text="Select expiration duration", font=("Poppins", 16, "bold")).pack(pady=5)
        tk.OptionMenu(self.frame, self.expiration_var, *self.EXPIRATION_OPTIONS.keys()).pack(pady=5)

        self.generate_button = tk.Button(
            self.frame, text="Generate Key", command=self.generate_key,
            bg="green", font=("Poppins", 14, "bold"), fg="white")
        self.generate_button.pack(pady=5, ipadx=10)

    def _create_input_field(self, label_text, input_type):
        """Create and return an input field with label and validation."""
        vcmd = (self.frame.register(self.validate_input), "%P", input_type)
        tk.Label(self.frame, text=label_text, font=("Poppins", 16, "bold")).pack(pady=5)
        entry = tk.Entry(self.frame, font=("Poppins", 14), validate="key", validatecommand=vcmd)
        entry.pack(pady=5)
        return entry

    def validate_input(self, input_str, mode):
        """Validates input based on the specified mode (numeric or letters)."""
        if mode == "numeric":
            return (input_str.isdigit() and len(input_str) <= 10) or input_str == ""
        elif mode == "letters":
            return all(char.isalpha() or char.isspace() for char in input_str)
        return False

    def generate_license_key(self):
        """Generate a random license key in the format AAAA-1234-BBBB-1234."""
        return "-".join([
            "".join(random.choices(string.ascii_uppercase, k=4)),
            "".join(random.choices(string.digits, k=4)),
            "".join(random.choices(string.ascii_uppercase, k=4)),
            "".join(random.choices(string.digits, k=4)) ])

    def save_key_to_csv(self, license_key, expiration_date):
        """Save the license key and expiration date to a CSV file."""
        csv_file_path = os.path.join(self.REPO_PATH, self.CSV_FILE_NAME)
        file_exists = os.path.isfile(csv_file_path)

        try:
            with open(csv_file_path, mode="a", newline="") as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["License Key", "Expiration Date"])
                writer.writerow([license_key, expiration_date])
            return True  # Return True if successful
        except IOError as e:
            messagebox.showerror("File Error", f"Failed to save license key: {str(e)}")
            return False  # Return False if failed

    def git_commit_and_push(self):
        """Commit and push CSV to GitHub."""
        try:
            os.chdir(self.REPO_PATH)
            subprocess.run(["git", "add", self.CSV_FILE_NAME], check=True)
            subprocess.run(["git", "commit", "-m", "Add new license key"], check=True)
            subprocess.run(["git", "push", "origin", "master"], check=True)
            return True  # Return True if successful
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Git Error", f"Git command failed: {str(e)}")
            return False  # Return False if failed
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"Error during Git push: {str(e)}")
            return False  # Return False if failed

    def generate_pdf_invoice(self, license_key, expiration_date, months, name, Number):
        """Generate a PDF invoice for the license key."""
        subscription_fee = self.SUBSCRIPTION_FEES[months]
        months_str = f"{months} month" if months == 1 else f"{months} month's"
        Number = f"(+91){Number}"
        Name = name.capitalize()

        html_content = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>License Key Invoice</title>
        <style>
        body {{font-family:  Verdana;margin: 40px}}
        h1 {{color: blueviolet; text-align: center;}}
        hr {{border: 0;border-top: 1px solid #e0e0e0;}}
        .info-title {{font-size: 1.23rem;font-weight: bold;}}
        .section-title {{text-align: center;font-weight: bold;font-size: 1.23rem;}}
        .info {{display: flex;justify-content: space-between;margin: 20px;}}
        .invoice-details{{margin: 20px;}}
        .invoice {{display: flex;justify-content: space-between;margin: 20px;}}
        .subscription-fees {{ display: flex;justify-content: space-between;margin: 20px;}}
        .total {{font-weight: bold;color: blue;}}
        .subscription-fees .fee {{font-size: 1.23rem;font-weight: bold;}}
        .terms {{margin: 20px;}}
        .terms ul {{list-style: none;padding: 0;}}
        .terms ul li {{margin-bottom: 10px;position: relative;padding-left: 20px;line-height: 1.6;}}
        .terms ul li:before {{content: "•";position: absolute;left: 0;color: blue;}}
        .support-info {{text-align: center;margin-top: 20px;}}
        .footer {{text-align: center;font-weight: bold;margin-top: 40px;}}
        .footer p {{font-size: large;}}
        </style>
        </head>
        <body>
        <div class="container">
        <h1>License Key Invoice</h1>
        <hr>
        <div class="info">
        <div>
        <p class="info-title">Provided By</p>
        <p>Company: Tillow</p><p>API Provider: Ayush Negi</p>
        </div>
        <div>
        <p class="info-title">Bill To</p>
        <p>Customer Name: {Name}</p>
        <p>Phone Number: {Number}</p>
        </div>
        </div>
        <div class="invoice-details">
        <p class="section-title">License Details</p>
        <p>License Key: {license_key}</p>
        <p>Duration: {months_str}</p>
        <p>Expiration Date: {expiration_date}</p>
        </div>
        <hr>
        <div class="subscription-fees">
        <span class="fee">Subscription Fee</span>
        <span>₹ {subscription_fee}</span>
        </div>
        <div class="invoice">
        <span>INVOICE - PAID</span>
        <span>Date: {datetime.now().strftime("%d-%m-%Y")}</span>
        <span class="total">Total Amount Paid: ₹ {subscription_fee}</span>
        </div>
        <div class="terms">
        <h3>Terms and Conditions</h3>
        <ul>
        <li>Message Delivery: Message delivery times and success are not guaranteed, as they depend on network conditions and recipient availability.</li>
        <li>Usage Limitations: The API is for compliant business and informational purposes only. Unsolicited or spam messages are prohibited and may result in suspension.</li>
        <li>Data Privacy: Customer and recipient data is handled per our privacy policy and not shared with unauthorized third parties.</li>
        <li>Compliance with WhatsApp Policies: Users must adhere to all WhatsApp policies. Violations may result in API access suspension.</li>
        <li>Refund Policy: Refunds are unavailable once an API call is processed. For technical issues or delivery failures due to system errors, please contact support.</li>
        </ul>
        </div>
        <div class="support-info">
        <p class="section-title">Support Contact</p>
        <p>For questions or support, contact the Developer at nayush517@gmail.com.</p>
        </div>
        <div class="footer">
        <p>Thank You for Your Business!</p>
        <p>We appreciate your choice of Tillow for your messaging needs.</p>
        </div>
        </div>
        </body>
        </html>
        """

        with sync_playwright() as p:
            edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            try:
                browser = p.chromium.launch(executable_path=edge_path, headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.set_content(html_content)
                pdf_path = os.path.join(self.output_folder, f'Invoice_{datetime.now().strftime("%d-%m-%Y")}.pdf')
                page.pdf(path=pdf_path, format='A4')
                messagebox.showinfo("Success", "Invoice PDF generated successfully.")
                return True  # Return True if successful
            except Exception as e:
                messagebox.showerror("PDF Error", f"Failed to generate PDF: {str(e)}")
                return False  # Return False if failed
            finally:
                context.close()
                browser.close()

    def generate_key(self):
        """Generate a license key, handle CSV save, Git push, and PDF generation."""
        self.generate_button.config(state="disabled")
        
        try:
            # Step 1: Input validation
            name = self.name_entry.get().strip()
            phone = self.phone_entry.get().strip()
            duration = self.expiration_var.get()

            if not name or len(name) < 3 or not phone or duration == "Select duration":
                messagebox.showerror("Input Error", "Please complete all fields.")
                self.generate_button.config(state="normal")
                return

            months = self.EXPIRATION_OPTIONS[duration]
            license_key = self.generate_license_key()
            expiration_date = (datetime.now() + timedelta(days=30 * months)).strftime("%d-%m-%Y")

            # Step 2: Save to CSV
            if not self.save_key_to_csv(license_key, expiration_date):
                messagebox.showerror("CSV Error", "Failed to save license key to CSV.")
                self.generate_button.config(state="normal")
                return

            # Step 3: Git commit and push
            if not self.git_commit_and_push():
                messagebox.showerror("Git Error", "Failed to commit and push changes.")
                self.generate_button.config(state="normal")
                return

            # Step 4: Generate PDF invoice
            if not self.generate_pdf_invoice(license_key, expiration_date, months, name, phone):
                messagebox.showerror("PDF Error", "Failed to generate PDF.")
                self.generate_button.config(state="normal")
                return

            # If all steps succeed, close the app
            self.root.destroy()
            
        except Exception as e:
            self.generate_button.config(state="normal")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseKeyGenerator(root)
    root.mainloop()