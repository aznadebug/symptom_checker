"""Symptom Checker Pro - rule-based medical triage assistant.
Educational only. NOT a medical diagnosis.
Run: python symptom_checker_pro.py   (standalone, no installs needed)
"""
import csv
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

HISTORY_FILE = "history.csv"

# ---------------------------------------------------------------- DATA
CONDITIONS = {
    "Common Cold": {
        "symptoms": {"runny nose": 3, "sneezing": 3, "sore throat": 2,
                     "cough": 2, "mild fever": 1, "fatigue": 1},
        "advice": "Rest, drink fluids, and use over-the-counter relief."},
    "Influenza (Flu)": {
        "symptoms": {"high fever": 3, "body aches": 3, "fatigue": 2,
                     "cough": 2, "headache": 2, "chills": 3},
        "advice": "Rest and hydrate. See a doctor if high-risk or worsening."},
    "COVID-19": {
        "symptoms": {"high fever": 2, "cough": 3, "loss of smell": 4,
                     "fatigue": 2, "shortness of breath": 3, "sore throat": 1},
        "advice": "Take a test, isolate, and monitor your breathing."},
    "Allergies": {
        "symptoms": {"sneezing": 3, "runny nose": 2, "itchy eyes": 4,
                     "rash": 2, "cough": 1},
        "advice": "Avoid triggers; antihistamines may help."},
    "Migraine": {
        "symptoms": {"headache": 4, "nausea": 3, "light sensitivity": 4,
                     "dizziness": 2},
        "advice": "Rest in a dark, quiet room and stay hydrated."},
    "Food Poisoning": {
        "symptoms": {"nausea": 3, "vomiting": 4, "diarrhea": 4,
                     "stomach pain": 3, "mild fever": 1},
        "advice": "Replace fluids with oral rehydration. Seek care if severe."},
}
RED_FLAGS = {"shortness of breath", "chest pain"}
ALL_SYMPTOMS = sorted({s for c in CONDITIONS.values()
                       for s in c["symptoms"]} | RED_FLAGS)
SEVERITY = {"Mild": 0.6, "Moderate": 1.0, "Severe": 1.4}
RISK_COLORS = {"LOW": "#2e9e5b", "MODERATE": "#e0a100", "HIGH": "#d64545"}

DARK_MODE = True  # set to False for the light theme
if DARK_MODE:
    BG, PANEL, FIELD = "#000000", "#121212", "#1e1e1e"
    FG, MUTED, BORDER = "#e6e6e6", "#9a9a9a", "#333333"
    ACCENT, HEADER, BAR_BG = "#4da3ff", "#0d2a45", "#2a2a2a"
    BTN, BTN_HOVER = "#1f3a5a", "#2b4f7a"
else:
    BG, PANEL, FIELD = "#f0f0f0", "#ffffff", "#ffffff"
    FG, MUTED, BORDER = "#222222", "#666666", "#cccccc"
    ACCENT, HEADER, BAR_BG = "#1f78b4", "#1f4e79", "#eeeeee"
    BTN, BTN_HOVER = "#dcdcdc", "#c8c8c8"


# ---------------------------------------------------------------- LOGIC
def score_conditions(selected):
    """selected: {symptom: severity_multiplier} -> sorted [(name, pct)]."""
    results = []
    for name, data in CONDITIONS.items():
        weights = data["symptoms"]
        total = sum(weights.values())
        matched = sum(w * selected[s] for s, w in weights.items()
                      if s in selected)
        pct = min(100.0, round(matched / total * 100, 1))
        if pct > 0:
            results.append((name, pct))
    return sorted(results, key=lambda x: x[1], reverse=True)


def assess_risk(selected, severities, results, age, days):
    """Combine several factors into a LOW / MODERATE / HIGH rating."""
    points, reasons = 0, []
    if set(selected) & RED_FLAGS:
        points += 3
        reasons.append("red-flag symptom present")
    if severities.count("Severe") >= 3:
        points += 1
        reasons.append("multiple severe symptoms")
    if results and results[0][1] >= 60:
        points += 1
        reasons.append("strong match to a condition")
    if age < 5 or age > 65:
        points += 1
        reasons.append("age is a higher-risk group")
    if days > 7:
        points += 1
        reasons.append("symptoms lasting over a week")
    level = "HIGH" if points >= 3 else "MODERATE" if points == 2 else "LOW"
    return level, reasons


def save_history(row):
    new = not os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["Time", "Age", "Days", "Symptoms",
                        "Top match", "Match %", "Risk"])
        w.writerow(row)


