import tkinter as tk
from tkinter import messagebox
import ctypes
import time


def press_ctrl_v():
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
        self.root.overrideredirect(True)   # removes white Windows title bar
        self.root.geometry("210x360+200+200")
        self.root.configure(bg="#252525")
        self.root.attributes("-topmost", True)

        self.pinned = False
        self.phrases = []

        self.build_ui()

    def build_ui(self):
        self.header = tk.Frame(self.root, bg="#0078d7", height=42)
        self.header.pack(fill="x")

        self.title = tk.Label(
            self.header,
            text="Clipboard",
            fg="white",
            bg="#0078d7",
            font=("Segoe UI", 12)
        )
        self.title.pack(side="left", padx=8)

        self.close_btn = tk.Button(
            self.header,
            text="×",
            fg="white",
            bg="#0078d7",
            activebackground="#005fa3",
            activeforeground="white",
            bd=0,
            font=("Segoe UI", 16),
            command=self.root.destroy
        )
        self.close_btn.pack(side="right", padx=4)

        self.pin_btn = tk.Button(
            self.header,
            text="📌",
            fg="white",
            bg="#0078d7",
            activebackground="#005fa3",
            activeforeground="white",
            bd=0,
            font=("Segoe UI", 11),
            command=self.toggle_pin
        )
        self.pin_btn.pack(side="right")

        # draggable header
        for widget in (self.header, self.title):
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)

        self.button_frame = tk.Frame(self.root, bg="#252525")
        self.button_frame.pack(fill="both", expand=True)

        self.new_btn = tk.Button(
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
        self.new_btn.pack(fill="x", padx=5, pady=5)

    def toggle_pin(self):
        self.pinned = not self.pinned
        self.pin_btn.configure(bg="#00a86b" if self.pinned else "#0078d7")

    def start_move(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.drag_x
        y = self.root.winfo_pointery() - self.drag_y
        self.root.geometry(f"+{x}+{y}")

    def open_new_phrase_window(self):
        win = tk.Toplevel(self.root)
        win.title("New Phrase")
        win.geometry("520x460")
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
            wrap="word",
            height=12
        )
        content_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        button_area = tk.Frame(win, bg="#252525")
        button_area.pack(fill="x", padx=15, pady=(0, 15))

        def save_phrase():
            title = title_entry.get().strip()
            content = content_text.get("1.0", "end-1c")

            if not title:
                messagebox.showwarning("Missing title", "Please enter a title.")
                return

            if not content.strip():
                messagebox.showwarning("Missing content", "Please enter phrase content.")
                return

            self.phrases.append({"title": title, "content": content})
            self.add_phrase_button(title, content)
            win.destroy()

        save_btn = tk.Button(
            button_area,
            text="Save Phrase",
            font=("Segoe UI", 11),
            bg="#0078d7",
            fg="white",
            activebackground="#005fa3",
            activeforeground="white",
            bd=0,
            command=save_phrase
        )
        save_btn.pack(side="right", ipadx=18, ipady=6)

        cancel_btn = tk.Button(
            button_area,
            text="Cancel",
            font=("Segoe UI", 11),
            bg="#444444",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            bd=0,
            command=win.destroy
        )
        cancel_btn.pack(side="right", padx=(0, 8), ipadx=18, ipady=6)

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
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()

        if not self.pinned:
            self.root.withdraw()

        time.sleep(0.15)
        press_ctrl_v()

        if self.pinned:
            self.root.deiconify()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardApp(root)
    root.mainloop()