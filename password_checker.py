#!/usr/bin/env python3
import re
import math
import tkinter as tk
from tkinter import ttk

# ----------------------------
# Password checking logic
# ----------------------------
SPECIALS = r""" !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""

def evaluate_password(pw: str):
    """Return dict with booleans, score (0-5), label, and entropy estimate."""
    checks = {
        "length": len(pw) >= 8,
        "upper": bool(re.search(r"[A-Z]", pw)),
        "lower": bool(re.search(r"[a-z]", pw)),
        "digit": bool(re.search(r"\d", pw)),
        "special": bool(re.search(rf"[{re.escape(SPECIALS)}]", pw)),
    }

    # Score: one point for each satisfied criterion
    score = sum(checks.values())

    # Strength label
    if score <= 2:
        label = "Weak"
    elif score == 3:
        label = "Moderate"
    elif score == 4:
        label = "Strong"
    else:
        label = "Very Strong"

    # Entropy estimate (very rough): log2(charset_size^length) = length*log2(charset)
    charset = 0
    if checks["lower"]: charset += 26
    if checks["upper"]: charset += 26
    if checks["digit"]: charset += 10
    if checks["special"]: charset += len(SPECIALS)
    # If nothing matched, fallback to lowercase size to avoid 0
    charset = charset or 26
    entropy_bits = len(pw) * math.log2(charset)

    # Suggestions
    suggestions = []
    if len(pw) < 12:
        suggestions.append("Use 12+ characters")
    if not checks["upper"]:
        suggestions.append("Add uppercase letters (A–Z)")
    if not checks["lower"]:
        suggestions.append("Add lowercase letters (a–z)")
    if not checks["digit"]:
        suggestions.append("Add numbers (0–9)")
    if not checks["special"]:
        suggestions.append("Add special characters (!@#...)")
    if re.search(r"(.)\1\1", pw):
        suggestions.append("Avoid repeating the same character 3+ times")
    if re.search(r"(?:password|qwerty|abc|1234)", pw, re.I):
        suggestions.append("Avoid common patterns/words")

    return checks, score, label, entropy_bits, suggestions

# ----------------------------
# GUI
# ----------------------------
class PasswordCheckerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Strength Checker")
        self.geometry("560x420")
        self.minsize(520, 380)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Header
        header = ttk.Label(self, text="🔐 Password Strength Checker", font=("Segoe UI", 16, "bold"))
        header.pack(pady=(14, 6))

        # Frame for input + show toggle
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", padx=16)

        ttk.Label(input_frame, text="Enter password:").grid(row=0, column=0, sticky="w", pady=6)
        self.pw_var = tk.StringVar()
        self.entry = ttk.Entry(input_frame, textvariable=self.pw_var, show="•", width=46, font=("Segoe UI", 11))
        self.entry.grid(row=1, column=0, sticky="we", pady=(0, 6), columnspan=2)
        input_frame.columnconfigure(0, weight=1)

        self.show_var = tk.BooleanVar(value=False)
        show_chk = ttk.Checkbutton(input_frame, text="Show", variable=self.show_var, command=self.toggle_show)
        show_chk.grid(row=1, column=2, padx=(8,0))

        # Strength bar + label
        bar_frame = ttk.Frame(self)
        bar_frame.pack(fill="x", padx=16, pady=(6, 4))

        ttk.Label(bar_frame, text="Strength:").pack(anchor="w")
        self.progress = ttk.Progressbar(bar_frame, maximum=5)
        self.progress.pack(fill="x", pady=4)

        self.str_label = ttk.Label(bar_frame, text="—", font=("Segoe UI", 11, "bold"))
        self.str_label.pack(anchor="w")

        # Criteria checklist
        crit_frame = ttk.LabelFrame(self, text="Criteria")
        crit_frame.pack(fill="x", padx=16, pady=(8, 4))

        self.chk_len = ttk.Label(crit_frame, text="• Length ≥ 8")
        self.chk_up = ttk.Label(crit_frame, text="• Uppercase letter (A–Z)")
        self.chk_lo = ttk.Label(crit_frame, text="• Lowercase letter (a–z)")
        self.chk_dg = ttk.Label(crit_frame, text="• Number (0–9)")
        self.chk_sp = ttk.Label(crit_frame, text="• Special character (!@#...)")

        for i, w in enumerate([self.chk_len, self.chk_up, self.chk_lo, self.chk_dg, self.chk_sp]):
            w.grid(row=i, column=0, sticky="w", padx=8, pady=2)

        # Entropy + tips
        info_frame = ttk.LabelFrame(self, text="Analysis")
        info_frame.pack(fill="both", expand=True, padx=16, pady=(8, 12))

        self.entropy_lbl = ttk.Label(info_frame, text="Entropy: — bits")
        self.entropy_lbl.pack(anchor="w", padx=8, pady=(6, 2))

        self.tips = tk.Text(info_frame, height=4, wrap="word")
        self.tips.configure(state="disabled")
        self.tips.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))

        copy_btn = ttk.Button(btn_frame, text="Copy Password", command=self.copy_password)
        copy_btn.pack(side="left")

        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_all)
        clear_btn.pack(side="right")

        # Live updates
        self.entry.bind("<KeyRelease>", lambda e: self.update_assessment())
        self.update_assessment()
        self.entry.focus_set()

    # ------------ helpers ------------
    def toggle_show(self):
        self.entry.config(show="" if self.show_var.get() else "•")

    def set_check_style(self, widget: ttk.Label, ok: bool):
        widget.config(foreground=("#1b5e20" if ok else "#b71c1c"))
        text = widget.cget("text")
        # ensure consistent bullet/checkbox look
        if ok and not text.startswith("✔ "):
            widget.config(text="✔ " + text.lstrip("• ").lstrip("✔ ").lstrip("✖ "))
        elif not ok and not text.startswith("✖ "):
            widget.config(text="✖ " + text.lstrip("• ").lstrip("✔ ").lstrip("✖ "))

    def color_for_score(self, score: int):
        # 0..5 → color
        return {
            0: "#b71c1c",  # red
            1: "#e53935",
            2: "#fb8c00",  # orange
            3: "#fdd835",  # yellow
            4: "#43a047",  # green
            5: "#1b5e20",  # dark green
        }.get(score, "#1b5e20")

    def update_assessment(self):
        pw = self.pw_var.get()
        checks, score, label, entropy_bits, suggestions = evaluate_password(pw)

        # progress and label
        self.progress['value'] = score
        self.progress.update_idletasks()
        self.str_label.config(text=f"{label}  (score {score}/5)", foreground=self.color_for_score(score))

        # check items
        self.set_check_style(self.chk_len, checks["length"])
        self.set_check_style(self.chk_up, checks["upper"])
        self.set_check_style(self.chk_lo, checks["lower"])
        self.set_check_style(self.chk_dg, checks["digit"])
        self.set_check_style(self.chk_sp, checks["special"])

        # entropy
        self.entropy_lbl.config(text=f"Entropy: {entropy_bits:.1f} bits")

        # tips
        self.tips.configure(state="normal")
        self.tips.delete("1.0", "end")
        if pw == "":
            self.tips.insert("end", "Type a password to see feedback and suggestions here.")
        elif suggestions:
            self.tips.insert("end", "Suggestions:\n- " + "\n- ".join(suggestions))
        else:
            self.tips.insert("end", "Great! Your password meets all criteria.")
        self.tips.configure(state="disabled")

    def copy_password(self):
        pw = self.pw_var.get()
        if not pw:
            return
        self.clipboard_clear()
        self.clipboard_append(pw)

    def clear_all(self):
        self.pw_var.set("")
        self.update_assessment()

# ----------------------------
# Run app
# ----------------------------
if __name__ == "__main__":
    app = PasswordCheckerGUI()
    app.mainloop()
