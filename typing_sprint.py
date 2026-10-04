"""
============================================================
                   ⚡ TYPING SPRINT ⚡
   A fast-paced interactive typing game in Python.
   Features:
     1. Main Menu / Quick Play
     2. Game Modes (Time Attack, Accuracy Streak, Sentence Sprint)
     3. Settings (Difficulty, Duration, Categories, High Scores)
     4. Quit
     5. Procedural Synthesizer Sound Effects
============================================================
"""

import time
import random
import os
import json
import threading

# Native Windows sound support without any external libraries
try:
    import winsound
    HAS_WINSOUND = True
except Exception:
    HAS_WINSOUND = False


def sfx_beep(freq, dur=40):
    """Play a single beep frequency in a background thread."""
    if not HAS_WINSOUND:
        return
    def _b():
        try:
            winsound.Beep(int(freq), int(dur))
        except Exception:
            pass
    threading.Thread(target=_b, daemon=True).start()


def sfx_melody(notes):
    """Play a sequence of notes [(freq, dur), ...] in a background thread."""
    if not HAS_WINSOUND:
        return
    def _m():
        try:
            for freq, dur in notes:
                winsound.Beep(int(freq), int(dur))
        except Exception:
            pass
    threading.Thread(target=_m, daemon=True).start()


# Sound Presets
def snd_correct():
    sfx_melody([(880, 45), (1320, 65)])

def snd_miss():
    sfx_melody([(340, 50), (220, 80)])

def snd_countdown():
    sfx_beep(650, 60)

def snd_go():
    sfx_melody([(784, 80), (1046, 120)])

def snd_streak_fail():
    sfx_melody([(440, 70), (330, 90), (180, 160)])

def snd_fanfare():
    sfx_melody([(523, 70), (659, 70), (784, 70), (1046, 180)])


# Word repositories by category & difficulty
WORD_BANKS = {
    "Easy": [
        "cat", "dog", "sun", "run", "sky", "red", "blue", "code", "fast",
        "game", "play", "jump", "tree", "book", "fire", "wind", "gold",
        "fish", "star", "moon", "hero", "path", "cool", "glow", "time"
    ],
    "Medium": [
        "python", "sprint", "speed", "keyboard", "challenge", "velocity",
        "screen", "player", "action", "reflex", "victory", "network",
        "program", "system", "dynamic", "focus", "battle", "target",
        "engine", "future", "matrix", "stream", "puzzle", "energy"
    ],
    "Hard": [
        "asynchronous", "polymorphism", "synchronization", "cryptography",
        "architecture", "multithreading", "encapsulation", "optimization",
        "troubleshooting", "infrastructure", "interoperability", "cybersecurity",
        "microservices", "computational", "telecommunications", "quantum"
    ],
    "Programming": [
        "variable", "function", "iteration", "boolean", "dictionary",
        "recursion", "exception", "algorithm", "compiler", "debugging",
        "terminal", "database", "parameter", "inheritance", "framework"
    ]
}

SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "Practice and consistency are the keys to high typing speed.",
    "Python is an intuitive and expressive programming language.",
    "Clean code always looks like it was written by someone who cares.",
    "Stay focused keep your fingers moving and beat your personal record.",
    "Great developers write code that humans can easily understand."
]

HIGH_SCORE_FILE = "highscores.json"

DEFAULT_SETTINGS = {
    "difficulty": "Medium",
    "duration": 30,  # seconds for timed sprint
    "category": "Medium"
}


def clear_screen():
    """Clear terminal screen cleanly across OS platforms."""
    os.system("cls" if os.name == "nt" else "clear")


def load_high_scores():
    """Load high scores from file using basic file handling."""
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_high_score(mode, wpm, accuracy, score):
    """Save a new score record to high scores file."""
    scores = load_high_scores()
    record = {
        "mode": mode,
        "wpm": round(wpm, 1),
        "accuracy": round(accuracy, 1),
        "score": score,
        "date": time.strftime("%Y-%m-%d %H:%M")
    }
    scores.append(record)
    scores.sort(key=lambda x: x.get("wpm", 0), reverse=True)
    scores = scores[:10]
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            json.dump(scores, f, indent=4)
    except Exception as e:
        print(f"Notice: Could not save high score ({e})")


