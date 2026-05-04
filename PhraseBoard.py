import tkinter as tk
from tkinter import messagebox
import ctypes
import time


# ---------- Windows Ctrl+V paste ----------
def press_ctrl_v():
    # Virtual key codes
    VK_CONTROL = 0x11
    VK_V = 0x56
    KEYEVENTF_KEYUP = 0x0002

    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_V, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


class ClipboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phrases")
        self.root.geometry("210x360")
        self.root.configure(bg="#252525")
        self.root.attributes("-topmost", True)

        self.phrases = []

        self.build_ui()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0078d7", height=40)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="Clipboard",
            fg="white",
            bg="#0078d7",
            font=("Segoe UI", 12)
        )
        title.pack(side="left", padx=10)

        close_btn = tk.Button(
            header,
            text="×",
            fg="white",
            bg="#0078d7",
            bd=0,
            font=("Segoe UI", 16),
            command=self.root.destroy
        )
        close_btn.pack(side="right", padx=5)

        # Make window draggable
        header.bind("<Button-1>", self.start_move)
        header.bind("<B1-Motion>", self.do_move)
        title.bind("<Button-1>", self.start_move)
        title.bind("<B1-Motion>", self.do_move)

        # Phrase buttons area
        self.button_frame = tk.Frame(self.root, bg="#252525")
        self.button_frame.pack(fill="both", expand=True)

        # New phrase button
        new_btn = tk.Button(
            self.root,
            text="New phrase...",
            anchor="w",
            fg="white",
            bg="#252525",
            activebackground="#333333",
            activeforeground="white",
            bd=0,
            font=("Segoe UI", 11),
            command=self.open_new_phrase_window
        )
        new_btn.pack(fill="x", padx=5, pady=5)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.x
        y = self.root.winfo_pointery() - self.y
        self.root.geometry(f"+{x}+{y}")

    def open_new_phrase_window(self):
        win = tk.Toplevel(self.root)
        win.title("New Phrase")
        win.geometry("520x420")
        win.configure(bg="#252525")
        win.attributes("-topmost", True)

        tk.Label(
            win,
            text="Title",
            fg="white",
            bg="#252525",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        title_entry = tk.Entry(
            win,
            font=("Segoe UI", 11),
            bg="#1e1e1e",
            fg="white",
            insertbackground="white"
        )
        title_entry.pack(fill="x", padx=15)

        tk.Label(
            win,
            text="Phrase content",
            fg="white",
            bg="#252525",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        content_text = tk.Text(
            win,
            font=("Segoe UI", 11),
            bg="#1e1e1e",
            fg="white",
            insertbackground="white",
            wrap="word"
        )
        content_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        def save_phrase():
            title = title_entry.get().strip()
            content = content_text.get("1.0", "end-1c")

            if not title:
                messagebox.showwarning("Missing title", "Please enter a title.")
                return

            if not content:
                messagebox.showwarning("Missing content", "Please enter phrase content.")
                return

            self.phrases.append({
                "title": title,
                "content": content
            })

            self.add_phrase_button(title, content)
            win.destroy()

        save_btn = tk.Button(
            win,
            text="Save Phrase",
            font=("Segoe UI", 11),
            bg="#0078d7",
            fg="white",
            bd=0,
            command=save_phrase
        )
        save_btn.pack(fill="x", padx=15, pady=(0, 15))

    def add_phrase_button(self, title, content):
        btn = tk.Button(
            self.button_frame,
            text=title,
            anchor="w",
            fg="white",
            bg="#252525",
            activebackground="#333333",
            activeforeground="white",
            bd=0,
            font=("Segoe UI", 11),
            command=lambda: self.paste_phrase(content)
        )
        btn.pack(fill="x", padx=5, pady=2)

    def paste_phrase(self, content):
        # Put phrase into clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()

        # Small delay, then paste into active app
        self.root.withdraw()
        time.sleep(0.15)
        press_ctrl_v()
        self.root.deiconify()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardApp(root)
    root.mainloop()