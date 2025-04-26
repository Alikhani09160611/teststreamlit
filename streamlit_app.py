import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import re
import sys
from pyvirtualdisplay import Display

class ArduinoSimulator:
    def __init__(self, master):
        self.master = master
        master.title("شبیه‌ساز هوشمند آردوینو ESP32")
        master.geometry("850x650")

        # تنظیمات پیشفرض
        self.DEFAULT_SSID = "HydrogenFi-5G"
        self.DEFAULT_PASSWORD = "Secure@H2Face123"
        self.LED_COLORS = ["#FF0000", "#00FF00"]
        
        # وضعیت سامانه
        self.simulation_active = False
        self.wifi_connected = False
        self.led_states = [False, False]
        
        # ایجاد کامپوننت‌ها
        self.create_gui()
        self.log("🚀 سامانه با موفقیت راه‌اندازی شد")

    def create_gui(self):
        # بخش آپلود فایل
        upload_frame = ttk.LabelFrame(self.master, text="مدیریت فایل برنامه")
        upload_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Button(upload_frame, text="📤 آپلود فایل .ino", command=self.upload_ino).pack(pady=5)
        self.file_label = ttk.Label(upload_frame, text="📂 هیچ فایلی انتخاب نشده")
        self.file_label.pack()

        # بخش سخت‌افزار
        hw_frame = ttk.LabelFrame(self.master, text="شبیه‌سازی سخت‌افزاری")
        hw_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5)
        
        # LED ها
        self.leds = []
        for i in range(2):
            frame = tk.Frame(hw_frame)
            frame.pack(pady=10)
            canvas = tk.Canvas(frame, width=40, height=40, bg="black")
            self.leds.append(canvas.create_oval(5,5,35,35, fill="gray"))
            canvas.pack(side="left")
            ttk.Label(frame, text=f"💡 LED {i+1}", font=('Tahoma',10)).pack(side="left", padx=5)
        
        # دکمه‌ها
        ttk.Label(hw_frame, text="🎛 دکمه‌های TS22", font=('Tahoma',10,'bold')).pack(pady=5)
        btn_frame = tk.Frame(hw_frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text="🔄 تغییر LED 1", command=lambda: self.toggle_led(0)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 تغییر LED 2", command=lambda: self.toggle_led(1)).pack(side="left", padx=5)

        # ترمینال
        terminal_frame = ttk.LabelFrame(self.master, text="📟 ترمینال اجرا")
        terminal_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        self.terminal = tk.Text(terminal_frame, height=15, bg="black", fg="#00FF00", font=('Courier', 10))
        self.terminal.pack(fill="both", expand=True)

        # کنترل‌ها
        control_frame = ttk.Frame(self.master)
        control_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.start_btn = ttk.Button(control_frame, text="▶ شروع شبیه‌سازی", command=self.toggle_simulation)
        self.start_btn.pack(pady=5)
        
        self.wifi_status = ttk.Label(control_frame, text="📶 وضعیت اینترنت: قطع", foreground="red")
        self.wifi_status.pack()

    def upload_ino(self):
        file_path = filedialog.askopenfilename(filetypes=[("فایل آردوینو", "*.ino")])
        if file_path:
            try:
                self.modify_arduino_code(file_path)
                self.file_label.config(text=f"📁 {file_path.split('/')[-1]}")
                self.log("✅ فایل با موفقیت پردازش شد")
                messagebox.showinfo("موفق", "برنامه با تنظیمات جدید آماده است!")
            except Exception as e:
                messagebox.showerror("خطا", f"❌ پردازش فایل ناموفق:\n{str(e)}")

    def modify_arduino_code(self, path):
        with open(path, 'r+', encoding='utf-8') as f:
            code = f.read()
            code = re.sub(r'char\s*ssid\s*=\s*".*?";', f'char ssid = "{self.DEFAULT_SSID}";', code)
            code = re.sub(r'char\s*password\s*=\s*".*?";', f'char password = "{self.DEFAULT_PASSWORD}";', code)
            f.seek(0)
            f.write(code)
            f.truncate()

    def toggle_simulation(self):
        self.simulation_active = not self.simulation_active
        if self.simulation_active:
            threading.Thread(target=self.simulation_loop, daemon=True).start()
            self.start_btn.config(text="⏹ توقف شبیه‌سازی")
            self.log("🚦 شبیه‌سازی فعال شد")
        else:
            self.start_btn.config(text="▶ شروع شبیه‌سازی")
            self.log("🛑 شبیه‌سازی متوقف شد")

    def simulation_loop(self):
        while self.simulation_active:
            self.wifi_connected = not self.wifi_connected
            status_text = "🌐 متصل" if self.wifi_connected else "❌ قطع"
            color = "green" if self.wifi_connected else "red"
            self.wifi_status.config(text=f"📶 وضعیت اینترنت: {status_text}", foreground=color)
            time.sleep(2)

    def toggle_led(self, led_num):
        self.led_states[led_num] = not self.led_states[led_num]
        color = "yellow" if self.led_states[led_num] else "gray"
        hw_frame = self.master.winfo_children()[2]
        canvas = hw_frame.winfo_children()[led_num].winfo_children()[0]
        canvas.itemconfig(self.leds[led_num], fill=color)
        self.log(f"💡 LED {led_num+1} {'✅ فعال' if self.led_states[led_num] else '❌ غیرفعال'} شد")

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.terminal.insert("end", f"[{timestamp}] {message}\n")
        self.terminal.see("end")
        self.terminal.update_idletasks()

    def on_close(self):
        if messagebox.askokcancel("خروج", "آیا مطمئنید می‌خواهید خارج شوید؟"):
            self.simulation_active = False
            self.master.destroy()

if __name__ == "__main__":
    # تنظیمات ویژه برای Hugging Face Spaces
    if 'linux' in sys.platform:
        display = Display(visible=0, size=(800, 600))
        display.start()
    
    root = tk.Tk()
    app = ArduinoSimulator(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

    if 'linux' in sys.platform:
        display.stop()