# ---------------------------------------------------------------- GUI
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Symptom Checker Pro")
        self.geometry("980x640")
        self.configure(bg=BG)
        self.setup_style()
        tk.Label(self, text="Symptom Checker Pro", bg=HEADER, fg="white",
                 font=("Arial", 16, "bold"), pady=10).pack(fill="x")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        self.check_tab, self.hist_tab = ttk.Frame(nb), ttk.Frame(nb)
        nb.add(self.check_tab, text="  Check  ")
        nb.add(self.hist_tab, text="  History  ")
        self.build_check()
        self.build_history()
        tk.Label(self, bg=BG, fg=MUTED, text="Educational tool only. "
                 "Not a medical diagnosis. In an emergency, call your "
                 "local emergency number.").pack(pady=3)

    # ---- theme
    def setup_style(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure(".", background=BG, foreground=FG, fieldbackground=FIELD,
                     bordercolor=BORDER, lightcolor=BG, darkcolor=BG,
                     troughcolor=FIELD, insertcolor=FG)
        st.configure("TFrame", background=BG)
        st.configure("TLabel", background=BG, foreground=FG)
        st.configure("TLabelframe", background=BG, bordercolor=BORDER)
        st.configure("TLabelframe.Label", background=BG, foreground=FG)
        st.configure("TCheckbutton", background=BG, foreground=FG)
        st.map("TCheckbutton", background=[("active", BG)],
               foreground=[("active", FG)],
               indicatorcolor=[("selected", ACCENT), ("!selected", FIELD)])
        st.configure("TButton", background=BTN, foreground=FG, padding=6,
                     bordercolor=BORDER)
        st.map("TButton", background=[("active", BTN_HOVER)])
        st.configure("TEntry", fieldbackground=FIELD, foreground=FG)
        st.configure("TSpinbox", fieldbackground=FIELD, foreground=FG,
                     arrowcolor=FG)
        st.configure("TCombobox", fieldbackground=FIELD, foreground=FG,
                     background=BTN, arrowcolor=FG, selectbackground=FIELD,
                     selectforeground=FG)
        st.map("TCombobox", fieldbackground=[("readonly", FIELD)],
               foreground=[("readonly", FG)])
        self.option_add("*TCombobox*Listbox.background", FIELD)
        self.option_add("*TCombobox*Listbox.foreground", FG)
        self.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        st.configure("TNotebook", background=BG, bordercolor=BORDER)
        st.configure("TNotebook.Tab", background=PANEL, foreground=MUTED,
                     padding=(12, 6))
        st.map("TNotebook.Tab", background=[("selected", BTN)],
               foreground=[("selected", FG)])
        st.configure("Treeview", background=FIELD, fieldbackground=FIELD,
                     foreground=FG, bordercolor=BORDER)
        st.configure("Treeview.Heading", background=PANEL, foreground=FG)
        st.map("Treeview", background=[("selected", ACCENT)],
               foreground=[("selected", "#000000")])

    # ---- check tab
    def build_check(self):
        left = ttk.Frame(self.check_tab)
        left.pack(side="left", fill="y", padx=10, pady=8)
        right = ttk.Frame(self.check_tab)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        info = ttk.LabelFrame(left, text="Patient info")
        info.pack(fill="x")
        ttk.Label(info, text="Age:").grid(row=0, column=0, padx=6, pady=5)
        self.age = ttk.Entry(info, width=6)
        self.age.insert(0, "25")
        self.age.grid(row=0, column=1)
        ttk.Label(info, text="Days sick:").grid(row=0, column=2, padx=6)
        self.days = ttk.Spinbox(info, from_=0, to=60, width=5)
        self.days.set(1)
        self.days.grid(row=0, column=3, padx=(0, 6))

        sym = ttk.LabelFrame(left, text="Symptoms and severity")
        sym.pack(fill="x", pady=8)
        self.vars, self.sev = {}, {}
        per_col = 11
        for i, s in enumerate(ALL_SYMPTOMS):
            r, c = i % per_col, (i // per_col) * 2
            self.vars[s] = tk.BooleanVar()
            ttk.Checkbutton(sym, text=s.title(),
                            variable=self.vars[s]).grid(
                row=r, column=c, sticky="w", padx=6, pady=2)
            cb = ttk.Combobox(sym, values=list(SEVERITY), width=9,
                              state="readonly")
            cb.set("Moderate")
            cb.grid(row=r, column=c + 1, padx=(0, 10))
            self.sev[s] = cb

        btns = ttk.Frame(left)
        btns.pack(pady=4)
        ttk.Button(btns, text="Analyze", command=self.analyze).pack(
            side="left", padx=4)
        ttk.Button(btns, text="Clear", command=self.clear).pack(
            side="left", padx=4)

        self.risk = tk.Label(right, text="RISK LEVEL: --", bg="#555",
                             fg="white", font=("Arial", 14, "bold"), pady=8)
        self.risk.pack(fill="x")
        self.canvas = tk.Canvas(right, height=190, bg=PANEL,
                                highlightthickness=1,
                                highlightbackground=BORDER)
        self.canvas.pack(fill="x", pady=8)
        self.text = tk.Text(right, height=10, wrap="word", state="disabled",
                            bg=FIELD, fg=FG, insertbackground=FG,
                            relief="flat", highlightthickness=1,
                            highlightbackground=BORDER, padx=8, pady=8)
        self.text.pack(fill="both", expand=True)

    def analyze(self):
        try:
            age, days = int(self.age.get()), int(self.days.get())
            if not (0 <= age <= 120 and days >= 0):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input",
                                 "Enter a valid age (0-120) and days.")
            return
        chosen = [s for s, v in self.vars.items() if v.get()]
        if not chosen:
            messagebox.showinfo("No symptoms", "Select at least one symptom.")
            return
        sev_names = [self.sev[s].get() for s in chosen]
        selected = {s: SEVERITY[self.sev[s].get()] for s in chosen}

        results = score_conditions(selected)
        level, reasons = assess_risk(selected, sev_names, results, age, days)
        self.draw_bars(results[:5])
        self.risk.config(text=f"RISK LEVEL: {level}", bg=RISK_COLORS[level])

        lines = []
        if results:
            lines.append(f"Top match: {results[0][0]} ({results[0][1]}%)")
            lines.append(f"Advice: {CONDITIONS[results[0][0]]['advice']}")
        else:
            lines.append("No condition matched. Consider seeing a doctor.")
        if reasons:
            lines.append("\nRisk factors: " + "; ".join(reasons) + ".")
        if level == "HIGH":
            lines.append("\nPlease seek medical attention promptly.")
        self.set_text("\n".join(lines))

        top = results[0] if results else ("None", 0)
        save_history([f"{datetime.now():%Y-%m-%d %H:%M}", age, days,
                      ", ".join(chosen), top[0], top[1], level])
        self.load_history()

    def draw_bars(self, results):
        self.canvas.delete("all")
        if not results:
            return
        for i, (name, pct) in enumerate(results):
            y = 15 + i * 34
            self.canvas.create_text(10, y + 10, text=name, anchor="w",
                                    font=("Arial", 10), fill=FG)
            x0 = 170
            self.canvas.create_rectangle(x0, y, x0 + 300, y + 20,
                                         fill=BAR_BG, outline="")
            self.canvas.create_rectangle(x0, y, x0 + 3 * pct, y + 20,
                                         fill=ACCENT, outline="")
            self.canvas.create_text(x0 + 310, y + 10, text=f"{pct}%",
                                    anchor="w", font=("Arial", 10, "bold"),
                                    fill=FG)

    def set_text(self, msg):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", msg)
        self.text.config(state="disabled")

    def clear(self):
        for s in ALL_SYMPTOMS:
            self.vars[s].set(False)
            self.sev[s].set("Moderate")
        self.canvas.delete("all")
        self.risk.config(text="RISK LEVEL: --", bg="#555")
        self.set_text("")

    # ---- history tab
    def build_history(self):
        cols = ["Time", "Age", "Days", "Symptoms", "Top match",
                "Match %", "Risk"]
        self.tree = ttk.Treeview(self.hist_tab, columns=cols,
                                 show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=300 if c == "Symptoms" else 90)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Button(self.hist_tab, text="Clear history",
                   command=self.clear_history).pack(pady=4)
        self.load_history()

    def load_history(self):
        self.tree.delete(*self.tree.get_children())
        if not os.path.exists(HISTORY_FILE):
            return
        with open(HISTORY_FILE, newline="") as f:
            rows = list(csv.reader(f))[1:]
        for row in reversed(rows):
            self.tree.insert("", "end", values=row)

    def clear_history(self):
        if messagebox.askyesno("Confirm", "Delete all saved history?"):
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            self.load_history()


if __name__ == "__main__":
    App().mainloop()