import tkinter as tk
from PIL import Image, ImageTk

class Pyro_SimpleTK:
    def __init__(self, width=400, height=300, bg="white", title="SimpleTK",
                 hide_topbar=False, title_color="gray", show_mbox=True):
        self.root = tk.Tk()
        self.bg = bg
        self.root.configure(bg=bg)

        self.original_width = width
        self.original_height = height
        self.root.geometry(f"{width}x{height}+100+100")
        self.root.update_idletasks()

        self.widgets = []
        self.show_mbox = show_mbox
        self.mbox = None

        # Track maximize/restore states
        self.is_maximized = False
        self.is_minimized = False

        if hide_topbar:
            self.root.overrideredirect(True)
            self._add_custom_titlebar(title)
        else:
            self.root.title(title)

    def _add_custom_titlebar(self, title):
        self.title_frame = tk.Frame(self.root, bg="gray")
        self.title_frame.pack(side="top", fill="x")

        # Optional draggable MBox
        if self.show_mbox:
            self.mbox = tk.Label(self.title_frame, bg="green", width=2)
            self.mbox.pack(side="left", padx=2, pady=2)
            self.mbox.bind("<ButtonPress-1>", self.start_move)
            self.mbox.bind("<B1-Motion>", self.do_move)

        # Title label
        self.title_label = tk.Label(self.title_frame, text=title, bg="gray", fg="white")
        self.title_label.pack(side="left", padx=5, pady=2)

        # Buttons container
        self.btn_frame = tk.Frame(self.title_frame, bg="gray")
        self.btn_frame.pack(side="right", padx=2)

        # Maximize button
        self.max_btn = tk.Button(self.btn_frame, text="□", bg="lightgray", fg="black", command=self.maximize)
        self.max_btn.pack(side="left", padx=1)

        # Restore button
        self.restore_btn = tk.Button(self.btn_frame, text="🗗", bg="lightgray", fg="black", command=self.restore)
        self.restore_btn.pack(side="left", padx=1)

        # Minimize button
        self.min_btn = tk.Button(self.btn_frame, text="-", bg="yellow", fg="black", command=self.minimize)
        self.min_btn.pack(side="left", padx=1)

        # Close button
        self.close_btn = tk.Button(self.btn_frame, text="✖", bg="red", fg="white", command=self.close)
        self.close_btn.pack(side="left", padx=1)

    # Dragging functions for MBox
    def start_move(self, event):
        self.x_offset = event.x
        self.y_offset = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.x_offset
        y = self.root.winfo_pointery() - self.y_offset
        self.root.geometry(f"+{x}+{y}")

    # Center helper
    def _center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # Maximize
    def maximize(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.is_maximized = True
        self.is_minimized = False

    # Restore to original size
    def restore(self):
        self._center_window(self.original_width, self.original_height)
        self.is_maximized = False
        self.is_minimized = False

    # Minimize (small centered window)
    def minimize(self):
        mini_width = self.original_width // 3
        mini_height = self.original_height // 3
        self._center_window(mini_width, mini_height)
        self.is_minimized = True
        self.is_maximized = False

    # Show/Hide MBox dynamically
    def show_mbox_box(self):
        if not self.mbox:
            self.mbox = tk.Label(self.title_frame, bg="green", width=2)
            self.mbox.pack(side="left", padx=2, pady=2)
            self.mbox.bind("<ButtonPress-1>", self.start_move)
            self.mbox.bind("<B1-Motion>", self.do_move)

    def hide_mbox_box(self):
        if self.mbox:
            self.mbox.destroy()
            self.mbox = None

    # Add widgets
    def add_label(self, name, text, fg="black", bg=None):
        bg = bg or self.bg
        lbl = tk.Label(self.root, text=text, fg=fg, bg=bg)
        lbl.pack(padx=5, pady=5)
        self.widgets.append((name, lbl))
        return lbl

    def add_button(self, name, text, command=None, fg="black", bg=None):
        bg = bg or self.bg
        btn = tk.Button(self.root, text=text, fg=fg, bg=bg, command=command)
        btn.pack(padx=5, pady=5)
        self.widgets.append((name, btn))
        return btn

    def add_image(self, name, path, width=None, height=None):
        img = Image.open(path)
        if width and height:
            img = img.resize((width, height))
        photo = ImageTk.PhotoImage(img)
        lbl = tk.Label(self.root, image=photo, bg=self.bg)
        lbl.image = photo
        lbl.pack(padx=5, pady=5)
        self.widgets.append((name, lbl))
        return lbl

    # Close window
    def close(self):
        print("Closing window...")
        self.root.destroy()

    # Run main loop
    def run(self):
        self.root.mainloop()