def calculate_metrics(target_text, typed_text, elapsed_seconds):
    """Calculate accuracy, words per minute (WPM), and score."""
    if elapsed_seconds <= 0:
        elapsed_seconds = 0.1

    correct_chars = 0
    min_len = min(len(target_text), len(typed_text))
    for i in range(min_len):
        if target_text[i] == typed_text[i]:
            correct_chars += 1

    total_possible = max(len(target_text), len(typed_text), 1)
    accuracy = (correct_chars / total_possible) * 100

    minutes = elapsed_seconds / 60.0
    wpm = (len(typed_text) / 5.0) / minutes if minutes > 0 else 0

    score = int(wpm * (accuracy / 100) * 10)
    return round(wpm, 1), round(accuracy, 1), score


# ============================================================
#                      GAME MODES
# ============================================================

def play_time_attack(settings):
    """Mode 1: Timed Sprint - Type as many words as you can in the given time."""
    clear_screen()
    duration = settings["duration"]
    difficulty = settings["difficulty"]
    word_pool = list(WORD_BANKS.get(difficulty, WORD_BANKS["Medium"]))

    print("=" * 60)
    print(f"        ⚡ TIME ATTACK SPRINT ({duration}s - {difficulty}) ⚡")
    print("=" * 60)
    print("Instructions:")
    print(f"  • Type each word accurately and press [ENTER].")
    print(f"  • You have {duration} seconds to type as many words as possible.")
    print("=" * 60)
    input("\nPress [ENTER] when ready to start countdown...")

    for count in [3, 2, 1]:
        snd_countdown()
        print(f"Starting in {count}...", end="\r")
        time.sleep(1)
    snd_go()
    print("GO! 🚀                           \n")

    start_time = time.time()
    words_completed = 0
    words_correct = 0
    total_target_chars = 0
    total_typed_chars = 0

    while True:
        elapsed = time.time() - start_time
        remaining = duration - elapsed
        if remaining <= 0:
            print("\n⏰ Time is UP!")
            break

        target_word = random.choice(word_pool)
        print(f"[{int(remaining)}s left] Word: \033[1;36m{target_word}\033[0m")
        try:
            user_input = input(">> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGame aborted.")
            return

        words_completed += 1
        total_target_chars += len(target_word)
        total_typed_chars += len(user_input)

        if user_input == target_word:
            words_correct += 1
            snd_correct()
            print("  ✓ Correct!\n")
        else:
            snd_miss()
            print(f"  ✗ Missed! (Expected: '{target_word}')\n")

    total_elapsed = min(time.time() - start_time, duration)
    accuracy = (words_correct / words_completed * 100) if words_completed > 0 else 0
    minutes = total_elapsed / 60.0
    wpm = (total_typed_chars / 5.0) / minutes if minutes > 0 else 0
    score = int(wpm * (accuracy / 100) * 10)

    snd_fanfare()
    display_results("Time Attack Sprint", wpm, accuracy, score, [
        ("Time Limit", f"{duration}s"),
        ("Words Completed", words_completed),
        ("Words Correct", words_correct)
    ])
    save_high_score("Time Attack", wpm, accuracy, score)


def play_accuracy_streak(settings):
    """Mode 2: Sudden Death Streak - One mistake and you are out!"""
    clear_screen()
    difficulty = settings["difficulty"]
    word_pool = list(WORD_BANKS.get(difficulty, WORD_BANKS["Medium"]))

    print("=" * 60)
    print(f"       🎯 ACCURACY STREAK (SUDDEN DEATH - {difficulty}) 🎯")
    print("=" * 60)
    print("Instructions:")
    print("  • Type each word with 100% precision.")
    print("  • A single typo or mistake ends the game immediately!")
    print("=" * 60)
    input("\nPress [ENTER] to begin...")

    streak = 0
    total_chars = 0
    start_time = time.time()

    while True:
        target_word = random.choice(word_pool)
        print(f"\n[Streak: {streak}] Type: \033[1;33m{target_word}\033[0m")
        try:
            user_input = input(">> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGame aborted.")
            return

        if user_input == target_word:
            streak += 1
            total_chars += len(target_word)
            snd_correct()
            print(f"  ⚡ Streak: {streak}! Keep going!")
        else:
            snd_streak_fail()
            print("\n💥 MISTAKE! Streak broken!")
            print(f"Expected: '{target_word}', but you typed: '{user_input}'")
            break

    elapsed = max(time.time() - start_time, 0.5)
    minutes = elapsed / 60.0
    wpm = (total_chars / 5.0) / minutes if minutes > 0 else 0
    accuracy = 100.0 if streak > 0 else 0.0
    score = streak * 150

    display_results("Accuracy Streak", wpm, accuracy, score, [
        ("Longest Streak", f"{streak} words"),
        ("Total Characters", total_chars),
        ("Survival Time", f"{round(elapsed, 1)}s")
    ])
    save_high_score("Accuracy Streak", wpm, accuracy, score)


