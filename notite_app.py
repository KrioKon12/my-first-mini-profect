import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, TYPE_CHECKING
from datetime import datetime
import sqlite3

if TYPE_CHECKING:
    from tkinter import Tk


class ManagerNotite:
    def __init__(self, root_window: "tk.Tk"):
        self.root: "tk.Tk" = root_window
        self.notes: List[dict] = []
        self.edit_index = None
        self.dark_mode = False

        # Culori Light/Dark
        self.colors = {
            'light': {
                'bg': '#f8f9fa',
                'fg': '#212529',
                'card_bg': '#ffffff',
                'button_bg': '#007bff',
                'entry_bg': '#ffffff',
                'combobox_bg': '#ffffff'
            },
            'dark': {
                'bg': '#1a1a1a',
                'fg': '#ffffff',
                'card_bg': '#2d2d2d',
                'button_bg': '#0d6efd',
                'entry_bg': '#2d2d2d',
                'combobox_bg': '#2d2d2d'
            }
        }

        # Categorii
        self.categorii = ["Personal", "Muncă", "Școală", "Altele"]

        # Setări fereastră
        self.root.title("📝 Manager Notițe")
        self.root.geometry("700x600")
        self.root.bind("<Delete>", lambda e: self.delete_notite())
        self.root.bind("<Control-s>", lambda e: self.save_notite())
        self.root.bind("<Control-Return>", lambda e: self.add_note())
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

        # Stiluri ttk
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        # Entry notiță
        self.entry_notite = ttk.Entry(self.root, style="Light.TEntry")
        self.entry_notite.pack(pady=5, padx=10, fill=tk.X)

        # ComboBox categorie
        self.categorie_var = tk.StringVar(value=self.categorii[0])
        self.combo_categorie = ttk.Combobox(
            self.root, textvariable=self.categorie_var, values=self.categorii,
            state="readonly", style="Light.TCombobox"
        )
        self.combo_categorie.pack(pady=5)

        # ComboBox pentru filtre
        self.filter_categorie_var = tk.StringVar(value="Toate")
        categorii_filtrare = ["Toate"] + self.categorii
        self.combo_filter_categorie = ttk.Combobox(
            self.root, textvariable=self.filter_categorie_var,
            values=categorii_filtrare, state="readonly", style="Light.TCombobox"
        )
        self.combo_filter_categorie.pack(pady=5, padx=10, fill=tk.X)
        self.combo_filter_categorie.bind("<<ComboboxSelected>>", self.filter_notes)

        # Căutare
        self.search_var = tk.StringVar()
        self.entry_search = ttk.Entry(self.root, textvariable=self.search_var, style="Light.TEntry")
        self.entry_search.pack(pady=5, padx=10, fill=tk.X)
        self.entry_search.insert(0, "Caută...")
        self.entry_search.bind("<KeyRelease>", self.filter_notes)

        # Listbox + scrollbars
        self.frame_listbox = tk.Frame(self.root)
        self.frame_listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(
            self.frame_listbox, height=15, width=50, bg="white", bd=2, relief="solid"
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar_y = tk.Scrollbar(self.frame_listbox, orient=tk.VERTICAL, command=self.listbox.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.scrollbar_y.set)

        self.scrollbar_x = tk.Scrollbar(self.frame_listbox, orient=tk.HORIZONTAL, command=self.listbox.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.listbox.config(xscrollcommand=self.scrollbar_x.set)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, anchor="w", style="Light.TLabel")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # Frame butoane
        self.frame_butoane = ttk.Frame(self.root)
        self.frame_butoane.pack(pady=5, padx=10, fill=tk.X)

        # Butoane principale
        btn_info = [
            ("Adaugă", self.add_note),
            ("Șterge", self.delete_notite),
            ("Editează", self.start_edit),
            ("Salvează modificarea", self.edit_note),
            ("🌙 Mod Întunecat", self.toggle_dark_mode)
        ]
        for text, cmd in btn_info:
            ttk.Button(self.frame_butoane, text=text, command=cmd, style="Light.TButton").pack(
                side=tk.LEFT, padx=5, expand=True, fill=tk.X
            )

        # Încărcare notițe
        self.load_notite()

        # Aplică tema Light/Dark inițială
        self.apply_theme()

    def configure_styles(self):
        # Light
        self.style.configure("Light.TEntry", fieldbackground=self.colors['light']['entry_bg'], foreground=self.colors['light']['fg'])
        self.style.configure("Light.TCombobox", fieldbackground=self.colors['light']['combobox_bg'], foreground=self.colors['light']['fg'])
        self.style.configure("Light.TButton", background=self.colors['light']['button_bg'], foreground="white")
        self.style.configure("Light.TLabel", background=self.colors['light']['bg'], foreground=self.colors['light']['fg'])

        # Dark
        self.style.configure("Dark.TEntry", fieldbackground=self.colors['dark']['entry_bg'], foreground=self.colors['dark']['fg'])
        self.style.configure("Dark.TCombobox", fieldbackground=self.colors['dark']['combobox_bg'], foreground=self.colors['dark']['fg'])
        self.style.configure("Dark.TButton", background=self.colors['dark']['button_bg'], foreground="white")
        self.style.configure("Dark.TLabel", background=self.colors['dark']['bg'], foreground=self.colors['dark']['fg'])

    def apply_theme(self):
        theme = 'dark' if self.dark_mode else 'light'
        colors = self.colors[theme]

        # Fereastra principală
        self.root.configure(bg=colors['bg'])

        # Entry notiță și căutare
        self.entry_notite.configure(background=colors['entry_bg'], foreground=colors['fg'])
        self.entry_search.configure(background=colors['entry_bg'], foreground=colors['fg'])

        # Combobox-uri
        self.combo_categorie.configure(style=f"{theme.capitalize()}.TCombobox")
        self.combo_filter_categorie.configure(style=f"{theme.capitalize()}.TCombobox")

        # Listbox
        self.listbox.configure(bg=colors['card_bg'], fg=colors['fg'], selectbackground=colors['button_bg'], selectforeground="white")

        # Frame listbox
        self.frame_listbox.configure(bg=colors['card_bg'])

        # Status
        self.status_label.configure(style=f"{theme.capitalize()}.TLabel")

        # Butoane
        for child in self.frame_butoane.winfo_children():
            child.configure(style=f"{theme.capitalize()}.TButton")

    def add_note(self):
        noul_text = self.entry_notite.get().strip()
        categorie = self.categorie_var.get()
        if noul_text:
            data_ora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.notes.append({"text": noul_text, "categorie": categorie, "data_ora": data_ora})
            self.sort_notes()
            self.entry_notite.delete(0, tk.END)
            self.filter_notes()
        else:
            messagebox.showwarning("Avertisment", "Nu ai introdus nicio notiță")

    def update_listbox(self, lista=None):
        self.listbox.delete(0, tk.END)
        if lista is None:
            lista = self.notes
        for note in lista:
            self.listbox.insert(tk.END, f"[{note['categorie']}] {note['text']} - {note['data_ora']}")
        self.status_var.set(f"{len(self.notes)} notițe salvate")

    def delete_notite(self):
        selectie = self.listbox.curselection()
        if not selectie:
            messagebox.showwarning("Avertisment", "Nu ai selectat nicio notiță")
            return
        if messagebox.askyesno("Confirmare", "Sigur vrei să ștergi această notiță?"):
            index = selectie[0]
            self.notes.pop(index)
            self.sort_notes()
            self.filter_notes()

    def save_notite(self):
        try:
            with sqlite3.connect("notite.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notite (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text TEXT NOT NULL,
                        categorie TEXT,
                        data_ora TEXT
                    )
                """)
                cursor.execute("DELETE FROM notite")
                cursor.executemany(
                    "INSERT INTO notite (text, categorie, data_ora) VALUES (?, ?, ?)",
                    [(n["text"], n["categorie"], n["data_ora"]) for n in self.notes]
                )
                conn.commit()
        except sqlite3.OperationalError as e:
            messagebox.showerror("Eroare DB", f"Baza de date este blocată: {e}")

    def load_notite(self):
        self.notes.clear()
        with sqlite3.connect("notite.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notite (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    categorie TEXT,
                    data_ora TEXT
                )
            """)
            conn.commit()
            cursor.execute("SELECT text, categorie, data_ora FROM notite")
            rows = cursor.fetchall()
        for text, categorie, data_ora in rows:
            self.notes.append({
                "text": text,
                "categorie": categorie,
                "data_ora": data_ora if data_ora else ""
            })
        self.sort_notes()

    def edit_note(self):
        if self.edit_index is None:
            messagebox.showwarning("Avertisment", "Nu editezi nicio notiță acum")
            return
        noul_text = self.entry_notite.get().strip()
        if not noul_text:
            messagebox.showwarning("Avertisment", "Textul nu poate fi gol")
            return
        self.notes[self.edit_index]["text"] = noul_text
        self.notes[self.edit_index]["categorie"] = self.categorie_var.get()
        self.edit_index = None
        self.entry_notite.delete(0, tk.END)
        self.sort_notes()
        self.filter_notes()
        messagebox.showinfo("Succes", "Notița a fost modificată")

    def filter_notes(self, event=0):
        query = self.search_var.get().strip().lower()
        if query == "caută...":
            query = ""
        selected_cat = self.filter_categorie_var.get().strip()
        lista_filtrata = [
            n for n in self.notes
            if (query in n["text"].lower()) and
            (selected_cat == "Toate" or n["categorie"].strip() == selected_cat)
        ]
        self.update_listbox(lista_filtrata)

    def sort_notes(self):
        self.notes.sort(key=lambda n: n["text"].lower())
        self.update_listbox()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        btn = self.frame_butoane.winfo_children()[-1]
        btn.configure(text="☀️ Mod Luminos" if self.dark_mode else "🌙 Mod Întunecat")

    def start_edit(self):
        selectie = self.listbox.curselection()
        if not selectie:
            messagebox.showwarning("Avertisment", "Nu ai selectat nicio notiță pentru editare")
            return
        self.edit_index = selectie[0]
        nota = self.notes[self.edit_index]
        self.entry_notite.delete(0, tk.END)
        self.entry_notite.insert(0, nota["text"])
        self.categorie_var.set(nota.get("categorie", "General"))

    def on_exit(self):
        try:
            self.save_notite()
        except sqlite3.OperationalError:
            pass
        finally:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Manager Notițe")
    root.geometry("700x600")
    root.resizable(False, False)
    app = ManagerNotite(root)
    root.mainloop()
