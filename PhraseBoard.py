import tkinter as tk
from tkinter import messagebox
import ctypes
import os
import time


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def press_ctrl_v():
    VK_CONTROL = 0x11
    VK_V = 0x56
    KEYUP = 0x0002

    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_V, 0, 0, 0)
    user32.keybd_event(VK_V, 0, KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYUP, 0)


def get_window_pid(hwnd):
    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


class ClipboardApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.min_width = 220
        self.min_height = 300
        self.root.geometry("220x380+300+200")
        self.root.minsize(self.min_width, self.min_height)
        self.root.configure(bg="#252525")

        self.pinned = False
        self.last_target_hwnd = None
        self.my_pid = os.getpid()

        self.build_ui()
        self.track_last_active_window()

    def build_ui(self):
        # top blue bar
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

        close_btn = tk.Button(
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
        close_btn.pack(side="right", padx=4)

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

        for w in (self.header, self.title):
            w.bind("<Button-1>", self.start_move)
            w.bind("<B1-Motion>", self.do_move)

        # scrollable phrase list
        list_container = tk.Frame(self.root, bg="#252525")
        list_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            list_container,
            bg="#252525",
            highlightthickness=0
        )
        self.scrollbar = tk.Scrollbar(
            list_container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.button_frame = tk.Frame(self.canvas, bg="#252525")

        self.button_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.button_frame,
            anchor="nw"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self.resize_canvas_window)
        self.canvas.bind_all("<MouseWheel>", self.mouse_scroll)

        # fixed bottom area
        bottom = tk.Frame(self.root, bg="#252525")
        bottom.pack(fill="x")

        new_btn = tk.Button(
            bottom,
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
        new_btn.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        resize_grip = tk.Label(
            bottom,
            text="◢",
            fg="white",
            bg="#252525",
            cursor="size_nw_se"
        )
        resize_grip.pack(side="right", padx=4)

        resize_grip.bind("<Button-1>", self.start_resize)
        resize_grip.bind("<B1-Motion>", self.do_resize)

    def resize_canvas_window(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def mouse_scroll(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def toggle_pin(self):
        self.pinned = not self.pinned
        self.root.attributes("-topmost", self.pinned)
        self.pin_btn.configure(bg="#00a86b" if self.pinned else "#0078d7")

    def start_move(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.drag_x
        y = self.root.winfo_pointery() - self.drag_y
        self.root.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self.start_w = self.root.winfo_width()
        self.start_h = self.root.winfo_height()
        self.start_x = event.x_root
        self.start_y = event.y_root

    def do_resize(self, event):
        new_w = max(self.min_width, self.start_w + event.x_root - self.start_x)
        new_h = max(self.min_height, self.start_h + event.y_root - self.start_y)
        self.root.geometry(f"{new_w}x{new_h}")

    def track_last_active_window(self):
        hwnd = user32.GetForegroundWindow()

        if hwnd:
            pid = get_window_pid(hwnd)

            # save only windows that are NOT this clipboard app
            if pid != self.my_pid:
                self.last_target_hwnd = hwnd

        self.root.after(300, self.track_last_active_window)
    def open_new_phrase_window(self):
        win = tk.Toplevel(self.root)
        win.title("New Phrase")
        win.geometry("520x460")
        win.minsize(420, 360)
        win.configure(bg="#252525")
        win.attributes("-topmost", True)

        main = tk.Frame(win, bg="#252525")
        main.pack(fill="both", expand=True)

        tk.Label(
            main,
            text="Title",
            fg="white",
            bg="#252525",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        title_entry = tk.Entry(
            main,
            font=("Segoe UI", 11),
            bg="#1e1e1e",
            fg="white",
            insertbackground="white"
        )
        title_entry.pack(fill="x", padx=15)

        tk.Label(
            main,
            text="Phrase content",
            fg="white",
            bg="#252525",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        content_text = tk.Text(
            main,
            font=("Segoe UI", 11),
            bg="#1e1e1e",
            fg="white",
            insertbackground="white",
            wrap="word",
            height=10
        )
        content_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        button_area = tk.Frame(win, bg="#252525")
        button_area.pack(fill="x", side="bottom", padx=15, pady=(0, 15))

        def save_phrase():
            title = title_entry.get().strip()
            content = content_text.get("1.0", "end-1c")

            if not title:
                messagebox.showwarning("Missing title", "Please enter a title.")
                return

            if not content.strip():
                messagebox.showwarning("Missing content", "Please enter phrase content.")
                return

            self.add_phrase_button(title, content)
            win.destroy()

        save_btn = tk.Button(
            button_area,
            text="Save Phrase",
            bg="#0078d7",
            fg="white",
            activebackground="#005fa3",
            activeforeground="white",
            bd=0,
            font=("Segoe UI", 11),
            command=save_phrase
        )
        save_btn.pack(side="right", ipadx=18, ipady=6)

        cancel_btn = tk.Button(
            button_area,
            text="Cancel",
            bg="#444444",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            bd=0,
            font=("Segoe UI", 11),
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

        target = self.last_target_hwnd

        # Hide briefly only if unpinned
        if not self.pinned:
            self.root.withdraw()

        time.sleep(0.15)

        if target:
            user32.SetForegroundWindow(target)
            time.sleep(0.15)

        press_ctrl_v()

        # Bring clipboard back if unpinned
        if not self.pinned:
            time.sleep(0.1)
            self.root.deiconify()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardApp(root)
    root.mainloop()