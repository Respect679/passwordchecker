import tkinter as tk
from PIL import Image, ImageTk
import re
import os
import hashlib
import requests

# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("Cyber Security Password Checker")
root.geometry("800x500")
root.minsize(600, 400)

# ----------- Load Background Image -----------
if not os.path.exists("back.png"):
    raise FileNotFoundError("❌ 'back.png' not found in this folder.")
original_image = Image.open("back.png")

bg_label = tk.Label(root)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
current_photo = None

def resize_bg(event):
    def apply_resize():
        global current_photo
        w, h = root.winfo_width(), root.winfo_height()
        resized = original_image.resize((w, h), Image.LANCZOS)
        current_photo = ImageTk.PhotoImage(resized)
        bg_label.config(image=current_photo)
    root.after(50, apply_resize)

root.bind("<Configure>", resize_bg)
root.after(100, lambda: resize_bg(None))  # Initial load

# ---------------- Breach Check Function ----------------
def check_pwned(password):
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    try:
        res = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
        if res.status_code != 200:
            return "⚠️ Could not check breach status"
        hashes = res.text.splitlines()
        for line in hashes:
            hash_suffix, count = line.split(":")
            if hash_suffix == suffix:
                return f"⚠️ Found in {count} breaches!"
        return "✅ Not found in known breaches"
    except:
        return "⚠️ API error (check internet)"

# ---------------- Password Strength Logic ----------------
common_passwords = ["123456", "password", "qwerty", "letmein", "abc123"]

def check_strength(event=None):
    password = entry.get()
    strength = "Weak 🔴"
    color = "#ff4d4d"
    tips = []

    if password in common_passwords:
        strength = "Very Weak ❌"
        tips.append("Avoid common passwords.")
    elif len(password) < 8:
        tips.append("Use at least 8 characters.")
    else:
        if not re.search(r"[A-Z]", password):
            tips.append("Add an uppercase letter.")
        if not re.search(r"[a-z]", password):
            tips.append("Add a lowercase letter.")
        if not re.search(r"[0-9]", password):
            tips.append("Include a number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            tips.append("Use special characters like @ or #.")

        if not tips:
            strength = "Strong 🟢"
            color = "#4CAF50"
        elif len(tips) <= 2:
            strength = "Medium 🟠"
            color = "#FFA500"

    # Add real-world breach check
    breach_status = check_pwned(password)
    tips.append(breach_status)

    result_label.config(text=f"Strength: {strength}", fg=color)
    tip_label.config(text="\n".join(tips), fg="white")

# ---------------- Overlay UI ----------------
overlay = tk.Frame(root, bg="#000000", bd=0)
overlay.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(overlay, text="🔐 Password Strength Checker", font=("Helvetica", 18, "bold"),
         bg="#000000", fg="white").pack(pady=10)

# Entry field
entry = tk.Entry(overlay, show="*", font=("Helvetica", 14), width=30,
                 bg="#333", fg="white", insertbackground="white", bd=1, relief="flat")
entry.pack(pady=5)
entry.bind("<KeyRelease>", check_strength)

# Show/Hide toggle
show_password = False
def toggle_password():
    global show_password
    if show_password:
        entry.config(show="*")
        toggle_btn.config(text="👁️ Show")
        show_password = False
    else:
        entry.config(show="")
        toggle_btn.config(text="🔒 Hide")
        show_password = True

toggle_btn = tk.Button(overlay, text="👁️ Show", command=toggle_password,
                       font=("Helvetica", 10), bg="#555", fg="white",
                       relief="flat", padx=5, pady=2)
toggle_btn.pack(pady=4)

# Result Labels
result_label = tk.Label(overlay, text="", font=("Helvetica", 14, "bold"),
                        bg="#000000", fg="white")
result_label.pack(pady=5)

tip_label = tk.Label(overlay, text="", font=("Helvetica", 11),
                     bg="#000000", fg="white", wraplength=500, justify="left")
tip_label.pack(pady=5)

# Exit Button
tk.Button(overlay, text="Exit", command=root.quit, font=("Helvetica", 10, "bold"),
          bg="#d9534f", fg="white", padx=10, pady=4, relief="flat").pack(pady=10)

# Run the app
root.mainloop()