def play_sentence_sprint():
    """Mode 3: Sentence Velocity - Type a complete sentence for precise WPM/CPM."""
    clear_screen()
    sentence = random.choice(SENTENCES)

    print("=" * 60)
    print("            📜 SENTENCE SPRINT TEST 📜")
    print("=" * 60)
    print("Instructions:")
    print("  • Type the sentence below exactly as shown including punctuation.")
    print("  • Press [ENTER] when finished.")
    print("=" * 60)
    input("\nPress [ENTER] to reveal the sentence and start timer...")

    clear_screen()
    print("Target Sentence:")
    print(f"\033[1;32m{sentence}\033[0m\n")

    start_time = time.time()
    try:
        user_input = input("Type here:\n>> ")
    except (KeyboardInterrupt, EOFError):
        print("\nGame aborted.")
        return
    elapsed = max(time.time() - start_time, 0.1)

    if user_input.strip() == sentence:
        snd_fanfare()
    else:
        snd_miss()

    wpm, accuracy, score = calculate_metrics(sentence, user_input, elapsed)

    display_results("Sentence Sprint", wpm, accuracy, score, [
        ("Time Taken", f"{round(elapsed, 2)}s"),
        ("Target Length", f"{len(sentence)} chars"),
        ("Typed Length", f"{len(user_input)} chars")
    ])
    save_high_score("Sentence Sprint", wpm, accuracy, score)


def display_results(mode_name, wpm, accuracy, score, extra_stats=None):
    """Nicely formatted summary card for game results."""
    print("\n" + "=" * 60)
    print(f"             🏆 GAME RESULTS: {mode_name} 🏆")
    print("=" * 60)
    print(f"  ⚡ Typing Velocity : \033[1;36m{round(wpm, 1)} WPM\033[0m")
    print(f"  🎯 Accuracy        : \033[1;32m{round(accuracy, 1)}%\033[0m")
    print(f"  ⭐ Total Score     : \033[1;33m{score} PTS\033[0m")
    if extra_stats:
        print("-" * 60)
        for label, val in extra_stats:
            print(f"  • {label:<18} : {val}")
    print("=" * 60)
    input("\nPress [ENTER] to return to menu...")


# ============================================================
#                      SETTINGS & HIGH SCORES
# ============================================================

def show_high_scores():
    """Display saved leaderboard."""
    clear_screen()
    scores = load_high_scores()
    print("=" * 60)
    print("               🏆 TYPING SPRINT HALL OF FAME 🏆")
    print("=" * 60)
    if not scores:
        print("\n  No high scores recorded yet! Play a game to set a record.\n")
    else:
        print(f"  {'#':<3} {'Mode':<18} {'WPM':<8} {'Accuracy':<10} {'Score':<8} {'Date':<15}")
        print("  " + "-" * 56)
        for idx, rec in enumerate(scores, start=1):
            print(f"  {idx:<3} {rec.get('mode', 'N/A'):<18} {rec.get('wpm', 0):<8} {rec.get('accuracy', 0)}%{'':<3} {rec.get('score', 0):<8} {rec.get('date', 'N/A'):<15}")
    print("=" * 60)
    input("\nPress [ENTER] to continue...")


