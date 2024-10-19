import tkinter as tk
import random
import webbrowser
from tkinter import messagebox


class WordGuessGame:
    def __init__(self, master, filename='words5.txt'):
        self.master = master
        self.words = self.load_words(filename)
        self.secret_word = ''
        self.attempts = 5
        self.current_attempt = 0
        self.result_labels = []
        self.timer_label = None
        self.time_left = 120  # Czas 2 minuty (120 sekund)
        self.timer_active = False
        self.score = 0  # Licznik punktów
        self.correct_letters = [False] * 5  # Tablica śledząca odgadnięte litery
        self.rekord = 0

        self.create_widgets()
        self.start_new_game()

    def load_words(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                words = [line.strip().lower() for line in file if len(line.strip()) == 5]
            return words
        except FileNotFoundError:
            print(f"Błąd: Nie znaleziono pliku '{filename}'.")
            exit(1)

    def create_widgets(self):
        self.master.configure(bg='blue')

        self.attempt_frame = tk.Frame(self.master, bg='blue')
        self.attempt_frame.pack(pady=10)

        # Utwórz etykiety dla prób
        for attempt in range(5):
            row_labels = []
            for letter in range(5):
                label = tk.Label(self.attempt_frame, text=" ", font=("Helvetica", 24), width=5, bg='blue',
                                 borderwidth=2, relief='solid', fg='white')
                label.grid(row=attempt, column=letter)
                row_labels.append(label)
            self.result_labels.append(row_labels)

        self.entry = tk.Entry(self.master, font=("Helvetica", 24), width=25)
        self.entry.pack(pady=10)

        self.confirm_button = tk.Button(self.master,bg='green', text="Potwierdź", width=25, command=self.check_guess, font=("Helvetica", 16))
        self.confirm_button.pack(pady=10)

        self.hint_button = tk.Button(self.master, bg='#F0E68C', text="Podpowiedź", width=25, command=self.reveal_hint, font=("Helvetica", 16))
        self.hint_button.pack(pady=10)

        self.surrender_button = tk.Button(self.master, bg='coral', text="Poddaj się", width=25, command=self.surrender, font=("Helvetica", 16))
        self.surrender_button.pack(pady=10)

        self.restart_button = tk.Button(self.master, bg='royalblue', text="Rozpocznij grę od nowa", width=25, command=self.start_new_game,
                                        font=("Helvetica", 16))
        self.restart_button.pack(pady=10)

        self.timer_label = tk.Label(self.master, text="Pozostały czas: 2:00", font=("Helvetica", 16), bg='blue', fg='red')
        self.timer_label.pack(pady=10)

        self.message_label = tk.Label(self.master, text="", font=("Helvetica", 16), bg='blue', fg='white')
        self.message_label.pack(pady=10)

        self.info_label = tk.Label(self.master, text="", font=("Helvetica", 16), bg='blue', fg='white')
        self.info_label.pack(pady=10)

        self.points_label = tk.Label(self.master, text=f"Punkty: {self.score}", font=("Helvetica", 16), bg='blue', fg='yellow')
        self.points_label.pack(pady=10)

    def start_new_game(self):
        self.secret_word = random.choice(self.words).upper()
        self.attempts = 5
        self.current_attempt = 0
        self.time_left = 120  # Resetuj czas
        self.timer_active = True
        self.correct_letters = [False] * 5  # Resetuj tablicę odgadniętych liter
        self.clear_labels()
        self.entry.config(state=tk.NORMAL)
        self.confirm_button.config(state=tk.NORMAL)
        self.hint_button.config(state=tk.NORMAL)
        self.surrender_button.config(state=tk.NORMAL)
        self.entry.delete(0, tk.END)
        self.message_label.config(text="")
        self.info_label.config(text=f"Pierwsza litera: '{self.secret_word[0]}'")
        self.update_timer()

    def clear_labels(self):
        for row_labels in self.result_labels:
            for label in row_labels:
                label.config(text=" ", fg='white', bg='blue')

    def check_guess(self):
        guess = self.entry.get().lower()
        if len(guess) != 5:
            self.message_label.config(text="Proszę wpisać pięcioliterowe słowo.")
            return

        if guess not in self.words:
            self.message_label.config(text="Słowo nie występuje w słowniku. -5 sekund")
            self.time_left -= 5
            return

        if guess.upper() == self.secret_word:
            self.message_label.config(text="Brawo! Odgadłeś słowo!")
            self.update_labels(guess.upper())
            self.update_score()  # Dodaj punkty
            self.restart_button.config(text="Graj dalej")
            self.zapytaj_o_wyszukiwanie(self.secret_word)
            self.end_game()
            return

        self.update_labels(guess.upper())

        self.current_attempt += 1
        self.attempts -= 1

        if self.attempts == 0:
            self.message_label.config(text=f"Niestety, przegrałeś! Szukane słowo to: {self.secret_word}")
            self.reset_score()  # Resetuj punkty
            self.reveal_secret_word()
            self.end_game()
        else:
            self.entry.delete(0, tk.END)
            self.message_label.config(text=f"Pozostałe próby: {self.attempts}")

    def update_labels(self, guess):
        secret_word_list = list(self.secret_word)
        guessed_letters = [''] * 5

        for i, letter in enumerate(guess):
            if letter == self.secret_word[i]:
                self.result_labels[self.current_attempt][i].config(text=letter, bg='lime', fg='black')
                guessed_letters[i] = letter
                secret_word_list[i] = None
                self.correct_letters[i] = True  # Oznacz literę jako poprawnie odgadniętą

        for i, letter in enumerate(guess):
            if guessed_letters[i] == '':
                if letter in secret_word_list:
                    self.result_labels[self.current_attempt][i].config(text=letter, bg='blue', fg='magenta')
                    secret_word_list[secret_word_list.index(letter)] = None
                else:
                    self.result_labels[self.current_attempt][i].config(text=letter, bg='blue', fg='white')

    def reveal_hint(self):
        # Znajdź litery, które nie zostały jeszcze poprawnie odgadnięte
        unrevealed_indices = [i for i, correct in enumerate(self.correct_letters) if not correct]

        # Jeśli są jeszcze litery do odkrycia
        if unrevealed_indices:
            reveal_index = random.choice(unrevealed_indices)
            correct_letter = self.secret_word[reveal_index]

            # Odkryj poprawną literę na wskazanej pozycji
            self.result_labels[self.current_attempt][reveal_index].config(text=correct_letter, fg='black', bg="lime")
            self.correct_letters[reveal_index] = True  # Oznacz literę jako poprawnie odgadniętą
            self.message_label.config(text=f"Odkryta litera: {correct_letter}")
        else:
            self.message_label.config(text="Wszystkie litery zostały już odkryte.")

        # Dezaktywuj przycisk podpowiedzi, aby nie można było użyć go ponownie
        self.hint_button.config(state=tk.DISABLED)

    def surrender(self):
        self.message_label.config(text=f"Poddałeś się. Szukane słowo to: {self.secret_word}")
        self.reveal_secret_word()
        self.reset_score()  # Resetuj punkty
        self.end_game()

    def reveal_secret_word(self):
        for i, letter in enumerate(self.secret_word):
            self.result_labels[self.current_attempt][i].config(text=letter, bg='coral', fg='black')
        self.zapytaj_o_wyszukiwanie(self.secret_word)

    def update_timer(self):
        if self.time_left > 0 and self.timer_active:
            minutes, seconds = divmod(self.time_left, 60)
            self.timer_label.config(text=f"Pozostały czas: {minutes}:{seconds:02d}")
            self.time_left -= 1
            self.master.after(1000, self.update_timer)
        elif self.time_left <= 0:
            self.message_label.config(text=f"Czas minął! Szukane słowo to: {self.secret_word}")
            self.timer_label.config(text=f"Pozostały czas: 00:00")
            self.reveal_secret_word()
            self.reset_score()  # Resetuj punkty
            self.end_game()

    def update_score(self):
        self.score += self.attempts  # Dodaj punkty za pozostałe próby
        self.points_label.config(text=f"Punkty: {self.score}")

    def reset_score(self):
        self.timer_label.config(text=f"UZYSKANY WYNIK: {self.score}")
        self.score = 0  # Zresetuj punkty
        self.points_label.config(text=f"Punkty: {self.score}")
        self.restart_button.config(text="Rozpocznij grę od nowa")

    def end_game(self):
        self.entry.config(state=tk.DISABLED)
        self.confirm_button.config(state=tk.DISABLED)
        self.hint_button.config(state=tk.DISABLED)
        self.surrender_button.config(state=tk.DISABLED)
        self.timer_active = False

    def wyszukaj_w_przegladarce(self, slowo):
        url = f"https://www.google.com/search?q={slowo}"
        webbrowser.open(url)

    def zapytaj_o_wyszukiwanie(self, slowo):
        odpowiedz = messagebox.askyesno("GOOGLE", f"Czy wyszukać znaczenie słowa {slowo}?")
        if odpowiedz:
            self.wyszukaj_w_przegladarce(slowo)
        else:
            return

root = tk.Tk()
root.title("GRA W PIEĆ RAZY PIĘĆ")
root.iconbitmap("ico.ico")
game = WordGuessGame(root)
root.bind('<Return>', lambda event: game.check_guess())
root.mainloop()
