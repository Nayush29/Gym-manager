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

    def generate_pdf_invoice(self, license_key, expiration_date, months, name, number):
        """Generate a PDF invoice for the license key."""
        # Subscription fee based on months selected
        subscription_fee = self.SUBSCRIPTION_FEES.get(months, 0)
        subscription_type = f"{months} month{'s' if months != 1 else ''}"

        # Format the phone number
        number = f"(+91){number}"

        # Capitalize customer name
        name = name.capitalize()

        # Calculate GST (assuming 18%)
        gst = round(subscription_fee * 0.18, 2)
        total_amount = round(subscription_fee + gst, 2)

        # Invoice details
        invoice_number = f"INV{datetime.now().strftime('%Y%m%d')}"
        date = datetime.now().strftime('%d-%m-%Y')

        # Prepare the HTML content for the invoice
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>License Key Invoice</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Poppins', sans-serif;
            margin: 30px;
        }}

        .container {{
            margin: 10px;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #e6e6e6;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        .logo svg {{
            height: 50px;
        }}

        .invoice-title {{
            font-size: 1.8em;
            font-weight: 600;
        }}

        .invoice-info {{
            font-size: 1em;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }}

        .info {{
            display: flex;
            justify-content: space-between;
            padding-top: 20px;
            border-top: 1px solid #e6e6e6;
        }}

        .info h3 {{
            margin: 0;
            font-weight: 600;
        }}

        .invoice-details,
        .total {{
            padding-top: 20px;
            border-top: 1px solid #e6e6e6;
        }}

        .invoice-details p,
        .total p {{
            font-size: 0.95em;
            line-height: 1.6;
        }}

        h3 {{
            margin: 0;
        }}

        .terms {{
            padding-top: 20px;
        }}

        .terms ul {{
            list-style: none;
            padding: 10px;
            margin: 0;
            font-size: 0.9em;
        }}

        .terms ul li {{
            position: relative;
            padding-left: 20px;
            line-height: 1.8;
        }}

        .terms ul li:before {{
            content: "•";
            position: absolute;
            left: 0;
            color: #5068d4;
            font-size: 1.2em;
        }}

        .total {{
            border-bottom: 1px solid #e6e6e6;
        }}

        .total p {{
            display: flex;
            justify-content: space-between;
        }}

        .total p strong {{
            text-align: right;
            color: #5068d4;
            font-weight: bold;
            flex-grow: 1;
        }}

        .support-info {{
            margin-bottom: 20px;
            font-size: 0.95em;
        }}

        .support-info p {{
            margin: 10px;
        }}

        .footer {{
            text-align: center;
            font-size: 1em;
            font-weight: 600;
            border-top: 1px solid #e6e6e6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <svg xmlns="http://www.w3.org/2000/svg">
                    <path
                        d="M15 32.8462C17.1242 32.8462 18.8461 31.1242 18.8461 29C18.8461 26.8758 17.1242 25.1539 15 25.1539C12.8758 25.1539 11.1538 26.8758 11.1538 29C11.1538 31.1242 12.8758 32.8462 15 32.8462ZM15 22.8462C17.1242 22.8462 18.8461 21.1242 18.8461 19C18.8461 16.8758 17.1242 15.1538 15 15.1538C12.8758 15.1538 11.1538 16.8758 11.1538 19C11.1538 21.1242 12.8758 22.8462 15 22.8462ZM25 32.8462C27.1242 32.8462 28.8462 31.1242 28.8462 29C28.8462 26.8758 27.1242 25.1539 25 25.1539C22.8758 25.1539 21.1538 26.8758 21.1538 29C21.1538 31.1242 22.8758 32.8462 25 32.8462ZM25 22.8462C27.1242 22.8462 28.8462 21.1242 28.8462 19C28.8462 16.8758 27.1242 15.1538 25 15.1538C22.8758 15.1538 21.1538 16.8758 21.1538 19C21.1538 21.1242 22.8758 22.8462 25 22.8462ZM20 4C30.8333 4 40 13.1667 40 24C40 34.8333 30.8333 44 20 44C9.16668 44 0 34.8333 0 24C0 13.1668 9.16673 4 20 4ZM20 9.38461C11.9512 9.38461 5.38462 15.7238 5.38462 23.7315C5.38462 31.7392 11.9512 38.6154 20 38.6154C28.0488 38.6154 34.6154 31.7392 34.6154 23.7315C34.6154 15.7238 28.0488 9.38461 20 9.38461ZM62.6848 35.9231H68.9693C69.1955 35.9231 69.2924 35.8262 69.357 35.6L71.4382 27.9166L73.4572 35.6C73.5218 35.8262 73.6187 35.9231 73.8449 35.9231H80.1268C80.3852 35.9231 80.5468 35.8262 80.6114 35.6L85.0011 19.3077V35.5354C85.0011 35.7615 85.1626 35.9231 85.3888 35.9231H92.3026C92.5287 35.9231 92.6903 35.7615 92.6903 35.5354V18.6185C92.6903 18.3923 92.5287 18.2308 92.3026 18.2308L78.8307 18.2321C78.6046 18.2321 78.4753 18.3291 78.4107 18.5875L76.8848 26.4076L75.3482 18.5875C75.3159 18.3614 75.1544 18.2321 74.9282 18.2321H68.0901C67.8639 18.2321 67.7024 18.3614 67.6701 18.5875L66.1738 26.4076L64.6823 18.5875C64.6177 18.3291 64.4885 18.2321 64.2623 18.2321L54.0538 18.2308V12.4678C54.0538 12.177 53.8536 12.0478 53.5306 12.1447L47.1123 14.215C46.8861 14.2796 46.7569 14.4735 46.7569 14.6996L46.7494 17.4155C46.7494 18.094 46.394 18.3847 45.7155 18.3847H44.0563C43.8301 18.3847 43.6685 18.5462 43.6685 18.7724V23.6139C43.6685 23.8401 43.8301 24.0016 44.0563 24.0016H46.5385V29.8815C46.5385 34.0492 48.1785 36.4046 53.1861 36.4046C55.1246 36.4046 56.7092 36.1555 57.5493 35.7678C57.8077 35.6386 57.9 35.477 57.9 35.2186V30.6413C57.9 30.3828 57.6462 30.2536 57.3231 30.4151C56.9031 30.609 56.4169 30.6413 55.9323 30.6413C54.64 30.6413 54.2276 30.1567 54.2276 28.5413V24.0016H57.238C57.4642 24.0016 57.6149 23.8518 57.6149 23.6257V19.3077L62.2002 35.6C62.2648 35.8262 62.4263 35.9231 62.6848 35.9231ZM85.0011 16.3053C85.0011 16.5315 85.1626 16.6931 85.3888 16.6931H92.3026C92.5287 16.6931 92.6903 16.5315 92.6903 16.3053V12.4678C92.6903 12.2416 92.5287 12.0801 92.3026 12.0801H85.3888C85.1626 12.0801 85.0011 12.2416 85.0011 12.4678V16.3053ZM94.2299 35.5354C94.2299 35.7615 94.3914 35.9231 94.6176 35.9231H101.539C101.765 35.9231 101.926 35.7615 101.926 35.5354V12.4678C101.926 12.2416 101.765 12.0801 101.539 12.0801H94.6176C94.3914 12.0801 94.2299 12.2416 94.2299 12.4678V35.5354ZM103.465 35.5354C103.465 35.7615 103.627 35.9231 103.853 35.9231H110.755C110.982 35.9231 111.143 35.7615 111.143 35.5354L111.139 18.6185C111.139 18.3923 110.978 18.2308 110.752 18.2308H103.849C103.623 18.2308 103.462 18.3923 103.462 18.6185L103.465 35.5354ZM103.462 16.3053C103.462 16.5315 103.623 16.6931 103.849 16.6931H110.755C110.982 16.6931 111.143 16.5315 111.143 16.3053L111.139 12.4678C111.139 12.2416 110.978 12.0801 110.752 12.0801H103.849C103.623 12.0801 103.462 12.2416 103.462 12.4678V16.3053ZM112.352 27.2323C112.352 32.4985 116.395 36.4615 122.308 36.4615C128.22 36.4615 132.228 32.4985 132.228 27.2323V26.8123C132.228 21.5462 128.22 17.6923 122.308 17.6923C116.395 17.6923 112.352 21.5462 112.352 26.8123V27.2323ZM119.769 27.2462V26.9307C119.769 24.5077 120.886 23.56 122.308 23.56C123.729 23.56 124.852 24.5077 124.852 26.9307V27.2462C124.852 29.637 123.729 30.6369 122.308 30.6369C120.886 30.6369 119.769 29.637 119.769 27.2462Z"
                        fill="#F22F46"></path>
                </svg>
            </div>
            <div class="invoice-title">Invoice - PAID</div>
        </div>

        <div class="invoice-info">
            <div>Invoice Number: {invoice_number}</div>
            <div>Date: {date}</div>
        </div>

        <div class="info">
            <div>
                <h3>Provided By</h3>
                <p>Company: Twillo</p>
                <p>API Provider: Ayush Negi</p>
            </div>
            <div>
                <h3>Bill To</h3>
                <p>Customer Name: {name}</p>
                <p>Phone Number: {number}</p>
            </div>
        </div>

        <div class="invoice-details">
            <h3>License Details</h3>
            <p>License Key: {license_key}</p>
            <p>Expiration Date: {expiration_date}</p>
            <p>Subscription Duration: {subscription_type}</p>
            <p>Subscription Fee: ₹{subscription_fee}</p>
        </div>

        <div class="total">
            <h3>Invoice Summary</h3>
            <p>Subscription Fee: ₹{subscription_fee}</p>
            <p>GST (18%): ₹{gst}</p>
            <p><strong>Total Amount Paid: ₹{total_amount}</strong></p>
        </div>

        <div class="terms">
            <h3>Terms and Conditions</h3>
            <ul>
                <li>Message delivery times and success are subject to network conditions and recipient availability.
                </li>
                <li>API use is restricted to compliant business and informational purposes. Spam messages are prohibited
                    and may result in suspension.</li>
                <li>Data privacy is strictly maintained and not shared with unauthorized parties.</li>
                <li>Users must adhere to WhatsApp policies. Violations may result in API suspension.</li>
                <li>No refunds are available once an API call is processed. Contact support for technical issues.</li>
            </ul>
        </div>

        <div class="support-info">
            <h3>Support Contact</h3>
            <p>For questions or support, contact the Developer at <a
                    href="mailto:nayush517@gmail.com">nayush517@gmail.com</a></p>
        </div>

        <div class="footer">
            <p>Thank You for Choosing Tillow for Your Messaging Needs!</p>
        </div>
    </div>
</body>
</html>
        """

        # Use Playwright to generate the PDF
        with sync_playwright() as p:
            edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            try:
                browser = p.chromium.launch(executable_path=edge_path, headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.set_content(html_content)

                # Define PDF path
                pdf_path = os.path.join(self.output_folder, f'Invoice_{invoice_number}_{datetime.now().strftime("%d-%m-%Y")}.pdf')
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