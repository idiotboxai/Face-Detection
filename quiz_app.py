import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import mediapipe as mp
from PIL import Image, ImageTk
import time
from threading import Thread
import queue
from ttkthemes import ThemedTk

class MCQApp:
    def __init__(self, root, user_id, database):
        self.root = root
        self.user_id = user_id
        self.database = database
        self.root.title("AWS Quiz - Hand Gesture Recognition")
        self.root.geometry("1200x800")
        self.setup_styles()
        self.setup_ui()
        self.setup_video()
        self.setup_game_state()

    def setup_styles(self):
        style = ttk.Style()
        style.configure('Quiz.TLabel', font=('Helvetica', 16), padding=10, foreground='white', background='#333')
        style.configure('Option.TLabel', font=('Helvetica', 14), padding=5, foreground='white', background='#444')
        style.configure('Score.TLabel', font=('Helvetica', 14, 'bold'), foreground='#007BFF', background='#333')
        style.configure('Feedback.TLabel', font=('Helvetica', 14, 'bold'), background='#333')

    def setup_ui(self):
        self.bg_canvas = tk.Canvas(self.root, bg='#333', highlightthickness=0)
        self.bg_canvas.place(relwidth=1, relheight=1)
        self.bg_canvas.create_rectangle(0, 0, 1200, 800, fill='#333', outline='')
        self.main_container = ttk.Frame(self.bg_canvas, padding="20")
        self.main_container.pack(fill="both", expand=True)
        self.quiz_frame = ttk.Frame(self.main_container)
        self.quiz_frame.pack(side="left", fill="both", expand=True, padx=10)
        self.question_frame = ttk.LabelFrame(self.quiz_frame, text="Question", padding="10", style='Card.TFrame')
        self.question_frame.pack(fill="x", pady=10)
        self.question_label = ttk.Label(self.question_frame, text="", wraplength=500, style='Quiz.TLabel')
        self.question_label.pack(pady=10)
        self.options_frame = ttk.LabelFrame(self.quiz_frame, text="Options", padding="10", style='Card.TFrame')
        self.options_frame.pack(fill="x", pady=10)
        self.option_labels = []
        for _ in range(4):
            label = ttk.Label(self.options_frame, text="", wraplength=500, style='Option.TLabel')
            label.pack(pady=5)
            self.option_labels.append(label)
        self.feedback_label = ttk.Label(self.quiz_frame, text="", style='Feedback.TLabel')
        self.feedback_label.pack(pady=10)
        self.score_label = ttk.Label(self.quiz_frame, text="Score: 0", style='Score.TLabel')
        self.score_label.pack(pady=5)
        self.video_frame = ttk.LabelFrame(self.main_container, text="Hand Gesture Recognition", padding="10", style='Card.TFrame')
        self.video_frame.pack(side="right", fill="both", expand=True, padx=10)
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(pady=10)
        instruction_text = """
        Instructions:
        1. Show your hand to the camera
        2. Hold up fingers to select your answer:
           - 1 finger for option 1
           - 2 fingers for option 2
           - 3 fingers for option 3
           - 4 fingers for option 4
        3. Hold the gesture steady for a moment
        """
        self.instruction_label = ttk.Label(self.video_frame, text=instruction_text, wraplength=400)
        self.instruction_label.pack(pady=10)

    def setup_video(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    def setup_game_state(self):
        self.current_question = 0
        self.score = 0
        self.last_detected_fingers = 0
        self.answer_locked = False
        self.update_question()

    def count_fingers(self, hand_landmarks):
        finger_tips = [8, 12, 16, 20]
        finger_count = 0
        if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
            finger_count += 1
        for tip_id in finger_tips:
            if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
                finger_count += 1
        return min(finger_count, 4)

    def video_capture_thread(self):
        while True:
            ret, frame = self.cap.read()
            if ret:
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                self.frame_queue.put(frame)
            else:
                break

    def process_frame(self):
        try:
            frame = self.frame_queue.get_nowait()
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            current_time = time.time()
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    if current_time - self.last_answer_time > self.answer_cooldown:
                        finger_count = self.count_fingers(hand_landmarks)
                        if finger_count > 0:
                            self.check_answer(finger_count - 1)
                            self.last_answer_time = current_time
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        except queue.Empty:
            pass
        finally:
            self.root.after(10, self.process_frame)

    def update_question(self):
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            self.question_label.config(text=question["question"])
            for i, option in enumerate(question["options"]):
                self.option_labels[i].config(text=f"{i+1}. {option}")
            self.answer_locked = False
            self.feedback_label.config(text="")
        else:
            self.show_final_score()

    def check_answer(self, answer_index):
        if not self.answer_locked and self.current_question < len(self.questions):
            correct_answer = self.questions[self.current_question]["correct"]
            if answer_index == correct_answer:
                self.score += 1
                self.feedback_label.config(text="Correct!", foreground="green")
            else:
                self.feedback_label.config(text="Incorrect!", foreground="red")
            self.score_label.config(text=f"Score: {self.score}")
            self.answer_locked = True
            self.root.after(2000, self.next_question)

    def next_question(self):
        self.current_question += 1
        self.update_question()

    def show_final_score(self):
        self.database.save_score(self.user_id, self.score, len(self.questions))
        message = f"Quiz completed!\nFinal score: {self.score}/{len(self.questions)}"
        messagebox.showinfo("Quiz Complete", message)
        self.cap.release()
        self.root.destroy()

    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()
