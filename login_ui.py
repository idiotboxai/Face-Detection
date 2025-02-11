import tkinter as tk
from tkinter import ttk, messagebox
import re
from ttkthemes import ThemedTk

class LoginUI:
    def __init__(self, database):
        self.root = ThemedTk(theme="equilux")
        self.root.title("AWS Quiz Login")
        self.root.geometry("800x600")
        self.database = database
        self.user_id = None
        self.setup_styles()
        self.create_login_frame()

    def setup_styles(self):
        style = ttk.Style()
        style.configure('Custom.TEntry', padding=10, fieldbackground='#2E2E2E', foreground='white', bordercolor='#444', lightcolor='#444', darkcolor='#444')
        style.configure('Custom.TButton', padding=10, background='#007BFF', foreground='white', font=('Helvetica', 12, 'bold'), borderwidth=0)
        style.map('Custom.TButton', background=[('active', '#0056b3')])
        style.configure('Title.TLabel', font=('Helvetica', 28, 'bold'), foreground='white', background='#333')
        style.configure('Subtitle.TLabel', font=('Helvetica', 14), foreground='#CCCCCC', background='#333')

    def create_login_frame(self):
        self.bg_canvas = tk.Canvas(self.root, bg='#333', highlightthickness=0)
        self.bg_canvas.place(relwidth=1, relheight=1)
        self.bg_canvas.create_rectangle(0, 0, 800, 600, fill='#333', outline='')
        self.main_frame = ttk.Frame(self.bg_canvas, padding="20", style='Custom.TFrame')
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(self.main_frame, text="AWS Quiz Login", style='Title.TLabel').pack(pady=20)
        self.login_frame = ttk.LabelFrame(self.main_frame, padding="20", style='Custom.TLabelframe')
        self.login_frame.pack(fill="both", expand=True)
        ttk.Label(self.login_frame, text="Username:", style='Subtitle.TLabel').pack(pady=5)
        self.username_entry = ttk.Entry(self.login_frame, style='Custom.TEntry', width=30)
        self.username_entry.pack(pady=5)
        ttk.Label(self.login_frame, text="Password:", style='Subtitle.TLabel').pack(pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="●", style='Custom.TEntry', width=30)
        self.password_entry.pack(pady=5)
        ttk.Button(self.login_frame, text="Login", style='Custom.TButton', command=self.handle_login).pack(pady=20)
        ttk.Button(self.login_frame, text="Register", style='Custom.TButton', command=self.show_register_frame).pack(pady=5)

    def create_register_frame(self):
        self.register_frame = ttk.LabelFrame(self.main_frame, padding="20", style='Custom.TLabelframe')
        self.register_frame.pack(fill="both", expand=True)
        ttk.Label(self.register_frame, text="Create Username:").pack(pady=5)
        self.reg_username = ttk.Entry(self.register_frame, style='Custom.TEntry', width=30)
        self.reg_username.pack(pady=5)
        ttk.Label(self.register_frame, text="Email:").pack(pady=5)
        self.reg_email = ttk.Entry(self.register_frame, style='Custom.TEntry', width=30)
        self.reg_email.pack(pady=5)
        ttk.Label(self.register_frame, text="Create Password:").pack(pady=5)
        self.reg_password = ttk.Entry(self.register_frame, show="●", style='Custom.TEntry', width=30)
        self.reg_password.pack(pady=5)
        ttk.Label(self.register_frame, text="Confirm Password:").pack(pady=5)
        self.reg_confirm = ttk.Entry(self.register_frame, show="●", style='Custom.TEntry', width=30)
        self.reg_confirm.pack(pady=5)
        ttk.Button(self.register_frame, text="Register", style='Custom.TButton', command=self.handle_register).pack(pady=20)
        ttk.Button(self.register_frame, text="Back to Login", style='Custom.TButton', command=self.show_login_frame).pack(pady=5)

    def show_register_frame(self):
        self.login_frame.pack_forget()
        self.create_register_frame()

    def show_login_frame(self):
        if hasattr(self, 'register_frame'):
            self.register_frame.pack_forget()
        self.login_frame.pack()

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def handle_register(self):
        username = self.reg_username.get()
        email = self.reg_email.get()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        if not all([username, email, password, confirm]):
            messagebox.showerror("Error", "All fields are required!")
            return
        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email format!")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long!")
            return
        if self.database.register_user(username, password, email):
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.show_login_frame()
        else:
            messagebox.showerror("Error", "Username or email already exists!")

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return
        user_id = self.database.verify_user(username, password)
        if user_id:
            self.user_id = user_id
            self.root.quit()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def run(self):
        self.root.mainloop()
        user_id = self.user_id
        if hasattr(self, 'root') and self.root:
            self.root.destroy()
        return user_id
