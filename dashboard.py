from tkinter import ttk
from ttkthemes import ThemedTk

class Dashboard:
    def __init__(self, user_id, database):
        self.root = ThemedTk(theme="equilux")
        self.root.title("AWS Quiz Dashboard")
        self.root.geometry("800x600")
        self.user_id = user_id
        self.database = database
        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.configure('Custom.TButton', padding=10, background='#007BFF', foreground='white', font=('Helvetica', 12, 'bold'), borderwidth=0)
        style.map('Custom.TButton', background=[('active', '#0056b3')])
        style.configure('Card.TFrame', background='#444', borderwidth=2, relief='raised')
        style.configure('Card.TLabel', background='#444', foreground='white', font=('Helvetica', 12))

    def setup_ui(self):
        self.bg_canvas = tk.Canvas(self.root, bg='#333', highlightthickness=0)
        self.bg_canvas.place(relwidth=1, relheight=1)
        self.bg_canvas.create_rectangle(0, 0, 800, 600, fill='#333', outline='')
        main_frame = ttk.Frame(self.bg_canvas, padding="20")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(main_frame, text="Welcome to AWS Quiz", font=('Helvetica', 24, 'bold'), foreground='white').pack(pady=20)
        scores_frame = ttk.LabelFrame(main_frame, text="Previous Scores", padding="10", style='Card.TFrame')
        scores_frame.pack(fill="both", expand=True, pady=20)
        scores = self.database.get_user_scores(self.user_id)
        if scores:
            for score, total, date in scores:
                score_text = f"Score: {score}/{total} - Date: {date}"
                card = ttk.Frame(scores_frame, style='Card.TFrame')
                card.pack(fill="x", pady=5, padx=5)
                ttk.Label(card, text=score_text, style='Card.TLabel').pack(pady=5)
        else:
            ttk.Label(scores_frame, text="No previous attempts", style='Card.TLabel').pack(pady=5)
        ttk.Button(main_frame, text="Start New Quiz", style='Custom.TButton', command=self.start_quiz).pack(pady=20)
        ttk.Button(main_frame, text="Quit", style='Custom.TButton', command=self.root.destroy).pack(pady=10)

    def start_quiz(self):
        self.root.destroy()
        quiz_root = ThemedTk(theme="equilux")
        quiz_app = MCQApp(quiz_root, self.user_id, self.database)
        quiz_root.mainloop()

    def run(self):
        self.root.mainloop()