def settings_menu(settings):
    """Menu 3: Customize game settings."""
    while True:
        clear_screen()
        print("=" * 60)
        print("                  ⚙️ GAME SETTINGS ⚙️")
        print("=" * 60)
        print(f"  [1] Difficulty Level  : \033[1;36m{settings['difficulty']}\033[0m (Easy / Medium / Hard)")
        print(f"  [2] Sprint Duration   : \033[1;36m{settings['duration']} seconds\033[0m")
        print(f"  [3] Word Category     : \033[1;36m{settings['category']}\033[0m (Easy/Medium/Hard/Programming)")
        print(f"  [4] View High Scores Leaderboard")
        print(f"  [5] Reset Settings to Defaults")
        print(f"  [6] Back to Main Menu")
        print("=" * 60)

        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            print("\nSelect Difficulty:")
            print("  1. Easy    (short 3-4 letter words)")
            print("  2. Medium  (standard 5-8 letter words)")
            print("  3. Hard    (complex 10+ letter vocabulary)")
            diff_choice = input("Choose (1-3): ").strip()
            if diff_choice == "1":
                settings["difficulty"] = "Easy"
                settings["category"] = "Easy"
            elif diff_choice == "2":
                settings["difficulty"] = "Medium"
                settings["category"] = "Medium"
            elif diff_choice == "3":
                settings["difficulty"] = "Hard"
                settings["category"] = "Hard"
            else:
                print("Invalid choice.")
                time.sleep(1)

        elif choice == "2":
            print("\nSelect Duration for Time Attack:")
            print("  1. 15 Seconds (Blitz)")
            print("  2. 30 Seconds (Standard)")
            print("  3. 60 Seconds (Endurance)")
            dur_choice = input("Choose (1-3): ").strip()
            if dur_choice == "1":
                settings["duration"] = 15
            elif dur_choice == "2":
                settings["duration"] = 30
            elif dur_choice == "3":
                settings["duration"] = 60
            else:
                print("Invalid choice.")
                time.sleep(1)

        elif choice == "3":
            print("\nSelect Word Category:")
            print("  1. Easy")
            print("  2. Medium")
            print("  3. Hard")
            print("  4. Programming Terms")
            cat_choice = input("Choose (1-4): ").strip()
            if cat_choice == "1":
                settings["category"] = "Easy"
                settings["difficulty"] = "Easy"
            elif cat_choice == "2":
                settings["category"] = "Medium"
                settings["difficulty"] = "Medium"
            elif cat_choice == "3":
                settings["category"] = "Hard"
                settings["difficulty"] = "Hard"
            elif cat_choice == "4":
                settings["category"] = "Programming"
                settings["difficulty"] = "Programming"
            else:
                print("Invalid choice.")
                time.sleep(1)

        elif choice == "4":
            show_high_scores()

        elif choice == "5":
            settings["difficulty"] = "Medium"
            settings["duration"] = 30
            settings["category"] = "Medium"
            snd_correct()
            print("\nSettings reset to defaults!")
            time.sleep(1)

        elif choice == "6":
            break
        else:
            print("Invalid selection. Please choose 1-6.")
            time.sleep(1)


# ============================================================
#                      GAMES SUB-MENU
# ============================================================

def games_menu(settings):
    """Menu 2: Game Modes selector."""
    while True:
        clear_screen()
        print("=" * 60)
        print("                 🎮 GAME MODES 🎮")
        print("=" * 60)
        print("  [1] Time Attack Sprint    (Beat the clock, type as many words as possible)")
        print("  [2] Accuracy Streak       (Sudden Death: 1 typo = Game Over)")
        print("  [3] Sentence Sprint       (Full sentence test with exact WPM)")
        print("  [4] Back to Main Menu")
        print("=" * 60)

        choice = input("Select a game mode (1-4): ").strip()

        if choice == "1":
            play_time_attack(settings)
        elif choice == "2":
            play_accuracy_streak(settings)
        elif choice == "3":
            play_sentence_sprint()
        elif choice == "4":
            break
        else:
            print("Invalid choice! Please choose 1-4.")
            time.sleep(1)


# ============================================================
#                      MAIN MENU
# ============================================================

def main_menu():
    """Main Application Entry Point with 1. Menu, 2. Games, 3. Setting, 4. Quit."""
    settings = dict(DEFAULT_SETTINGS)

    while True:
        clear_screen()
        print("=" * 60)
        print("            ⚡⚡⚡ TYPING SPRINT ⚡⚡⚡")
        print("          Master Your Keystrokes & Velocity")
        print("=" * 60)
        print("  [1] Menu (Quick Play - Standard Sprint)")
        print("  [2] Games (Choose Game Modes & Challenges)")
        print("  [3] Setting (Difficulty, Timer, Words & Scores)")
        print("  [4] Quit")
        print("=" * 60)
        print(f"Current: Difficulty={settings['difficulty']} | Timer={settings['duration']}s | Pool={settings['category']}")
        print("=" * 60)

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            play_time_attack(settings)
        elif choice == "2":
            games_menu(settings)
        elif choice == "3":
            settings_menu(settings)
        elif choice == "4":
            clear_screen()
            print("=" * 60)
            print("       Thank you for playing Typing Sprint! 👋")
            print("                 Keep typing fast!")
            print("=" * 60)
            break
        else:
            print("Invalid option! Please enter a number between 1 and 4.")
            time.sleep(1.2)


if __name__ == "__main__":
    main_menu()
