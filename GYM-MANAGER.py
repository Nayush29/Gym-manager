import base64
import os
import socket
import sqlite3
import sys
import time
import requests
import webbrowser
import babel.numbers
import tkinter as tk
import pandas as pd
from io import BytesIO, StringIO
from tkcalendar import DateEntry
from tkinter import ttk,messagebox
from PIL import Image, ImageTk
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class GymManagerApp:
    def __init__(self, root):
        """Initializes the Gym Manager application."""
        import pywhatkit as kit
        self.kit = kit

        self.root = root
        self.root.state("zoomed")
        self.root.title("Gym Manager")

        self.BG_COLOR = "#0071C5"
        self.FG_COLOR = "#FFFFFF"
        self.GREEN_BG_COLOR = "#059212"
        self.RED_BG_COLOR = "#C40C0C"
        self.BLUE_BG_COLOR = "#000080"
        self.button_padding = 10
        self.FONT_LARGE = ("Times New Roman", 20, "bold")
        self.FONT_MEDIUM = ("Poppins", 16, "bold")
        self.FONT_SMALL_INPUT = ("Poppins", 16)
        self.FONT_SMALL = ("Poppins", 13, "bold")
        self.FONT_MEDIUM_TABLE = ("Poppins", 14, "bold")
        self.FONT_SMALL_TABLE = ("Poppins", 13)

        self.db_path = os.path.join(os.path.dirname(sys.executable), "gym.db")

        self.init_database()

        if not self.update_expired_members():
            self.root.destroy()
        else:
            self.setup_ui()

    def init_database(self):
        """Creates tables in the database if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """ CREATE TABLE IF NOT EXISTS members (
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
                    notified TEXT NOT NULL DEFAULT 'True' CHECK (notified IN ('True', 'False')))
                """ )
            
            cursor.execute(
                """ CREATE TABLE IF NOT EXISTS app_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_count INTEGER DEFAULT 0,
                    license_key_expiration TEXT DEFAULT NULL)
                """ )
            
            conn.commit()

    def update_expired_members(self):
        """Checks and updates the status of members based on their expiration date."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                current_date = datetime.now().date()

                cursor.execute(" SELECT license_key_expiration, message_count FROM app_data ")
                app_data = cursor.fetchone()

                if app_data:
                    license_key_expiration_str, message_count = app_data
                    if license_key_expiration_str and message_count > 20:
                        license_key_expiration = datetime.strptime(license_key_expiration_str,
                        "%d-%m-%Y").date()
                        if current_date > license_key_expiration:
                            cursor.execute(" UPDATE app_data SET message_count = 0 ")

                cursor.execute(" SELECT id, duration, date_of_activation FROM members WHERE status = 'Active' ")
                rows = cursor.fetchall()
                updates_inactive = []
                updates_active = []

                for member_id, duration_str, date_of_activation in rows:
                    duration_months = int(duration_str.split()[0])
                    activation_date = datetime.strptime(date_of_activation, "%d-%m-%Y").date()
                    expiration_date = activation_date + relativedelta(months=duration_months)
                    expiration_date_str = expiration_date.strftime("%d-%m-%Y")

                    if current_date > expiration_date:
                        updates_inactive.append((expiration_date_str, "Inactive", "False", member_id))
                    else:
                        updates_active.append((expiration_date_str, member_id))

                if updates_inactive:
                    cursor.executemany(" UPDATE members SET expiration_date = ?, status = ?, notified = ? WHERE id = ? ", updates_inactive)

                if updates_active:
                    cursor.executemany(" UPDATE members SET expiration_date = ? WHERE id = ? ", updates_active)

                conn.commit()
                return True

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            return False

    def setup_ui(self):
        """Sets up the user interface for the Gym Manager application."""
        self.background_image = tk.Label(self.root)
        self.background_image.pack(fill=tk.BOTH, expand=True)
        self.image_data = """/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsK
                            CwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQU
                            FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAQkB4ADASIA
                            AhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQA
                            AAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3
                            ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm
                            p6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEA
                            AwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSEx
                            BhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElK
                            U1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3
                            uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD8qqKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKAF3UlO8unrCzt8vz/7tADaMV2Gg/DvV9eZfKtmRPu72r1jwf8B7FP3moP5zL/f+4tY1MTTg
                            d9PCVJnjnhXwTfeJ7jbBEzorfM617X4N/Z1jhuEn1NpNi13ulQ2eiL5FtAqIu37i1tXOqsm+Bv41
                            3/J/F/sV4lTGyn8B7dDL4x+Iq2HhjRdKiRooI3eJvl2/3qtalqSw2dutt+5Rv4Faufk1iK2uHZmX
                            f8213/3K53UvEO+V181flrglKU/iPSjGMPhNrxD4nZ7dLFm3p/E396uHufEMVnKis3yfM+z+81Vb
                            zWN8Usu3zpd2xa5TUpm81JZ/vt/B/dWto0w5jQ1LXpbm8adZW2f3EarFtctctErM2/b83+7XOQ22
                            9drbf9/b96ta2mVInZWX5P4P71bcvKHMdVvi+wI2752+erGlX8syxQQfPLK3lKv3/mZ9lcLcarL5
                            SK37n5v7vzt/9lX2R+zr8CtP03w5aeJfEPmJqFx8kVpNFvitYvv7/wDe/vUcpEpcpseBvh7c6VZ2
                            7XltAl35S+bM7fOrf7FaSaV/Zq2jX0E81pKzJ8io6RMu9/n/AN/ZXsepWOmQyys19Gl7LtuoH+X5
                            1/z/AAV5f4z1We5aWzgvFe3ZmeWZIHRP9j/0NKiUeUIy5jzzxP4qvI7eWKz8yFJVaLyUZNjfP86M
                            i/L/ALX96vP9e0+VLe483zNm1bryUl3oq/ff/gX+xXcPZxfY7hbmL7Y7Nsa4hR4oov4HR3/h3p93
                            +83y1xXiGH+x9Qu4L5p30yVYopXRtksW7Z8jp/E2yuaMeYvmPMtbv4vsDptkmd7pn3v/ABNs+4/+
                            1/ernL+/ZLe0/wBJ87yotiTbf9U3/wBhWtulhs9V0+5naGLz/tEH2hdj7fn2P/vOtczr15/Yt5qF
                            jazrc2jS/LMi/JtZE+T/AGa76cTGUjdtr6C1s7ixng+32irLcLMn+tiVk2I/+0vybqg0nxBJqTW7
                            Ff8AVSxebs+TzYt6K+9FbarK7K2/73z1yjvPYS7VVZkZdjb/AJ0/3P8A2an6XeNDcO0E7bJV8qV2
                            /wBr/wBl/hrqicEpH2L4A+JE6XWn+IbZpL+LTZ2f7J5HmyrufY+x/wDW7d6/Mj/Kq/NX6BfArW9B
                            8SaDZanpEH2B7/8A0hof45fv/J/tfx1+PHgzxI0K2l40q2dxLO0UCW+9N0qojJE+37yu/wDF/C1f
                            aX7Mfj+8TXE0zStQZ9PvIlvdOsbh/wDSLVvNRJbX/a+d3ZX/AItj10U5HNUjzxP0FvJlubPyJ2jm
                            SWJUZ/k/4A9cf8SPE9r4MtVtrNo/7dliVIEmb/ll9ze/+z89beleMNFv/DllqqyslpLa+a0zxfdV
                            fv8A+79z/wBArxTVftmsainiiezjmluone2S4bZtiV/3UX+z8j/fraUjjpx945W2mtrZbRtQ3fKy
                            ysjL8ku7e+//AGdm96luXuftESqv2BLiWW4WF5d/+qTfWJqtxPrd/FtnjhSWKWLYn8Lea/z/APjn
                            /j9ZV/ra6rqiW143ky26yoyebvf7ifvf9350/wCB1ynpcp1ttcz63qjsrR2dpexbP9v7Rs/8d/8A
                            sHqxput3M1nb7mjd4mlt2Tb+6ZVf7/8AvbKyofEn2O/SWeD7ZaWE9ujPCv8ArW2Onyf99pWx9vW2
                            012VVe7inuHnt/7rM/yP/u1ZjIpPo8EMl7Kt4z3F1eSv+5f55bXzd+z/AMf21UuUi1vXpb5laGWW
                            L7LAn/TuqfI9S20MsLJ57LDLYT79/wDBLu+/s/z/AB1lWd+usWGj3LMs175Wz7RD9zav8GytAOa1
                            vwwv9pWV5tbfFZ3Fkzov3riXZsd/++P/ABysewv5bm1uILmzaZFlVIpv+mq/I6V6LeQ3L+H38/8A
                            fSqzXG9F+9LvfykrnLazg0ezt75fnS1n/ep9/a2z5/8A0OokbcxlPNFJcWUttL/rbzZdQuvyfLRc
                            X7aJeahuX7N9gb78y/eVv40q3c6Ot5auzS+TuVtrp99m3/I+z/gdaCaVP4g+0LqC+cjS/wCu+5u+
                            esx6nI38P2y4t9XubZvKZWeJNvz/AO+9YttbN4h0nzWZYX8/Z8/312vXewxtNv3L/o8UrW8Ssv3l
                            WornSbaHeq23kxSy7/7qVlymsZHE620U3kqy/vV+R9jbN1Yr2c81m6qqpbs2xnRfvf399dbqtnFN
                            fysqt/qvm2fPtqKw03erwKrPE3yfOv3v9usi+Y4nVbyWw1ZNKtlZ/wB1vX/e2VEuiNbfK377avmt
                            /vNXYf2Ut5eXE6wf6V/qld/uVY1TR1s2ii8pXii+87/cZv8AcoL5jkrPSldrhp1+SJfl/uKzfPvq
                            jDpMs2y1X50/9Bb+/XXXNtE7Oqq3+4v3Gaiz01LO381U2P8A733V/uUBzHM21gsKvEv8LJ8/+1XT
                            aVZrCsuz52Zfl/2adbaV5LJuX523f8B/2609Fs97TbV3otLlI5ippVg1tLu2/wCxXfeHrZZokWdW
                            /wB/+D/gdZOm2fnXD7l2ba6vRLZd39x933K2jEiUjoLZFkVFgVXT+5/drQtrNrm4/uIvyb0/ian2
                            2molgjLtd60tKRoZbf8Aut/tV08px8xbbQWht03L937r/wB6uU1VG3eUv8X8G6vS7+5VLf5fk3f+
                            O1yU2mxeU8rK2/5t1XKJjGRxl5ZtbW7srN5u77/8bV5p4msF/eytu+Zq9T1h2s9+7+7vV68/1tFu
                            d0v30/8AHKjlOmJ5lqqLZ2+7+P8A9BrzHxDctNsVlZ9n3a9O8VWzPdbVX5PuVwPiezWG32r8m3/4
                            itNRHlXiF/Jt/l+T726uCvLBdvmt86N8613viGzbzfk++zfO/wDwCuH1t2T5V/vNUcpMjkr9/vr8
                            yfN8uysr7PHN+8ZW3t/erS151h/1TViJMyNu3Vsc0uWXxE00Kwq3zb/mrPkmaZqle53xbWqCPcvz
                            ba1jE46lQ1bFFTZuTezfx/3a3ba8VIk2tsfd9+uSSZ0Z/wCCr9s/3GZvk/u1EonTTlGR2dtNvi3N
                            8iVn3N5+9/i8rbUthcq9ujVV1WHfK7ffrLU2MzW5leJFVa5+RNtbt++/fub56w3+SRa1gcdYT/cp
                            lI1JWxxjnfdSqtMp+5m+VaAGUUUUAFFFFADvMo+7Tafu/vUAO++3y1In+tqOOj7tSXH3TVs3VJfm
                            X5q09/8A39/v1iW77mVq1rZ967vufNXFUie9Ql7poW23bu/2q0rbb95l37qxU/dt8v39taFs/wC6
                            2/7Vch6UfeN3eu2npMr7P4/7v+9WekzOz7fk3LWhbfOvy1B1Fq2WLc+1tibvlq95KpEm77jfdqvC
                            iou5m+anK+/5qUvdDUvW21F/uVsWH75tyr861j20LO237/zfcrd01dm/5f4VrLU0j8R1GlIu3d/d
                            rYR12/L/ABfe/wB6sew+dfl3fdWttIVeLbt/io1NC1bJ50XzfcX56tzW3kr93733qitk2L8tWn3P
                            FSiSfAtFFFfSH54FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRT9u3+KnY/d/eoAbvp0dW7HTp9SuPIgiaaVm+4i1778NP2eHufKvNXXZ/0x3ferGpVj
                            D4jsoYaWI+E8n8JfDXV/GFwjRQNDbt/y2Zfkr3vwf8E9D8PL5tz/AKZdv91pf4a9YfwxB4Y0tPIg
                            jSLav8CJXHrMzt5rbk+bZ/u15VTEyn8J71HAxgWLmGLTVRba23p/f2/dqiiL5u1m2S7f4/4qsXVz
                            G9rttpWdIvnrkv7YbzXZmZ3V/v1w8p3+7D4TbuX3r5XmrvZt/wDcrM1XVvszRRL87qv8HyVS1XUv
                            mSWBm+Vf+Bs1Yl/eb7fz3Zd/8NVy/wAocxFqmsNNK+5V3/733a5zVb+eG62q3nbv4P4Kl1WaWFor
                            lfv/AO39xqxdSvPtN19p+ZP9irjTMZVCxM8sMTyztsf+4rVlTXjPF8yq77m/4CtVry/lmt3Vvnqv
                            I7f9dv4N1dPKY8xpw37Iu2Dbub+ChL9vLRF+7/E/8H+/WOly3935f9ivXvgV8I7r4teJkib5NKt2
                            /wBMmXcu3bt/dLt+7vq/ZlxqHoH7M/wBn8eatZeJdVs2m8PrLsiR/wDlq3yfvW/upX21r00/h7Q/
                            s1t5KWjL5UUzrveKWtW20fTPAfh/R9N+w7LRVVFe3VERdqf3G/3KzUtl8Q36eR/pmlfK/wBnmXej
                            f8A+SoI9pzS5pHCW0zXm22uZWhl/4+GTyt6Wv99N/wDEr1t6r4Vis/EcqrbT/ZG06LULXzmfZPKu
                            /em9fuy/xbNnzV6VpvhiCzt7ee+09v7PXd/o82xLhYmf5ERF/hRKq3nw3try1SDSr5f7VsFa6sZr
                            hX+Xd9+3lff/AB79y0RpkSrHj+qW1il5qvhPVb5v7MaC11Wd9P8A9HuFWV9iXEX+1v8Am2fNXzz8
                            SPt1nZ3uh6m39t/Y5fs9rfIv7qeJXR0f/a++nyb/ALrvXqfxF8Trqum6Vq9zB/Zuq6D5tlY3b3Xm
                            veRbNjxfc3bUl2Lv/wB9q4rW9Ys9e0nQtYaxWG9aKK3uoX3yxLdK+zZ82/yt6O+59zbl/wBqjlgb
                            R5jwrXtNtrnQb3UL7dNdSukUE3ms7wKqJsdF/i37dux/mX/gVctc/wDHvLuiV3ZvK3t9/cuz51RP
                            4dip/wACevVvEL6QkV2raRHsVYpbZLedHiiZn3u6Ov8Ard6b1+4u1f8AcevL9bvPJ02yZZ2d1ilt
                            ZUeL/VbZXZNjfxfI/wB//wCJqyJGPf7Zt6uzebKzfvXZN67KypJlbyntvkdtrsm3ai/fWtC/aCGW
                            VWZd77Zd/wDdVkrMuZm3JudfNVflf/ZpxOaRbsLydmZVm8lYpfNiV/4Zfl2bf+BKm6vdfh18SIE8
                            2KCdfDep395byxatDLst7CVX/wCPjf8A7iyqyJ8vz14inkJ9nZp2/erE6ui79zK/z12fw90G81jx
                            HpVtYpbald3V8kUFpcfOjtK+xF2L/D8//j9ahE/VP4b+J/EPi3wLp8FzfW01uyxXV19kX5G3ffRH
                            /iV/vVa17Sp9VtbSDTJdm2XyvtFw33v4P++d9afgzwxB4M8K6JodjAsKRWaxRP8AfRl2b0qXW7+2
                            1LWbiC2s2vLiJVilhhb5F2//ALdUY8x5r4qe58PazcSz6fAmnrKtuuxv9a0sW+J0f/f3rXA2dyyW
                            6K1sv22KL5k277hlZ/ub/wDfr0jxloNjrf2T7TBfX6W7LKtj/e+Tzdjf7nyN/u1x+q+HdaT/AEnT
                            7m00r7RKtvvmiV/N2vvTZ/d3/PQbRkVby8bTbfULG2umhlvG+2rC/wB9WV/nT/Zq2+qtqt5qcttc
                            ybbNYrL7v+tZnT5//H65zxCl5YXlxqdzFHYS2u6WV5v9bKzOiI6f7Pz1kwzXlz4ou7yzvPsFvK0U
                            svy/ulbZsdNn/jv/AI9UDO+tvE8um3iQQNHNvsYr21R9+xlb5Ef/AMcqXwrCqS+RebYXt90u+Fv9
                            bKz/AN2ufmvJb/S4rxfLhuIrXyl3rsRYl+4m/wD4AlathqVteMkU67LWw2PsRn81Zf7j1YuU7hUl
                            mZ5VXyU8/Y0Ltv8AlVPk/wDQ65+bSlsLDU5VsZPKa63zw/web/uVe0TWFfS7udpZJpZdyRTfweaz
                            /I//AABNlXdSmn1JriJYt8W7+Bd+6Vov/ZKcjL4TE/sGWwlXym860274kdvur/sVYuYWs9PslWXZ
                            LLL/AL6LW2/hWL7ZZahbMyRRWao0L/xf5eormzW5sdKn+V383fs/+wpFcxiXOiq7NAsrJcNLvb/9
                            iqWq2EqMkDeY92rbJ33fItdq9gz2sUrRLC7N8qI33qr3NgtzbvO3lzbfk2bvvU+UOY4+88PrZxSy
                            rtmdov46xEtmRfPVfsb7vl+Xejf332V2Gq20r27y2zbHX73+1RbQ/abVFb78UW/5FrHlLjI5q80e
                            CGXzbZtib/v/AP2dZmt2crxfKu/Z/H/G3/A6657ZUVIP4l/esu371YL33nXG1l2Irf8AfVHKEZHN
                            Xln5MqKq73272/g21FbW0tyqQKux1Xe3+7W7c2/nXT7tu/8Az8lPh03Y0u1ld2/g/u1HKXzGDbW3
                            +lPu+fav3PuVrWaRJLbxNtTc3zf3G/36hjtv9MRdvyffZ9v93+Cr1tbeddOyqrurf8Aq+Uku2CMl
                            /Ky7Ui/iT+81dHoNz51xK27592zf/drn9Eha23szN8259j1u2b/6VKq/7jbKoUjtdEmaa88hvnTc
                            1d9pWlLMztKv3V/gWuB8PQqjfe3vXqGlTRW1knmtsf79bxOCoc/eJ/p7qv3Fqvc2a7d3zbNrPs/v
                            NWheQ/6ZuX+J6q6qjW0Xyt93/wAdrQg4nxPpsU0b7fvKtee6lpv2ZZVRfJ/32r03UpFuok3fP8v3
                            65TVYVdXibb/ALTvQbRkeNeJLDyd/wAvz15Z4httkTsy7Pmb77V7n4nhRIpZW214/wCJ0VFuG/3t
                            iP8Aw1GpqeT+IYf9bu/hbZ/45Xm/iFPJaXbt2ffr0PW900srL9xvvf7XyfwV55r0ywxPt/ut/wAB
                            o1JkcFqT/abrc3yLt3bt1YVy/wDD/DWlfozyyszVjv8ANWtM460vdGs28/N8tH3f4qTfTa2OAl/3
                            qsWs29kVvu1V3U+Ftn3fvVMjaMuWR19hcru27v4di/NVi8mVl2tL97/vuufs5mhXzdvyr/47V1N1
                            zK+77n3/AJ65tTvKuqJ5Kr/A275fm/hrHb5t+6tjW3+ZItvzr/crF+ZW/wB6tYnNWkQ0UUVscYU+
                            Pd/DSSUfeoAf/v1FUrv9yoqACiiigAooooAerU5HqKnhaC4ktu3zVsWz/L8y/wAVYiN81a1s6q3z
                            fxfJWNSJ34aRpJ8ip93/AGq04fvbm+T5azEjbytrVoI/y/e+f/ary6h7dP3S7bfO21vn/wCA1p27
                            qny/c+X5qzEf+Jm+99560ERni+Xb96oOyJeTb5T7v79WETY33aZbQsn8X/jtW9jRqm5t9KUeY0Lt
                            tt+782yti2/ur/DWPbJvX5vkRq3dNh3s+7/ZrH4izoNKRk2Mqt/wOujtl3r81Y+mpF5X/fNdHpts
                            vlfNT1LLCIvyN/e+ShN0zJ/6BTtn3tv/AOzQibGXd8lGoHwLRRRX0Z+eBRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABTtrUfxUqL/FQA+P5my1dB4S8G6h4y1R
                            LGxiZ5X/AIv4KseBvAGq+PNWWxsYGf5v3j7fuV9xfC74J2Pw60lN8S/bdvzP/eauapU5D0MNh+eX
                            NI5HwD8DdM8DaTb3V4qzXHy7neu2e5gttmxdiL/cror+za8Xbt+78n+7WVeW1slx5S7Zplb+D/cr
                            xKkpTkfTUoxh8By+oaxPqSurf6pfk+dq5q82Waoysrszfc/urXQeJ1b/AFrRfI/3dmxNyrXI3Txv
                            bysy/I3yfeqOXlLlIittV/sq4uHuV328q/c++9c1qV4qM8ts0bxfxojfdatXVbOeaxRlaNE+b565
                            T91bRvEzb3+/8nz1cYmf2Rtzfy3nzKqwp/FWTfzK7bvuRKvzbP4qm+0tu2sux2dnZ/uf8ArP1W5V
                            3RVXZtWtznlIz9Suftiurbki/ubvnrMebzPmb59q/cqV7lYZZWb53b5diVXuY1SKVmZt7fwf3Ko5
                            9TNufnl3KzVDsVv4t/8AeqZkZ2Rf4Gb7laWlaa15eSxQQSXlwy/uki+fd8/yVt9kNS34D8Gah8Qv
                            FFloun7nllb5n/55L8m96/UD4J/CvSvhL4XtNPs4l+0Sr80yffZv468v/Zj/AGf4vhvbw6nqttFN
                            rd/Fuut3z+Uv30RV/h/2q+mPD2jxarcefbS+Tu8pG+X7m1/n+9U/EVL3I8oX+iRartlvvPdN2/cq
                            7EZq7PQfAcWmx3a3NnafaFX5X27N26i58E3k3hfU7O2Vrm42yy2syr5sS7/uP8v9yutvEWziS283
                            90u3b5TbHX7n97/0OtYx5TjlL+U5p0/s37a7TtZ3DS+VsRfut/wL+HZXlPirUp4brT57G8X+0LC8
                            e1nt7eXY+1Ynl2P/AHl3vVv4heM7PwrearfWup3d/cS3Urz2M0vm+Q2zZ8iN92L5K8M8T+J21XVI
                            rpZbuHTPs32qB0tZZbhvkT96jr/tsi/991Eqh00qcvikc78VLmx+zpqdnLIlvdXjOzpF88Vwuz5P
                            n+Xcnz7U/irxHUrmfWL9NTtfs0OoeU0Uvkt5SNLsdERN3yq2ze3+8716d4imvtB0P7Hea4t5p7f6
                            ev8AoaeUzS/6p7jc+5f3qbW2fK3yMn92vNPE95Y6xpMVzpTWN/LFE8Swp9+1uvNR3RN3yt8iPtd/
                            +A1jy8x6XNyxPP8AVbyzvtUllnWOF7hmd7f54kVmTYjon93+KuQ1ZmhsYpJCxiv4vNfd99tsrqj7
                            f4dy10WtXVtNdXq3VrJqF6qRRQXa7UeJlbc/yfdbcu9f7y7K4u8hmvGmXyJXaLbu8ncyxfJ/F/vK
                            v/Aa0hE4KlQhZdzJ8zeT8rqzrvZVb+B/9n5aZqEPnXkvlf8ALVm+43yfK23f/wACrQhh8u31BokZ
                            9N2qmx/7rP8AI6t/F/H8v+xVuHQ0uY9Qgiu1mSKBriKa3gfYy7t7u/yblVU2/wDfSV08pzcwywRb
                            m60/avyRfOqbvu/cR99fZ/7CXwfs9e8aJrn/ACy0mJopd/3JZ/nf5N38SfJXkHwj+C0/iq6uJ77w
                            1qF/EzL5rWMqRfZ4m+dLhNzoz/c3ts3fL/ErfLX6JfBzwHpHw98F2Wn6e2+K/b7QrwxeU7M38ez+
                            5UR+I2lLlidW6Twy2n2OJvtEUX2dvO/1Sq1Y+q69Lpv9qqsHk3a7XleFd6Nt/grqH8h5pXWfZ5u1
                            4oXX5Nq/wN/tVjateWNn9ra5be8UEV1L8vybq21OPmONtr9ZoredYmmuIolin+bZtXYn3/8Aa+R6
                            5LUofO0uVmn85LWBUaHb95W3vvSu18aWFs63sUErWFvdMv8AFsRomRH37/8Af/8AQ65rxDDBcrp7
                            LBdw/bIFt76FvubVR03p/v8Am0amx5zc2f8AaTXd9P8A6Zp9na2/zzNv83596fJ/sbE/77ps2led
                            a6e0HlzW95PcXsVi6/I25Pub/wDgG5q0Nbs2ufC8T6ZBJDKytFY3b79kqsmzY/8Ae+RH/wC+0rVu
                            baxmt2s2naF4rPf8i/JulTY7pWRsc09hO+mptZYYms5f+/rfPFEi/wCxWrpWlMjaVOred4g+aW8R
                            2dElZqyrywXUrfT2sZ2mSLckVv8Affc3yb3/ANyrqXLTRPc+fsuIrWK4ZH++27f9xP8AgNQPU05v
                            7QTXNQiudsKL8/kp86K3+XrotK1i8SK0ggb7Y8TN833NzVx9hrc9wt6rSql3FFvVHZH3bd//AMXW
                            npTtuSBZ1dfNi2zf7X8fyUAdhbXMupalbqn7lN3zJ/tfx1Y1Kz+zeVBu/wBIb52/2f8AYrPsJpds
                            sU+5LhWbbs/5a1p23+k2qMyxpLEuxnf+KrMh32ZryW3VZd7xQfNv+5/wCs/7TP5sSrE2xfkf/aqa
                            wuWSzT5djrLvnZP4qtWemteapKysyJ/Cj0EFXVUXc7QbvKVtmz+9VS2tvOs5ZU+SWWXY2+tu5ha2
                            t4rZYmm2tvZ0b71Y+pM1nLEy7XT7+xPv7aBxkZ9zD5MTzq373+L+PbXL3Vts1Larfe/j/u1uwzNN
                            cXTXO5ElX79VLZF8pJJ/v+b5rIn32/2KDYyrlJUunZdr/wDxNW7OzZ4nnVvu/Ouz7lMv9Qa5uHVV
                            2fN/d+6v9yrtnMtuvlM2yJV+bZUDM1JvOsHVdv2tvkrQ0q2+x29xK38Xyb/4/wDfpipvupW/jVti
                            /Ls21b0q8eaweBm/i2f7rVpEz5ijCksNxK23eirv+T+Gtixv/JVNq/vWbe9QOjIyKqs6K3zbP4ql
                            sNNV1ilaf5/v1oRzHYeGHlTytzb/AJd7LXoFhDLc26TtL8v8Nec6JNLMybf3O5V+WvQNN1KKFXi3
                            fPt+VKUTmqBczbPm/jqlfzNNEm5f4W3Vp38kE1u22X5P8/JWPDcrc7GVfkb5/wDvmtCTBv8A9zcN
                            F/wCuS1Wb966/wAbf7NdBqs2y/Zt29d+9q5rXr/y/m2r8vzqlBqeeeM49+/b8m2vIvFSN93+9u//
                            AG69d1Lc+xZdz7vk/wCBV5v4ws/l+b5H/h/2qCzxfVbZtvy/P97f8teea3td3Vl+6rbkRq9g16FU
                            s3+XYm3Z/utXj/iKH96+35Nqs++o1A8415/9KZVX7zN8lYLps+9Wxqrqku7a2+sVt1bQPNrfEMp7
                            fLTKK1OYKdHTaKANO3fftT5trVvpeQQxbtzJtrl7d/LbdVm4uvubWZErGUfeO+NT3feHX82+VG/2
                            f46zUXc2KnR9/wB77lNm27vlq4nPU94r0UUVZgFOR9tNooAevzfeplFFABRRRQAUUUUAFO8um077
                            tAEn3f8AvqrkL/xf7NZ9WYvvVlJG1KXKbqTfuk3fO/8AEtWLabY+37+6seFm27VrTR/lT5f96uKU
                            T3qUjXtpt6/3P9+t62TeqK3zpt+/XM23z/L/AAN8610GmzfuUXbXMelE27VFhVN1WEdXZKqQ/JEj
                            N/8AtVbhf7jMv3vu7Pv1JvqaFsnzVt6bHs+78j/7dc/bTfL/AMC/jroNNf5ty/cVqx1NeY6jSt33
                            V/2a6K2f90m3+Kud0pNn+/tWugtpm8pN22jUZdtvk3s332om/wB1vvbKP9X/ALH8dD/dTc1GpB8B
                            UUUV9Gfn4UUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA9K2
                            vDfhu+8T6pFp9jA01xL/AHVrNhRppEVV3uzfKtfol+xz+y2ui6XF4l1qJvtcu11R1+6v3krGpLlO
                            mhT5pHS/s/fs5f8ACvfC8VzLAv22Vd87uv8AsV6nc+G4If8Aj5+d933Er02/22sDxQLsT/erh9em
                            aHe3lM/8debVPeicleeVYW9xL5H+6leSa1NAnmrAnkyruff/AL3369W1i5/0N5flRFXZ89eM+IHu
                            U/0n5X/8c+b+DbXNI6YmFrd5vaKzbaiRK3yf7NZ9tpVncxeVcqsMX32T+9WheJFc3CNOvk3C/wAf
                            3PmqpqVzHDpvlXNt53zb96fxMv8AB/u1OpZxXjy/VIvstn8kS1xUKLbSorN/DvroNVh/0/zW+5sZ
                            2/ubm/gSsG5tt9xtZW3t8m/+6taxIqSM28m+2XTsq7HX7v8AcrPuYZUj3N8/+3W09hHCzwNP/D87
                            7qzblJUieL5pov4fm+T/AH62OaRkzQ+dsZfn/wDZqqvpu+KLd/FXQW1n+4fbu/e/e+WtXSvDEuq3
                            CxKsmzcyL/wGoD2Zy9hoLTX8UTRM6bflT7+5q+o/2bPgPBNeXfiDVY9jWqvst3X7y702P/wD5vlr
                            E+FHwinuZreW5tmm2/dh/j+X+PfX2H4P8N2NhozxNL5MXzeVs/1q0c3MbS906DRNHg1iJPIX7HKu
                            2KfyZfnba/yV6l4Vs7aGJ5VaSaL7nyN97dWF4A8MS21raKzNM+3fFs/i/wB//gFdxc6bAlrEzQLC
                            8S79kP8AF/sV2RicFSX2Sx/aUWlRO2791F87/N8+3+//ALteaeM/Hmn23mrY3y/a5VV4rd/neWJv
                            4P8AvupvHPi2V/sTLLstNv723eLfuWuZ0rRLPW9SSx1yztry3bzYluN3lbl2fJs/u/J/cqKgU48n
                            vSPP08AXOsNqcWoKsO2Vbi1mfe/y7PuO/wDEvzvVXUtHbwxpd3piszxWDRItu6+bti3/AGjfE391
                            Pvf8ArrfE+lLpvh/QrzTJZLzVVtfsV5bwz7HlTf/AKO/z/woiOtc14/s20rWrTU7bVWvNKXSZbe8
                            R2+dV+0O8Ton+w/7r/vj+5UeyNvaHlniLXovDGlveWOtR3l9ZQXEUFu9qj7fK+dEeJv4X83cvz/L
                            XzvpXg1rfwldtYxNZou6LyXb97PFs81LiJP4pUlRF3p91X/u17x4wuote16LbbQfa2gldrjyk8qd
                            mRNn/fboi7K8VmubbUtBW7ub5Ut7exlvdMTe6yysyIibE/hV9jqq/wALOjVRcpHn+t3Nml/pVzcr
                            sRoP9M+z/IjbU+eVE/v/APsz1x/nTusref5Pm7YmZG+9tfam7+833qv+IdY/tCXT2aDybhYvNlR1
                            3uys+xE/742LXOzfubfyrldjtE0q7PvqrfcRv/Qq0jE5pSLbXUr29ru3QpEyp87fIqsrfJt/i3/P
                            XoHwz8H6n4sXWPsrRJLawSyy+d+6SW1gTdKny/N9yL5l/iWvP7KGK6VcqzebIu2JPl+VG3t87fc+
                            Xc1fZX7NPga503WbS8+xxzJYfaJVmu4N/wB6VJfn/vN9l+7/ALMrr/HWmpEZH0H8EPA2mf8ACK+G
                            teubaeG3v/s/kQ3cWx4lZHeV/wDgf/siV9IW1tLYLZTzszytE3zt/wAsvk+T/vise20SKzitPs3m
                            PbtdLexedF+6ii2fJEif3a6KztoryW4WDciy/Js3fxKlKJEpGbqTs918q74otrrCnz/99f7W+uZ1
                            XTf7Vlt1eKNLvdvZkb91/wDZ11Fn9pTZFbK0178yS+d/zyX+Ouf1W885ri2aX7Aiwb7V3T+L+OtC
                            Tndb8NwTXEsE9zPNE0G+LZ9xfubErE1521XSXtoHkfyollZNvzrtf+D/AGdlbuqwrpuqSy3Mq3lv
                            La26b0byvKbe6o//AABHrN1KGV4L2JfnRrrymuIW+7FsqNTVHmLzKn2K8glubzTLCJYv7PeJE23T
                            b381/wC79zbT7N53luLZZY7yJmf7K6Lv8r++j/7m+tW28izutdnW2u5ruVWRbd13/Kv8f+1/BWVY
                            QxXi3q6VLvsrz7R5Vwvz+VuT7/8A31WR0mZZyXKX8tnbNHDe2DN86fIjKyfI6JU2q6U1/qSSreKj
                            /Zl835fki/4H/uPTP7KV9ct9QgZfskVmyXSw/flb7ifP/sf+z1Y1LbqXmzzv+6Zfs7PD/c2fJUD1
                            MTRLae2byrnbNLEvlLNCvySr/fb/AL4rY02aWw1Z/s26a0+V96bNm7+5VXSrODRLVP37TXDLK/z/
                            AD/98PV2z817WFV3QpKvzbPv7qA1OrhvPtlq7Kv+kKu/5G+/W1pusW015esy/uootipu/irldBvJ
                            ba63NtRIv++G21sfLtiuV+TzV81k/wBqrM5GhczLMssSxNDKy/x1pW1y1tcRT7lSJotjPVK2v4NS
                            sH+VnlX7z/3qZvlv7C3s22o6tvZ9v8NaGJralrCw6M8q/wCt3bItnz1j6rZq9um5fnVd9UfEiSpE
                            jLLvii27djfxVVudVvJrf7zQ7v4P7q09Q5TM1J5YWt9rb3aora6+2Tyqv3F/j21at0X/AEhWZv8A
                            Z/vrUWxdHt5Z2dXdl2f71ZG0TNuX+0XSIreSkTb/APerXhhiuYtytsiVt7f7VYVhvdvI3K6M3zVq
                            xwslnK0C/wAXzVMeYJAm51eVfk3fPvrPtrmWz2Kzqibd/wDcer1m63MVvbfwffb+/VG8hihvE3Mv
                            /A6vlEdBbTLtT5t6Mu+qsLyuzs33F+9XP/221teJAm10b5G/g+9XUfb1miSJf+Wq1cTL4TdSZ7aW
                            JVXZt2bf96uws7ZkXz2Zn2t9/wDu1yVvcxfZ/NVfvbX+992rVz4n8mziiVt+372+tCDq7q8WGK3V
                            mXZuql9vitl+9/C3yVif2kmpbFVWfb/tVlfaW+0Jt27FVkqA5S7czb7x2b5/l2fJXP3yRXLfMv3m
                            rTuZluV27tny/wAH/wAXWSk0W2Vv42+RUerDlOX1WzV2+X50376868W2fnRf73z/AO7XoutzMksS
                            wfc37G+X7tcbrf8ApMXy/In3P7/zUFnjPiezZ4niVmdK8X8YQrbb4lb5/uNsr3jxzMthZy7dvyq1
                            fPt/HLqVw8rLsRfnbZ89RqB5praM8u/5tm2sVhtOK7LxDYKlu7N8m3/7OuNZcNXRTPNr/EMoooqz
                            mCiiigB67qG/2qZRQBY3qi/7dRb6ZTqC+YbRRRQQFFFFABRRRQAUUUUAFFFFABRRRQA6pk/9mqGp
                            o6mRcfiNKGbYy7fnSrdu7fI3/fNY8L7GrTtptny/x1y1Inq0JGlbPs+VvvVt6a2zZurnFff/AL6/
                            erWs5tny/wAdcEont0pHVI/7r/gX3KvWab5f935FrPsNv8X8Nattt837v/jtZHVqascP+j7krYsN
                            qSor1lI7P8u2tOwTfKny1GoanS6bN8ybv7tbttt2/N9+uds/4F/u7XraSbYyN/wKjU1NvZvWonm2
                            Mm6rFrNvi+b5/wCOq9ztmZdv31o1JPgeiiivoz8/CiiigAooooAKKKKACiiigAooooAKKKKACiii
                            gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKA
                            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
                            KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoo
                            ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiii
                            gAooooAKKKKACiiigAooooAcibqXbuoT/WVesbCXUry3ggVpJZZUiVdv3magD3/9jf4FT/Fb4l2l
                            3dQN/Y+my+bP/cZl/gr9eLDR10qwt7O2iXYq7Pkryr9kj4M2Pwp+FGlQT2ypqcsCS3T7fvSt83/s
                            1e5bGj/ertTb/s1x1PePSpe6cPrdsy3TxKqpt+9XH+IfN+eKCBXdV++7bK63xVeRQ3W5vnlb/wAd
                            rldls91FLOu+Lb82/wDjrmPSieM+J9Y+R7ZpY0lb5/k+dK861azaFrdp/kRm+/u3/wDA69F8f2Ft
                            c3lx5SeT5XzqifIjfP8AJXmuqpcvapulV0272/2V/grmlE7InM628t/f7VXfsX77/JtrHvLxra4R
                            Z1V0+fb829K07mGebzZW+fdu+/XOXMPkyozK2xd27/7CpLK/iGGJLWJli2bv4/73z1zqIz36btuz
                            aztsrdv7+KZot0W/7235fkrMSzaFnZotjt8ip/HWpiZt9pXnXW1duz76/wC7UMOj+d5sTLsSJd2z
                            +CumtrHzt7N9+L5GrqtK0T7ZZ+REqv5vz7H2b6iUgjHnOFsNBW/dP3DJL/Ds+4y17l4D+Hs80Uqr
                            BG8sW11/gdf9yjwl4Jiez82e2VEi/jTe/wB2vbtE8GNDZxXNmux7j5fJmao96RfwDPCXhtdNVIIE
                            nS4+5Km2vbfCXhhrZXVlXf8ALKv/AAGqXgPw3K9mjXMSwtu2fI3yKv8Ac/2q9G0qwlht3iWX7Tbt
                            8m9G+df7n+7XfSpnBXqFq2s7aG1doFZ33fK+3Zu/v1z9/wCJ4Jre4igZnuLdW22+7Z8+zfso1vUp
                            La6Sxnn86KJvNZJonfb/ALm3/brC1LR1v21CXzZ0llgZ1hRdkSt9/fVyOaMSxpWiNc/aLa5ZXslg
                            +0Sw7k3xLs3/ACf7NV7b57DT510W2e7tZ/Kbzl2PB/B/4+nzf8DrotKm1OHTbKdmtpniiZJ9kXlR
                            Kv8A+xWFf3NzYapuW8h+zyyokGz+H5P4H/hX/fo5S+bmOa8T20r+K71ltraa3l0zzYvs7fdWL7iJ
                            /tb3evEfij/pnmwaVrSw3thY291LsVInilZ/3qbP4ldE3fc/j3V2D+M7PW/KjvJf+JrFut75LfYj
                            xXTSukWz/gGz5K4WabV9V0PWLPV7a0S7/wCEiuvKR/3rxbfkd3/2dmz/AICiUSNoniniF2+2I2nb
                            fKsIPNtX81/vb0eJNn913d2V/wCJk+T+7XnXjP7TZ69dweaqS28/zO6siKu+J96Js+VU+T5K9t17
                            w21wi+HLmSTRIrXYl4+1bhJF3tFtR23NtfzVZX+XbtrwzUNQvLyC+tmkZ7qKJb1JbhVSWWVdju7v
                            s/2E/wCBP8v36g01PMJLaBfttzct9stUi81fm/1rb32f8B2/+gVlahDK7uyrstWTeqP8+1Vfbt/3
                            lVVWte/vIpryWzub5nsll82eW3i+8v8Asf3V/wBisKazjsb63bUm86GVfNZfN37vk37vl/3q6jlq
                            HR+A7XTLm8SW5tlTTYpd7fM3myr8u+JP7zbNzbP9j/ar9Gv2adNfVb+3ig1BvKs7pktU3ea89vLE
                            m/f/AHW8rym/4BtT5a/PXwCtvbXKwXLeTffvbeWbarK0Uvlf3kb5vnbbtr9P/wBjP7ZNYRK08V/p
                            +2623bxb3lVXSKLf/dbZ/f8AurQR9k9+fSvsf+jLfNfvFEyfO33m3/fqx5NzN9n/AHvk7vkbyV+8
                            yvUtn5H2i7iXd80rP5z/AN2rdt8l0m3a/lbZZURfvbX+SgxkVLmwl3Pc2aqlwsXlfvv4tv8Acrz/
                            AMQ3P2mWWxuVX+0FtW2+d9xfn37/APdrvf3u3b9sbyombck332eotStoHt91zZr8v7ppnbfui+5s
                            qwjI8/udB/tKziuftMUyN/rfl+SXaibK5K5dpr/VW2xzJLAtw1vF8nm/wI//AH2leoTPsjt7NYv9
                            EXzYlT/a2b0f/wBDrmbbQYrDTbf5VRIllla4dvnb/Y/3U31BtGRyTvPZ6k95eRfY3VtkE275Jfk2
                            P/6HWPDpWyW0itoJET7V5Ur7fkVW+R/kp95/aeq2Grafc3kCW7KqQTeR/Crp9yuj0pPtOn3DNOyX
                            sqttuH/+IqDY4HUrOfwwyy20TX9vFK3np/d+f79Ymq2F1bRahYwW2x4pWRn3J8ysm/8A9n212dyl
                            jZ6lqcTNPNZLAt6yI3z7qZcWa3NrutlZL5ovNld2/wBa1ZGxwVtDP/ZqTyvHCkSp8n391W7a/wB+
                            2JlXfFFv37/u1Lc2d5Nrl7B9mWGVolSL5fvM38e//YqpZ2EttL5GoSs/y7G+b5G/36kZvaJc226V
                            f9du+f8Av7a2k22yytLuf5flT/7OsezsG0+z81otiq2xX/u1evPNmsE8ht8X8Oxdm7/b31RnI6eG
                            2ttNt4oml3/L5rbP71NdYJr+02t8kv3v4PlWmaVDFc2tp9pbe7Rfxr92quqvvliWx+R7Nd7bF/z/
                            AH60MSvfzLctetOvkorfKn3/APgdZkN5E9v+/wDvt89SzW0t/cPEsu95V/gesp03tdKzeT5Tf770
                            9S4lS/1LZebW/wCWv/fFZWpar/orqjM7M2z/AMfrQRLb7ekrbd6r5q//ABdc55zfbJW+WFGbfv8A
                            +B1kbfCXtKv5/tUrMuyHb9/+7XYW2pLZ6Hsn2pLK+9t9cvbPAi2+3987fO38FWr91mtYpVl+78n9
                            +nEiRoWe2a6+X5EZt7P9ysXW7ZkvJWVmdF+ffVhLz7HFuZm/uq9YOvalKlg+1l3s2z/YrTUgsW15
                            FtRtyu+7f89dMl/A9ruWVXda83mudsSRK33fvP8AwVseBr/zldZP73zf8B/gpRCR6RDefY7DazbH
                            qi837qXa3zq38dYt/qv2m4itmZt+756z9V1j7NG7fcdfnp6kROts/EK2dvL5TfeqWz1JZv3rfJ/s
                            bv8A0CvOrHxClzbuq/fWLev+1WhDfrC21W+787P991bZWfMUd79p8yJ90uzd8n3ax7yb5kZfuLWe
                            9/PNcJErb9q7mptzdMn3vkT7/wDv1pqBX1KZnb/armbl/O+b+Ffn/wB6uj1W8ge3/uO38dcp4hmX
                            TdNdvmR9uxaNSTyLxm39pb4F+Td87V5ZqVmtn5v8Hy/fr1u/s2ht7hm3eb99v9379eVeMLlfKfa3
                            3k37KNQPLPFuobomVfnRvkrh/wC9urs9eVZt+7+78rf3a4+ZG3VrE468SvRRRWxwBRRRQAU5H202
                            igB0lNoooAKKKKACiiigAooooAKKKKACiiigAooooAft2tTkfZ92o91JQBYX5mq6i/NuX/gVZ6tV
                            5Jv++N1YyO6lL3jVR/l/4DWhbN935W+Zaz7f/Vr/ALK1p2b7Nrf7y151Q9yh8J0WlO3lfL/FWxC7
                            baxNNm2LtXb92tu2dXVP7+2szuNizfd825q3dNTe/wDFXP2z/Km1a6DT32f/AGFZGpvWD7Jf7/y1
                            uwuyL/DXOWz7/vffrbtplTZuqNToiaFtNsbbUu/5t33Kqpcq/wAzMuz/ANCpk02+jUk+GqKKK+jP
                            zwKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiig
                            AooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAC
                            iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKK
                            KKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooo
                            oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigB6fe+avpD9hv4Vt8
                            S/jhp7ywedZaWv2qXem5N38CV83rX6q/8EyvhW2l/D+78QzxbLjUpd6v/s1EjanH3j7asNK+x2sS
                            rEqRKuxdlZt5uhll3fP/AHa6ryf9F+aua1KFoYpZZZV2L/BXPqd8TzzxbbfbGdV+R65LUnisLVGn
                            3TSqvy11fie/VLjz2aP5W37K5rUnaSz89tv99a5ztj8J454zfzm/f7kRv4/uV5zcpFeK7W0rOitv
                            ZPubv8vXrfiR2uXla5Xft+7v/vf39lef3+lfYIpW27PNX5f4P8rXPI64nD37s8W3dvf7/wDsVzl+
                            nmXCK0S/L/HXTXKed5sTbUi/v/3qz0sPtK+Uq7P7v+7WRsc4+lsrI3lb9/z7P7q1bttJi1K4/et5
                            Lrt2/L/drSSHbdJF9zd8m/8Ajrs7bwTY3Mtoqy/e+9/f3f36AOP0fQf9M8hV+9/f+41eoeG/h/K8
                            qKsUc1wy+ayJ8+3+4i1q6b8N4k1z9xF51vtV97t91f8Afr2bQfBNjpuxl3XiKuxUT+9S5SJS5PhO
                            Z0Twk0Nn9juYm2LEu2GH5NzV6doOh2dnZvZxytD8q7d673qXw3ZxTaojLHI8rtsX/ZWu90TTba4u
                            pZZ4PJuP4d6/w12U6Zx1KhV8K6U32NoG+eJWXbM/3GrauZIra4l+VnRlR2mhbZt/+Kq3baVBoNvu
                            topNm7evzfd/3KpXjz/aJZFZdkrbVhh/u10/AcHxSM+O8XUpbf5lmdWba+2tL+wYoYomVo/9q4/j
                            /wBjelN03QYIZbe+VfOl8pv3391V31Dear9pt5Z7OVpvs6t5ton32Vvuf+P0RAiv9Nn1u8uJ554/
                            KZWtbq3dtiMzROiJ/wCP1wl4n2/+z7y2s1fSvK81od3+tiV32Js/hb5Eru9SSCaLU9v+nvYbYmT5
                            02/crhJtKvvB+nyrbSrfyxebe6cl39yX5/8AVb/72z+CtC4nJar4Vs9bsNVngWCHUL9be9gaZt/m
                            xNvdE/3t/wD7JXk+q6o2sa5dfap7mz1iwlisNdtNvzxXn+kNvlT7rq6sv/Adle8eMEtr7UrfT2i+
                            xxbor1bi3fZcWrNsldP9r5P/AB6vAvGaf8IrrKahbWzX+p3+prqF5qaN/wAhKK1lRJfNT7vyb3X/
                            AIBWEom0ZHmnxCvJblU1zTFaa4sNO8rVUsfkSWw+dElR/usyNvX/AHX3V8/+LbNrzVHliXfqF/eM
                            k6OvyRKr/IiP93aiJu/4BXt3iib7HcaxplzffY9Hv0ZJbiFvKeW1vJZZXt5U/hWLyolXYvy7/wDb
                            ryfxLcLLZ+F9Hvlksbho/K27l/dJLvR3Zl+6ybN+zd9zf83z0cpR5fqOsW+la1ewW1ostvL9qsP+
                            Jmnzr5u9El/2WVW3f72+uXW+aaRp7l9kqrs3Kq/Nu3bv/Q66jxtrEmq6/cT33l3968qyy3aL97b8
                            ruu3+Ftu5f8Afrgmm8plbzPvfe/8draPvHJKXKdro93BaaxpV5BAvkxNEsq+bv8ANddu6X/ZX5v/
                            AGWv1V/Yn1WK88M6nuZrzypbXyoUXypYomuHTe397Yjozf8AAK/JDw9fRWt0J1Xd5UUrxxN93d/B
                            u/4F/wCgpX6GfsYfGC502/t7P7Y01pFFFZLMlr87RSxO/m7/APbl+Vv9pE+7/EfCX8UT7u0vWINb
                            1S9VYv8AiXxSy7tn/LVl/uf/ABFX/JlmlS5V2hT/AFrW/wDwB/v/AO5XNeHUnttU1OxVY7D7G2xt
                            jfJO8vzyv/vV1Fm9tDeoqs3lS/e+Z/vbKuJjIz9W0dbmK03Kz+bOsUru2z918+/fRf2E+pWsUcCq
                            lusTbpv4/K2fwVq3L/b72LdudImbcn8DNsoubOVLO3nWLfKyqjQp/dpkcxzSabLbXV3eNctNaMux
                            YX++rbE2PVLW/wBzYXFsu54pYmSVP97+BK6rVbNpon+b5JW+bf8Aw7f/AGase/02C2s7iBov3qwb
                            4Nv8NAcx57qulNpt/cM0UEOleUqWqf3W2Vk3NhLpUrpOqv5XybN3+tZkrrtVs/8AiTWnm7rxIm82
                            X5fnrE+wfZrfT765b7ekUS7Xf+9WEonTE4ew0RvNt1lVby3b915yN95f9un3Ltc6t5rM0Nr5TRM6
                            L93/AIHXUXNvLZtcQLLGkW3fBD/tffqpc3+/TfIurbzkvF+/t+eKo5TY4dEnSW9lgg85ImV4ndvn
                            20y2s/7b2Ssu+WWXeqbfu1oXPySvt/cv5W35P4v9+rdtpOy3iZZ282LykbZVgZ72FzYWr+e7TOrb
                            /J/2als5t9ujKuxN33NvyVsXm+a48hfnf7n+9Wbc20+m79q7HX7yfwf98VHKQaFzeLZqzMrb9uxa
                            qas8SW7rB8nm/efdT9Vv/tFuk6rvl3bP76ViateLc2CMzfIrb2dPk/4BWmpRd1K5azit57Zv3W3Y
                            3yfw/wC/WK6Pcs8/mrDFu+b/AGq1fGb+doOmNE3k+b87Inybf9xa5R7nYstsjrsi+9/f/wB+siSx
                            rflWd07L8iMvzO9ZWqwxPpcW1mheX5F/2v79aFzCt54ZuLlp1835kiT+81cU+vf2lb26/MnlL838
                            HzfcoLNXUk+x3ESxMz7l2M+5Ef7lCaks1m67/ut8v9z5a4/VdYZ2TzZfn/772r/cpthf7P3CtsTa
                            3yf7P8CVoUdI95Lfy/e/dKn/AADcv8FZT3jXLIrfIm7f/u1Fba3slliZdjquzYn3/l/jqpDf/fZl
                            +SnqQWLd963DM38NTaVrC6UqK06pE3/jzVialeMkSMvyOyv/ALG+sS/1JmuIlVl+8qbP7y/36NSz
                            05NSZ281fnf/AHqzLnVYprVFaVXi+ZPn/iffXKWet77iKKWX5PN/z/vVX1W8aSHcrKn97+5RqQa1
                            trC22xVZd+7Z97+GuisNV33Dt9/b8n/2deOvrEsP8Wzc38ddLpOq/wCkfM3z7vl/2t38dBZ6rba8
                            26WXd8jNUt/qrTW77WVHVti//F1wqX+9tu7/AGPk/hrQh1Jn2szb9rb/AJv7tZAdneOqWe1fn+b/
                            AIHXH+J087Zbbmfc3zf7tbek3K3Me9m/es29a5zVt1zrLLu/u1pqBz/i238nS/lXZubYvzfPtWvD
                            PENhsldWb5FX5fmr6D8ZvF9l8pV/1S7P++vkevBPEO77Q8Um3/Zp6kHmWt/edtq/7Py/JXBXzedO
                            xWu/8QwtM0qruR2/2vkauCvIfJl2/wAda0zkr/CUqKKc6ba2PNG0UUUAFFFFABRRRQAUUUUAFFFF
                            ABRRRQAUUUUAFFFFABRRRQAUUUUAPV9rVYt/vVX/AIqlh+9USNqcveN22fcqf3P92tO2T+F1rHsf
                            mirVtvklXb93+L5q86p8R9DQN2wfZ95v4f7tbdtudX/ufw1zls+/Zt/vV0dg67fvb/l2MlYHfE2L
                            D7yfe+Za3bX5Pu/8CrCs32b/APO6tNH2MjVkbcx1Fi6IvzfwrVpJm3fMy/d/76rFtrn7nzMn+/8A
                            xVoWzrt++z7W/hqNQjI1ftOxUZv/ANih5v8Aa+es/wC0rH/F/wB90+S5VItrN/FS5TQ+N6KKK+kP
                            z8KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiig
                            AooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAC
                            iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKK
                            KKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooo
                            oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiinUAa+haPPrmtWOmwKz
                            zXk6wr/vM+2v3v8A2dfAEXgP4c6JpSxeT5VqqMm3/Yr8ev2J/AA+IX7Qnh2Bk3QWDNey7v8AY+6t
                            fulYWa2FrFAv8KrWMjsp/CMvPkbatc/qrr9ldWXZ/wCzV0cj+TvZlXZtrj9b0q8v9ZRVl/0Tyt+x
                            P71YyNonmXi3R1mtU3fP5XyNv/irlNS8q5t1tmaSHav3938Neu+Mvs0MSKsTb9/391eW+MJot1pE
                            0Wz91s+f+JaiR2U5cxwOpab53+tl+T5fnZvu15/4nhW5v0i89kRVbykT53X5K9O155b+wiVYI0Rl
                            2L/tLXA39nLDcLfLF5zy7vn27P4K5pHZE83hsdl46tG0yKuz/eamvoiw3Dqu50ZfufcT/vuultra
                            e8voolVt+7zWf/gfz/8AjlbEOmq7RfuvOTzd7I/8S/x1zm3Mclonh5X/AHvzfK/9/f8ALXqHh7QZ
                            bmWy/wBG2Iy7N7/J/wCO1q6J4Vgm82VYo0i+55P3K7PQdBitrplggkm/2P4K15SJSDw94SaGJ9rR
                            vKu77/3K9F0qzieWylVlR9v72GFfu0/RNEge8i3N9jdv9n+KuisNKX7Q8E86pKn3vKX73z10xicc
                            qhFpuifYJfPeBnTczqiffrtbaGKG32tEsNw3yfPVeGw2NtWX91/D83zrT7m5V7iKJpWmdYt+967I
                            nBKXMV7/AE37fE+5v3Ssu16Y9t9mi2q291/j273ip7wyXl06rKv2ddn3PkdasaVpvnTXEqrIm7d/
                            oj/xf7bv/FTGXbeFptL2wboUlib5/ueVu3oj/wDfdef+G9VbTbXyrmXftllRXmX96zRP8+9//QUr
                            rrnSvti/6ZueJf8Ani33vn2f+zvWJYQrc27wXzbNPvN0SQpFsTbvf5H/ALzbP46UhRDVLyXTdUuN
                            tnHZ3V1Ytcf6dLt+ZU835/8AceuZ8eTQXMt3pFp5U1ksXlWqTN86/uk81/8AeR6t+IfDdnrdxpkC
                            xSX6eUtveTS3Wz90jp9/+8vyVwXjN538UXdtBqHnae1nK8E33HiuFd/++V/9C+SpLiYXifxDBcqm
                            p30qzJZxNbs8Lb3lt2TzU2f7mz5K8U8eaa954T8SwSXP2+4vNFnt9O/5+IvNl+1RSrt/glR3+583
                            yf7dep6lpU9zb6nbafuht9ZsZbKe7m+eK1bYmxET/gb/ACf3XrPvLPSLDVNPvtVnj03T7xm1Ce72
                            +a6ta2UWxP8AZ2bErPlOg+WviJc/adQu7bU51tvEEWjp9mmZvkll3xfaIpW+7tdNn3N33/8AfryH
                            xBfprdvcfZrbyb1miee3SLZLErI6P975m+d/uJ/C9el+JJryb+0/9GjsItZs4ooLG4g2OsssvySo
                            m99uyJ3b+6u9P4q8n1rxUtveamlskj6lLPF9j1BG3OqxI6ptX+HfKyfNT1HI5DVpp7G4mljdVuH8
                            2wli3K6bVTZsXb8v3dtcjc7k2/d3Mq7q2NUuZ7OO40x5IniWdnfbtf5v9lq5+4+Taq9dvzVrE82o
                            WNNmZLjYrbEl+Rq+pf2cviJ/wjGtxWNjO268a3sm3/O/y3ETokT/AN1N3zf7L18uaUnk3nmsvyQf
                            O2+uv8DeJl8J6xp9yoZ7i1vIrj+4mxX3On+zu+T5v9haJR5i6EveP2e8AX8U2rXd9YtJeW91K1xO
                            lx/yy+f5Nlel3N+tnqlpZqvyNu+1P/d/dPs/77r5/wDgJ42n1jUrJrmWNJZYluJbd5Ul8pdn3Plr
                            27RLmLVby71xtMnmuGX7nm7NsX3ERE/i/vVjE6ap0WlXk/2qKJomdJYGdf767v43rTe5aG8stv3P
                            mTZXOW2qz/bHtovnuPNWJURfurv+d9//ALJWq9mt5ePtlbZu3rN/d21uc5FqVy0LPt+d22XDI6/J
                            WPcor3H2ZWWaV23s+7/VRLWhqV59mvImX55W3O0L/c3L/wDt1j3MMtyvyz+T/A3+zQBn6k7Qt5Cr
                            HD+9b77fw7H+esdN2n6b5DQLefdX5P4at6lcr5srruv0VVinRPvstY95Zzw6bewW0TWd7F/qt7fJ
                            /sJUGsSpeWy39ms9mqo8UW9UmX70v3NlUptSiTfBc/c8pfNdErQsJr620RFnto5ru6+eXZ9ysm5u
                            ftN/bxXltvsW+5/cqNTYz9S037Gu623TJLF/GtUn02fTYrSe2l2JLueVH/z/ALdaF1c3Kazdqy77
                            dU8qJ/4P9yq9ykSS7VVZovuM6L8lGoBZ3iw6bKzMsLqvm76papCz6WitL96Jfn/vVYsLODUv3U+6
                            Ha29qqQ3ivdS2bK37pt+9/7v+5QAzSmis7dN7fJ9z/erPeztry6+zK2xPK82X/gX3Kfqrtcuirth
                            ii+T5F+7XLu8v71l+R5WZt+7Y+2lIot+Ib+B7e0g81n8pt6On32/4BXL3l/9pilVvk3Mrt/f+b7i
                            f+OVLeXK20V3Oy+c7f7W9/8AbRH/ANyuHm1VXl+VW2/wf7LVmB1F/rGy4SzVm2bfmT+98lcPc3jW
                            yuvyo7Mv/Aa0Ly5WaWLbuRPl3P8AxszVharqsSWDqq/Ju2f7fy/3601NPhGPeRN9ruWZfKi+Tf8A
                            7S//ALdZWleKv9MedNu91b+L+Kuf1DUms4kiaXfE26sHVbyWzVJYN3y09RHfPqsryvcsq72+f/er
                            attSgvLd938Kq+1P9r+NK8afxb9zczTbfvb61rbxItzLuZvu/wBz+7/co1IO/wBSuvOiRW+dF3fJ
                            /wCz1hX94s08SrKvm/xP/tL9+sd9YWS1f9787fx7/wD0GsJ9WZ5dyy/eVP8Ab20FnVPra2146q29
                            2VZV3/c+589Tf8JI14rtu3xfKi/79eearrDW8v8Ardj7d6/7NP03XtlvKqN/rdrt/tUakGlqt/K9
                            195UeLd/DWtpvidXv/KTd/ql+euM1XWGhilZm+9u/wB+szR9WX7QkrNvf/bb+7WfvFnv2lakvmbn
                            l2J8j1tTa3E+yBfnryWHWGhVG3N8yrWlYax53lM21P4F+b56JGkT17Tb9ktdzS/PtV/9tlpltfrM
                            3nt99m2Vx9hrHy/MzbFi2LW3YXLSW6NtX/vqkPUo6xftc+arfI+6vJfFttvldl/2kr0jW/31vcKr
                            bNv8e6uJv7aJ/N+Xe6rv/wB5qfMKR5LqsLP97b/3196uB1r57j7v3a9L16Hybp1Zfvf7VcZqumt9
                            n3ff2rW0DjrROP8ALod91PmTY1N2/NXSeUMooooICiiigAopyJuo8ugBtFO+7TaACiiigAp1K/ap
                            USguMeci2mmVbdP+AVX2/NQEo8oyiiiggKKKKACiiigB1TRttqGpI/8AZqZF0/iNS2m2/J/B/t1r
                            Qv8A991g2zb2+atuH7qVxVD3qEjTs2b5K6Kzm/i/grlbb55Ilb+L7tbVtMqLt+5XMelE6u2mZ12r
                            /uNWglyqL97+H+OuatrnyV+9916u/b12/M/zt89QanR21zslRlZdtWk1Jo1+Ztn/AAKuStrxkb/W
                            tsqw94rr8zN/31UcpodH/au/+JvvUz+1W+627fXLvqCo3zNv2/dqJ9V+bb5rO/8At0cpHMeH0UUV
                            7x8MFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFF
                            ABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUA
                            FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABTvMptO8ygD9Cf+CUHg
                            NdS8W+IPEckW/wCz7bSJv96v1SuH2LtWvi//AIJd+AG8N/A/+151/e6lcyv/AMB37K+0Jk31kd8D
                            PufN8p/mrH+2RfZ3bzdm1t7/APAa3blN6+Utcv5MFnburbftDS/Kn/A6g0Of8VJFNZ3G1tkqrsXf
                            XkviyGWaW0iZlm2qqb91d78TtKvnvH2zsnzfNsrgktlRninZZnXc7PWEjrpHH6rqvnXkVs0qwxRL
                            sVEbf/v1jzWbXmjSywXPzs3lRW6Vpalp8T3DytFG7srU+201XWL5mhSLc+xP9yuaR2GFYeG5XtXl
                            X9zK3yLM/wD7In92rVnpS395b7tv3f4F+9WxDDLt8iBd6Kuxf77bq7jRNEgv9kVtAsL7V3VcYhKX
                            KUtK0SdLBPIigTd91H/hrvdL0vYtvB5vyNF99F/io0Hw99gW7iaJn2t8u+umttElRbeJW86X5f8A
                            gNbRicEpFrTfDau2ydmR/lroLbSo7bfLbRLsZtn3vnqK2sZbDeqtJNtb5vOb7tXfOWG3iWBVSWVm
                            TY9XE5yK8s4kt08pWTa29v8AaqlbOrt+6bzrj+L5fvf7D/3atQ3k7xItzO3lM2zZt/iq2ieSrwQK
                            qbv463IK+yKO8iW5VYU2/vUT5/8AcStC5haG6SWCVobdml83Z/FVKw03fql3eNOz3EqrFsf7jLVq
                            w3PdSsy74ol2b5l2I3+XoAzb/Tbz7VabpZ0eJli85JfkZfnd3esHxPrFn9gtJXWOG0+3fZWmdv8A
                            VNsfe/8AtLWtqurahc3n2GW2aG3iXZvm+5+93/8AxFcz4keJNDl+0tstG+0bUfZsVloKic1DD53h
                            +40+DT7lLuWxlsvOdkTyvNidEeX/AIBVe/0G+muEtrGW2d7JotKlu7dfvMu9337v4HTZ8/8AsVdv
                            NVnmvrdvN/0KVovtVumxJVVvuRf/ABVc/wD8LCvE8QRK0Ec1k159ovHRv9Uv+qid/wDvhFqC+Uz/
                            ABnusNPliVvJe/1P+0LWFPnls7pbdEdET+Jfv/8AfdfM/wAXdbufBlrcRRag2sbfs9/LM6/8erS+
                            Ujoifdfem9fk+7/wN93qHjO/i0f4e/2ZPqsf9sWEH22zuEV5bhWnll3o/wDwDZtr49+Knjyfxto1
                            pqu37BZXEvyokr+azL+6SLZ/e3RO39396n9ysJSOmMSLxn8SNM1jTdVivnu5rjzWfTNzeVLa3TSx
                            LcPK7fwvb79qfd+SvD9SZbXR0ljnk82a5fdFMrLLFsRGR/v/AN1q6PxZrX9m+INSkWOCa6vIGhni
                            uIkd4pZUVHX+7uRV+9/Cz155qt1JeXjzz/xJs/4CqbU/9AraJzVJcpY1uaWadt06zlv41/i/i3/8
                            CZmqpDbsk3mtuRFi83cvzf7G/wD76q3feH7620C11VoGfT7h2iiuP4FZfvp/vfMlV7fWJ7e1uLRZ
                            W+yyp5Trt/g37v8A0KtDg5iW5bztLZfmml83fK6r/BsTZWfp+77Uqru3s2ymW00iOyrIybl2ttq9
                            YXMq3HmbWd9v/A1/3aoI+9I/R39ifUp9V81dTvJk3WcvlfLv3KqbPN37PvJv27H/AL9fcGlbrazi
                            s7G2aztIoFtfORv9Uv8AH977z18KfsJWf9j3Wu2er/afslxZxXEtikTv96X5Nn++n8Cf3K/QC82/
                            6PBbMqW/7qVv9lV+/wD+OVzRPSkaCWEVhEixLvdIpUXZ/d37Ki1u8+xy2XkfOkTeUyJ/B/tvVTVb
                            z/TNqrvdWV2mRtnm0zW3ihVFgbzruVN67P4lrc5w/thba6lln+SJVb738VYt5qs6QW7rB9jeWLzf
                            Jm/ianX/AIh0iG4i+0rvt5YN7TIu/b/l65LxDeXOq7LmDz3uF/dL53/LJf8AcpcxrGJoaJr0UOs+
                            RbQeSjReayN8+5qrv4k3aze21y2yVv3q/L8n/wBlWZfv9jWyiVvOuPNXb/fapprb5ftlzAv+i/Oq
                            ffrLUvlGWGpRI1xFbM3lRLtVHrHv7nzliig/fJ5Wz5H+7VTVZl+3peWO14ni2N/f/wCB1lXV5LpU
                            NpeKqwvE29kdvvUall3ULqVNJliVtksW799/A1NhdZtJt/tNz+9Zt+z+8tVNemXUrOK5glZ3l+f5
                            /wCL/O+orOaLVdkHmskqt8yf3VX7/wD6HRqBDquttDdSwW0DIn31+b71ZF5rC3MsTJLsuGX5k/vf
                            7FUfEmpLCqSszI7S/c/ur/lK5+5sZXlsryzvPk83fKm7f9z/AG6NSjbm1hobK9WdvliXZs+/u/2K
                            peIdYim+Xymh+98+7Zt+T/7Osm41Laz3zKr28rf6n/a/+KrM8Q6rBqVlFFB86L96b+839yjUsz3v
                            5dVsLva2xLdtip/tfx7K5d3aa381l8nb8/3vn3f79adtrFtpMTytKz/Lv2fcRV+7/wB9VzXiHxIu
                            5Fi2wxfc2f7P/wAXRqTzDLnW2dd33E+6mz/0Osx7/Yz+f/F93e38VYWq3jQ/Nv8Al3f+O1z+t69+
                            9+b5/mX/AIDRqIl1vXPtLSxLuTyt235vurXNXmtyvF5Tbk/j37qivLlvtXmr/F/tVg6rc7f72/f9
                            /wC98tAFubUl+zuq7Zn3f99VX03xD99VZv8Aa/vpXL32sLbyuzL+9/h/2axE1WWGV2X+L72yrMpS
                            5D1OHxD50SKsv96pbbXtlxt3/d+6n8G2vMrPxC0Kr8v3f9qrcPiHdL/Eif7dZyiXGrzHd+J5vtNu
                            8q/xKv8AwGsSw1jYqfOvy/J87fdapbDVVvLfb9//AIDXNeIXaFvl+RN392iISkda98t4u5mV/m+4
                            9YSaqttqSRL/AHmT71ZVjr3lxbW+Ta33d1Z95ff6Qv8AHsatCPanr9nrH2mJF/yta1tqvksm5l/4
                            GteY+Hte875Ntbc2pMjeb8021P71YVDaMj1hNeVIomWVn+b+Cuws9SZ7NFT7nmu//fP9+vCrbxD/
                            AKPFXe+GPEn7r5vuNWZ0/Gdnco6ebu/5at/3zXPalCsPm7vk3LVu51Jpl3L8/wAtUrl9lu7bvvLv
                            /wCBU+YjlPN/EMLPcbl+/wDcrl9ST906t/F8jV3eqoqS/O29PvrXGX9qzsjMv3m31uY1Dzq+tZYZ
                            W3Ls/jqlGm6uo1232fNu3sv+1/ernnhZPl2fd+9XRGR5tanyyKtFORN1NqzjCn7flplPX+KgCWOL
                            dT/s7/w/cp1qv8W2tP7A01v8qfMtRKR2Rp88TF27t1M2VpJZ7NjMvyNVS5h2N8v3KOYxlT5Sv/F8
                            tHy0v+98tCrVmIbatQ/OzbarpCz/AHau20Lbvu70aokb0fiInh+Xd8tMWHf/AHa0by2VfmZtlVE+
                            RmX/ANAqOY6JU/eKrrs3VDVt423barVscco8o3+GinU2ggKKKKAHq1JTadHQBbV2Sti3mXalc/V2
                            2m2MlY1I8x6VCodNbTbFq7Dcq6/8BrChmWPZu27/APYqxDNvi/4F8u+vO5eU9iMjaS5bc67vkqx9
                            v2L8zbE/hrCSb7+5tn/Aqie8/vNv+alym3tInQfb/wC6yvtofWNm/b/d/jrn/tK/w/f3fcRqr/bF
                            3Vfs5B7eMToJtUZ96s2z5f4Krrcs/wAytWOlyvy/M29fu1Klzv2VHs5Ee1OSooor2D5IKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAH/xVoWGny399b2cZ3SzSrEv+8zbaz1r
                            0j9n7w2/ir40eDNMVd73GoxNt/3X3f8AstH2S4+9I/cT9mPwYvgb4O6FpnlbHigX5K9TmRttUtBs
                            /sGjW8SrsRVqxcv/AHqyOrUz7+Zk3uu3fXGSP9vuHVtz3DS/L/s11d/ebVlVV/hrgnvPsd/LOytC
                            +/5n/wDiKmRrEo68ss0TxNLvuJZd+yvLdVs5bb5t2x2l3tb7fvV3Gt+KlTVEb7+352fb/FXE+Ibl
                            rzUkuXbYit5vyNXPI7KfunOXltLqGqbVg8mVvuo/8P8AvVs22m3Nz+6Vdm77z/wU7TYWm1Ta07bP
                            ut/frq7DR2s/3rS7E3Kiwv8AxVmbSkc/bWE+lX6SqqzIsq7N/wDFXceGLNvt7y+Rvb/YbZVS5hWz
                            v4ln2ujNsVketjTbD7Hf27Ts3zfdStIxIlI3rO/a8lfdZ/8ALX76V0FtcxQxPFPKyPu2RbP/AECs
                            zRLOKwt5W3SeUz72f+81W5raCGWK5WVU2t8u+ricY6GaPR7/AHXN40zLufyVXfu/uVNbPLc3STtZ
                            snlMzqk0tO2RPdIy/OkS/wB371b2np5y+bcs3zL9ytySpbzRTf8AHyiwpF8+3+Pb/wCy76ZDeedq
                            TyrF5MW3Yyf3Vqx+6+9cqror/wCXqK5tludNlXd88rf8AoILFykSW+1ZYofN+RpvN+7/AB7/AP2W
                            otSv10Gyt4l2zSypuihml3fx/J8n8W+hLZY7iWC2b7q/NM/3FrH1Lb9sSdmZEt13+a7feX+P/vig
                            DBubxrPVpbnU7yd38iXzU8391EzP+6f+Pd/HXNeP/syWcUEEtzeSxQKzo6ukMqtL99933djvXS3K
                            zzaNcNdxLeRebLcQO/8Ayy27PKd/99//AEOuN8Ya3s03TGaBryKzurW3uk83e8t1v+RP/H6g1iee
                            eM9Y0qw0HUNV1qeOwuJZVe8dFf8AcXTW8sUUu/7u15UT5P71cV/wn9t4V8W/2hfLc+IdEtZdl1p+
                            n2q7LqJbeK32XDs+5WSVHbe6ruZ91HjDStPT4cvfeIbmG5lf/ia3U03+qZor2JE+T/Y+RV/368k8
                            ea99vXUILaCR7JYotViS4i2XF1apEiW7+V/dTykf7n8aVGp0HOeM/G2uTabqei32paTf+ILzWri1
                            bZK+yK1+46O/y7dnyLv+79/71eAeM9Utre8tNI0y8mmtLW2+zv521/KlaXe+x97blXb97/gNdV4y
                            16eFX8z/AFWreVFefvV85/KfzXfzf4W3S7dv3vm21w3izT7W0n3QXK3llf75baWF33q0rJ8lx/u/
                            P/tNuo1JlI5zxJeQS6zcTpHErKGieKGXejS7Nvmo/wDErferlk83zfLZlTd/fq3c2zW915F8rQ+U
                            /lN/C6/8BqlcQrbO67t/zfI/8DLWsTzaki7DrF5YRNAs++3kb5oWbdE3/AazHbeztt2U3/d+9/s1
                            d+y+TAsjD/Wf6tH/AIv9utDH4ivt8lkk/gZty1s6XAs19DPO0kFu7Pufb/Eq7tv/AKD/AN9Vnfai
                            0EC/xxfd/wBr591b3g2GCa8f7SrTQ2+5lRV3ea7bFRf/AGb/AIDSkXS+I/SH9id/EdzLLPqrLDp6
                            2dvL525P3Uu/5PkX+4n/AH1X2dfzLNbxXkHnp5rfuk2/w/c37K+VP2QtK1DVfCtvqbNvSW6WVrSb
                            5NyxI6b/APgFfVFtI2g2sVsq+dcKquz/AOzXNE9KQXNmtz9o+1N86r8r/wB3/f8A7tYrveTW721j
                            bLZpF8/2i4/hVv4EStq41K282KJt032jduT76N/H/wB9b6wrm8lvLXz7ZfJfa0UsM3z7ZV+4laEm
                            CyT6VYeVP5l+kTNF9rRU+78nyf8A7FPtr9UsEl8if7Qsq7V/jbcn/j1M0rW57bTb2BYlv7eW8aKK
                            Z2/i2Jv/APH6x0v2s5Lvz9thKy+UsMLfxf33qNTQtpZ3k11Fczs2yLcmx/v7v4KrveMlrb3M7SJL
                            E2z/AHv9+n2zxaVa6YrzyPEzebK71nvZ2upXktjBK0NlLul37vvNRqMZc232m8iVmWGVvuuv9z+5
                            WFrdn9suNs8Enmqvlb/K+SX/AD8latu/+hvPt87ypW8re1Y+g6reRtcfatszxK3lf7K/5ejUATWI
                            IbOytJ9u9f4P/sK5y51KKz1S7iX78q/w/wAP+xRf63Al5bzxKz3EsuzY/wDD/nfXO+J7aVFiaJWh
                            l3f8fG7/AMcejUoqeIbmW8+0Xm3zorVX83Z9/c38Cf7mxK5e28Q77qKDe32dV/vfd3J/cp+t6r9g
                            0u4g3K8UW55X+f8Aes38H/feysezs/t95Ft+d1V32f8AAP79GoEuq6lsidt7JaKy7d//AKGlYmpa
                            58txLBLvTav+/wD79VfEl5G7eUrb0X73zfdZa5+6v/7N835fOSVd6/7VGo+Yu3OqwPE+5vv7dyfx
                            q1cpqt+ryvO0rJ975E+4q/Jsqk+pedb3cq/wsz/P/DXJPrm/TX3N+9l/g3fdrOIja17xVE8W3fvd
                            fuonz1zV/ra3GyVl2bfubv8A2emakn2awSWeVd/+xXK6lra7dv3P9itNSTY1LXlj81VVnf7/AM/3
                            PuVy+qaxvXav975tn8NV/wC1VdmZvv8A3Nz/AN2se5ud9w/y7KrlMZVOQbc3klw252qu33aY9Mrp
                            PNlLmCpUd0qKigg1bDWJbFtu5tlXr/VI7632/wAa1z+6nbmX71Rym0an8weY0LNtajf/AOg037zU
                            5vlqzLmJrO+ls5NyV0Sa2tzborbt/wB9UT7n+5XK05G2bWqJRNqdSUGdg2qeTsZfuSrv+T+9/crq
                            /D3iT/R0b5nfbXm9xfrNaorJslX+LdVvRdWe3+X/AGflrmlTPUhXjKR7lpviTzoolb50X/0GtBNV
                            85X+Zdn9zb/DXmWia2vm+U332+TYrV0SakqW+7d975Pvfw1zSO0sarc/vdq7XT7+/ZXO3iedvVfu
                            VfeZZt7ff2/dqq8Pnb13fJ99aumZyOfv7Bbj5m+Tym2f71crfWLJLKyt/F/FXb3ieT8qtvf+Kud1
                            WH907Mv/AI7Vxkc1SPOclt+akq3c2zJ81VPvV3x948ipHkkNp6Uypk/1lAol+ztmdfvbK6i2s9ip
                            829P4v8AarH0tVeVFdV2fxf7XyV0tnG21PlX+/XOerT+EzbnTW+83yJu/wC+qyr6z2K21f8AdrrX
                            tmdk+Xem3/vmq9zZ/Misv8bUAcO9jtVm3VF9jZFVvvbq6q5sP3e1l2bqpXNmyRttX5P4f9mq5pGP
                            sYyMqzh/0r5vuVpPbLZwvubY7NVW2hV7jayts/iq+9tPcsvyqiL/AAVEi4x5CkiNf/d++v8AHV17
                            NYV3Lt/ubP8Abqa2h8lk3f3vm2fxVLMiv/FsTd81SWc1NJvqo/ytWjLtVvl/2vlqm+3561ic1aPu
                            lWineZTa2OAKKKKACiiigB79qmSXb2qHd/eoaguMuUv+cv8AB/DVj7Y2z/YrLDbVod2bbUezOyOJ
                            lE1Zb75f7qVUe8+aqlPfdu3NUxpxCVeUiX7S3/AKZ51Qf7tJVcpze0kW0vGqwlwz/dbZurNqWGTZ
                            Rym0a8vtFeiiirOMKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAHJ9+vpb
                            9gPw82t/tQeGdy/8eatdr/3x8v8A6HXzUn3lr7Q/4Jd6V/aH7QV3P5W/7LYN8y/w7nqKnwl0/iP2
                            Sh+S3iVv7tUrx/m2rVq5+RU2rWLqUzfJ/BWR1alG5vFe6dfuOtcl4mmtkW0ZfuMuzf8A3asa3qss
                            115a/I6/eeuH1LW7z7VEqxK9uzb2f+9WEjrjExHs5by6eW2i/wCJfFP+9mdqt62mlQ29vYxeX5TN
                            va4roNNuZZtGvVWBYYpd0sr/AO1XCa3pUsNq9zA3nfM3lJtpG0feCz02Ka93Wcq7JZW2v/B8tbFs
                            87ypB/rtvz7ErH0e2+2XkW1Wht2f5ndtn8Hz11Caa1ndWjLKrptV1RP4V/26C5F6GGDzXVold1XY
                            r/x7q07aGVLyK++Z/wCD7vyLVrVbmx0e33W3yXG3eyf3qlttKW20mK5gbfcNFvlSZvk/3ErU5jTd
                            HS63NFIlvt+X5vkrQtnV7XdtV3/iSasnw9earrd15d1F51uq/wB35FrobbTWTUYpV+dIl2t8tWYy
                            HaV5Vyrtu/e/+OJWtbW2zYrN8n99KZZwrNcIqquzbuZXrQvLd3i+Vfur8qJVmWplPbfvkngbyYlb
                            eybfvUJD5OpIzSs8v3/8pTrP7TDap9pi2XEu7ciNVt4VeK0+ZkuGZU3/AMH/AOzQGoy8vFh0u7W5
                            byfNberp/D/B/wCyVx9zqC3NvEsH+qWCLzftH+qVVf7/APn+/Xa395bJo1wzRtNEkTI2z/a+Xf8A
                            +zVxFzcWz2ssDNHC7T/Z9n30+4j7/wDdoKiZ/i3UlTVNMs2/1V/usoHt/wDVM3yP8/8A3xt/3a8/
                            +Itmz2b/AGOeOHVYrq3iRLRd/lXESPLK/wDdZkRNv/A67XxbZy6b4m0+8a2X+zLqVr37XMr7ImW1
                            dd6f3V2J/wCP1x/xFtp9H+0QLA1ho9/Kv2WZP+WUsvyXFwn95Uid2qDaJ4F4h1i21jSbTTLGBdEf
                            Xm+0Wc18qP8AYv3qS7P7rb5UTcifdrx/Vby+sLLWtVnWWw1C1sbDT7XW9QlTyYLyD5Lp0Rf9auza
                            qp97++ldVqutyv4L1PVbqC2TR/D+p/YtJmmVktLq3a4RN7/7Tpvb5PlSuN8T6lL4e16XTLa+jvIr
                            OV72LUHi3/ar9ki/1SfdZpUf/Z2/PUGx5V8V7qC68JafZwRXL28Wo39x5SQf8tZ33I8rMm75djfL
                            s+7XnOsJBJZQ6lbOqWu3fLL9xkuvv/c/upv+X/fr1l9en0nxYmq3lrLqssWp/wBv6hYvK7pcK0ss
                            Hlbf4f4ldn/2Frze80lfE3hTxHr0Uem6RFpMtmk+nQyeVLeNP5q74l/u/ulbYnyfOlWYyPPNV89t
                            j3itNcXDea0zt/rf+BVj3Kr5rbd23/brZ+zz6krrBBJM9rFvb5lfav3d3/fTLTdKmjm/0S5lZLWV
                            lVptu/yv+A1rE4KnvSKCeRNb7Z2aF1+62371Vribzn+X5E/hSmv97b9//aSoasgXad3y16R8K9Nn
                            vNat7aOTyZWuYk3bv99v4vl/g2/8DrzyGPe3y19B/s06bY6r8Q9Ja6ike3uLyKKW3hgd3RVdGd1R
                            f4f4W/36xqSOmhH7R+l/wc8K6h4b8C6PorRK8rQK7PD/AA/xyvv/ANyvULPdqst9K37mJImRZt3y
                            Sqrp9yudsHvLazsltomdLzdcQW9vvd1i+4iP/wB911Gmx6VDE+lTy/YHs/na3dn+7XNE7JDLm/8A
                            syywP8kS7XgmRf8AWt/fqlc6Ut//AKTukhllXeyJ/C33K0rl2tri0sbFVe0lX78331ZaLm/W2ll+
                            zK32hmVJXf8AhraJHMcVbeHl0TZ9pZkt/K82BE/i/v1XvLCz0SKKe52om1lV3/hb+/XYPpSur3l5
                            eedFuV/Oh+RFi2bP/Q6rv4bgvLiLcvnW6xf8tvubv9ijlL5jlNSvLl1SeKxZ0WLeu9fkp82m21/q
                            1klsrQ2Uq/v66B5lvL+WJZVe0ZlRf7i/P9yq+q3OmaPcfNP891/o6w/71MDM1KztlsLeC2i8lGZ3
                            rz/xDcq9xcf2fBveJfs7On8Lf362PE9zqegqnkbntIvvzTfI/wDuLXG21z9mtbie23JFdTtKyP8A
                            /EUFxOZ1KFYb/wAppf8Aj1iXb82xP9h//H3rF17xJc3mk7rxVSJWliVE+R1ZU+TY9aut3LPb3F4s
                            ey6/1Wz5E2r/APtv8tcVqtz5NjLpm7zvl37/AONdn3/++6jUox/ENzLCunxKrOjNv/v/AO3WC+qz
                            6PFcXjN88q7GT+BVZ/n/AOBVAniTfbxSv88sTfL/AB/7j/5/uVzmsXjTW7szb/N/g3fxfxv/AL1G
                            pIarc/uri53bImrMudVaa3maKL/VRfL81VZrzztITz2WaXc3ybvk/wBisG81aK2vLiBZfklX5f8A
                            aajUDPudS/deUrb3lb5tjfJXOak/2XVnXer/AN56fJefZrh2/j/hrn9YvGhj3Ky7m2/I1Gocxd1X
                            Vt++L5pv73zVy+pXO5lZfuf+hU+4vlhZlX522/frKmm3LtrWMTmqVPdFeX+7UP8AFR/DSVscEpcw
                            u7+7SbmptFBAUUUUAFO3NTaKACiiigAooooAfu+anLJ5L/LUVP8A96gDSs9Va2b5fv101j4k86La
                            zf7f3vu1w7MTT47hk+7WMqcZHfSxMo/EelR6xv2bvk/4F96rVtebNrL9yvPbbVW3Ju+5W7pWqpNc
                            Rbm2Jt+b5q5pRlE7414zN24feiN999tYty6zM8Uv3Nu+tiaZZlf5mRP4f9qsd9iSbvl/i+SkXyyM
                            fVFVvl2r/s7KxGXy2+ati5mWZf4U/u7Vqlcw/wAVdUZHm1o8xU2fNT0X/Zpmxt1XobNtqbfvNWkp
                            HNTjzSNfRLbZ8zfxfd/2q66ws9iozfJ/ern9KhdNjfwV2Fh95Fb/AGtmz/crm1PSiOS22L+9XYjf
                            7NV7m2V2/wBaz/761vJbedFu2/3d2/79E1h8vy7nrORtynHzWDfJ97/gFUbyw+X5l+7/AAV3D6b9
                            /duR933dtZV/pTJvZl31epj8JyltYLDK3y/w1NIi7UX5t6/x1a8lvNRW+RKekOzfuanqBmeTL5u1
                            V+T+/TXRkX5m/i+5Wr9mZ2RlTftqvcw7F+b/AH6NQOfezVt7P8n/AKHWPeIv8P3K3bmaWFnVW2bf
                            nV3+/WLcw/7LVVMxqR90pSbf4aZVvyflqv8AdbbXScEo8oyilakoICiiigAooooAKd5lNooAemN3
                            zUjptpNtL81AC/7tMoooAerU6o91SVLLiRUUUVRAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUU
                            AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA
                            UUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABR
                            RRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFF
                            FABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUU
                            AFFFFABRRRQAUUUUAPb7xr9Av+CR+led8RvFd9837q1ii/8AQ6/P3+9X6X/8Ef8ATW3+Nb5l+81v
                            F/6HUyLj8R+l149c5qTqjP8AxvXQaq+xf7j1wmt6wqM+759v3qykdkYnL63eS211cNO0ez+FK4q/
                            1JnliWeWTYq7GRPkSuo8cvFcyxSrJ97azf8AAq4y/tm1K6fyF8mH5vv/AN2uY74nR3L3MzRRW1zB
                            DbxReauxfvViaJqVnJf3djct/okUTO0z/f3NWfbaksOlvub/AFS7ERPm+Wq+j7rbS72dov8Aj6+6
                            jf3f79BfKdgmm2L6XEsU6zRbmfzt38P8FW9BudMsNLuF3NeXsu7aiL861w9zrcD6lFFBtRIl+5/e
                            3fJV3TXlTVpZWlVIfubE++38GygJRO2ud15psVzc3nnRbl/cp/dq7putz3mrRaZp9msPmrva4f5v
                            K/ufJXL61frc2f2ba0Oxf3UKV3vgPyH3tt33arsbeuzb8lOBjL3TbsLO80pXWC8/dfL8m373yVsJ
                            ueztFXd5rNvas+GFYbpIm8yZ2/v/AHK2/wB7cxf3EWuk45BbefDcfLAs3yslMudSgdYlXdDK3/fC
                            1Y85potts2x93zOn8VROjXNq8CqqRRK259qUydREs1ubhFVY081WTfcNsdl/z/BS3N59msLu2tW8
                            l9q28G9dm3/bqvYTT6bZ27amyzP5rJv2/O39z/dq1fv5zW8qrG8UTeayfI7/AOxQGo13jS13bZHi
                            aD76L87V59pPiGLXpUW+0qSwiZntZ7RW37WeL++nzO3ybmd67bUr+XypWgWd7iKVUaG0+fbt/j3/
                            AO5Xm+g22oPcW955FyiX+p3F1O8zbHiXe7oj/wB1vubaCoh4Y0fWrOe9g1OWNLJXVIoZZXlia3+f
                            fK+7/v1s/wBivNPij4nubOKylgsZIbTUrVrW1sb5nl8qVt++4iT/AGETza9As/FVtpWvWmma1rVl
                            qVvLFEjQ/cu4murqVE3p/Ev+qX/vv+5XD6r4b1VNBt7m5VbOKwaK3sX+R5ViW4/0jY/8W+L5Kg2i
                            fKvjDw9J4P8AD+u2On2a6x4KvLOK9XyW+2xWtqqJFLcb/vbkaXcv8Xyf3a4rUrWfR/DNq15rlon/
                            AAkviG/sr+a4gW4SKKCJJbeWKVvm/jdd/wB75K7L/hGW8PLok+lWyzWktjdXF5aahK6Wk6732RXH
                            +19n3sqf3k/2K8N8cXH2zS9bl0+xnm0ywvFtWvr5EiS1tZXeWKJ/+m/711Zf9ioNpGFY+NvEvhu2
                            1CXQZ20zdEmi3KXCrK8tu26V2lR1f5mZ9zPt2/On8Vef6vcBGtYFvJL9YFVJJZoF+Rvm+X5vmZP7
                            u7b96tu51LUNJhtNbWfym1azltftDN8/7pkRvl/h+VV27v71YWsXy67rH2iBpJJb6XdcLM+52l3f
                            M+77rbt3/j9aHLIz7FZVs7jUIYpPOs5Ym+0Lt8pPvfe/3mrOkkgmukZY9js3zbduxm3f3P7tWJoZ
                            7GG6t5V2N5u10dv7u9vmWqVjqD2F5bzxbd9uyyp/d3K26tDkkVLiFoZniZdjq33WouXWabeqrCjf
                            wL/DRdTSXk8s7/O8jMzNUNWYm9c6DPpVzFHeMu7arbYZV37WTctfVX7D2gtqHxE0y5tlge6itbjy
                            t6vsWVtibP8AgabK+VbVGa1ErbvNf91uZfkVdqfPur9EP+CengmDUvBqahLFJ5t/dXFl5zr86+VE
                            kqIn+y7v/wCgVzVD0qEY8vMfaWiaJcpY2i315JbXFrZ7Fht5diRf30qwmlWMLP8AZrGea9b70zs7
                            7v8AfrYTytK0m3trlpHl81Yvn+/u+/Ur2bWG/wCzbUuJV3tM/wDE1Vyl8xy+palbW2rW6rBLC7QN
                            877/APgb7Kih0H7ZcLeW15PDb7We6mm+eXa3/oNbfh7TYtY3z3MqzSyr5X+xEq1u3Ol21nv8/wDi
                            X+D+Jf7lIiUjH8PabBptnFpltL8kTM6zO2//AG6qeIU8neqssPm7fufIjVevIZbVX2xfd2pEn96q
                            WpeHrvWLeKzb/Q7iVdiujb/KWrJOUvPDy2GjOttOruzb1t0X59/9+q+q2EV/o26+gVLu1X5Xf76t
                            /wCzVq3lt/wj0TqzLNtVklmf77MtcvbXkupWEV41ys26VUn2L/t/cqDU5rxxftfwW8UErJbxf6/Y
                            n3l+5srym48T3lm+mK3/AB7xL+9f7jt/sJ/v/wAdegfELW/+Eev9Qa2Vbmyl+Zv49rf7/wDDXkHj
                            Z1vNDtL6KXYkS75dn8NBvH4TJ8c+MJ7+Xz1i8n7Z87bPuKv30/4FsSuP1W8lS1inWeNIpVZGeFvn
                            /wCB7au3mpLpX2i2Zd7yxM7TfxquxPuVwt5ftZ2cSqzTPLKzqn+zsqNREOpa3bWbIsHyeUv8a7Pl
                            /v1i69ftYakkEu1Nyt8j/Nubfv8Av1a8Q2azea0C75W27l/u/wBxK5LUr/7YvzfPLt370/i2/JRq
                            QVLnW97fZl+T5t/+3Wfr00W1LmBt7xLs31VvrxfsabvklXd89YNzqTOrr9x2ajUAubz96jN9z5n+
                            eufv7nzriVt33vu1NNcq1xKrfPtZtv8A3zWV521WVV+Zv4q1jHmOapU90ruzP1bdSfdpWWmVscAU
                            UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAD925qlSZoW+VmqvTo6AOhs9eb5FZvk/9Bp3
                            2/7S3+9u+TdXO/d+6aesrVjKmd8cTI0nm+b7uz5v96mO7P8AKzb/AJt1VEm2Nuapra53t81HKHtI
                            zJVhVW+b5/m/4HWnbQyzSpKrL8/3v9mqSOkjIv8As/M1atm6xqir/d31JtCPKasKbFTav8XzV0ei
                            JvlTc2//AGHrBto/OZNrfP8A3K6PSrbYvzLWEjpj7p0tsn2mLa259rVsJbL5W7bs/u1S0pPm+X7j
                            fwVtptht/nb7y7P+BUhGPeLv+VV/9nesy8s/ll+995v/AECugSHez7tuz5qqXltv3r/B/vU+YDgr
                            y2+zM+2s/wCzf3lb71dnqWmrD/Dv/wByuf8AszSSbVWtNSeULO1if5f7tZ+q22yX+LZXQWFt5MT7
                            v7+yq+q2bfIy7UT+/RqB5/NZ7JdzLv2/P8/8VRX9nv37m+RV+WrupPsZIvvvu+WmQus2/cv3fu0a
                            kHOOmz5Wqm/yt/tVr38LbfN+X5m/4HWQf4q6KRx1iGiiirOMKKKKACiiigAooooAKKcibqXbtoAb
                            uo3U7y6d5dBfKEdM/ip+35t1FAcpFRRRQQFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFADv4q/VD/gj+6/8Ib4t+X5/wC0V/8ARSV+V9fqX/wSFmX/AIRXxQu75/t2/Z/wBKiR
                            cT9CPEL71f5tm1a8s1u/iSJ1Za9G8Tv+6fe2xK8X8XXkUNrLKzfP/DXHI9WlE5/xPqv2ZknVvOdP
                            uo7V55Z63qGvapcLczr5q/ulRP4v9uq+va9LNFtVd7y/efd/t/JXLvNc2OqW8qz+TcM2xkRtiRbn
                            /vf7lY8x3xid3rGpRaJL9jTdNuZdzov8VWvFGsNpWm2i2zec8qru/vtXG3N5Olw940uy0Zt6/wD7
                            f/fFWn1j7NFaXm5pvvJFDMvyNu/j/wCAfPVBynUTaxBbNZS+VH9oX52R6NK1uXWL95VXZE0uxdn+
                            f9uuHttVttSlSWeVUlbbKqP/ABbvufJXfeFbZrP9+zLvVfN2J8lAfAelaVptyl5brFbLNKzbN7r9
                            2u70GzlsN6zsvzfxp/FXGeGNbZ7h5WbY6xbPJT+LdXpGlbUtUZbZX3Lvb+N1reJwVTTe22RIits2
                            /wAf92rEKecsSq0aO27c7t96q800G1Z2+/u2KtSvtkillZWSWL50Rf8Ax+tznLdn5u59u2F//HGp
                            n2N5rV9reS+77/8Ae3fwVBvlvLXym+R5WTyt/wB/d89MZJUliWKJd6y/NNQRqWLi8ih81mZn2r/B
                            /D/+3VR41SWWJljs/NiVFS4+5u/g3/7VSvte/itmgkheVW3Pcfc+X7nyfw76NSma/urjT7mzWaJf
                            3stw/wA6L/fR/wC9QGpyWtzT6JpdxqEEDPaRWv2qX+z5dlxdbfk2ff2tvWuP0TVdPs7zw+tzFcw3
                            es3S2s8UzJL9jl2PcJ5qfd3Ir/8AfNaGsWcWpeFZZ9PvJIYvN/cTfOiWu3fv2I33l+R/++6sIljr
                            1wlnB5EOsaTZrercXa74vNaJ03v/ALTxO7f8DqDX4Tl/H2vaR4kupp7O5tLy9+xxeVdxRKj/ALi9
                            +R93975rjb/v15r8SvGEtjpbahpVouqXfhK2uLqKxVnSVrVrd0dNq/8ALV977d6fwVv/ABmv5PB/
                            g23Wx1NtHTxBp0VpapDFEzqqypFLLs/2Le4eXb/uV5heTXNn48t9ZsYYI7jWdQsLW8V5X36957bb
                            f7P/AHVt4kdp1/u76DaPwngPjzR9M03/AITjSvtMyafFY2dvo8z3kv2GKXfEn2p/n3N+6eXbv3K+
                            yuTuYdM1tdd0zV/tVrrTRSy2Pha7l3+fdSv5trKzRff2W8q7t/8AEjtV3WL6fxJqXj/V7ZbN7jRv
                            9AuYtrfZLp/NeBJYom+Zp0eVPKiX5fkWsdo5dBXw5c/bGsNS02KCW2167j3PLdTp/wA8vnadUTyk
                            T+Ff9n56jUJHknjS3nmvGtZJPt93Zr9iimt/lilaKV03on3WV1X5dn9ysqGS2vLNrHyGu9Yn8r7N
                            cW0n3W3Ozq3/AH2n+75Vavi6Sfw/qVoIWniu9J27obiXe8UrbGf5v727czf3Waud1aGKSHT20qe5
                            muGi826fytjrcfPvVdv3lVV3b/8Aaatjml7phX1vJbzvbSD99E7RN838W6qsybNvy/w0so2sjLJv
                            3Lubav3ahqjm+MKKKmtoVdkVv71Mg6Dw/pss11+/XNpF80ru2xF/u7/++fu1+wX7LvhjT/Bnwl8G
                            aZpi+T5tit6zuvz+a295Xf8A4B9n/wDHK/KX4caDP4w8WeH/AA9Zysl7f31rbt83yNvl/v8A8Oz5
                            f+BO1ftfovga5s4rKS8l857OdUWFFRE+zr8j70X+NHRKwqfEelT92J02m2ct/cWn25m3rudfl/hX
                            +/Ttl5rFwm59kTRNu2/+OVt3KM9hb/xyyq0WxP4VqVIfsFq8ECLDui3yv/dqzHmOfSGDdbrFE0Ms
                            TNu8ldm6tO/fdFEtt877fvv/AA1bmjuUt/ldYZW/8dWqOqo1vOyrK0NusW7fu+81MkwvENhqcPia
                            01BbyRNPtYGRrT/nrK38f/AP/Z6u3OsT/upfKVHt181kT+Gn273mq27zy7fsiy7F3/fbbUWq3Nno
                            9vLc/fvbption+5QWcTqt/beIYrezaD7NcX8rPs/jVVT+/XBXlzbWGm3EE862brOyLs+43+3Wh4/
                            0TULnwrLFY3jWeoSxN/pG354l++7/wDjlcFc6O1z4Z0+znlkvHig2Nd/7X8bt/v1B0GP4u1uzttN
                            8hVaZL9mlb/vjZ/7JXjnj+5g0qCXT7aXzrKXZ8/+19/5/wDaT/2et3xJqs6RRQMzJbxRNF/cdmZ9
                            iO//AAPfXk/iq8bT/KVn+SVt+92+7u+eoL+Et3+vQQ+Gbj5fO1CVfK85/wC7v2Pt/wCAIlcYmttp
                            trFefLNLEzRMn8f3KxbzxDc/cX5EX7uz/lkv9z/gdY/9qtbXW1ZVdGVvkT7n/AP9qrINq/1jyYpZ
                            52b/AEj96qJ/erjbq5861+0tKv71m+T/ANAp1/efbJ0bd+9Zf9T/ALNYtz87SxM2yJf4aCBl/M7t
                            /FsZd7VzmpOqRPtb5/uf7e2rF5qUv2iXc33U2KlZElwrK7NuWVv46CKnwlFpm+f/AGqip1I1dB5o
                            slNoooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAF3UvzU2igCxDNsro
                            NNmV1+Zf/sa5pv4au2Fz5MqbvuVEonTTqcvunoGm7X+b79dVpVt9xtvybq4fSrlof9ta7PSrnzl/
                            2HrjkelGR1Gnwr/BW2ib1+Z2d0+T5KydKhVG+Vf96ugtof73z0jUbDYfL8tMurf5d38dauxUX5ai
                            udm35m+7QBy9/bedFt2/e+9WI9hsZ2Vfu111/CqRfKv3qxLhPm2t8+2tCTMtrZYbjbt+9Wbr0ypD
                            tX+98tbTo27+HYv3XeuX1t97f33+5TCRxtwjXN1v++n3KsXP7lfl+4606a2+b5v4mqu/3du2jUxM
                            C5dnZv7v8NUXt3/irbvE+VNq7P8AbpiWe/8Au7P4vlojLlIlHnMJ0qLcfSuij0pdz7lbYtRPom5v
                            l+T/AH615jmlQMT5no8lq6VNHVG27fnX/Zqy+lL/ABKv+zvWj2hccMcp5LPT/s+1a3YdKi/vb/8A
                            crSttHVF+7/wOo9oXHDROSezpn2bZXXSaaqbGVf9ihNHiRtrKvzVHtS/YROaWxbbnbv+WnfY/v11
                            b2cUP8NZlzbff3f8Bqfam3sImF5K7ahfbWtNbbF+Vm/2f9qs24/3dnzV0RlzHNUjyFaiiirOD7RF
                            RRRVkBRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFF
                            ABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUA
                            FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA9fvV+lv8AwSOutln4
                            ti83Z/pUXyf8Ar80l+9X37/wSm1JofGHiizSXZuiil2bqiRcfiP0z8VXLbfl+f5a8J8WX8sMV2q7
                            d6rs+eva/E9yqxuzNXzv8RbzzpZfI+5t2N/DurgqHt0DyHUtbaaKWJm+f+/9z+Ouam1trlvKWXfE
                            sv8AH/F/f31U8Q6wqalKu7Z/B/sLXLveLbK39/7+6uT7R6XKejW2tq9ukSs2zfsbf8+7/Yo1bWJb
                            bRnubltnzbFRG3/d+RPk/wBx64HSte86Xyl/hb5d/wB/dWtqt55Nv97zv49/39rf7FWRymloPiT7
                            fqVv9pVd8TfK7/fWJfubK+hvCVh/aUVuzNvlZt/z18iaJc+Zribp496sjqn8bfPX2H4Pdry1i2qu
                            9l+V0atYmNT4T1XwxZrZxW7NbK8sv8aLXof2OXzU+zMqRbfm3fwtXI+EnleKKBl/equxflru7OSX
                            97F5Wzyv/Hmau6B5tUZpu2ZXZdvlRfI2+rFzNstZfsy7JfkRf9pWpuz7HZvFBtR2+98tV3mvrzSI
                            ma2+wXESsjQ7v71Uc+pYttNlhnt/PlZ/KbYqSr/FspyPK8SbW+2PEzbn/vMv/stPvJvJtUl3Lcus
                            Svt3fOv3/wD4iorm5ttNaJWtpf3qt5rwt93dQGpUsNbvLm+t4mtoL/yl/fzJ8/3vm2J/s1maxpqf
                            bLSdWawis55ZWd/kRZWTYjv/AHvkfdW3eWy/Y7jSraXyfNi+z74fvxbv9v8A2ErnPGdndvFFpk8s
                            P9jtFcXF0jt5svyv+62baA1OFv7yC5vJfDmtQTw6Jf8A2yL7O/z/ALpfk81n/hV/vf7r0ar44gtt
                            G0K+ttIXW9Ma8l0+e4hl2futjukr/wDTLYm3fW1qVyvie1e8nbfEt19nlhT+LdF5r793/LLY/wD4
                            5XmWq3moWd/p9tY30kOj36xebYzL8jWbI73ESbfuskWzb/s1Bsef/GN9PT4tfD+zXT47/T9ZvPtq
                            7Jdj2e2JERIt3y7ZUfayf7leSR2Fz4b8DRX2vX134nuP+Epit77Xt3lJYW88v2dPs6fwt99fk+78
                            9dj4w8SX0Om6l4gWxhm0LRvt+q6T9obf5G63it7eJNv3YoorV2Z3f70qV5v450P7HpuseEdK+23+
                            k2ttYXqSzTtvlv7x0lit3/65Pu+58y/JQanP/FCxj1ZbtrWeOHwPYeMLi30V7a2S3e/+zfJ8r7/m
                            ZPn+b/b3V5r4w1K7s/E1rb6zBvult7XXdM0+1VHis1ukR4nlf+DbE0W5Pu7ndq7f4i3+nab438KW
                            1tbSzeD4tAbV59DdklTRrq63pe7E/wBh03bH+bd8v8Veca3qUHgxtSgvzJeeIref+w764hukuLeW
                            1VV/epL/ABNtSJV/vbP9mgPsnnPjyS6kur1p7aRLiK5livrjZ8jXTSuz/N/H/s/7NclY6pPpW5lV
                            UlZXTzv4l3Jtb/x1q7Pxrq91HFqGh2upNqeitqD6h8ibfNlZFVZfm+b5kfbXnNy6vK+z7m75aqJx
                            1JELvv8Au0R0z/vmn1oc0Qp6N5cu7+61Mq9pNi1/fwWy7tssmxttIPtH1x+xD8Nf+Ez+N2jyLHD9
                            osIJdXXc/wDqv3SeU7/7Kbm2/wC9/sV+sXhWGe202KVlZHWLfKkzbv3v3HT/ANAr4N/YG8Gtc6X4
                            y8RtA0N7danb2USO2zda2qbJUT/gb/c/2K+/9BvIn0tlVWeWVm2/7rJ8/wD7JU/aO5/CW3s1vorS
                            VvMSXb9o+T5E+X7lWNVdUt90C/6Q23a9aEL71iVV37V2S/7PyUbIrmXbA294m2bP7tBlqYls8d5K
                            9yzM6KuzY/8AFRbWHnf6TPtS3ZmSL5vvVoJYfY7V9214trbnSqsj/aYrT7SuxVb5U+5tWqHqYlnN
                            +6u5YmbZ5vlRJu+9/feorPTYt1w1z++eL7qP/erVv9EW5t02s0MMU7S/I38NZVzDFqUV7tlaFNyu
                            z/7NSGp5Z4h1v7Zq8qsv2O3271d/ubd/368k1LxpeXN09nbQKlvFOyNNN8ny/cr2bxzDAktvEqq6
                            XW1In/3a+afHOqz6Pa3cFjAz3dxP8qJ8nyr8776g64HmviHXmvJdYtp1bymnaX/bX+NPn/h+fZXk
                            PiKa+vLWVp28592xU/2a7vxD4igsLdPszb7jb/pT/fTcv33f/P3krzLx5rfkypFYrsSWLfL/ABuz
                            f3/9mgJGS+sN4duJYLzbeRS7vK3/AO0n3/8Axyua1K8V9Sdl3Ju+f+4m2pby5+W3lZm+0Krebv8A
                            n3Vj72mlldtv9/elBAPft5SRKzb93/s9V7yb/SH3fJ8vzfNT7mZblv8Anjt+7WPqVzI8u5WbY+3/
                            AIHQBSuZt6vIqfIzffas1/8AXVqarqXnRRQRLsiVfuVQkTcjN8v3v+B1rGJwVJfZKlFFFWYhRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRTtrUAdRoNwzqn3
                            n+bZ96u+0RN+z5f4lrzrw23yv8vz7q9H0FPOZG/2q45fEerS96J3GlfdRVrqLP8A1SLtV/7z1ztg
                            n91Gfb/s10Gnu+75qzOzmLrp5a7v4t/yulZ95uf+98yr/wCh1oPcrt2/3ar3Mm9XX5d9BfKUrlPl
                            /v8Ay1iXKKjfNWrc3OxX/wBn5Kwrm5+bc3/fdAGVfzMjPt+5/t1z9ynnS7d296u6lc79+3d/tVS3
                            7pUZfk204/EYGZc2sSfK336yntvM+Vv73366K5tlm+Zm2bqyprdURNq/P/DWmpl7xn/Zl3JuX/e+
                            WpUs/l+Ztj/w1eS23796/PUrwtMqfLsSguMSpbQqi7W/hq2lhvVvlq3bWG1vl+f5a0Laz3y/Kuz/
                            AIBWcpG0Ymemjq67mbZ8tMudJVF/2P8AbWurtbNki2sv/jtV7mzidf8Ab2/LUe0L5Tj5odm9VVXS
                            of4dv3K2LmH5X+78tUntv9mkXykSQt8+5v8AvuoXdf4V+7/s1eS2bam6q7229fm21IcpUf51/if/
                            AH6pOm9f93+OtB0/hX+L7tM8n90/y7PloD4DCuId8T/xvWPcLj725a6q5RUifb8/+5XNX+1G+7W9
                            I4q/wlKSmUN/s0V1nlyIqKKKsxCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigCWOvr7/gm14jXQ/jZcWruyfbLXb/3y1fIL/x7q9z/AGP9e/sH47aFPu/1rNF/d+9UVPhNqPxH
                            7QeLZlm0v7/8P36+b/iLcr+9bd5P3q941LUlufD6yt/Eq186fEh1/wBIRm3pu+VP71ebVPeoRPnf
                            xheRJePtbe6/+hVyUOqzvdOzfxfJ/wABrV8YTL9veRtqbf7n39tcY+qrDceeu5/4NjfJt/265zsl
                            I27bUpba/i3N87b92+ul1XWIH02Lay71+evPdSv22xXK/J82z7lbWm6lFfab977n3k21RjzFix1j
                            ZqlpctEqbpV+/wD7/wB+vvD4dQ/adNstv7522/In8NfnUl+tndW7Ku91nXZC7b93zpX6V/BlPOsL
                            Jl8tH2/N8vyVtHcxqfAey+HrOV5UZYvJ8r5Nv96ujR1jk2t9/d/wCqmmottaoq7n/wDZfnq9NZz3
                            nm/KsLt/qneu/lPKkOSGdLh5Wgj2Rfd3t96i5mlms5ZV+/Ku/e/31piX7XMUU7MqeV/r0Rf9iqT6
                            3Z3LanFA3k3Eu1FhmX+H+5TJ1LCJJrFhd7lZJdvmqifc/uVSmufJZLZZY7O93b2Tbv3fwO9WLZ4k
                            0t2bdZyxP9n8l/k3f3H/AN359tcu+sNC17p62f8AxM9q29nM++VJZWR3dN/8KpsSgNTpXSzmvIrZ
                            YJ0luNqMnlOiKvz733/3nrh/Ek2n6D4wtG1CLyX1SeKyVHl+SWXyvuf98fNXRapr0mo6klin2uDU
                            4olVWSBvJZ1T513/AMPy1xusa3p6a9FpFzPp9/4rigbVdHsUl2XDKqbHli3fx7PloKieb+M9S8Wa
                            b4f1O2i1fTf7bilXV1fU22W8tvFsSVE2/wC4nz/7aVj39zFpuqarqen6nA+n+I9fW4imdne00RZd
                            PSKVERv78r7tife3p8ny13GvJodn/pN1Yx39pb6T/Z95DcfIkVv5W+XzX+7uR7d2b/aevAvGGiWe
                            vazdxXN9d/8ACNavf2eoWdv8lraRXDW6RfPKvzLviiiaL/feoOmJg6lZypoet+HLHTNUsPA9xplx
                            pFnpNo3m3d1LaxI8T3DrvZFuLhP/ABxP79cBpsV9p/iXWdSi1ybUtKg8Utex29vb+VaNrPlbfs+9
                            97/JAzf7rIuxa9P8VWepp8RvD/2ZdQsLewil1fX4dP8ANt7ie3/5ZXDv92VUew2bE/264Bvsdn4q
                            8D21joaw+H9SvF1rWNQsd+yzvZ3e1t/Nib915qSsv8XzVAHCW+j33hjSNbbRYPt9wsVq9nfXy7/7
                            RnnuN+xP4drxI+/e+5vnryDxnqFp/wAIlouh2M7X9rF9qlaWGDY8srSukSs38a7ETaqfw/8AfNer
                            pc6rdeAfEen3k7X+t+H9Tlt4IZV/0e6vN7o8rv8AL5XlK7+UiV51p+seHvD3jRfEbaHqV/4VWKeL
                            QLSGfZcJPs2RbpdjbvK/+IqxVDxe4m8643tKzlvvf+zferOuNzfNs2J/DXT3No1/K0jbnupX3y75
                            V+ban71/m/iZt1ZN/DHJLL9mWRYvNbaj/f2bvk3f7XzVUThlGUjJ2baKvTWqwoFX5m/i/wBlv7tV
                            9zbdy1ZHKQ1e012huEli+9F89VlXzNirud69B+G/gb/hYnjbR/D9pL5KaleW9k1w/wAzxNK+z5f7
                            3+7UyCMeaR+tX7Hvwxl8A/Bnw1bavpn2DxAsEt7cuzeaipdO8vy/7ezZ/u19IaDpqtpLzrEvmytE
                            /wA7f99/8BrM8Kv9j0O30/b532Nf7P8AOT5/P2/ut7f98Vu22nzpdPE3l+av8EX3G20onTItokVm
                            ybYGhdvnbZ9zd/A9Fz5s119pVVh82X5v9rb/AB1M/m6ldSssu+3XajO/9/8A2KhTTWSVNzNN5q7G
                            Td92rJ1Itbv5dHtbfarOjN+9p9xJ51vE3lb3ii3q9M1VJ5vKVIv3X32R2/hWmXNs1nbxRefv8352
                            Z2+6tAalV386zlVYpH+XeyVymq2f9sS28Ft5kMrQM7b/AJEXbXR6rDLbbNt8uz77JXOa3qqvZywW
                            zb7uL55X/ursqQ1PNPH+pL9jf+zVWa7tdyM83935N/8A45vWvB/H+7dp95Ysr3CwNLLcOu9G3RP9
                            xf8Agdel+P8AVfsHhx76Bv8Aj8ZbdUT/AFrMz7P++a8k8Z2DXniqXTJZ9iWFmrzpaMmxYtnzp/vP
                            92oOuB8y+MPIe6WWzXZays3mo33/AL/3/wDeevPNbuW82WVtrpu2Kn92vQPEMy232fzV/dLuT+PY
                            u53SvJ/Ezz6bfy7tzpK37p//AIj+9QBUvJo7mV2Zfn+bbs/36qzebNLLuVk2r9/b8lOvIfsywzq3
                            zsvzVVvNS85X27k/vbG+9UamRmXjy3MXyr/49WYkzW3+838NWbmZVg+6rsy/M/8AFWTu+atYxM6k
                            uUWVdzfL92mbvlob5fu0ytjgCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiii
                            gAooooAKKKKACiiigAp38NNp1AHR+G4W2/c+993/AGq9V8MWHypuVneuH8H6az7F27K9g8MaU0y/
                            d31zVD1aHwmxZw7FTb/wLetXnTyfmb/xynfYWRk/g/8Aiqr3M3ksm5tnzNWB08pF52yX72//ANlp
                            95fq67t1Y9zebN+37/8Au1iXmqskW1f/AEKtC+Y07/Uok3ruVN1Ykl+s3zf7NUnvGml+b/gL0xZt
                            kW/+PdWYht/8kTtuX/vmsm22rL+9X+KtO4m3t/Cjsvy1Uhh+bc235n+//doIIpn3/dX738H92ofs
                            zzbFb7lXt6v8qvVi2ttyvtWgsqJCnz/L/wCO1btrNnlRlX+KrSWezYq1rWdts2bk2bay5jTlM9LN
                            oW+X50rV022V/wDvn+Crf2Bpv4V+7spyQ+SvzfPtqC4xIrm2XdtXdv8Avr/tVlXm512t/D/33W6/
                            m7X2r96sfUk8lvmX+HfQbHP3MP8AFt+Td9yokT918yrWg0yv8v8A4/VSZNm/b/v0F8pX2fcZV+7/
                            AAVXmRtr7tuz/Yp7zJbM/wArVX+2LMu1asyIbnbt/i3rtqr9+J/92rDvK2+oZkba6r9/+GgzkZ80
                            y75Vbd/t1z9+irL8vyVvXMMvlfN86bvuf7NZl5CsK/N/vVtH4jGpEwpEZKZVi67VXRa7Dx5R94io
                            ooqzmCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigB2/wCbdXq37OcLP8WN
                            CZfkdZ0df++68qX+L+7Xr/7Lqb/i/o67Wfc1RU+E3o/GfsBbTM/hK3ZvnT/7CvAvilcs/m7V+f8A
                            hSve0dk8JRRKvz7dn/jlfPnxFmdZbhU272/i/jrx6p9BRPmrxzcb5X3fI6/wf7deczX6pLKv8H/o
                            Neh+M4VvLiXauzb/AN9t/t15PqT7F2t8j/NuqIl1DYs7n7SksE7fI3zr/wCP03wxr32bUntm/wD2
                            q55NVZG3Kyu8X8G6q+qzeTdJfW33GZf4fu108pjzHcarts9SinZv9H3LL8n++lfp38AbmC88L6ZP
                            Bt+aJZW+X+9X5b/b4NY8P287fO6tX6i/swJ/xbfQpVXznaJXZE/3KukRU+E+iIUWFUlVfkX+CrH+
                            plee5be/39lZqXLXMSNP+5+Zf+A1LJDLD9rg3bPtC+UtxN9z7ldh5siLVZvm2wIqRSxM/wAn8W7/
                            AOwqjZw20Os2+oLGuy1Xyvn+5uZNnz/8DpmpeIF8J2tpdwQQPLEzRLDsZ/Nl+5sXb93YlUHS+vFu
                            Nm13VmdYfn2Stv37E/8AQv8AYpjOgmtvOv7iW+l87zVVIv7i/P8APXOaroOoeEv7M/4R7y5niunl
                            b7Q3m7d38H+8lbFnfwJpfn+Us1xbtslib5937r7+7/f+X/gFZ6X9jpV4mn6fu+z3kvm3lxcN+6bc
                            mz91/tb9lAFTxJeReG7jSrG+a5vLSW+iSC+3b3naXf8Aun/2dm+vMvG0OleCfiDqvxZWzub/AFWw
                            tWt9tj8+6zVN8UUSf3X/AItlejTQ3l54c/sW81Cd9VlX7FBq3kf69pUffLFF/CyI715Zol5O+uaV
                            otn4V/s3w/4f0fyrHU7u+82WW6i/dfZXT/cXczv/AOPUFRDx/wDDeDTW1vV9IX+1dVv9HuLVfDc1
                            19nsZ5bqWW4uHf8AvMnmv/wFErxp7NvEnhu00q5tob/R7/R/DkX2jzXllW62bEii3J9232u3m/e/
                            75r1LW7a5ht9TnttqaFpMVrbyvfT/vV2u8t3LLK3y7U81Yt6O38a1x/xdubnwiuu61p8Ul5FpNrZ
                            6hbWNivyK0tvLF5Vr/ebZKkuylI2icVp7af4N1Syg8T3stzqGo+Ib/RbiZE8prywiiaK3iV/us3y
                            ysvz/fl3f368i8X6pqFj4d+IWn6nLFremaRZxPZvabbe4XXLqVNkrL/Ft2bmX/ga13uq21tqviDw
                            f4ebxHH4tu7PXVuIre7i+y7bWXT4vtt6n8LbHidf4trb/wCKua0+ad/FWm31jP5K7dZ1/Vbe7VZY
                            pWV1SKKKVvvLt8pl/h/3dtZF8p5/r00/hzVNF8WeGbRbbQrVovtn25/n1aWd/ndovursbe3z/d+9
                            XiMc0um6ak9tPLbXcU6y2s3lbIlVk+Z/n/i+b+D71eneG7ywTxbo+kar5ulW+pXSxeIWm3Sy+VE6
                            PcPa/fVnl2Sr8n8WyvP7y/vH8H28+qz3cdxKqS6Ku+J4Xt1ldJXl+fcjqu1V+X7u/wDvVZHKef3F
                            st/f3sdpHst1Vpdsv39qL/eas+ZZZrhItmyVfk+9t+7WxeRq+pWtzqEi3VvKqvLslXzdjf3/APaq
                            rrFvBp901tFdR3ifK6zQszJt2bv4tvzLuqonNUkZMn/HmzN9/wA35v8Ax+qjO38NCP8Afo/36swL
                            Frc/Z1dl+8y7Vr6b/Yb8Mf2x+014PglWK5isN2q7WbZ+9SLfF/3w7p/s18v2sLXFwkIXlm21+hH/
                            AATL8A3N58UvGvjC5tlmtNL09oo4du59ssv31/i/5ZVEjSmfpkmlS2dvb2bTqm6JfnT77Ss7tvrV
                            +5E6Mu+4iibdMn/fdV9Jh2MitB/CqfJ/C3+/RYJFp91LAyyTJ99n/g+Z/wD0Kg0H20zQ7YLbbNul
                            3t/ci/jpl54ns7PxRcaQzeTdrAtxs/g+Z6La2lhWVtvk2+7Yr/8APVqmurOB7+KS5ijmlZVTzn/i
                            pkakN5cyw+bfXiq6S7UVE/hqDxPCr6TErM2/5UXZ/FUtzNbfvoG+f5vlR/ubayb+5nS/eVWWaHyv
                            lT/2egNSK/8Asdtb/bmVnuPKVNj/AMNeb+LdQitlu54NsMssqefM7fw10Gsa8syu1zEyI3zs6f79
                            fO+t/wDCWTeJvFd9rVnGnh+Xa9iiy/PtX+N/7v8ABS5jWMSL4i3LPpt61sv2l4mWKJIfn+86fPXj
                            mq3k/h7xpqd5Ozea0HlSvN9xdv3ET+9s/wBuu78Z+J222kWlTqnmr5s7oyO7Ns/g/wDQv9qvF/iX
                            4nlvNc1Oe2sWeyaJka4dd7/f2bN/+2/3nqTrPN/Gdzvt9q7fKZm+T7+3596V55458Q3OsaTo+nzx
                            Kn2CJIleFU/hTZvfb/frq9YuW/su3iZl+0RbpZXT59zM/wAn/jlcDeTMlxKrRedcbm2rQc5zt489
                            g0W5v4flqvcusLO25tjf+O1YuX+Z/tPyf3kquiRXjOitsi+/uqCJfylG5mjht5VVd+75N9ZHzKfS
                            te/ha2i2rWb8v8X3v4a6InHUK9FFFWYhRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQA6rNhC1xOqLVdGK10XhXTWvLxPl/iVamp7sTalHnkekeCdK87Y23
                            5K9t0HRPsdrub7tcv8OvDf8Aqv8Aa/vV7c/hvydLdv4/v1xcx7dOJ5jeTfM6/wDs1YV/cr95mX5V
                            rd15Fs2dmX56861vVd9xt2/J9yiPvBUC/wBS+V9v8W6sK8vPO+79yh5mmZ/u7G/gpz2azM+1t9aa
                            nNzESJ52/fTZn/hbd977lT/ZmhXd9+q9zDsZ2+V3X/b+SjU1G/wuytvf/eqF/nl2r/FT0/fb2WtD
                            7G0bf8B31kOPvEVnZs7P/c/v7q2raz+Xb9/5ai0+Hf8Aw/erbtrdkb5lb5fkpSNoxKiWDJ823/vi
                            tC2h+X5F3/Nsq7bWDeUiqvz/AH/nrQSw2b1X/vis5FxKVtDsZNrb0qK5TyZX3fPurVTb5SN8tZ9+
                            vnM7bvn+/UGhX3q8X+fmrH1jb87L/uNV25RtqN/AtZty/wB/dtoNTBufkaonmq3eTRbX2/e21ifa
                            d/8At7loIJb/AGuqMv8ADWa9tvl3fN/f+9Vh5vuM38PzrVe5m37NvyPu+5VmQ9/nX/b/ALlMd97I
                            u3/vuq7zL/e+f+//AB057nYyfxp/fraJnzEVy/kxbVXf8tc5f3Pnf7D7a1ry5VZfvfd3Vg3M29nZ
                            vv8A8NOPxGNT4TPmf5nqD7v8VS3L76ib7xrsPHl8QyiiiqMQooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAeG+Y17V+ye6p8ZNKZv71eKr975q9i/ZgkVPi5pW75NzrUVPhNqP
                            8Q/Yq5hX/hF4mX+7vr59+ItmyNKyqv8Atf32r6Y02H7V4Ph+XftWvn/4nWE8zXaqteVVPeonyP4z
                            dkv5V/vPXkniaFY2aVV2Iv8Ac+evaPH9mtndOqr8nzfP/tV5Frb+d5qt9zdsrGB01onD3kzQyrKn
                            z/7G2pft6zJ97901V9Vh8mX5vnSsf7S1m21fuN91K74xPNkd34Gv1ttS+zMvyStvX5a/YP8AZys2
                            sPAehWys0MS2e6vxk8K3ivqUTbm81tqRIn32benyV+2HwQh2eD9KtlZUSK1Xc/8AwCiMeWRcpe4e
                            luipaxK2103b13/3v7+yrFyk+2W+aJZtvyLC/wBzb/HVRbyze8is28x5Wi8351+TbVi2uIrm1uG0
                            /c+35PJT+Jf43rqOEpPbf29Fd209tJZpE29XT/Zf+CqmzydNu9MZp4X89tru3zrb7P8Ax1n+9Wnb
                            f8TjQ3nWVkilZfKd/wCL+Os6zhnSW9vp4l/0yX7LA7xfdiVP/QvvUEFCzsLPSv8AiStLc3n+hqkU
                            zt/Dv/g/3N9VNb1vRfD115V4uofbZWtbWK32+a7ebLsifZ/Cu/fu/wBytjW7ZZLC3nSKezu4mWKK
                            4hX/AFSt8zv/AOOJVTVdNX+0nuVudl75trLdXEMW+WWKJ98UW7+Fd/3v9+gsqPc/bLW0WDU47+Vl
                            a3gXz/KeWVX37P8AZ+dEX/drn1mi0HT/AJbFbm9v3lXUf3W1JZ5U2pKj/wAKo3/fFaCaVo154j1v
                            RtK+yQ67o14t7eXc3zvBf3UX3/8Ax9P+A1x8PjCLxJr1p4altF8Q/ZX+xedcL5SMvlebdXG9f4Ui
                            +T/aegqMTn7PwrofhvTdE0zxHrzalquqRWGn6xd28XyapdNsZ4tn8SPvRfkryu18H33h34T6r4c8
                            Q2yzXfiPU5Ypbi3vH+0WqxXssVvbxP8AwtFF/c2/L8teq+P9N2eJrTRbbVYNH1CVl1XTIWi2eVpc
                            Fqm9Ivk/1vmpu3/7dcjc39j4m/4TjXNT1C7v7LRvsfi+C02okVhE1un73/abd5rMn8LVBseIab4V
                            udN1aKO5gXSvBHgh7jQovEz/APH3qPn28q/Z4lb+Pzbpfm/ibZ/drjra/bwv4jutBubZr/xBpOmR
                            aBLp99En+h3E++3ieJNnzKkTfN/Dueus8TWsHhDwytpa69PqdjfePLDWr+aVvvRRWUt0lvAnzru2
                            /Mzp/dt/4q801jxFfQ+HfGGrrBDrepa5/wAT1tcu7N/OiT7Wjpcb2+b+6rf3V/goA5/SvA0fgS40
                            2PWtQnn1Cw1Fbu2XzUlSWwtfmltdrfcl3ruVf7qvXhsetXmpWdxo0TQOt/qCyu00ESP5v3E/e7Ny
                            r877l+Va9V8Z6housap4wTw5c/YNH+xu632rSr9oluPvOlui/wAVxLvVk+7trwrUJmslhs1XD7t8
                            v+9/c/4D/wChb6qJjUlyl3xZp39j+ILrTGkim+xytayzQtuRmRtjbW/u7kbb/s7a5+627flX/O5q
                            luFazkijZdksW1m/9CqjWhwSlzD9nl/3Xo/vUzZ8tG371Io19JsXumZ4kZ2Xbt2f32+Vf/Hq/U7/
                            AIJ66bBZ/DnxBqds373XLxft0210226/ciT/AIA9fnL8I/DsHifXrqxn27Gtn2vu/j/g/wDHv4q/
                            YX9lfSrGw+EvhTSrbStPsIrWCW6luIYv9a2/a+//AH3qJHbTjy0z3jTbpprBIl+e3bd9l/g3f3Kl
                            02NrC1e2Zle4uG81pf7u1KpQ3kU1rFH5Xk3G1duxfu7fkq3qU0VncJAzK6bf++fkoJGW1heQy3cv
                            ns6NtSJP95/nqXWLyCwtbi5aXYkUTbvOWs2bz4ZbRYNQ328s6u3/AEy/2KZczT6lfvF9mjmRG+bz
                            m+Tbvpkalh7Z4Yt0C+dcMuxv/ZK5ezhsbCK4nufPe9vG+zypN8+3/YStvVXtrfXPscUrQy/63en3
                            K5e/1WCzs3la8XerMi+d/wAtWoKicp4wuVv7yJftjWH8DJ9zcqV5Z8Tr+8TS7i5vrn91LF5S2iN/
                            D/frqPGd/P8Ab7v7TbM7sqpAjr/qv9t68f8AFsN4l/ZfbJdkXlNKs27f937m9/u/xvUHTGJyWvax
                            FDaxXlirQ28qskH3ERn/AI/n2fL9yvHfFVtKul+fc6hKllK37+3hXfEvz70T/e/ir0Lxzcz3+jSx
                            LPvt4t3lb9iIyt8ju/8As/P8leT+PNSltvAdpEtyr6fLK0s6Jt+VvuIn975EqCzz/VfEipryz+Qu
                            zb5UUL/crl7y/a81m7uVXY7Lv+T+FfubK3by5iudclnXbsaLyok+4i/7dZT2fk292rfPcMvyonzo
                            tWYnP3Nss0vmt8m751f+9/uVi3DSfMq/P82xX/2a6LW7ye/t7dWXY6rsVEXYi/7lYX/HtFtaX/gF
                            BjIynuJX+VmaoXVk+9/FU80ytJuVf97d/FVb71bROaQ1qSiiqMQooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAfgswVa9d+Gvh7zmRmX5vl/h/iryzTYfO
                            vIlr6V+FGiK/kt833d/+/WNSR34aPvHs3w38N72i2xbE+X+GvYPEOj/2bobtt+dV31X+F3h7esXy
                            12fj/SW/sOXb8ibf+AfcrmieifGnja5ZGl+9vX5K8nuHaa6dWZt+5/v13vxI1LfqUsS/521w8Nt9
                            /cv8X36Ik1Cum52T5Vf+7Vu2hbzX/wB37+6mQ22xU2/I6feqX7n8K7H/AI601OYW5dtqbtvzUz7T
                            50X3fk21LMm/Zt+4rf3aZDD5zJ8mz5aNS4le2tmdlata2h85v/i6LOz3L8u5HX71bVnpWzYrfx/x
                            1nI6A02zV4kZVXf/AA1sJbMjbtvybqmsNN+ZF2/droLawXb81RI0iV9KsFmbdt+89atzpS7X2rs3
                            Vp2em7F+Xc7r/wCPU66h2KitUG5xtzYbJdzLs2/d2fc3Vk3SbGdf467C8h3/ACbdm3599c1fwqjP
                            u3fLUAc5fu0Nvub5/mrn9Vud7bl2pWtqr7F+78lcy773fdt2UFFK/wB235azHufJZ/u1ev5k8r/g
                            Vc48zSS7l+5uoMeY03mXarfLvb+DdVG5vFRt38C/3GqlNf8A3/49v9+s+5vPlb5v93ZW8SKhoTXm
                            /wCVfnf/AGP4ar3F40K/e3p91d1Z6Tb1ZWlWmTXO9dvy1fKc3MTXM3zfe+f+KqVy/wC8/iqXzv3W
                            z/O6qkn3VreJFSXuleSov4qezUytzypBRRRQQFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABR
                            RRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFF
                            FABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUU
                            AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA
                            UUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABR
                            RRQAUUUUAFFFFAD1+Zq9d/ZpTd8WNJ/3v/Z68h8yvXP2b5vJ+Lmk7vkXf/7NUVPhN6Pxn7aeFUV/
                            DNuv8HlKleKfFqzltvN+9Xtngba/hy3b/Zrgfi1pXnWssqrv+WvNqfCe1Sl7x8NeP9NZPN3K3/xV
                            eGaqnl3Dq3yfwV9MfEW2V5bhVX5NrJXzv4ns1hldtv8AEz1xx+I76nwnD6l5Vyzq3/fdc5c22xni
                            Zvl/h+WumvI/3srVz9+iuu3+Cu+J5sg8J7rfxBZfNsRp4kZn+8nz1+5vwfttnhXT1+Z0VYnZ/wC7
                            8lfh74VhabxBYwTzrZxeer+c67/KRX3u9fuP8K9SZPB+j/Zrn7ZaSwL9/Zv27Eq/tES+E9IufIuV
                            eJYN92q/uv8AaqlbQz2epbVtm3xK3z7fu/J9yokuYLbzYtTn8mWLdLvh31atr/UEvIp2byYmXZF5
                            y/eX+/vrpOQmtnW20RIrZWf5mRURf4qdpXnzSxaZc208z27K/nfwbf4/96s90+06NLBbahJDKrbI
                            pofn3fxvT5NY1XS7BGs2tr/dZy3HnXEvlbNv3F/76+amRqVPFWq32pNL9jtlSWKK42+c33WX7m9K
                            5X7TKmjfa2l+x3ErRSy28Pzytb/7f91d9dAltcpa6ZrWuMsOoWdn9oa3hl3273TIiPK6L97/AL7r
                            kbzVbR9WSVdXn+2xQL56Jau737LFKyRJF8+3Y/z7E+b7lBUSxpWg2MMut/Y7aSHWNZs2vbqFGd/t
                            W1EiileX+FvkRdlZV5cxaVpNxqdrPaPFeRNK2oQqmywt2Tej7/7v3K5fVZvEGm6N4autV160h8Oe
                            H7O/1rX/AA3/AMvd4sUT7E83erb93zb/ALu6sfW9V8P/APCEeBfhXrNjczabrOhXl7qEOkweV5sU
                            SIiWW5k3JvV/97clLmNDK+N9/fPq3ijRfDSyp410vwzYarZ312yfLFvS3+T/AGZUiffWZryeHvD+
                            pRNr3kQ+DLCe4vdfuIW2brWWySK0i2f88vN+bY/+992s2w8P65r2h3Wqa14f0/w94q1G8Wy1VFup
                            XS10aCJJVluJd/ms+xNkVuj7fm+dG2NXCeKvFtt4q8B+O2lnksLLxNdWaf2clnFFcRWF1K8UTojf
                            MzeVb7t7/d3/AN35ayNYxOa+OULP4b8/zYX0/S9Hs4otMSXfd39xfXHlSyxf7PlRLtb/AGH2ba+f
                            /EHiCXQfhpbtp0t3pt3daO1g2ns2x1sGukWVLjd/z1dPl2fw16N4z1q11DVU1jUtXXRNE8S+VaW1
                            9aRt/odhYrt/0eX+JmlSLf8AJ/y1lVfutXz/AOP9A1LT/EWrnV76fWPLieVZZpWimZZfnV9jL/A3
                            3lX7taxFVOZv9VS4a0a50q0tltdPiRXhX/W7X3+a/wDeZ923fWPo6RpdNcz/ADxW6+a2z+9/An/f
                            VRWzm4tZoGZnm8pUi/3d6NULTOLO4tkZkt929/8Aab+GmedzcxSuWe4czt8zyszVDU7f6iJR/tVB
                            VhyhR/FRT0Xe3/AaRR6n8I5ILPTdb1KdtjRtEvyffaLfuliX/fX/ANBr9n/hDoNnY+CPDm1fs0uq
                            aZbywW/8CxLEm9H/ALvzq9fkB8EfCsGvR291PP5lvYXzefYzP5SXStF8iI/zfMzbP4P4q/Yr4Y2D
                            al4I0dlvrlJpbW3ZrR9ieUvlJ8n+7U/aOmPwnZtNbTah9pbzE/0W3+59zbUtt5Vxf/aZ/LvLeJfm
                            3/f3f/s0y8kWa6t7a2njmuGi2rvb90rf7f8As1L4e8HxaJ5UEs+/ykV/JRvkVd+9330CKGm/abbS
                            9Qtttskvny/ZZpv9r7n/AI5XM/8ACy4LD4iWXgy5sd8upaTLqq6sn8O35Nj/AN1q6i8h1W/1y7l8
                            +CZLX/SLWFIvuqybEd/9v79ee6D8NND8L6tqviO51PUNS1u8iZLp9QunldV/uKi/Krf7lAom7ear
                            ef2s7eVbTPFZs63EzfJK38GyuXvEb7PL9p+zTarFZrcXSO3yQL/fq3DcyvZu19osaPLErpDu3vEv
                            8H3q5zxPqVtD4X1C+WJpr3a0UsLtseXb/wAsnf8Au1BcDjPE95Lc2tw95fND5s8SS/3PK/3/APgd
                            eReLfE9jrfiC7VbyC8tLNmt1RN/yqqfc2f8Afdd34z8VNNo1pqMEkH2u6lWKVNvmxL99Puf7FeP3
                            l4tnbveLocG9p/s8F3Cv7qWX+5/wPfWcjsgcf4q8T2PifXNYuYPPh0ryFt1RF+SWX502f+Pp/wB8
                            V554h0q5sNDsrmezkhhv1Z4nuF2JLt++6J/d/wDQq7D4i6bc+G9Di+06hbWdxeN9oaxt4tn2Vmd3
                            R3+f+4leb634tvPFV/pWmXMs9zZWsXlLvX+79zf/ALP+xTMZHKPeK8lw0sXyRfd3/wB7+5WbpXiG
                            DTbfUImi3vKzOvy763dbtdthLfTxbLLe0Sy/32X5HeuK1SaX/R3a28lG+T7mz5f79WQV7+/Z7d5d
                            q/e+X5vuVzsiyTK0rfdrotVuVuVt4/K2Kq/MiLWbvW7a4gV/JVUXbv8A9mqiYyM53V1RflT/AGqi
                            uFSN9qtv/wBqn3HG1d2/bVcbl+aric0pDKKKKsxCiiigAooooAKKKKACiiigAooooAKKKKACiiig
                            AooooAKKKKACiiigAooooAKKKKACiiigDovCtt514zMvy/cr6++EWj71t/lb/fr5c+G9n510m5f4
                            q+zfhLZr+6RV+dVWuCp8R6uGj7p9MfDHStioqrWh8Y/9A8K3fy/Pt/3K2/hjp+y3+791aqfG/RGv
                            PDNwu35drVtH4S+b3j80vFW651m4Zv7zfxVnpDvX7v8A9jXR+MrD7HrMqr8iM3/fNc4jqn/7NSEg
                            SFfnZvv/AN/+9Q8O/wDvbP7lH2lXXav8LU/zvmo1IDZs/wBhNtFtbNNK7L/3xVpLbzl+b5/+A1ra
                            TZrtRv73y7KNS4le2s282JV+RGWuo02z85vm+TbTLfSludjKu/5a6vR9H+zbNsWzdt/i30am0SXT
                            dE2KjVqpoLbkZV2JWxYWDPsWL/crqLXRVdUZlrCRtE5dLPZFtZfu1n36fwbf9uu7utN/hXd92ua1
                            awaHf8v/AAOoL5jibzd/D/D/AH65LWH2Suq/7ldhquzc67vu/wDj1cFr2+Nn2/PtoGc5qqedv3Vz
                            Vz+53/366K8mdN6r/wABrmtVufmfc38P3/8AeoM5SMK/k+V/9qsS5mVPl+b5f7i1oXlz8rr/ALVc
                            5cTbZX3bdlXGJmRXk2/5l2om6q80i/d/75qJ5v8AO6q7S52f7NdkYnDUrcpYdv4V/iqLzvn3VDua
                            mfNV8pzSqlnzvlpkz/NUStRu+ajlIlLmGUUUVZiFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQA7zK9Q/Z4uvs3xY0Fm/il215l/drrvhReNZ/ELRJF+T9+tRU+E2p+7I
                            /dL4e3P2nwvbsv8AdWq/jOw+2Wbxf7NUvgy/2nwXaNu/hWt3Xnit4fmZU/364/snsR92R8f/ABX8
                            MeS0rKq/Lu/4FXy74z03ybp1ZNnzV96/EXR/tKyyqu/+Ovk/4heG9krbl3/3v/iK82XuyPS5uaJ8
                            46rD5e/+Cua1K22NuZfvP/BXofiTSlhaVfvov3q4TVId+/7yV2ROOoVNB/0nVre2+bZLKsTOjbH2
                            1+0fwEdZPh9olsvlw3H2PZ9o2/d/+z+5X4pW0zWF556rvlXdt+b7v9x6/Wr9lfxPLrHwj0y7WeS8
                            SKKLzfl/iV3R0/z/AHK2+0c32T6LfzfNSWe2b7buiiaa4+4y10CaxPrC/vYI/u/Z1V/uMu+ucttS
                            ivLB9Qa2kR7Vd8DzS703fx1oeHrlZm2ssl5LKrXHztsRf9z+8tdMTmkbH2zfdP8AZtqRRKqNCjfe
                            3pWFrcNnf3CM0Ec0TbrKV0Xeirs+dP8AP8dW79Nnmy237m7VYtqfxt8m37lVNkulXUVnbT7IrydY
                            p/OX7v3N/wDwJ6ZJk6L4w0rW9J1W5T+0rx9JdbV0t4tjtLvTeif5/gqDR9SlhupZfKW81BvK/wBL
                            dfKiVpX+eJH/ANhErd1u51PSvEEVisEc1lLLvV3bZs2/P/l/4mrP0/StP8GeBYmnVobSKC4vZZrh
                            v3sSsj73d6APN/HNg154g13VV1D5/EFquladb+V9ot5ZfKl+4n+fuVLc+M7PUrzULzVfLv8A+y/E
                            1n4Ygu9ypLEzeV88W3/prLtb/cqbxP4kl0GwtG820SZrWW9W7t4tiadF9lfZ8n8PyI7f7bbFrnPE
                            +vX2pa9qEVnLaX+p69pUqaFp6wJss1tYt8t0/wDdl8191QanHp4kvH+JF3orf2bYareWv/E4t7iJ
                            5ZZbdbqV7KWJPu7U3+Uz/wB53/uV87/GO58Rp4v8H+IfIih0yW1upb59q/Z4ovNeJ0/vfuvkVXr3
                            2w8N+KLP4zPF59zeaJF4IispdZvoonuP7S2fIiS/7CbP9nc9fN738+j+C9TtraC9+0aXFZ6/P/wk
                            Mv2hINOid5YrWX5/maW43tsT/gW6o1NTkfizFc/EHXrjVWex8PWOg6Az6LZ2/wAlpYxWsUu+3Vf+
                            essrbl+X+P5q8B8Q+IJ4GtY9QtJvNltYpZUu93myts+SXc3zfP8Ae/usuyuu1a31P4iapqVw2qtD
                            qHiCdtSutLG5PnZm2Ls+78q+btX+FXWuB8YateaxLb3d5eSX9w0ECpcTNv8A3Sps2f7Kr9zbWsTn
                            rS5Tm/3ryszf8svvbvlqORjHE428y7WVqZJcy/OrNv3Nuaod/wDD/wChVocAUUUR0jUP96r1g0aS
                            /vU+8v3/AO7/ALVUfvVL/u0C/vHrPwdtr7UPFGiWdiyzbmlvbqG4b918vyI7p/s1+1/wxh02aWyb
                            7TI8VhbRJE/34mi2bET/AGq/HD9m22g/tyW+lWN3sGXb999nz7kfZ/v/AN+v2V8DTRaJ4X09ViVN
                            tsr73/h+RN/+f9usvtHX9g6XVXg8PK95a6Qs12yqm9IvuxLvply8dzod6ys39p3Fqv2q3RvniXZv
                            2f8Aj1WLm11C/i1CJZFhdolS1mdv3Uu3532f7NVby2/tKW4sba5jhuFX7Uzw/IjN9x97/wC/VmWp
                            ykN40ejSsyyaan2Vbez+be91Ls/jplzqUGlttuVV9dlVfNTd97++9TQvc3Om28uqqtm8qq8vkr/q
                            pazLN21u8llWzb7W0vlLdzLs2xVBqRa4k+lWsutTzrMl0vmwQp8jqtebeIYbnVfD3kLcwTXvms7S
                            /wAG377ps/3K7bxVoM+vWGqy6m3nRRN+4S3+R1VE/wDQa4TUraKz8L6neXl8tn9gs/Ki8lvnZm/g
                            T/xxaC4nBeKIbOGWKKfyIbezi+0LYwr8/wA2/wDg/wC+68K8c+JJ7nwzDY2d5/ZVlYX32ixXds+Z
                            v43/AOB/3/u17bqvjmfw2uiahpGi215qEVn9n864bft3fIju/wDe/wDs68c8c+G9P+Htr4gu9e16
                            21vxKrLLY6fp8W+3+b53+ff83z/LWH2joOF8W6Is2s3bJPHeIsCyzzXEu/f/AB7Pv/77/wDAK8h1
                            6ZodcdVud8UsXy7P/ZP73/AK9emsLO51K0vP7MnvL3UoG3Qv8ifMm/eif7CI9cDf6VZ2f2hLmzaH
                            UFlZoPm+eJf4ET+61aakyOVvJI7zS/7Ka5bYq72+X5FX+4lc1qkkW11nWR3+VIPm27dtdfqmmwaV
                            cfY552hu2n/eyuyfd3/wVzviSzWwv7hV3PEu3a83yPtajUxOfuHlhj8ptqO38e77tY9wjNvZd2z+
                            9W29zG6pct99PkXf9xqwbiaWTf8AN8m6tYmNTljEq/db+GrENu0yuyr8i/eqFkVY/vfPT0mkhhdV
                            b5G+8tbHAV/4aKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiin/8AodAHqvwltlmuoq+2Pg5pqoyfLsf5Ur46+CcKvdRbq+6vg/Yec1vtXZ82+uCp8Z7F
                            D4T6d8DWa21lEu37y76b8S7NptDuP4/larHhj9zFEv8As1d8Z7ZtDm3L8+2uiBHN7x+YXxX037Nr
                            1wq/f83+GvNLzcjJt+R/uNsr2v462a2GvXG1VTc2/wD2/v14e83nXG1vuUi5D7P7/wA27Z8m7fWr
                            bJvldm+dKz4fkXd/31V2zdn37qCDQs0++q/Ptro9KsG3bl27/u1mWFmqS7m/irsNKtlRU/dL81Rq
                            XEu6JpvzIyrvf7jf7VdxpulKi/w1BoumqiokXyf/ALFdvYaUrxRKq73ZaDoJtH0dUZG2/wC38ldL
                            DpsUKptX5Kt6Vo/yojRfdWtV7Bkt/mVX20EHH3mm/M/y/Iv8dclrcLQq7L89eoXibFdfuJXm/idP
                            JldVdnSs+U3jI831pN/zMq/LXA6r89w6r/wJP9mu+1h/lfd/tf7lcDqSeWz7vv0co9Tj9YhZN+5d
                            n8dcbrb71/v/AMFdh4kuX+fa2x/ubN1cPfvvf7tEYmcpHP3jsivuffu+9XM3j7GfazVt64+yL5fv
                            s1c5M+9n/uV0xicFap7pFJUVK1JWx5oUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFF
                            ABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUA
                            FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFAD/92tjwreHTfEWmXK/wTr/6FWPu2tVi2l8m4ik/usrUFx3P
                            3F/Zy1j+1fh3ZS7lf90tdF420efVfmWX7v3VrxX9iTxOusfD63iVt+35PvV9G3Nt5yvurzz2Ph94
                            8k1Wwa2t3iZt/wAteK/EXwwtysu1dj/7tfTXiHR9lvLtXftX+7XkniHSpblZfl+WueUTspSPiXxh
                            on2a4lVvnf8A21+7XlOt6ayN8v8A+zX1D8S/DDQyysy7P41rwnxBo7JKy7fkoiXUPKrmFft1vEzb
                            4vN+av0l/YP8W6jqnw5u9KsWX7Fu+eFfnfaj/f8A+B7q/O3WLZkd5V3J95N6L92vsX/gn74w/s3T
                            dQ0q2X7HcSt5rzfefaqOj/8AoVdBzRPuN7mV9Dlia8kh3K0rIkqO6pv+5srsIb9rnRriVWjsNM2+
                            b5yffbb/AHP7qVzlnrdi9vdyyt/pETfuJkXfLK2z7lSpqTWctk0ESzO3+t+Xci7k+5spxkc1U67U
                            pLm/0557aXZqsqeVA+3+Jf77/wANZ/8AZty9wkVzFvlXa95d2jb0a6/gif8A2f8Abq7qurK9ntto
                            lSX7i/L/AK1mT5/+ApXP/Zr7QbeWSBWmdYGllmuG+dpdn9z+Jv7tbmRY0251C8v9buYL6S5eK8+x
                            PYzRJ5TNsT5Edv4f/iKu63qU99FrEGoLaaPp8X+i3VxfT73ZW+T79RW2qfafDUWr2etSzeb5UUs1
                            wuz7Gm/5/K/6av8Ad3/7dcV4w0258Q2d3p9zO2t6ZZ7dQtZrjZFaRXEEqSxI7p8zb32bn/2KBfaM
                            fxBeaH4b8TaxaT61p82oWDLq/iS483zbh4oERIrdIm/h+fa3+/XM+H45/D+h+INcutQ0+08R6D9s
                            fXdYmtUlt4opYt72+/f/AMsl2K397ZTNH8AW3gnxv4i8R6V4P0Sz8R/2Hv1HVpp3lRr2ff8AwP8A
                            8skZov8Aadq4rw94V8R+NtWt28Uavp82ia9A27SfK83z7izfyruW4Rf+mqO393+GoNjF1vxmvwK+
                            EHg3QbzV7x7u3sdW1Kxmu283+0mV08p7hl37Vfa/lL/dSvKptaf4iaH8NJI7e08E3fjS5v7LWrvV
                            IPNtLpLOWV4kRP40Rl2/7LPt+avSPi5rmj/FDxJqCtb2fhPw/qzy+HdK1uaJfNl0iL97cNEjfcbe
                            mxU2/wAdfKMNz4S03wDqWqyXWvalfeF9V+y+HtJdvKt4rOfezvO/8O9n+6n/AAP71WEo+6c14q0S
                            fxN4f8UeNrRl0q30S+tbKdXl2vLdTrLsSLZu3fLbys33dv3a8q1XyvLt2ijZLeXc/wA/8Xz7d9e8
                            eMvE+ua38Pfh7oFjpsWj+GovPg060t4ki+33U/yXEsr7vmlRHiVWfc210/vNXlHiDw/LpuhPZMtk
                            nlStN9o3fvd/lfPb/wDAaqJzVPeicNGsc0n8SL/D/vUyVGRU+X7y0x/lba1Wbhv9DtV/u7//AEKt
                            jgEZf3UTf7TVXqzIq/YLfa3z7m3VWqDaI/8Ahp6/d3fw0z+GhvloNj279m24aPVtditp1hvZbH/R
                            k/vtv/v/AHU2fe+ev2X+FHiq+1LwDo923kaxts4ktYU2P5qtEmze6/Lu+5X44fsqzI/xMezaDzku
                            LVllSHajsv8AHs/h+783/AK/YT4J38EPwj0xldk+ywPZS3EWyKJpd7s7/L/F8/8A45XNL4jan8J0
                            2m39zbXSf2neLeX1/F9n+yQtvii8r/W7P7v3/m/3K5n+1V0q61VdQ0G8h8rUVtbG4t/nSVWi+/8A
                            7v3627bW9KmsJZ9PnbXtVWWKKL5VSaBZU3+a9UtVffpN7eXOrsl6rb1sZm/4BsRP9utA5SHVde0z
                            Tb+yllvPtMt/LElqj/cVd6ebsT/crkvHnxy0x/EHivU9GiubnR/DliqRXCQPEl1dMj/JFu2ebs2f
                            wfxVp6boOg23ijzYLz7frdnB/wAfCMn/ABLmaL7if3ar3+sQWcqWepwec9qu+DfBv3S7/k/+KoL5
                            YnOP/auseD4ra+1yPw3res2vmz7/AL8Ssm/Y/wDd2b68is9EvE8M6npVnHqGvaPpcvy30ypF5+3/
                            AJa7/wCL5/7leoeJJvD3hvxBqsVzq7alrd/pn2i+e4+fyNqfcRP4d+/7leb+LfHmkarqXhrw54ev
                            rnRNMutOit9TmRfnll37/kRv79YSNonnPiewXRP7Kuda1WO5tNSgV4rGFn+X+Pe//AETb/crl5ry
                            DWNWRdKsbaH7UsVu01xF88USfPv3/e279jf7WytbXvBmi+IbPXdT1zV7mw/sFVTTIUX97dbd/wAj
                            /wAO35Ep39pWfhvwb4fvll87VfFESpPC2x3tf+Af7CJRzGp5vcpPN4m82BvOtNL/AOXjzUTzYldN
                            6J/vpv8A7tee/Ei/vJvFCXkG1EvNsu1FdPK/4FXrtt9je6ls9Kiney2rFdXDbJX+/wDO/wDu/P8A
                            crzXxnbWP2jVYLaeS/eX5LV0+RP+B/3aOYg5FE0+w1JLzVZV1KVVbfCi/Ju3/I7vXJahcy6kt7cs
                            rJaS7kgd/wC7v2VtWEP2CV9MniZJZfkn8778SrVW80261i8lsbODfb2cDsyo2zav9/8A4HWhJwt8
                            uywii3b/AC2b7tZnzI3zfP8A71b7p9svJYIv3Py/Mzr93bWRfTfabj5UVP4V2VrE460SpcvH5v7r
                            7lV6VqStjgCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoop+3bQAyiin
                            7fly1ADKKe3zNSeXQA2inSUrfw0Ae3/BD/j6Td/dWvvb4OM32e0l+4lfAPwQm2aglff3wfh/0W3/
                            AIE2/wDfNcFT4z3qf8I+kPD1zv8AK2tWx4hhWbS5Vb7m2uZ8NzLCqfL/AOPV0Gqzb7CXc38NdEDj
                            kfn7+0bpuzUbtv493/s9fNly/wBml+ba+1q+sP2lrBvtTtt37m/8dr5XuYdkv+78vz0i2NT99LFt
                            +T5vu/8As9dPpVhv2bfnrCsId8qf3938ddbpvzxfKq/doA2NN03ZL8yrv+X/AIDXXaJYN8m77lZ9
                            mkX7rb8+2u40Sz/1X9zbvqNTUtaVuSX5v4a9G8No21Pl31z9hpKzKjNtr0DRNKWPyv7u6lGJZu6V
                            C235l+Tbvq7c2you5fv/AMVaFnZ/Km37tF5bMjf360MuY5LVYV+zv8v3a8n8Tw72fb9+vYNStlVZ
                            fup/BXlnid1RZf7it9+s5G0Ty3UvkXa235a8/wBem2M/zV3utzL8/wA2x/ufJXmXiebyfN3N/eo1
                            KOJ1u53q7L/e+XfXJalN5K/N/d/8erd1S53s7Vxuq3W+Xd/tf3qeplKRj6xc72/i2LWC/wB6tC+m
                            3s7Lu2bv71UDXRE8utL3hlFFFWYBRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFOjpv8VO+7QB+j3/BOvxh52ky2Lt/qm/j/AN+v0A2b/u1+UX7A
                            /ihdL8YXFm3/AC1l31+rulTfabOJv7yrXBL4z2Ob3eYo3MK3C7WWuF17RFRZW216Bc2zeb/sVz+v
                            WzOroq76JRNqZ80/Ejw8kyy/L93+5XzP4z8NsjOyrsevtDxnpWyKVtu9/uNXz74z0eJGlX5ti/P/
                            ALrVx/Cd/wBk+Wdb0Hzm2tF9773+7Xrf7KOpN4b8b2kDsqWl0sqKiS/O2102f99/Otc54h03ZcS7
                            dr7mb5KyvBmsL4b8YaVfbvJli3Rb/wDrq+yrObl94/SDR7yLUrdJbaePzVRv3KfPu/267jTXl+3u
                            2keZDEv3Xdf3XzfI/wD45XiXhjXpbP8As+DyoET7KvzpL8jLs+d67qw8Tqlv/ZVzcyQ2XzIr27b0
                            3ff2f+OVtGQVInq0OpXN5LL8sDvK2+B/7v8AsOn8NM1W/azuPNWKea4lZbf7Pu+S1/2/+B1hW2pS
                            3l59jngu7CWXc/nQr/rV2bP++tlUbnXtl1d6ZPqKw2lntRZvvvLuT5It396tuY4+U6tvtU2/T54I
                            IdKafzWt5vkRYkRN7u/97f8Awf7lcp4kmufEOtXtzpup21hpX2GW1ie4+SKzvF+eJ/K/ib+Km21/
                            falrl3B9mnf7HZy6hFb+a6JLcL8nlO/975k2pTNe8Qtq2qfbLnSP7BtIoLe4uri0dHlupfvvEif7
                            iOv/AAOnqHKef2c3hfVbDxxLrmuXN5qupNb3GpzXDfZ0unit3litLdG+837rfsSvPLn4zaVpvhX4
                            ZeKp9PbTfDV5qdxp8+kvE8V9Esr/AGiW4RF/1sHmvtbZ8rV3d/qWg+KtF0zx/qH2uG7+yrLp1jfQ
                            b0WWX+N9v9/Zt3/7dYnirR9I8eMjfbLabXYrW31Ce4uF8pLC1aXzfs9v/Cq/w76z941PP/DGpQfF
                            HXPB+p694Qk1W9Ztc1W+hffFb6TarcO9pvRvlXe6fx/N+6r5/wDip9h1XVtPnttTbxDfeJtObVfE
                            Vx4bg/0Gwb7iW8Sfd2xIiea7/wB+vSLDxbqv/CwfHvgzV4NWm0TVJb+Vk/epL+6810iTb96J/vf7
                            rp/frzPVPiN/ZtjaWvg6BvDGm6t4Xt9F1Vn3SpFtdHeVX+bZv/ib/Ypxl7o+U4LxV4gudQ8KWGjN
                            FMi6NPL5V3Fu/dTy+V8+7721Vt/k3fOzP/sLXGeJv7PFrdbbyS51OWWW6lh8rb5DLLt+9/FvT5ty
                            10via2im8dXa22r3kWlXk8Tte3zb0i+RFeVlX5W+feq/8BrjdVhktdbt5PNWZ7dYnnZ/4W/jTa3+
                            9XRE46hx0aq0ibqb937v/fVbq6f+81NVwn2NWlVf+B7f/ZlrEVPuVfMcEogrM0W3d8m6mL81D/u2
                            ZaeNu35utMuISKq/dbfR/wCP0/btX5fv7qhb/ZoCR6Z8D7y5s/iRo7QcStdRbvm2KsW9d7/8BX5v
                            93dX7Q/CjVrG/wDCWmRQaYyafLF5UX2dvNt5WX+Nv7rbP79fhr4BRX8ZaIjs2xryJW8ptr/fr9nf
                            gn4ks08My6ZbT+TpkUv2tU27JWlb76f99vWUviOmjH3T0XVYbzRPGEWoTwfbNM8hXlh0/wCTzbpn
                            dIk/2tiUarZteXGsan59pZ2mmxbF1C4Xekrfef8A74pt5eX2jrcXltp6+IbfbtlsbeXYkTfwbP7z
                            fPueuP8AEOgtrez7Vc3b6JZ332KXTIfkilZkTf8A8BTf/wCOVnqdPKaGsX+labfxMumNv1bddT+T
                            E++6VYvkeX+7UL+IZf7SuItMl/tXzWZJ7hF/49fk/wBUlW7y8WbQ5bRtcg828l+zxJ/y1VVrgtN0
                            dfiRrmpWNtqdz4SsrVpUttQfYiS7UfzX/wBpv/QaXMWYniLWIvAdnrE8vg6+1W71Sfav3H82Vv8A
                            lkn/AI5XJeJ0gufEb65c6faeG9Ys1VlR23orKn8G3733Nvyf3K2vEOsSvoKW0GuLZ/Y5WsoNQ3b/
                            ADW+48qf7X368/1vxJB4b8JXdzeTyXPiC8uvsVrv/wCWVu3yI/8AdVn+9vrM6eX3SLw94k0HxJ4j
                            tNPublUsmi+0Xl9drv3fOm//AGf4Nv3K8/8Ai7omn2C3ep6V9rhRp/8AiWW7q73Dfwf73zp8yold
                            74D8Taf4D8R+I4PsNjqSXkFvawahMqP5CxI+/Z/45/3xVjQX8nx9/bMFzbX8VvFLdxXeof6qJVT+
                            D/a+eoI+GR5fptz/AGD4X0+fzZP7Sls2+2Wky7Nu7Z99G+63yp8leb6DbLqVr4gaztWmuIm+0I/3
                            EiXfs+d/4mq3r2vX3xC+JEX265XStPlvPKvJkb/VRK/z/wDAn2/7nz1meM9bs/Acstjod4s1kzNt
                            mdt7y7n+Tf8A7lWaHnVzZ6rrfiG42r5163zs6f8Aj++rF5DP4V2f6Yv2uVfKnT+5/sV2em6xouiX
                            lxqtsrJcXUWzyXb513fx/wC89eX+MIb7+2Xntlldpdzsj/NtrUwl7pFDptzcWF1qcsEiaez+U12i
                            /uvNZN2zd91tq/wf7Vc/qUMSaWjQKrpu+ab+Nq9Ft/Hk9v8ACe48I3dsqRNLLdRJMu3czP8AO+3+
                            8qxf+P1wmtJ9l0m0gaNfvbvkqzjl70TkqKmd13fKuxqYq10HmjKKKKACiiigAooooAKKKKACiiig
                            AooooAKKKKACiiigAoop6rQAyipdnzUbWoL5RlKu6nIlPRKm4cox/mo2f7dPb/dplBfKNX71D/P8
                            1WJI1b7tQ1REo8oza1L/ABLTqazUEHrXwQmX+1kV6/Qj4S3i/YLf5fvfJX5xfCW52a9Fub7zL8lf
                            or8KJl/suy+ZdlcFT4j2KHvRPoDQZv8AR0/v1tzXPnW7q38Vcjol4qRJ/Glbb3mxX20RCR87/tD6
                            Is1rLKy7/wC9XxZqUPk3kvysiNu+/X3x8Y7Z9S0m4Vfk+WviLxVYNZ6lLuX/AIG/+/W5DMqxT7iv
                            /e+Wul0p9+xtv+6n92uXtpvmiX7kS1t2fyN8tAI73Strqi/M/wDBvr0Pw2m/Yu75/uf8BrznQUZt
                            i/M716h4ehWGVGb+L56g1PQNBs/OVNqs/wDGtd3oNg21Fb+H565Lw3N8ybv7uyu90n+BlqyZG7Zw
                            t9n+b5P4Kbf/AOq+b5Ku2yM8SfwbaivNrqm/5E+/QQcD4hfyd/8Ac+/XkXie5++v30+/XsHidFmi
                            dl+7trwrxnefY7h9y/xVnI2ief8AiS52K+1vn215T4huWml/h3/N8n92u41vUvOl+81eda3cq8rt
                            L8n92jUDitbvFRXXcu9f79cPqt5+9+X/AIDXS62+9nb5dm7ZXH6qio3y7f8AgFbRMakvdM95mkbc
                            1RU//ZplbHlBRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFAB/FT0/wBZTP4qKAPev2RdS+wfFWyVt3zMtftH4SdbnSbdl/u1+G/7OV59j+KG
                            lf7Uq1+33gB9/hu3b+J1rjqfGelT/hG7NCu19tc5qsK+U9dRM6v8tZVzCu193yJRqbRPLPE9tFHZ
                            uzKr7l3183+P0gmuLj7v+zX0x4/v7b7O0W/Zt+SvmTxhNEl+/wA2/wC9/wCh1zSO+meNeJ9H3tuX
                            /gaJXD22j20OpP8AaYt8TLsXZ99WV96On/fFeseIfKdd+7Zt3J/4/XnWq+Xps3nsv8TbX/u7t+9/
                            95F/9DoCXxHtvgDxdeX1vp86+Y/lf6PK+3ft+TY7/wC/Xufhi885f7PuYJEu4l3xPafP8v3Pnr5h
                            +FHif7NpaaYtz9mivNz/ACfO/wDl6+gPCXiTb4P/ALIXy31BpWvfte7e7/3Ef/ZSsfhkbfFE9b+G
                            /iT/AEe7a7aS/iis3Szvnb96t029/uf3fn/9AqXZcppemafc/JdxXUUrTXbRRRf77/7Vef6U7W1r
                            b3LMv2KL/UOnz3E/9xK9OuNE1B9J0We80zfpV/FE/wDBKi7fn2On96uyJx1I+8ci+m+L5vFHm3Oq
                            2l/p91dea9u8vlJAq/Ij/L95f/i6b42sNc8Q2FvpmmaVHqWmaXdW97azQz/Z3upVR/k/veVvdN9W
                            rnVfDmmy3dn/AGZGnn+VZS2j77dFiZ32J/6G1Ytto99qTfY7VpLCy1GezigsbG62eUyy+a6f9cn8
                            pPn/ANt6RmUbyGea80TwczSf2reTy2893p677ewt1i2P/u7PnbY/3lrze80fU7/wA+gz+I/7e0+/
                            0yw/s600yDzb5bVZf+Pq42/MqvXpHjO50rTbfStM8LtO+uywXFlE+mLK6WrT70ld3+62/YnzvXNf
                            Drw9ofg/RvGCzxR6J4KsLNpV8STSrb3F/cLv2WqOuxvkagDy/wAWfEJ9SX4hQeGNPWbR7DU7DSrP
                            UPEN8lrKkUqeVvZ2+bzX8p92/wC7Fs/v14/8WtH0X4e3nhTSPDFjPNbtara6rcK3mpdXX2je/lSp
                            96JEfZ8le2694b02b4ueFdF8S6RbX/ge3061uLl7iX55f3TunlOv8Urvt+f5v3VeNeHvFWq6V8SL
                            jw9ttvBOlatrDXWy+3xJYRL5uyLf95VRP7n3mdKfMWc7qXjTQP8AhVtp8PrTw8ujsniG41fU9ZuG
                            817rbsWJNv3liSLzdy/3nRv71eO6xcfbtO1C5aD7NfNfreysnyo0Uv3Pl+98r/8AoVeqTaHpFn4B
                            8RSNO2peK21q6+x3MMTukthFE7+b/d2yvLuV/wDYrz3+x18M32n3MXkXkU7WssuxvNTypU83ynVf
                            4kVfmrc5JROavpp5rjUmgZvlbfK38e37rfNXNpJsl3bW313OqLJeah4jlRFmi8rzVlib5FXzUZPm
                            /wB35a5eSFbmN5VdYU81vlqonNUiZ+xnXd/49Tkd3l+b/cqa5mj8xFi3bFX5aqR0zMd9/wD26HRq
                            Nny7/vr92ljX5d25d25aAJrG8ns7pJ0fZKr7lf8AutX6nfs0/Evw+niPxVbavPqiW9/p1u8DravK
                            n2ppXff/AMD31+VSbdv+3X3j+xP4wu7z7DE1xHNcWt1a2U/73fus2+dH2f7DJt/4BUVjej/KfdSa
                            rotrq39rrqc95FdbrKJLdv8AVNK+z7n+xsqH7S3hLWdM/sWefVdKilurttMmTc91LKnlJv3fdVNm
                            7dTYdY0X/hI7jULmKxmi02X/AI+4W2Stu3/uok/2P4q5zwrZ6ZYal4g1Bby7SXUtRtYondt7xRSp
                            8/8AwFEeuc7+U3rDxPvvLi+Wz0mz1Oz3RS3dw2xGbyv+WX97ZXllz4h1z7Bp9tcrbJFeWNxKsL7E
                            eJWfZv8A/Q6is/Bln9q1vTNGa+8VXezZY6ncLtiVWl/e7E/ibZ8tXfGeqxX9n4u/sjwvHZu221/t
                            OZv9Qi/fSL/c2fwU+Y2jHlPJ/Cula1baXp+gLFaTXazyur3bbIlX+DZXUfEXwN4Q8K+C9Hg0zxLP
                            4k8R6lK0Wo26f6qJm++iIv8Aqtn3f722uEf4r3M114C8PahZx2dv4fZbXU75F33EsX8bv8n8f/oS
                            VQ+Jd59s1nxHZ+FZVh0xZftVr5rfvWV/87qnmKlGXMTvbaLpvh/TINPljvJUb7RdJMyfuv8AY3/3
                            kT/x+sLW7rSvFum3EtnPPYXHmxWtrY27fw7Hd9/+0/8A47VTRNE8PWfhXxLLqtzP/wAJHLFFFpkK
                            S7PvI7u7/wCzv/8AZ65rwyl5o9rFZz+fMkStLLcW7feuGT5E3/3E3/8AodSPlOcufDen3/i1LOeW
                            503T9srzy7fni2pv/wC+ndNtea+IdHWwaWKK++2eVL8z7X2Kv9/fXoGsaleXml3rTytDe3k+9kmX
                            ZtXfsT56ybm8bTdJuNKaWOb7V88roqfd2bP/ALL/AHqknUbrfw91Pwr/AMI1Pqfl7LxYrpXiZH2K
                            3z7P9756Z4t0GzvPFVoumeZNLL/qof4G/vps/hrPtvE95qWjPYtLJeWlqvyyzN/sf7VaFhc6fbaC
                            mrrLIniiLzUZ933l3uiI6fwLs2fc/v1tEzlErpqS6Vr0s99Z+dcRRfZ/3yo/lfJs315/raS63Les
                            nlwxLKzqn+fu11Fn9p8T39w0Sq6xf6RLvb+Fv7lYiW11eXF3bWarCkvyPvb560MZRPPWXc/zNUNd
                            T/wj99eWF00EcbxWH+tf7u7d/wChfcrnpvK8pNq/P/FXRE8qpHlkVaKKKsxCiiigAooooAKKKKAC
                            iinx7f4qAGU7y6PlooAVlozto/hqWgvl5iJjuahVanJHT/MqbhGIzbup6J/dp6/KybVpKRcYxG+X
                            TvLp/wDDRHUnTyjdm7eq0zZ5exqm+X7n/s3y0zcfu/L8tBjyh5ir9371J/eo+X+Ld92mv975aCP8
                            Q7+5/fpq/wCzTPvtT3/gqgkMprLTqZTREjsPh1f/AGPxBb7v4nWv0L+EWq+do9vt+f8Aj/76r82N
                            Bm+z30Lf7S197/ATWFubC3VmbZ8v/oFcdT4j1MP8J9NaVf7LdNzb/lrZh1Xf/uVyNtcrc26fN/sV
                            bSb7NsXdv+apOqRL4ns/7StZdv39uyvj34r+FWsLy4ZV+639yvsr5pon/gX+7Xgvxj0TzldvK3ot
                            amJ8rpuSV/u7N38ddLoiK7Ivy72+Ssq5sGS6/iT53rotDtmdlX+78/z1ZkdtoKbFTarJub/vmvSN
                            K2zSxLEv3dv+5XCaU628tdxoN4sLIrff3LUGh6R4Yhle4iVvnTbv316XpUKpsXd/D81ec+GJlSX5
                            G3/LXpGlfPs/gfbVkyOrtkXyk2/c21maruT7vyVoWyfuv92srW5lSJ91BJw/id/JtZW/hb+Cvnrx
                            /Mz+ay/399ey+MtSWGJ9zbErwzxheK6v83zsv/j1BoeT69cxQq6/Lv3NtrzLxDqX712b/gNdr4nm
                            Z7iVf42rzXW3R2f/AL42VGpMjnNVufOZ12/xfLXNXz10F58jf+P1zV9N50ua0j8RzVPhKrUlFFbn
                            AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA
                            UUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABR
                            RRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFF
                            FABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUU
                            AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA
                            UUUUAOpdpahf4a2PDeiy67qlvZxLv3t81BcY80j1r9lvwHd+JPiNp86Rt9nilXe/+z/HX7QeDLP7
                            BodvH/0yWvj/APZL+CEXhiwtLm5tlSWX5/n/AIV/gr7T01NkW1fuVwc3NI9Xl5I8pLCjbn+b/drm
                            vE+pfYIpW3bPl37K6i8/0aJ5X+5XhnxF8WtNK6q3yrRIulHmOE8ea81z5rbm+b73zfJXj/ieZbm3
                            83d8/wA3+3ursPEkzXm/d9+vNfFVz5K+Uv3P76fw1ieh9k5TVb9XtXauH8T3i3Nu8G7ZtWuj1uZU
                            V9r764HWH86J2Zvk+/soiYSLHgzxVBo8v79W+0RTqkTo33f9j/vjfX1H4S8SWaSvfaY0E1u0XlRT
                            Tf3mr4iubxUaXavyMrbv/i69v+C3iqJLVNKbd9nliXbvb7zf7FYyNqZ9beD5r5Ld7ZZVfU13Syuz
                            f6r7+zZ/s/croNK0fVfEl/omiwavczXEs/2prG3leK3iXZseX/gFedeGLyKGKJp4m+aLyt/m7N+1
                            /kR//HK7rSptTttSlubV/nVmt4prdvs77WT/AFSPV05BUidhrdyqqjXNjaeVFeLF/ac2x4pdsTpv
                            f+L+Os258N21v4o1C50GW21jWIl+z3V3cb/skHyf8e8X8O7565m2v2uYrG5bTG1KLz99rD5vzq8S
                            fOj7v9tHrq9N1iL+zZdDvLaPStQlbzWhtFR0ut0qf6r+6+zeu/8A4DXQcconn+mzah4VutQs7HVb
                            bw94Xv8AUZbqXU4V+0Sp+6fZEif7cuxFSsL4kfDTwheeC9P0r+z9Q03QorxXiu5p/Nl+zs/71Et2
                            /wCWr733O9dh4V1tbC31DUPEMFpommWF59tupktXSX91E7xSon3d29Erj/E9/wCJfDek6ZPbXlpr
                            0Uujtdf6WqXEv2hokld5UX/f+/UFfaMG/wBS0WbWdMs59P1SHT4rO3dbGFUT7B5SOlul0/8AC/z/
                            AHN/8aVwtnpX/CxItQ0/XNSj0G4lsf7dvr6+tkurieBpUTfE397arbf7vybq9Am8AS2fhy0XxDqs
                            F/ZX91cXrQ28r+bf3Sy7E2J/D5SJuVH/AIdlcTqU0F58bH1Bbm5fXdOZrWXRtPb97fr5SIiRP93a
                            +9N/+0lWB5hrUOq/ELQVsfDV59vh8PxX9lo8OxLe4n0RNkvmvt/iTf8Ad+987rWD4uh8Iab4f8CX
                            Xgq2W/stL0L7V4imRvnutU2Pv3/7CM/yf7G+ug1vSm8AeFdPvNPgks9Ys9Wv9PvNJuJ/3tntt96f
                            Ov3l/e7l3/3K4u5j0288O63J4eX7Ba3ki77GG533E679qJKrfd/ett2/xVpGRlKJ55rH2HT/AAfA
                            tirbbyXfI3m/PFtT54mT+6zbGVv9msTVbadLeGL5X+1RfbUSLb8u7b97/vmug8YeG77w8tvrS2K2
                            FleSS28Sbl+byvllRk/3ty/8Aom2x/Z4EtlZ4raKWWXanzRMiJsX/ZZ3/wDH60OaUeY4RY91u21f
                            utt31XRfm+Wr0i7Y3UrseN9q0xF22+7/AD/HVnNylTZ975qP/QKdvX5ty0qf7X3aYhj7kavc/wBm
                            rx4/g3XtaW2i866uLPfF838USO3yf7W9ty/7leFN8xrovButt4f1iK6RFZ9yr5rf8svmX56cvhFT
                            lyVD9hfBlz9s0ay1yziWwe6gt3nR9kvkX8sW97j/AGl+d66C81ZYby6vImjeJYoreKaaD5GX++if
                            xN8ir/wOvD/2TvG2oal4BuJZ4oLPUIoIr3Zt835Zf/ZnTY3/AANK9D1bxDPqWm6hc21nJrFvpcCx
                            RXF22yW1lZHdNifxfPFXB8J7sPfOO0rWNc1T4paJ4ctfEcemytavE1x5X+j2G3e+/wD3k/g/36xf
                            EWsaLprXFnqtzP8AZ5bqJ9Oh09nRLxfuO7/777P++6Z4Y02zm1y7+03i2eq+ILqK1lu5vn+yxN89
                            xs/74+/XR6preg+HfhvrEWi6b/bHiC11WWy/tB2TfLFFKjxbFf8AubEqIly92RympeP9B8H/AAb8
                            VeHp/Dyp4o1a5+1fa5lRHf5/ub/9j7tc748S2+HvxV0Kz8WafbX9l/Znm7LGXdFuaL91vf8A2Hfb
                            WZ4/ubzUtJ12xbbeW8TLdT3b/fRpU2on+6/3v+B1haD8Lm8c+HF16fU9Q1KLTYpXvLSFXd1iV9nz
                            /wB1X/h/3KOaRfux94wbnxtbXOuXdrbQfZtPl3JA7rs3Lv2ffb+47uu+ua8T6rqHhLVJdBtr7+1Y
                            W2ur26uiNu+/8/8AeTftrq77QbvxB4m8KeENfkXw5YxeVuvm+Z4LP729/wDaZdyrv/i+arX7TEPg
                            zwlqlpY/Ddrm8smX/j4mZ5fm3pvffV8pHN9k8/8AFV/4e17wfp88Usn/AAlaz/v4f4FVX+SJE+98
                            n3md64LTdeuV8QJpiWbXn29ltWR1+dmd/uJ/DXW6J4S0Ow8H3fiW81Vv+El81kWxf7irs/j/ANqu
                            X0nx/baLZ2+7TlmvYr77bFcOvzs2/wCSkR/hNa/+Gi6bpOt3N9qUelTWsrxLp+1H83am93+/919+
                            1X/2K5dLZodJiggi867Zt7N/s/wJW3qGpahql/L4o8Tae0NlfxbLN5l2+b/t1yOq6rPYXSfY4pH3
                            f7P/AHxVmZ0ulabLo+h3E6rs1CVvmf8Ag276x/D1tBNLd6hPebLdW2On3Nzf79bF5f3KaDFFPtmu
                            GVUXyf4VZ3+d65rxU0Gi2cUFsnk3Ev3/AJvnb/fp/wCEBrXMFtrzt/y6yxNLLbo29N2x1T/xxt1c
                            TraRrcfuolhX+7XQalbWyWdvc2creb5StKjVm3NnHqiRMs6+bt+dnrpgcdePunOUU9ty01q2PLEo
                            oooAKKKKACiiigAp+37tM/ip/wB75qAD/gVO2f3moSPdT9rVJtyhs2f7VP2UMu6hVqDaMeUF+f71
                            N/3d1OjXe33tlH3pG20AIn8dTP8A66hEXb9756H/APZqC4x5QX5fu0bt33af8zsiqtM/hbbUGw9v
                            l2fwL/eqFNu7d/DTn/1NR/MrLt/hqzGQkz7/APYWmojJ8y09ZmRqYztI77vneqOaXxBJ975qZU0b
                            /Mq/w0xvvfL/AOO0ByjPLoopWX+6tMRLbNslVv8Aar66/Z78Sf6LEu5fl218e7sNXuXwK177HeJF
                            ub71ZVjtw0vsn374ev2miXd/droPO2L/ABPXmvgzVfOtUVm+989dql/53yp89ckT0pHS2d4sy7WZ
                            t9cP8S9HW8sLj/d/u101hc+TLu/j+5VjW7Zby1ZW2um3fVxMD4x1vR2s9Sl+X7v3tn+/RpSLC3y/
                            fb7tegeP/Dy2d/LKteb/AGnyZdqt92tNTI66zm/df7ddLpXmTLF838dcVpV59xt1dx4Y2/aolb7n
                            3FoLieseErOVIkb5n+bZ/u167onzqn8HzbGrzzwx+5WJV+5XfaUnzVZEjqt+y3RVauV8T3Py7W3O
                            i10b/wCq+WuU8SP+6+78jfJQQeL+P7xX3fd+Vv8A2SvDPE9403zbv4fmr2jxy++J1b5PvfPXh/if
                            +NV+eoOj7J5p4huVeWV2b7y151qs3zPtX733a7XxPc/M9ee6lc/M7K3yf7FWc5maq/y/K33a5q6/
                            1j1sXz/fXdvf+KsSZt7VUDjqSIqKKc6ba2OYbRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFH8VAEsaM33a+vv2M/gj/b2sRaveQM6fK6V87/C
                            vwTL428VWlmqs6bvmr9gvgV8NLbwT4StIFgXf5Vcdaf2Ynq4an9qR3fhjR10q1iWCLZt+Su60222
                            L83z1i2EKvKlda8P2Ow82ojE2qSOP8f6x9j02WJW+fbXzF4kv5by6dtu91+SvZfH+sLNLKu7fXkW
                            q2eyJ5d2xPm+eokbUvhPPPE+qrbROrN/Fs/3v9ivPPEN5st/N270ZWSuo8Z36Iybl+Rd33/v15rr
                            epNcxfeXytv3Kg6Tmdbdvvb2/wDiq4XVbhn37v8AVV2Gq3nkrKzfOjfwV5zql/vllZfubqImRz+q
                            zLD8v8Dferc8M+OL7/R4PtMcP2NWeLev+5s2tXHareLufbWLDc7W3M23+8v96t+XmiYSqckj9J/B
                            lxY+P9JtG0idkTarxQ7t+5m+47P/ALiV2elXMttqllY3zKl7aqyK80X7qLb990f/AIHXy/8ABDxn
                            p+m6lb2dtqcc1vLaqkW35H810R3R/wDcb5a+hYXX7RZNczt5srea0P8Ay1iZfvvv/u/PXFKPJI74
                            /vond+DfGcttqVvY6k1tf6Z9si82H/VPtbenmo/3l/gb+L5U/wButC2uYry/12DRtQsnvZZ/Ntr5
                            IvNSKLf/AK3f95dlcF509tLerbKv2SKJkldG+eKLzUTfv/3P/Q6ls5m0HVrizW2aw+0M11ZujfIy
                            qm94n/74/wDH6uMiJUzsLx9XfTds9st5pUsC2U8NvOjvL5T/ADu6S/e3pv3fP/Alc5rbr4e0nxRq
                            d9Lc63LLdMkFjbxJ9k8pU3xJsX++/wB7/ZrT8TwxfZ9T1zUPslhcRTrd2tii7/vJ9/Z/d2O9V016
                            8udLsrZYlsH0u8uEi0ZPn83zfnill/vL8+2tTI88+IWlSzX8V5qum6kniCX7fcQTafeeVFBE2xIo
                            ok+988Uvzb6yrzwxoKWuu+Jd2/xNF5r+G7Ga8eK4ilgsrd3d3V9zfvfuo7/3/kr0tL+zvGdls9Zv
                            9T8OXTW95fPB9nSK1835Hd2+9v3/AHE/uV5lrHg/SvB+m+IrzTG1W/1XWfEOyOZ4vn06z8rbLKzN
                            /E7fN/u7VoAx9U8JaT488ceCPDyxalc+GPFV1Fca1cQv5txa6zKjtL5Tfe+5uXb8yfNu/hrxKb4f
                            eGtN8L3/AIg1B7yzuovNsv7G275b9Vdtsvyp+62Im599fQ//AAtRda+ImlW3g7wi1hFYSwW9jdwy
                            /wDL1Ejp5v8A21uJU3O/8Ncf8S/BPk/FLw1Z+JfEsFn4g1bTpb2V7GffaWc6o6eUzfL9/fs+5/HW
                            kTD/ABHlOteHLfVF8K+HPEulL4c8Rbt9rFNEw+2LLLE2+6Z9rfNF93Z/wKvLNQkW38MWt4HuYprh
                            tqqj/ulVXZ1R13fd2v8ALXpXjvxFq/j661PWvEs82q+I7CDY9wq7fI3bIkR/4fufd/hrzXVLy81K
                            z1qC58xLiARM0UK/JE0W1Pv/AO4v/fVbRMakTL8QNPqEb3cvlzNLKrSzRN96XZ91f/Ha5RvuIu3Z
                            /tVvakxtrGxtW3OtxbLdN/stvf5/++Kx7n5PlX50Vm2zf3q0OaXKQojSfL9xKidNjVYfdDEjN8+5
                            fl/2aryOvloo+9/FVHNIYjsm5VqaP5n3t91vvVDHu3fL9+rC7Y1X5vlb+7VkR3Pt79j/AOIr6JY2
                            VnbX0kOqrbXDxTQ/cVVRE2Sp935N/wArv/cevrLSv7PhV7ltMudNSKVUZH/492iW3+S4R/7zvv8A
                            k37dsv8Av1+afwR8R2ulXOq2l2rb7jSpYoNj/wCtl3I6pu/h+Xejf8Br9H/CuuS+M/CGiabZ6Q1+
                            9n9nt5ZnbzUiX7O7fO/8XyJt/wB5K4KkT3qUvdPPH8Q+Gk1nTJ9v9mxSxS2UqTLvSJfN+SVJf7zu
                            yf8Ajn9yrGq38F5odvrniWCx1Lypbh10yxZ0SXyk2J5qfxb/AJGqpqmtro/9t6fPpVjCmrWq2Uu+
                            B9m3fvTY/wDC38VVb+Hw94b8K6fFPcz6lrt/eRI0KQfJa28sqI7xf7if+z1zROyRz+j+KtM8Z+Kr
                            3/hJbGDwr4X1S8iumt9M/ur8mze3+2lZ+tePJ9K1bx7Y+Gmnh0S/VbW1u0ZE27fuJs/vb6Zrc2h6
                            VcarpmkafPeS2DLL9udkeKLc7vsdP+AfcSvMvEOpW39kpq899JC95dN59paK6fxpsdP7zffqyOXm
                            OX0+21PxJrP2HUNVnTbKqb7ht8rLs3I7/wC592vSPG3i3wLYeH/BljbWd3Z67/x66tNaT7/tSt/B
                            F/DF/B/3x86VykOpS+Er/StTg+zTRNLsi+0LvlRdmze6f+g/3azPFXhWWw1yWdmtn0+KVZWu7ff5
                            vzf3P7uzZ9+j4QlH3jktS8Nz2fiO7ivJ2hWL54Le4+d/7+x/9msfW9YvPE+qea1jGjxN5UvlL8jV
                            0tzeWOvate6hqV5LeSt8kEP/AC1l+f8Av1leMNcgh1xLnQbP+yot2z7Du3p/49QZam34Y+J1z4T8
                            YaE+p2Nt4k0HSX3xaZfL+6b5H2O/8PyfeVXrkvHHj6PXvGGv65Z2MFhFqErOlpCu1Fb5d7r/AAp/
                            wGue1aaW83s0nnI7b22/wt/cq3qnhO2/stJ4LyPfuX7/APtfw1tGRyy9wzYfEk8KrPu86aVv3qf+
                            gVY+zTzM8+pNsdl/dJ/7PV37HbWdnE/+jbNu/emzezL/AAVz+papPqUiTtuht1bar1uRzFK2825a
                            dVfYjfMzVnSOyNU1zefM6wM3lbvlqqxZvvNVxicEqnMQ077tNorU5gooooAKKKXdQAlFFP27qAE2
                            fLup8dNT5uGbatP+63y7v+BUFxHb6N9PT5fmajdu/hrI6REel20bfm+anIm6guIMvy7tvy03ZvWn
                            ffSmeXQEveHo2xk/vVYjZYfvf8BqLcvnbl+daP8Ae/vUBEf5jI25f4qTZ/Czfdp9ymxUZWX/AIBV
                            fzmf733KC5SH7/m3babcTK3y7f8AgVJJN93av8PzVE6t95qDGUiWZFRv7+7+OoNjRt83yUJ/rKc+
                            2qMAb/vumUzzKPMpj5h9P371qHzKVfmoI5hz/O1dX4A1VtK1mJt3yNXKeZVixuGtZ0lX76tSnH3S
                            6UuWR+gHw315bmzt23Kn8FeoR6qqfxb0X56+XPgt4nWawRWb+H7le0W2ttt+X+L71eb8J70T0aHW
                            N+/b9xvu10Fnqq3Nuis3z15fpusM7Iq/caui0HUv9KRW+5VBKJhfFfTfOgeVf7rf8Br58v4W+2Oq
                            /wATV9UeJ7NdSs5dyfeX/vqvn/XtH+x37tt/ireJzSG6Vpu9k/g3fO1d7oMPkqkv93564rQZtv8A
                            Fv3V3uiWzTKnzbKepEf5j1Pwxqu/YzN8jf8AxFep6I6zRIy7UrybwxpSpLEv3/l/75r1nQUVIk2t
                            935KC5HS+T+6rl/E9tsV66jfviSuZ8SfNE7Mu+rMTwXxym/zV2/e+f8A8frwHxbc+W0u3+Fa+g/H
                            7tufb8ny187+MEb97t/i/wDs6Dbm908f16Zpndm/hritVdVV/n/jrsteT5nXb935K4LW7rbvWgxq
                            GJfzfvXX/aqh91ae7MzNv5b/AGqhroiebKXMFFFFBAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAD2+9UscLOyqq7/mqJfmavSPgn8O5/iF42srO
                            JN8SsrPUylymlOPPLlPsr9hn4DqtmmtXkCvNL93d89ffvkxWFqkS1yXwo8GQeCfCtpbQRKm1f4K6
                            i5dryVGX7itXnns/B7sTd8PW3nM7N/epvjnW/sFg8S/3a09EhSzsHlb79ebePNY+33DxKzbK2Mo+
                            9I8t8Q6lLc3UvzfJ9yuP168l+zpubY/3FSuq1uaK1+Vm37fvb6838Va8qK8St93cv9ysZHfE8y8W
                            3i7vmZnf/wCzrzfVbrYvzNvrrfFV+rrKsTMnyt/6HXlviHUpdzqrb3/v1EQlIx9V1Jtu1m3/ADf3
                            vu1wmq3Plyytub5m/grY1W8ba/8AvfwVxuq3juzt/BW3KY83ulG8ufOl2rWY/wB7d/DUz/73z1X/
                            ANqumJ5tSXOd34JvLa1s3VYpP7Q89d0yN92KvtXwBrcXifwvaaqs/k7Va3aGVvvbfk+R/wDvivhf
                            w/qv9k291OqK7Mq/e/h+d697/Z7+K1nNb3HhzV4tm5muorhPv/Ls+T/gb1x16fMelhqvL7p9L20N
                            89vp8UDRwpKzRTu6um5Vf503/wC8iU19e1CwsL1VjV7eK2aWVHbekSq/z/7W7Yny1UfUpYbe0sdT
                            uY3t7j51eFt+1W/u/wDjlFsltrWjanottp8c2p3l0vlTXDeU8US/f2J/e2P/AN9JXm83IerynqCe
                            JIPiXdJeaZpkcLy3UST/ALpHf91s+Tf/AHazEttXh8fW8reZYS3Fr5Szbniis2id/N81/usr/wAN
                            Zum+NtP1XxV4c8L6U1zYPFFFaxTTRIjy7Uf/AFrr95v3X360tb1681Lw/dywMyaYsq2V4lpKkqSr
                            E/zy/N821E+9/wADrvjI4+Qi17XItV1LVWlnvkuNWilvYPJuv3V40XzxRIjfKyo77v8A9iuS1u51
                            P+2dP0HXvEN2+p3+mN4nnuLuCJHladEiSJEX70uxNuytq2s11XXtE1XT4p9e+wK1l9nRU+Zd7u8v
                            lfw/JsZdlc1c6wsNm2prqFtea7YWtxFPNcQbJbW3810t5d7fxJ8+5P8AvuqMZRPL7/w9d3+qXC6R
                            L/Zun2Go2u5/Ke3lXzUdnR3/AIv3sSN8n3VR6i+JFtoet6Td6fZ+Gru51iWWBvDs32p3RWiuP9It
                            URvmZpXfctdB42m0rT9Usrbw94l/4SrUNNSwvby+uG8pL+4llfzURF/uJs2/771X1RdT1L4eSreL
                            J4Y0e112WVdTSB727gv1bz7e3i/i2v8AJt2bdtOIVDw3XNe8N6lHr8XiC61mLW1gWygRbdbdJHT5
                            t10v3laJkZdv32+Rq8kSW80q6lkdmSVmaJ1b7kq/df733q9z8Q694f0vxhda5r2h3OtpqMVxLqOx
                            tiebLauife+6/m7HavJbu/k8NyW9n9m85Yp/tEH26Bv3bfL91f4lreJxS/vGN4quWv8AVrhoIme1
                            gVUi+bfsiXaif5/26wsN5CN/Bu/i+5XTXViupR+XbXUczqreXvbZuVX/ALn8Lf3V/u1zEkm9WVfk
                            Xf8AKm77tbHDIrvupqSfMNw3L/dqV/8AVI1RKm5a1MQU7W+WrFvGzsir99m+WoVWrFukrOm377fd
                            qJBH4zufCWuz+HI7i9t7SKd/3W2abf8AK33V3bX27dyfx1+hXwK8Q6mngGy0XzYPDep2qtqC64kX
                            lfL8jomxnfczulx/s/cr4Q8AQ6hY6Dq2tQXdp/Zuky2suoaZdy/vZ2Z5Vi2Rfx7PnZv7u7dX0z8I
                            9Y1fW5dP8QNBJrEV/Y/2fpmk+b9lt4vsu+Xf5v8AGyJLL8n/AE1RXrmqHq0j1bxD/b1myRLFA6S6
                            iz/a5mSWVrr76OifdXem/wCd/wDdrM8Tp4j0HxBqHhd0tLa7is2la4htfn8pvnf7O/3dyb3+T/0G
                            vTbCHWviX4ct/EM8Gm2esW959ngeFXiiliif+433vuf99V5L458YeMdBv4rlvMm1WKKWK1u3i/1q
                            sjps/wDQ645e6elGXOeY6xpNt4e0nxR/Yt5czaPeT74NQvmfzYlX+8mz5t/8P+1T00e517xNaeHN
                            agi03+y9F82D91se6X5HT5F/uVtpc3KRaVpmlah52oXkUry3GoQb7eWL5/K3/wAP9zd/wOuRm8SX
                            j6ld65qfiq2sNQtYnt4IbSL55/76b/7v8Kp/sUFyKXiGHQfA3iDSoG1BfEl3ut71b6Fd8Ssr/wCq
                            2N/7PVT4kX+r/GDxBLqd9LbaU7L+/wD3XlJLt+4mz+9/ufdqkmvaU+r/ANr2zNDb+R+4mSLZEtwy
                            fxo38P8A7NXNJqk8Ok3F5qdz50V586v/ALX+4v8A6DVmcjN8Mabc6JdahqX2FbxpYJVghdt0sS/x
                            v/dVq4ZLy91W+eddqKzbG3/ersJtKvtEuHa8a5sLi4gV9j/I8sTP8nyfwq9cpZ3EH9s3ESs0NlK3
                            zPN87rTM9Sazs7a31KVbmeNEiXeuz/lrTEs49YWLTILO5S6uGZ4pvn/er/BsX+Jaz3SRFuImgaZG
                            b5dn39taDXOr2NhZT207I8UX7p/k/dRbHR61jE5anvHK3Gmz2t49szbPKb+9UO90V4F+fd/CtXdU
                            +e3ilaVnu5WbzWdqp3CfuopFj2bV+d933mrqOOXulZ0+zXC/dmaqu6nyf61tzb/9qk3f3a1OGRFR
                            TtlH3HoENop/8P8AdplABS7ad/u0KtACeXT9q0+GTZTPvVJfKP8Al8r7vzf36ZQse6n+ZSL5R+/c
                            tN5X2pyfI33qN275v/Hak2HMNv8ADRu+WmPM38W7fSwlXb5moL5ojraF5m2r96ppm2fK21GX+7TP
                            OX7y/ItMeRd+5v8AgSUBzRjEmhdpvlX7396onf5vl27v71JDJ99VfYlNd9jfLQLm90Y+/wDip2/c
                            u1Uo+bd8y/eqLd81Uc5bS5ks9y7V+b++tV/vyUx3lf726m7t1PlDmDdt/wB6hF9W203dSVRiFFFF
                            ABRRTz/Dn7tABt+WinUbPuUFnrvwZ8QtZ3nlM38VfTdheLNb7l/2dtfFvhnUv7N1S3aDcm7729q+
                            l/B/iT7TYI3zPtX7j15tY96hL3T1C2fyfutvf/brTs9YlSWJlbZt2psrkrPUmdf77rWh9v8AOVP4
                            /wDfrM3PWNN1L+0rNN6rsX5GrzH4haUvmvKvyf8AAa0/D2ttD95fvfIqbqseJ3a/s/lVUdq3jI5Z
                            RPN9K+Rvm+R93yrXofhh2TY21vlXYtcTZ2fk3W35d+6vSPD3lW0W5l2O3z/7zVpqQeh+Hpn3Jub+
                            L/vmvTfDyK8Xyvv/AI68i0S8/wBIT5fkb/x2vVfD0zbU2ou/79ASOwhh/dVgeJEVIvmb/YrdR221
                            ynid2SJ9v39tWZHiXj+FV+X+8rJ89fPPjBNlu6ruR/8A0KvoPx+7Pv8A9mvnLxzc7F+b+Hd9z+9Q
                            VU+E8h8Q7tzturzfW3dGeu48Q37ea6qv3V/8ergr7fNv3ff3bqDGXvGLN96mVKyfvWWoq6DzQooo
                            oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiig
                            AooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAC
                            iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKK
                            KKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooo
                            oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACl20l
                            S+XQA+FGmlVV+9X6JfsH/B9bPTU1q5g/eytvV3WvhL4d+G5fFXi7T9PVGfzZVWv2g+BXgmPwl4L0
                            +BYtjrEv3E2VzVJfZPSw0fd5j0i5dYYtq/cWmabbfabiL5fvVXd/OuPKT59tdNoNsvm7mX/VVgdM
                            vhLGt7bDTdv/AACvH9bkX96y13vjnWGT91/CteWareecjqzb3276cgpHFa3Ms29mb5Pv14p48v8A
                            /SnVd3zbv9z79eoeJ5pNz7dybfkrxrxPeLbXEu7c7/c+9WJ0xPPPENy0Ky7t1eX+IbzZK+75E+b5
                            69A8VX/kr/wL+989eYeIZmeJ22/Iv3fmq4j1OR1i82fe3P8Aerl7ibf81aesXTTf8CasJ33N/s1v
                            GJxVJcgn/AqX/wAfo2/7XyUK1bHJqbGjpFN9qgdtglgbyv8Ae+8q0aJrE+g6zaX0H+ttZVlX/gNZ
                            kLujblq3cXKTLEyr+9X73+1UHRT+E+uvDfjy28QslyrLtltfs8SfP8rM6b/93Zvr2W1e2eze58qN
                            7iLbtdPk2/JsdH/2vuV8UeDfFln9ot4oN1m8qeU3+zL/AAS7/wD2T/Yr3r4deIbm5s4mnl33Hms7
                            Q7t7/LsR3/3fmVt9eZWpn0NKUZxO4mSzs9NS8ZpLO7s2ZoHt13u0q/Omz/ZdPl/4HWqmvWdn4ced
                            YGm1Dz1uLqa3X/l3370TZv8A7nysj0+/htprfbcxec8u66tXh+TazJsRNn+/VjTUg8By2WrtfWkL
                            +b9ivtPmXfLE3/LKX/aWuaPxFy+E3de8Zrf61rEuh6fP4bu7qWJ7VIV+eL91vi+df77712VyXjzd
                            r2vS3k9ysMq6EtxdWKslrL9oZ3TZ/wCObm/u/JXR6rr2h6Csuq2199s1u4s1t4LTc/2eJlT5HeX+
                            H7j7t/zf3KxH8PLrFrqatbN/at/5Fw0182x7VvN3yxbv7z7/AJf4f4f7ldPMc/LE5238QwW2uaZE
                            ulabr0sXh26e8tLGDZF9l2P+9l/i8+LfF86feryn4heesej6bbT/AGDRNJilvdiStK8Xz7YpZdz/
                            AOvf7tdn4/vIPCVxrGlT+RpXiX+x5dKbZE+yW3837Rv3r8250Tau/wC9vrkbm8s9euIvENzpUGm/
                            b1itZ7GG8eJJV37IkRNnzOjojM/8NbHLI8t8SfY9P0bUNPZbu8S8vorpdW3Om3amzY8TfxLvf56x
                            fEPiCPxJpMo1lZ7/AMS2rxRRXat+5a1Vf4/4mZPkVf8AZauo+IOg6x/wi1rrOqxxQ/6RLZ3m+TbN
                            u3/I/lN95fl+8i/+hV5ykzabqzRrGt/DFu2u67fNXdt/irspnm1zLvoYobewkglV3aL5lRfutuqg
                            m2FvmXf/AMCre1LTYH8RXFnBLF5LTtFFN82xa59kaF2+7u+638VXE4Je6Qs2/wD3aZUjP/s7W/vU
                            n3q2MSaazlhWJmX5ZV3r/u1t2EM8MqSxfPcRRb4k+/8A3v8A0GqlvF9qureO5kaGLzUid1/hX/7G
                            vQ9L8nwvrmpS6dHLqGnRefFZ3F5B8rbmaJfkbbuba6tt/haolI2jEow6LbX11pUS3DJaXE+2CW4+
                            Tz1Zf3rb2/208qvRfhvbb/E2leDNV8Sz+G7TdKu+ZpU8jc8Tu/lfdVXSJW/2l2Vyl3paaxHa6XaX
                            cmpRWF5LZwtd/ubeKJV3ebu+587b9ybvm+T+Jqjh8TX0erS+I9N+S6/dWUlxfKsu1JYnR/nb5vuo
                            u3+JVrGR6NP3T7k+Evj/AErwk1uukXy3j2eo/wBhWdjbt5tvLE3zvdb2+6srvu/4A+zdXqHjP4XS
                            +P7CXWbHzJtTV9l0nm7IpW/6Zf3d+yvjDwBrEXga3l0/XNKVEl05NVV7i5+eeJXR7d4n+T5Xd33P
                            /wABWvuL4FXN8nhnStK8VXcMNvE0VrFfWN19oSWJX3pv/wBr+H+/XKdvw+9E+WvE/wBuvLy90y6i
                            ttK0ywgZ9OsUiffatvTfvf8Auo7/ADf8DrjPH/g9fAfij+z7ae01u7274LiFd0X999if8D3fPX2h
                            8RfhF/wmGm6xq9nP5OoRXjKuoIuxPKX5N+z+Lf8A+yV8/wDibwr/AMIeuptZ3Mf2uWKKLTHuF33D
                            Ls/e/e/v1PLyl80ZHz5c3ly9lbtqcFjsZvss9pt8rzW3u/3F/hT+GsJ7yfT7hLOeBfsUt18tu6o7
                            xOqfI/8Au7/4K6XVdHtn1FNV1WWC/tIoN7JCz793z7H+X7vzpXFaleLYebfNYtDL5vmwXCNv3f8A
                            fVQEg1i4vtYunvNTvFv71lZIE837q/wfJ/sVyUlh9m1K4uWvINkS7P76St/cSuzh8QT+NpUtrnTb
                            GGVYGVntF2/Kqff/AOB/+Pfw0nhjxVp+j6ok9j4cgvLSKdbhbjVF+RmVP9VtX5dtbxJPO77S76aX
                            dLL5Nx8vy7tqLVx9Nn+yy2cU7Pb/APLWZ2+T7n/xdWfFWt/2xq1xfT20ULyts2fciX/dX+Gse+vr
                            y5VovtMn2Lb8zRK+z5f4K6Tlqe4Y+qwxWFwkSyrM6/edGrPmhZW2s2//AIFVh0+VVX+981V5gI/l
                            3b2/i+aqiebKX8xXV1X+HNOVfvbaVEVm+Ztif3ttM/3a2OYJN38VG3dQybVo3fL/ALVADd1L5dHm
                            U2gB/wD6HTKcj7aTdQA75ttJuam0UATK/wAvzNQ27d92o/vvSszUF8xPs+Wmo+1fmo+/96h0Xd8r
                            b6gods+XctWd8H2VFWJvN3fM7VU+VPu/PR8q/e+egfNyjvJ2ruqa2SBmfz92z/Yqv5zfd+/UW4+l
                            MOaJY3q0v9xN3/fNJM6/dVvkqD+LdTdtURzC/epeNv8AtUyiggc77qbRTpHZvvUANooooAKd996b
                            TvmSgBfmdqdRt+Td/FRUljkT5vmp7w7GdaVPu/M1S+XUG0Y8w7dsZGWvY/h14k/0fymkZ3avHUTf
                            /wCy10fhPUv7Pv8A5t3zbWWsKkeaJ6VI+nbC/V2T73yr/wB9V0Vm6uibf4vnry/QdYWaJPmV/u76
                            7DTdV8lXVd2zb8uyuM7InV/b/szJt/2q3bC8XUk27md1X/vmuHe8a5iTbu+X/wAdrQ0HUvs15833
                            GbZVxJOrm0dluElZF+WrumpsuE3bX/8AQKZc6qvlblas/Tb9prh3X+Kuk5z1Dw3D8yM3+/Xq3htF
                            fZ81eOeHrxtyf98V6x4bvGRUb/gFRzEyPQIfkX/YrlPE8ypE/wDcrb/tD9z71x/ie83rsb563Mjx
                            Lx/ebPOb+D7i186eOXZ2+X/a3V7x45+8+7dXgXjP5fNoKkeM69Hvuv7+9v4K5LUm2b9v/oNdbqsL
                            +a7f79cbqr+Tv/2v9mgzqfCYTNuZtvSmUrUldB5YUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUU
                            AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA
                            UUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABR
                            RRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFF
                            FABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUU
                            AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABT12/8Cof/AFlEaszLtqgPqX9iH4ev4h8eW+oy
                            q2yJvl/4DX61WdmtjpsUS/3a+Nf2Cfh7/Y/hm0vGi/eyrvZ6+0LlGf5V+5XnSlzHsUvdjyjLO23y
                            u38G6ugS5XTdLllb5N1VLa28mLbWb45v/semuu77q0gl78jzzxh4kW8vHb+7Xnl5qrPcS7fuN8ny
                            U3WL9ry6ZVZneX7zf3aqTKtna7m+TatQdkY8pzXifWPJXylbe7LXj/i28i3Oy7f/AIqu48VXjTeb
                            tbfLu+Z//ia8f8T6kr+azMv+5/dX+5Um5xPiqZX3szfe+7XmviG/372X/wAcruNe2zLK2/51rzfW
                            5lhif7rv/fq4mOpylw/nSfdX+9977tZv+03z1auXV5t27fVKuyJ5Nb3h6NsbbRtVlof733ad839+
                            mRqCfcp/3PvUJ/H8tG/5aUjaJNbTPDKki/fVty16voviSe4W41rRbn7BqFrZt9qt3b/W73RX2f7+
                            +vIq09N1i501pfLdkilXyn/2l/uVEoxmdlOp7I+4vAfxC0H4hW9uljJJYanFA2xHb+6n/wAUr090
                            azlRdVaCbTJV+ZH+/uaXdv3fw/8AA6+T/h14wXw/rtpOzyQ3SKsUWx9ifcbZub/gVfWHhjx/ba94
                            VhVrG2v3lgW6uoZm3v8Ac+5v/u7/AJq8ipS5JHsU6kZnVareN4DvH09YoNVmlVdQbULhU+zy27J+
                            63p/Fs3vu2fernUs/Evj/wAEeMNXsdQtLC48r7bPsuv3rKqfJEn+46fKlZVz5+valp9jughR5WRX
                            f7nlMmx3dP8Ab/ylMttN0/wqtvFPc+TqDRXD3kKbHSJdmxLjZ/3w3z7dqvupRkRKPKeZa9f3KXkP
                            9nz3P9oal5GoLqdxE8vzbPn+fYzMyOqr/d+as7VfEPiF10T+0Ly7023W6WWW4eXYkH8G94l+78/z
                            N8nzbK7C60fxLZ2GiXjanJYXdnPLZLdw7ZYtrRI6P/d273T/AHVevMtbmvLNtH1NpZEh1SJomuIZ
                            0luJVi+SV2/2fvbfu11QOaRV8Z6lbX2sS6vrkcc0t0qSyy2Mr77xWd/3uxvlVX2q2yuHudSs9Sh+
                            zpFsSKJbe2+b513Pvd3/AL1dDql5qTXKTqkslxD+6V7hWZJURd8SMv3fkX+H/bVq5a6s7KG4ilsb
                            xoYX2ytv+/E3935f96u6JwVCvq1j5N89qqyeb/B5ysu5t339rf3q59kEbfMv3fvKzV0GqarfNJ9m
                            vG86WBt/2hn3y/8Afe6sfZHeLuaXZcM23Ztq4nm1OUqRws+3b87f3a1rDTQ8d8j7fOiiZ0Vv7ysv
                            /su6ug8H+AdV8Q2Gu3VtEqW+mwRSz+cypt82VIovvf7T17L4T8IwaTZtqV5aWcyrpN59lt4Y98t1
                            PbIkrvt27tr7WXd/dfctHMXGn/Mc/wCBPBukLqni22udT+zWlhBdPFfSwbNzpFuiT+Jtrt/47vro
                            PDcOmeJ7/TXnefRNCsPDcv8Aat1qy71a/XzZUS3/AIlVt0SKqfNt+9X01pvwxk8PXVl4ivoLbxCv
                            jKC48PaVpN3EtvEs9rbu1u6P95lRE2tL/FWF8N/2ePF/i3w/aeFfEuhz6DcWeu2qf2hCqO8qqiIl
                            xv3/AOqdN+7733KJHSfJE2javfaPo8+r2a2GlapPLa2d3M+y3i8p91x8v3vk3/Nu/irPbQdOs9eu
                            GsrjUL/wlHcbGu1ieL7Yi7d6ru+Xe29vv/dr3fVPh7c6r8O/iKt8q6lZeCLrdBaWN5/okt/dXVxE
                            9xt/iVPs+7Z/t7a8ouL+w1CHTdMjhmg8OxWq2reU3kP9s+fddMife27tjf3lX+8tZcxry8x69+zv
                            8PtZ/aA8aSyrFPrGn+F9Oiaf+0J1m821i/e2luqf3UVWXan3v+BV+g3wc8Jf8U5o+tT2en63qF5a
                            /wBq2d9Cro8tvLs2RJu/ufIvz18m/sl3ltceKode8P8A2TRNPg1G81DUdJt2e3e1lbZb2lvv/iia
                            Le23+6z19z+A9S1Wz03VbPV57nWNbTUf+JjcRRPb2lnFs81Esl/jiSL+595qqPKTKUjE8Q6bqFz4
                            dvdP1OPZpUWop5E2mK7yt8//AC1b7zbH/hSvPbnwTBc3Fxobfadb12JWupb64sXe3s2nuH2RJ/e2
                            J/vfL9+vpiZ4JrVPIl2XtxB9ntkmifYzf7e37srpXJabZ/abyyn1pWe7tby4ls7fc8ssX+/t+X5P
                            /Z6iUQjUPhfx/wDs969o+g3EVyt3ClxP5sVvDB87Lsffv2/d/wBj+7Xi9r8O3stcfTde0+7fRVs3
                            vbm3t5UWVtvzJuf+6/3WWv13ms0uVSxa2ivGln2Nb3C7/KiXZ5u+VfuvtfdsrxT4peAfCfibwrrV
                            39ph8PXunX62XnX25k27tvlbF/1rbWRk/wB+olTLjiZH5bXOivqUt3PZx2mm+bO8Vrab/uxL9xPl
                            +8qO3364nVPIfzUubm5muLd/K3xfJEv+3t/ir7w+LX7Ger6bdP8A2VeWM1ltaWJLvZb3Crsd32bf
                            9xP46+T/ABD8NLzwrY3F9faR51p9s/s9tQeVLiXzdn3IkX+L/wAdqOWUTp5oyPFdbmnvLxFuVaG3
                            b7r7fvf7dV2fybDyGnuU+b/j327N1dxqnhPWNP8AFT2kGmNqV9EjtFYv+9eJPnf5P9z71cY+j+cz
                            3Mk6+bKzM1ui75V+f+5W0ZHNIxJv3nyxLsXd/e+SqDrsbbu+WtW8bZsii+5F8yv/AHl/vVFdWH2G
                            VY5JF+aJZdyfNW0TzanvGYvzLtpHTbVm6SJrhvIb91/DvpjwyKvmsvyM33q2OYhd91NoooAKKKKA
                            CiiigAooooAePm/i20n8VNpyPtoAfIy7V20ym0UAP2r/AHqNq/3qZRQA7+Km0UUAO3NRTaKACiii
                            gCaaFoW+Zlaoaf8A+h0fd/ioATa1N/ipd1G6gByr/d+9Q8ZRtrfep+5VX5Wbn71M37m3N96gB/8A
                            vf3altvu7ai/3v7tT2yqq7qmRtT96QP91FqZPuotRK37z5vkp39zdWUjriPT/Z/hqdXZGRvmSlXa
                            jLtX/gLrTkTd9751rM6onpfg/Xonii3f7lekWF4skSbf9n+KvB9KuVs2Rm+R2+7XqXh7Ut6puZfv
                            1xSj7x0xPS9Nk3L/AHPl+/VjesMvy/P82+sKwv0/i/i+Ra0Huf7rL83+3QaHRWd4syuv3K27BFSX
                            b9x2bfXCW1/80XzfO9dhol4s2xvv1cZGcj1Pw8+xVX+989ekaVfqnlKn8Pz15PoN4qKm3/c/4BXZ
                            6bqSx7Nrf7damMonov2/evzNvrC1u5+0r8q/7FVLbVYnVP43apX/AH0W5vuVpExPJfFVgzrKzfO/
                            +9XhPjmz8nzV2/e3V9LeM7bZZv8A36+d/H6N+9Vfv1oXI8J1tFRX+6j157qrr/e3vXe+J/3csv8A
                            fb5NledawjI+5v71NHNU+EyG+8aSlb7xpK3PNCiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAe1bXg/TTqniPT7Xbv82Vaxf4q9Q/Z70M618TtJXb
                            vSKXe1FT4TelHmkfrl+zf4bXRPBGnxKuzbAqfdr2VYd7fd31yXw/sP7N8P2USrs/dfcruLNP3W6u
                            CJ6kh6/O3yrsryT4u+IVtneL+9Xrr/ubN5V/3Fr5X+NOvedrLwLP86/e/wBmiQU4++YSaqu7zd2/
                            /b/u1ia3rEtzHKq/c/v/AN5azba83K7bm8paqalqSrFKq7t3/jm2sT0Dn/ENysNuq7t7srf8BrxT
                            xPf/AGm4uPm3/NXoHiTUm2yszfw15Fqtyvmv82zc38dREUjE1a82LKrV574hdv8A2T71dVrc29n2
                            /I6/364rWJt/y/7VbwMZGI8O/fVfZ/eqy7bFbb81VvMrrPKqfEN3ZqWOmbNtSJ/raYRHfep1FN8y
                            oNgp38PzUUVAC/c/+J3V7v8ACvW5dP8AD9xc2zRvd28qps3bd1v5W9/vV4QjKku7bv8A4ttaEOqT
                            21u8ETSwxN/cbbu/3v8AgNKpHnNqdX2R9v8AhKHT9SsJdcnuYJrS427bd23v9x32J/s/JXOvqun2
                            0XlXNjsS8ilt53T97+6Z/klT+Ld8qLsd68n+CPxKg037VbavKv2LynRXdmd1Zt3z7f7vz17A9/Fq
                            S2jNLH5SstvA6fcZV+fe+3+He/8A45XlVIyhI96Mo1o8xyNzqVnpX2SK5vruHTLD91smV9kvmo77
                            0T+9sTaz/wC5XmOpQ6Db2kEGn6lJM8sksqrcQbNrbdro3+y6/wDj1eg+KraeHRr2K5W5/tD7d9oa
                            Z13pt+dERH/4C/8A33Xn99NpF/Fb6ha6VO+q3UvleUzf6OnyfJKv8TN8u7ZXTSOar7hz0+vanaiV
                            dzQ+WqrKjN/d+4+7+9/tfe+Ssm+s1m3qkapcbFT5v4l2K27/AHq22vn8SSWkbTRvLKywSJt2uzM+
                            1JV/9B/2apWtjf8AiK4t7axgaa6t4mmZy6Km1P4vm+X5f4v71dtM8ypI5a5t1kiiWP7/APy0T+9/
                            tV3Hwx+HF54m1ZZJ4Z3so2XzWhXc/wA393/a27n/AO+P71ejfCb4IeIfFtnfQW2hx3Nxq0sUMF9N
                            LtlsIt+6W4RW/v8A3NrfNX3p4V+CsXhv4c7tNllvNd0aW6/sdP7OT7R/rfKt0dP4l3xOzP8A+y1Z
                            z8sfiPnL4e/s0nxna+P7G1ub7RNClR7XT5tUgT7XLFBtuH81Pu7NyfL/ALO2vevCXgPT/En/AAhW
                            uW2tQw6FL9ltYtTu4EdL/wA3fFb2uz5Pl++3/AEr02xsbbxl4Bv9O8TaddTa7onlaPrUWk/ure/W
                            6eL7RLay/wASfwt/Eqo9d8/w3gs9Y0m+/sG2udE8F7pdAsbS8dLSJmREid4vutsTdtf5tuz5aCJS
                            Ldt4A0izi0fwxY2f/FP6NFFqVj+63vao0X2fyk3fNu/irx/xd4M8UfC74pXvj9/FH/FL2ETWunWk
                            0+xF3p86bPu/JL82x/8Adr3XRNY1y/0TWLm5nudmpSvf2qXESpLaxbPkT5fvV8k/tYa2reF/DGn2
                            15JDLf3V/ZNp0sTo95KsvmxSxI38e91Vv9rfWdSRtQjzS5T5d+IVxBr1nrus6Lp0L6JpF0v26bdE
                            qRXU8ryxf8Adt7/xfN8tcLoniqa48QaVe6vocGsW9hY3UTRW6Jtbz/tHlXUrIv3klut/8K/In92o
                            LPR7jV4PEUeo6hc6JZeZL9ucRyywtdRJ+6tdn3d7Syy7d/8AD92vbP2UfhrpvjrVrqTSPIv9asLV
                            LTU0vtkSSyzyxf6qL+JIvK2u2z+5WUT0pcsYnvH7JfwN1LwZ4N8VtfW2l397eQRRWF9Cvmu0uz59
                            i/x/99f36+kNN02xm1zU7m2vL6w0+XdLfbLqV/se3yv9V/dV9n8H8O+uo8JWNnpNhcaVBY/utLtV
                            82F4NkW7Y+xIn/i3/erlLzSrzSrDw/plrp99oj3EUrtrNjE72Nm38CbP4l+d9qP/ABVXLynmylzS
                            Oj0/Up0tfL1Wdry4+yxXss0UX7pf3SJ+63J97cj/AHK0PD1nea3dWUFzqH2/7Yn22eZF8rcqf6p/
                            97+FqwfBOj+I7+LT9M1rV7TUvsC/aonhiaKWX59ifJ/sV6b4flsdL8PW9zaP/okSs880q/w/P/e+
                            7W0YmMpcpw/xG8P32vaQ/hPwd4mXwr4i1ZVuIte+/LOsWxJX2/xNs8pa5rXvGeja9E7XMTWD27f2
                            fYzahF9ne6v2R4vNRG+98ifL/e31S+Jfi1PiFr2haDpEt9YaFcbdXg8SaPOnzJ8n+jo/8MTvt3P9
                            35NteA/tUWt54q8baF4h8Q61puifD/whdWsTanC73V3Ldb/N3oi/eZ2RPm/2HqJS/lKjH+Y6HUvD
                            1jo/wx8V6r4l1691W316L+zdT1a7bypftkUqeVaxJ/ufxp/crzb9tjxhaeGNB8G6DoPhix0rxLb6
                            dFe6ijRfvYpWi+RNn9//AMe/uUfFrXNF0fVvhF4ssb5db0fWYLjxFeWlxv8As/nwSxP9oSL+HfE8
                            tHir4XaV4m1L4gfH74kanaeLIpYPsWk6DYxfupbqWLZapv3/ADNFvT/dZKj3uU0j/Mcv8KfgDP8A
                            E7xRpVzLr1p4YuLDSpdU8Q3Fuzyy2cXlbN+7ftVpfmb/AL7rxXwf4B0Xx58aPHH/AAg9tqFz4U02
                            CW4i1nVk8pLe3WJNju/3Vd337F/irE+Ffxy8R+DPAvjvwFYz2kP/AAkDxLfatcfPceUqbPK37/u1
                            xWk+KtV8P/274KbxjJbeFdenSXUXtPkt7ryon2bv++lq4hLmMW68Gal4k8C+KvGzXNlZ2thf2trd
                            WifJLLLPvf5E/upsrC8Mxae3ifTJNcjlv9PllXdbxP8APKu9k2bv4a7D4b+D7r4meMtK0GxubS0l
                            1a7+z775vKhiZfmTezf7O/8A4Cu2sTxZoem+F/HmtaVe3S3kVi0tut3pbboZZV+60X+zuVq0MZRO
                            f8WTWM2oXbwWn2CXz3T7On3ItrP8n/oNc4zttT5t6L92tDVZoprpHikabdEvmt/EzfxU26uIZd8c
                            EHytt2s/zP8AdrWJwS94y9lHl1N5LOu5f/Qaib67qsgRE3U2nOm2lVtu7/2agBlLtq1Nb+Ts/eK+
                            5d3yt92n3Cxxyrtn85Nv8K7f+A0AUttJWm0dothbskrfa2ZvNTb8qrWa1ACum2m0+b71MoAKKKKA
                            CiiigAooooAKKKKACiiigAooooAKKc77qX5fmoANm/7tJJSr9xqZQA9/vfjVhP7235KrVN97ZUyN
                            KZY/4F8lO+bdUSOtS/7dYnXAton3P4P4at20Lbv/AGeq9tN8v9//AIDV2zf5tzbUTd9ysJHfAt21
                            s7/7e3/x2uw8PXjQ7Vbb8v3q5y2+9/fStO2mVG+ZaxkbRPUNKuVdfl2u+6tXzv8AviuH0HVVRdu7
                            /gaV1ENz5y/K3/fdYj1NNHVPn/j3b1St3StS8lkX5vvVyiXW+XdV7SrxUuImb7n36srlPYNEv1Rk
                            bd/47XYabfr93dsdq8v0rUFRd1dRpUzTMn8b/K/yVYz1LTf33y7t9dNDDstf9uuS8Lp8qfNXW+ds
                            t0Zf7vzVtE5ZHGeM032r7v8A9mvnT4i7UW4/3a+hvGc3+i3Cr/dr5s+I1zvidfv7v/Ha3MZHhXiR
                            N8srbv3X+xXnmqzJtb++38Neh+IX2XDxL8/y15lqi4um/wBpaqJjU+EzWpKl3/3lpv3vu1seaMoo
                            ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiii
                            gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKA
                            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
                            KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoo
                            ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAH7vm
                            r6Q/Yr0ddV+J0UjLv27Ur5vT7tfYX7AemrN4rln27/mqKnwnZhviP1Q8PWypYW6r/d+Wuo2bIkrE
                            8PJ+6i/2FrppoV2xKrVzHZU+I5/xbqH9m6N8zbPlr488c3P2zVLidm+fdvr6N+N+vf2bpe3d96vk
                            LW9Sa5ll3M3zN81Y1JHZQj9oi+2fvflb5Pm/4FVHUrxUidf42Vt1YtzqrIyMzfw7Ko3N/wCdE7bv
                            /sqx947DnfEN4rxSruXZXmmqw/aV+X/xxq7XW3+071X5E/v7q4q/2or/ADLsX/aoOaRxuqp/pD7m
                            ZP8AfrkdVT5ty/c3V1ut3PzuzL/F8qVxuquyVpSIqGJJTE+69TTKyH5vvVXT5a7zyqnxEu/e1Hyv
                            TPLqZPloD4g+Zf8Aap2/5dtNp3zbag2DzKKPu0bv9n/x6oAETdRv+bdRHUX8NWBbtppbabdE2x69
                            7+G/xWjvNNsvD983kwsi2u/au/aqbnffXz4/8FWLWZoZUbeyJ9xmT+7WcqfObU68qUj640RJbbVN
                            TltrmRIr+BrdZkVJfm+R0d0ZH27Pu70/22rgtVv/ALNrmq7bSCa9iuvtFt5MCIkVwqbN7p86sr7v
                            uVy/gz4wXOlTwwXMf2lYomt4N/8AtIifP/3xXp9tcwQ3Fx9h2unkL5vy7/7m93rk5ZRPS9pGqeKw
                            293Y6tdbraKa4V5UX902xm+dtm1f4t+3bX0z+zv+yXqXjCO417xBo+oPo9vdNa/2fErxO0u9Pu7X
                            +X/aX5v4/mrD+HXwl/4T/wCI1uqq32KXVre1nm3O7srP+9/4Dsd6/SXwH8NLHw3pdlZ208+j2Wl3
                            Su1jaXT+VLvT5Pn/AL3zV0ROCt7pU8AfC218JeGrfw+sGlw6hpc7NBd28SpLLuTaibmTdtRfl/4B
                            Wtquj6ho9nb22mywTeILWJpbO4vl+0easV07/O/97Y//AI/XS3M2mXMt7c226/1PQV+2sifukl+R
                            /Ki3/wB6uH8Nw23iTwf4X1C51PUPKls7rVbx3n+0PLLLKiJE7r/wNV2f3K01OYt6bbRTbPFV00mg
                            3fkS3E+jbn+yS3TbIv3u7/vnZ/t7q0Lz7TZ6ykXh6Bb/AEfTdJlS6+zyu7ttT91ap/e3vvX/AGdl
                            av2O5fXIl0rQ59Viup4ri8vtQl3Jp0Sp8nyt95/4tlS+LfAes/8ACK3Hhrwvri6PcSeVdLq25Xu4
                            oluEllleLZ829l+X/Z30ake0iQeJ/DN54yvPP8PX1tpr2cTafa6h/wAtbC/aXZcIifd/1Xy18I/t
                            OeLbr46/D/4f+KoLaDSoZb+4srrUL6XzfKaeWX7L5X8TRbYvvp95q+xfEerWq/EbTdeW+nhuLzT7
                            i40rwzFP5Xmqqfvbi6Vf7/8An71fM+i+KfAuifErSr7W7XRNY8K+HNC0nw7a6fc+bFL9nWKJ21JU
                            2bXl8+4uIl/3H+7WdQ2py5fePmuZbjxB/bHhfwBJrGvfD/TtYTVZVsYke+lliWKL7R/tLtT5Vbd/
                            e2/xV+jXwT+CPgvQbe18Z23g658Mahq1m7RafqCp9ot237fNl2/32+b/AIHXyL+yX8PbvxJ8VLrU
                            549UsPCHh+8v9aglhbyr2/8AKuPs6W6f9Mk/i+b73y1+mTakqWsUq7YYtn7+Fmd5fKZPk+b+L+Cr
                            px+1IutL7MTH1u2a/wBUt5Vi1BImtbiyW3hndImiZE3u6f3v7j06w8PPbX12uo6nJc6ZKq28SStv
                            8qL+NJW/ib7lNvJl1K4vX8+5heWWKWfyWR9yxfL5S/3d/wDFWfZ+MJ7b4oeFNBaOGa01mK/uPJi+
                            WWJYk/1sqfwr9xP950rb7Rx/ZO4toYtH0uVvI/0iL91Bbw/xf7CV5v8AHjxhp/hvw7p+n61cx2fg
                            /Wbr+xdWe3fZcK06bUiTb9373zf7Nelaxcz6b4YlnuYFubiwg3RS/ceWX+6tfP8A+0J4VtNYfT9V
                            udBW5fTtTsHtdL+07Lee/n+/LLu+X5F2L/33Vy+EKfvy944y/wDCsXhn4ua7PFpen3Phzw54UXSL
                            XQYZWiisLVn81ZZUX+F9m7Z/uV8+/tPQ33xQ8EeDfD3hq00/SvCi6ct1Z6fYzvcbZ3+bfP8Axeb8
                            ku1Pm2rXsXiTW7PTdY+LWvW3iP8Asp5ft+land2K+al/KqRRW9rbo38MS/Kzp81fIek+EtV+DS/D
                            W+ttX87xL4slivVsYWffYWsXyOmz5trOryt86fJsrhkd0fi5j0/SvjNY/D3xHo/iHTIFuddvNHl0
                            28fWIv8AQWbYivb2sSfLFEi/M2x/4P8Ab+XwP4hW/iXwx4suNEg8S3evaPC/naZFDct9lZ33bJdr
                            fLu+bbu+9935q7X9rb4r+Htb8QafpXgVWsPCvhXyrTTtPSD/AFrvv82V2/i837u6tLwJ8MdD8G/t
                            SeD/AAV8Ybqx1LRf7Puv7Tcyf6JFK1k8sSeaj/fRttXyl83L7x4Frng208Kw28888X2uWBIp4Un3
                            zNKz7nl2/wC46baw/wDhG5fGfiK4g0WGa/uFiVIrNP8AXN8js/8AvbNu5mq14m8T6n4S8Uabr1jd
                            Lcv5Gy1+1oku2LZsRXX+Jtv8VchovjLU/DF5DqGlX0tvepL5v2iFtjo3zr97/aWrjH7RzSqcvum/
                            J4otLHwXqOhDQVGqvqf219Ullb7QsSpsWL/gL72Zv71cFcyxSWtuEX/SF3eau2vQvBuq+D7zRfHU
                            Hi6zu9S1y8s1fQtTik2+RdLLudpV/iV1dv8AviuF12xtrO6Vbafzl2Lubd/s1rE5KnNKPumhdeJp
                            bnwlY6I1haCGyuZbhbjyv3rbtvyO/wDEq/8As9YV9G0N0Vbbu2fwf7tF5NBMtusUDQui7ZW3bt7f
                            3qpq+/71bHNzHonhubwc3w/8XDV4JJvEu21i0hvN2+V8/wC9+XbXA3O3zW2t8u5q1tB8L33iGG6e
                            xiV1s7ZrqXc38G7bWIybGZW3bv7tAEfmVZtoZbqVI4FZ5W+RUT7zVV3Vds7yWwuorm2bZLEyujr/
                            AAtQQaeqpBNrHlWls1h91Ghmb7rfdb71UVii03VPKuV86KKX5kRvvVNq73N1fvPcyrNLL+9eVfm3
                            bmqjbTNDMkq7WZW/j+5QAy4ZZpHdF2IzfKlV6t3VtHbsm2RZlZd3y/w1XZv4f4aAEd91NpyJuptA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFS/epklKlBcRyPtq0jq/+xVVXZKej/wAX
                            8VRKJcZGlDN8u75U2/7NXrX59lZls/8Ae/8A2at2r7JP9isjvjI6Czf/AIG/8NaVm6uvzMtc/Zzf
                            xLWhbzfNub5Pm/hrCUTsjI6bTd27+5/d+auws7nYuxvvt/frh7C82Km37+779bVncb2+Zq5jaJ10
                            MyzL/sVahmVJ9q7v9msVHZFfdR9pZ5fvNsX+OoNjuNK1TZ/H8+5dr16B4Xv1mZHZtn3U/wB6vHLO
                            Z9yfx/79d74Yv9mxd3+3RIOU9+8PXLbdv3N1dRNefutqt/t15z4e1L5U2/3a7NJt0W7+DbXTGRzS
                            icp4zmb7O6/x14F42habcu3Z/wCy19AeJ5lmidV2/MrPXiXiS2Z/vLv3LXUc3KeA+JLBkuJW+/8A
                            /E1wWq6b/Eq7K9o1vR9++Jl+/wDJXGX/AIbldtqr8n8VBB5u+lS7dy/3apTWEsP3l2V3r6LvZ9ys
                            iKtUrmzVEdNv+w3y1XMYypxkcQybdtMat+601V+b+BW2fJVd7PZF/qmo9oYyoGRspKsvb/NULpsa
                            tOY55U5R+IiopWpKozCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            Af8A3q+5f+Cftttv9y/O+7f/AOP18M/xV+gH/BPqzV5Ub+PatY1Dvw3xH6V+Hof3MStXR3KeT839
                            2szR4dlujN/dqxqs2yzdlrLU2qfGfNX7RuvRJL5Hm7K+ZLy5+0xbl3fe+/Xpv7Qmqy3ms3Cs3ybv
                            l/2a8VS/ZFVWZkVvupXFU+I9ilH3Qv8A9yvzNvf5XqpeX6zNsVdiKv8A31V68eC5Xa3zutcjf3P2
                            Zn8pdifd/v0FyMzVn3s67q4rVrZpt+1d9dXfzbNjL86ffrlNSvJXZ9tBze6cZrdtLu+X7n8WyuP1
                            Kb5nVl+euw1u5V4nXb8/9+uNvI/nbb/Cv/A62p/EY1fhMpn3Nijf/DQw2tSIldp5vvD6fTKlpSLi
                            FN+7Tv4Uaj7tSWFN8yn/AN7+Cmfw/NQHwjvvL97ZRS/xf9MqSOgBvzUxkbbT2+T7tM3/ADfNuqyJ
                            AsjKy7a67wH4yvPD+vW8guWSKVlSXzW+Tbu/jrkX+7Wjpdm+o30MEUc8zO3ypbrulb5f4Vo+yHNK
                            Mj9d/wBjnw3pV59olgs45ns2Xc7r8jbk+R6+vZNK8m38i5VXSWX7V5O35938deGfsl+D4/A3wJ0T
                            TGsZEivJ/tU/7198TTpvff8Axbk/3ttey6pa7p7i7itr52is4ni+zyfvZWeX5vnb+9/ElKMQqS5p
                            FW4e2bxA9zPPbQ3EsX2Jrd/4riJN/wBz+JvKeqvhvTf7N0aLSrNbZNKaVfstu8Xzxffl2f73mvU9
                            9a/21Pbz2N1CuoRX0v76ZdnlL/y1T+Ld/Av3l+596ugutat9DuNPgvId+oXk7RWyRLuWX5Xlbeyp
                            8u2JN3/fFMy1Mrx14f1K18Ly6DoMkr3F/K17eXzNv8qJXRpdn+0/3VWvDPihpuq+G/iR4g8apqcc
                            Piuz8H7dH8M6Yvm7rCJHeVJXb5fnf7rf9Mq2PiZ8SvFkPi7wDqtzpV3pXhXTVutQ8UX0VzFbp5S7
                            0sopUd93lea6sy/e+5XEeLdE1DR/FGnr4guo/EPijWYl0/xJd6Nay+bdWd48qJbojSu1rBbxPK38
                            TN96lI0jGRw/j7xVqujftNeMPiC0tp4b8JeH9HsNAnuL6Jbi4uonX5Ht4v8Anlvfd/tbK+cks5k+
                            K174SvNV03xJpVreWXh3QnmX9zdXUX/Hu+7/AJ5I7y7v9p3+au7+OnjCT4M+AfAtrfeFNNhur+8v
                            /EU+k6hI7v8AYYG+y6ZDLtlZv9V5Uu19vzJt+X5tvjnjrTfEHjzxBoOmeJdf0Lw9oms6c/izTr6K
                            BH8qK8upX2OqfdZ5Xf8Adbm2Vzy5jtjy8p94/sx2Gn6p4Q/4R/Rrm516Hw+1/wCEL6+SVESXbKl1
                            LcRN/Fvldt3+ztr6R1LW4raWKdYpIYtyxN5K+a/73Z/3yqP956+DP2LfG19puseDLbQfCN3YeDPC
                            q39lrvibzfNt7h2TfLK3yfxysu3/AGU/4DX1B45+Jy+HpdK1C+ljSyv/ALPZWf8AZ8UsssVxLL/o
                            7+V97ynSKVm/veUnyVXMcsqcuY9Nm0qzXWLiRbuOz1Owlt5Z7h5fkaJX3/Kn/AnrQ0vR9B8P+JNd
                            8VbobbULral1fXbfPFbr/Au77q/xVwFzDeW32LTNV0XT7+G/llT7RYxfZ0it1dJYk++zbZXT5v8A
                            2amWfj+O68K6JL4h0axTWtevJbVoUnS9t3l8qX5lli/gRFdfnT+OjmMpRIbDxhp/xa8K/D3xfqt1
                            c6VaajLFLoehvc7HvLqXfseVP+WuyJt+3/gVeC/tk33iH4r+E/D/AIc8IKt/aXWuz+bfW91/pEt/
                            Yfutm3/YZP8Avqtr4o+OLyw+Mnwl0zw/odzqVxoOlXSzvaReVFYJPsieWL/lk7RLF93du+f5Wrh/
                            H+var8H9c8C+HPh9Z6lretWviK4stV17UIIrhPNnf7Qib12L5qJKjN92olI6KdP7R578fdS1ia18
                            H/Dvwt4Y+zalpKr4i8SJbokX2+8iRHu97/7v3v8AprVfQfiRqXizXvi78WNM03TbC31bweqSJ5Sy
                            /wBjRM6W8Tqv3d77H+VKo+KtD8I+Bvixrvijxd4m8UeOYdWi1m6W0sbeKytLiVLpdnmvv+aJ9m9/
                            K2/cT+H5W8bh8H6nZ28y6/q8fhXR/Efhu61/R4UlZYp18390kqfL8r/Oi79zfJu2/PSNvdHaFquk
                            eE/gV4i8I6fZz+IfE/jTVrCK1uvL3Mq2250RP4ld2l/76f8A2a81tl0rxB4N1tdevryHxnFqMXkf
                            aN7bot/713dvusldRpvjbSPgf8dtC8T+F1s/Ftv4f8q9tVvI28qWfyn3u3z7vklbdu/2N1eZeL/E
                            aeJNel1iWCNJLyWW6um+8ss7vvlf+H+Jvu/3a1iZSMHUFl1T7QrNPN9j2oqou9ViX5a774P+DfB+
                            vaT47vvGesNo81noUt1oVom5Pt95v/dIv+z8teaX+vT391dS7Y4WuF+Zbddq1d1vxhfaxFpts0rJ
                            FpsX2e13ffiT+7WxwSlGUuYjh1iTRVvbW0kWaK8gWKVmTd/tfL/wKs65vPPuN3lRwqyqu1F+Sr2o
                            abd2sFleT20kdveK0sD+UypKu90d0/3XR1/4BWT537plZV3s27fVGMpFdm+ajd81MoqyDTs7+6s1
                            uIoJ2RLiLypVVvvr/cqk7+c25v8Avqrum38+l3STwbUfb/Gvy1nyM0jMzdaAEdNtHmU2igDb0XzH
                            t9QjiWL5oPmaX7//AAGs+2umt5Nyqr/Ls+aq/wD47T49vmKrfIv8VACJMyMrL/DS3EzXMzSP95qR
                            1Xd8tTKjwskjx/I33d6/eoAEhZLfz1ZfvbdtVpKvTWbJAk6hni3bG+X7r/3aspN5zWrXsDfZdrKn
                            krt3UAVNNsHvrqKBWVGl+6z1XkXy5GVv4flpzpsZ1+b5fu1NeWbWyxM0iv5q7/lb7tAFGinfLTaA
                            CiiigAooooAKKKKACiiigAooooAKKKKACiiigB6v/ep0dRU9f/HaAJ0fZ/6HV62m3/xf8BrNSTb/
                            AMCXbU8L7G2ttrKUTaMjbtpv7u2tK2mZ4fnbYm6uftvk2bW+9WtbTfL/AH13VyyPVidBZvs2fN92
                            tW2fZL8rfI39+uftX2bV/g/uVsW02zZu+esZHTE6u2uWddu5qsb9n3m+7VGzf5U+VamdGT5W2/L/
                            ALNYnTGJpWFz8yfxpXV6JeeTcJub71cPZ3ip95d6ff8A/H66DTbzZKm3b/cqTaJ714VvP3SNu2fL
                            XfW1yz2qbW/4HXjXhXVZfs6Lv+dtteoaPM0y/wC38tdEZHNUiGqw/afvfPXn+q6PvV9y/wAXy/7t
                            esf2b52/+59+s++0FZF81VVE210xOOR4Df6Cv3tu/wDz9+uS1jRPm+XaiV7nqvh5kb73yNXI6l4V
                            3q+3+KtBHiupaP8A7Pz7f7tc/c6JsavWtY0HYz/d3rXJXln839zbWfMB5veaV8qMy1j3Nrs3/Lvd
                            fmrvdVsNivtX591cff23k79vyU9SZRlE5i5mVkVt2xl3LtrPuX/4H/tVYvj++/uf7tV2XetaxOOp
                            73ulSinSUR1scA2iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAdX6
                            F/8ABPd/mi3f3Vr89f71fof/AME94flib5dm2sah3Yb4j9MNK/49/lo8QusOly7m2VNpSL5P+21Z
                            Pj+8+zeHLhv4/KauU6Ptnwb8b9YiufEd2q/f83/4uvH3meaXcv3F+StD4pa8z+KrvdudPNrE025+
                            0q7t97dXIeui7N88T7mb+L/frn7yFpvmVWf+98v3q1pt27d83zbqzHhlmuNq/O7UF1PgOS1K5aFk
                            ib5P9iuX1vUti7V27/mrpfFVt9jbcm3zVrz3W5mmldv+AVZyamZfzedv2/cX7tc9ePsWX/aq3qTy
                            pu3NWLczfNXTSiYV5e6Mf5qI6YiU+uo4Ij5KN/yvR/vfdoRPmqDYPMooTbt/26dQAJ/tfw0f3qX7
                            y0lBEv5Q+9Tf+BUz+GpnTYtBYx0pn8NElCx/3qsiQGvSfgj4HvPiF8SPDmjxKz295qdvbzy27/PF
                            Ez/O/wDe+VN1ec7PmSvrv/gnr4AtvEX7QuhanbMtzFoMEuq3Uzv5UUH8ESf3mbe1QH2uY/X3T9Ns
                            9EsLfSNMSRIorXYu/wC58qfx/wDjlM8Q6ta+G9G0/V9Vvl0fSrVd99fXH3FX+NH/ALqv/frM8W+J
                            LbQfBGu68ytMmjQXF1PC7bInVU3u6P8A3a5/436Drnir4b+INM0/yfteuRfYpZriXZDYRfxyr/tf
                            PQRy+97x3t5Jpnh+10qe5vvJ0+4lW1i2L8krt8yO7/7X3q8E+JHj7TNP0+Hxb/wlS2Hhrwr43ur3
                            Vb7zf3vmpZSxRWsS/dZXd/K/3Wrq/iV4j1Gz8G+HbPwtDDr+saXrdhFeRXfzRRbYlidmT/x7an8V
                            fNvxv1JPFvw0+I0lz4a+2Wl5Pcf2db3Fi6J9qV/sqS2qf3kt0+0N/wBdaqUuU1p0+eR0HxF+My/E
                            X4C674j1fQ5NE+2eErjWrPR7i6815ZYLqJEdv+mW+VP++K8/8W+ILbxR4q01LPWms9Yl0ywsLrSY
                            lT7XqMurS+Qmx9+791E0X+789fMT/GbxHc694gvIrnT5tK8R6Z/wjuowwwJElhZfJEiIjf6pd7o2
                            yorfxhrng2z0+fdY2FvYt5unS267L2V1TyovN+83+jq7sn8W75q5+Y6uXlOg8R+ELbxJ48+Jvg69
                            tpddvvB9neP/AMJfb3T+VL9lidd91ufakUronyp/F/erz7QbGDTdH0/V/EEEGveD9NWey32N15Uv
                            mypK8SbG+bbFKjy/c/v/AMNZHjyHU9HtVvra4u7SHVomuJ4Ud9ktr5v7p5f7yyv8y7v771j+ONe8
                            OxapoLeF9KkttHtdFtbW883en226+z/6VK3/AG1llT/dRKuPvGcpSifVXwZ+LnjHw38LW8J6bbQW
                            ej6TqNgktxb/ALpLr7ksr7vl3fupX3J/txV9W+KvG2o6Xrn9oaLbabrCaXZrt0RlS1iS1luIkt0l
                            Z/8AgG3Z9356/NL4b/Fy88Paf4fjuVjubSy1OXVdky/62dbX7P5X/A02f9819K+Fdb0H4heCEvp7
                            W8m1NfKvdTuJtRlSW6igeJHsov7u/wCT5P8AbrlqSlE6qcec+m/CXxFsfEkWoaYur32pW8rfYtR1
                            Z2e3dmb96/2d2/ufd2J96u7S80Hw34I1Pz9Sk0rQop4tKsbT7CiXFrcT/ukSL/bl3/f/ANuvnH4X
                            Xljc+I7eXSLO2v7TRoGuJ3u53lt4op3+SWX+LdFs273/APHa9L1vRNK1WXT4PFEt3f6xpN1b6vFq
                            ekr5VpqMux5/Ndd/yqjxbdr/APs9FOUgrUuU9N8SeJ4rPS7LUvIttKuFl8qCxuJUSWW6lTelvt/z
                            tr5n1jWl+GPiu41C2ae/0ez1VZX/ALTvvtCazrl1b/PFFF95l+dNrJ8qsm2u2+M2g6frfhnVbmxn
                            trx4pYr2C++yv/o7fJvlRPvM/wAjsmyvJPFXj7SvDfiC31W50q+vPEGk3jarY293p3lS2DbP9Hur
                            pG+7/sp/uVtIiMTy/wAZ+LV8E+A08PW2kNf+KL/Sb/QNYtNQV5bjTvPunldLdP7yJ5W5v/iK8q1r
                            xDqHxg8QaJp/jbVbg29nBFpsF9FBvdIoopfKTZ937/ytt/v7q9C8K291428QfErV/EuvW1pdxaVc
                            a5bajbqm+81SVovli3/7Lyt/s768i8Q+ILq/1R428+wa3ZUidlT91LLF877v7zqrfLUFnG6lIsLS
                            2KmOGXa3lNCfkXcnz/N/wH5q9F/ae/4Vr/wmH/FtY44fDtnp9rYK/wDHdTrF+9lfd/v/AMFVNY+E
                            EeifAPwz8Q7u7abVdW1q6tIrGb/nzgRNkvy/N80u5a8f1vxRc6xFZRT7UW1TykRF/hrpjE46ko/E
                            Y11N9pk3KqxfKqbVrV0Tw9feILyW2021a5uI4HuGSL+GJV3O/wA3+zWB9962bDUrvSpJZrSWeFtr
                            I80O5d27+Bq6TxzdvvHmp3+g6PpGoKtzp+k2ctrpysv+qWWV5X/3vnd64zf826rN5fyX8gZ9qbV2
                            qtQzIsbfK29KC5SIabT1+61MoIH7v+BU3dSUUAFPddu3jbTKXdQBaawnW3inZWFvK21XqGTZsTb9
                            /wDiqbzpJlSJmZ4lb5aiSFnbau1qAGLXoFzqV58RLHQtIgsbOF9IsWi81PlaVf77/wC1XP6ett/o
                            8VzG+xZG82WH5n2/w/8Aj1dRa/D/AFqbwfqHjWwtZYvC9ncrZNfM3/LVtvyL/wB9f+PVlKRtGmcJ
                            50kKyxN9xvvJu/irTudEns9FtNTeePypW2rEj/Ov+1Wgn9jLaM0kEk1xLGqq+7Yqtvbe3/fOyseS
                            2nmtfPZleJf4Epcxfs+Ubrg09p4msZJpt0S+b5q7f3v8dZO4f3asKi+U7N97+Gq3l1sYyiNopWpK
                            CAooooAKKKKACiiigAooooAKKKKACiiigAooooAKXdSUUAFWIXqBqkR6C4l2F9i7f71adnN86LWZ
                            bfd+9/FV62+dq5z0qfvG7ZzfvU/9nro7b/VIrfP/AMCrnLB97J8v3mroLb59nzbNvz1y1DvpnUaI
                            +/Z8v3f761tvYRPF5qs3zf8AjtYOlO2113N/8VXYab++iirjkdkTmLmzawuNrL8jL/B/DVqxmZLh
                            Nu77y/P/AHa6i50T7Tbu275NrfPXKXkMthL83ybW27/71BqeoeDNQ+ZN3z/79ew6Dc7/ALzf3d1f
                            PnhK82bF/i27N71714Mdbm3RW/i/8dq6Rz1T0bSrbzovmrQvNKV7eVW+T/YrS8PabviRtu/d/crY
                            udK2Kyr9+u+JwSkeVX+g+c3+wtcpr2j/AGNk/uf369gv9NW2i+Za838VSLt2r/D87U9QieO+IbZd
                            27av8Vef6rCqb2X+Hd/DXoviq5++y/7VeWeIbxvN3K33qzkbnL6q/wAr/L/e2vu+5XG38nzOq/xf
                            PXR6lcs6v/8AFVy1zJ9/d/D8lETOocveIz3Tqvz/ADfLVCaHbWr8s3m7v4W37qqXTqm/av8Au/7t
                            dMTjqR90zW+7TKd5lNrY8oKKc6baI6ADy6Kf/D8tM+7QA2iiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKAH/x1+hv/BP3cnlLt+9sr89P+W1feH/BP3VvJvIol/z89Y1Dswx+puibnVP9
                            2uP+MF55Phy7Vf8AnkyV1elXP+ipt/u/LXnnxvm8nwvd/wC7XNU+E7KfxH5lePH3+KLhvubZW/4F
                            9+q+m33krtT+L/0KrHjObfrN23+03/AaxLO8WGVIm+/9+uaJ6UvdOrebZa/NtR/vViTa1FZ3Dsu3
                            5f8Aa/iqxc36TbGVt+5a5rUofO3/AN/+KoGYnifWPt7Ou3523fPXD36bFdmrq7y22ea3zf79cVqt
                            y8LOv3/m+5VxIOf1V97JWY/ztWhqTtuT/drKZfmr0KfwnmV5e8PV/m+Wk37qf5Py7v4KbsVferMf
                            eHf3afH975qZT/8Alm9QbDpKa6U6jb8v3aADf/eopU+dXpP71ADf+A07e235lpv/AAKiSgAfclMp
                            8lMoAarfNX6cf8EwfBmg3mja7eNpF3NqEqxJPdzKqIyt8+z/AHf4v++K/MdW+av1X/4Jyw2Om/Ae
                            4ludMaHUJ9Ylt11ZJfuxbNz70/h2f3acjOJ9m+KPBsHjbSb3RbxbmG13WqtNM22KdFdH+zs/8avt
                            +at7WkePQ7dtTgskeWWL7Va7ml8rc/yIvyf3/wCNq5LfBpsN7rOlRX15cW8q3s9o8/zyxL8/7pG+
                            X59nypVTwxrfiW58EaPc3NtbP4zuLGwbWvtzeVF5vlI7o6fdZvv/AHKRMjgvGdz4qf4qf29qttDN
                            4ctdWt4rPTLSdPs9mqo/m6hcS/xNv+VET5l+T/er5X/aM8baRDJca1a3vii/lgll1Jru7l32lr9u
                            SW1lbav+q3ywbV3r8vlP/fr2L49/EW58eabrFnoeoXOiTeD/ABEt0qJA8txdbU3pFFLE+3an8W/+
                            H5a+VfiDJc+PvBXjDxfc+MbHSpb/AFH+17zRr6Vov7WullVoreKLYvyoj3G7/b2f7VYSOynHkjzH
                            zHfX114VXVbRWaF7jyobpXX512ypL91l/vKjf8CrrV+J1pqXhvxFBqtnFfalqUtm9nfXCb3sVg/1
                            rxL/AHpVZdzv821P4q4LxVL511LLKs6XU0r+fb3av5sTfK38X8Tbnqx4Yha6uFhljaGxZG+2fuvu
                            xMyrK6b/AOJVb5f92tox90zlL3j0DVPFlq9paw6boM1slvo9hZXzPK9xu8p9/wBoRv8Abb5dvy/K
                            zIv+zwN9H5McTtPFeWQZLiS0+7tVn+dNy/d+Ztv3v/Qa0PBPjaDwfrOmjUNKi17SrO+S6n0m7nZb
                            e8i/uNt/h2//ABVFrqOn28U00/y29xKqtFC22JImlV96IyfNEjI67f4t3+xR9ofNGUTl2kuXjfWW
                            bYn2rfH8v/LX7/8AD935dte+/A74gJqEWofbrtbD9/LcXVxt37llRPkf+6qvu27Pm/74r5yu5pNr
                            2cbSGy8154t/8S/39v8AurXReFfEkOg+H7pFiaa9ln3N83yKqxOqb1/333f8AoqU+eJjhq3LU5ZH
                            3f8AB/Uv+Ef8TRahY61J4b2xNFPbvAlwjLO7xIiRfxRIn71t/wDfSvQbDXrmz0v7ZrWq2VhokVn5
                            sV3pO+VL+4lSWK3tX3fdfZ8zf7lfN/wx8YP4k827aeJNW1JrewW7275bW4llSJJYlT7z/c27/l2/
                            NXtVz4elTVvEHgnVb6x0rTIpZbWfUJmeW0v2+SX53+7ufZs81/mVvlry4+57p70vfOj0TxBqdhdW
                            8WoX1i/xAsJfsXkwwbreBVd9lw+37zv/ABf3a8nsPEDa98SPGU/iPUG1XUNZT+0NVuNQtfs9u0Vr
                            8kSRbvvb0R/ufxJXpcOvLo/i19Qs1k03U2sF83ULSVJXsPNi2bJUVP8AWv8Ae+T5VrxTxnbaVry+
                            EmXVY5tFs4t7Xb/c8qBNm9X/AIpfNTdsf5fv10cxzcpzmt+D/D03ijxBPqvjXSU+3+Hm13w3Fp77
                            IVupXiRLf7/yu67/AJfvfJXhVzbSvqlxqF9L5MsEsTT2k0u6Xzdn39mz5v469r8Z/EjXvEnizVte
                            n0W0Tw14mvre41P7Dp0UTyraoiIkUuz9wuzYrbH3bt7V4rrFmj+KtSeKCVIJd0se2XelujNuRWdv
                            4VX+L+Jq0iQVPE2vXj+bZwX0j2jR+asMz+a67/vIrL93f/drzeZNn+9/EtdR4k0efQZJY0bzreSP
                            zd+7+H7v/s61y8zRbUC7t/8AFurrpx5TysRIqVp/2lLDa/Zovlg3K+xv71ZlO+atjgFZm+b+7TKf
                            u+WmUAFFFFABRRRQAU6Om09WaN1ZfloAN2Pu1sPcwPpdvEltsuFZna4/vVFo6Jc3SWbSRwJOyq00
                            33Iv9qtKz0lprh1gf7Y6y+UsMK73l/29n92okbU4m34Y0qLWv+Jatzbaa7RNLc3dx8/3djps2/NX
                            UQ/FHVX+Cx+GrQb9Mh1VtVeVV+dm2fxf7Pyp97+/WVZ2a30+m2uh6ZI7xWLfat/zvu+87/7P+7W/
                            rUvhrS/hrL9lluX8UXV1uRmTaiwKibv/AGasjvjE8403TYIZLL+0H/0WXczJD99fk+X/AL7q7NJu
                            VNKZYkhi3bJl/i+f5Hdlq14Z15odD1uzWx86W8Vf9Ib/AJZKtYGsXkjssar9mi2KrbG+Rvl+9QEv
                            diZzyNZ/dXY3zfOy/epthNBFFcMyt5u35apOz7vvb9tMX73XbW3KebKXMDfM1MpW+8aSqICiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKev3aZUq/6s0AW7Z/lq7b/P/wB9f3az4fu/N/er
                            Qtn/AOB7a5qh30jdsE/e7f7v3a27b5/u/c27K5+zdftH/Afmrds921645HpUzq9Kf5d22uw0r5Pm
                            3L833q4rSn/dbf8AartdK+S3i+69c0jvidr4etl2/Ntf/Yqrr3hhbzfuX/vj+7TNKdklRdrf79dX
                            bTfutrbU2f3Ky1OnlPLNKhlsL/ym3fe+X5vvV9F/DGHfEjV5ZeaD9puPNgXem6vavgzbMmyJlrWk
                            c1X3YnuPhi22Wqbl+et25/1X3W31LpVn5dum3+7VfVYWt/u/cavWPEl70jlfEjq/yr8leL+Kpt/m
                            r9+vSPE9yyM/9/8A9CryHxPcs7P/AAf/ABNZyOmMTzfxPMu7ym+/uZG/3a8t8Q7fnX/gdeheJ3bd
                            L82+vL/EO3c6/L8v8dZm+pzGpP8A3d3/AH1XHareKm9W+R3ro9Vm++ytXG6u/wB/d/e/8erSJy1J
                            FTfs3/xo3yb6qXH+z/8As0ed8q7qa77/ALtbRicdSp7pXZqSl/3aT+GtjgFb+7R/u07f81M/ioLD
                            +KjzKKf5lBBFRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAD/wCGvs/9g+/+x6yi
                            7vvbv9/79fF9fVf7EmpLbeLYYm+/5tY1PhOnDfEfsBoj+dawt/srXnX7QmpRw+Gbj5tnytXe+GH/
                            AOJbb/x7lWvD/wBqK8a20O4/ubd+yuap8J6tOPvHwJ4nuYn1SXb8+5mf71c1NMv2iZvl3p935a0N
                            Vf8A0yXc2/b93/vuufufvPtdXeuY6anxGxY3W+VFZv8AgFF5tRXl/wCBqlc+s0qfvd+//YSraX7f
                            xbk/36CyjeTLtf8A2v8Ax2uCv0aa6fav95K7XUpt67l3fxVx948SNtb+Jf4KIhI5i+X+99/dVH/d
                            q7fuzt8y/wDfFZv8VelH4TyqkveLDvu/hplFFSA+Omfw09Pn+79+nf3vm3/8BoAb/vbqcn3/AOL/
                            AIHTfuf3v96nL83+3/wKgkKbs3fw09vutub/AIDTP+BUFDpKXaq/7FMokoAY77qKHTbRQA3+Jf8A
                            4qv1H/YP1vTLz4EpBKscN7FPLvfzdv71nf8Aev8A7O2vy4/jevvD9iHx5Y2HhfU9BWVppYl+0N5z
                            bk+Z03p/3wlKpIKEeaR+gtteQXkumXlzt1LUPsvyvD86fc+5/vbKx/iL45im8P3up6ZBHNNFqK2/
                            2i7s5ZXtfK2PK8USp8y7PlrjNS8Z6Vc3TxLfedcS3UUvnW8vlOsW9Puf3d+yjQfE+mTXWlXjQeTp
                            ks8u6a+Z/t32dpXdEdF+98n8FYxkdMqfIeX/ABy1LVb/AEPXfDVjqF34P8ORfb9Q1O0t13y3kv7r
                            7PavcfL5UsqS7vK+5t+Wvl/xdrGoTWHhzQWn0mZLPwz9nsbT7D5t611PcPcSpEnzfcuEf53+7sev
                            qZvCa+JJLeRV1BNY1yXW5dOTUP8Aj08qWXY97cWu/c0qJt2/d+WvKfBnwu0rw98Rk17SvFEV5F4I
                            a/uJfEj/ALp18iJ5U3fwpveVPk2N99KfKI+O/Hl5feJLy41PUbmbUtSlnb7VLNF87NsVWdtvy/e2
                            r/e+Suf0r7K/lK1z9juomb99K7eUy7G2/d+783/odfQOvfAHxLD4+0zTNQ2zarq2mLq+tQ6Yrf6B
                            FO8tw6Ss33ZURN2z/bSvPviF8Oz4Q1q30pbae21CCz3XiPKjou7cyOv97cmxmX+FqvmMqlP+U47/
                            AIRue/0ebXmltkhgZVa3X5Xl+fa2xf7qVehs7G48L3t5qeqxW+sWrRQWOk+V/rbeVHld9/3U2bl2
                            /wC09Zn2iWbQbS0adne1kliitPK+dFb5t3/A2+X/ACtbPjC2n0fxPe2etQyaVfWemLb3Nuy/vUl8
                            pVRH/wBv7m7+793+GrMPhOEvod8yvEv+jv8AcTfub/8Aaqg03z/L8ny7KmSZNvlssXzfxtu+Worm
                            NY2dVZZtv8a1rE5JHq3wv8VT6LPZXXmSLbrc/dhX5/NVVaJ1/wBpdjbW/hr9AfDHgDSviF4ZuLzS
                            r7UIdKsLNbjxNp92rqksv35Xt3+82/8Ah2fxJX5geHtQWz+1u07QusErQbf+erfJ/wCg7q/X39nX
                            weqfCr4b6vqGg6leaxo2nWsrW983lTearpsRP70X8S/7SJXHUp+9zHq0MT7p5L47+KGpfCu18C/D
                            SHT55tMi1NX1p7GeJLu/82Lb9n3N93bLv3fP/DtrkfFvh+P/AIRmKVtKbUvClvqMVl9h0u6SWJfI
                            l2RRPcb/AJfm+98n3v8Acr6w1X4J+APG2vWV9Z+RrEWkz3mkNcXemS3Dy3n2h/tTtL91nifeu/Y3
                            8dfOOvfCLwh4P8QP4Js4rzWL2/gXVdRht7xLhLPzZdkSb/7zxfw//F1Hs5HTGpGXwnz74z03xD4q
                            guLafSLvStPumi1WLTLGVHSK1lidIndFf72y33N/son9+vMvG11pFtpOmWOlLqU2sfY/Kv7ib5Un
                            lWXciIn+x/49X0He/DSw03XvH8GraVLrHijTta+xf2J9s+z/AGC12Ps82VPlb90iN8n3fu15p4YT
                            wn4S8faFeeLNFvr/AEz97LPY28qRReVsfynT/aR2T7/3qfwBL3onj6WP261vYvs0kN7FAyy+a2zd
                            8+/e+77v3fu1w80XkylfvMrV3vjiaWHWppfP85pfnf5vvf8A2W2ua03RZ9e1G0giXyUuJ0tVlmb5
                            N7P/AHq64nlVo/ZOf/3VqxbeWjfvd2xl/grf17w7L4f1jU9Na6ivGsLmW0a4tmDxS+U23ejf3W2/
                            L/erAaFo1VmRkRvmX/arbm5jj5Qkh8mJG3K+7+H+7VaOn7d+7atRUEBRRVhodi/e3v8A3aAK9FFF
                            AD1WtaHQb6bRbjVVj/0C3lWJ5v7rNWXHXWQ+ILm58Fv4ftrWP7PFc/2lLcJ99vkVNjf7K7qAIbax
                            017HTJftUn2q4nZZ02f6pN6fOrf9910Hh6GfR/EzLpTTzJFKyRX0Suvysmz/AD/uVF4e8N3et3mn
                            6eksbxP8ljcXH7q3aVnRGVn/ALtd/wCGLDWtY8b3cFsyzXHh+L7Kv2FU8rcnyb3b+79/56xkelGP
                            LEiuIYvCWrabF4a1eSbzdO8rUb6GB9i3DJ89vv8A72//ANDrBv8ASoEvIrNpZIdPt2WKXevzr/f+
                            T+Gu7mttQufh9quqz+ZDoWm30W/7OyfNP/G+/wC83z1m+Ede0pPD/jO+1W0bV9V1K2W3sX3fOjbH
                            d5djfxfInz1kbHFeIdbsYZdQsdDWd33+VFcfwNFs+f8A4FXGIkEWkvuRXl3fMn8ar/fqxpV3OtxP
                            u8wSqrfKq/M399f++aluJons/Ksd39oX7eVLb7P/ABxf+B1oc1SXunPzR+Tbqv7t2b5t6ff21Rq5
                            eWc9hcPBPFJDKv3kddu1qh2fKjbq3OAg3Ubql8rav+1XS+JvDcegxaekV5HeS3UHmy7G+58iNtoL
                            5TlKKKKCAooooAKKKKACiiigAooooAKKKKACiiigAooooAVqclNapUXduoLiXLdPM3bqt2ybG/v1
                            Utk+X/datC2T5vl21znZTiadsm/+BvmroLZPl+b+7WPYbn/hatu2j2bNy7/l/grlkerSOg0qH5U2
                            /wDAq7LTdqW6N5q7/wC5XH6b8i/MrV0dgqzMjK371v8AviuaR3xO10q5X5N22umsJlm37mWuPs0l
                            SVPmWui0rdH5X+1XOdJ01hCqL8vz/wDodeq/C51huIvu/wC1/cryezT5k27n3V6h8OrCe2/h/wBv
                            5/4q1p/Gctf4T6T0q5X7On+0tY/iG/ihV23/ADrVSwv2trVFlXen8VZXiG5WSLd9zdXpcx4XL7xw
                            /iS/WZX3fI//AI/Xj/iq8+/8395K7jxDeLDK7M3+3Xlnie/++ytvfd/47T1OyJwXiG5379rbE215
                            vr14v2h933F/uV2Hie/XzW2tv/3K801a83yvt+9/FWQjH1W5/dfLXH6pMr7EV9/zV0GrO3lSqv3V
                            +euSd/MZmb/x2umBz1SK4dkqv92p7l9/+/UG2tI7Hl1PiBVpI6P+A0v+1VmYlPprdRTqg2iFH33o
                            o/ioERUUUVZkFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUA
                            FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFF
                            ABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQBL/DX0R+x/ctbePItrfdlr
                            53X7jV77+yKm/wCIEK7vl82KsanwnVhviP2b8JTb9Ji3ff2189ftV62sOm3ETbU3fItfQfgz/kDW
                            /wAv8NfM37W9ms1hKy/fVa46nwnqx+I+FdVuVe4lZn3/AP7dY827zPm/u1YuZGt7ja3+fv1XW5+0
                            rXMdEipJMybP7/zbqzLm8ZGf71adzJFuRV+f/gVZV5tSKVXXYlWMr3Opb1dWf5P7lc5qr+Yzt996
                            t3lzsb5WbZ92sK8mZ/lX/vqrjH3hVJGe83zfxJVdfmb5qlmVd1Mr0Dype8FFFFQWP/u077n+/RR8
                            1ADf9inN/D/u0f79NoAKd838NNf+CnR0ARfw0P8Aeanu9D/e+X59tVEiQyht22imt8y0xSD5navp
                            b9lHxg2j+KbixWeGwsLi2+z3Jl2bpWZt+7d/d2q3y18xyPurqfBviF9F1KGdirwtKu5GX73+1/wG
                            lUjzRJo1OWofqJpt5PeeI72eDTIUsmgW9lR02eV8jonz/wC38n/j9dN4e8YXL+KoraeKSw1CX7Q9
                            8l3BFdW8tvv/AOXeVf8AVSo//odeM+CfGH/CQ2em3NnctqUTQM8twnyJLKyOiI/8P3Er0D4deJ2m
                            hSKe2gv9YilV5bF28qK6ZndH+Rfm2/JurzYy5Jcp7co88T0vS/A+ueJLi68caHoel6b4mtYJdNtd
                            Y8Tam7XGnea//LWKL+La7f7TfJXVaT8B9cv/ABR4Hhur7RJtE8OLLf601lAn/FR38q7E82L+GKJV
                            Rvn/AIv92tv4RQzzRaY32G7TU9LeW1lS7n/vP+9uNiPtZn3/ACts3baf+0n8QvF/w70fSr7w/wDZ
                            tN077dbvrGrX1ur28VmzorxL/E0r/N/33Xp/ZPHqc3NynzL8WIZ/D3jjUPFmp+Dta8PeHY7G6t77
                            UYZVlm1mW8uER0lRfmi/dRbVd/lRW/2K+HPijc3ialFLcyyfZL9pbqzmV/Nf7Ozumx3/AL+xPm/7
                            6r7d/bY+IUVhdaVPoeqzQtdLv+yN876yy7EdH3fdXZL/AN9Pur87fiteeX4t1C0trWTTdKil/wBF
                            0x7r7R9lib5/K83/AIFXLL3pHox9yHMaPwN8caN8NfiVpXiXxBY3Oq2mm3iXUljbrFsutvzIjM/3
                            V3qlZni3WoviV4yudTdmhuL+BrrU7tE2+bLs82aXb/tS7q5/UPEH9rQ2S/ZYbW6ii8mS7X78qp91
                            2X+9t+X/AGqwbaa5S63QM32hW+V0rp5Ty5VIkKx+cy7mVN38b024maZlZlVP91aLp5Zpf3n3l+Wr
                            FnmG4SfZHMqv8yTfMn/Aqs45fEdd8JfhvqvxW8bab4X0aBpr6/l2s+zekUX8crL/ALFfvp4Y0vTP
                            CVhomh3LfY7dYEt9OhhXY8qwRb0T5vmb7jv/AHfkr4i/4Jl/CVfCfg/W/iVqNjZQvrKtZadNbxSy
                            yxWv/Lx977q/J/45X25qFzpvhy3l8S69qraVptmipZ6tcS/P5EuzzUfcjbf4Kk6Ix5Sr4h8YeD7e
                            6TwHfXkjTajYS3q6ZYrLFK1n997hdv8Afdtrf7T1454sv9Rh0Xxl4u0rRtH0TT4mTVVmu4GXUIrO
                            K3RNr2//AC1n/dPtXd93Yv3q8v8AiV8S/GOpeH7v4kSJDCnhzVotCsbt4NlxeWEt1s3u+/8A5aun
                            zMn9yvKvjr4tvrPS9b8NWOqq+p+MtR3/AGe4Z0ls7eKXzUillb5lV3d9uzbuWuWpUPQpUzPufBnw
                            +s/DPiXXJ/Fn2+71mddQitNTldLuVVut2y6Rfmi3xfe/2qzfiJ4P/wCEw+2+MdB8Dx6Dpuks2lQR
                            Ov2K0eKX5NPiiil+aWfe8rM/8HyVofC6w1y81SLwrp8tjZpp2mXUU76HBEksqxbHlllum37tm9G+
                            T/YWvP4f7T8VXmoarfeKNWs9M8i6f7ddr9ouL+62IkSbF+VV+T5X/wBh6zOrU8/8f+A9B8B/FJLG
                            +1PT/FSRWq3Wp/aElieKV4v+PfYv9x3T7lV9F8RT6D8L28OT2Om3Ph/VNTi1eLUFtd1xayxJ5XlR
                            St/sfK23d/31Xa/EvxJBZ+A1gsbbT5ptZaJG1C7VHu4li+eX/daWXazO/wDCleePea14/wBOtNMl
                            Zv8AQG3/AGiFf4f9yn7Qw9n9o848Ztp95qjLpUEkNvF8nksu2s/R7ZWuHiuYJJnaJvKXd8it/fb/
                            AGa+rPBPwX8P6P8AAjxF48vruNPEtrfLa6dpl2qPFf8A3PNdG/jdd7/LXF/s/wDwr1f43fE248P6
                            Nc2NhcSxXVxLfXa7Uit4Nm93/wB/ei/JW0ahjKlH4jzXxeq6T4Y8P2kSWcy/vbr7RDFsll819m12
                            /j2eV8u37tefW8LIyS+V5yK3zJtr2DxxLaWn261vJYNVe32xRXe9pfuvKiJEy/Kqunz/ADferK8P
                            +H9+l27pJM/mxLL5KRbdsu7cn+98q/8AfNbRqGMqPMcBZ6LfX7SpBBI7RQfaJ/l+6n97/wAerOms
                            2h27v4l3LX0Ppdt4Ov8ARvibq/irzn8US2drF4bsbT/R081nTzXb/cT+GuF8Z2Gg2fhmLbeRzam0
                            vyw27b0Vf7++j2nvEex9081sEge4/wBJlaFNv3krV8MWdjfeItHs9VvG03Tbq6iS8vlXe8UTOm9/
                            +Ar81YNTWfkNdJ9p3LF/Fs+9WxwHTeLtO0ex1vV4NF1Br7Sre5lis7iVdjyxL9x/+B/erD0dZbm8
                            W2WfyUl+Vnb+7Tba3WWX5n/i/i/9CrqNV8MxeHPGFvY2V5DrH72La9v9x9392olI2jHmOi0qFdSs
                            Ei1Cf5LBm8q0/gVf76f7Nd34b035ruVZVhllVUbZ8iNu+X565Tww/wBm1KX7NZtNexLKk8KRb/KX
                            +/8A8ArVTWFRXiZvtNxEyos0Lf61f79c+p6XKaGt+HmudJ/sa2aWG0afe0KS7IkZf4/9r7n364/V
                            bZtK8pli2Iu6KJ0b72377/8Aj9dNfawv2y9ZfMhSWJvn3feZk2bKwdVeJFtbOBvOsovuzbvnbd9/
                            /wAf30olyOS0XUr7w3rj30DRvcbWTa6b0VmT/aqukKvslsYp/wC3Ym+1NMjfxb/4Vq3Nta4eJV2b
                            m+Vf46ryeVDcS7mkTbE3yJ9/d/t1oYyjzGFc/a9VmmvLl2mlaX97M/8AeroLjRNIh8F2V82prNq0
                            suz7Ii7PKX/besxLGW8s921oYovvOv3Kimhj8t5UZdm7/Ut/6HVmPszBdvmpXlZ/vf8AAau3yKi/
                            Kuz5vvf3qqL8u5dtXc45fEV6Kfu92plUQFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFOjoAVV31
                            PCu9qiRKsQpWcmdNOJbhTcvyrWlbW2xv+BVn20Kv/HsfdWtbJvlTbWB3xiatgmxk/wBmti2/eOm6
                            sq2+Vfu/PWxpq7F+Za5ZSO+ETorZPJX5fuVvWH75v4n2Vz+lbXZ1/grotKhVN+1tibaxkelGJvWF
                            z5zIv3EXbtrtdNdYYotqq9cVbI1wu5f4dv8A3zXVaUkqKn3n/wB+uaRpqdtoNh9vli2xM7/7FfRH
                            gbw/F9jt9y7/AJa8Z+HWms+2Vv4mr6I8K7obP5lWuyhE8nEyLd5ZqkPyr/FXnniq/a2V91eoX9yv
                            lPu/iry3xV5Ts67vn2/LXoHBE8f8VXks29v9cjV5frd4+2Xd/D/s16hr1tsll3V5f4ntvJlfb9/b
                            UanQeaa27Oz/APs9cPqqfM+1l3/+hV2GvboZXZt2z/Yrj7l1fe25kas/tDkclqr7F3fwfcrnF27m
                            +aul1tF8pG/2q5fzP733lrpiebUlyhJ935qgVaV23fWmp9+tjjkLyv8As0bvmpJKb/FQQS0USUVB
                            0D9//fdOT/d/4FTU/wBdR/F833qkmJXooorUxCiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAe/8ArK+n/wBi3QWvPGSy7d+3a9fMWyvu39hvwlslS5dfnZ/mfbWNT4Tvw0feP0o8H/udLiib
                            +FVSvnr9rRP+JXKy7vu/+yV9F6JCsNqn+yteE/tS22/RpW279q7646nwHpR+I/OLW5le8dZayrmZ
                            Yfu/f/ifbWhr21LqVv4//s6wXdX/AIv/AB6uaJtIi877n+01Zuq3nzOi/fq1cuqLFtb7v8e6sTUn
                            XbLtagZlalN/47WK021/+BVf1VPn3bqy3/11dtKPunn1pSHf79Mkpqbt33qdHXSc3xBJRHRRHUGw
                            9H207Z9ym/f3f3qdJ935aACiOj+9TZKAHb/4aP4d1Kny/wANM8ygB6bf4m+SmUyigAjpklPjprbm
                            b71WYyIn6/NQiNv/ALtOkqL+LrWsTjl8R9a/syeNrG+tZfD18rO9/dL5EKNsiiiWLe7vu/h+R/8A
                            eavrDwZ4e1fxPcJqqrvt9Ns4ookt50SWwilld0R/4pd772r8xfAevXnh/wAR2k9nKqPKy2+/+6rP
                            X6Ofs2Wf/CZ/2fq67n1DyPs+oo7bNrRO+/Z/e/vL/wB9V51SnyzPbo1uakfa3wx8NxaJZ2jN5k16
                            rfNNEvyff+4m7/cpnxI8VW1zNpmnz2P9pafeT3XmzPsliieD59n/AF1/dfL/APYV0ug2Eun28Vos
                            86ah9jWXzkXei7n/ANqvnL4u+J9F1K31Pw9Yst5af2nf3EEKb08q/g3yyxPt/h2SvL/tNWvwxOaM
                            eeZ8VftOeM5dWW9s2tlv0t9T/tXSb7/VPYRSo6S2Wz7330ib5/4q+Xb77HqkME1xeNDdyyy+ejRf
                            uokVE2Mnz/M33l219G/Fbxct9r2oWN8lzpXh/Vp1tb75YnvfNi/eom5v9Ury7H+T/vqvlR7b/SJd
                            26bb96op/Ed1b3Y8pXt4V83csqo6t8u/7jVSaTbPuU/Nu+8vy1p2dh9ps5ZWn8na3y+avyN/wKql
                            9bNay+W6skv8W+uo8iUeb3iu0ysrbk3u38bNXp3wT+HOo/Fr4paD4OsbZrm7v52Rl/gVdm9nf5fu
                            /LurzHcyt8rfN/D81fox/wAEw/C6Q+F/GvirVbb/AIlC6jZ2ttfIm6489Ud5YlZfm/5a2/8A49Sk
                            RH4j9CvB8OlaVeS+AtPsV0d9L0WKVX06LZaRRS74kiif/fR2rkfipqsupfCfxF4aW8025lllistC
                            TWZf+P8AaKWJ/nXZ8zJ5T16BqGrRfC7SfEHijUtPudSRla6tbTSbV7i48hU/uL/tP/4/XnumovxI
                            0O91G01HT3126nlXTltPKuJdLWXY/lN8n3tqOrf79P7Jt8Z5f4t0TStE8c2t5qs8FnoUTRPqLveb
                            7SeJf9IeWJP+ervK6bK+OvEPhuX4keMNb8Y64t39lvLyW40JPN3vLFvfYjv93ds2bUT7uyvePiQy
                            /GLXE0/whpS2eiaGzeG57h/9bLcM/wC9dEb7393f/DXPXOqaV4P8UXvgPXLO51XTfCUsuq6dp/lJ
                            Fb2F/Knyb7hflZfn/wBr5q4JHsUvdOYubn/hBfEz6VpVs2vana6ddXqwv/o8XlT2USPb/L95kfe3
                            /AK8HudS17QfDkS3LQQ2SxW7xJubzWVfuPs/i++9dV423aP4ol1fU9Xub+3i/wBH863+SL5tjvFv
                            /vbHRWdG2/Olc74kubnxhrEWoavEtnpUUUFrZ2Lq9x5ETb9nzL95n+dv9nfWcjp5YnLvo6+Kry4l
                            0y1aw09WVPvea6t/G/z11tsmn+GLV7GzaS81OVVTe7JF8rffT5U+7XZeE/hjbapL4iVtStNEt9E0
                            W41xbiXfF9sX5F8qD+Hd83+1XMeGbPU9Y8ZRX2+JIrCz36dLcKqJLEqb3fZ/tu38dBiafiy58WeM
                            PC/hnwrdJFp2g6arRaYnmrKjs293bf8Ad3f71cvpvhW28HzXdjBeNYOqtFLdws6fum2fx/7e/wD3
                            a6WzSK5s/Ktop79/PZItkuxFb76Ps/3P7lV7nWPti2V81zHM8UH2fyZlTeyrvTZ/u7/79BY6z0HS
                            tejfTFbT9NtPI+2rfOu9N0SPsRP7zP8Aw1x9tc+df28v+pRW3sjts+XZv3o//fdFz4qs3urT7Tuv
                            4Yot8tvC2x2+f7iU/wAGWeh+KviNpukeLNeXw3oV00rz323e8SrE7p/4/wDL/wDs0ESjy+8crfat
                            pUNv4gtp9N/tK+vpYntbve6JFt+d/k/i3p8v/A65b/hG47aSJbmJpriVW/co33as69qNnDqCNpkb
                            Paru2NKu3f8AM67/APZ+VUamQ332i4SdbmJJfP2eSz7XZdn397fw1vHmMJckjmptH33/AJG1UaVv
                            3SI1Z9zprW1w8EjKHiba1Wr64V7za27YrfMv3f8AeqvdTRXF03kL5MX8O6uuPMeXLkJobNZF2q7b
                            0+fZ/e/3a7C/hg8M2vh++03V4NSuJYPtD28KMj2su/dsb+99371cP5zJtZWb7uzdW1qvif8Atie0
                            dtsP2eJIt8MCJuVf4/8Aeo5QjKJ6B4s1i+0fxNcS2ur2n+n2e65m0ltqPvRN6Ozfx/N81TeKv7P0
                            q/0yLwrY3dtFYWdvcXV9dq/zP9/f/s/P92uGtrmx1W3vYmvo7NLWLzYndd7zt/crZm8bajc+F9Qv
                            G1dX+3zraz6ei/PsRPk+f+7Ucp0+0iX0vItbsbWeeffEztLdfLtf5nffs/2qpX94s15e2dsrPb7v
                            3D/8tfl/v1i/6ZJcabpazxbfN+VGb5F3/wB5v4q0tUjg0XxBd6f9rjv5Yk2/aLf7jt9776/w0coc
                            xVmtp0sPPb5H++zp9+nQ2LXn3kZ1ZW3J/H/wD+7VvXpra88plVbBGXYsMLO6N/cd6NUs/wDhHr+1
                            tmnWaWWBXbyX3fMyfxf3aZHMUbmaVIkggff/AHlT7lZuvWa2txKsqrC6tv2J89aru+7csSp5T766
                            Hw34Z0/VfAfiLxVqscu+Jvs9rsdETeqbvu/xfNQRI8smma5lSNfnT5UqtIjQt5Tfc3UsjyQzfM3z
                            LSPtbY2773361iccirRRRVmIUUUUAFFFFABRRRQAUUUUAFFFFABRStSx0AFPptSom7dUs2jElhT5
                            kqwif8Aqv/FV2FFdfmrKR2RiTWyb1RVX562LZPl27f4qz7ZNm+Vf72yti2+TZt/4DXPI74xNJE2f
                            KtbFsjQtub7n9ys+ztvO2bvkrYtof3vzNsRf79cZ2Ria1tDvZGVdiV0Gmo21KybPa/y7t9bdmjRy
                            /wAP/APuVzSOyMTpbFNtv8q/P/6FXbeEtNa8ZN0W/wD9AWuP8PWbalcRRL93/YXfX0F8PfCUcKoz
                            fP8AL93bTjHnCpU5YnQeFdEitoolXaj/AMSV6npVzBbWqba5J4Vtovl+TZ93ZVd9VltldVb7tepH
                            3TxJS5zqPEGsLDFuib51ry/XtV2NuZvnp1/4hZ96s2zb/cauF17W2TerMrp/6DV8wRiVNV1BZldv
                            73/jteda9eLNF83zuq7K0NY1jyVfay/d/wCB1wmsa3vXdu+T/wBBp6lHJeIU3yu38bM3yVwl+7R7
                            9v8Ae+5XZ69cq6u27+H5a4TVZtn3fk/j+9RqTL4TnNVm2LKrL/FXOyfe+WtjVLnzt/zbE3VhNlm+
                            ataZ5taQyinSU2tjjCiiigB1PqNqkqWXEmb7q7f4vvUz/WL/ALC0ySj+GkURUUUVZkFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABTpKbT1ztOfu0AaGiWDalqlvbL/E1fqb+yd4S/sfR7R/7yr/D
                            /sV+dnwN8Ntr3jS3j2/Krr96v1t+DnhuLTdJt12/wrXDVl73Kerho+7zHtem7fs/zf3a8a/aHhWb
                            Q7hX/u/79exWybIq8v8AjHYfbNGu/wDrlsWs6nwHTR+I/LXxyn2bUpdqt8zf+z1x8z75dy/J/tpX
                            ovxU0v7Pq1wrfwtXl7/uW+Zf738Vc0Tsl8QX7/crCuLlnjf97sqxc3kv3vmrHvLzfvVf71bRjzGM
                            pchUuZmkX5m+7VT7/wDv1JNNvZfl+X+7UP8AFXfE8qpLmkORKkf/AFtJHT46YRiMkp/3P9+mSUVB
                            sH8NP2bGokpm/f8AeoAfQ70eZTKAH+ZTPMoooAHfdRRRQAb6Y77VSlemSVcTGoMqKpd/y03b/eq0
                            ccjW0u2kvNSt4IEWaV5dqo/8X+9X7GfsE+Em8P8Awt/tW+traFtW3XUvlfP5vlRJsuNrf6rem9vk
                            r8yP2Zvh7afFb4oaD4TnhuU/tKdIpbu3Xf5Fu3+tbZ/uMy7v4d+7+Cv3H8H+G7Hw9oOn6ZBHHDaW
                            Fn9n2J9zyvuIm/8Au/JWcvekdkfdplrWPFiL4UTxdYzyvp/9n/aIreWPZ8uz77q38X93fXwx8UYd
                            M8DRf2np8uqXmmapq3+mPMzv9luJ4otlxvX5old/NTyv+mX+3X1L8Ste8m/1PSraD+3vtUUX260t
                            22JFYeU6psi/6av8v/AK+RPj9Zz+FfAfhzw9befNZeINYuki0+ZdjtL8jxJ/1yi+0Sr/ALr/AOzX
                            NUOyhE+PvGevQx+JL7VWtmt7dp5LjTornZeLL8zr+9l2xb0+R9u/a67vut96vKriGKaGUpazvLE2
                            5nVvkWL+Heqp/wCPbq7/AOIsM+n6fpOn3WoWc0VnBuSxtFbba7pX3pu/ibevzf8AAa4XRNSe2muG
                            gdUaVfubdyN975G/2aumXX/lMG4ZX+7u2f3Xb7tXb+8864SdWV2aL5vk+7/BWjfafBHodlqEM6vL
                            K0sU8K/8sn3bk/4CyVjXNskP2dlnWbcu9tn8Lf3a3OD/AAmp4b0GfxJr2m6PZ/LdX88VlFub70sr
                            7U+7977y1+63wr8A6Z8E/APhzwV4XgksLLTVifUbi7iR938V1K+3/lq+zbX5cfsP/BOf4sfFrR7y
                            Ux6bZeH2/te5uHbfLeeVKibIl/3m+Zq/ZzRdBi03VNSlj8ya3ll2t5r79z/d3/73zLS+IOXlOfvP
                            il4FvNXsfCt94jjS61mBfsdvDK6POrfwI6/Nu+79zbXn/iPXvAHwF1Lw54D0qBfDfiLxHPLe2bWM
                            Dyo11sf97dS7/uu/zf7Wyum/4UDovhvxx4c8RwSQw6Z4Vs7q30XSYovkiln/ANbK7fxP/wDFV5F4
                            q+Et94w+OEXxL8Y6naJFoLrFoWmaf/DKu9Inld/vM7v9yo941jGJd8RWen+D9Z1rXL7TNN8Q29/K
                            iXUNuz2W2WXYj3Wz5vl+59z5q+b9b8N/2CvivU9T1xtS+0XkUTJDvS0it9/3ET/f/jf7/wAle8eJ
                            LmC5l0SKdpIb3dFFqLxL8isu99iJ/t/drzzwr4bufiV8RvD/AIa1OeFLS4vt+opbxPslWL/SHib/
                            AGdmxaxkdsfdieSfG6HUrrxBa+CGn0+/8GwWsXinR7S4i2XsEV4m7yrjb97Z/D/EqVxvifRItB0v
                            UFaCS8srVYv9Lt2/0eJmR9iP/wB8fN/drtb6bRvid8SPil4/udQi8PfaoJZdC+1/P+6ifyoookX+
                            /wDe/wCB15lD461rXrWXwqsS22hXjLdXlu6s7+bs2b/mTd9z+N/4qxqG0S7rfm6VZ6fobQaTfxRL
                            9tbVtPn815Wni/1Wxvu7ER/ufL8lW7bbr1vaLp8q2cunLLcNd3yo6fuE3pEn8Tb0TayVX0Tw9bJb
                            +ILPT2X7Pa2v2hndv3u1X+TZ/tv5v3P4qx7zUrPxD4f0y5trZdEtNDgit777PPsu79mf55dn+3vp
                            BzBM9tpq6VeeGp5L+XTf9NuobiL5IpVff8ifxL9xfn+Ws/4taro/ie9vdX8P2NzYXEsUT39xqc6b
                            7i6ZHd5YolT7u/8Ag/2E/v0/xD4qew1S3+zKrpa6ctqtumxHZWT53fb/AK3565FL/wDtW6solnjS
                            6l3W8ULtsTaqb3d/7q/w0w5ix45hn8PaDp+i6rbafbXFvZ/bYLvTF2SytOm7967fwps+7XIeONR8
                            Lnw7oraHBqCaqtqq6n9rbejXm753Vv7v92n+M/HlnfyaFPbWjPremwMl9cXcvmpcMsr7ERf7qI3/
                            AI7Xml5qrXWpTTtErozs7Qr8iVtCmcdSvy/EaDarJ/ZyQNctu/1q7f8A0Gs+a8S2tVjjbznl2szf
                            3f8AZqveX32y6MuzyUZvlRKrs6fOq/3vlaunlOCVf+UEXzldml2P/db+Kq43P0obbtXb97vTd1bH
                            GPZW2jd/wGmbqN1JQBYV0VH3Lu3fdb+7VvSr6Oxula5g+02/8cLNt3VmUUAb2i3FlDq0MmpQSzaf
                            G/72GFvm2/3d1aX9pQPeSwWdmsNrLP5sTTfPKqfwJvrm7aRPtSs3yJu+bb/drpLm50+HXn/syWSa
                            0iXbE83yvWMjspyOldPsexm8ua4b5PkX5N39yormzW23bl/0hvvPu+dahs7xkl3K3zqytvf+9/cq
                            K5vPOaWVm3y7mRnrLU3K9zqSu0XkfJKq/M+75GWs248SX1tpsunpdSf2fLL5r2/95v4t1OubxYdi
                            t88W3+BaxbmaSZkj2/L/AA/3q1iZykVryb7TcOzLsqrT5F2SMtMrY4AooooAKKKKACiiigAooooA
                            KKKKACiiigAp6/camU7y6AHoPmq3DDv/ANh/9qoUTdVhIW/u/drGR3wiPSFnZvl/2qtpCv8A8VRb
                            w/L97fVq2Vl/ibfu+5trnlI7Iluztmf7rb0X/wAerQTc/wArLsfd8tRWy7Iv7+6rtt89wiMv3f79
                            csjshE07Paiou35/7+6ugtbNZvvN937yVlWaeTKit86bt/8Au1tWbu/3fufxVjL3T0oxL1si7v4k
                            210ui2Et/L8v3Ko+HtEn1W6RV+dP79ezeBvh75OyVl/8drHl5wlU5CXwL4Y+xtFK275q9l0S5azj
                            TarJ8uysWw0f7Ns27fl/2q2EdUVN33674x5Dzakuc0rnXm+7trHv9Y3/AHf+BVVv7z7Mu1W3v/6D
                            XL6lqypviX7if+hVtEwGeIdb3s+3/wAcrz/Vdb3s+5mq74kv2eJ93yP/ALFeZa3rbw3Dr82+tNQL
                            Gvaxv3q33GrzzWNSlRn2/c/2607/AFJpn+X565TVZlRfm3b/AO/WQ5FLUtV87ftX7v8Afauc1Wbf
                            Fu/9mo1S52KzfcTd9+sK5v8Aer/L/FWnKY838xVv33M/+9WdJVm4uPOXFV2rpieVUlzyBmplFFWY
                            hRRRQAVKny0za1EdAD6Kfs/vNTP4qg2kRUUUVZiFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            Dqk+7uUUz7zNWnoln9s1GCJtzru+aguMeaR9T/se+BP7S1RLx12bWXb95t38dfpx4S0r+zbBP91a
                            +Qv2OfCS6bpduzRN/C//AAKvsO/1u202z+aVUrg+0e3GPLHlNebUlT7m2uS8YXMepabMu7furmtS
                            +JFs8rqssdY7+LV1Lem75GqKkjaNP3j4c+PelfYNeu9qts37/u/3nr5/vLn5v9j5q+s/2gdH+03E
                            sq/Ju+981fJPiC2+wzSr99N7Mtc0Tpl8JhXF5t+9/wChVlTTb2/2aluG2M/8FVfO+avSjE8qpUHe
                            XUVG/wDvUblrQ45SiSr/AKqihH3USVJtEPLo/ho8yjzKRYSUUSUUAFFFFABRR5dFABQzUblplWQL
                            spjvQ70yqOaUg31PZ2yzXCq27azbfkXdUG3f/s12ngDT9Q1LxZpVtpkEc19cXUVvBM0SSpFK77Ub
                            +795l+9Vy90xj78j9Jf+Cc/wHi0HwDfeOJLbUIdS1mJYrB75UWJbX77ywKrt/Fs+/X3Yj3Nt4fuP
                            tKweUtnLEsL7Et2be/ztL/DvTZXD/C7wNF8Mfh34f8L6f58yaNZrbys6o7zy7Pn/AO+3ro/GepXl
                            n4X1NtMs21i92r5Fo7bIl+58j/3V2bmZ/wDbrGJ2nl/ifQbHR/iJe+PZ9Qu4bS18I/2e1v8AO9pK
                            qo8rvFt+ZtlfFX7QPifUNV8C2ms6r/aE2q2cthFFq1vvRLVZbd3e3f8Aut86M397f/DX2h8WvFV5
                            b6l/Z9tbQTaxFdWtpa2lx8iQWcsu6W4ZP+Wq+V/B/sV8hftB6XA2j6tY2N9Z21vqkm5XikaZ7qWz
                            bYibF+48vmruX/YRf4qxkddA+P8A4oQ6HJcQ/wBh2n2BorZFvP37s9xcfMzytv8A9/btWsqZ9Pt9
                            Dt5LHRmmuLK1Vb69cvLC0rP8v+7tRttFzYXc1/d6daQXD6lDE7NaSxbZdqIzP8rL95VZv9r5aZDp
                            ceo6W66VLP8AZ3tXlltWVmSKVf8A2R/4Wb+JKuJFT3pHO3Gi3KfYvKga5e83eRCnzPuV9n3V/wB2
                            sm2tvOeJfubm27/4a0Eu7qzuLWeKfZLE3mpsba8Tbv8A4qvUPgD4A/4Wl8RoLKWWKztLCP7a3yKy
                            PtdPkbd95m/8e21p9k5ox94/Sr9jn4V2fwr+CkWsWOiyXmsXUHzS26/aJbxGdGR4v4VTe7/c/uV9
                            h6bcrZrZbm86a8bfEz/JubYiP8leefCjTbPwf4D8JQW1nPZxRWavFaJLv27n/wBUn/oVd/4S03Xt
                            Bu/EFzq+qx39pLP5umW6QeV9jtf7j/3nZmf/AL5SlEKkhdem0/wx9kgW23osrXDQxNudWb+OvJ/H
                            N+r3H2ZYIHiullffDL8/m+U+9P8Ae2J96tXW9enfXtTWCfzpbhd8X+zt/wCWSVw/ie8sZlms/t0a
                            J/aPmzwv8+6XZ9x0/u0wjE8q8VeIrPUv7Vl1FfJeL7LKsKM7pKzRJs2f7X/s1ef+J/Geg/C7wlrX
                            iPUG1JLi1ivNK0r+z4JbeKXUZ4vkeWX/AGIk3P8A7X3K6PxhbalqviP+yvD0El/rF432WB3gR/IX
                            Z99/4VaL73z186eIfEGq+JIv+Fbz65d+JPC+l6s2oWzusT/vWf8AevcS/wAXzu+1P+A1yHpR+E6D
                            4XI39if2hqq6TMnhezXUJ7Gbd5UrRbERN/z7t/3v+BvXOXWtXPir4gy+LJW8mLxGsrtaWNtteK1+
                            RHi2/wC+iff+au48T6UsPxO8R+GvDV1p83gzQ9Mt9Q1HUEVPs+3yvub/APYd3Vf/ALCuCtvEljZ6
                            ClzY2N3Z6nLqKtbW99EibrBovkff/Eru77NlT9kvmM+/vLmG8+zXLfYPsEVxFElovzy7n3on+9/4
                            6uz565rVbyWG8uFW285/KW4b5U3ys330fb8q7K1dS1tvKu4PNtEvb/UfNivt3zxLsf5E/u79j7f7
                            2+vP7yaXRLXUJ7nU2+0NuTZ/HtX7lHKMNe1iK8vNQ3RL/pm3ytnzyxKv8Cf7Ncleax9jtUtmVXuG
                            ff8AaHX+7Tn1WWH9+qtDcJF+9eZfu7v49jVyFzqUt5cPc/L+6+dd3+/WnKcspF6bRdRvdPu9Vgs7
                            mbTIpVilvkibykZvuru+7ub+7XJs1ekweNL7Tfg/L4ci1BVsbzU2vZbT+OVliRFZ/wDd+8teaSMW
                            Oa64xPKqS5h275fmamO+6m0VZiFFFFABRRRQAUUUUAOjq9Y3Pkt/D97+7VH7tNoA6pLx2+986fK+
                            /wDvU97xdrrEux2/j/vVz9vebPlZasfaf7v3/wCLfWPKdnN7pLNf/L83/AUdapTXO9V/8epjzb/v
                            NvqB/wDa+9VxiYykJJTaKKsxCiiigAooooAKKKKACiiigAooooAKKKKAHR09Eop8dSy4kqKtWIdq
                            fw76gT/WVattu75t1ZSPSgWrb5Pu/P8A7VaKw/L/AH3Vv+AVUtodjbl3bK0Lb5Pl3fP/ALdc9SR3
                            xiXbZd/+x/8AFVetoW+Rmf733ahtrfYqbW3/AMdXbZPOVFXd8v3a4zspmtZ2zTL/ALDfx12HhLwr
                            PrDJ+6bZ/s76Z4M8JS6rdRbVZE3f3d9fTHgD4erYRRbot+371Ty85cqnIZ/w9+Gn2ZUZovuV6xZ6
                            VFpq7V/3K1bPT4rOJEXb8tZuq36oz7P+A11xjynmyqSmVLyZYd/9+sq51LZ8v+Vqjeal52/d8n92
                            sK81Rk+9/uVRmS63rf7r71cbf6wyfMzVDrGqtuf5vk+b+KuPv9V2fMzfJ/vVoWXtY8Qrtfd8/wDe
                            rzTXtSZ5XZfkRv8A0Greq6x5zPu+438Fcpf3nnb9q1mAXWpbG+X/AL7rnNb1VkV2Zl3/ADVFqWpe
                            T97+Fq5fUtSe53/N8m7+992tdTKUivqWpNMzqvyf3qzZpvM3M336Zc7t1Q/erojE8upU5gko+9Sy
                            bv4qZVmAUUUUAFFFFAD9y03dSUUAS0VF/DUtSXzEVFFFUQFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFADq7n4X6C2ueI7eJVZ/wB6tcMn36+oP2V/BP8AaWrRTtFvT5X+dayq+7E7MNHmkfoB+z34
                            J+zeHLf+B9u/7tZv7Q6anoOjTT2rN8v8aV6x8LtN+x6bbrtrB+Pdg2peH5VVl2bP7tcvL7p6vN7x
                            8Bf8LXvodU23PyN/f+dPlr0DQfid5yovm/J8qV5F488MNa3lxKv31auPttVvNEn+ZmRP/HK5pROy
                            Mj6F8eXi63pe75X+9Xyl48sGhvHb+D5kr2Cz8Z/2la7WZkRv9quJ8c2C3kTqvzu33XSso+7I2l70
                            TxC8T5tu6qklbesWbQybl3bdtYjV68Zcx83Xj7wyilT/AF1ORNtWc0R33af5lRUbmqTp5uUlopnm
                            UeZSL5oj6azfN8tOpklMiUh/nH/ZpvmGmb2T7rfLTPMo5SOYl3NTf/HKPMplUZhu+Wn/APodJ8v+
                            1Sp/rqABvvfL92mUUUyZB/er7h/4J3/C6PxV8RLHV3S2v7ewSW9lt5ot+2Xdshl/uqyNXxPZr5tw
                            ny79zfd3bf8Ax6v2S/Yb8ANonwT0S81PT40u9cgaVvsi7N0Sf8e+/wD30+as6kjajH7R9O6VbfaY
                            kW5ZYZZdqQJu2OzK/wA6b/8Ax2uC8YQ+JbPTdTuWW0vLrXLPS7dtJdv3UFwvy3ez/ZeLb/3x/tV6
                            Bcwy7bdpYlmtNyu038cTxPv3v/3wtcdealB4n0j5p45tKl06K40ya3b/AEjbLbo+/d/v7/k/2Kk1
                            j8R5b8bPGtnpt423zZpfEUV1ov2vTlffZ/J/yyb/AJZSy7du5f7lfDvxifXLNfDNm2vag72eiyrp
                            mjJEryxXS+UkssuxPmZ/nl/3kSvrr4o6w2pWHiDT52k019L1iJ/nX/Xq0UTv8i/d+/5u+vk340Ww
                            16zEurTz6VqUWnp/Z+qWjfaEvJV2Olr8jfe2Ojb3b/e21hKUj0I8sT51sPFU3/CyNF8Q6vfTvdRa
                            hFNeXM26WVtuzfu/v/KvzJ/tbau+MItMvdevdT8PtF/YmpSS3UtjYj7P9g819iROm77qN91f4Vrn
                            /DtvHql5fQXUU0N1Akt1FKq7m3L95X3fw/e3VS15bnQbi33SRPviSf8A0Zl2/N8yK23+7W0Tml/M
                            Ol1S8vHikvrnZp6zokrQxLvVf4n+5/v/APAq+xf2J/CttqmuahfLZ3N54ftdaWW2a7TYiOz/ALqX
                            Yv3n8p0b+7Xx7/wj2qTJqE8dnJeWn2X7RPNCu+KJdn+tfb93+Lbv+9X6P/sE6JInh/TLy+ubawl0
                            m2urj/W/eWeKLfsRflb5PK+dPu/doqGEfiPtqHUoo/7Hs544bO7XbEqo3+jxMu/5/wDeffXQeIJr
                            6z021tlu2e78pXa4df3W7+5XP6LoukX8mhWLMt/b3s7alB5y7tywJ/4787pU2vXl5c3j3MFz5yM3
                            zQzfIny/Oj/+Of8Aj9VH4TKXxHCeKtVi0qK7vr6CR9YvF+y2syfxf7EX+1/F/u15F4h1i+vNWiWz
                            sWsLew829vpt3+keVEn34v8Af37f+B16R4z1uW/aXxHOq3/2BGt4ET5LeKX5PNdP/i68n8Ta3Bon
                            jK4vPELTw6DLarb3WpzQP9nXzYndE/3t6J/BXPI76cf5jgde1L/i3/8AwjDXUmiXeqeJme88U6e3
                            z/InyWqP975K+YPhfrD6br0XhPUVtdKuLCW8+1f2mrJKzL86b93zf7v+/XtGpXjXMuiaDBPbeHvD
                            /g+JtVur6b/VLLPK7xPs/iZN+1f9yvn+TSrTx98RPEer6rq/2yV7q8uG1B1dXl8p/v7f+ApUSkdM
                            fd909Kufsej2flafZtN4g1TTl+1W98yIkUqyy702f3dmxl3/ANzdXNeOdbvPE/hfRLxv3P2CB9vn
                            bHfd/fd/7uz5V/u73p+q38upXX26ee2e+8RxS2Xz/I9hEr7PN/3nT/gPz1xl/eT6xFqGn2cC6rFp
                            dir3jw79ixJL/lf+B1Qw1SO+sdH0HVbu88nRdUVrqBmii3v5W/7ifwqju/zvXH+dZ6l4V8Qfa547
                            PWIlivbG4u2+eVf44k/2v4q2NB0e8+KHii4sVeO2t7ezne1hu5/KitYlTe/yP/fT7qJ/fSuFNq1x
                            ZT6neX0Hm2s62v2dnTeysv31Rv4f9qtInLKRY+J2pS3njG4nbXF1WW4giaea3TyolZk+dNq/wpXL
                            63fR3l5C25fliRWZPublWs+O8WFk3qrrv3M38dV7ht8rqq7Pm+7XTynm1KgOzN91mdF+Vdy/w1W2
                            fLuqzbJE1wiztsT+Kq7Jtfap3VZzDKKft+WmUAFFFFABRRRQAUUUUAFFFFAD13L8y/LTlkZf4qio
                            oAduam0UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFPRv4aZTvu0APjq3arub7tV0TdVpE+Xdur
                            GR2RiCbfNq9Cmz+66f71VEfeyf391XbNGhl+7WNQ7IFu3hjRdvzI/wDsVoJGqfKq/vf4t9RJD+9T
                            bWhbJ+9+7XHL3jvgWra2kWLb9/8Agrs/Bng2fUrxF8pvK+X760/wf4bl1i/ij270Vt+xP7tfT/w6
                            8BxWdum6JaOU2lLkLfw6+Hq2FqjNB8+3Z937tex6Xpq2yqqqtGlaSsNuiqq7NtbthZ7NzMvyV0xi
                            cEpc5lalC0Nru+5Xm+vX/wBmZ2Zt/wA1ei+LZltrHb9+vCvFusb22q67933/AO9RyhEfc6r50vys
                            qferJv7xn/5as+5/+AVjpqXzfK1Fzfr9n3M9aahzGFr2pfM+51T71cZqupLcrtZm/iq94hv/AN7L
                            8/3ty1xNzeM7fP8AxLRqIr39z8u1WrCmvPl3L9+rGpXOzezf8BrlLzUlhZ33fP8A3Eo1JlIbqr+d
                            E7N8ny7/AJf4q5K4uPM+6uKnudSZ2l2s3zVQ8ytoxPNqVP5RzuzfL/DUe6lptanMOd91NoooAKKK
                            KACiiigAp392m09VoAd5dFM8yn1JZFRRRVEBRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRT1WgC9
                            pds95fQqq7/mXdX6H/sr+EvsGk27Kvz7f7tfFXwp8KtrerRfL/F99f7tfpr8FvDa6Voduqr5L7fl
                            rjrS5j2MNT5Y859C+D4VtrB2ZlTateafGbxhBbWEqqu+u7tppbPTXVf4q8U+Itsl+zNLuf5vuVHN
                            7pvH4j5X8c3kt5LLKsSpu/2a8l1uG5TezRfPu+5X0x4n0Gzjl3Mu/b87V5J4wtooYn2xLv3N/wB8
                            1idHKeOXNzPbN+4Zk/4D96i28SSt/r2+fb9x6veIXZJZVVW2KtcfqSsjJ8v3f9n/AGKgOYNbh+0u
                            2zbsb7uxq5G5haFnVl+etZ7+W2+ZfnWse8vGmbdXVRjI4K8o8pX+Wjd/dpnmUeXXWebzD/Mo3/3a
                            ZuVqPLpkcweZQrtTKKoOaQ/f8tFMkpdv+1QHMOoplFBHMLvp1R7aNtBfMSb/AO9RRRQHMFFFEdSa
                            nafDfw23i/xt4f8ADy+Wj6zqNrYRTSqzJE0sqJv2/wAX3q/enwxpsHhjTYbOBdlusX2WKJV++yp/
                            An+3sr8jv+CffgyTxZ+0No7Rf6rSVl1W5/ueVEjKr7v73myxfc/h31+t015Fc38US7obu/ib7K/3
                            /KlX/lr/AN8bq5anxHVGPumsniKLULe4vIlZ7KK6W1vrR/7+zY6J/wB915Z8Tte1rRIdHttI0Oe/
                            1Cw1GK3ZIV/0drBZf3r/AMPzOn8H8P8Au11et6q01qkumWP2+4s7xXSGZvs7+az+U8r/AN75HeuK
                            8Z+LZ7zxBZaVbPcu8s8Vxa29v8n2qLZ/f/h2Pv3b60LjE8PTxavjDwv441C6s9QsL2LVr+6/0tUt
                            5by137Le32L91vkRd/8AsV8+/Fa8sfCur6LrmvXOmzXv2mLV5fCbztK6xRXCKkUu35PniiVWbZ91
                            3/2q9i+OusX3/CYRafc6Ld3+lXFjLdT3Fps2NfwP86RP975P7j/er56+Jkr33hO78RLY2l9e7Pst
                            1Yuzs9mjtKv3PvblaJt391krGR2RPIo9e0y58Uar4ltvD32Dy9W+2y29pcbrdLWV33W6rs/uvtV6
                            5rxNDDLeX1xZwXdhaPO7WEV987/Z97bU3f3l2/w1Y8Mata2msKrxN9sZmitbj5PvMm2LzVddu3d8
                            zN96rt54Vks7ibTdTvpbN7BJUWWaCV0/1TukX/A32qv+/u/2a2Ob/CP+Gujz+IotS09Iri5LWcq/
                            6Ps81dvzonzfeR3RF2/3ti/xV+pn7M2j+ddaO2mRWkPhWw8N2r6dpKfLcNvf/SLh5f7zvvXb/eie
                            vzt8A+FfD91rPh1dPn1LSreVZbq+m1CJN7LEn3ImX+P5H2r/ALf/AHz+iv7Os19eeEpbGDT7nRLr
                            RvsdrZ/boPKf7Otuju6J/tu7r/wCs5BGPun0FoU32zxvPq62dtbaZp1m1vK6t/pu+V/nTb/zy+RH
                            /wC+6x/EN/pmifv9Tvl32DNLFNdt91ZfkRET/fepdKVrfw7fa8086X1/asu9PmRvId97sv8AD87P
                            trhfH+paC+h6fr2q2094lrLa3tqj73d1b5Ik2f3vNdKPskcvvHP/ABFv10GJE1W+gmlv2WWCxt22
                            bmWLekXy/wC38zf7leSfGDVY/E9xq2kNc6tf6PpNqkUVujb4mvGT55X/AL2xN/z/AMNdN8Y5l023
                            e2a2WHUNq3rW9um+WJW/1v8A6HXjnifWLmwvNbtmuZYdYiiWJruFtlpErJ/qv97Z8u/++9ZnTE80
                            1WHTNB1mXToJWv8ATJbO3e6u7hXSLcqfc2fxMnz/AD/3q8o8M3UFh4yuLuxbzrKVX8qKZm+Zd7fO
                            6/w70r1qHWPCHg3wh4o1DxDrly/iVtO2aBplpFvh+0S/fd3+fd8myvn/AETVFhi1KVmkS7llZVZv
                            739z/dqfhKOouLVrD7Pfagk80UqtFYzXHyRN+9SLfv8A7qOjrVDxB4k03QVXRtKvp3spXZ7y+h/d
                            fam/uPt+8iN91a4/WNWubiz0+0uZ55YYt+13lZki3tu+RP4f72z+9VS/1L7Zfqy2zPZRbkX/AGf4
                            fv1py8xl8Jp6TqFp4Z1JdU06XfcW9zFLEk0W9P3bLKr/AD/e+ZV+X+Jd1Z/j7xtP4y1+/wBavPsy
                            X9/dNLP9ni2o3+2vy/L/AMBrMa58lbhLzdNay7miSFvuy/w1gtdPGvlbdy7t21lroicdSoVdp3ev
                            +7Tvvt826mt/F8tOdldvlXZ/wKtjgGf8BptFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA
                            UUUUAFFFFABRRRQAUUUUAFFFFABRRTvLoAPLp6KtN2/3ad5dSWSp81WURTtX7m5qhX/aq3bIrq1Z
                            yO+lEfCjJsZf99qvwou77u/b/tVBbQ+Yv+7WrYW2xf8AermlI74xiXbOHfs/3Pu10eg6JPrFwkSx
                            bHrP0vTZby4SJV+9956+iPhL8Pd8qStF97/x2ub4jbm5DsPhd8Olhii3RbNq17xoOmrD5Squzb8n
                            +7WZomlLYQeUqr/crqNKhb+7/FXTGJzSkbdtZ/Km1f8AY+7TLmb7NE+7+Fq1URUtf4d/+3XC+Ode
                            Wwt3Xza3Ob4jkfH/AInXa8S/O7fwbq8S1u/379zL839//arY8W+J1uZWVZa831LVd9x/rd6VGp0/
                            ZLr6kqb2/wDQ6ytS1vZv+b/brMudS3tt83+Fq53Vbz97t3L/ALlGoh2q6tvZ2Zt/3vn/ALtYU158
                            v3l+Wori5X59rf8Aj1Zl/MvlMq/I9GpMpFLW79Ui3bt/8HyVwlzcNMz/AO1Wxrd5sZ1X+7XO7q1p
                            xOOtU+yJJTaVqStjgCiiigAooooAKKKKACiiigAooooAd96lXcv3aT7tElADaKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKAH/xVd021a8v7eNV+81Utv8AtV6F8L/Cb69rNvvXYnmo33d/8VRUlyxN
                            qUeeXKfT37N/w9idYrlomTd839+vt3wfpS2zRKvyJFtryn4UeD10fSbf5dm1a920q2aOz+VdlcHx
                            HvcvJHlNDWL+JLNF3V454wuYvvM3z/cr0PxDeeTE6/x14v4tvJUV2Z9/8dRKXIEYnm/ie/V2f/a+
                            SvNNbeK5uH3bnf7nz12GvXMXz/x/f/76rzzVZm3PubZ81cftDv5Tktb02B1fav3v9muUv9N3s7Ku
                            xP8Ad/2K66/+RX+b565y8RX+9/6FWxEonC6ppsbO+5WR9rVy9/YtbMvzV3Wqp8v3fu/7VcveJ50f
                            9+uqlU5Tgr0ozic626kq48O3bt/4FVVl/wCBV3qVzxJU+Ujp3mUSPuptUYj/APx2jayUbvloV/71
                            ADKdHT/l20eXQXykbUlS+XTHTbQQNo/hp+35aZQA7+Gn0zzKfvT+81ABRRHRv/u/eqDbmPuv/gmd
                            o+mL8QfEWpsyzXbaPLbun3UiWWWL73z/APTJv++6/RCzv5dSt7jyJ5Ib213Jazbf9UzP9xf9+vz3
                            /wCCbV1Fb694o8+BnRdOld/lTY6u8UX3vvbk/wDZ3r7q+2anDdJEs8r28Uq7rjciJtVP/Hvnrjqf
                            EelTj7pb1vXtT03xHb2OoTxvpktrFdX1xbwf6Qsv2hEt4v8AgdcVf3k9nr1xFqSwQxefeJeXbts8
                            ra/yS/7K70qHxn4nvLCX+z7O5tL/AFCW1ZJ7iG6+dlW4Tf8APs2+bsf5Urx343+MNc0fWbXSls18
                            MXF/a2tuz6zv2X9wtxKjo6M/9xUb/do5jaMTM02/sb/4c6fA08c2q3863Frd3H+qsJZ7iV3RH+9t
                            /uu/99P92vHfidHp/wBh1Dz3u4b3VNF+1L5UHz3Vxa3EqOjt93d877n/ALuxq9l8QeD7Oz/4Rfwv
                            ZwaFf3eowfbb77PqL+bpdrE++J/K/h+bftXfu215Z4h8Pa5NrOsXOlW1tNFfweVFp/2xJbuXa8tu
                            8tvE33d6Jub/AIBRIo+YPh7fXel+JfIj0a28Q/bopbWWxuIklSVdnzOm/wC66/eVv71el614ogsL
                            XQ9K1eC7m09Qt1FMqNFqFrK3ypFK7NtZdqfdb/gNeVW876bqlrdQyKrx3SuizL5T/K3y/d+791l+
                            X5a9P8SW3iCbXNVW7nW/1KWJIlT/AFvlPLsSLev3dyRO+1k/ifdW5zxjymfpMWpeBfE2mWPg/UrH
                            U9Y1GWKWz1D/AFrxb/4V3fL8291b/cf/AHq/UD4P+IbrxJo0s88f2CW8W1ddQuF3y3S+UiPvT+8j
                            712f7lfAXh/4St4E8UfCSW5g+369qNmniJrdpEdNqyr9l8pf4d8Wzdv+fd81fengxLnwx4Ne8vLm
                            2fUFla4uvsi7IomVNlxF/wAAes5FxOh0HytH1nxLBbafqk13efZ7pnSf/RGl37Nnzfdf5PmrM8Ve
                            KrH+1orFom+0RXnmvpKNvlZt6JFu/wBlH2PXGeG/EP2DVvFt015JNqt/qfzaZDK9ulrbxIiI9wrf
                            d3/61dn3t9c/4hufEeg3/iDUl1XwvYRf6PFZ6hueK7WVvuf3/NZN/wB/5dtRzG0o+8cv4z1ufSrf
                            U75vMfU5bqWylhRd+1WfZ9//AGP/AIuvOvGdm3h6z8UK08eyXTlvZ/4083f89uj/ADruT72/+99y
                            vR/EHiTTdH8B2+oWi6grX6z2UmratKrXF/dMnzvZRL/qv9p2r5i8T+P9XTUv7VvrGxmt4olsrXSb
                            hX8rayOifJv/AHro/wDH/sbqQjiPih8RLzxp/Y9rJa2kVvbwLZadaWibUT5FVZX/AIvN3b/v/wB6
                            uJ16GWwuLi28rZcS/LL/AAJu/vpWbczO1/KzTrM6xK0Vw7fd+62//ep+qR7orG5bUFudyfvIot2+
                            Jv7v/s27/brTlOfm5CteTXP2j7Nc3Ox4v9vZVWS6lt9k7T77iVldkX/Z/vVUvrnzliVl2SqvzS7v
                            vVEu2aaXzZ9i/wB/726tuU5pVC7f3MWsXV3eMywyyy71hRfkrKk3zMzO3zrQ/wC5b5XqJJWTdtqz
                            mlKJH5dNp2+m1ZiFFFFABRRRQAu6koooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAKKKKACiinr/AHqABepqx/B/t1DViFPmqJG1MeifNV22/u1EkLJ/drSs7X5X3bfvVzSkerTi
                            WLNFdk+Vq3rCzab5V3b/ALnyVmWCbG+Zfu/x16n8NPBcusXSStF97/ZrjOyMeU7D4V+APtlxFK0T
                            J/wGvqLwr4bi0q3i2rsrF8DeFV0uzT91sevRdN0391tX+GtoxOapIfbQ7Nifx1taamyJGWmpYfcZ
                            qydb16LSo3Zfk2/+PV1HN8Rra34hjs7d/mV3VdlfPnxL8YNNviWX59zU3xn8RWmllXd8n+9sryzV
                            dYa/uvmb52/2qjU2jHkKN/ft5v3m+ZmT/vmsLUJP7zf+O1bvLxUZNv8Atfw/c3Vz9zqXzPub7tGp
                            RXuZtn8W+sG8vFeWJmb5/uVNqV1vZ9v31/ufxVzOpXmyTbv2bWZF/wBqjUmUh9zc+WyNu/irE1LW
                            Nn3WV/8AZqlrepeY2xW2LWI8zO1axic0qkYk1/c+dL8v/fVVPvPTJKK2j7pwSlzy5g8ym0UUEBRR
                            RQAUUUUAFFFFABRRRQAUUUUAFPVqTzKbQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU/b92mUUAW
                            beFppVjX+JttfY/7NPw3877PctF86tvbev8AFXy14Hsf7Q163Vl3/Oq1+mvwE8JRaV4cst6rvlVf
                            +AVx15Hq4SH2j1rw9pv2O3Ra6Zbr7Nb7FrPs02MlWHff8v3N1c0TvkZOq/vleVv9yvEvHk0v71V3
                            f8Ar2vUr+KztXib77V5P4nhW/wB6wf3t++oqm0Dxe8T/AEj5q4LxBbb5flb733a9N16z+xs/yqn+
                            /XmOt7/tD7f4v79c3KdPMcrqrr86r/d2Vy+pXPk/xbP71dLrEPkxf7f364zVfvOv3/mrYiUuYxdV
                            uWkXdurnLp5YVfb8lbV/9512/wCxWRJ/q33L/DW1P4jmqfCY7bpGSoXTdVh02NUUld8TypRImtyO
                            9MdKs5pKfMYypx+yVXplWXT+9UO3azVqc0o8ofKtC/NTKdHQQPd91FM8ylVqmxfMJ81DvuopV+X7
                            1UQMop+35qZQA7zKPu0feqRP9dQB9i/8E99aW2+I2safbWcVzdXGmSytNL9zarxfJ/wP/vqvue88
                            Tz6HcXatL5zrattt3i+SL/Y/2v8Afr88/wBhPXl0H4zWi3PmQ29/FLZRTfwrL5Tvt/8AHa+0viWl
                            8lraanbNHDqFhfNdWsMLJL5qsmx3dP8AcevNq+7M+hoR9wdqvjDydU0dls4U0+Wzl8/Z9ye4+/F+
                            6/h+RK8v1J9M8T+OtCvtVl1TUruKxuL37ddzvsiuFd0t7VEdPuomz5/4qseM9budVuolZms3s7xU
                            sX8j/X3HlOmz7/8AG77a5fSrzxDZ+Kn1q21VdNtNSl+ytbzea9xa7nd0dE/5a7HRFZETb89HNzHT
                            ynqFzptneXC+JWWS812JbW30xLux/e2e2LZdxbF2ebF8+5d+7+981eb/ABR0FbzTdTZdcWbXZYLe
                            9sdQmb7K9gq3D797rs+X5/8AgO+vQNEv4rnxNZarrWvXd/4l1KW48h7Gwl/dPFF/x8J87qv30bZ/
                            t1N4h8MWOq+H9Q0qe5vtVlXTG0qeFYIkillnld9iP/seU/8AH/BVHKfD/wANPDdz4k+IVro+s6fc
                            39k63Sywp+92rsd/3TJ/t/N/davpi20Hw98KNc0exbSm1u7XRbV2SZtn2rz3+dP7yMiPuRHbd+6+
                            /Xh/w30nU/Dfxe8NeH7nz7CVJZ7Rvsm5XlXym2P/AHWZP4v7tfYGt2Ft4ev72+a2W/l8qKKzmTe8
                            Ut/An/fTbN7/APAqf2QPKfGej6lbeH/hJ4uuYFs7eK6l022u0b7R9vuot8sSeV8myKJ02KnzN/fd
                            q+pvD00vg/4d+H4G0G0sHtYmt/7P2+bdxSy7HleX5/7++Vv9+vKdNkgvvhykt9F/aV14c1Nn0WZL
                            V7hPt8tx5rvEnyLt+b5n3/31r165SWHwfp8qxTv9vZr2e+uIPs93ub777G+6stQOJ4uniHULPx5r
                            elNbX2paFeRLq8Fu8W+L+55ssv3l+f8Av/Ii7Kwby51XWLWy0PQ7aydGla91H79xKu7fvTe3y/I6
                            Oy/7ibP9ro/E1hPpt5p7T69q2g6fdT/2VPqCLue4sJd7vFKip/fRF+T+/urnPGcNylndaZbK15aX
                            F9EuyFfKuJV8qX5Nn3tqJF87/wAXz1jH3TplI8N8c69bapY299qrR6lplvdO72KStF57RS7HdnX/
                            AFTOi7fkT5q4LxN4kudKeW6tra2s7i/lbbC7vL9gVXfZsRv7i/ddq9N8W232/VJbOx0iNNMllVrN
                            EV0dpYk+/wDc3K2/5tqferyLxnatYafFPO0H2rUVaWdHn824i+f59zfdXduX5fvVZjI8qvJHmv5Z
                            Gl85mbezKv3v4qbfKrSJHFL5yfwv8yKv95fmroNS0O6tL+3kvZbSJpLeK9XZKjbkZUZF2r/Ft/hr
                            J8QPPeXT3c7b3lbzX+Tam5v9mu+J5tTm5THby44k+VvN3fN/dZaj+yypF5jfIlaP29oWeeCBYSy/
                            f2/db+8v92sl9ztuZvvVcTgkN/i2rTKd/F81P2bVqyCKinfLTaACinbWo2tQA2inqu//AHqZQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFLtoAclOp6Jup8cO5l/u1Bt
                            GPMJ5dW7ZPmX7tNRGdfl21oW9vt+6tRKR30okqQ/N/8AEVp2dsr7Ny/Ov3arWcO/7v8Ae2V0Glaa
                            140W1V82uCUjvia3hLw82t3iKq/J/u19a/C7wTFYWqM0Sp8vy1wXwc8ALti3R/P8v/slfSWiaOts
                            qfL8irsq4x5wqVPsmhpWm7It237q766vTbZdqf8AxdVbC2WSLb/eq69ytnE+7+Guzl5Tg5g1W8Ww
                            t3ZfuLXzv8V/HGxpYlauy8f/ABCWzjliVlR9tfKXjnxPLNeS/Nvdt38X36xkbRjykWq+J2uXfdKz
                            u3+zWS+vNtTbt/76rn3uW8t/76/eqr9sbzUZqepR0FzqTfeZvnrHuZm819rNVeG5Z/mbd833k3VU
                            vJtny7aCZDLy8/u7t/8AE/8AerktbvPmRlbe7NvrTvrzZE7L/wCON92uUuZt6/d+SrIqfCVbqbzW
                            3VX3UM2Wof73410Hl1Jc0hlFFFBmFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUA
                            FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFF
                            ABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUA
                            FFFFABRRRQAUUUUAFFFFABTv7tNp0dAHr3wH0FtY8TWn9/dv+7X6deANK+waTbqq/MqrXwF+y1o6
                            za5by/3W2NX6K+Hv3MEUa/xLXm1Jc0j6HDR5aRvbPuLTn3Iv/oNWbazZ/m+XZ/t1a+xxTN833FqD
                            TU5zXtH86z89vkf7i/LXmviLy7C1dVX7vyN/fWvWvE959ms/u70rxrxVMv2eWVt2/wD8cokVA8f8
                            Q3jXl18y/JXCa8i2zbdqu7fd+au41597P8q7Pm2/7Vef62rTXG5v+A1H2jpOF1u5+Z1b5K5S8ddv
                            9+uzv9NaZtzf3q5y8s1tW2t89QZHKalbK8W5W/e7a5q4Rnjbau+u11WFYV2s1crcIu/+/VwkVL3z
                            HuNytu21C6Mnyt/wKr1zb/Mu3/gNV5kaT9638Vd8TzakSo0O9X/vLR5dTD5C21tlJI3935K0Obl+
                            0ReXUTL9+pU+781D/NQRKPNEq/7tMqw6bai2/NWpxyjyDKKKKCB6v/epKbRQA6j7j0q/NTqCxiU9
                            fmoZavWcO+RP/QaiRdOPMegfCDxJeeG/HXh2+tp/LS1vIpdkzbYm/vs3/AGav0K+Iutq8D3NsttN
                            DcQfuH3fP8z/AMD/AN16/NfQdttcRMyr5W75t6/w/wAf+7X3B8Jr6bWvh/aaVJGq61pexIHvG3br
                            V3/df77Ov9z7teXXkfQ0PciMh1hl1a0gZraZJZ4r2J03ukTLKj7E+f7r7HXen8VUrDTdXuYruC+t
                            lhil/wBIV5rpPNaJpX81Ld9/y7HVt29vu16XbaDqGvXmq6m09o9xawS6e0LwbPstvs+/5S/xP/D9
                            3+9/s10Hh/4b3l5r3h/T7rw5pM1jFeeaztc/YpZV2b9/735m2bE/ur89VGJcpHM3+lXz+MIoLnT2
                            mRpVuoktGS3uPs/lI6bPn+78nzfd3NWxbeHtXW31VYF1LR7vWWluJbi7WKWWzaVH2fJ/0y2PXtfh
                            j4RXWpXWt6n4l1X+zft9zL59jYzxbIvkRInf+6uz+GJtv8X8dS694SvLa8t4NIljmvV8qKd9QZ5b
                            FYme4Tzf+msr/Oqxb/7jPW0YnH7SJ8seM5tP034v/DXT76Dztbs7OW3i8lkl3XDOmx0iX5tyIm/f
                            9z5/96vbbyz1fXvHnheVteX+z9GaK6+z3HlOkTNFsld/+mr+a6/7O+uO+OnhfxRoOk+CtP0PwnY3
                            jxawzz+LLtUfUIIpUe3iifciKqv5v8Dt9yvbtE8H6npugo2oTx6J4gv4orKK48hG3StE+/fEz7mZ
                            It+3Y/3kStNSOYpXPwl0+z8PeFLG5VXt11aW9327booNtv5ro/8Avt8v/A67PxJYLeSxN5X2+7lW
                            KJZrf7ksS/I//wAUqVT1LR9Q1TXP7D8PahL4eTRLNIoNQu13w3nmv5u9Pv7m2bvmaup8GfDq20fw
                            /oWlXN5d6kmksqwPdsnmxbU2fw/ef+L/AIHQY+1Pnz4hQ6x4PhsfDnhWOXVfGXiC8s207ULiDf8A
                            Y7CKX97sX+F/mfc1P8ZfA2+/4TeXXrlo4beVvm2NsddqO3yf9dfnr6yvNN0+wuEnggjm1jyGT/gL
                            P9xvk/v15/4t020S61PWdV1CPR4pfstlZ2Lt8kTLvd0/4H8n/AU/26zlTL9pzHyfqvwlawWy1q2Z
                            odbuvNurWx3futObf+6+f+Jnry+/+BWh6lqX9g3l82j2V5dLda1reofciZfnuHi2p83yI/8AwLZX
                            1n4q8N+IfDd/rvihvI167l+zppljCr/La7/v+V/qt235t/8AdrzTZo1z8ULSfxtrjaVpksvlWv2d
                            m2S2/lebcPFEqbm+eJE3bP46RtzH54ax4BjvvFWoWelf8TLT1nZLO+hXykli37UldP4F2fNt+989
                            butfDLWrCfU7YNbWyNZ/Z53u0RnVl/exf7rOybN1fUCfC6XQZdblaz/sHSpb9n0nw9DF9ouLOLfs
                            824lb+J9m7/ernP+EJs3v9Vln1xtSiltfNur64VJX+0K7onybP4ESnzEez5j4/fwDPDLdJeS77hG
                            +5Dufd/t1Tbw3KsrsyNMqp8vkozbNz7U3f8AAvl219b3XgmxsFivG+dPKW4lu3Xyn81ndHRIv7tM
                            174Y6RoOrWk8dz50V/5V7fWluqpcWcW/c6On8W/73/odHtJB9WifIaeG7lZHgljbzVVd6OrfKzPt
                            +b/dpNBhi0rUnurpY3ez+dbeZfklb+5XtvjObSPt+oRW32m8spZ2RbtokS4liZ/kfZ93du2/In9+
                            ua034by6wtwvlLDtX/U7/nerjXI+qRPH0s57mKWRI/ki+Z3/ALtRPC0Ozb/vV71qngOx0/w1p62q
                            s99Kz3V1bu6okSK+xfvf99Vzt54Pj1KWX5okiXb86/OjN/tuv8Nbe0Mfqx5P9nkZd3+1t3Uj20qM
                            +5W+WvSdb8Jx2d5cLbTrNEkuyXd/Eyp99f8AZ3Vg6xYedcPtVtnzJ8i/wrR7QiWGONRtjUbdzVv2
                            /h7zpf3reSlWX0eK2bynVkdJVeR2/hX/AGf71X7SJj7GZzLptqKtO8s9m+WJWa38xkVmqkkW7dT5
                            jGUeQhop2z5d1NqiAooooAKKKf8A7tADKft3VLb2zTS7V+9WrbaUztt+5/eqeYvlMpbZ5E3LQ8Ox
                            q6BNHnRf7m5qqXNmyM/3fu0uYv2Zjsq7ab/wGrs1s38VRPbf7VHMEolXdRuqR4dlDpVkcpFRT9v8
                            NO2baCCPdS+XT6Km5fKLtpyJvajy6lRCu75tn96kXGmEcO773yLUqLv/AIf4qIYXm+6taFtCz7GX
                            +9sWsZSO+MBttbbJUVfv/wAXzVoQw7Nn3nSmW1n+9Zl/vVq21mz/AHfk/vVzSkdlOI+wt/3qbVr1
                            j4aeCZby6t523P8AN8vy1yngzwrLrWpRbVZ0r6w+HXgb7BbxMy7HVd61ES5e4dX4M0FdNtYlVdny
                            /NXothZs6ptrK0rSmRk2/IldhDCtnap/BtrpiccpEXnLZxb/AO7Xn/j/AMcx2Fm+1vvf8Ap3xC8c
                            xaVFtWXY+1vutXz74t8Wtfq6r5n+/urWQRic5458cy3Msq7m/wBqvLL+8+0zPure17983yt97+Dd
                            XLzJ5O9v42rniali52rb7V/+zrMvHZNir8nzfN/u0/7Tv3/7tVLmb5vm/u1pqTItpNv/AItlZmpX
                            K/8Aju9npr3nyptX+LZWJqt4yK/yt/co1IMrVL7zpn2/c/h21ku29qsXHz/N8qVV3fLitonBUkMo
                            oorU5gooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
                            KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoo
                            ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiii
                            gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKA
                            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
                            KKKACnbKbTo6APrP9lFN+pW7fc3V+gHh6HfEjNX5+fsqTbL203f8B+b71ff2gzMyp8m9K8qp8R9J
                            S+A7K2m/dqqr81WETyV/vvWVbXPk79q/7FaH2zfs3bfl+f7tXEJGZ4tRU06ZmrwrxC/2+88pfuV7
                            V4z828s3iXb8y/frzV9B8n7Q0/8AD92okXA8s8VaV5Nu7fx/cry3VYdjP8u/bXsviF2Rni/j2/8A
                            s9eaXlmv2h9y/JuqDpPOtVTYrqq7K4+/f5t38f8Aceu48Tp5Mr7Ub5H2Vwl5bPcyuztUEHNakkrs
                            /wD7JWJ5Ksz7v7rJXR6lttlrmrl2dty/c+/TLj8JXuU8mX5f4fn/AN6sq4+7uVdm1q0pnbc+7b83
                            yf8AAazLl9jbVrppnHUK7/d3Urr+8bb/AOOUkybGo+/92uk4CKnyUUySgiQMtQOrIatfeqF/vVUS
                            KkeaJBv9qZVh0qJVrY45R5BlFLtqSOggbu2tTqHSnp/s/eqS4j4YdzJu+7WlZ23zPuWqsMPz7fl/
                            +KrXtl2fw/PXLUkerQpmnYw7021778E/Ft5YeJtP+2XjTWl55tq0Lts8hfk2Or/7H8NeH6bCvmpu
                            /iX76fcr1D4VwtqvjfQoIIoJvKl37Lvf8ytsR3+X7zfPu/4BXGer8MT9APhd4M0V7eWDUP7Zmdt1
                            vapCrpb+U3332r/F/t16X4nS20rRbu6ntLma4ig+ywfZ0+9LLs2IlZXgbR77SbDzVlV3Xc8SQ/fb
                            /Y/8cr0J0b7PaXM+6FGgV1Tb5qRNs/8AZK6Ynm1Je8NubOC5s7fZLHZy28tvcNb2/wAkXmxIn3//
                            AB+rut2E/jDVJbPUJ4IbeW1i8j7Iv+ltdRXHmu+/+FUR4vk/23rHs7l7/wAprG8aGWW1iltfOi3o
                            rN87vs/3K5/SvEOm6V4y1vwrPPq2vTWaxXrX259kXn75fKidfu/cZVb/AHK3Oc6/4i+AfD/jPwPe
                            +G76+im1Pz4tQsb7f8s8trLFL5W7+Jt6bGX+69Qar4SXVfGFlL5Ud49hKstjabvkguGTe8r/AMO7
                            Zv2f79Ynjjydd+OHh/RdD1iO98P+HNFutQn0mJd39m6oq7bV2lT+KWK4uNyO38G6tO5s76w8CvZ/
                            2gsOp+Q32+ZF/i8rY+z/AIG9BnE6jy7tnW0ZI/skarFZp5u7ev8AG/8AwP5mrd8NzRSRXs63KzXd
                            nP8AZ97t8iy7N+z/AH9jpXK6JpVt4Y0bT9PsZZHt7CJbWBPv7f8Agf8AFXS2GjxaVa6rbeRHDbys
                            11fXCsjI0qps/wC+/kSgJFTVby8htbuVYGm1NZYniSGXZ5v+x/up8+7/AHK4XXrPxC/ijWvELtHN
                            pirFb2du8W//AEfZ/pcv+87/AC/8Arorb+2r/S0nvvs1hLeansdLdd7wWC/ci+b+J/7/APt1n+J/
                            7TvPFUunvB9j8KWcETLfO372W6V98sSJ/dSJPv8A+3VfEEfdPNPGitolnqGoW0k6abYaitl/ZKTo
                            n2y6nT5EXd/D8/3K861bwfPr3xIT4jaq3ky2Fqtk2k6ZL5tuvyPvT/e/vf7Neu/GjwN4d+JfxK8L
                            3k9tHf6FpMcTxXdu/wB6837kd/4ZVRE+9XmEOlxXlxe6nqU8l/p8sS3v9mWK+UlrEz7HT5fvb9lc
                            dQ7KUuaJ5z4h23lx4Xtra5ubOW8VpdTTc7/bLhndE2bv4U3/APj9Y8OiwQ2bf6NHDLLPcWn2F/nR
                            9vyeV/vI7vXYaVbW1/4t0rSNV1Jbx4ttvFqCbPKi2/cf/vvYtcr4VfUNa8H6rfXO17izurj9y67J
                            bpmf59n++6bqR1GT4hhsX1LUJW3QxeUqRInyIvzukrv/AA/Jsf5K8/8AEPjC20eysrZotm6L5bt1
                            dEaLY6In/AH/APHHrtrDRLzxPpOqtp9tPeWnkf2hPplv8+23if78rt/cd3V0/ibe1eL+OfGF5c2G
                            j+FWij+zxSvexTPEjy+UybPnf/x6pkalTTfDD+J5bjV7lfsEUW5Nm77u77j7P9//ANDrq9bfSLDU
                            nXSrO5TR7qLevnN/pEXybHd/9nf91Kx9N1JdKt7S5ZZ/KVVdYZvk89V+Tfs/33T5P9imKl54k8R3
                            Fs1zHDZSyxXF4/yfdX597o33VRPl2JUESkMtk0+/ZJbmL7Hbras7O7b9qqmxH/33rC1V7nSrq30x
                            bZrZ22y/vlRPvfc+T+Jf4qrpr2malrmu3jX0dnFar5VnY7d6XS79jp/u/wAVYS6lc3mrW+oXNyv3
                            m2vNK7+V8mxP++Eqxmx42sIvD2pXdtcqupan9xprTZsibfvf/gNcPfzb5bKBpV3KrP8Ad/hatW51
                            W+hs9Tuop/8AiWXDfZXuP7y/I2xf7uzdWFps1ja3H2m5g+2JLE22F2+Rf9uny8xnzcoPbXdtPFbN
                            AsPzb1ab+7s+T/vus/WngW1RmlZ7jzW3Kq/98fPVnxx421XxnqMVzfNH50US2+2Fdm1U+Vfu1yM1
                            403zN8/y7FX+7XTGmccqvKS3l8tztX7if3UrPebfRNM8zbmoDLJt3K3/AAGujlPNlLnIuWWmU9v7
                            1MqzEKKKKACrdrD51wit91qYkLTSKqr96uq8MeHnuZU82Ntjf+g1EpG1OPMP0TRGuW2quz5tm+ur
                            s/DfzIzbv+AV0Xhjwqz2sqrEzpLLsV/7tdtb+FWsLVPlZ9yr8/8AGtc+p38p5Zc6Cvybvubl3pXN
                            X2lNG0u3d8v3d6/w17Bqum/LtZWT5fm/vo1cjqulfZmllVfkf+N/n3UBKJ5leWaws6qv8P8A3zWe
                            9s219q11F4ipuaRd/wB6s90VF+X/AL4qyOUwnh8v+69RP8y/7VaVzt8ray73qg3ys3/xNWRykOxf
                            vLTP4am+bd/fo27V+WqMfZjETf8Adp6Qt/eqVf8Aap+zetRzG0aYypUhb+7/ALdCfNVtEbam5aiU
                            jpjELe3rQtofJ2N9yhId6ptX5Kuw23nMit8lccpHZGJbs7ddnzf3q2NN02W8uEggXe7Vn20Lbtqq
                            u/7n+3/wCvcPg/4Anubr7TPF87VBfw+8d78Ivhv9jiiZl/hr33StH+zKiqvyL8lUvDGjxWduiqv3
                            V2V1v7qzj+b7jV0xiccpc5F5kVhEm777VzXi34gR2Fq8Stsfb/wBf9us/wAZ+J/JV1Vl/wDia8H8
                            SeIZ7lpV3VpqRGIeM/E7axeP838Wz/gNcTf3K+U7MzJVt3lmbzW++38dYWtzNHE+1v8Ax6lzGpzm
                            pX++X5V+RfvVhXl58v3lRNtS3N48cr7v4v8Ax6sq5m3t/DTH8ITXOxty/faqN5c/Lu/76qvcXn2Z
                            kXbsTd9+qV/quxniXc//ALK1GpiS20zPs3t8n36zdSm3tKysrpv+anvc/wCqWL+FfvVRv7lnX5v7
                            1VAip7kSq77/ALtV9vpzSU2uk82UuYKKKKCAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACnfw02nfw0AfS37Md40OqWS7m/76r9C/Ctzvt4mb+K
                            vzZ/ZzvGTWbf5v4v4f8Afr9FfDFz/odvuX7vz15dX4j6Sh/DPQIZmT5V/i+RqtpbM8rs3zuzbP8A
                            gNY8Nyr/ADK29/4q3bC532+5l+daUQkGq2e+z2qvz/xfNXnusaayb2Vtjv8AJXot/N5Nm7bfnryz
                            xPrDQwysqsj7d6olUETzLxU/2a4dmb5/uN8u/bXmniS8273Vfn3V215NLfrNIyt97e3+1XGa9Z/a
                            VdWX513bay+0dkTzfW9t429V+9/6FXFak7Q7127/APbruNbh+zS7V3fw1y+q2fnLu+X/AHKCOY4m
                            5/0xdrrWfcW0UMTpW3fwtD9376/d2Vzl4ktzs+b5/wC5QETKf5GfbWf/ABOzfJWhN8jf+O1UuU+V
                            9v8AFW1ORjWj9opTfvm+Wov+A1YdPJVN1Q7/ALrNXUebU90bTvLof7z7aKCP7o2omapd392oZKqI
                            SG0x6fR92mc0o8wynx01/wDWUi/LVGY/Z81SojK3+7T0T5at+T52/wCX7tRKR1QpkttCv3VatW2T
                            Y/8At/36z7WHyWTctadsmxfmrjl70j1aceU6Pw3YXOsX9rZ2cTTXEreVEn/j/wAn/AK+8v2PPgJY
                            vYW/iVrOezu7yLzZbe7bf/H+6fY33d//AMRXiX7JPwN/4T+//tC5g2S2c++KV2dUi8pE3vs+98+7
                            b/wB9tfpr4V0Gz02z+zfZo9ir9nWFGf9/Kv3JX/ib50ojHmCvV5fdLdtpq20UX2lm3/K6wwt8/7r
                            7+xP/HqZbW0vkWlzbQSQ2ktr9oXYv3fn/wBVLu/iro7mztv7S23Ks961jK63Hm7H++m//db/AG64
                            m/e88PfE7WNYXU2h8NWfh7ZBpjS/upb9riV5bh/4vu+Uu3/frqPN5uYyoZrzwroemS+IZYbzWGb/
                            AI+9PXfEys7uiJt+b5E2bv8AvquV+Iviq+0DwRq+h6RfRaV49v8AWLWyXUIdi/Y/Ni+1S3EXm/LL
                            B5CfL95d29fvK1M8fX+qzeMNK83SGmtLzTootYhR/Nt4r9Yt6W6uv3P3TblbZ89cj4ys/tn7X3wt
                            g8QjTb9f+FeLcQaTcS+b9lvPNlle42/8BliV6AO403wZ/wAIr8KpdF8P2f8Awj18q7Lq+vrpEdfN
                            R3uL24/iZkR9+x/4nSuz8W6ls1LT9FW+nS4v1it1mRfnb5N8v/jif+P1d8JQ6g/iDxB9pnjv9Ela
                            3eLTJot8sSsj73ll/i3/ACfJ/DsrP022vtY8YS3mps01var/AMS75vnWVndH/wDHNlZyGb159u0r
                            SZdQ0+KOZLVfNi86XyvPuP8AllFv/h/vNW74qtvt/g27nsV+0y/LKv8Acl/uO+3+H+KqngzUrbXr
                            B1udS+3r5sssT/fRYpfuIv8AtfPtqWHxsq61ouh21mz6nPbS3Urv+6Sziifajy/76/drWBnIbqWl
                            f8Jho2lWzRT+Us8VxcpD+63Mvz/P/dX/AGKzvGnjO203w7qUmnXNpNqV1AtlY2ism+eWWVEldE/2
                            FrcuXub/AEN5baee/bUomSBPubdyf+hP/t15Tq/wv0Xwb8RvBqpdMqaD4XurS6t5W3vdfaZYtrP/
                            AHdi28vzom756oI+8cl8Wry+Szez0rSL6wt9LtYntbjcn2f7Qv8AA+1/9Uife/vV5pqXjy2ez0Jr
                            aWWGWKCW6vGSLyreK3VHf/gXzolegaxf3P8AwjOsXksU9n4atfuTfI8TNFL8iPF9779ea+M9N8m3
                            u4LlY5ovKuN3k7ElWL/W/J/D/Bt+5XLI74/ynP22lW1hpeoS3zSX+oebK9qlvE/my3GzfEmxfvKn
                            3v7tV08eaV4Y1myl8hdSt9Nsbjz0+d/tUs6fI6P935P4t/3al1XXp9Kl0SxgWSwt/sbO0KNvdZZf
                            uO7/AHt2yuC1W/W20G7axnb7JEzW8SP8n2r5/n3/AO1v+X/gdI3OcX4l+L/BPw31jw5pVi1hd6tE
                            txdXG354rXf86f7O+vIrnwnqt5p//CVXlz9vlV/KiRF/1USfJv8Am+bbur134uvoPw9+Gujzrqra
                            l4y8Ryy3uo2PzvFa2v3LVP8Ae+422vLLPxbB421bT21W2l0q02/Z5/JV/lt1RPkT/wAcqQLFzNqG
                            vLZStOumxaDarcMkzfPLudHRIkX5W/g+/XNalba9eSpq9y0iXF+vy7G2Oq/c+dP4WdalTVYrNtQa
                            2tl8poPsTJN8+35//Qqz7+zvE8EJqKRXLxS3TRfbnn+SX/Y2fe3UcpkUPEELabpdjp8aw222dpVf
                            d88u7+Dcv8NdR8N7zwPpeu+IE8ZyalNosVjL/Z0Nonzy3jfMjs/+z/48tGifEvw58N/iXZeILbw5
                            H4k0+Kz8r+z9W/epFK0Wx3X+H79eT+Jtcn1q/u7nyPJill814kX5Fb5tv/oVbRiZSqcsTY8TaxYr
                            pNvZ6dPPMjJvlRvuK3/7Kp/3xXErMzr8zfd+7S26LN807fJu+b+/TJlVGbb/AHq2jGMfdOCVSUve
                            LF55j3HzSK7Mv3l+7VJh5Uu1v4aY9N3Vsc0pcw5mpPMpf/Q6ZQQP+Zv4aZRRQA9aXbvbC02t7QdK
                            a/V9sTPL/wAsttSXGPNI2/DPh+K81a1VlaGLbtZ/9r+/XrvgzwTeJLLt2zW6tsTZ99v+B10Hw6+E
                            X9vRRXPkRwtEuyXZ99dyJs317h4Y+G/9iWe777s2zZt/iX5N9YSPSjE4/QfCv9lW9v5sCp5u7b/v
                            bP46P7Hn+z3DeV8/8KbfvV6g+gy2cSLcovlN8+z77/NWZ/Zvk71Zd8X97+7U6nTynlWpeHlhs/Pb
                            7614p4hZvNeJWbYrfKjt91a+kPG1usOmvL8qIq76+YvFV4qNKytv2/7VZ8xfL7piaxDsuNvyon39
                            v92ucuZlh3r9/wCX+7Wnf3n2lnZfnRfkb5qwnfe3yq2zd81aHNyld5v71Qu2+XfVh4dsTt8tROvk
                            qnzf8BqyOUr7NtLjbU8f735dv3qfsV/urQXGJEnz/dX56ltk8l/mp0MOxt1WET5k+Ws5SNo0xvk7
                            2dl+7Wlb2e/YzL89N2eTs3LWhCjTfd/8crm5jaMR1nDvX5asWybJfm/vbKfb/dTcv/jm+uz8DeDJ
                            9b1ZP3TPFuX761B0m18NPAcut6kk7RfJuX5P4K+vvA3g+LR7VPl+esf4Y+BotKs7dmiX5fnr12ws
                            Ftl3Mq/drpjE46khlnZrZ2+5l/4HXD+P/FS6au2Jvn/uV1HifWFs7dlVtn/Aq+ffHOpS6ldS/vf8
                            7601MYxM/UvE8t48qs3zs2+uPuXaZnZW3vu/76qWb9yu5mbft+f/AGqJHV13f7NZGpSuYdkX3vvV
                            xmvXKpFt/wBnZXV6lct5Xy/7VeeeJ7z+Hd8/36CDnLy83r83zuu7bWPc37I3zf7lNv7zfL8vzutY
                            95Nsbcvz/wAHzVrqZFjUpt67m++33dlZLvtl/wBimzXDyL8zM+3/AMdqu0m75q1jE5pVImqjbNnm
                            /d27/wDbrMuX3bKV5tqxbf7tQu3zVcYkVKnPEioooqzjCiiigAooooAKKKKACiiigAooooAKKKKA
                            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
                            KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoo
                            ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiii
                            gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKA
                            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiin/N8tAHrXwKvPs3iO3Xd/nfX6
                            K+D7lrnSbdvm3+VX5m/CW8+zeI4fm2fMtfoh8PdSa50O1l++m1U3/wB75Ery6/xH0mE9+kexaI7P
                            v3ff/v10FtftCu1fuN93/Zrh7PWPJ+XdWxDf/abjY3ybfnrMuUTtrl4odB3N/tV5Pfq+pXDqq/J8
                            2569IsLn+1tNeBl+Va4/WP8AiWxOq/xNsetSInnPiGwgs22xRKibf++a8v8AEltLNv8AIiZPvf7l
                            ewX9hPNL5rfOrfdT+7WLquj/AGa3+aD726p5TaJ883+j7GeWf+8yVyWt20W35a9b1uwZGf7T/F8j
                            V5Z4nRYW2r8iLuqDblOC1KH918q//tVz9zCyK+5mT5f4K6DUnaZfl+dF/grmZnba+75HWgyMeZPm
                            +b/7Oquxfk3LUtz97dTGh3xfL8lOIqkjNvJt7f7NQ/fVKfN956Z96u88qpIX/eqJP9dUlNkqomPK
                            D/NTKfvX+7TG/u1JoRUP9ynOlMT/AFVWcsv5Qb/Vil/2KPO/u06171Qi2m75EVavIn8K1RhVvuqv
                            3mrTt9u19vz1yVD06US3bJs+b/0OvQPg34A1D4i+OdK0qxgkmTz182WGLckSrvdF/wCBtXDWyM7I
                            u3znb7vy/eZq/Rb9hv4Uz+E/BtxrOqxz2Fxft8ibf9a3/s3y/drA76kuWPMfSXwi8B6V4J0mKzaK
                            0S7+/P8AZ1+SX5Pn/wDQ/wDx+vYNN0dkZJVnaZ2ilfe//LJlTZsesqz0dXW7ggiV3i/eq+1U3bvn
                            2f8AjldBbWcD6bFfX0tzYPFF+9Z/v7WrpjE8epLmMK6mg03xHpl5+4TUkVdN8l4HfzVldN7p/v1w
                            /jKH/hLtB1vT7adbCW6nuNupqyPbwLE/lJK7t96J/K+b/frV1bxhF4Z8b2MuoXkOpeEvESwWGhag
                            jpsiutkreUv95pdu3d/wGuS1XQdTS4TRZby2s/ClroF/b6naTQeakrSpviiSX+6m99397ZWsggcd
                            oPxg0dPFXxD0251Bb+bwffWGtXkOmM90l1brZRRSyp/dS33NuT7vyVgeCde8OfEL9tbxhrnhXUrT
                            xJb6XoejabpV8mx4vmil3ojf3fl/g/irasdXtrTRfEGj6DBpraxr3heWyuorf915t01lFFF+9+9t
                            +T5d/wB7fXFfsi/DGD9ny/8ADl5rli1zF4t0W3233lIkthfy7/tFl5X3l8qKJG3v8u56RrKP2j6z
                            s00XTdDlvIJ/9bLFFLDM33Wid0f73+29VNEs76zS3nvIF/1rSy2kK/e/ufP/AN81d8UW2l2Om3C3
                            a+dFYRb54Vi+dm++uz/gW1m/vUzVdum2+hfaZWSW8VYok3bPNanI54lnwZYL5WoW1zpi2HzL5Fuj
                            fPt/v/7r0zW9E+02ry2t41hd+avnvC372WJX/wCPff8A3asXKfbF+0q3kp5uxpnb59q/wb6wrzWP
                            Evh7Vtd1DTLO01W0v2s7XTtPmXY7t/y8XDv/ALn8H+xSGb/h/XtM1zx54ibTLxU1XQdOaJ4ml/0K
                            BpUife/8O5Nn/fNeJXPi3TNb8P8AiCXSPFEetvYNKmseJHi3pdLFE8r+U/8Ad3vtXZ8tM+Iuq3Nz
                            oNx4C+G/2aGXVL6W91aa4idE/snerXEru33fNfev+69YHxU+JelWt7p+i+GtPhe91S1aKC0sYNlj
                            YW8SbPNdPu7dibVrPmKhH3jj/EMLXl5p/hzT4L7QdEla3uNRmvv3v2+4aXfFs/u/P/6HXOfE7xJb
                            aDq1vqGoXLb7pvKih27/ADbXzU37P9zYlXdQ8SW2js63OoT3l7a/Z7hru4bYiqvzumz/AG68a1K/
                            bxbLLeWNnc3OpxNdXCzXa/JFa7Pn2/8AAHrM7iu+qS6PbyzrFfarerOt1LcO2/ylb7j/APAPu/8A
                            AKZqs0HiHw49ss8em2WlstwqTMnmzyyvvdP/AGapte8VXN/p3h+20ryLP7LKtveX0zf69Fl+RET/
                            AGN6/wDj9eSfEvwxBYapLc3Msk0srN9h2fI9wyu/73/den8I/iLvj/W9M8Q+ILK8VW2RRfZVSZfv
                            Kv3Hf/viud1VNQmure8VlhtLyVXgm2/wqjpsSn+HtN1Cz0u3vJ4IES8l8pppm+f5U+5XM+J/EMr2
                            FlZ/aV2WE7eUn39u7ZvpB8BSv7yeza7s1n3v5rbk/vVn3mpKln9hW5nvIol82K3SX90sv9/ZVTVJ
                            pftEsrTqj7W27qzHvJdKldVZd8sS/PD/AA1XKY8wurapLcWsXkK0Nq67GZv4n/iqK2igmvoor6VY
                            Ytu5mi/ib/aqe48/Um0/Q4p1dIpdi/3NzVFc39z4fj1XSpYoJnlZUa4+8/y/3HroicdSRj3yRQ3U
                            v2b54f4Xqozt92nujJsZvuNUe5sFVPy1tE45SI6Kf8u7+5Sb/m3UEDaKKf8ALtoAM/7TUbflzRsr
                            b1fVINSeJorOK2RIvK2J/wChUFxjzGfp9o15Oqr93+Kvoz4OeBrbWItPkW2kS7in3s7t8jLvrgvh
                            X4A/t7ULdp4vvS/3d38dfoN8HPhQuieVFBbKj/xVjL3jvpx5YmT4G8Af2J9olg3JL5v71K7250H9
                            1FK33VX/AL6ruLbwla6PLLLF/F87LVLVbOKGz+Zd6M9ZanScPf2v2y3iZYtjqvy/7VclqtzFpUL/
                            AGlldNv3Ntdbf7kv/KZf3X/LL+41fPnxj8VNpt/9miZd/wA33Kw5jaMTlfiv4z8m3ls4F+RvnX/d
                            r551W5aa4+b+781dBr2t3Oq3ku7c77m/4B89YWpTed8/8e2r5i/smJ5LOrturPSFn+Vm31oOksNx
                            /wCPulV7m287fRzGZV+R28rbVR02SbV/hq3DNsX5fv1CkK7W/v1uZConzbv+A05F272X/gVS26Kl
                            TKjfNu+9/wCy1jKR0xph9mbb8y1YSFfs/mt9+nJ+5XazfO3/AKDU1tDvZGVKwkdPKMtrZrn73yPW
                            mkLWy7f7zVDbI3yf+yV23hLwZPr1/Evlfud3zVBqS+D/AAlLr10i+VvRtu3/AHa+rfhp8NINHtYm
                            ni/e0/4afC6DSrW3laLe7V7LpuiKiIzLsRV+X5avlOGpIsaJpSw2qLt+7/47R4h1L7Dbu29amvLz
                            7Hbu33P4K838Ya21yzxf3q2+yc3Kcz4h8QteXUq7v9jZXG36b1+b+L/0Gtia2Z7h2b56z7z7u2ka
                            nH6rZ/vfu/JurKuX8nzdv8VdFqqbIXZW+SuC1XUmhuE2t97cn3qB8wX9z+6rzzxO67XZvv11F5c7
                            1dll+6tcfrHz2/zfOm75noMzhPOl899y74t3zf7NNuYVSJ2Zvn+ZFSrt5CqXUW77nzVnp/x7oq/c
                            3b66DnkY7oyU1uu2rtztf+HZVRPmraJwVI8shiJuptO+7TaoxCiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAp7fdWmUUAdH4NuWs/
                            ENu6/e3ba+/fhjrH/Emt03f3XX/Yr89NBdodSt2X56+2/hFqX2zS4lZvk+X5P9qvNxPxHvZf8PKe
                            66bqu/Zub563dK1jZcbd29N1edabN+92t9z+/wDx10GlbnldlfZ82/8Av1x8x6tSJ7n4Y1W2h0uW
                            Vtu9v7/8Nc5ef6TdPLc/6pm+/wDwf98VL4Mhe8s3Xds2Nv2VoXNhFtTcvybvv10xOD4DjbnTZby4
                            llVv3Xm7Itn92q+qwrc27ttXeq7Fru4dKtoV+8yVy2sWcENvcbXZ9qVqEZHz/wCMLCX7RK33NleK
                            +LYd9xt/g3NXvvjlGe4dVXYi/wDj1eOeLbP5vl27/v765zsPMr+z8n5f4v8AbrnLmz8nfu+5Xcar
                            5U3msv8Ae+5/e+SuC1h5WZ1+bZ/D81BznOXj7Jdq/wC/WfczbF2tVuZGSX5l/wB75qx7mTfK7VtT
                            iZ1JcpFs67qd93ZRu+/R/D8tdR5v94Kav3f71M/hp/8AvfJQWH8Tf7lDbf7tOprf7NMkilWmLtqx
                            Mu771V6owkMf/ap6L83zLRQn+uqjH7RdRlVk+b5N1adt91NtZKJu31o27qjfN/3xXJUPVpHrHwL8
                            G3XjbxiunwaQ1/DNF5P2veyfZW81Njo3977i7fvbXav168DeEovD2k6ZpSxR+VFEqMm5/l+T53r4
                            f/4J7+ErO/a01dZWSWK8ukvLd/n89V+z7P8Avjen/j9ffGmp9gurdN06Sysqb0/vS/33pRCtKXwn
                            TWf2NLr7Hc3kcMsu1ltJvk/g/g/2kRP/AB+tzUtS1NUsYLT+z4Xv3ZfOun3OvyfJ+6/i/wDZawLp
                            INb1y08+eSwm0ueKKf5f9b8+/wD76/0dP++64/x58SGb4jaJJEs9tF4cvovNdIHlfUVut9ukW/8A
                            hVHdJWb/AGErp+E4+XmOG17R/Dnwu+H/AIP8X+NvEt3DpXhWJLWxTatxaNcNcfJetF97dv8A++Vr
                            N0q28Z23gW9sYL6xs9Tisbiyim8QxPcJf7flS6fbs2q6Rbtn8O9K6D4nXPhHUtD8QQeLF1DxDo8u
                            q2tldW93F+6TfLEkUtumz90ru+3f/tvVTxbrGtJYJbaHc/2bd3+v/Zb641BUleKJn8pEiT/prsdl
                            /wB+sZHTE5f4M2cfi3+zfFUljF9u8QWthqsumW/y3st1AnlPFul/1SxbE/77rU/ZV8I3vxK+InxH
                            +LXi/T4rF59alsPDtk11LM+lrEzQXW1Wfb87LEu5F+Z4n/h21B8Tvi1pvwxsLi+8Jxx/8JxZ2f8A
                            wjui6hdxNLaRXH3pfNT+Gd/4fvb1SvYdK1u2+Gnw+0fdYtf6grW9l9ntF3p9ondPNlf/AGUd3Znr
                            QiXMdlqUKv8A6S0SzPE3zLM2xP8AY3/7O+sWGSXVYrT+1V/02wn83zk+5E2x/uP/ALG+sTxDqt9r
                            evXHhyxvFh83bLfv/wA8tz/In/A/nb/gFaumzTvFdytP51w27ykdk8rbsfZ8n935Kr4jHlLfhvUI
                            prHxLLr0ENhpVneNFZ+dKn723RP9b/u1zniHXl8N2esX0+pzTahfyxJo+nw/wxNsTf8A7zvvrC+J
                            H9leM7X/AIRrWlksNPvLVbqea0+Tzdr/AD26J/tpTr7xhqHhvxBqbt4fg1W0tbOz1Wx0m0/4/pXl
                            TYlv83yr/qlajmLjE86+MfxX0HwD441L4SeGvDl/4h8deIILNrpvN229hFEiN8/8W3+L+62+uN8Z
                            +JNatrN4rO2kh1vVlWyvLjan7iJfN+0On+5vTb/v1n2/iG5h8M+IPjNqGh3eseONZ812htF+ewl+
                            5Fao/wDFFE6fN/erj9S1KfxV4fRtRvLmF5bX7RfJYtsiguG/exRO/wDtuj/crnkdNOmQ38OgQ3Dy
                            rLJYPEvm3T3fzvdNFsRP9pvkrj/GXirUofh/d61pEFy7aksunxTeUiRSs3+ti3f7H9+m6reQXPje
                            01prmR9VidrKBLhkdIpWtXd7h1X5fk+6u/8Av1xnifRPEs3wJ0zxBc6qtn4Ui1a6S12Mn7+63/vd
                            ife//Y3VRt/iOC0pZ7PTU0+5uftnlQfaIt/yfN/Aj/7X+3TPGXja+0eZ9GWSK/1tl+z3Wof61Ird
                            k+SJEb5V2f3qz3v4tE8L2ur3N4rytPs+yKv7112I6S/7vzVwqQvqt156xsiS/wCkXMrtv+Xf8lZh
                            zHVWd5Y+Fdk98zaki/Pa2/mvslb7j/L/AHq4+3uZLnxA6tZx2cq/dhmb5F/76qw0kEypeTv/AKIu
                            9F2fwyr9x9lUl1rSn8P6hFeWc9zrssu+K+835UXZW8YmNSRSvrFnW4u55438qfymhRv/AEGorryI
                            Zbe5nVZreVd6xI/zr/vVLoN5pENrqf8AasE01w0G2zVG+7Lu+89c5HIqNuZd4rSMTjlUJftEsLeY
                            rMm7+Konka4bczfP/edqsW6RTb1ll8ldu5f9pqpO29q1OOQm1qXd96htyv8AN8rUN8tBAz+Giiig
                            ApdtJT2/vUACr83zcCu48GaD9vuE/wCerfIrv/D/AMBrl9Ktmml2r9z+Kvpr9nvwWtxq8Uv2FZoW
                            XylZ/wCHd/Gn+1WMpHfRp/aPa/2fvBKvb2nn2PkpF91HXf8AN/fr7Q0HRIrOwt2b9zcf7tcf8Jfh
                            1BpVmjXMqvKv3Ur11NN3xv5/34vnWiJtI5zVbCDzklX7/wDGlcF4qmXTZfm3TI1d3quqqjbWiX91
                            uSvH/EWrS2cV7LPF8ksv7r+OsZFxMfW9btoUladv3XlbP9ta+SfijbSzXF3cszTbm+V/7vz/ACV7
                            d4z1tZt6r8nzf3v733Hrw/xhcz389xbKy7G/8drGR2RPF3doZZWVd/3k/vvVfZ5KvOvzp/vU/wAQ
                            u2m6k8Ssv3t9Y1zuRZYmZvmoiEiu7/aZXZWZH+b5KqzXPkrtapba5ihuH27f++qpXL7JXZfvtVmB
                            X3bF+Zd9WLf5l+98/wB+qqNuVm/u1PDDu+ZV/wB2rkTEt2yN91m37alhTez7W2f+h1Xh+R33f3mq
                            7b/ddvl27tlc8jvpx90mtrP7TK+75EX+/Vq2tlSVN6t8yq9PttrsjMv3a6Pwl4el8Q6lFFB8+7bu
                            /wBr56wkdPxG78OvAcviTVIl2t5W7f8A+P19a+APhXZ6IsMrRKn935Kb8IvhjBoOmxTzqv3V/wC+
                            q9QSZUuNqr+6X7tXGJx1JGxo+mxIqbYvk2r/ALi1tXO2GJ2VapaU6vF/vUatNst32v8AP9yumJx/
                            aOa1uZn3r/B9/wD3q4S/sPtMrsq/7tdXf3+zfurnLmZdz7m+RmStNSjl7+z8mJ227K5S8m/e7W+R
                            P7lega3Mv2d1Zd77dleZaw621xLu+/8A+hVkWZuqvvt/l/h3V5N4hmlhut1ejarqv+ivu+/83/Aq
                            8p8Yalvun2/8CenEgpf2lsXd9/5dipWFf3Kv977/AN+qk1/vTdu2Iv3arvMu3czb0rTUylIqOjTX
                            CbdvzL/HUX2NfkVfvtu/i/hokvFS83KzfNTHvPLlTb8jr89GoGRfQqqoyfd+aqPktt3VsbFvJXZt
                            2zd8y1SudrK+35F3fcrWMjmq0/tFLb/eplP2/wAX3qTa1bHANooooAKKKKACiiigAooooAKKKKAC
                            iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKK
                            KKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooo
                            oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiig
                            AooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAC
                            iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKe33FplO/u0AX9Pm8m
                            8iZf7y/+hV9Y/BzVdlnb/M2z/wBBWvkVPkZGX+9X0l8FtV/0WJWb52/uNXHiY/aPVy+XvH03pUyz
                            S/N8/wDB8lbeiXLpdOu5vK3Vzmg2bTbP7ldbb20SROzfI/8AD/t15Z9DUO+8Mar9mt7hVZUf761u
                            2d/Pc/K3zp/t15PpWqyw3iqrffb7leoWczJpqS7WR9u9q6KcjglEsJebGdWX5GbfurK8QzQeU/lL
                            /rfnq0tylsyee3zyr9/+7Wbq1mrru3fI3z10EnmPjOGKaJ2Xb8v3q8a8W2ESb9v8Ve1+IbaC2+Zp
                            9+5v+AV5P4hhR2favyfw1kaxPJ9b03yV+/sdk37K4TVYVhhfft+7vZq9F8Q+b5uza33a838Q+b5U
                            u5vk/hSoJOavNtzK6/wbvm2Vzt//AK07dv3m+7V99UaFZY2+fd956xZJN1dNKMjiqSiP+Xbtp3nK
                            kart3f7VRfw/LTq3MQXb/wADok+7/t0za/8Adp+xv4moAH/2qb/uU5/vIzU376UAMb/ViopKe9G7
                            Z/vVZjIZTd1T/wAO2opKoiXulqHbuTd86VrWdt9puooGlVHlbY0z/cWse3ZfkroPD1supatZWzS+
                            T5sqpvb/AMcrnqHfQP01/ZF8H6fpdjNLpukf2VcPBb+aksu5ImeJN6J/ebYiMzP/ABO/9yvq22h8
                            5kngRZrRpd91/ciXZvf/AIFvRK+ev2Y9Haw8J67BfLHM7X37qG3d3fdsR33/APAnr6AsEtkuntrm
                            eS8tJf8AR5/JXYjNsT/W/wDAPlrOAVTq7PXp47zyIIo00+WzW9a7mX71xK7siRf3vuv/AOOVwmiX
                            M+qeINVudQiZNKtbpr1biFt8V1b+U+z/AIE8vzKifd2V0ttus7+Vby2kmtNLit5bOaGL5PNZ5d8S
                            Iv8ACkSJ/wB/Xrzd/EmmaPNaaquuNrEWrX1ummXCN+63NvR4rdP7qJvT/vuumoc0TzX4p+OtK+KG
                            l+DI/wC3rGw8P3sEXinVrTdtu5bCz3ypEn++0SblqpeaxbeJ9NstT8Na5fPFL9n8Ty3F3FvhvLpX
                            dPKd2/ubPmT7q7ErC+J3w38AWdlcWP8AYtjYa7pulL9qt9Gb7VLFYSo7yyyuv3d6bl3/AO/XH+P/
                            ABJ4V+HvhXTPAraDc2fw/wBSvPN06+t5Xllv7WdEdHR/4YopX+4/396Vzf4jv5fd909K+IWpeH/+
                            FYeRrlzqF5qUXiGwvYr77Dsiv7+WVHd0b+5FFtXb975N1fTc1tFDLZXMsE80sStu+ZESWJtnzy/+
                            P/8Aj9fGPiSz8Q+KvHXwM8JxaKs3g3Q5ZdQnhh3xebKvyy+a/wDFs+T/AIDX1dpVhqdh438S6m19
                            Beafq1tZ2Vmli3m/ZfKiuPnf/ZffW0ZHNIxLPXFvPiB4lnXT5IU8230qV3b/AFvlI8qS/wC9+92/
                            8Aq280t/rmsS6hFJDbszW/zy7UZVT7//AH26Vy+iXk6alZTy3Ns8Taxf3CojbPNVbdERN/8AsfP/
                            AN8V0tzf31zf6erQRvZNK1xK+777L86J/wCOVOpRt6DDeX/iPUNtzaaklgsVlLC/37NpU3u/+1vS
                            vnHRPiV44hl+PXxf0jw/JN4ql1Oz8LaKl9tS0sIk/dPKqN83yv8AM399q9p1LWG0e6S20xo9NvZV
                            lurrfF8ktwyb0evD/jH428Kw2+i2d5p+rTahfy3Fxa/ZJ3SKW6/5ZebF/F/A33GqpDjHnKPjCbU7
                            bXvBng7T9aneysLH7bfIn3Lq4Z3TZ/tfPvevNfGc2kW91caRot5c6bp8V417eJN9yVl2In3v4d7v
                            8n+wlXfFupXNnptvrlzLfWGutL/p18i70s1+z7ERE/hZ5d+3f/frzfVdSi0rVrTT52XWL2K183ej
                            b0llZHlRHf8AvJ8+7+7vrHmOozPFsN9qV5pmp2sH2/Srq8+zrEi+Ukt0qb3i3/7n3q4Xxr4q1fVf
                            D+m+HL6eC00qwvFb7Orb4rP5vn2f3v8Aab+6lXdb17V4fD+p6ReXiwpE0Wq6Yvn/APHqzP8APtRf
                            vM/3a80mvIoZpZ7lZHili81vOd/m3b2/76o+IyKfiTWlv4rezgVZplbb9rZdu5fu7FX+7/FurVs4
                            Z/8AhF2n0u2kfan2XUbuZ0SLdv3psT+Lav3q5fxJ5umyaVKtzbTP9lR1SH/ll8n3H/2qZ/xM7PQf
                            t3lTpplxdf67zfkZl++n+19+tzklLlkMe5gs7O7tmvmm/hVEX5Grn/tMrKkX31Vt61ekvJbltzRK
                            kUTfcT5NtMs9Sl026lkg2uzq0Xzf7VVE5qkuYpSN9olbanLfdRar7G3VYSaRGbb/ABfxbahT5W3b
                            d9bHNIZSqdv8VDLub5aTzKCApW+Zc0bvlpu6gBKKeu2mtQAtSR96YlXdLs3vLqJFX7zbaC6fxHVe
                            CdE+03UUu3ztzfKi/favvb9mPwTLbaknn2zQptX53++rf7H/AH3XzP8ACLwNLJLb3TRNtdd8SIv9
                            2v0Q+D/h6eG3t5bmDY/lLu2fwVznscvLE9d8N6PKjIrKvlbfmd6u63N/ZUSbW+Td81WNNubb7G94
                            krI6/Iqf3lrl/E+vRQ7op5Vd2+RaDmj70jlfEOsK947KzPb/AHFrxn4ha3vbyILlpkVt/wD8RXR+
                            KNYZPNlVtm3+D+7XlmuXMt/vnX9y6/e31hI74x5Tl7zzZriVrmVfmX5tjfdbfXmvjZ4ra43QN5yf
                            N/HsrurzWItu7a0zs3zf9915f4+ufOlla2i2bVaokX8R4v4nknm1R5WXf/tViv59y3mq2yL7n3v4
                            a1fEKXn3pdtYs0L28H31d1/hX+GrjEKgzVLX7HsbfvZqqb2f7vyJTfO87+L+Kmfw7dtdPKcHNzEs
                            btCrbdrq33quw3LQxVQd/wDaqVP9ai7vkqOXmNoy5TTRFT5qns9qf3vmqqm7av8AurWlYWzzbPvP
                            83yps+9XHI9KkXktt+yJVZ938FfTH7Ovw6Z5UublP93/AGa4T4XfCu51q8ilniZ0/h/2a+y/Afgl
                            dB0tNsXz1jGPMFSXKbVyi2FmkS/c2/NsrKtnaS4+9WhqT/f3fPVKz2/aE2/xfJWxz6nQWEzQt8u7
                            ZVHXtbVLd2/2flrWhRYbVGavLPHmt+TL5SNsT7n3a1MPikRalrbuz7Za5zUtbVP4m+9vrHm1jfC/
                            /fFYmq6lvV/m3vuoEbd54h87+L5N1cZrd5vZ5Wb+LfTftjea/wA2ysfWNS2ROqr89aAYOpakzs7b
                            m+98qbq8/wDEO6ZpW+47NXR38zbXZWb71clrdz50rbvuLTD7Jymqs0MW1d2z+Gq73LfZ0g3Mj/7t
                            N1R9yp/A/wBzZVF5tkVWc/uwG3E371tzfL/u1E1z8u1k+f8AvVC8zNTfM9q15ThlWl9ksJfFEdV+
                            RmquztN1qOl+anymcpSkDNSbmptFUQFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABTvMptFAD/wD0GvbfgnqXl3ESf3vkX/a+evEv
                            4vlr034RXmzUol/uyrWNf4Tvwn8Q+9fCu17VGZfk3fL/APF1u6lZtcqm1/8AgFYXgZGudLt9u7++
                            tdnbWcqL/fdf468U+kkc5baJPbXST7vu16LZ699u03yvuOvyNWU+ms9ru/u/JUvgzQWudUfczIi1
                            0ROaUuYsW2m3Vyzszb9q71T/AGar39z9m2KzNsX+DbXdvZwWFrLtX97t2b64LUkbUrqVVX5F/wDH
                            q1MYnnPidPt906s29IvkVv726uH8QvHbfd/h+9Xret6PFbW8qs2z/f8Av14/45dbOJ1VdiLuT/eX
                            +/Um54/4w1LyW+Xd8q1454muZLlWZWZEr07xb87Pt++teXa3bSvvX7iL89REzkcdNub+KmLu/iq1
                            c2zI38L0xLfY3zK1elGUeU8qUZcw2nIn8P8Aeo3bP9im/MjPUjHbNnzUI/3ttH3qb8tBQbNtH3qP
                            MokoAY6f3qNjPtWjb8tH8P3asjlH1C3+zU1Qv8m+lEioKmdyr3+7tr0P4a6xpml+MtKn1q1W501p
                            1in3Psddz/63c33WT+9XnKP5bV1ngnTZ9a8UaPp9pAt5cXF1EiQsu5W+f7n+1RIuhI/Vn9ni5vrb
                            wfd/2my/Z1vLh/OZdu7c7vvl/wBr5/l/2dle96UlzeWsNit9vvbxftVrdvB935E379vyr9968X/Z
                            s1i58W+HNQl+020yS332dvJ+TYv2eLZv/wByLZX0Bpsl9ptvb/ZlWZGuvs91N/AqNvd3/wC+K5on
                            TUJbzVYPDf2rTb6eOw0yW1l2ypL+68pU2PLvb5lb564TSoYtH8C2ltPc2MKabAy2tu+yXyImR9j+
                            b/ddPm+SuuvL/wDs1otMbQ/t+hM0XkO679qbJZX37v4d8SLs/wBuuUuXttN8H+bqcEv9qteXF78/
                            7152XfK9uif3dny7K3MYnh/iGGfxzo3itb5bTw9pXiC1lt9Oe3Xe/wBlRESJ5XX+J3+bZv8Au15F
                            4DvP7S+C9lY31jc6lLFPf2USXc+20R1ldIopXXd9xUVU2f8AfNe1eFbC+ZbiKe5kv7eXWLq6vIdQ
                            XZLta3d/s8X/ADyV0fb8/wB2uP0S/XwTrlvZ3M/2DRNW1PVHa7miRPKuotm+4df4V2bKwkdZ3HgO
                            5tNV+I3gKK0uWsL3RtCZdRhu9++XUZ0TzUiT+7Fs2s/+3Xu1zc6fbfZ/+Pl7iyiZFt0X979nbYnm
                            7P4lT+B/vfP/ALdeE/CjWJ5vEKeKLnQ/7E0TWZbfSNHuHl33F1cRb99xKn92V0T5v4tiV7N4huJb
                            y/SCDxLDYf8APe4dfuquyJ//AB//ANkq/snPL4zzfwfbfY2tYJ4N72v2+4/56/umdER0f/gfzf79
                            egWyNbabFPcrBvl+SKGGLft/3P8AgG+vLPAtzBDrNpL5/wBv+0S36Wru33olliTZ/wAD+dv+AV6b
                            bX63OpWkX2mTTbe1l+X5fvS79nyVETaRj+M7y50eK3vFubuH9/snhRftFxdbYtmxP7tfNXxpuWTx
                            98J5V2/bVvryKDT/AJ/3XlRfO7v/ABMm/wD8cr6g1y8Wz0ZGbUJNkV0vlXafvXn+f50/2d6V8ofF
                            zxJP4q+M2mwXmqwJo/hKJbKx0+xlbzZbq63yy3GxfvLt+X+7RIuI74rtp+pXCaZrltO+hL9niuks
                            Wfers/8Ax8Sv91tjP9x/7leNfELR7HTdS8V3Ola9p8P9kz29rp3kr+91aJkfzXT/AHHT5nrv/G3i
                            fXvFV/o9s1tp+gvFfSpLv3o8Sy7/ACpbj/vjbsevFfEj6VcxafLq+oLf3em3ktl/Z9pEieb87yu+
                            9f4XZ/v/AN2kXE5d9SsYfD+pwNYrNq0rRP8A2hMz74lXe7oiN/fritUv1vLW4WefaiovkfJ95V/+
                            y+Wul8T3kFiu1VW5u/K82dIf9VEq/Oib/wCJvn2tXGeKL9ZotPtmto0eziWJnh+43/Aqqmc1WXKY
                            eqK8N426DyXb5tm7d95alub29/s1LGS5Z7SBvNW33fIjN975aznmWZXZtzyt/wCO0XHmuiSs6u7f
                            9911nlcxA8zeX5Z/hpjfw7aNvzUNtH3fmqzEdvZ9qs3y01WI4WmU6gA/i+WkakooAd5lNoooAd/F
                            S/e+9R/3zViGFrlvkXe38VADEhZvvV6X4A8Hz3lx8vybm+//AHVrM8JeGGkvLfz03ozf6lq+ovhp
                            8Ot91FA1ssMrRLL8n8K/3P8AxyuaUj1aVPkPQ/gz8LmubNItzO//ACydF+fb/HX1x4PT7BE+nrFJ
                            5SxK8rTffrzf4e2dt4Y02K5tp/u7k2f7Vbum+MNT0238+f5/3uxnep1OmUeY7jW/GcWlNEqwKlp8
                            yb/+B15bqusfbL152+f5m/20o8ba9Lqul3DLLGkUrf8AA65mz8p7FPN+eKL5G/4DWcpBGJieIYZX
                            utqz790vzInz7a5DxI7WKyrco2zbsruJtesZLy7nig3/AMHz/fVl/uVx/wAQtVaa3faq7/8A0HdS
                            N9TyfxPra6XpLxWMTPKzb/n/ANqvP7m/+2Wsrz/froNeeeGdIt3nRSrs37d/+5XI+JE+xy2620Wz
                            5fm2VIonn/jLdcr8qslcRI/y/M3zV3/iZ1s7fdK+92X+9Xn94++4dv8Aarpgc1aRAi+Yfl+Val+b
                            5KhVqf8A7taHHEmjXfsp+3958qslS21t50vyr/u/LXb+Evh7qHiC8h22zJEzL87q/wB2sJS5Tvp0
                            5TMrw9olzqs6RW0XnP8A7C17r8NPghJf3UVzcxfeb5vl/havSPhF8B1023iaddj/AMXyfI3+3X0d
                            onhKDTVSKCL7u3564/ikd/uwMTwH4Ai0S3iXyvmVf++a9AuXSztdv935atzJBpVmnzbK881XxUt5
                            f+QrLs/3q2+A5pe8V9Yudkr/AHk+asyz1tYbj5m/3fmo1W5/0d3/AOAb64251VYWT5meqHqekXni
                            dYbP72/cv96vF/Gmttc3krfN83zqlaupa9+6RVZv4q8/1vUt9w7f3KDIZc6l/wCPVn3OpfM7Lu/u
                            VnzXiv8AN/H/ALFRXNwrxbV/iSn7pBXudV+zM/zb/wCNv9pax7nUvtPzL/dbbTLx97bVZf8AarFu
                            b/7M25f/ABxq0AZrd4tnH9752rzrVdYVGdfvtWl4g8Qr91m3p/c3Vw9zM00rN/erWMeY5KlTkLl9
                            fecu1vv/AN6sxm+ahmb+KmVpGPKcEpcw7zKbRRVEBRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAV3Xwxufs+t
                            w/71cRt+auj8EzeTrdv82z51rKrG8TpofGfo58H7ln0mJWXf8v30r2PTbNXX5vk3ferxT4FOr6DE
                            zV9AWCL5W5f4F2V5kT6SWxFc2cX2d4tq/N8nz1oeGLOK23tt+6tV7pFdkZa6CwtWSz8pF/estWc0
                            jEvLxrlnVomRF+TfWPfwxWdmzW0W+XbsrsJnk2vFPbbE+5Wbf2ESRfuvuN81UEZHkniSz2ab5s7f
                            vdrJ/t14P4tSe53xN8+7dX0hr2grbebLO2/d/BXj/jx9PS4fbEqfLs/75rKR0xPnfXrZbZbhp/8A
                            x+vPNS2zb923Z/t16H4zvPtMr7tu/bXmWpJv+98n975qAkY9zNbfP8q71/2axLyZWbbt3r/erQmh
                            +ba33Kz7q2WFtq/xVvT5TjqFV5F+9tVKi/if/ZqV9rb9v/AaHTb/ALH+xXScPvDKd/D/AMCo8ym/
                            w/8AAqCg2bGoo+b5Plo+7QREH2075X+9UVFVyjHt93/epqpu+9Sfep6fe/uUwKn8VenfAeb7N8XP
                            DU//ACxt7rzZdr7Nq7Pn+avNn+Rq7b4a2F3qXjSyWztlvPK3Sz27ts3RL99Nzf7NVL4DCn8Z+uv7
                            OVtE/h/VWtr5oZZb5ntru3g2pEqv5SJ/upFEi7/4q9ts7DfYSrbah5N7K7xb0bftlb50liT7rfJX
                            j/7PFhbeHvhzoUTztf291A0rTbd+5Wfem/8Avb/n217GkPnWenzu3k3FmreRvXe8SfcR9n97+GuO
                            J31CvbW1nfy6hp7andzXFussUtpcN888vlI6Pv8Aurv2PXg95odtqurWWtTtfak+ktvs7dJdkVrf
                            zvsu3t/+e67H273+Va9gTR9D8T6l4oa+utQmls1tdKb97st1aJ/tX7r+987orf7m2sTxP4h1f/hI
                            7G+lgtr/AExdHlivtQ3bPNl/gSJP4V3/ADM/+xtq5ERPEnudV8O/EvxHLbfa/FWp6pdXEWrXbxeV
                            ZWDRW/8Ao9vE/wD3xu2fxb65zx/8MdT8Sal4agbXG029vPtV7q1pt82XzWdJXff/AA702K1ezTW2
                            n6b4c0+LV9VjsH02D/hJLp7iXyklii/eo6f3vkT/AMcrJfxx4a+G/wDaetXKwX+lWGnX+qvLdz77
                            hpZZdiW6f7mxV/2VT+Ko5Tp5jMbwfpXh/wCMmn2d8tzrEvhzw3a6r9nil2W+nbnl2Ju3/ef723/Y
                            /wByvTrZLPXpZm/syC/8P3U8t7Zv5r/dWJIv3r/3XffKqf7FeeeHtV0+z8H3bXniGO88QaleWt7q
                            N3M2zzbptjv/ALsSfIqp/dRFro9b8Waak/h3wT9u02a38Va1cWD3CK//AB4LZPLd7duz5tq+Vv8A
                            4a0MZB8Ov7K8Q+EvA99YwR6rcN9sigu4V2JFK3mxfJ/6D/wOuzm0f7BcXEtzeSQoyrK0My+aisu/
                            f8n8P8Fc/wDHZ9c0f4SxQfCmCCG38ORK9rp9vBs82Jf9Ulu/975N1bvifWLy8tYvPtp0t5bW3/tG
                            7mbYkTKm93T+9/qv/H6CPiOXvLyDSrPVdVs52m0pYtlrDuS1SWVU+/FF/E3+xXzjeabY+NNQ+Gvj
                            HwhJaX+pa9LfvLY7USWzt1/dJLdP/wAA+5/3xXqPxL8W215cW+uWdzbQ3ct1cWsE12rpbxRMm5Lh
                            Iv4tkX8dfP8A4S8PQeDLqLwdoOrweJImi8q617Rl2RT3E6b0iR/7yb03fP8Ax1kdMfhOZ8Xa39s+
                            J2sXOvS/2w9xpl1eraQzpFErRImze/8AEuxNy/xfPXiut6WsPhe0tlu/7NvfPbdYy/62JmiSVJXd
                            P4X3oqr/AA/8DrT8VX9j4PuknvNPn1i9gnurXVYbhtiRXG/90iP/AHUVK4rxXrevadp1jY6nZtYX
                            USNdWdxcJ+9lt59mze7/AH12fd/urUxjzFy9yJL4zm0W5kso9IivEtIrWL7cl829/N2b3dF/uv8A
                            w/NXmN1NLcea25nXd81dDqV8/wDYlvBJct9oZPNZdv3lb7q1iWzrDZ3G7d5svyqm2uyMTz6lTmM9
                            bZtqs3yI33WanXPzsrsyvu/ufw0XFz50US7vurt21XX5d/y1oecN3f3aSSil2szbaogZRRRQAUU5
                            H20b6AF2UbKlWNpvlre0rw3LebvMVoVX5f8AeqJS5TaNOUzJsbCW/lRFX/gVd14Z8GSvLNKkrfuv
                            l+f5fmrb8P8AgxXd4ngaH5djb/vr/vV7B4P8EwahYozK3m/Lt2fxKr/f2VjKR6VOjGJi+BvAcupe
                            U3kM6RfO3y7/AOP/AOwr618H6PdaJFaN9hWF7yJ/nm/hXZ8nz/8AfdZPw08B3MOlyxW1nvu7iVol
                            dF+RV/269o0TQ9M16ztGuZ2mt7WBomdPubv7lYHQZt5ZwWFlZXNsyvbxfupdv8Tf36z7aS51K3u1
                            Vt8TL/H/AA1oalNFtRbOD7NpkT/fdP4qxLNG0qWKD/XfaN3z/crQCommrZrtnl+2SqzIybazbmG5
                            trx4lVXil+T+5/v7K6X+zd6pK397Z8lH2y2SV7a5T97FuRX/AL1Mk4/VdKWa322y7H/j/wBqvPPE
                            NgrtLtZpnVfK/wC+a9Q165WzX5W+T7i/wJ/vtXBa3cxaPobz3LKjyrvi3/f/AM/I9ZGx4vqtm8Nn
                            L/fVv73z1514h1tbm3f7qOqtt+b567LxDf7Irq8Vt779n3/vLXkXiTVfs1u+5V3szfJQHwHO+INU
                            +1RJBt2bW2/ernHi/i/h/hp9xcy3kvzfOasWFjLc/Kq763+GJxylzyKybt3yVs6T4bvNYkVYImm/
                            u7K9F+HfwZvvElxE8sDJE38O371fWvw0/Z7ttKsImngjT+8m379c1Sp/KdkaPL8R4F8KP2e59Yur
                            eW5i+7/fWvrLwf8ACvT/AA9bxbolR1/2f7tdtoPhuz0pfItolSrFzt819vyVjGP8xfNyfCM0fTd/
                            7pfkT/drqHsFs4vNb+7XP6VN/pSbv9xq1fFviSLTdLf5lRNu+ugiR5f8UfH62FvLAsvz/d+992vK
                            NK8UNNeOzN87fe+b/wBArnPiX4nbUtUuNsu9NzbUrnNKvJY5f9j5W/3anlA9gvNe8612/wAC/wAd
                            cZf6qyNu270/v7qsW15vhRW+f7v/AAKs+4h+0712/d3Ou+jlHqUrzVW2pu+fbXNarefNu/4Hs3VL
                            rczWbPu+5/6FXH6rrCp8z7X/AIdlUc5oPf8A91f9uornUtkW3dsT5vvt89czNrf93an++1ZtzrH3
                            tzKlacsSeY2LzWFTft+RG/8AQq5HW9V2L/C7/N/FTZtVa4l+98n+xWDrFz/Fv/21p6kSlExb66a4
                            mYtVLfQ3zNupETdXWeVKXMDvuptFFBAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRTkTdTaACiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAlf79a3ht9mr
                            W+3++tY1aeg/8hGKip8JtT+I/Q34CTM2gp/33X0hZ3Kw6Wn/AI9/tV8xfAS5b+yUX+BV+/ur6L0S
                            bf5u77irXj/aPpPiidFpqLeXCIy/xb6617xbD7q/vduxq5rSk86X5dvy/erRf9z8zN89bRMZF+G5
                            udSidW/c7m2LWVrcfk2qLuV5V+Src0Mr/Isv+9VS5W2totzfP/Av+1VERieW+KtVZ7fymVt6/wAb
                            14J8QptiP/f/AIq998eSfZpX/dbPl2L8tfNvxOvPtlw7QLs+X7/3P9h65Kh2RPGdeRpll+8+5f8A
                            vmuSvEbbuZf975a7K5Teu5m/vfJWfqSRXVui7V3qtAHntynzOu3ft/8AQaynX7Q237m3+/XX38P2
                            ZZWVV2OvzfJXK3LK9xu+5/sVohf3TMSGNZ0/vVFc/wCtf/2Srd4+xl2r/FVR5N0bbq64nnS5SH5n
                            o+VNtKieZtX+GhE/h/irQxGfwp/v0feo/wCWiUf5+7VkRB/uUypflX5VqPcv8X8NKIx0dGz/AGt9
                            M/vUbvmpgEyM3zL8iV7t+x/4NuvFvxo0edYJZrLTW+1XW1fk2/wI/wDsu1eO2Glz6rdLbW0TTTS7
                            tiJ/31/6Dur9L/2BvhXBoPwnu9XtpfOvb+6WVpk+421Pub/7tKpL3eUzpx97mPqDw9YS6bptkvlL
                            NbxRebFcfJ/obL9zYn++9dbc6qtndRS2bRzPcWssSptRnaX5Pn+b7v8A9nWVpW5/Ks9rfZ5WaLf9
                            /d8if+z1k+KtSi0rUre+s7ZYbj5t000H3V+5s+X/AG65onTL3yr458eam9q9tbX2n2Dfarfyn8rz
                            ZdvyfaPn+78if+gV4D4/+KkWm6smn6ZdahqUTLeXs+p3zJFbxK37rYkX+3vf560PHnxLs7dpVudV
                            XR7RoGsp5kX54m3ps8pG/hfe+5/4a+OPjd4m1p/GMy6Luh0nalvBKnzptVNu+Vm+VW3tu20S974T
                            aMeQ9A8SftMPpfhXT2ZJPNa1tYra7hgiupZYoHTekssv3t8qKu/73368E1L4rX3xC1rU3vrpkt7+
                            dr2eW7be6t8m9/k/i3/dTbt+euSvLe0TT00ibXoJmSXcv2dN6Rf8D/u/M/y/3mrn9QuYLb93bS7P
                            KVUaVI9ryNt+f5q2jTMalbl+E9o8M/FrXtF0lIv7QUXcUsV1BfMqyy7VTb5SJ91d3yN8/wDFXsHw
                            t8X2lz4f8ceKm1ySa98IRWssH2u4ZnleeXbLFFv+bc6LKrbU/g+781fFsOqXM32eN5VhWOVpWl/j
                            Zvvbn/vV1XhuK78aeLhJZ3K6TDdM97dND8iWqqru/wD7Nt/3qPZkRxEZH6r/AA0+Lt5r2uS61Y6h
                            p+paFLArxaZdy7JVZvl3p/ufd+5XfeKtKn1LUk0pvsm+6i2XX3Jdtu0qO/lf76P9+vzq+APxi0Gx
                            +KWiWkVzFZ2/kS28Wp30WxGuG+4n+zvb+/X3P/wlGleFfhzrGn2cX9saroeiy6quz/j4vNqP8iP/
                            AHUfZWPwHZ7vxROK8ceG5bzSbvauoalrETXEVrd3y/6PuaJ98USL/CifL/33XzF8LkuYfAOu32lW
                            0f8ApWsRWkE02/yrBlTZvR/7zvv/APHK+x/HWoeIdKv/AIX+HNI1K0h1jxHfRaLqdvbwI8uk2sqf
                            O+z+Ftm9d9eTw6P4fs/2hNQg8EW1jomgWGorZW1vqG77DFcWqeR9qZf+eu9ZaOUuNT7J8heJNbvL
                            BvIaC0vL2Jri3urS7XYnms+x5XR/vN/Fv/2647xleQah4ftXvrm71TWollh+0S3DvbxRKyKiRf7q
                            /wAP92u88T2LzePtT8R61Laa9cNr8sUtjE2z7ZuR383Z/c2um1/9iuH1Xy0lRblraHR9zf6CjfPt
                            XY77Nv3Vf7u+iMhVDi9QvG16zRlsY4ZrCCKLfbpt3Kvy72/2qwJnlvJfmZn+b5UWvUfFtssNxLba
                            fZNptpqkUUsFp8r7Yt3yNvX/AL6b/frn/D19F4b1N5/sizXEUUv2T7Rs2LKy/fb/AID93/arpjI8
                            6pT5jh7iF4ZXRl2OrfMn92pbewaafym2o3+21eh6J4Jl8SappVrfT/YGvJ4opbt/4YndPnb/AHN3
                            /jldh4g+CcFn8WL3wLot9BrEUV1Lt1jdthZVTdv3f/ZUSqERw38x4Ytuyq7+YqOu3atRPDL95lb5
                            v4nr2DVfh3P/AGdb3y6a1hpis1vHcSxN/pUqu6fI2z7vy/M1Wr/4Y/2Pa6VHqSr/AKUv2iJ0b5GV
                            v79R7Qv6oeO/2TP57QsrJLt3bKfrGg3Wi6g9nOq+av8Adr1q50GxTVIrl9roq/ukdv8AY+5RZ+Ab
                            y/iu9cubPfY27qk7P8m3d9xKj2xf1SJ5Z/wjN9/ZqXjRfumbYtaOl+D7q/tXufLbyYv9b8vzIv8A
                            fr0y/wDDEUOpRWzSx/Z7pVuF+b5FVv4/9lk/uVpw6Cyalq0Fj/pNva2sXn3ELfumXf8Ax/8AfD1P
                            tS40IxOK8JeAX1XWbeJY/klf/XP82xdm/e1dFpWlMl5cLBEszrOvlPt+9tf7/wD32ldBbawv2yJr
                            P/QIpYorTZD87ttT5/8Avuu48MeHrGzutMilWTzZYLh5f7it8mz5/wDbff8AJS+M6eXkKvh7wTqF
                            zcWniOdVuZb+Xypbf7jqyp990/hr6N8PeA4k+0XMEXz+Q0Wz7m5l/wBisLwH4e1CHSUW+0+P7RLE
                            377/AJ5J/t/7WxK94+FHh6z8Q3lk2pytDceV5rW/3Nu7+PZ/wCtNSJSOU8GaVeW0SfvZIZViXz0V
                            vut/sV6BommwaPFFK0TJo8t0zzqn95q6Cz0TTLZdTtmbe15db1f+D5a0L+zW20lIImV7SVmdv79G
                            pHMcfeW0GpNd7f31lu+WGuH025e/8TPE0Gzyovuf5/4BXe6bYRalJdtBOv2iKLZ8n+59+sV4fsEr
                            tc7ftDfOrf8A2dZFxKj3MENxaeRErpK29q5zxPDBbXDyrt81f/HqxfiF8TrHRF+zW0sf2hF37E+/
                            XhPif4u31/dS2y3Lb1b76f79PmNuU9A8T+KoLa3uNzLv+5/fryXxn4qie32tcs8K7vKT+78nzpXI
                            6lreparLNFuZ0lb5v9qornw3far5UDbtn3Nj/wAS1HMHKcZqvjBXaVV+fb/crirzTdR8QXC7IG2L
                            92voDQfgnE+yRoGmTd9967vR/hpbafKi+Quz/dqPam3KfMXh74R6jq0q7omTdt2rX0P8N/2cooWi
                            a5g+9/8At16t4e8N2dr5W22VPurXoWmp9mZFX+Gp5ucj4BvhvwHY6DaosECo/wDwH79dklstva7m
                            +/t37PuJWL9s2J8rfPTLnWGeL5m/h+ateXlIlLmJZtS2fNu2bqx7zVmeXarVFc3Oxd26uXvNV2XH
                            3tny/wC5Ryj1OtttV+xxea23yv79eb/EvxnPcq8EErbNtWL/AFtnt3VW/jrjdaRr+43M2zd8lUGp
                            wNzYNc3G6Xc/zbq07bSlRflXY38NXfsy2y7mXZVW51VUb5du/wD9BrTUzkS3MzeU6qzVS+3vD95/
                            vVRufEkUMT7mb5a4/VfFqpv2suzb/ep6kcxo+KNYidnVW2f7/wDFXm2q3nzSsv8AwGotV1trltzM
                            yVhXN+zxPv8A/H1pcpEh19qW9fvbH21j3Opb9+z7+3+OquqXnywqvytt+aqT/Jv2/wAP+1WhjKX2
                            gbUmRqhubx7nZ81VW+ZqGrXlRwSlKQkdI33jSUVZiFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFF
                            FABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUU
                            AaKrH9lV97faPM/4Ds/vf99VRf8Ah/3abupKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAdVzTWZbyLb/E1U6t6au+8i/3qcvhLh8Z96/AR2m0OJmb
                            5FVU2V9N6CkSWsW/7iqz18pfs8XO/SYl3fJt+5X1Loj77eJW/wB9a8n7R9PT+E73Tfks3l27E+41
                            RL/xMrp4Fbe/3/8AgNWtKhZ4k3f6r+5/eq3qSQWyp9mXZL99nqjHm94LqwisIkZrnf8A3qxdS1L/
                            AJazuu/7i/7tVLnUpXlT5meua8T3PnNuZmR9m9Up8wRiY/jbxDbXMUrN++dP++6+cfGetrczv8ux
                            P/Qf8vXffEXVf7Nt/mZklb5N/wDu18/+Idblmlf5/wCL7v8Adrml70jpj7pj3+6bftX5Vb79c/cz
                            RbnVm3ovyN/vVoXOq/uvlbZ/wKuZub9vtG7a2z+J0oI5jP1X99K/7/Yn+xWLNt83aq/dbf8AJ/dr
                            dR4Jrr/SV2Iy79+2s94dlw8qxNNb/wALp/EtWHMc/efvpX2r/wB8VTm/h+bb/s7a0bl1huHVfuf+
                            g1AkKvG7N95dv3a6YyMakYlFE2LT4UV1fd/wGonT5v8AZob5f71bnHyiP/HTF/1ZpaRf9WaCBWX5
                            v79ElElMf5VSgiQ9Pm+VaHTdUO9kqaH5/vVZHNE77wet54n1bR/C+lW6wtqN1FZSNCm6afe2z5m+
                            9s2t91Plr9orDwXp/wALvh3oXh7TIPsdlYRRW7On32+T5P8Ax+vz5/4Jm/DH/hMPire+I7qLfaaH
                            FF5T7fkWV9//AKBX6UfEV3vLrT1i+e7VvlTdv+Vvk37P9ysKh00v5TndKmihaX7TeLD+9ba7t93/
                            AOJ/vfJ/frj/AB/4tXR7XVrm88vSkig8pH8/7a8rN9yXYv8AqlrsLP7HNeJA2oSea371bR4kTzdv
                            /wARv21zl/c2Ogy6hLZxNDDKu/5bX91K39xPk3f+y1mbe7zHyF4z1W+26g0+n6pquqtYyvZ+dpzx
                            farht7y/O38KJ/Gny/7bslfPXjb4X+MfE32fVdZbT9H0+81NrKC0hb91FLs3uu1f7io252/uV9ef
                            HXR/EaeJr3xHc6rbalFFBb2sT6hfbEsLff8AaHTYuxW3xI//ALP9xK8w8faRYN4HWe1Vf7Y1fUYv
                            sf27/lwsmi+e4X5EVZZXbbu/2tv36cS6nvHyVceGb6wt4raxnkvJpdzT+Sv7pdrPsdX/AIt+zcrV
                            XvPDl82maPA0SjzYmli3tt83c7fP/tfKlei+KfCF94d8Yaxor6lY6m2kxSvFNaSq9o21N2xP727a
                            67P4fm21yXieS9vJmlWSOG1uIl8i3RETZbo7KibF+633W+9/HXTzHBKkcf4iWMapcbLhZtqL9z+J
                            tiK//s1b2jxyXOmX1rY2TJLL5SrMsvzM6b9/3v8AZdNy/wCzUWm+ChqVqz+esN8nyxW7xNul+VPu
                            7f4tzfL/AHq9X+HX7POueJLq702xbzllgieB3bynWV9jJtT73zpvX/gLrRKRzRpS5jqv2Q/Ctjrn
                            7Q3w/g/sbR/EaLp8968V3/qVl2Sr5twv8XlNtb/gFfpHeab4quNL0zxHbeB9JsPGsumNZW0VjK0t
                            jFF5qbIvm2bt6Vyn7Iv7PEHwQ8Jpq91Y2154q1Sdorm7uFS38q1i+T5P9/czV7BpWq3N54qa+0W2
                            a5+37v7Hlu5XW0aJf+Ph0i/hZ/4aj4zs92JwXxSuNT+HfhzxH4h8PXNlD4j0HTpbuV7jTtztL5X/
                            AB6pL/u/xfw187+D/gnBqt5pnwpvvGezT9SgaXWNesYkl+1XkSfaJYklf73zv81fS/xI1u68C+Cd
                            S8L3l9/wk/j/AMdSy2ttY+Uuyzin+RnZP4Yokf8A4Fsrx3WL+z+CfhnZ4eZprjSbGXStMu9Qi3PF
                            LK7pLLEnybtmx/nqJe6XT94+RLmHwF/Z3/CR6fpGpX96usS2t1CnyJLZrFtifZ/fd/m/3XrF8MeH
                            tIufEulW08ccL6v/AKE2rX2x7ewtWdH81E/vbEdfn/v16h4J8NweDPDkXi9P9P0q81Fv9LuIv9H+
                            VHTykT+871P4v+D9t8O7610Oxu18W+M7/R31rWE8ryrfS7WVEbZs+6rbPlrGP8x2SPE9e8LvbN4i
                            8Q6feRalolnqy6VawsW+3SqyfJKqbPmV/u/L/FXoXxs+Cf8Awr2z+HWg6ZBPf+OtR0xdX8TaPcRf
                            urNm2eVE/wAvybP/AB7ZXpfwx1jSNN+I2n+L/EunxvoUUW9vJtfkiWJPkl+599K6218E6r4s8RXf
                            xL8ceJZpkaBntYbiDZdy26/PFuRf4tn8FbmBwnjn9njTPB/hXVdPsYGv/EdnPFLda9by/wCiWG5E
                            +0On+58+3/vmtvW/hp4a03XvGcVtZyPb3mhWr6db6e3lbmVPnuH3f3/4tldV8eLqx8H6D4AW2uZI
                            7TxLpX9q6jbv/rZfkT91/wCPrVX4iveWHjC98S64scN3Fp0VkyJLvRomt02Iif7lYy5TeMTlPhjb
                            wX/gFPD2q6LHf6rrNn9n8O3GofIlrFvleV0/u/JXD+P/AIY3ngDwDo/ijV9r2WqSt9lhmZElbb/7
                            L9+vRdHhn8VWD23hCLf9j0dm1bULuXYlhb73/wCPf/argPG3iGf46+INEttVlaHTND8jT7OGZnSJ
                            Yt+95f8Aab5KXL7ofaOU8G/DSz8VeDdY8cX0TWGiWES+fD9yV9zvEmxPvfwf98vXQfHLxJFZ+PHZ
                            ry0v/N0xkaHT4vKtJYtnyPs+7uT+/R4y8Q/Y9NfwrbLHD4fs9Tt0tdWRfkv1+0fOifw/Im9a8/8A
                            jq+nzfG67trOJodCiWKVok+4sSp87/8AfFR9kepoeOPEmofDX4fXGh33hy0dfE1jb3tnqFw2+4s/
                            kT5Itqfdf71eb+G01W50aW2s1n+0X8TP8jbEa3X+N/8Ax/8A77pvxa8YW3jPxVNHp8s82nxKiWf2
                            hm/dRKi7EVf7tOs7Z9BsPDWoS6hvhuItnkpvV4Fb76P/ALL0S94Rp6JZy2GpWU9mrTJ9+KZ/nTcr
                            7P8AxyvoDStBsbnxhaaZYrI9ktqt1dTI/wB1m2fJ/vffrzTwrpu/QYpbmVfsnntbwQov+qVvn37/
                            AOLe/wD6GlfQfw08PS7Xs4Ime4v5YvK8n5/N8r7/AM/3q2iZnsXgzRLbVZdVvtPX7Zo6stlFvX51
                            bY/z133gzwrPYXT3l9+5uGi/1P8AAq/wVd8N6I2iLb6UsCw2/n+a3+18m+u1uXgeK4kb59vyRf7P
                            +xWmpzykc7f6rFZ+HLKJYo5riK62M7r/AA76x/E6ROtpPF+5SJVdId3yVLfwtbXWqzsuxJV+X5q4
                            LxP48aGKWBov9IlVv/ZKzkEYmZ4h8SRaJ/p0U6wuv3krxL4r/GC+vGRdPl+Rl+Zk379v8Hz/AN77
                            9aXjnUpb/wAH+bv2S/bGiZ0+f7uz77/dry2/0ptS1lLO2X7y/f8A4PuJ89ZnZGJyOtzX2t6p8zST
                            StEyM7s/zbk2VreGPBM9yu1omR1b77/fbdXqXhX4Y21hEk9zt31Nqt5babL5Fmu/d/Gn+zUmhg2H
                            gCztonZo1fZ/33urWTwrAn+ott+3a/z/AD1paDYT6k25m+T7/wDvV6BYeHldU3L8rLRyilI5fQ/D
                            beV83mfN/wCg1sXOg21tb/MqvXR/Zo9Nt3+75v3K5LxDrap8q/J/eo5Q9pIqJeLC21dqbfkrTs9V
                            V1fd/F/3x/33Xnj6wz3T7m3ru310Fteb4tybtm2r5SPiOrfUm+Rvl37fmrJvNe8ld275P4krPTUm
                            h+Zm8nav/AGrivFXi1LaB9rKj7mT71Azb1XxUz/KsrbVb/vmsd9bab+L59396uB/4Sdrn5WZU/j+
                            9T7bW9jbVb/bq4mfMdg9+r/db7y79lMeZd25ttc0niHfcJtb/wCyql4h8YR2FrLtb51/2q01DmiH
                            jbxBFYW7ssvz7flry+28Vb2b962/c3z1j+J/Fr6qz7m3p9z79cpc6lLD91pNm35aNSJSOr1XxOzs
                            +2X+L+9XL3OpM8vzN/wOufe8lvLjyl/hbfWgkKuu5vk2/wAdLlMeYsJctcq6tu31U8lnlfczP/sV
                            ds7ZXt03LvfdU00Kw/e+/wD3kpknOXlsz72b+Fti/LVS/T5dy/cZv7tbdzbLMu1vkTfvrK1Lavyb
                            vl+996rM5GPMlQbqkkfdUVdBwSCiiiggKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKAHUeXT0j3VN5NRzG0acpFSiiirMQooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAq3YP5N1Ezf3qqtUkbbWVqC4n23+zTeLc2sS7vmWvqrTbnZJFF/Gu2vi/9le8R7jazfdX
                            f97/AG6+0PB+25vEZv4mry6nxH0NP4D1awTyVibf8+2qOsaqsOxfKZ600eKFm3fc21UubZfK83yt
                            7t91HpjMd0lubfzVVYUb59j1zXiK/wD7H0uWdold9vy/367CGzlfZul85/7m35ErjPi7cwaP4eeJ
                            tvm/c2U5CifIvxR8VT6xqm5vkT+5ury+/uV+dmlV3atjxneT3mqS7XZ/n/g/365y20qV5XW5aRH3
                            fc/gauaMTaUjPuUivJfKaXyf46zHtmtm2q3nI/3q1r6zX7Q/y70+XbWZculmvywMj/733quRlqZ9
                            5NEkTxN/uKn8dZlzfxwqiruhRV2fJVu8tlv7eWfyt7/faucmdfut8lWA+bbt/hf/AG9tUpLb5vlb
                            5dtW/vrt3bEX+D+9VF3ZJdr/ACJW0RVPhK/+z/FTPMp77W/i+7Tdnyr/AH63OOQfw7vubqZQ6bqP
                            +WaUEBTWj3N8v93dTn27nqF/vblqomMpDZPn+Zv/AB2rlv5SIGYb3X+H/vr/AOxqr92u5+EXge5+
                            J3xG8NeF7Zfm1K+ih2M38P8AH/46rU5ERj7x+uH7AfwiX4b/AAF0q5aNYdT17/iYXSbf7yfIn/fF
                            ei+KryB/EyLFA321W+V2bYnzfI6V3Giab/Ymk6fYwbYYrCJYvu/wqleWXl5FeXFxOzfOytLLbuv3
                            Pn3u9csjsh8R0FnDfXPlW19tR4l2QXCNs3bflSJE/wB9KxfGeparomk3GptY3Osbdz/Z3lTZE0Tp
                            8if76Ul5qUFtLFYtLJNLK3mqkLP+4i2ebvl3/dqLVbPUNSieXSrxYX8r/Rbe+V5YpbhU3o/95f8A
                            7OkXI8/8Q+G/D2pNZaevhqCaWWK4uPtF3vSJfNfYku//AGHb/wBAr5/+OvgzUL/Tft1trjQ6ZYLd
                            S2to6olxPbyy/I7/AMPyXCbf7u3Y1fRuufEu8+Hum+IPEviD7IkSqtrYom9vN1HZE/2VIv4YkVPN
                            3f7deD/D+a5+N/w3/s/WtK1S8fyLiyZ7GBEmvLdd/wBkR3/5ZRS3Hy/c+bY9ORcf5jwfRPh69hea
                            hqVzZ2l/plho9/cTvcS/upfPtXiS4T+Hcksu5U2fwVVsPCWq+IdDstMuWtoUsJd/2u0tvKRtyIjo
                            z7PmbYm3/eSvcn8ANc6S/hq8vvsEsqxRXjvFsSVYP9U6f3P9IRFiiR/m317R+zr4A0fx/cbbbT2s
                            Irjyrq8tNu9GWfe/3W/iffub/fSoj/KXKXL7xzX7P37H+mW1hca1qFnBf2USsnnTMn8T/JsT+GvY
                            /Bn7NOmaDqVpbaVPHptlFdNetvi2Syr8+ze/8KpvfbXReBvgs3gPxv4jvra5ab+17xXvLF2f9xbr
                            8luiL91VfZ9+vSLnTZZtUt7NoJ3iliXz5fvosUTu+z/gbv8A+Qq05Tm5v5R9xpdno9hbxNKt/d2F
                            m10qI3ySr/BWZr3jzRfhX4L0/XvFWq70T/R7G3tLXc8sv39iL97/AGaseJ7O+S/l/wBMVLRopYmh
                            Zf3s/m/L838K7P4ErM8baDaTfEbwZt0qCaLTdHv38maVPKtW/deU+z/b+er1Mjz22mvvAFnb6n4h
                            0pde8Z6zdXF1eP8AduEi+/b2+/8Ah+TYteFeJ9HvrzwXpmh+JfLv7rVJWitdWu2dE0b53d7VNv3m
                            /wBuvYvHPxU1O28aanougQWmq+KJZ7h/Jml/dQRLF/f/AIm/+Lrw3Tb+LwTo3/FX6VfX/iWwluNa
                            VJpf9EtZWfYiRbv9auz+P+H56zkd1PY5/wCIr6DqvhV/C+h6rcvZeH0s30fSbdfknupZfnf7nzMj
                            pub/AH60P+EPvvG15qekWc7aVrF/BLb6xd3Gx7jUZV2P9lT/AGUif/0Ot3wY+p3nhWynttDXTfFv
                            ij7Yi2LxJ8qq6ebep/dVE2baZpXh/UHvPBWh6Y8+t6rLLeRWc0K/6REzbN97L/s7N/8A33UF6nS/
                            8Kug8SfCF4FvJPD3h211iKyvr7yN7yxeVsfZu+7vf918n3ab4B8QS+BtJuPEPiXT/wC2NPWC6sIL
                            vUG/1sqfIm/+78lcZ8RfiR4u1LXrv4KaLqFpN4V0a+WXUdUt13+bKv73Y7/7b/erq/EL3Pxm+Jfh
                            zwPfarHonhyztW1W6hhXfFuiTzf/AB90+bfV/wCEx977R5v8XU0fw9daPeWzXOt6wui2cTTOjtFa
                            3k6fPF/dX/gFcf8AGzxbFo9vo+i6rO0zyqry28Lb9zMn9/8A2KpW3xXl8Zp4t2wL/Y8V0txPMmxH
                            Xc7/AGd0T7259iVx/iHQZ9Y01J4P9P1u4Vrj7Q7f6qJUT5/727/Y/wBiszaPu/Edb8Uby2+Etr4M
                            8AaLqqzf2losV7rF9DL87NLv/wBHfb/c31U8GW15qtu/hrTJYP7Y1LdaxPdts8pVTe7p9z+Df/tP
                            XmVzDodnrlk15fT3l3FL/p1999FXe+xP/HE+592sLUvHEupXWoW0FysMsU63UF3Dv37tjp8m35tu
                            x6sZ2E2sWyeD73Ste1qS/wD+EfupbKz0e3bZub5P3qP/AHd7v9/+/XBapNdt4Y1B7mD/AE6KVklu
                            3l3ytE/zbfm/h2/LWP4b0WfxDeaxeLeQWEVhA1xdb2+eXc/3EX+JqY+pQapdPFErTLPtRd/8Xz/x
                            /wDAKA1G6lrH2+1sp7aKP7QsXlT7PkTcqV09jeNDolusVi00V/EtktxMn3dr/fT+99/79Zs2mz3O
                            m61aaNpSvaWcqyz3z/woyfIjV7B8K/Beh+LdL+w69rjaPD4f0xb2DS5lTff3Db1dFb+LY6o23/bS
                            gR2Xwo0FbxtQ0rUJWv8Aw/E0Tq8K/O0qonzp/ufJ/wCOV9cfBDwrL9n0q++Wzi02eWJU2/O275/n
                            rzz9nXwzLcaDpn+gqlvKsry27r88Uv8ABF/4+n/fFfW2j+HotKt9KglijhlbdK2z+KnynNUkS2Hl
                            Wekv9pbzrt2Z1fb/AHv4Kx/H941no1v9hVd8sqp/t0X+qxTXksT/ACJasz/JXm/irxyyWe5l2S28
                            vzJ/srV8xjGPMWPHOpNptx5EE7P8u9kf/crxL42fEvT7z+xNQsfnvWgaKWFF+63+U2/8DqHxn4k1
                            C/uJfs1400su37ju7rurK8PfCi+1uV5bz7m5nZ3+/wDNWPNznfGMYfEcJomlah4qt/Ibclo0quyb
                            nRGbf877P71el6b4bsfCtn5reWjxKvzv/dVK1bmHSvAdvuby0uPvf71eK+OfiFPrd46q2yLd9xG+
                            8tHKaHS+IfHM9/cPFbboUb+CotBs57povP8Av7t1c/4Vh+0LuZm3/f8An/ir1XQbOBLdGX79UZyk
                            dB4b0pbaJNq/71dXM8VtZbmbZ/drlP7YWwt/mrjPE/xIbb5Vs3ybv733aDMveLfGDQs6qzJ/d/2q
                            5T+0pb+J23N81c5c6k+sM7MzP/7LWtbTJbWaL/ndQaDoUV7p933Frb85UtU/uVyiXLJcf727/vmr
                            d5rcVtZuzN86/wDAKBmf4w8VfYLd03f3v9+vF9e8aNfyvF5v3tz/ACVS+KPxCaa88hWX/gNcCmq+
                            c3+t+98/z1oZykdzpuveS21W+RfvPWqmqs67t2z/AIDXm8OpKmz+BP4lroE1VXtdv8dMzN258Q+T
                            K6r9/wC987VxnifxI1zv3f8AAfmqLUtSV97KzbK5e5dprhNzb/46NSeYEd/nb5qsWyb1/ip7L8vy
                            rv2/JvSi2RvN+Xcn975qNSCv9gVLjeq7HatC1sGuWiVvk+X+CiZFeX+5Vq2uVh3t/BQBYe2WH5f7
                            vyVi3M29nVfko1XW/uRL9/77Vz9zqnzfe+ZasPhJb/UmRqxZrlpm2tRc3HnNVetYx+0cFSpzfCJ8
                            1H3qbRVnMFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFF
                            FABRRT1WgCxCV+92qdE3VFDH/FVuGFv4W+T+/WEj0o83KY9FFFbnmhRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFF
                            ABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUA
                            FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFABT2/hplO/u0AfTH7Md55Nwnzfw7K+5vh1efabiL5d7r92vz6/Z2vHTVLfb8m35f/H6/
                            QX4awtc3CMv32+SvNqR94+hofwz1h/8AlkrfPuqvc38szPFFtdFqpc3nkrtb7+7+GjStsyyxbvJd
                            l3s9BpqaEM3kqm7dv/uV418eNWa/s0tl/u/Nvr1p/NfZ97b9xfmrivHmgr/ZssU8DTXsvz/8BokK
                            J8SeJNEa2uvIdWeX5XZE/iZvnrN1XSorNtzMyOy/LD/HXoXjnT4tHvJftMu+WJt/3vnX/YryLXtY
                            nvLzz/K852ZUVN1YmhXv7mKFdrfuX+/XOXOpWzruZmdF+fen39taGqws8SLPueXaz/Ov3fnrnblG
                            fYqqzoq7W2f3f79XykakqXKzW7+Rt+z7d7f39tc1qSK+xlXYzfd3LWhdW09h86sruy796f3f9uql
                            zGtxGskDNs+/sf8Ahb+Naf8AeAz0Rl+Zv71V3fzN+5d/8dTOzbni+bezVDdPt2qv31/uVtEzly8p
                            X3/vdzU3erqir96j5WXd/FSK+xf92tjjkNT/AF1DP/do2bFpn8VBHMNb5Vob/wAi0n3qP4VarMZB
                            /u19l/8ABMvwNL4q+PH9ptAv2LRrCV5WdN/72X5E/wB3+L/vivjTd/er9Uf+CTvgyfTfhp4l8RvB
                            /wAhK++zxTf7MSbf/Q6VQIn21qqb9Gu9y+dF5DIybv8AYrxxE+zfa4rOBZriWX7UqJ/y1+T5E/8A
                            HK9Q8Z3k9nZxLbL53mzru/gSJV/v/wDAq81ea5sJ0a5aS8eKVotkK7Jf7+xP8/drmkd9I0raZYbB
                            Pmjmt4m82WF/ndW8pPn3/wAX8dZt5f6gn2vUGnk/s+WdkghsYE82L7nmo/8Avunyv/t1K8NtC32z
                            +zPtNvEy+fDcL5W1v4Hb+9/B/wABohs9XvPtcS3McPm+bFPvbeitKn71E/2aRcg1jw7pmsRW8q6f
                            GmsNA275vkiXfvf/AHmd0irxzxDf6f4J8W6VpS6gqarcS2t02mJP+9li/wCWT3G35v3Wx/k+7XfX
                            n9r2ccunwQRw2Vh9ni+yTXT+bK33Pkf/AL4/4FXiSfC+8v8A44an4+8SztealeRK62lpAyfZYtnz
                            vtZ9vz7Nv/fdORFM63xDo/8Awm0tvFY6Ut/LFPEljDdweVFAyo7o8r/7D/N8n8SJX0v+y78PbzwD
                            8P31e8uoNY1DW777R9rSLyks7XYkSJFu/h/dbv8AgdeQfCXSd91p8DSzw6nEtx5Vun+kRSy79+xH
                            X/2f5a+j7BtV021li1PUvt6zvcRWKLEsUUUUT7E3Kv3t+3dV0/5jGt/KTTP9puJd0DOkq7J5n+//
                            ALCVzV/5F+1jrl5Pcwy2f2hlSGXYjRfc+f8A8fqx4k1KLTbW7lWVUeVl/fOz7Gl+4lO1Wazs7Pcs
                            7bIvuoi/e2702P8A77vV8xESumjz+No9QXWv3OhLOt1FNu2vL9ze/wDup/D/AMDryKz+NDeIPH3x
                            L8QW0Fi/grTVg0q1eZtlxdNAnzuj/wBx3dFru7+8g8Sab4gg1rXI4dH+yypczaSrtLFE2xNmz+DZ
                            /wCz14z4/wBK0rwT4X8CeFdK0r/iVXmv291fX0zfPtiff+9f+JnfYtYykbRj7xwr+KrHQ/Fulf2h
                            oP8AZviCwiXSmfzdjvdTvvll/wB37n3/AP2StDWJl8W3+lT6nqa39xu/sXTLHb8ixSy/vXd/4qyf
                            iF4n0XXvjrrHiXULFrnw14SWWJodipLeXXlb0d3/AIl3/L/wOsfW9Q1fWPEuj/brmxsFuILe9s7e
                            Fdj6da73d9/97fvSsTs5To/iJ428R+Nvi5p899piwxeFdOl0C6exbykv3d0l2Rf7PlJWZqXiS20r
                            x1d+P1/tDQfCmg2P2KW30xt0rLL/AMu7v/e+RPk31b1v4irqvjS70xdNZImi+0T3e7Z5St8nmp/w
                            BHp3iHVtBuf2OPHGlafbRwp4g8ZfZdKhfZvaKJLeXe3/AHw//fdamMvd+E840eaxvND0qKKWPQbe
                            Xdey/Z5/9IaKV3dPNf8AjbZ/7P8A3Kr+J9bsdN+1zrqskNlbytZS7GdZWt2RHd0f7250V1/2a+f/
                            AA9qUGifFK4sfEM7PFaxLFBC/wDqvl+4myvQvDE2kePNZin8S332bw5Z3TS6ikK7E+zxI/7r/gfy
                            VJtL3S9a+JPB3w3+FSar4a0przxHea/cSsl9/wAe/wBj2fIn/AP4d/8AFWD4Y8baZo/w78UT3MU8
                            3i262vp1w/8AqrWLytjxf73364/x/wCJ4NY8cXa2NnJpXh/7V/oen/cfyt/39lZviiaDWG1DU2X7
                            BpUTfZ1hT78rKnzou7+GjmHqVfBfjLSPDbLLc2i+Ibu6tZbdrd/k8qVn+R//AB1V/wCBVjWdg1zP
                            rW6W202Wwg+0LC/zvK2/Z8n/AACqWsXmkf2ylz4es2ht22uqTNv8plrMeG71XXklVl+0Ts23Z9xf
                            k+5VClLlNa2k8nUdPvGsYHTymilhhb/Wrs+T/gVS6bZz2bPeboIbeVnii+b+Lf8AfqlbW9rp+neQ
                            00v9rpdr/o6fwKrbt6f8Bq/oltBqqahFc20+9l821iRfuy7977v+AU/hCJ3fwu8Gai/iXUPDTa9H
                            psU8DXV5cbt6PEqfw17h8E/hXK+raPbX0rJb3k7W898i738rfv3p/v7Kx/gD4PWbUrS+W2V7htO+
                            yzpdq/3v76f7NfbHwZ8E6DZ+FdKa5ud93Eu7Yn/LKiPvGMvdOz0TQbTwlo1xpGlSK+nxXTXVrNMv
                            zt/f/wDZKZc/EVbmztNQ2+T5UrI29qpeLfEltZyvBpjeduX/AL5rgZnn1Kzez8jekrbt/wBzbRKR
                            EY/zFubxPPrGrXu2VoUlZnb5q5y/sLm8l2su/wDhZ91dhpXhtbW33/3f43+/XP8AirUIrBn+6m2k
                            bR5Slonw9Wzf7c6/O38dbs3iex0eweJdu/5k+esK5+JECaTLErK/8C1454k8YPeXDqrfJ/3zupxj
                            yh8Zn/FfW5dV1J2WXen8H+zXmS2bPI7Mu/burrblJb9X3NUV5bLDa7v4GrTUP7o/w8zIsS/8Drur
                            bVWton3S7Ny15/peqxQxbt33fkqLUvGDPcSqu10Xb/wGjUJHS+J/GEsNvtWX/gf96uFfW2uZXVmb
                            er/Lsqvc6qt5cIv8H+9Wejqlw7Nuo1I5jpbPUFjX/wAcrYS83xfP/wABrikuV2ojNvrYTVfs1u7M
                            3z0ahE07nVYIW+avKfHnxI+zRPBbS1n+MPHP2fzVWX52Vv4vutXkmvax9sll2v8A99M3zUBKRBr2
                            qNeXTszfxfL/ALVWtNfztv3d+75q5++3NGjf3v8Aap9hftDu2bUf+GrMeb3joN+/7vz06S/l2ptb
                            7y76qpMzqm5dj0xHV/lX5/lb+KgCW5uWf5fv/NVe2Te277m6i8dod+1v4qpWdyyt5TN83zf8BoA2
                            PuLubd/t/NQk2xfvf79RXNy3zs3zoq/L81YP9pbV+as+UPd+2dA9yqfeZfmX79VbnUlhi2tt/wBx
                            P4qxX1R2VstuqnNM0z/xPW3szGVWMfhLlxcs8m7d83zferPZ2dqPOb+Gk+b71aRjynHKpzEe6l+9
                            TaKoxCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKft+Wk/hod91ADaKKKACiiigAoop
                            yJuoAWPb/FRuX+7Qy/NTKAH7KNtH3vlXpU6QtQaKPMQLHuNWoYaEj21dhh+X5v8A0GsZSOunT5fi
                            JraHZ8277tSunzJViG2+/wD3G/2qPsv3Pm+Ray1OyRyVFFFdZ4gUUUUAFFFFABRRRQAUUUUAFFFF
                            ABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUA
                            FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFF
                            ABRRRQAU/b81Mqbn/wAdq4ger/BPVfsGsxbvuf73+3X6K/CK8V7hGZtiba/ML4d6l9j1y33fe83+
                            9X6N/Aq/ivLe3Vm+dlVPu15tT4j28NLmieu6xeLDePu+dP79WNKvIoVf++y7K5/VZoka7Zom3/Mi
                            vurT8DaC1/dQxLKv3d7O/wDDWMTsqfCdglms2lyy/afJTd82/wDu/wB+qN5o8Gt28rSzyQvEu+J/
                            71dHc2f2xnaKLfb+Rs3u39379YWq3OoTXj/ZtsKff8nb975/4HrU5oyPk/4keCft9/eyq3nIz/cS
                            vJ7nwZ9m/dLEyMv+z/4/X1V450r+zbe4laVkeX52+4leT6rc3NhF80S/vYG8qZP4W/uf+OPXPI7I
                            +8fOviHTZftHmt8iKrffrj7m3Xb8qskv8Oz7jf79eu+M7D7ZE+5fJRW37n+427+D/vuvItbeKFXi
                            WdoU/im20ESjynP6kmy4SJtyIi/x/wAVZ6v/AGPNvXa6S/d21aeGVotzNvRlZ9n3dv8AuVlOjI21
                            mV0WtidR95tSWVW271dqpb12Pub738NOuLlpmdmqJ0+Xd/6BW0TOUhjL/tfI1Rf31X56c77qYnyO
                            9aHBIX7iVDT/AJqiqyJA77qKH+Wot9Wc0pD4/vfdr93P2PPAEXw9/Zs8G2K/JNLYrey/390vz1+I
                            fgzw5deLPEWk6TbRM73l1Fa/J/tvt/8AZq/oP8JWDaV4f0rT2XYtvZxRbP7u1KzqHTTj7phfEi5l
                            sNJt4ltmeKX/AFsvlb9q/PXkkM2+8RopWd4ml8p3XekTfwf+OV6n8WoZX0m0iWed4pZYtqQ/I+5X
                            +5/4/XmlnNBcxRWKt9g+7eskMTpLtb/0L/gFccviPSo/CbqQyvcP9pike7tfnlSGLf5W5Pk/9n+S
                            rGpSahc2FvFeWazWm6WKV4ZU81v3W/fv/vfcqlYW0GsRfZrlo0/jaF22JK38Cb/4vkq3Z31zN/r/
                            ALJNbyy3CKlvK8SLa/wb3b+KqMahUvEa8V5dPVX1iWK3spXf50tWVHf7n8Wze/z/AN6uE8Q3MWsW
                            t3Ku57S6ZbK12K+9v3Wz/P8A31W3eXO+/u9Pg1C58qwXY+p2K/Z7f7RKj74vN/iVE2t/3wv8b154
                            +qt4V0uLU/CFtPraXGkta2Lbk+0L5qeV9oiRk3MyIjrv/wBt99ORcYnufwo8P3PhfTfEd9pTafYa
                            mtq0UU19K7xLKsX7pP8Ac37d9dhqSa9YRaEuoXLX93pNj5V5d7Ui8+4VNksuz+FX+9XgPwa+xeFf
                            gv4W8OeLGvdS8Sy3lhLK6xyyxReVdLL80v3d6KmxU/il2L/FXvNxrFtqWoanFazz71nVFRU+7/Gn
                            zt935H+5/t0Rl7pzSj7xX154prrR9PWza8spdRW9b+5FFEm9Hd/7u+s6aRtV+0arBeQXj2Cqs9xc
                            furdkaWVkdE/ibatbelaxBbW97Bc30l/cNE0tqm352i83Y6b/wDYrldVm0q/t/IuYNkVm3mxRPK7
                            u25/v/7WykXEwfFVzqFn4PvW+H1nBNe3+5GS7XY/2Bv9bL/vIn3f9yud+IUP2bS7K51PyNYSVvst
                            jFu2fvVTzfNRP7qIj1mfFHxDpV5o1w3h7V5NBSLWorKf7Wz772Jv3UsUX++j/LTE8H6UmspqrarP
                            eXHn+VFDt814IpYtjoif3kV6Dp5eU8/0S50z4r/FDU7y+0VYfC/2X7RFabtj38rfc/8Aia4XxPC2
                            gxWniO8uWv8AWNcnt0XT1X5IoopdiJv/ALuzYzV2VnYS6JqWj6G1y0Oj6Mt1cQO67JfNZ32I7/xK
                            ifdrldY0rT4fsmq+bJM63ixLsb5FXe+/Yn+471kbnQaxr1injC38Q61ZwXlppNmv2rTIZ0R7zcjp
                            Eif8DrynxJr15rHm69bLBZ6Zpdmssti7bIluGl+dE/h3bETd/wAAqv4z/sGwXU5bGeea7l1HZ50z
                            O+2LYmzan92sK/vLOGLQvD1tu1iW8umlZEb/AMf/AN5NlHxGfwnk/jZNV1jxbb61qNp9jS8Zn+RN
                            nyqj/PWn/aUtnpMWlNZq9pqkCur7vn2/feul8eXltf3lxFY20kz2Ct5+z7kSqnzuu3/vlq88ezl0
                            e68+5nWHauxURv8AVb/7lX8Icxe1Xxo1z4ol1W5ijmlig+z/AOwvybN7/wC1XL+JLa+h0u3nvpdi
                            3Tb/ACl3fd/v7afqurRQ2KWNnEvzTrK127fPK330/wCA1n/Ejxhc+KtWiluY44ViiVFSFNiLt+T7
                            v/AaIx5iJS5DPvJkW/i2t5Kyr82z+FqtWOly3KtPbO0LxNvV3+V2/vutVfCeg3mvXjyQR74rf55W
                            b+7XdfY7nUtSiis4PJRV2KiK+9vn+erl7gR98r+EtBa21ayuYNqXDbkaWb50+b5N9ex+Cfhjqfir
                            xDFc2y+TZLEsW9F+98mzf9yuq+EX7OV94k1y0lvIvJtFVfkff/6HX3B4Y+GOleCdGiitoI9+1Uaj
                            l5y+aMDx/wCHXhVfA2m2W62X7REvzTP87t/sV21heXk148tszQ+aux9n92uoudEj1BnZdyP9/wC7
                            WhpuiRW0T7vvrRymMqhiW2j7GlZtzu3z73rVtrBX+6v8fzVsPZqy7d2//gNV7y5j0eweWdvnWjlI
                            5jn/ABb4qs/DGlyszL8i79lfKXjP4utqupXHkNsRm2fNUvx1+Lq3l1cWays6bv733q+df+Ehaa63
                            fxv87VobRjyxPbbPxDPcxfM3yIrP/u1XS5+2XTqzb9v+1WJpV5FNpLt8vzVBZ6wyXjt82/bs/wB5
                            aNRHVPqUVns3Nv8AvVleJ/EK/Y1Zf9z71c/qWqskv3l2bWrn7nVftMX+xQQOTxC32fb8yfx/JWf/
                            AGsrszN/F92se8uVTe3zO/3NlFn++ZFb+Jvmo1A6j7Y3m/L8/wAq7qtu6/J/cb/x2sp5orZXkZl/
                            4HVHUvFUFtb7V/2fk3VnEDoIbmKFvmb7u7/crmvFvjlbOJ1Vtm6uU1jxb9mtZYlZUdvn2bq88v8A
                            xD9vuPm3bK3MpSjAk1rWmvLpf95tyVRebfvkX5N22syR2Rt601ZmZ/7tVynN7b3jSuJPOj/hT/Yq
                            K3O3crfxbfmpvneTEzfx7v71VvtLb6OUJSjzHQPfqm+JV3vtosJvmf5tiP8Ax7qwkmZN1WEvHh+X
                            d8lP3i4yLupXir8qtWe02zbt+eqsk29npn/AqXKYyrl57zcrqv8AF/tVRd91FN524rSMTGVSUhu6
                            lR9tNoqjEd5lJupKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAopyJuo/hoAbTvMptFABR
                            RRQAUUUUAFFOjpVWgB38P+3Rs3U3b83PyVY+5t3VJcYjNq0eS38NS7P71Som6s+Y7PZldIf9mpo1
                            3tUv2f5W/wDHqmht9rLto5i4x5Ahh/dbtv8AwKrSfIu37lM+bZ8396rCWzuvyts/3Ky1NviJkdU3
                            7qtIn8K02G3Z1+dv96nTOsK/L/F/45Sj7wS9w4Wiiiuw8cKKKKACiiigAooooAKKKKACiiigAooo
                            oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiig
                            AooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAC
                            iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKK
                            KKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooo
                            oAKerfNTKd8yUAdB4Mk8nXLeX+BWr9A/2eL9X2Sr/wAslr899Fm+xvbsv8TV9p/su+JFeLyt3yMq
                            1x1j2MNL3T6Y1W8lm2K3/LVvuJ/4/XceD7Znil8htibd8r/7NcTf+VN5TK+9/nrptBum+wPAr/Oz
                            fN81YxOyp8J1ttcrDa/6/wCSL7qI2yh7+CGwm1C5VkSL5IoUX56r2yRX8qKzeSjNsXZ/7NR4nvFS
                            zijiVfs8TbPk/iqiOX3jzLWra28SN/xM/Phdt0Xyf3/4HrynxPbfY99tOqvcK3zJ9zyv7mz/AH9j
                            /wDfb16t4n1trNUVd01wzfNsX7v+3srxzxP/AGnfy3d5cxSJtVUiuJvv7N/8f/fH/jlZHTE8k8f6
                            ks1mnnrsRV8qL+5uV/n/AOBfPXiut3K3kvlL8m7b9z+7XtviS2ivFRNu+KJv3vzIjsrf3N1eZa9p
                            qpcRNZp5KLKqLE67H+Z/46gioeeXzt9slVpdlrF93f8AJurKSZX+VV/77/u10utabG11KrN8qbl/
                            uInzvvrn7mxjT5l3OjN8q10Ef3TPuX87ZtX5P9haqVsPCv2f7nku33U3VBc6bLDEsrbXTd8rp826
                            tIyMZRkZm7+9Td3X/aqR38z+H+Kov96tzkIt9D/e20R1E3zVZxSkDfM2KSlf/WUkdUYn0X+xb4Vl
                            8SfG7wzt3Pb298srJ/A235/m/wC+Vr9tba5VrhYm/wBbX5X/APBOjw8yePNPuUgWbbFLcSu/8PyV
                            +p0M2+X5f4q4JfEerL3Yxief/FG5voZX2zq9pFtfyfK+eJW+SuB3t/ZcTWbQTSsvyzQ/8svk+5/s
                            tXcfFTSoPtCXK7vtEtqySw7m2S7f9j+986NXn9tNcusqtZwQ26LuaZG+T/P8VY1DspfCW7xGv7z/
                            AImbRvaNFsXTE2bG2/3/APaf5KvPDYv+4vImv7hmieK3hX5IokT5N6f7ny1jf2V9p+0RQRLZ7V+0
                            RTebslZv4Pkb/wAdq3DfskSWdzeLsvFltVm81bd5fKiTYn+6m/79UEolTW9FttY024gvPsMMXn7P
                            s7rsT7jpsdP4vkf/ANDrFS2gmvGg0/Vbawi02zuk+RUd13bIt+7/AGPnVUrd1K5W8tU0jTLO2vNT
                            2raxOivsbamx3Z/9zf8A8Brl/DKQaJpuqytY2msO264a0tIN9wzRSpv2p/zyR23b6BHe283g6bSd
                            Js7O+1DR7i11GK9a3hg3Pfqtwipbo/8ACrvsbdXcfbJdNurtrll2famibyfubfuRf8C2Ii14FqV/
                            pfxA+MHhDSrTTdYtrrwlp9xrGoeb+6ivGZkSLbtf/VI/z/8AAK9d0q1vrDTYrOeVZvsq/wDH28Wz
                            zdyfvZdn97f92rMpROX8T3N9/wALV0SKxbZFp2mXVx9nRtiS75djo/8AerbudSvJrO0lufISVYvN
                            WFF+7u/gT/gD1w91eNrHxE8KaNc23nSxWMuoT6n5uy4+z/c+zun3vnf5mrTvHs4VfUbaWewuPIbb
                            vXftb+5tb+5UG3KcJ8V9Ki1vxV4EsbOznv7uXUWvYrSGJ98vlRb/AJ/7i/7b1q239laDqz30recj
                            S/bWu93/AC8Kn3Nn975//HK5L4o+LPF3g/x9oWmWdy323XrX7EuoeQiyxWrOn2jyv+AVu+J4YtBs
                            NK8iKN7fTYpbpbd1dnZP7/8AvUGmpx/ifR4PtV3pVzA0N3Zxb2fzd7rF/H/wJ64ea5ttStdE1CeV
                            bays2uEih/567U2JvT/gD11GleP4rjXr3V77T1s4orNZZ3Rf3t7LKm//ANA2KqVy/iq5s7PVNK3W
                            KwpFFKiwp87ytsffLs/23oLOF1LxDptzf6s1tZq6RWPlLvX/AJeG/wDZ0/v15tpsMX9s6ZrU91JC
                            8UrIqoz713P87/8Aj/8A45XV6rcweVLctEyW9rLvV/uJKzP9xP73yV5/c6fqfi2XVYNKgaGKJWuG
                            f7m1V+d331IFu28YXmjt4ji0FdkV/FLZS3br/wAsm+//APt155rdm2l6pcaYt59vSLbLK+7ej/Ij
                            /wDAqvJeNYWvlW0rTbV+bYv/AH29YKQypeSsy/61fl+b7y1ZGpVvr/etwqxMm5/3Xy/dqWw8Jz6l
                            KjMjb5fm+9XR2Gj2c32KL/XXHzOyIv3fnr3X4UfBy88YXFvttm2eb9/bRzfyi5ef3pHBeA/A+oXS
                            rZ6fBJu2quxN/wC9/wBtttfVXwW/Zs+zNFqGqxb3/wBv5Nv/AACvY/hR8ENM8GW/mtbR+azfxr89
                            ewW9hEmyJYlRF/hT5auMeb4iJSjH4TH8PeHrPSo4oraJUf8Av1q39tLcR7Wf5F+7TbzbZsjLtR1+
                            emXOqqlm/wAyp/G1bnH8RStnVJH+b5/uf71Q3WsLZq67tj/xVxupeKlS6eJZfv8A3XSuf1XxOqb9
                            0vz7vv7qjU25T0i21hX82fzfkrw/46fFptN027toJfur/wCyVoar4/XTdLlXzV+7v+9Xyz8TvGDa
                            rcSsrM+7/gdLmLjE8/8AE+sS6xqUrMzfeb/2SsWzf/Stv96neS0zO3zP/Hv20+2TbcP/AH221ESj
                            tbDVWhtdvy7Nvy76vW2qrt3Lt3uv3ErjLnUGtonVW3uq/wAFRabqUrruZv4q01IOg1vUt6ptrPhm
                            b7O7N9zb8tOXbc/xrvX71RalcxWdu7bqz90DnLzUm3bv+Afeqa21VY5UXd/Du3pXKa3qqp9xv4me
                            se58Q7N22Vd+3/KVpqZSlyHYa34qVIvlb5NzfxVy+pa2zwbl+43z/ermL7VGvGRW3Ii1K82+3+Vt
                            kSr/AN9NWnKR7XmK99fPMzfNWezNTpG3t/dprffNaxicFSXNIT5qKRvvGkqjEe0u7Z/s0L81G1aT
                            5koAPu0/ezt8tRtSUFhRRRQQFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFF
                            AD1ak+9TaKACiiigAooooAKKKKAJflaiinqv8W+oLjEYtWIV+5uojX+KplXdt/i21HMdkaf2hF2p
                            /t/7lP2fMlPhhV6tLbqn+x/BUmxV/h2/3vu1d8n7v8dP+X+GmXMyou77j/3/AO9UahzD0Rd3zVYh
                            dY2dv4F+esm51JU37fndqqtqU/8AC3/AarllIx9vGJ0s2pbG3Myp/uNWJf6x5zfut1UHuZLhtzNV
                            dlNbRp8pFSvzjKKKKs4wooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAsQv5Mu6vqj9lfVWS4iX
                            5dm77lfKX+7XvX7NOqy22rJE0uxN/wAtY1vhO/CS97lP0AtrlppYk3bHaXZXQeFbNblvIefY6r81
                            cf4e2zLY3jfvk2sv/At/369I8MWG+4lZYtiS/wAf+1XBE9iR1dtCs1wirF91d+/+9VLxDbfabCW+
                            lWSF4trrbp/EtaVnZyzapEs8+xG+SVNtdBc+HvJXb5skMsTfL5P3/m+f/wAcStuU5ubkkeGXPhtr
                            i6/tpblvKVfNlfd96L+5savH/idrE7aa0qxQQ/xrvX55fvuibP8Age6vo7xbDP5t7A0H7qKD7Va+
                            S2/zZdn39n/slfKniqz+x39vPc2fnRRRfvUmneKVfn2I/wDdZ03uuz+JdlRKJ0xlzHk959pv4opV
                            ibZLKrsjr91VRHR0/wC+3rl/ELwXlxLPtZ5W2/Oi/wB19m+vQNbuYHuLiVtyW7M0UDw/fii2fJ8/
                            3d2z5a88v7y+trqVoJY4ZV2o0M2z5lb+/wDJ8zPURiEpHC627Xi3Cyu021vl3/Ju+f7lZMjy3N1t
                            aVUiXa+xP4V+Sum16wa8ll+2SwI7KzrDDFs/4Bv+7XGWyTpKvy/I3yb3b7q1qRzGhf6VHDePPdPO
                            8TbtqJ9/bv8AkrPm0uWFpUX5Eb5dkrfM39ytV0uprLzVlVHibyl3/fVVqlcwzzNuaXzn3fMm56DQ
                            wLjS5Ybh4lXft/utWddbfvV1FzC0KvKsUkKbtm/b91v7lY99Zqys/wD47trWnLmOKvT933THdmps
                            m7+KnP8A+PUySus8eQr/AOsqW1Tzp1X+81Q1csG/0yD5v4lokOn8R+hX7CVs0Pir5dqXEVnLtf8A
                            vbtm+v0Q0e5aZkVVZE2/3fu1+cn7Ddz9p1u7ZvnSKBk37Nm1W/g3/wDff/fdfoRok3nW8W1tjrtf
                            ZXBE9SRzvxRm33+nt99WW4i2f3dyff8A9qvLNNm1Cawt0WVYUli2RP8AcRv9jY33q9N+LU3nS6Va
                            s0kKbZX3ov8AdT/7OvL0s/7L0m3gWVniiZpYPJbe8XybPv8A92uap8R00vhLCP532ixnZprjymdH
                            f50iai20eKaX+11gk/tBbX7F9ovvkS6VkR38pP8AgCJ/wCqmlaXeQ3ST6Vczw3HzeQiNv8pZd/8A
                            6G/3q2NB025sLV4Fn+33ESrbzzPP5r+b/wBMv4vuURNpGF4tm8VWdrqE9jcwaPqbNLFZ/ZIvkit2
                            iRNn97c7u/zp93Z/sVzXgPTdK8H+H7eK+1W7v9Vs7Ge3iuPKfetvF9zYn+3Ls3f3tldhbarPYXD2
                            1tLB9iVluJZreJ3ln2u+yLfK/wDfZ2/77rH1i8s002W2sbGN7uW1lSe+81E8q6i+f7Om75l+Te33
                            K2/vE6mP8Pby+vP2jNQ0+6n864sPDbRNcO0XmrFK6b5Xf+LY+/5K918W+IbbRNJ/tO5aN7eJvmmR
                            tiRKyff2f79fOXw31XSr/wDaq8Uf6HJ5UVitrA9xPslZk2eb93+He9fQWtvP4kt9KRYpJreVvNuo
                            X2IiysnyVMZc0TOp8Rx/gzxhqOq61r1jfaJaW1xo0sUUurJueXUfNRHTdu+6qp/AtdNrbxWEV2zL
                            IiL92aFaz/D1q1zYXsFzpCw3H26WVtZuJf3V1brsVH+X/cZad4n1vfarFbW2nvp7bUabzXT7Ku/e
                            77P4v4P++6YvtHgXxXvNQh+MXhSW5n+2W7Trb2fnfOi7k+fYldBbeVNLetqepLfuyyxfYYW37Wb7
                            ib/+Afx1t+M4fDkN1o/iXXILm8uLBZU0yxsYv9bfsn7rcn8Kom9qzLbVf9Ae2s4t7y3i+fNDF5Sf
                            am/vv/sfPuqftG8vhOKudNbW7rQoLmf7BplrZ291Kj7P9bv+dH/4BWZraL4w8aawljLBDZRWu2K4
                            uPuPt379n/A0rtdLs59S1bWJ5/snlRN5UGxfkXa/yPs/2K8f8Z3ltqvi2WxaX/RNzbvubJWZ/wC5
                            /v76BnBarf21z8Prue2lhhls7r5XdvnZmf5Pk/4BXn9zrFzeWqahPfNZvfq3mun7pNv8af7W+uw8
                            YWdjbaXey7Y0Szutux/n3fcd0/4G6VwnjabVdV1y0W50xdNiaJZYLSH5Nyt89AGfqsNn4fvEiaLf
                            E0DebDt/iaqulabeardJJOuxNuxVSrul6J9v1J1ZWml2t87t92ve/g/8Fp/HmrWVnFZ+Tbrt82ZF
                            f+L5P/QaCNSj8HPgJP4wv7dlib7P9xn/AIN2+v0D+HvgCz8GaTbwQQfvdv8AdroPhd8H9M8E6bFa
                            W1sqeUq16LJoMFtL5v3NtbRpnLUqHH7Psy7mX5aHvIki+b5HWr3iZ1hZNu2uE1XVWh2fwf3a6fhM
                            Y++M8T6wtnE7M33l+VK8s8Q/EKWFZVgn2I3+1T/H3ifyf3Syq6ba8N17xUs1wkTSrsd/++ax5jpj
                            E7i515pv3u7e7K33/wCH56xLzWGeLzWZti7v4q4S/wDE7I0SLLsT+5uqreeJ5ZrN4tzfL/46rU9S
                            h3jDxDLcq8Syt8rNXkGt3KveP5rfOzN87Vv63ryws/zM6bf41/irimvPtN55rNs+b5aziBob1hi+
                            Zd+35/8AYrHubzZdbm/2au3NzFDa/eXezfP8tc/c3PnfMzf98UfaILGpXP2nYqfxNT7a8aHZ83yb
                            q5q5uWS6l27tif32qV7xnt02tv3fP8laak8x1FtrDIz/ADVj+KtYb7PLsb5NrMtYVtfslwqq3+8l
                            VNbvGa3l3fxfLspcoSl7pzV1qUt425mqlzTm+++2jzK6kjx5SlIav3af5zbFj/hpP7m6m7fm/v1R
                            A1qSiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACnr81MqWgAqXY22oqf5lQbR5S1Cm5n+b7tWERUaqSTf3f/AEOm/bG/
                            hb+HZUcpt7Q0vO+9/wChUPeKrfe37fvVlPNLJ/FUTM5+9R7Mz9tIuvf/AHttV3mkm+81Q0/71aRj
                            EylKUhu3+KnJuejb/FS/3cf5atSBFb5t38NNk2/w05m/763UySgBtFFFQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAPr1j4G3jW+uIqNs/e15KvWuy+HV+2m+IIvmZNy1FT4TehLlmfqP4GtlvN
                            L0zbueLbs/v163olsttZvui+T+L5q8k+An/Ey8K6fKzLvii2L/tf7de13ELTWqKsbJ5rLEyQt/DX
                            BE9yUi3pU32aWKW53PLKypsf+Ld8ldLbabc39/FbT+fD5TbJZkb5Pl/v1j+TPZ2F7Z2KxzagvyLM
                            6/6pVoudbXwxf6fp8/mTWTQN5rxN88rb62ickvfOf8Z2cGsazLK2ntD9giaKxuEb5938exP4lr5s
                            8YWDXnh+XUINPnvLvz28j7Qux5/+eqIn/A/l/wByvou88QtHob+Krazaa4liltfJu12SxNv+4leG
                            eKtN1Dxn4P2tY3NnFZ3UWq2exkS7+0NvSWJ3/wBz71RI6aZ8++IdNaG3ezRftl3EypsT/lk2x32P
                            /tJ8nz1y9/4Y1W5W3l1GJYYpV+Xe371l+f7/APs19FX+iafbal9mWxjs0Wz81d7P825/9bv+7ud9
                            9eZX+iS6xLFqaxSIksuxbe4++sS/fd/738fz1ibniUPh5ZrhIp9s00r/AC/x/d/v0y58HwTat5X7
                            v91uff8A7Sp9yvRbzw3FDLtZmme8ZnV/uPEvzrsRP+B7v92orB4tNuLufyPtnlStv82Leiqu9Pn/
                            AN//AGKgXKedPo6zW9vc2zR/6R86w7fn/wBt6x4fDE1neW9ysvnWu7fLs2Pti/v7P7u7b89elQ6P
                            c6rK9z9l3u37qC3RnSJW2b9jv91V/wBis+2tv7K+0ahc2zTRRM1v9k/vKyOjoif7D7GWjmNuWB5r
                            r2jtsmktl+SWVop0Rtib1/jVa5TUrC+t1RlVniX/ANlr1t4W0rRrhXiWZFlX5HXf+62fJs/2v79W
                            k0GWa323MCo7K23Yyb9uz5N6f7e9f++KuNTlIlT54nzxcNvl3fMtQ7dr7fmr1vxJ8NZ7y8f7Ha+S
                            8UTOybdiNt+++5q861jQb3RLjbdWcltu+6sy1306kZniVsNKBjVPbSbJFaoXXa1CffrY44+7I+7f
                            2JNVazXUJdy/Mvzb/wDgH3K+9fD3idUZJWbYm391/tLX5m/sn619mtb1WZdrSpu+bY6//Y/LX1/o
                            Pi1kW0ilXfF99tnz15tSXLI+hhHnieveP9e33Wj7ovORfNiV3/iVkf8A+IrjJodlwm1f9Ea13pNv
                            2fd/g2VieJPGzX9vp9syt5ss7W8T7fk2sj//ABG2uotrZtyQTzs6eV5recu/aqp87/7Vc0pc5fLy
                            D4dK+32dxEs8k1p8sUt2kWx/9z/ZrP1u8tkZNPVpLBGiZ2uIW2TRfP8Ac3/7f3t9bF4/2O1S2ZYJ
                            rf78SJ/uJ/47XOa9GuqxRW08skNvE3zeS29G2pv+5s/v/wDodWMx7/Xp0tb1lXyYrWL5Xml+eeVt
                            6fJF/wB8N/wOuF1K51e8idrPTLR/7UupbeJ0bZ5TLFvfYn+xs+Z66jVbO8uWintXbZErboUiRHi8
                            37+x/vbfv/8Afdcj/ZWlW0XleR52oRWstxFd/apdirs+d9n3V/ur/d31YHG/C5765+PGpqtyv2uW
                            KVpUT5ElbzfkT/gGzd8n9yvrr/TJriJlZr+x+yrthRtiS/7/APdZHr4a8K69LpXxsSfT1jdJbpbe
                            JEb5FVk+4j/xfO9fZvhW5WwupYp51mt/KW9bZ8kU/wB/5P8AZ+5WNIqtE3tNv9M02y/s+2nkm+2a
                            nKipNF8kTfJ8kX95az9Ytvs1hqc+p+QmmS7Wlh2/6pt/zv8A+gVY8H3ltrem+H9eiaJ7SWCW6s4X
                            X5/Nlf53f/a3vtqj8V4ZZvC/2bVdqae19ayyptfzpWXzd/8A8VXQcv2jyLxDr3h618dJqqrfald2
                            usW9rZvsdIp5Zbe42S/3fk2Vd+3xaPp13efM7reNK39xmff/AAf8Drd/aB0G08MR/CfQV3We7U/7
                            V1Vv41lnR4rVXf8A2PnrI1iwle1uLOC2jfypWef+N23f7H/A6y+0b/FHmOB1ubTIYrex8+R72/l+
                            0M9vK+xtr7/nrzpNNZPEGsfafn+wbtsP8e1n313tzo7Wd+7T7YU8rzYkRd/zN/An/oNc/fw21m2s
                            eROz/bJ13O673ZtifJQM8y8bW0EPmzvB5yXU7bYf4Plf599c1pVhc6rq3mzztNNEuyJ5f4Vb7if8
                            ArsPFVmv9qS2Kss0USrKr7f4m++iVu/Cj4dah4t8TWirEsL/AHFf59ir/HQKUS38Ivg5c+IfEEVt
                            BBsdm/fv99FWv0K+GPwxsfBNhbxQQL5qqu75aq/C/wCFFn4B0uLbEvm7V3Ptr1KzhV/m/vV0xicF
                            Sp/KXrBPm8xv/HKyfEmuKjbFbZWg94ttvVq4XxJc77x/m+Tb9yuo5o+9Iz9b1VponZv7teaeJ9YV
                            LOVmbY6/JUvj/wAbW2iWb7pdnmr8v+zXzR42+MDXLSxebsRov9ylzHZGI74i+M9ktx8/3WrxLVfF
                            TPeMysqfP9+qnifxVLq0r7W/1rfdf+KuKv5JXl2q2+Va5viNuY6iHxI010jK7fd2f7G7+/W0+sNt
                            3Lt+X7z/AMDV5fvltpU27dzL9/dVhNVldU81tifc+9WmpmdHfzfb5dzNs27tqVzV5efZrh2Vv4vu
                            f3aLnWPOX5WZNv8Afrl7nWGhunVm3/wfe+7QPmNu/wBYZ/4qwbnVWhiTc3ybqJrnfLFB82/b81Ym
                            qzff3f3vlSrMahM+pecssjM1RR6w0LL97/gNY/2pvn27vmqHc1VynN7aJqzalL5+5W2f3dlPv7xr
                            lUV/4ayoXZ5fm+ertxt2pKv8X8FEoijU5jMoRd7UrNSI+2tjhF+b+KmUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFOR9tJtqdH3qy7aAIN1JTvLptABRRRQAUUUUAOkpV+7TKdHVgFP2tt2/epn96lb+KgA3feo3f
                            LR/vf99UyoAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
                            KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoo
                            ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiii
                            gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKA
                            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigBWrovCbyvrdsyr951SucrsP
                            hvYtqXjbSoFTfunVdqVFT4Tan8R+qv7PelNbeEtHiZV2Mv8Av19APpu+zt/3e+KL97v/AL23+5Xk
                            /wALtN/srSdPtm++sXlLs+T7v/7Feqvrd9Nb2iqq3NlZxb5fm2fx1xxPVka1nfs9m/nxRwyy/vYv
                            Obyk27P7n96uMTWIte1Syu5ZfOtN0tqkPkeUktx/8VWreebqtvaLZ3UdhLF87TXC7/N/3Kx7a8Z/
                            EdxeWdrbfZNSnuIonmbakUqps+VP+APVyCMTndVuZ7zZBa6nd38sSs6pcQeV83/s/wDv1y/iSG20
                            TS7v7dL51vt+XeyebEu/7n+9v/j/ANuuz1u5ttHuk1BZI5vssVwt1LcLveeVk/dIn91fv15ZqttF
                            oN4kqy/b4pf3TWL/AL2LbL87oif3f9uszpicfqtteeG9F1Dz1kf7KsV6mzynTaz7Ps7o38Kebu37
                            /wC/XKfYJ4Zf7Tvmkhls4GlVNzukrN8iROmz5V2Pu+Td99K6jVfDEX2rW51gnmuJVX7HN5++KD97
                            /Gm/btTZ9ysfXrn7TFb6gsqv5sUSfufkeXbK7/On93Z5qrs/v/P9ysjblOcTw8s3hK7voNsNxZtc
                            IsKfwsyb9if7WxNqo77V3/frHsPCuq3PhnW7lfLhSLb87wO/2WWX5Iotn3duz7zP8rf8DrrtFSea
                            3fT1VfK83f5X37dkV0+SX/gD7dn+xXRaV4VVLe4+0xQTebdNt2M6efEvybHT/YRE2/JQM8K1X99q
                            UWlW19BZ28UTfJNA7xLt370d/u/P/C9c1cpEkz7rm2T7u17eV3835Pn2Js/g/i+f+Oul+MGqwQ3F
                            xE0rWaSyskqIiI+6J9iI/wDeXZsry+/1Vvstl5S/ZkiZnabb8/zffdP7qps+7UC5ju00V5tLlvln
                            k+wyy/Z9irvdpVTf8/8AdXZ8u/726uZ1VG0VZZ2iZ5VZHZ0lSWWL+PY/z/N8n8P92ok8T3kMWoW1
                            mzJaM3lRTb3dP4Ed0/h/4GlYV/pXk2tozeeksu750l+SX5/k+f8Ai/joNoyOo0TbealZS3MskL7l
                            uIt7J5XlM/z7Eb/Y+artzo8D3Uv2xrSZ2lZ1huG/1q/3/m/2K5VPD628kLXNy03mRPuRGZniVU+R
                            Pm+VaS/sFdUZp5UuInb5Jld3bbsRHT+9sqPhNvdmNuPhx4f1i6fy/MsJdvypaMjo7/7rfdrHv/gj
                            qSKr2N7Y3O/cuxm8p/8A4mulubBrC1tGgudn3n+T5/mX76f9909NYWaVFWVkRVV2eZn3s3+wn8FX
                            7epE5pYSlMf8KdL1rwDf3S31nNDby7droyyp/wCO17ro/jmBG8qeX52VV85PkdV/3K8cs/ELWauv
                            n/7uxvnamP4kaaVGZVeWJ/lfb8//AH3XNUqSkbU6EYH1H4e8QxX0SRXNy32iKeJ7bY33mZ/kd/8A
                            x+vbZntrZfmnjRf76Lu3MyfcX/Py18ReAPiX/wATzT9Pb5LuWdbdd/3NzPsR1/2vv19l6lbM8u2J
                            tnlK1vEn3P8AfqIhUibE15LbfbdrL/zyi+0TokW3f86eb/z1+T5a5G5mi1LUnvFs2huFlWJprhZX
                            Rf8Af2/e3/J/45V5I7mGw0yKVY5pUiiRvOb5N2z/AOwpkOsT2F/FA0qwvF8kVpt3ov8A11eumJyB
                            qvhKXVbC3trnVV/etLdSzWL+bK21PnR02bVX5ErzfxbYf29oyS6hrltpqXTSosNxYuks/wAnz/ul
                            rqL/AMQ3Om/aFa5k+0Syttf+NlZ9iPs/29j7f9/+CqTwzw2dxLFYzzXsUVv5D3EqOm1n/ey/+P1s
                            RqeCaJ4SvtK+Lli1nbR39vpt5E880MT/AGdVZ0it5fv/AMbv8u+vtXQfDzXl/LBbLOkOpbbKCZ4t
                            7qy73fzf++6+d7C4lsPjtp+mLuhi1KD7RqOnwxInm/ZYnuET/dSVEb/gFfVfgPVdQhit5Vn36nFa
                            qm+Vf4tm/f8A+P1EY+8VUl7piaD4JnfwDoWlXO2FLCX7LvsW+T91cPvT/d3pure8T6VbX6xO1z5P
                            /PBPN37mX7nz/wAXyVq+DEnttBuNP1WKPfdXl1cS7Pk+aV9+/wD4HveorzTYL+38xpYPslu2xYVX
                            /Vf7j108vunHze8fL/7Ql54jh8JXttqsE+t+PtW1qzuFSGJ0igigfej/AOyvyf3663UrzU30u3vl
                            gtk82VUun2uiN/fr0jxyuuTW8Wn3Nyt/ZffZ5lRpW/ufPXn+tzLoOh/Y9qvqsqyyxI7fI1Y8vKdM
                            Zc0Tyf4i6xc/Jtg8l4p1iV/7y/feuM1W2imt3RvuNLu/22+Sug8eeJ9R+y2SzxedcRKyM+35PNpv
                            hjwrqHi28t4m/fPLtdkVfut/HQbROZ8K/DSfxb4muLz95s+RIlr7j+CfwWsfB9gl40S/a2+f/dqv
                            8H/gzbeHokvLlf8ASG+f7te121sqful+Sto0zgrV+b3SGb5121Mly1nFtb5Kd5KpL/sVw/j/AMZx
                            aPNFBu2PXSc3xF7xJ4q+xt975G+SvN/HPjxbCzedW+dfkrB8Z+Kvtlm67vn++teS694tXUrWWJmW
                            jmNo0zyn4x/Ei5vGlbc33t+z+Cvn+58VPqErxN9xm+Z67P4x6l5MvlL87y7k3/3fnryryV3fL8+2
                            stTaUjdub/7k6r8/8Kfwf79Z6XLQ7Gb7i/3/AL7UOjTRIzN9z+CrH/Luisv73+Kgj4jHubxnZ1/y
                            tRfb/Mi27v8Ab/36qa3c/Zm+X7n+xVW22/ZX/g/jWjUgn1XUmtrV2Vt7s1crc3klzK7N9xvnp+qX
                            0ty3zfI392slWatYxOapU5TQS5k3bmbe33Kq3MzTN833aY0zfw02FVZvmq4xMZVOb3RP9+mfxU+b
                            5W+WoqsxHp8nzU5pW2qtM8yiSgA+9R92m0UEBRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA9XZOlIj7abRQAU
                            UUUAFFFFABRRRQAUUUUAS+ZTPMptFAC7qGpKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi
                            iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK
                            KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo
                            AKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA
                            ooooAev3Gr2P9mHTYtS+LWmblZ1Rd/y/3q8b/vV9QfsVeH/tnjJ77/eRXqKnwm9H4z9A7PUlhnt4
                            LZW+0eV5X3vu/fr2jwxZy2emy6U0Uk1xLF5rO7fO23+Cvmf+2JdB1KVtrTbW3q/97/O+vVfB/wAS
                            J3v31DULlYbezgV2/wBlWrgjI9eUfdOu1KaL7ZcfZrGR7tl8qW0RtiRf3331wlyjX+qafpmlT/8A
                            EvsGila7uG/dM2/7j/7SP/HW3oKXOvWet6nfeZMl4y/Y0Rv4fNT969M8T+J4Hj1P7DKthaSxM+9I
                            v9a2zf8Af/8AQaog5x7aCHWdQVb7yfK3OyOu75v+eT/3fv8A365WHTb7TbC3bVbbfrsrfZWR2/1T
                            b/k2fw/6p03V0FxpU82m3di1zHYf2ouxrSaXe/2dURH+7WZr2peTf3Fs3z6bFarcWbwyu8rL/qt6
                            fxbqDp1OHv7P+zb+9e2inh1a3vFe1t/N82KW12Ijo6f3t6O3/A6r6lo9nNa2n9nyxPZX949reWLy
                            uv2C38reib/729Jf/Qa7h7aeHw+9zfW0F5ey30tlsmi+e6t2RPs7o/8AD9+reiQrpq3Fiy3cLrLb
                            2t5DNs32csX+qf8A4B5u7/vigOY5m28KqlvFbP8A8S3cvms//PDb86fJ/uVwvjnxPLo95ug8iZIp
                            W3u6vEkCsn7p3/3K94TQVfypfPaa3iumllf+8zI6f98/Pu/77rzTxD4eXxD4gSBvkiiiaWWZ2/1v
                            yfcRG/irKRcZcx8y3/gO78SSalqFz9pv9WliV7b7RKkSWs+/e29P4ldXXb/d2NWInw31PUtR+a5W
                            ZLXck+xnRNyu6O6fJ93f97ZX1Rr3hiLw9ZuyxLMl4q28uxtibmT/AFvzf33T5tn+21cPquqxJFd3
                            LLJYSyv+6t/IR/3TO+//AMfd2/ylQXGJ4ppfw6vJrW0iSxVIll81ZkbzUiZUfe6IvzNv+Sqj+G75
                            5XZraSFItu776bl+d96fw/fT/wAfr1C21iLSre7+x+e8SxfLdwr8itv2/In95PutWLf+IWm/s++s
                            90zK3/Lwzum2JEZHeL7u59rr/s7KC+UzLPwe02myru864bbKtpCu+VW2b33v/d/h/wCAVn694Dls
                            4rS2eeR7L5ZVmeB3lV5fnfZt/wBv5NldBpuq32m2t7PFB9gRrXzVhhn3ebcKifvflf7u9HZk/wBu
                            mW3iHZdSz218thd7Gl/tDc/krcfO6I6f3qiUjoPMrzw3qc2my3LW0/2dlXyPs+z97cKiI/8Atbt/
                            3krmtSs5bNU2q3mytvZ/4F2vsdK9NTd4nsLhl+yTXqzte3TTT+VKsTOm94k+T+//AAfN9+mahprX
                            kVpbNtv9Tba9rceajpKrSumx0/2EX+P/AGKyLPPbaZnaXbEqIvys+37vyJ/8XTkdv733fn+T+Kt6
                            /wDCttYW93c219I8TNtiht4H+Zm2I6O/9753/wC+K5p9PvEuvLtrGazeJdkvnbkRm3om/c3y/fZP
                            ++6DQv6Jqv2DxboV2y/Na30T79v3drpX6JpeRXlnbtOrI8q70R/vtX5mXOpKiO+1Xfyvl/2m+f50
                            /wBx6/RDwZ4hg1vwDomrwL51xdWsUqw/wf7j1n8BjI0LzVVtpZZWgkv0+XyEf7jM39z+9/8AYVYd
                            2aKb/To3uLiCJJ3eVEeVv7m+ufSa5vIrjU5286JWbykmV3iXc/yfJ/CyfPW9Z6bbWa3dtBbNMkvy
                            Mky/euP4H3/3a2gc0ge2W8i1CWW22S+Ur+Sku/8Ag+Te/wDwCuR8ZzXlzLd7m2Is9varaWMW/wAp
                            V+/vf/fT5v8Acrrrl2TSbuKVZby3l+dfs67EZtn3N/8AD9xP4688ttNlezt4Hs57PzZ1eXZP91m+
                            +mz+Jv8A9uug59Slongy5f47eF9VaW5hvl066urq0uG/eqrW8qJK7/3X37a+stE0dtN0my+x7oXt
                            YFiXzl+dl2bPn/74ryX4dfD3VYfHXjDxVrk+palFFpNnb2b3cqNcS7vuW6Iv8P3F/wCB19C3kMqb
                            Gb9ztV0be33qcYmdSpzGVsvvKSxuVZJbPyvndk/fr/v1ieJ79tNW3kZo0svtkT3Wxvk2/vU+5/3z
                            UqTW2paNb6nctPDufYrp8iNt+SvP/HPiS28MaXpkrXnnWkurW9qt3M3ybmR9m/8A2d71qYxj7xre
                            J5oLzWYvIvN6SxfN53yJEv8AfrzzxhJH9ntGnljR4l2NM8v+t/uV0fjhEs9Zu421WDUmi/0dprGd
                            JYpfNT56+f8AxPNLqrSwK2//AEr7Qvzfd2P8iJ/s1lKR2U4nM6qmr+ItcuLaJVmla62QQw79n9z/
                            AC9fcHwW+EsfhXSbe5vIt96yruriP2dfgaulW7+IdVXfe3Tb1R1+4rfwbK+mra22bFZa2p0zHE1v
                            sxG7PJRNv8NJDuT/AG9tPudsKfI1M85Ybfc393fXUecV9V1hdPtZZWb51Wvk34r+M1udelb7T8i/
                            OvzV6F8bvivZ6JZywQTq8v8AsV8T+M/GFzf3E1yrNv3Nsf8Ag21yykddOP2juPGfxaVFlVZ12N/H
                            Xi//AAs6W51J90v3fvbK5LW9YluW2szfe3/erHsId91/Ejt97Z/dq9TUf451iXVdSRlb+989ZltY
                            M6/N8/z/AHv71btzo7PKn99t38P92pv7Fb+7sdm+V/71PUy5TEtt0ksv/PJKsXMywxblZdn+3XR3
                            OiRW1ukTbX3f32rj9bmiTf8AdT/gVBRy+q/6TdJBFt+Zt/3qdfpst3iVt/y/99LVJ79Y793ZV30y
                            /wBSV1Ta2x9vzVZkZGovv+df4v4P7tUoV6sf4adcTeZ/DTk/cr/t7q2+yebL3pDXVUplIzf99Uit
                            VESE8ukb7xoakoICiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKK
                            KKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooo
                            oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiig
                            AooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAC
                            iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKK
                            KKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooo
                            oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAHr8tfd/7B+jqvh+6vmVU3
                            M21933fnr4T/ALtfof8Asr2EXh74QuzMs1wsu9mT5H+/v/8AsaxqHfho+8eweKrbydeT5fJi/h2N
                            8n+fkSuj8DXn2m4WBvLdJV2bEb+HZXI3N41/LFKvzxK2xXf+Ld/+3V7QbZprzT9q7H3ffT+GvNj8
                            R7H2T1C2uZbNtPtm8p7dvnbY3+t3Ps2fP/v/APjlVNbmtvFt/cRWzedEs67U3bEiiVN/m/7Wx65f
                            XnXSm1jz2aH/AFVvA7y/xff+SsK58eW2m28tyy+dFE32dk+47N/n5q6DHlNi5m+zLLp9zq9s+lS+
                            bZWro3lbWZPn+f73+1We/jDSNN1LRLPXNQazTVry3T7dNE77fKt337E/4B/B/frzTUPHkuqq9jLp
                            620upad5trM6/JFF8/lS7P7zo77v+AVL4z8MeLPjNb+EoNN8UWmiaFpsFrq8FpfQbHgbYm90f7zM
                            +xPk/hqAkey61oupacyafNpsVpcN5ssVjbS/62z2oy/8Db5WrpvCWiRaJZveXk8c17dQLut7f53X
                            53l+d/8AY3pVjw9r3/CQ6buVm+0Sy/Z2l/1u2Vf87mq74Y0TUEv7iW5aNN23yoYV+SJl3+a+/wD2
                            9/8AwGrI5ir4oSW2+yQWMVpDpSr812s++Vm+/wCUn/oLf79ZL2cDtb21z/oEsU7XCzeRseL++m/+
                            Ktb4gTLcxRWqqsMP/Hu1v/BKrfI7/wDfD1z95bXn9qJ9pljhiliaWzd/4mVH3o//AACguJyPjOzg
                            0e1tbbUP317LAyWfnRb9rbK+evEniKLSvl/eQy3n2jdsb513S/vXd2+7/Av+zvRU+5vr0j4keLd3
                            h+Xc8iSxWrRWdw+903eV+6+f+9/fr5s+IWvb5reTaryxKrs+77zNsd0/3U+f/vtKy5eYuMjH1XxD
                            eWcqQNP9guIpWtZdjbHaL/bf/Y+7v2fNWL/wlX9jxbZ5GR12ypsZH3Kr/fd2+b50d12Vxuva5cTS
                            7rna/wA215k++23d/wCPf3q4+bUpZptzSM/3d3+1tq40uYJVeQ9v8MfELT7PVLeJolv4YILiWKJ2
                            d3aVk2Im9n+787Ns/vJVjxVYa9pulpLqMscNpqlrLcM/8beU+xH2f3nbaq/7NeCw6kRE67WDqqhX
                            X+H5t26voDxl4hk17w5pV5bL5Ly6YtveK+/ypXZNm9P9x9jKqfxfeoqU+UinieeXunI/aP7JvbWe
                            W5V4rizidZrd9/lNsT5NuzcrJ861p6bqscOyOxktPKil82B3Z08pmf53l/i27k+5Xnd5E1uyRJ5n
                            msq7VX5dq/eT5v4vlZauJrdzDFKs6q9wsSos0Pyfx7/n2/erLlO/2p9AaPNBC3n3kqzeVdROqTbJ
                            dzOj7NnyJuX5E+/WP4gsdN1q1leTXLSzu7r55Uld9i7X+RH/AIdz/Lt2fd2V5unjm+e4Sf7SsMv7
                            rbvXfFuXZsfb/D8m+nTeIPOv7h2lZ93zy/ukT+D7iL/D833XqJR5i+YzfEOjy6JH5FzKsyK3yzIu
                            9G/4Fsr69+Ani2DUPgjpkTXKpd2Cy2vzrv2/3P8A4mvkJ9V8mJNzb4W3O3zfI3/2Vel/s9+Mk01v
                            EWlNO0NvKiXsSff+6+1//HfmpSj7pUpe8fVum3m24Tz5Ve3Xdut1VPNl2v8AI9Z9zrEF5DFLqst3
                            ZusWyJ7GX97L/vp935N/yp/eSuc03W1ufNSDcjbdkSIqb/8AY/742fNVvTb+e52Na+RCm5dzv9/7
                            jvs2f98NvrmjImUTuPD1/wD2kr2ay2jwxQK8qJFs837/APH93cmyKtvwWnnatbtc2OyXcrxS3ETo
                            7bfubP8AgdeeJfxXVwkXkRpLu8qWGH5NzMjuiJ/tfc+//cru/CWpbNe0xW8+83yxRRPd/O7M2z/x
                            5K7InNKJ778NPEkviq6vWnVX0y1lWKzSFdjq0T7H/wDH33f8ArqPGDt9luFglWGVVZ4pn+4v+xXM
                            /DS2udN01JbmD7BcSys8qbf9UzP9x6f451W20fSZdQaVfKiZvNhf7krfc2JXVH4TzftGZrGsRJYa
                            ZpjQbLtrWJ96L+6g+Te7/wDfdYng/wDsHR/C/irxBfW0d5p+jeev71N/2q8lTZEmz+Jtkr/99pXQ
                            3U1zDptuzW2+KKBZZbfd88XyJvR6828Ya1faP4m8OWl5azTeDbyf7bdRW6fPZ3WzZvf+98qrSkXG
                            PN7p4b4Y1KK/+HeiWcVytnrGjSsl5aQ/fWVf4P8Age+vWPg58ENQ1W8i1XWoPJt9zPFbuv3V/grb
                            8AfCXT7n42eONc0yNZvClw1u8Hy/JLcInzun+f4K+hbbbtiiWLYlYxj/ADGtav8AZiS2dstnbosS
                            7EX5Pkqw9z5Pzfc2Ub/3PtWbq15FDbvufZXecPxj7m/WZdzNsryT4o/E5tEsHgtpf3rbk3p/DVjx
                            t4waziligdv++q+fPGGq/b5X89vvNv8A9isZSOmnTPMvGet32vXksrSt8zN99vn+/XH63bbLCVpV
                            bZtr0C/ton3y7fvbn/3a808eaksNnLEu7ftqI/3jpkeWXlyqN5Tfw791W9BTfdbtv8X92uceOW5u
                            Nvzb2+f7td94S0pkvEVotiK1aGZtW2ms0sXy7/vba1o9EWzi8+dV3/8AoP8At1oXNmumxKzL91t/
                            +9XGeOfHMUMXkQSsj/wpurIg5/xn4kgh3RK3/A6801vWPOhf5t+35Pkqr4kv57y6+V2fd/tVzl5u
                            RtrffrSMTnlLkGyXLM25WqF3Z/vU1m/u0Yrs5TzZTlIP96hm+7SeZTaCAooooAKKKKACiiigAooo
                            oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiig
                            AooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAC
                            iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKK
                            KKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooo
                            oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiig
                            AooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAC
                            iiigAooooAKKKKACiiigAooooAKKKKAJa/QD9lfUopvBaae21EbbLsRt7tuTe/8A4/X5+V9d/sr6
                            21ta7l3fvVVF+b51ZU2fJ/6FWNY78N8R9Z6VZ/aYrhm+R1+dUf8AhWpdKuYkv5p1l2PEyoqf3v8A
                            bp+g2cF4rtBPs82D5kdfn2/7lYnnQW1xcRMrebt3rs/2X+TYleaeyavxL1K+a3eK2vFmdtyQIjI7
                            2q/d3/8AAH2f997a4/UtEbWPs8W1Uit1uEndG3o27/Wo/wDtfw1Nquqy2bJLbNGlw239y8X3maVH
                            f/gKbNzf3q6LQfCS2du9jEyo95LLudF2JEzv8/8AwKrM/hOP03w9LrFw8tzFbQuzbJXh+R4ov+WX
                            /fexFZK9LTQfsGm6P9mu2S381fsqIyI7L/uN8y/O7/8AAUqaw0pX1S7/ANGkheLdtfb95tn3/wDd
                            2VattNtrO681op5rhZYnitPK+Tcr7Hld/vbdn3f9yqGdL4Mhg0q8dba5abzWluG3/wB37n3P73yV
                            6Al/Z21us6zt5TL5rOkXzr/wD/frhXeKwlSWCJb+K8l/df8APVd3+wv+5Utsk+satcW0/wC5i/hR
                            W2O2379aRMJR5iLW7/SLzw5FPq+lNDLeRL9y82bm835E/wBlvn+b/frkfHnjNtB8qKCCN7hll8pP
                            N/fStF9xH/4Bv+ff/BXUePEgm0OKxtbZftEu5Nnlfum3fwV89eKtSlubi4b7ZIiRbUidInZ1+5v3
                            psRtux03Pv8AlokETzT4qeOZNSa3sVljdLVm8/7Ouzdu3uif7qK6fPXzl4t1j7ZfvK0u/ci/cb+F
                            a9D8YXkryy7mb96ybnT5EVf9j+8vz/8Aj+3+CvF9UbZK6rFsbbsVEXYn+/SKMS/m+b5W3qrMtZpZ
                            m+b+796pZPmXdTHRXX5fv11QPOryIN3zLur3zwxfwa9onh/TGaNIop4kZk+d0+4+/wD2F+6zf7le
                            AbvvV7B8HdSxfw2bMr28s6+b93Yv+9/Eqf3n/u/LRUjzBhpe8dEnhiK2sLHV9XjkT7ZF+4SWLZ5q
                            qm9Jdn+2/wB1P4ldGrjfEUK2JVbmOFXRf9VF8iKzfMybv+BV7V8VNUW60mJ2SVLe3nSyN2if6PKy
                            pu2xP91GRfK+XezKqbv7lfNviDVWubyX95v+Zv3397c+/dXHy80j2PacsSea82XHmsyp8vypTVvF
                            uX2+bJv+bdWEk2/arNs+ahZPJlbb/DWnsjm+sm6t0zxIu759uxt1TeDfEz+H/FVpeM7JDu8qX/rk
                            y7X/APHa56a8d/8Ae+7VW4m3vurWNMxqYk+r7DxIyfZ2aVt6y7Ik2/xbPn+eu+0rxVE8f+t8l2/j
                            XZvX5ET7/wDCuxPu18r+GfFrTWtpArfPEuxt/wDFXoGleMP9H2qypFuXaiLv+Zfv15dWnyS5T1aV
                            X2sT6Atte866i8ho7x5Vidt/34tru+93/hfYj/8AfdepeD9eWzlhn3QTS2u64ie3Z/lZfnR/mr5a
                            8Ja9PqtxdwTxLeRM32iVNzxbm2Om99n8Sb0/8f8Akr6N+GOmtMzRLYxw3csTRL50vyK2zYmz/vj/
                            AGaXMXLlPrbwlqXnLFeNcyTPeQK8v2j+Jm+d3rh/HT/8JJLaSrBbQxLdNK1vcfvduz7mxP8AerqL
                            DR/t/hm0ignkhZVifyX+TymrxTW/G32BrudvLhSwb7PP82x55fuO8X/A0da7OY4Ix949F1vUr57x
                            J/tOy3igZ5YYf+WrVzXgZ7zxb4glgggaa03MksztsdVR/wC5/t1xVt4kl1jXHn0pZ31CWVf3N3u2
                            Lti2fIlfSXw68N/8I34cSW5iVNQuNks+xfk3UR94up7kTo7OwisLWK2gVYUVdmxFq3CipUL/AHdz
                            ffqK51VbCweefbsVa2PN+MZrGpQaVE7M2yvCvFvxIlvNSlitpd6Rfe2VlfFH4iz6xdXEFtL+6ryG
                            bWvsyyytL87f99vUSkdkafKdhr3iZpldWlZ327P++q8/1W585ZWZm2ffrHvPFDXjbfuPVt0iewdm
                            XZ8u9v8AerM3MK/1KJIvKXbsevJ/G141/KkSr95W/wBv5a2vEmvfZr94ty/e+/8A3VrFvEa/ZGX+
                            KgNTl9B0fzriVlVk/wB/+GvTfD2mxW1wm77m1Wb/AHqz9B0eKFfurvX56l17XotEt3+ZUb7n/wBn
                            VmRX+IviTyVeJZdjtFXhWq3jXmpJK0u/+D7z1q+LfFrX9wm5m+X5Vrmkm+0t827Z/u1oTKRYS2j+
                            dmi/20+X7tcvr237Y+2uluZpYYvNVWTd8i1yt9D5LvE3zutbQOOv8Jn0U7y6bWx5oUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA6vbv2dvEj6V4kSCVpUiVl2P/AjN/wDF
                            14js+bbXTeDNYi0W/llaVofl/df71RU96JtSlyyP0y8E3jMlurMzp/qmdG+dl/2KNetvJvLiVfkS
                            WBkXY3z7l+4if79eVfATxz/wkNhaL5rea3yTzff+6n39n8Pz/LXsvifSvtnh/wA+1/1vleaqf7S1
                            5sonvRkef3PiSC6vLee+VfKi2xMjpv8AN+f7if7+x2b/AHNtesaLYPc6XLt3JaK333ld3Vt/397V
                            41ps0Vh5rP8AvliiaVX27/4PnRE/vI+//vuvXbaZbC1t4LmXzrdV3yv/AHm/3KIlyOzs9usX/m31
                            4thZNA1xPfP/AKqBFT97K/8AtVFf6rZ3/wDZt5pkGyLaqKk29Nyt9zf/ALOysm501fFWm2lnPFvS
                            KfzZUt32JL/sOn93566N9Eg+wJFP88Stsaab/VNt/uVtEwJbZJbZv3sHkyqrJFMnyI3+3/t7K1ra
                            833CK3+qV12oi7Jfmf8Ay1ZltpVy0VpL9rg2RfO000v3f9xKtvMum2qSzyrsZt8U333b7/8A47SJ
                            l7xy/wAV/G1rZ6W/2bzby0i3XDb22RS7n/jf+7/sfxLvr5c8SeMJb+WW5nnuX83c7XELfOy/O7o/
                            +y77F2V7R8Rbazm3xMzI8Sr5UM2yLc2x3d9n+xs/jrwrxDokttayy7mS3ibypdi/6pmf50f+Hcn/
                            ALJTlIuJ454zeVLV4J1WGWKL7vzptXZ8iJ/s/P8Ac/2K8l1iaR5GVn3qq/8AAGbf95f9n5v/AB2v
                            WPHzMYWvW8uGV52l+efd/fRHVV+98mz5f9uvL7rSpETa3ztFF/tJ8v8Aut/tbl/4DTjykVDkpf8A
                            2b7tMXcn/oNat5pscMrfN8u776L8m2sx1ZN33v8AgVdETgqRkV5Pmet7wnrkuj3j+VL5PmrsZqwp
                            m3bflpiNsatPsnNGXLI9o1rWNQ8SaPb6HDdXNxD573sWno22LzWiRWl2f3vKRP8AgKba861jR7mH
                            fcyIvkys211+43zfwV678B9Bs/FuuW+n3PmJbtA0t5fK3zxWqp+9/wCBPvRVrV1vww3xI1m7n0rS
                            ms/Dth9n01G/gaXyvkX/AHtifN/d/wCB1yylyHsRj7aJ88/Z2T+Fv9nfT0TfvZvv/wDoVekeM9J0
                            rw/K0FtumuG3Mz7k+X/c2157c7ppX2/Ou6rjLmMZUeQrTfP823+GqT/eStC43Iu11bf/AA1Sf5Gr
                            SBx1iWzvJbGXctd74Z1JtUltfNl8lImb53+4m6vO/JrV0rVJdNb5D97/AMdpVKfMXhq3JLlPf9B1
                            WCzv/sy+Y/lbXZ9yIjL8nyf+PutfSfwc1WfWNWtPIaOF5Ym8r7R9zd8mze//AAOvifwlqv2nVEZm
                            +RmTd53z7vn/APs6+jfhj48gsNWsomnV13Kjf7XybPk2/wAPz15soyge9GXPE+29V1a50fTbi5tr
                            xn1Dytn2hG82JW/56pXzb8VPHNnqtraXjW2y0if7UrvFsdm3/O6J/wB916w/iBbXwLaS3Kr9nliX
                            7jbPN/2ESvnHxDZ6h4us7LT9M3TXDSqv2RF+eLb/AMsnf/YrGUgjE+kP2fvDFtrfia71ffPNbxS7
                            Ikf+H/gf/fFfVbzLN+62/Iv3a8f+Evhu68E+BdKsZ1/03yFed9v3mr0WGbydis3z130/diebXlzS
                            NB9yN97YleWfFrxg0NnLbQNs3LsavRtV1L7HYSzt9xVr5U+IvjT7ZdXDK/yKzUSIpR5jhNY1jyfN
                            ZtqV5br3jDZcPFuXY7U7xn4tb51Vmf8A9lrx+/16W8vHlf8A56/x1mdkj1Oz1J5mRWb5/wD2auov
                            NVaHSflb5/8A0KvP/DF4tzAm5v8Ab/2627y8b7P8zK6N96gep5zr00r6i7M3yb2+5W34VRXVGlXf
                            t+7v/gqlc2f2+6dV/hb/AL6rrdE0eLTYkZtrvTiKRoXlzBo9n5q7U214J8RfFTTXEqK29P7ldn8U
                            fFS21vLFB8+3dur591LUpb+4Zmb71bRjzHHUqRgPuL95pVZvk2/d+WtfTbn/AEWJW2u7P/wOuV/i
                            qxHcsjfK2zdW0qZzRr/zHZXNyvlP8yvtX5q5KZmm+Vvndm+9TptSlddrM3+1TUVn3yM2zb/eWiMQ
                            qVIyKLrsam1K/wB5tv3airY4AooooAXdRup3l0bKC+UZRT2WkkoIG0UUUAFFFFABRTqPMoAbRRRQ
                            AUUUUAFFFFAD9vy0ynU2gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
                            KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoo
                            ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiii
                            gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKA
                            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
                            KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoo
                            ooAKKKKACiiigAooooAKKKKACnU2nI+2gD2P4L/EpfCurxfaZZIURdj7P4l37/u194fDrxDB4gsX
                            iglW8tJYvtUCff8Al/uV+WtneS2d0k8TbJV/ir63/Zp+ISvLLAs7fa7X/TYoUb59rf61P/Zq4a9M
                            9XDVOb3ZHuF/oM9y0qqyvNbzrdLCi7XaJvldN/8Aub/v16XZ6PaNFFc+Rv3KsrOi79jbPkrM8mxv
                            7jT7zz/3UrbGRPuNuT+5/v13fhnw80PheKVovORZZYon3bPlZ/kd6wjE75SMrzms1inuftcMUS/v
                            7hNiPLEv30/vN/3xXZaJc22q2trZp8iKrOiW8u//AIB833a89R5bPUvm2wxW63ETbGdU2/8AAv4v
                            uVu6C95YX9uy3jfZLpt8Xnfxf/E/craIpfCbuq2F9CyQTwLNb7t8qTLveL/vn7q/J/4/WbYabFZq
                            7W1j8kSs/wA8vm7Yv76f98f8BruvFVi1/Z+fZxLM+1ZVRF+SVfufc/3/AP0Cs+2t/Js3XzbR027I
                            pkbfu2/xvt+X+/RKJlGR5V4n8NwJcPEqwTS+Rsl8n/SNzOj703t/uJurzLxh4eg+xywNK02nxTtc
                            X0Ls/wBki3fxu+z97vZ0VkT/AG6+gPEGmxaVKkl9PJNKu6Xft8p7NW++7/3VdK8f8Z2ED2EVtY2c
                            80VxdfaF87YkX2Vfnff86+az70/77qJRNoy5jwfxJ8PbbVbq3XbbQpFK0S29vFs8q42I6I7t8zf3
                            lf5flrzfXPhf9murif8AtmJHl2ptZdyMzRJvR938aPv3f7W+vSvFV/qcNxb2cCtYIytcSo8To8DQ
                            IiPsf+L5ERd/+xXmvjLWPEG19TlWGZotsX2vcipu2P8A3f4tv8afxb99RzBynlmuaLdW+9tu+0Xd
                            tmTan3flfb/s1zjpF/eZHX7v8VdjqmvN5cUVzFJE+1tyN/Erfx7lrmmsY7tm8qVd7f8Aj3z10xOa
                            pEzLiHau5XV/l+as/a27pWlNG1nMyN/DVJ2+ZdtbxOCtE9g+A9tqGuaymh6VtTU9WnisoHeXZ5S/
                            O0r/AO4ifM1e8fE5F+GXgu38PaVeRfZ9Hia1l1B1+SW4f57jZt+833P3r/N/Clc1+w/4RtryXxB4
                            ou4pprfS9qyywr/qov42/wCBb1Wvbb/4Az/FDx9NuaB9KgZpbNHZvKZd+/ei/wASojpu3/el/wBh
                            a5qh6uGl7p8haL8Mdc8bXT3KxNtlXzVll+TzU/jf5flVau6l8OrHTvO8+5bfEvyusT7Pv/Iibvu/
                            L/vV9kfEXw3Z6bpdxofhOW2h02wVbfU9cu/+PeKXej7E/vMifN/dWvlLxnf6DcXVx5EWqeLb5d3+
                            kTM8UTN91/kX7uyuaUpHZy83vHk+q6JbWbYXckqrs27lfzW/9lrFs9EudY1GKx0y2mvLu4dUghhT
                            fKzf7CrXWa1bXK27S/8ACNfYImi3ttZ/u/36/Sb9jn9mfw54B8B+FNQ1qdbDxx4u0x9US7uIt3kW
                            v/LKKLd919m1mrpjKUYnm1oxkfFXh/8AYl8VahapPr2paf4bllb91aXDbpW+/wD3flX7ldan7Hfh
                            PSov+Jr4o1K8m/v2kCIjN/wL5q+0tUsdTkvvEvhzT7yyvLRbprVZlRPNa4ii3/K3/A64LVfhFrl/
                            /YkUFmqag0Hm3Vw/3FZn/j/77rP2k5HXSoUo/EfLM37M/h5f+QVrmpQ3e779xFE6bf8AcWm237Ov
                            jPR9Wt7nQ5/t8S7n8n7jtt+R0/2/nr7y0T4D6V4es/tNzFPqV2s8UXk/72/5/wDvtK9L0f4dbbfw
                            /Pqvlw2UUsu2xhi2P5W/599HLKQ5VqcPhPF9E+F0vjDw/aaHriroiaSrXU9w7f6i32f3/wC99+uz
                            +CHwZttE0GLxDeLBYS38X2iC0df3sSf7b/3tmyul8W6bB4/8QItjLHZ/D/SdRWXX763bfLf3UTps
                            sv8AcT7rV3Gq6lBc6bLbNBsuIrxtr/3V/uVcacTGVaUo8pju+xXaiGZpl3VFczL8iqtOR2s7V5Wr
                            TU5jjfjr4wi8PeC5VVvnb5N9fFOpeLfOt3Zmbe3zt/ttXuf7VfiJk8OIq/I7NXyFpuqtcxPt2/e2
                            fe3/AHkrCR2RjyxOc8Za3LNI6r8/3nrikvGhutzfcZvmRGrqPE+2G6l+bfXD3LtNcfLu/v8AyVcQ
                            kem+GNY8mLd/d+f738NXdS1trlXVW3/Ns3/3q8/0q/lh+Xdsretpl83bt+7975qJBGXKdLoiMlwm
                            5dm//gddRqt+um2G5m2bf/H/AJKwvDCf2lvVV+f79V/iLc/Y7NIm+9t2L/vbPv0RCoeH+Ptea/1K
                            Xb8nzfMlcV/FWhqVw011K27f838dUWf+H+GuynH3Twa0uaRFStRupKsxF3Vaa8eRfmZqrUu6gfMC
                            t81Nald91NoEFH8VFPVNy0ATo2/ZT9qt96m2yb/96rsKfe/u/wANYyO+MeaJnvDt3Uzy603tv7qV
                            E9v8v8Wf7u2jmCVAo0bWqx5O/wC78lM8l6vmOb2ZBto2VfS2ZF3MrIn+7VWaZd3y0yOXlGf8BplK
                            zs/Wm7qogSiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA
                            KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAo
                            oooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACii
                            igAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKK
                            ACiiigAooooAKKKKACiiigAooooAKKKKACiiigCZP4933q734U+Jv+EX8VW90/8AqV+8/wDsfLv/
                            APHa8/8Au1YhuWtbhJV++rbqmUeaJdOXLLmP03+G+qwXi29im68fyllgfcnzLv3/APjlevWfja21
                            jVNQ8L6fKv2dZfKiRG+f7iV8Sfs8eP1vINCWeRXvdNnVJd7bN1uz7P8Avnfs/wC+K9V+GOt3lt8Q
                            dQZoGmivJ2t2f7m753R9j/3UrzPgkfQcvPHmPoZ3unSWfyGTzWlRkeL5J5V/jRKqXlgyRXE9zczz
                            JLuSeb+Nf7mxP9jZXRvo8CN59zeSJDLF5qwou/b/AHIt/wD6FUV/prWCyqzRver/AKqF/nRpW/8A
                            20rUyiS+Etbs3vEvGgX7RLEtlK/m/Iu132J/4+9dLpVsumtCi+XDbxRMkSOuxEXe/wDH/drze2hl
                            0e40+JpfOlaW4lb91sTyt/8An5a6O28QxarLb2yxfb9srRMky/e/g/8AZ6cQlE2v3GvWsTNdNNFK
                            qxXkMv8AyyXY7p8n913RKyvHj2Oq27tcvZQpFp1rLfPuR3l/exJK/wDsrsR6x/E+ty/Z0uVvIEvZ
                            Z/3sMKsiSrE/z/8AoH/odeZeKfFVp4q+H9v4luZ7bRNH1y6lZpbtkd/sEUWx5Yk/uu7t80u3/vmt
                            A5ftHmnxRezub+7ubNruz82C6srNHtdjrbqmzzdv3tz/AML/AO5/cr508ZzXl40s8Cq8ssvlRTbl
                            R9rI+z91v+9s2fPX0T4osdF1iwkbxLqmrX0qIss/2edYpltYrdYvsq7fmZf4ml/i+evJr/wr4c0e
                            3T7TYz3kvzXDPNBK9xKron3E2bli2Im13T+N65ZHTE8Q12aWze4tF3JEuxW8777bV/vf7392uS3/
                            ADNu+RmbdX0RN4k8OaU0S2fh6Ka6SLzdkKo/lbdux23fL9/+/wD981z+sajLqTXGp6nodpYQ3FtF
                            exeTAmza0rou5f4d6q9bRkZypykeONeTzRLGzb/9+s65T5ty13msXNlc3T7bHYys275f4f8A9n5q
                            5O/hjRvl+T/YraMveOStR90+4f2DfDa+JPAPiCxaX+zbKWeW91HUN33bWJE+T/vrc/8AFt2f7dfZ
                            Vtp8XiTV/sOlRNoj6zFEs93v3/YNGit/kTd/DPcO7N/uV8h/sFtby/DfxRbainnWP9o29u0X8crN
                            taKL/Z3u3zV9A/GPTfH95oN34M8I2l94b02XUfN8U/EKaJ4rRWZN3lWv/LWVETZF8ibfk2bqioFL
                            4eU8K/ac+Lnge68Qf8Iv4TtJvEOn2EH2ex0ax/491uG/1ssu3/W7/wCJq8I1uw8Ya0yR3lraeHLK
                            WBdtvNs3fK3+7/EtfVut/Avw98B7GVdDuY7C0ig+0X3iHUF/0uWXZ/Bu+9/f2f7dYPgH4b6r8RNe
                            bXvCPh6+/wCEPsF+2p4p8SL890qsi/6PE33t/wA+1q55SPVj8J8j6l8PdcutGeWK51DUkigb5IbV
                            0Rvk/wDHl/26/avVdH8GeOfAfhqzvpYPKtbW3SCZG2PEuxF+Svi/x/YaV4AluJbll+2ssrrb+amy
                            JW+/8n3VWuP0f9p+xhZNDuZ1trRlX7LMku/a39x/++KzjW97lkFTDc3vRPqKz+HvhrwB4w1CWxvr
                            uZvPWWKGaXfF83zv8ldRok1z4qurTSmnjS3t5Z3lmf5H2r/B/u18vw/GCVPFUV9fTtNb7dnzf3dm
                            z/2Sug0f4xwabfoyy77doGt9m7a/yv8Af/4HvrpjKJzSpyPsbw34h0//AIR/TPt0GyWXdcbNvzqu
                            /wC+9ZN54f1Wz1nxHK1zH9r1aBUsUmb91pcS/fd0/wB35q+etV+PzJo1x5U8fm2dr+4Tb8jMrps/
                            9ArySb46+KPFvw+1jVbnXFh13xBLLZXk3m/Ituz7HSL+7sT7tbe0iYxw0pHqvxR8fWPgb4efD3wZ
                            oeoLc6f9q/e3at+9v5Wl+S4Z/wDbf52r2a2uZ4bC3+0t516y75X/ALzV8ieG/D2ofEv4l+FILHT2
                            /wCEf0GdfNuPuI0Sp+6T/vvYzV9cTbXvPKXa6L/8XWPNzG0oxgW9N/0lnZlqp4n1L7NB5S/I7Vp3
                            KLYWu77ny1wmsXjahfp8u9FrTU54+8fOv7Ydz9m8Mp838WyvjzRNY8tf9j7lfSf7beteTpsUDS/x
                            b/8Axx6+KvD+tTzXnkfwOy1hy80jol7p3Gtu1zcbm/i+SsT7AztKzV2tnojahaoy/wC/VfVdHito
                            niZfu1cfiMzj3XfLtXd8v3v92tvSlZ2/i+b+/VTTdKa5v9u1tjfOr13uleHvJXc0Tb9v3P8AarTU
                            cTrvh1pvkybm+d1+f/gNeWfG/WPJvXVf4V2L/wB917x4b0qWw0uWdt2xYt/z/wAVfMnxmvFudcuN
                            vz/NsX/ZWs/thX+E8qd/m/2aip0lNrvPngooooAKKKKACiinIm6gBd/tToWG/wCahPmq3DYs2+pk
                            bRjKQ+3X7+1atL8n3fkqWHTZXX5VZH/v1p23hW5uW+Vfk3/crCUj0oxMdPk2MtW97XKp/G/+7XV6
                            b8PXm+8rO/3a7LRPh7FbKjT7U/4BWPMbRieVWujz3mz91s3bv+A1RuZorBnVl/3Ur2vxP/Znh7SZ
                            VZvnZf8AYrwDVLpbu8eVE2K38NbU/eOOv7gy6vnuGqpTqbXSeaO8ym0UUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFAB/FUv3qiooA9B+GPjJvCfi+yuZW32Tf6POr/wxN/8Q3zf8Ar7h8Nw/wBsTy3lsyv9
                            vi82L5tn71n3/wDj9fnF/Fu3V9p/BH4lvH4G0/e3nSxXS28rqib1X+B/+B1x1o/aPYwVX7J94aIi
                            6l4P0q8tpbaw82L97Nt2P9z+D/aqpc+akqbpVhii+Rk+4jf7Cf7XzvWV8FvEkCaDcaZ9p3xWf3fO
                            Xe+1vnRE/vV6FNZ+dvgtmbZLu3Qps3/M+/56j4wl7sjgn8PXMO9ladIov3TOjfOzf7H8Lf79c+8P
                            2OLULm5lb7JF8kqI33m/z81eka3Cum3/AMvlzbYm/fTN5SRLs3/8CryLx/rDJpbvbNbPLL88T3H7
                            qLyl+d0/74R/4KJROmn7x518dPiJeaL4IdluVs9T1JN/+juzXEXmypE/yL/E6fKv92uH134g6f4B
                            uLvRfDOkafc3EU/2JruZ2ndtn7qJEV/l812bYzfdXezVhfFNZNeuNP09dTXTdMuNatbjUdQSNt6/
                            fTzUdvu7N/yon+w38NaWlalpGg2F3qumfuUv/Nt9MSZYvtcsTOiO+z+Fn2u3mv8AdWpibS+E3dK1
                            LWvH/iO4s/D2i2l/LFEsWtahfSpFFFK3yP5r7PlVHRFiiT+5uevH9e0HU7O4lXXNend1lldrHTJW
                            llb/AJZJ+9Z9210i2/P/AHPlr3XR/GGleJLC00/w8yw6PFLv1jXLv/Qodvm7/s9kmz5mdHdmf/x/
                            50rwfxpf3Ot3+p22lbbCyluri9+w2679sTf6r738WzZt3/wvv+9vol8JETk9W1C08N2f2aDbCkU/
                            zbmRnbem/wCZm+Zm/wDHK5y51TU9esLTTbHSm+0M2xbj5vNlX5FRP91GZNtbOmaNBeaxcGyXczbm
                            W71D7sSr952+8rs/zbVT722u81D4e3Og+H7S5gtpbC6vIG3X12237e0Wx0dIl+ZVfzfl/h/dUvdD
                            4zwq5s9VtpXnl2o7M7M7t/E336wbxJfK+avQ/H8MF5qlxPpVtOllK7eVFMm91Vfk+d1rzy5835vl
                            2J/Fsq4SCpH3T7L/AOCc3iqC18R3uj3N1HbWlveLrt5LMy7PKiTyk/8AH5f/AECv1S0//TNDitmn
                            uX0+WJ4me+k3PLtf7/8Asr/dWvxl/YV16x0f9oLT7bUXVLLUraWykSZvkl+4yI6/8Ar9Wte+IS6b
                            ptvKrL5Xm7GR2+RW/grp5jg5eePLEsfEv9mnwP8AEXVre88WK1/plmq/6CsrLEzbP4//AIiuK+PH
                            7RXhr4ReD30jSLaH7PbwbFt7fYiLF9xE2f7bv/45XBfEv9o220qKXc1ykUrMkTv/ALOxP/Z6/PL4
                            6fEqfxdr13tn2RSt+9RG+82/+P8A74T/AL4rmlKP2TvpU5faM/4lfGjUPGl5cTzys9w0vzTI3yN8
                            ++vL7jVZZm+Zmfd96s95izf36KcaUQqYmUvdieweBvi1P9lh03VZWdIl2QSv/d/uV17+Pm+wXEDT
                            rM6/PE6fxbK+b3+TZVuz8QT26urNvVv7zUpU+YiOLjH4z6Dfxt9ps0VZdm773zfIv9+ul+Fu7x/4
                            3svDUDfJeS+bPs/hVXT5/wDgdfNVt4k3oy7tj7dlfWH/AAT98N32t/EjVdT8qSa0itfKiuGVtnzP
                            /easfZy+0dnt4yj7p98eHtHtvDen2+n6ZAsMUS7N/wDerorCGLTYvPnbZuqxbW1npUT75VR/4vmr
                            jdb8Sf2lcPBbfOitsrb4Th+MdrXiCXVbx1X7n3FrC1vVYtKs5Z3dU2L81XbOFUWVm+R/4t9eG/HX
                            xnKlnLbWz/J/4/8ALSKjE+Yv2nvFreLbi4VZ96Rbk2J/F/cr558H2Et5rlvt3bN1e0ePLPzNJedv
                            9a25/nX56l+BXwxnvLyK8lgbyt2/fTjIJR5pHcaJ4bls9NRmi+Tb9+uK8Z2bPdbVr3vVbNbC38hV
                            3v8A+hrXA3PhKfUrj5Ymf5mf/gNH2i4nC+FdBaa6RWi3/wB1K9o8JeBvt6+b5TfLWr4V+G7Q2u5o
                            tny/frbudSg8GaHdztP5Lquz/wAc/gpDMHxneWPh7w/KqsqfL9z5K+F/H2sLqurSsv8AF89ekfE7
                            4tT6xdXcayfuvm2r/e+evELmZrmfczVvGPN7x5+JqcseQrUSU2iuk8oKKKKAHUeXQn36fDD51ADK
                            VK2LXw9PcbP4N1XYfCtynzbW/wCAVHtInTGhKRg20L7t23fWxZ/d+5vf7i7607bw9LC23yN/y1t2
                            GiNt3NG2+ueVSJ306PKGiPAjJviZHX+Pb8ldLbXkCS7m+f5v7tVLbSvJZdq/991bTSp9ybF/4Btr
                            nOyMTo7DUo0X5fk3N/3zRqvir7NE/kf8CrE/seWFvmb/AGG3rXM+Ibxba3dfNX/aTdUxjzBUlGBz
                            3jXxJJqz7d3yN97/AL6ri/u1b1K8a8uN1VK9KnHkieDUlzyD5nptFFWYhRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU
                            UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR
                            QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFA
                            BRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAF
                            FFFABRRRQAUUUUAFO+9TaKAHV9E/sx2ba43iDSk3TO0EV0q7v4lf+Gvnf+KvZf2bfE7+H/Hl0V8/
                            zZbCVFSH77N96saseaJ1YaXLM+4NE1u6sFu109vJls4ordk2/PuV/wD0H5673SvHN4lvbvuXZuZG
                            RG+8vz/x1y9ho9nNqiPbWzXlvf2a3Cv/AAMy/wBx/vN99609V022hZJ9rI6ysmyFtm7cm999ccT1
                            5cs5HRat4nkv9Lt54Fa8uPPXdaTN/qrf/bT71eW+P9bnRrtNsbpE32jZDs82JV2O6O/+5/B/sVoa
                            rrFjbNKt9PbWb7lulfU754ovlT5/NuIvursf7/zfNXl9zra63H5reX9nliW9i/evLFL87/Pv+7t3
                            u6qn3m2fPVyLjE4z4kWcWqzytqsq3+n2EEtx9nh3bJ52TZ8/8XyO8TbK4xPH0/ie4stSfbcvawRW
                            trDNsiii3bEld9n/AHzsf+FP9utvxnNcvb3CvJHDffZVl3va7JdzSo7pvX5f4E+/XjfiOad7za0u
                            y3aVpfs7rt2xKy7NzL8r/JREJS5D6Ck+JUGl+H7eS0j3ahLI9ra3ES/PFat+63J/D8+xGb+6r/L9
                            2uHvtY26t9jRZJri8ZrWK0WVvK3K/wDE/wDGsX3t38TO9c54e1ie5020VpfO82f9wlu+14olT7+7
                            +8lbGix3U2uXEKwNDCsVqGTO99rbJfK3fxM7/Myr/frQOY+nf2dfhXbalqPhS+SzjsIomit4nmg3
                            p5Wx3d9n+35r/P8Aw1Y8Q+EmubdLm1ad4ory60q1vrht6T+VLsR9/wDzy2bNv+y7tXrfwcv9D0fw
                            XqttqcUF/dyxeU0zq6pK0qb3R3/55IlcV4t1hPENrpmn6HYwTaff/K2oX11/ojeV86RWsS/wy7HV
                            nf8A+IrOXKRTl7x8ya94VuXtU8/9zFEu9kT7jN/n/vuvJPEPhuJG3eVsRvn+7s3V9cXOiL4kW08+
                            e5hTUZW3eTF/qGV3373/ALvybWryLxD4J+3q7rFs2/JLDDL8m7+BEf8Airm5eU9KMozPnmwubzwl
                            4gstTsd0N3ZzrcRf7y7Hr75/4X3aeLPhpZalA297yLbKm7/UN/Gn+99+vlbXvBMFhbpE0q/vW+4k
                            Wx/+BvWVpVnq/hWKWXSpVmtJdzT2krff2/xpW3MR7OMZc0TW+JXxFub+V4FnZ4l/g3O9eKX9/LeX
                            DSt99q6Dxhc77p22tD/sTffrj3mq6cTmxNfk90P96mPMq1E8zNUW7e3zV2cp4kq/8pK01M/5bU1v
                            vNWnpOlT6rf2tpaweddTyrFHF/eZ/u1fwxOb3pSOo+Fvw31X4oeMNN0PSIJJZriRFldF+SKL7ru1
                            fr/8IvhjpnwN8H2Wg2MS/ul2Szfxyt/HvrjP2V/gJpHwE8FxNPAs3iC/VZby7f7/ANz7if7m+tvx
                            D4znv/ECW1t9yVtn+7XBUkerQpnP/Ej4oyv4mextpf8AY2V1vgzTZbbTUnud3nN83zrXlupaDE/j
                            TzG+d1bf/t16rba8sNmkXzfKvy1mdkvh5YkXjPXotKX5fkdv9r7tfN/jy5W+uHVl+eX/AGtyN/t1
                            6l8Qr+V2eVtvy/Ps3V47qt5FNqSMy79zNVhE8/8AEPhKXVYoraCJn3P/AHfutXtXgbQbTwr4c+aJ
                            d6r838FbHh7wlAlhFeMqo/3/AJ/4az9Vdblfsyt/wPb8lA9Tirl5dS1J2Vt+5tn+3/wCvUPBnhKD
                            7Kks67IVX+P+Ja5LRNHVLz5l87+9s+TbTPi18V4vAehvBFKvm+VS+EUjsPGfjzRfCWm3C+bGm1f7
                            3z7v7lfGXxd+N0usSy21tO3lN/D/AB/x15148+KOoeIb+42zs6M33/8AZrz95pbmX5vnauiMeb4j
                            jqV4x92JpTJLfxS3LNWK/wDrK6+TS5bbSdrbfu7/APbrk/8AltW0TgrfzENFP3f8Cof/AFlWcwyi
                            iigB6/M1WrNtsn9+qq/xVas4Wm+Vamp8JtT+I7jRJFeJGX+L5NjrXa6UkDt83/j1ee6UjQxIzfc3
                            fLXVabeb9nzfd2pXnyPeid9bWFnNEn3UStWz8PWbr91X/wBuuX025bb975K6uw/0lfmb5NtQbRiW
                            P7BsV+4tVLnyrDftiXeq/N/s1sIi/JubZWPqs0W3/vqiJtU+E4rxDqskzPtZk+X+CvLPE80s25m+
                            f+9XpGtzKkUteX+ILxnZFrpieTX+E53dtplFFdh4oUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF
                            FFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUU
                            UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ
                            AUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB
                            RRRQAUUUUAPX5Wr074AywQ/Fzw7HfbRb3ErW+5/uqzo6p/49XmP3WrW0PUrnRNWstQtm2XFnKtxH
                            /vK27/2WnL4S4y5ZH6Y/By/ntfCtveXbSPcaXPcafKk334vn+T5K2/E+vRTL5TfOm3e37/Y//fH/
                            AACuX+DPiGLxVZ+KJbT57e/tYtVWszxPrEW+JWWS8SV1iWG0XY/yp9zf/tu/3K8s96l7xheM7+5m
                            tfsyqr/Mtu0P2WLZul/e73Rv9jY3/A65pr9vN8rzV8pm+be2x1+f596L8v30Tb/v0zxDry6b/aFz
                            cyq/lReV/oiu8Svv+5E+/czO6o2/+78v8FcF4n1ue2ldrmJkvfmeXeuzzWbZ8iI33dnyfP8A79Bf
                            900PE9q9zK86qtsjbdqO29FVt7PvT/fRK8P1pZZmUfM7OqRMqNt+X77bv7zfLXa6l48uby1liaWP
                            97A0Uqbvni/jRHf+P50euA1XXoLmbcyqm2VpV2f7P3P++60jExqSJLDXFtrO3iWXyYmn37E++q/w
                            V2fw9t5YfEdu0EbTXW5XnleX5GZX27//AGb/AIBXl9hrC28yMyK6L83zf7+7ZXsfwlv1fVLKJV85
                            JVVJWRtnzq7y7P8AdStzGMuY+lbDxJO/hW7W5inmiV1dX+55v7rZv/u7XfezI/8AsV0fhjxbczXW
                            k2arYvdrarFLcPsRILf76Iqf89XSJ/uf33rj7a5vIbhLNZVht1i2M6S70VmTe7omz+OtfR9NtrbW
                            Xb7HPDLLA0stwku92VUf91s+7ulTzf8AdrlOz7J6N/bn9paSn2axnv8A7ezW7TOqW6Ss3yfuv9ne
                            leNeIfPhW9traBdVu/N++ipFFBK3zuiP/sP8rPXUa9420+zt71dMikh11lRFTUGd0s4lf5HSL7u7
                            591cJD4nsdSa30i2lnv4onbyLd5UXz1/vy7f4Uff8n3quQRlynGeMNNazvP9JljeJm2b0+dFbf8A
                            vUT+9/Av/AK4W/2vK+1W+83yJ/FXqXjPxC15eW9jczxo6s0UX2S12b9z7EiiT73/AAN64rxP4en0
                            Foo7mVftcrbGtLT53Vv4Ed2+7v8A4qxlE2jU+yeea3YQX6utzFsdvuv/ALVeda3oMlhcS7fniX+O
                            vWLCzufELXC20Ek21tk7p/yyVf77/wANY/ieztrBriCfy0fam2FP4f8AY+Wrpy5TGvTjOJ5Lu5+a
                            j+KtjVLFYZWZVZE3f3NtZiQs1ehGUZHgypyhLlG9Gr7K/YJ+An/CT68/jrV7Zn0rTZfKsd6/JLcf
                            xv8A8Arnf2Wv2N9a+Nl4ms68s+j+EYvna4df3t1/sJ/s1+iiaPpHw78Jafouh20dhplhEsUSJ/7P
                            WdSR1Yaj9qRm+P8AxI2j6TL9mb59uzfXmngyO5fVEvLlmfb93f8Aw0eM/ELapL9mX503bP8AYrb0
                            GzS2sImdtny1xHr/AAxOcv7xpvEdxKysn735a6abxDFbWcysy79vy7K8u8W+J9niN4rZtif+hVbt
                            r+XVYk3L/drSJEi34z8Q77V3Vv4a8XudYuZtZTbFvTzW3fwV6xrdgrxJt+fctczf+G1sIPtTKu9v
                            76/+P1mBo3Pj+8sNJRV/hXZ/fqfwZfvq0T3lyzJtbf8AP9xq5rSk/tK6SBvuM/zfx10fjOzbwx4L
                            u5YGZNsT7fn2UxnM6r8WrPR7+4X7Sr7Wb5//AGSvmD40fEqfxVqz/MqRbvuf7Ncj4m8YX11ql3+9
                            b5pa5dnlv3Zm3O9dMYnFVr/ZiV60dFh87UIv4tv3qzpEaJ9tdn4N03fNby/N81bS+E82MeaZtarY
                            SppMrN9zb8tea3ETQy/NX0F4n0FU8P8AmqrO+1a8Q1WHfcPtVvl/iaojI7KlPmiY60NVhof3W7/0
                            Kq1bHnco2iilagQ7b81aumqu5d/yVkp9+tvSk3zfdrKodmG+I6jTUXbtb+8tdBpVms2xtu+sSztl
                            2/7FdBpSeZs/4FXIexGJ0FtZ/uvl/iWtvTXZF+X/ANBrEtpmhVP460LbVXT5dqp/tvWRtzRibz6g
                            211+/XOareN86/f/AN+n3OsKn365fXtbVFf7rvtb5KuMSJSMnxPf7Pl/2fv15lfzfabp2re8Qa20
                            zPF9z5q5b5q7YRPHxFTm90bRR/DRXQcAUUUVABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFF
                            ABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUA
                            FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRR
                            RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFF
                            ACt940bj60UUAfeH7D+p3EtnKHkLLbadcwqp6MqzLtDeuAxA9q6bxpcvp91qRT95LZCR7aWVizQt
                            I6rlecDarELxxRRXm1dz26Ox434016e31y6zHFNBpmlz30MEwLK0ifIu453Y/eM3BBLYJPAriNR8
                            y70K21SeeSa6v40ZjIQwh/dIzCPI43F+TyTgc0UVcDpkeVa5JIvlAyu3mcNk9a52SRmbrRRXTA8i
                            uCsa7L4f+IL7S9Yg+zzbcetFFXMVM+09P1GazhuHjK7/ALHFJlkB+YI2D9f3S/mfWtrTvF17dXUE
                            nl28RS5iZgkQIkwkuAQc8cDpiiiuGoer9g4W+uLi+0pb+4uZJp7ovdTbsYdjcqmOmcBXxjPRV9Kw
                            fCuLXQtfv4kjSe0tmji/dqdq/vgRuILcgAdaKKqJodr8C9Fsbn4anxTcWsV1r95qEtr9uuF3vBDA
                            3lRxxZ4RQp9MkgEnNcP4T8PWvxV+N9v4d1cyW2l2aoyx2DeU0nmNtO9sEnA6YxiiitDlfxCfG7Wh
                            8Pp7vRtA0+y06wiZoNkUZy+1cB255f8A2q8O8Kqupaxq95eD7VPboWjaXnaS45/D+tFFB2RL+s6H
                            ALcuzO7hc7m29V6Hp1r3/wDYi+DXhT4k+JEvdd01bo2y+ekPHll/Ugg5oorCBzVPiP0L1MJoa2ml
                            WMUdtYwjCRxjGK8u+Il9NJa7C2FbriiiiRrQPLbC2jutet4JFyjbs+tdn4wlOn6JEkPyrtooqDeR
                            8/XTsdeaZjvcnOW5r0ezhRdLJC/O3V+9FFUZFzTYhNF82TXIfFy9ls7KKOI7VK8+9FFBUDN+G8Ya
                            +Rm+Y/7XNb37S9xJpvgW6jhf5CuzDKDxs+lFFMKh+b2oSNLdSuxy26uk0azjj0+KXG523Z3c9Uoo
                            rslseHH4zmr75bqUDjLV6z4FtYt0Q2DAXH/oFFFFQuh8Z6h4mt0m8LlGXGF+8owa+dNagEkxZmYk
                            e9FFc1P4j0KnwmBcmqtFFd55GI+IbRRRQYEn8VbGlE7qKKiod+F+I7G1G6ZlycVuabIVuEVQAPpR
                            RXnnsm3YzMypnFT3KBF+UlfoaKKYGTfZjiLBmyF9a4HWrqWKOVlbBC8e1FFbHNU+A46WVp5sudxq
                            P27UUV2HgAPlptFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUA
                            FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU
                            UUUAFFFFAH//2Q=="""
        self.photo = None
        self.background_image.bind("<Configure>", self.load_and_resize_image)
        self.create_buttons()

    def load_and_resize_image(self, event):
        """Update the background image to fit the window size efficiently."""
        try:
            if not self.photo:
                image_bytes = base64.b64decode(self.image_data)
                self.image = Image.open(BytesIO(image_bytes))

            width, height = self.background_image.winfo_width(), self.background_image.winfo_height()

            if self.photo:
                old_width, old_height = self.photo.width(), self.photo.height()
                if old_width == width and old_height == height:
                    return

            resized_image = self.image.resize((width, height), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_image)
            self.background_image.config(image=self.photo)

        except IOError as e:
            messagebox.showerror("Image Load Error", f"Failed to load the image file.\nError: {str(e)}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred.\nError: {str(e)}")

    def create_buttons(self):
        """Create and add buttons to the sidebar."""
        self.sidebar_frame = tk.Frame(self.background_image, highlightbackground="#FFD700",
        highlightthickness= 4)
        self.sidebar_frame.pack(side=tk.LEFT, padx=150)

        button_data = ["Add Member", "View Member Details", "Gym Accounts", "Exit"]
        
        for label in button_data:
            button = tk.Button(
                self.sidebar_frame,
                text=label,
                bg="#2B3A6B",
                fg=self.FG_COLOR,
                font=self.FONT_LARGE,
                width=20,
                command=lambda l=label: self.on_button_click(l))
            button.pack(pady=10, padx=10)

            button.bind("<Enter>", lambda event: self.on_hover(event, is_enter=True))
            button.bind("<Leave>", lambda event: self.on_hover(event, is_enter=False))

    def on_button_click(self, label):
        """Handle button clicks."""
        if label == "Exit":
            self.root.destroy()
        else:
            self.show_content(label)

    def show_content(self, label):
        """Clear previous content and display appropriate content based on the label."""
        self.clear_main_frame()

        self.create_top_frame(label)

        content_functions = {
            "Add Member": self.show_add_member,
            "View Member Details": self.show_member_details,
            "Gym Accounts": self.show_gym_accounts }
        
        if label in content_functions:
            content_functions[label]()

    def clear_main_frame(self):
        """Function to clear the main frame before loading new content."""
        for widget in self.background_image.winfo_children():
            widget.destroy()
            
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()

    def create_top_frame(self, label):
        """Creates a top frame with a label in the center and a back button on the right."""
        top_frame = tk.Frame(self.background_image, bg="#2B3A6B", highlightthickness= 2)
        top_frame.pack(fill="x", pady=20, padx=20)

        back_button = tk.Button(
            top_frame,
            text="⬅️ Back",  
            font=self.FONT_SMALL,
            fg=self.FG_COLOR,
            bg="#6C757D",
            command=self.recreate_sidebar)
        back_button.grid(row=0, column=0, padx=10, sticky="w", ipadx=self.button_padding)

        back_button.bind("<Enter>", lambda event: self.on_hover(event, is_enter=True))
        back_button.bind("<Leave>", lambda event: self.on_hover(event, is_enter=False))

        label_widget = tk.Label(top_frame, text=label, font=self.FONT_LARGE, bg="#2B3A6B", fg=self.FG_COLOR)
        label_widget.grid(row=0, column=1, pady=5, padx=(0,80), sticky="ew")

        top_frame.grid_columnconfigure(1, weight=1)

    def recreate_sidebar(self):
        """Recreate the sidebar and restore the initial layout."""
        self.clear_main_frame()
        self.create_buttons()

    def on_hover(self, event, is_enter):
        """Change button color on hover based on the button's label."""
        label = event.widget.cget("text")

        color_mapping = {
            "Exit": "#C70039",
            "⬅️ Back": "#6C757D",
            "✅ Register": self.GREEN_BG_COLOR,
            "⏳ Reset": self.RED_BG_COLOR,
            "⬆️ Update": self.GREEN_BG_COLOR,
            "✂️ Delete": self.RED_BG_COLOR,
            "✅ Submit": self.GREEN_BG_COLOR,
            "⚠️ Alert" : self.RED_BG_COLOR,
            "Validate": self.BLUE_BG_COLOR,
            "Cancel": self.RED_BG_COLOR,
            "View Members": self.BG_COLOR,
            "Search": "#FFB300"}

        base_color = color_mapping.get(label, "#2B3A6B")

        if is_enter:
            event.widget.config(bg=self.darken_color(base_color))
        elif label == "Exit":
            event.widget.config(bg="#C70039" if is_enter else "#2B3A6B")
        else:
            event.widget.config(bg=base_color)

    def darken_color(self, color):
        """Darkens the given color by a specified factor."""
        color = color.lstrip('#')
        rgb = [int(color[i:i + 2], 16) for i in (0, 2, 4)]
        darkened_rgb = [int(c * 0.8) for c in rgb]
        return '#' + ''.join(f'{c:02x}' for c in darkened_rgb)
    
    def show_add_member(self):
        """Display the Add Member interface."""
        add_member_frame = tk.Frame(self.background_image)
        add_member_frame.pack(pady=20)

        labels = [
            "Name:",
            "Age:",
            "Gender:",
            "Phone Number:",
            "Membership Duration:",
            "Membership Fees: Rs",
            "Payment Method:"]

        for i, text in enumerate(labels):
            tk.Label(add_member_frame, font=self.FONT_MEDIUM, text=text).grid(row=i,
            column=0, pady=10, padx=(10, 0), sticky=tk.E)

        vcmd_text = (add_member_frame.register(self.validate_input), "%P", "letters")
        vcmd_numeric = (add_member_frame.register(self.validate_input), "%P", "numeric")

        self.entry_name = tk.Entry(
            add_member_frame,
            width=25,
            font=self.FONT_SMALL_INPUT,
            validate="key",
            validatecommand=vcmd_text)
        self.entry_name.grid(row=0, column=1, padx=(0, 20))
        self.entry_name.focus()

        age_options = [str(i) for i in range(10, 101)]
        self.age_choice = tk.StringVar(add_member_frame)
        self.age_choice.set("Select")
        age_menu = tk.OptionMenu(add_member_frame, self.age_choice, *age_options)
        age_menu.grid(row=1, column=1, sticky=tk.W)
        age_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)

        self.gender = tk.StringVar(add_member_frame)
        self.gender.set("Select")
        gender_menu = tk.OptionMenu(add_member_frame, self.gender, "Male", "Female")
        gender_menu.grid(row=2, column=1, sticky=tk.W)
        gender_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)

        self.entry_number = tk.Entry(
            add_member_frame,
            width=25,
            font=self.FONT_SMALL_INPUT,
            validate="key",
            validatecommand=vcmd_numeric)
        self.entry_number.grid(row=3, column=1, padx=(0, 20))

        duration_options = [f"{i} month" if i == 1 else f"{i} month's" for i in range(1, 13)]
        self.duration_choice = tk.StringVar(add_member_frame)
        self.duration_choice.set("Select")
        duration_menu = tk.OptionMenu(add_member_frame, self.duration_choice, *duration_options)
        duration_menu.grid(row=4, column=1, sticky=tk.W)
        duration_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)

        self.entry_fees = tk.Entry(
            add_member_frame,
            width=15,
            font=self.FONT_SMALL_INPUT,
            validate="key",
            validatecommand=vcmd_numeric)
        self.entry_fees.grid(row=5, column=1, sticky=tk.W)

        self.payment_method = tk.StringVar(add_member_frame)
        self.payment_method.set("Select")
        payment_menu = tk.OptionMenu(add_member_frame, self.payment_method, "Online", "Cash")
        payment_menu.grid(row=6, column=1, sticky=tk.W)
        payment_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)

        buttons_frame = tk.Frame(add_member_frame)
        buttons_frame.grid(row=8, column=0, columnspan=2, pady=10)

        register_button = tk.Button(
            buttons_frame,
            text="✅ Register",
            command=self.register_member,
            font=self.FONT_SMALL,
            bg=self.GREEN_BG_COLOR,
            fg=self.FG_COLOR)
        register_button.grid(row=0, column=0, padx=20, ipadx=self.button_padding)

        reset_button = tk.Button(
            buttons_frame,
            text="⏳ Reset",
            command=self.reset_form,
            font=self.FONT_SMALL,
            bg=self.RED_BG_COLOR,
            fg=self.FG_COLOR)
        reset_button.grid(row=0, column=1, ipadx=self.button_padding)

        for button in (register_button, reset_button):
            button.bind("<Enter>", lambda event: self.on_hover(event, is_enter=True))
            button.bind("<Leave>", lambda event: self.on_hover(event, is_enter=False))

    def reset_form(self):
        """Reset the form fields to their default state."""
        self.entry_name.delete(0, tk.END)
        self.age_choice.set("Select")
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
        date_of_activation = datetime.now().strftime("%d-%m-%Y")

        if not all([member_name, member_number, member_fees]) or member_age == "Select" or member_gender == "Select" or member_duration == "Select" or payment_method == "Select":
            messagebox.showwarning("Input Required",
            "Please ensure all required fields are filled out before proceeding.")
            return

        formatted_fees = f"Rs {member_fees}"

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(""" INSERT INTO members (name, age, gender, phone_number, duration, fees, payment_method, date_of_activation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (member_name, member_age, member_gender, member_number, member_duration, formatted_fees, payment_method, date_of_activation))
                conn.commit()

                self.reset_form()
                messagebox.showinfo(
                    "Registration Successful!",
                    f"{member_name} registered successfully with the following details:\n\n"
                    f"• Age: {member_age}\n"
                    f"• Gender: {member_gender}\n"
                    f"• Phone Number: {member_number}\n"
                    f"• Membership Duration: {member_duration}\n"
                    f"• Membership Fees: {formatted_fees}\n"
                    f"• Payment Method: {payment_method}")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        
    def show_member_details(self):
        """Display member details in a table format."""
        outer_frame = tk.Frame(self.background_image)
        outer_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        inner_frame = tk.Frame(outer_frame)
        inner_frame.pack(padx=10, fill=tk.BOTH, expand=True)
        
        top_frame = tk.Frame(inner_frame)
        top_frame.pack(pady=10, padx=20, fill=tk.X)

        month_options = self.get_month_options() or ["No Data Available"]
        self.current_month = datetime.now().strftime("%B %Y")

        if self.current_month in month_options:
            self.selected_month = tk.StringVar(value=self.current_month)
        else:
            self.selected_month = tk.StringVar(value=month_options[0])

        month_dropdown = tk.OptionMenu(top_frame, self.selected_month, *month_options)
        month_dropdown.pack(side=tk.LEFT)
        month_dropdown.config(font=self.FONT_SMALL, bg=self.BG_COLOR, fg=self.FG_COLOR)
        self.selected_month.trace_add("write", lambda *args: self.populate_treeview())

        search_button = tk.Button(
            top_frame, 
            text="Search", 
            bg="#FFB300", 
            fg=self.FG_COLOR,
            font=self.FONT_SMALL,
            command=self.search_members)
        search_button.pack(side=tk.RIGHT, ipadx=self.button_padding)

        search_button.bind("<Enter>", lambda event: self.on_hover(event, is_enter=True))
        search_button.bind("<Leave>", lambda event: self.on_hover(event, is_enter=False))

        placeholder_text = "Enter member name to search"

        vcmd_text = (top_frame.register(self.validate_input), "%P", "letters")

        self.search_box = tk.Entry(top_frame, width=30, font=self.FONT_SMALL_INPUT, fg="gray", validate="key",validatecommand=vcmd_text)
        self.search_box.insert(0, placeholder_text)
        self.search_box.pack(padx=10, side=tk.RIGHT)

        self.search_box.bind("<FocusIn>", lambda event: self.clear_placeholder(event, placeholder_text))
        self.search_box.bind("<FocusOut>", lambda event: self.add_placeholder(event, placeholder_text))

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
                "status"),
            show="headings", 
            style="custom.Treeview" )

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

        scrollbar = ttk.Scrollbar(inner_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(padx=(15,0), fill=tk.BOTH, expand=True)

        self.populate_treeview()

        base_frame = tk.Frame(outer_frame)
        base_frame.pack(side=tk.BOTTOM, anchor=tk.CENTER, pady=10)

        update_button = tk.Button(
            base_frame,
            bg=self.GREEN_BG_COLOR,
            fg=self.FG_COLOR,
            font=self.FONT_SMALL,
            text="⬆️ Update",
            command=self.update_record)
        update_button.pack(side=tk.LEFT, padx=20, ipadx=self.button_padding)

        delete_button = tk.Button(
            base_frame,
            bg=self.RED_BG_COLOR,
            fg=self.FG_COLOR,
            font=self.FONT_SMALL,
            text="✂️ Delete",
            command=self.delete_record)
        delete_button.pack(side=tk.RIGHT, ipadx=self.button_padding)

        for button in (delete_button, update_button):
            button.bind("<Enter>", lambda event: self.on_hover(event, is_enter=True))
            button.bind("<Leave>", lambda event: self.on_hover(event, is_enter=False))

        self.tree.bind("<Double-1>", self.on_click)

        style = ttk.Style()
        style.configure("custom.Treeview.Heading", font=self.FONT_MEDIUM_TABLE)
        style.configure("custom.Treeview", font=self.FONT_SMALL_TABLE, rowheight=35)

    def get_month_options(self):
        """Returns a list of months available in the database for selecting."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(""" SELECT DISTINCT substr(date_of_activation, 4, 7) AS activation_month_year FROM members WHERE date_of_activation IS NOT NULL ORDER BY activation_month_year DESC """)
                months = [row[0] for row in cursor.fetchall() if row[0] is not None]

                formatted_months = [datetime.strptime(month, "%m-%Y").strftime("%B %Y") for month in months]
                return formatted_months

        except sqlite3.Error as e:
            messagebox.showerror("Database Error",
            f"An error occurred while retrieving month options: {str(e)}")
            return []

    def populate_treeview(self):
        """Populates the Treeview widget with member data based on the selected month filter."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                selected_month_display = self.selected_month.get()

                if selected_month_display != "No Data Available":

                    selected_month_db = datetime.strptime(selected_month_display, "%B %Y").strftime("%m-%Y")

                    query = """ SELECT id, name, age, gender, phone_number,
                                duration, fees, payment_method, date_of_activation,
                                expiration_date, status FROM members 
                                WHERE substr(date_of_activation, 4, 7) = ? """
                    cursor.execute(query, (selected_month_db,))

                else:
                    query = """ SELECT id, name, age, gender, phone_number,
                            duration, fees, payment_method, date_of_activation,
                            expiration_date, status FROM members """
                    cursor.execute(query)

                rows = cursor.fetchall()
                
                if rows:
                    self.tree.delete(*self.tree.get_children()) 
                    for row in rows:
                        self.tree.insert("", tk.END, values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to retrieve member data.\nDetails: {str(e)}")

    def search_members(self):
        """Search for members based on the name input."""
        search_query = self.search_box.get().strip()

        if search_query == "Enter member name to search" or not search_query:
            messagebox.showwarning("Input Required",
            "Please enter a member name in the search field before proceeding.")
            return
        
        if len(search_query) < 3:
            messagebox.showwarning("Input Required",
            "Please enter at least 3 characters in the search field before proceeding.")
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(""" SELECT id, name, age, gender, phone_number,duration, fees, payment_method, date_of_activation, expiration_date, status FROM members WHERE name LIKE ? """,
                (f"%{search_query}%",))

                rows = cursor.fetchall()

                if not rows:
                    messagebox.showinfo("No Results Found","We couldn't find any matches for your search.")
                    return
                
                self.tree.delete(*self.tree.get_children()) 
                for row in rows:
                    self.tree.insert("", tk.END, values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def clear_placeholder(self, event, placeholder_text):
        """Clear placeholder text when focus is on the entry."""
        if self.search_box.get() == placeholder_text:
            self.search_box.delete(0, tk.END)
            self.search_box.config(fg="black")

    def add_placeholder(self, event, placeholder_text):
        """Add placeholder text when entry is empty and focus is lost."""
        if self.search_box.get() == "":
            self.search_box.insert(0, placeholder_text)
            self.search_box.config(fg="gray")
            
    def update_record(self):
        selected_items = self.tree.selection()

        if not selected_items:
            messagebox.showwarning("Input Warning", "Please select a record to update before proceeding.")
        else:
            selected_item = self.tree.item(selected_items[0])
            self.show_update_member(selected_item)

    def show_update_member(self, item):
        self.create_member_window(lambda: self.update_member(item))
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

    def create_member_window(self, submit_command):
        """Create a window for adding member details."""
        self.member_window = tk.Toplevel(self.root)
        self.member_window.title("Update Member Details")
        self.member_window.resizable(False, False)
        self.member_window.geometry("+400+50")
        self.member_window.grab_set()
        self.member_window.focus()

        labels = [
            "Name:",
            "Phone Number:",
            "Age:",
            "Gender:",
            "Status:",
            "Date of Activation:",
            "Membership Duration:",
            "Membership Fees: Rs",
            "Payment Method:" ]

        for i, text in enumerate(labels):
            tk.Label(self.member_window, font=self.FONT_MEDIUM, text=text).grid(row=i,
            column=0, pady=10, padx=(10, 0), sticky=tk.E)

        vcmd_text = (self.member_window.register(self.validate_input), "%P", "letters")
        vcmd_numeric = (self.member_window.register(self.validate_input), "%P", "numeric")

        self.entry_name = tk.Entry(
            self.member_window,
            width=25,
            font=self.FONT_SMALL_INPUT,
            validate="key",
            validatecommand=vcmd_text)
        self.entry_name.grid(row=0, column=1, padx=(0, 10))

        self.entry_number = tk.Entry(
            self.member_window,
            width=25,
            font=self.FONT_SMALL_INPUT,
            validate="key",
            validatecommand=vcmd_numeric)
        self.entry_number.grid(row=1, column=1, padx=(0, 10))

        age_options = [str(i) for i in range(10, 101)]
        self.age_choice = tk.StringVar(self.member_window)
        self.age_choice.set("Select")
        age_menu = tk.OptionMenu(self.member_window, self.age_choice, *age_options)
        age_menu.grid(row=2, column=1, sticky=tk.W)
        age_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)

        self.gender = tk.StringVar(self.member_window)
        self.gender.set("Select")
        gender_menu = tk.OptionMenu(self.member_window, self.gender, "Male", "Female")
        gender_menu.grid(row=3, column=1, sticky=tk.W)
        gender_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)

        self.status_choice = tk.StringVar(value="Select")
        status_menu = tk.OptionMenu(self.member_window, self.status_choice, "Active", "Inactive")
        status_menu.grid(row=4, column=1, sticky=tk.W)
        status_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)

        one_month_back = date.today() - timedelta(days=30)
        self.date_of_activation_entry = DateEntry(
            self.member_window,
            font=self.FONT_SMALL,
            date_pattern="DD-MM-YYYY",
            mindate=one_month_back)
        self.date_of_activation_entry.grid(row=5, column=1, sticky=tk.W)
        self.date_of_activation_entry.bind("<KeyPress>", lambda event: "break")

        duration_options = [f"{i} month" if i == 1 else f"{i} month's" for i in range(1, 13)]
        self.duration_choice = tk.StringVar(self.member_window)
        self.duration_choice.set("Select")
        duration_menu = tk.OptionMenu(self.member_window, self.duration_choice, *duration_options)
        duration_menu.grid(row=6, column=1, sticky=tk.W)
        duration_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)

        self.entry_fees = tk.Entry(
            self.member_window,
            width=15,
            font=self.FONT_SMALL_INPUT,
            validate="key",
            validatecommand=vcmd_numeric)
        self.entry_fees.grid(row=7, column=1, sticky=tk.W)

        self.payment_method = tk.StringVar(self.member_window)
        self.payment_method.set("Select")
        payment_menu = tk.OptionMenu(self.member_window, self.payment_method, "Online", "Cash")
        payment_menu.grid(row=8, column=1, sticky=tk.W)
        payment_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)

        submit_button = tk.Button(
            self.member_window,
            text="✅ Submit",
            command=submit_command,
            font=self.FONT_SMALL,
            bg=self.GREEN_BG_COLOR,
            fg=self.FG_COLOR)
        submit_button.grid(row=9, column=0, columnspan=2, pady=10 ,ipadx=self.button_padding)

        submit_button.bind("<Enter>", lambda event: self.on_hover(event, is_enter=True))
        submit_button.bind("<Leave>", lambda event: self.on_hover(event, is_enter=False))

    def update_member(self, item):
        formatted_date = self.date_of_activation_entry.get_date().strftime("%d-%m-%Y")
        formatted_fees = "Rs "+ self.entry_fees.get()
 
        updated_values = (
            item["values"][0],
            self.entry_name.get(),
            self.age_choice.get(),
            self.gender.get(),
            self.entry_number.get(),
            self.duration_choice.get(),
            formatted_fees,
            self.payment_method.get(),
            self.status_choice.get(),
            formatted_date )

        if any(str(field).strip() == "" for field in updated_values[1:]) or not self.entry_fees.get().strip():
            messagebox.showwarning("Input Required", "Please ensure all required fields are filled out before proceeding.")
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(""" UPDATE members SET name=?, age=?, gender=?, phone_number=?, duration=?, fees=?, payment_method=?, status=?, date_of_activation=? WHERE id=? """,
                (*updated_values[1:], updated_values[0]))
                conn.commit()
            
            self.populate_treeview()
            self.member_window.destroy()
            messagebox.showinfo("Success", "Member updated successfully.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def delete_record(self):
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showwarning("Input Warning", "Please select a record before attempting to delete.")
            return

        if messagebox.askyesno("Confirm Deletion","Are you sure you want to delete this member?\nThis action cannot be undone."):
            record_id = self.tree.item(selected_item[0], "values")[0]

            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM members WHERE id=?", (record_id,))
                    conn.commit()

                self.populate_treeview()
                messagebox.showinfo("Success", "Member deleted successfully.")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")

    def on_click(self, event):
        """Event handler for clicking on a specific cell in the treeview (column #2)."""
        try:
            col = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)

            if not item or col != "#2":
                return

            cell_data = self.tree.item(item, "values")[1]
            self.show_tooltip(cell_data)

        except IndexError:
            pass
        except Exception as e:
            messagebox.showerror("Selection Error", 
            f"An unexpected error occurred while processing your selection.\nError details: {str(e)}")

    def show_tooltip(self, text):
        """Displays a tooltip near the selected row in the treeview with the provided content."""
        try:
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()

            selected_item = self.tree.focus()
            x, y, width, height = self.tree.bbox(selected_item)
            
            if x and y:
                self.tooltip = tk.Toplevel(self.root)
                self.tooltip.wm_overrideredirect(True)
                self.tooltip.geometry("400x50+150+45")
                self.tooltip.configure(bg="yellow")

                text_widget = tk.Label(
                    self.tooltip,
                    text=text,
                    bg="yellow",
                    font=self.FONT_MEDIUM,
                    anchor="w")
                text_widget.pack(fill=tk.BOTH, expand=True)

                self.tooltip.after(5000, self.tooltip.destroy)

        except Exception as e:
            messagebox.showerror("Tooltip Error",
            f"An error occurred while trying to display the tooltip.\nError details: {str(e)}")

    def show_gym_accounts(self):
        """Display Gym Accounts information."""
        accounts_frame = tk.Frame(self.background_image)
        accounts_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.active_inactive_frame = tk.Frame(accounts_frame, bd=2, relief=tk.SOLID)
        self.active_inactive_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.Notification_frame = tk.Frame(accounts_frame, bd=2, relief=tk.SOLID)
        self.Notification_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")

        accounts_frame.grid_columnconfigure(1, weight=1)
        accounts_frame.grid_rowconfigure(0, weight=1)
        
        self.create_month_selection()
        self.view_monthly_members()
        self.view_inactive_members()

    def create_month_selection(self):
        """Create a dropdown for selecting month and a button to view members."""
        content_label = tk.Label(self.active_inactive_frame,text="Member Details",font=self.FONT_MEDIUM)
        content_label.grid(row=0, column=0, pady=10)
        
        section_frame = tk.Frame(self.active_inactive_frame, bd=2, relief=tk.SOLID)
        section_frame.grid(row=1, column=0, pady=10)

        month_label = tk.Label(section_frame, text="Select Month:", font=self.FONT_MEDIUM)
        month_label.grid(row=0, column=0, padx=(10,0), pady=10)

        month_options = self.get_month_options() or ["No Data Available"]
        self.current_month = datetime.now().strftime("%B %Y")

        if self.current_month in month_options:
            self.selected_month = tk.StringVar(value=self.current_month)
        else:
            self.selected_month = tk.StringVar(value=month_options[0])

        month_dropdown = tk.OptionMenu(section_frame, self.selected_month, *month_options)
        month_dropdown.grid(row=0, column=1, padx=(0,10), pady=10)
        month_dropdown.config(font=self.FONT_SMALL, bg=self.BG_COLOR, fg=self.FG_COLOR)

        view_month_button = tk.Button(
            section_frame,
            text="View Members",
            font=self.FONT_SMALL,
            bg=self.BG_COLOR,
            fg=self.FG_COLOR,
            command=self.view_monthly_members)
        view_month_button.grid(row=1, column=0, columnspan=2, pady=10,ipadx=self.button_padding)

        view_month_button.bind("<Enter>", lambda event: self.on_hover(event, is_enter=True))
        view_month_button.bind("<Leave>", lambda event: self.on_hover(event, is_enter=False))

    def view_monthly_members(self):
        """Displays the active and inactive members for the selected month."""
        selected_month = self.selected_month.get()

        if selected_month == "No Data Available":
            return

        month_year = datetime.strptime(selected_month, "%B %Y").strftime("%m-%Y")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(""" SELECT COUNT(*) AS total_count, COALESCE(SUM(CAST(REPLACE(fees, 'Rs', '') AS REAL)), 0) AS total_fees, (SELECT COUNT(*) FROM members WHERE status = 'Active') AS active_member_count FROM members WHERE substr(date_of_activation, 4, 7) = ? """, (month_year,))

                new_members_details = cursor.fetchone() or (0, 0, 0)
                total_count, total_fees, active_member_count = new_members_details

                cursor.execute(""" SELECT COUNT(*) FROM members  WHERE status = 'Inactive' AND substr(expiration_date, 4, 7) = ? """, (month_year,))

                inactive_member_count = cursor.fetchone()[0] or 0

        except sqlite3.Error as e:
            messagebox.showerror("Database Error",
            f"An error occurred while retrieving member data: {str(e)}")
            return

        self.clear_sections()

        selected_month_display = "Current Month" if selected_month == self.current_month else selected_month

        self.create_members_section( f"Members details for {selected_month_display}.", (total_count, total_fees), active_member_count, inactive_member_count, 2)
        
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

    def create_members_section(self, title, new_member_data, active_data, inactive_data, row):
        """Create a section for displaying active and inactive member data."""
        section_frame = tk.Frame(self.active_inactive_frame, bd=2, relief=tk.SOLID)
        section_frame.grid(row=row, column=0, pady=50, padx=10)

        title_label = tk.Label(section_frame, text=title, font=self.FONT_MEDIUM)
        title_label.grid(row=0, column=0, padx=10, pady=10)
        
        total_members, total_fees = new_member_data
        total_label = tk.Label(
            section_frame,
            text=f"Members Added: {total_members} ➕",
            fg="#388E3C",
            font=self.FONT_MEDIUM_TABLE)
        total_label.grid(row=1, column=0, padx=10, pady=10)

        Total_fees_label = tk.Label(
            section_frame,
            text=f"Total Fees: Rs {total_fees} ⚡",
            fg="#FFB300",
            font=self.FONT_MEDIUM_TABLE)
        Total_fees_label.grid(row=2, column=0, padx=10, pady=10)

        if "Members details for Current Month." in title:
            active_label = tk.Label(
                section_frame,
                text=f"Active Members Till Now: {active_data} ☑️",
                fg="#1976D2",
                font=self.FONT_MEDIUM_TABLE)
            active_label.grid(row=3, column=0, padx=10, pady=10)

            inactive_label = tk.Label(
                section_frame,
                text=f"Inactive Members: {inactive_data} ❎",
                fg="#D32F2F",
                font=self.FONT_MEDIUM_TABLE)
            inactive_label.grid(row=4, column=0, padx=10, pady=10)

    def view_inactive_members(self):
        """Displays the inactive members."""
        self.inner_frame = tk.Frame(self.Notification_frame)
        self.inner_frame.pack(fill=tk.BOTH, expand=True)

        self.top_frame = tk.Frame(self.inner_frame)
        self.top_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(self.top_frame, text="Inactive Members Details", font=self.FONT_MEDIUM).pack(anchor=tk.CENTER)

        display_months = ["Last Month", "This Month"]
        selected_display_month = tk.StringVar(value=display_months[1])

        selected_display_month.trace_add("write",
        lambda *args: self.refresh_inactive_members(selected_display_month.get()))

        month_dropdown_menu = tk.OptionMenu(self.top_frame, selected_display_month, *display_months)
        month_dropdown_menu.config(font=self.FONT_SMALL, bg=self.BG_COLOR, fg=self.FG_COLOR)
        month_dropdown_menu.pack(side=tk.LEFT)

        self.tree = ttk.Treeview(
            self.inner_frame,
            columns=(
                "id",
                "name",
                "phone_number",
                "duration",
                "Inactivation_date"),
            show="headings",
            style="Custom.Treeview")

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

        scrollbar = ttk.Scrollbar(self.inner_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(padx=(15, 0), fill=tk.BOTH, expand=True)

        base_frame = tk.Frame(self.Notification_frame)
        base_frame.pack(pady=10, anchor=tk.CENTER)

        alert_button = tk.Button(base_frame, bg=self.RED_BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL, text="⚠️ Alert", command=self.send_whatsapp_message)
        alert_button.pack(side=tk.LEFT, padx=20, ipadx=self.button_padding)

        update_button = tk.Button(base_frame, bg=self.GREEN_BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL, text="⬆️ Update", command=self.update_inactive)
        update_button.pack(side=tk.RIGHT, ipadx=self.button_padding)

        for button in (alert_button, update_button):
            button.bind("<Enter>", lambda event: self.on_hover(event, is_enter=True))
            button.bind("<Leave>", lambda event: self.on_hover(event, is_enter=False))

        self.tree.bind("<Double-1>", self.on_click)

        self.style = ttk.Style()
        self.style.configure("Custom.Treeview.Heading", font=self.FONT_MEDIUM_TABLE)
        self.style.configure("Custom.Treeview", font=self.FONT_SMALL_TABLE, rowheight=34)

        self.refresh_inactive_members(selected_display_month.get()) 

    def refresh_inactive_members(self, month):
        """Refreshes the inactive members list based on the selected month."""
        for widget in self.top_frame.winfo_children():
            if isinstance(widget, tk.Label) and (widget.cget("text").startswith("Notified:") or widget.cget("text").startswith("Unnotified:")):
                widget.destroy()

        for item in self.tree.get_children():
            self.tree.delete(item)

        current_month = datetime.now().strftime("%m-%Y")
        previous_month = (datetime.now() - relativedelta(months=1)).strftime("%m-%Y")

        month_str = current_month if month == "This Month" else previous_month

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(""" SELECT SUM(CASE WHEN notified = 'True' THEN 1 ELSE 0 END) AS true_count, SUM(CASE WHEN notified = 'False' THEN 1 ELSE 0 END) AS false_count FROM members WHERE status = 'Inactive' AND substr(expiration_date, 4, 7) = ? """, (month_str,))

                result = cursor.fetchone()
                true_count, false_count = (0, 0) if result == (None, None) else result

                cursor.execute(""" SELECT id, name, phone_number, duration, expiration_date FROM members WHERE status = 'Inactive' AND substr(expiration_date, 4, 7) = ?""", (month_str,))
                rows = cursor.fetchall()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            return

        tk.Label(self.top_frame, text=f"Notified: {true_count} ✅", font=self.FONT_SMALL, fg="#76FF03").pack(side=tk.RIGHT, padx=(10, 0))
        tk.Label(self.top_frame, text=f"Unnotified: {false_count} ❎", font=self.FONT_SMALL, fg="#00B0FF").pack(side=tk.RIGHT)

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def send_whatsapp_message(self):
        """Send WhatsApp messages to a list of users if logged in."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(""" SELECT id, name, phone_number, duration, expiration_date FROM members WHERE status = 'Inactive' AND substr(expiration_date, 4, 7) = ? AND notified = 'False' """,
                (self.expiration_month,))
                rows = cursor.fetchall()

            if not rows:
                messagebox.showinfo("No Members to Notify", "All inactive members have already been notified.")
                return

            self.message_count = self.load_message_count()
            self.license_valid, expiration_date = self.load_license_key_status()

            if not self.license_valid and self.message_count >= 20:
                self.handle_license_limit(expiration_date)
                return 

            if not self.is_whatsapp_logged_in():
                messagebox.showerror("WhatsApp Login Error", "WhatsApp Web is not logged in.\nPlease log in and try again.")
                return

            messages_sent = self.process_and_send_messages(rows)

            if messages_sent == len(rows):
                messagebox.showinfo("All Inactive Members Notified!", "All inactive members have been successfully alerted about their membership status!")
                self.show_content("Gym Accounts")
            else:
                self.handle_license_limit(expiration_date)

        except sqlite3.Error as e:
            self.handle_error("Database Error", f"An error occurred: {str(e)}")
        except Exception as e:
            self.handle_error("Message Sending Error",
            f"Failed to send messages.\nPlease try again. Error: {str(e)}")

    def load_message_count(self):
        """Load the message count from the app_data table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT message_count FROM app_data")
                result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            return 0
        
    def load_license_key_status(self):
        """Load the license key expiration date from the app_data table and check its validity."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT license_key_expiration FROM app_data")
                result = cursor.fetchone()
            expiration_date_str = result[0] if result else None

            if expiration_date_str is None:
                return False, None
                
            expiration_date = datetime.strptime(expiration_date_str, "%d-%m-%Y").date()
            is_valid = datetime.now().date() <= expiration_date
            return is_valid, expiration_date

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            return False, None

    def handle_license_limit(self, expiration_date):
        """Handle license limit notifications and prompt for key if necessary."""
        if expiration_date is not None:
            message = (f"""You have reached your limit of 20 free messages and your license key expired on {expiration_date}.\nTo restore full functionality, please enter a valid license key to continue using our services.""")
        else:
            message = "You've reached your free limit of 20 messages.\nTo continue enjoying our services without interruption, please enter a valid license key."

        messagebox.showwarning("License Required", message)
        self.create_license_key_interface()

    def is_whatsapp_logged_in(self):
        """Check if logged into WhatsApp Web and provide an option to stop."""
        self.root.withdraw()
        try:
            self.open_whatsapp_web()
            if messagebox.askyesno("WhatsApp Login", "Are you logged into WhatsApp Web?"):
                return True
            else:
                self.root.deiconify()
                self.root.state("zoomed")
                return False
        except Exception as e:
            self.root.deiconify()
            self.root.state("zoomed")
            messagebox.showerror("Login Error", 
            f"Login check failed.\nError details: {str(e)}")
            return False
        
    def open_whatsapp_web(self):
        """Open WhatsApp Web in a new window and wait for user confirmation."""
        webbrowser.open("https://web.whatsapp.com/")
        time.sleep(10)

    def process_and_send_messages(self, rows):
        """Process each message sending and return the count of messages sent."""
        messages_sent = 0

        for row in rows:
            if not self.license_valid and self.message_count >= 20:
                break
            
            member_id, name, phone_number, duration, expiration_date = row
            
            message = (
                f"Hi {name} 🙏\n"
                f"Your {duration} membership ended on {expiration_date} 🗓️\n"
                "Please renew to keep enjoying our services! 😊\n"
                "Thank you!" )
            
            phone_number_with_code = f"+91{phone_number}"

            try:
                self.kit.sendwhatmsg_instantly(phone_number_with_code, message, 20, True)
                messages_sent += 1

                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(" UPDATE members SET notified = 'True' WHERE id = ? ", (member_id,))
                    
                self.message_count += 1
                self.save_app_data(message_count=self.message_count)

            except Exception as e:
                messagebox.showerror("Message Sending Error",
                f"Failed to send message to {phone_number}.\nError details: {str(e)}")
                self.root.deiconify()
                self.root.state("zoomed")
                return messages_sent

        self.root.deiconify()
        self.root.state("zoomed")

        return messages_sent

    def handle_error(self, title, message):
        """Handle error messages and ensure the main window state is restored."""
        self.root.deiconify()
        self.root.state("zoomed")
        messagebox.showerror(title, message)

    def create_license_key_interface(self):
        """Create the license key entry interface and display license expiration message."""
        self.clear_main_frame()

        self.center_frame = tk.Frame(self.background_image)
        self.center_frame.pack(expand=True, fill=tk.NONE)

        title_label = tk.Label(
            self.center_frame,
            text="License Key Information",
            font=("Arial", 25, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        message_label = tk.Label(
            self.center_frame,
            text="Your license for the WhatsApp API has expired. Please renew to continue using the service.",
            font=("Arial", 20, "bold"),
            fg="red",
            wraplength=700)
        message_label.grid(row=1, column=0, padx=20, columnspan=2)

        license_label = tk.Label(self.center_frame, text="Enter License Key:", font=("Arial", 15, "bold"))
        license_label.grid(row=2, column=0, pady=10, sticky="e")
        
        self.license_entry = tk.Entry(self.center_frame, width=30, font=("Arial", 15))
        self.license_entry.grid(row=2, column=1, pady=10, sticky="w")
        self.license_entry.focus()
        self.license_entry.bind("<KeyRelease>", self.process_license_key)

        buttons_frame = tk.Frame(self.center_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=20)

        validate_button = tk.Button(
            buttons_frame,
            text="Validate",
            font=self.FONT_SMALL,
            bg=self.BLUE_BG_COLOR,
            fg=self.FG_COLOR,
            command=lambda: self.check_license_key(self.license_entry.get()))
        validate_button.pack(side=tk.LEFT, padx=20, ipadx=self.button_padding)

        Cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            font=self.FONT_SMALL,
            bg=self.RED_BG_COLOR,
            fg=self.FG_COLOR,
            command=lambda: self.show_content("Gym Accounts"))
        Cancel_button.pack(side=tk.RIGHT, ipadx=self.button_padding)

        for button in(validate_button, Cancel_button):
            button.bind("<Enter>", lambda event: self.on_hover(event, is_enter=True))
            button.bind("<Leave>", lambda event: self.on_hover(event, is_enter=False))

    def process_license_key(self, event):
        """Validate and format the license key with '-' after every 4 characters, allowing only alphanumeric characters."""
        value = self.license_entry.get().upper()
        allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        filtered_value = "".join(char for char in value if char in allowed_chars)
        limited_value = filtered_value[:16]
        formatted_value = "-".join(limited_value[i : i + 4] for i in range(0, len(limited_value), 4))
        self.license_entry.delete(0, tk.END)
        self.license_entry.insert(0, formatted_value)

    def check_license_key(self, license_key):
        """Check the license key and its expiration date against a file hosted on GitHub."""
        if not license_key:
            messagebox.showwarning("Input Warning", "License key cannot be empty.\nPlease provide a valid key.")
            return
        cleaned_license_key = license_key.replace("-", "").strip()

        if len(cleaned_license_key) != 16:
            messagebox.showwarning("Invalid License Key", 
            "The license key must be 16 characters long.\nPlease enter a valid key.")
            return
            
        url = "https://raw.githubusercontent.com/Nayush29/Gym-manager/master/License_keys.csv"

        try:
            response = requests.get(url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            required_columns = {"License Key", "Expiration Date"}

            if not required_columns.issubset(df.columns):
                messagebox.showerror("License Data Error",
                "Some required information is missing from the license data.\nPlease contact support for assistance to resolve this issue.")
                return
            
            matching_license = df[df["License Key"].str.strip() == license_key.strip()]

            if matching_license.empty:
                messagebox.showerror("License Key Not Found",
                f"Oops!\n\nThe license key '{license_key}' you entered was not found in our records.\n\nPlease double-check and try again or contact support if you need assistance.")
                return
            
            expiration_date_str = matching_license.iloc[0]["Expiration Date"].strip()
            expiration_date = datetime.strptime(expiration_date_str, "%d-%m-%Y").date()
            current_date = datetime.now().date()

            if current_date <= expiration_date:
                messagebox.showinfo("License Key Valid",
                f"Congratulations!\n\nYour license key '{license_key}' is valid until {expiration_date}.\n\nYou can now send WhatsApp messages seamlessly!")
                self.save_app_data(license_key_expiration=expiration_date)
                self.show_content("Gym Accounts")
            else:
                messagebox.showerror("License Key Expired",
                f"Unfortunately,\n\nYour license key '{license_key}' expired on {expiration_date}.\n\nPlease renew your license to continue using the service.")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("License Fetch Error",
            f"An issue occurred while fetching the license.\n\nPlease ensure you have internet access and try again.\n\nError details: {str(e)}")

        except Exception as e:
            messagebox.showerror("Unexpected Error",
            f"Something went wrong.\n\nPlease restart the application or try again.\n\nError: {str(e)}")
            
    def save_app_data(self, message_count=None, license_key_expiration=None):
        """Save the message count and license_key_expiration to the app_data table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(" SELECT id FROM app_data LIMIT 1 ")
                exists = cursor.fetchone()

                if exists:
                    cursor.execute(""" UPDATE app_data SET message_count = COALESCE(?, message_count),license_key_expiration  = COALESCE(?, license_key_expiration) WHERE id = ? """,(message_count, license_key_expiration, exists[0]))
                else:
                    cursor.execute(""" INSERT INTO app_data (message_count, license_key_expiration) 
                    VALUES (?, ?) """,(message_count, license_key_expiration))
                conn.commit()
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def update_inactive(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Input Warning", "Please select a record to update before proceeding.")
        else:
            selected_item = self.tree.item(selected_items[0])
            self.show_update_inactive(selected_item)

    def show_update_inactive(self, item):
        """Display the update window for an inactive member's details."""
        self.create_inactive_window("Update Inactive Details", lambda: self.update_inactive_member(item))
        
        values = item["values"]
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(""" SELECT name, phone_number, duration, fees, date_of_activation, status FROM members WHERE id = ? """, (values[0],))
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
                messagebox.showerror("Member Not Found", 
                "Sorry, we couldn't find the member.\nPlease verify the details and search again.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def create_inactive_window(self, title, submit_command):
        self.member_window = tk.Toplevel(self.root)
        self.member_window.title(title)
        self.member_window.resizable(False, False)
        self.member_window.geometry("+500+200")
        self.member_window.grab_set()
        self.member_window.focus()

        labels = [
            "Name:",
            "Phone Number:",
            "Status:",
            "Date of Activation:",
            "Membership Duration:",
            "Membership Fees:Rs"]
        
        for i, text in enumerate(labels):
            tk.Label(self.member_window, font=self.FONT_MEDIUM, text=text).grid(row=i,
            column=0, pady=10, padx=(10, 0), sticky=tk.E)
            
        vcmd_numeric = (self.member_window.register(self.validate_input), "%P", "numeric")

        self.entry_name = tk.Entry(
            self.member_window,
            font=self.FONT_SMALL_INPUT,
            validate="key",
            justify="center")
        self.entry_name.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)

        self.entry_number = tk.Entry(
            self.member_window,
            font=self.FONT_SMALL_INPUT,
            validate="key",
            justify="center")
        self.entry_number.grid(row=1, column=1, padx=(0, 10), sticky=tk.W)

        self.status_choice = tk.StringVar(value="Select")
        status_menu = tk.OptionMenu(self.member_window, self.status_choice, "Active", "Inactive")
        status_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)
        status_menu.grid(row=2, column=1, sticky=tk.W)
        self.status_choice.trace_add("write", lambda *args: self.update_date_entry_state())

        back_date = date.today() - timedelta(days=5)
        self.date_of_activation_entry = DateEntry(
            self.member_window,
            font=self.FONT_SMALL,
            date_pattern="DD-MM-YYYY",
            mindate=back_date)
        self.date_of_activation_entry.grid(row=3, column=1, sticky=tk.W)
        self.date_of_activation_entry.bind("<KeyPress>", lambda event: "break")

        duration_options = [f"{i} month" if i == 1 else f"{i} month's" for i in range(1, 13)]
        self.duration_choice = tk.StringVar(value="Select")
        duration_menu = tk.OptionMenu(self.member_window, self.duration_choice, *duration_options)
        duration_menu.config(bg=self.BG_COLOR, fg=self.FG_COLOR, font=self.FONT_SMALL)
        duration_menu.grid(row=4, column=1, sticky=tk.W)

        self.entry_fees = tk.Entry(
            self.member_window,
            font=self.FONT_SMALL_INPUT,
            validate="key",
            validatecommand=vcmd_numeric,
            width=10)
        self.entry_fees.grid(row=5, column=1, sticky=tk.W)

        submit_button = tk.Button(
            self.member_window,
            text="✅ Submit",
            command=submit_command,
            font=self.FONT_SMALL,
            bg=self.GREEN_BG_COLOR,
            fg=self.FG_COLOR)
        submit_button.grid(row=6, column=0, columnspan=2, pady=10, ipadx=self.button_padding)

        submit_button.bind("<Enter>", lambda event: self.on_hover(event, is_enter=True))
        submit_button.bind("<Leave>", lambda event: self.on_hover(event, is_enter=False))

    def update_date_entry_state(self):
        status = self.status_choice.get()
        if status == "Inactive":
            self.date_of_activation_entry.config(state=tk.DISABLED)
        else:
            self.date_of_activation_entry.config(state=tk.NORMAL)

    def update_inactive_member(self, item):
        formatted_date = self.date_of_activation_entry.get_date().strftime("%d-%m-%Y")
        formatted_fees = "Rs "+ self.entry_fees.get()

        updated_values = (
            item["values"][0],
            self.duration_choice.get(),
            formatted_fees,
            self.status_choice.get(),
            formatted_date)
        
        if any(str(field).strip() == "" for field in updated_values[1:]) or not self.entry_fees.get().strip():
            messagebox.showwarning("Input Required","Please ensure all required fields are filled out before proceeding.")
            return

        if updated_values[3] != "Active":
            messagebox.showwarning("Activation Required", 
            "Please activate the member before saving the details.")
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(""" UPDATE members SET duration = ?, fees = ?, status = ?,
                date_of_activation = ? WHERE id = ?""",(*updated_values[1:], updated_values[0]))

            self.member_window.destroy()
            self.show_content("Gym Accounts")
            messagebox.showinfo("Success", "Member activated successfully.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        
def check_internet():
    """Checks for an active internet connection."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def main():
    if not check_internet():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Connection Error", "Internet connection issue.\nPlease check your connection.")
        root.destroy()
    else:
        root = tk.Tk()
        GymManagerApp(root)
        root.mainloop()

if __name__ == "__main__":
    main()