"""
============================================================
             ⚡ TYPING SPRINT - FALLING WORDS EDITION ⚡
             Built with Pure Python & Tkinter
============================================================
Features:
  1. Falling Words Arena: Words cascade from top to bottom toward
     the electric laser barrier. Type them before shields are breached!
  2. Official Logo Integration: High-tech esports logo displayed
     in navigation, dashboard banner, HUD, dialogs, and window icon.
  3. Dynamic Target Reticle: Automatically locks onto falling words
     as you type, illuminating matched prefixes in neon emerald.
  4. Visual Particle Explosions & Floating Score Popups.
  5. Multiple Modes: Time Attack, Sudden Death Streak, Word Rush, Sentence Sprint.
  6. Procedural Synthesizer Sound Effects (Windows Audio).
  7. High Score Hall of Fame & Full Customization.
============================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import os
import shutil
import json
import threading
import math
import sys

# Windows Sound FX
try:
    import winsound
    HAS_WINSOUND = True
except Exception:
    HAS_WINSOUND = False

# High-DPI awareness on Windows
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# PIL / Pillow for Logo Image Rendering (Optional with graceful vector fallback)
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False

# Handle paths for normal script and PyInstaller onefile .exe
if getattr(sys, 'frozen', False):
    WORKSPACE_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = getattr(sys, '_MEIPASS', WORKSPACE_DIR)
else:
    WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = WORKSPACE_DIR

ASSETS_DIR = os.path.join(WORKSPACE_DIR, "assets")
BUNDLE_ASSETS = os.path.join(BUNDLE_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

LOGO_DEST_JPG = os.path.join(ASSETS_DIR, "logo.jpg")
LOGO_DEST_PNG = os.path.join(ASSETS_DIR, "logo.png")

# Auto-copy from generator path or bundled assets if not already in assets
AI_GEN_LOGO = r"C:\Users\Usman Computers\.gemini\antigravity-ide\brain\4c9c54bf-9f8a-4601-b233-5e40f0b7e223\typing_sprint_logo_1791110616790.jpg"
bundled_logo = os.path.join(BUNDLE_ASSETS, "logo.jpg")

source_logo = None
if os.path.exists(bundled_logo):
    source_logo = bundled_logo
elif os.path.exists(AI_GEN_LOGO):
    source_logo = AI_GEN_LOGO

if source_logo and (not os.path.exists(LOGO_DEST_JPG) or os.path.getsize(LOGO_DEST_JPG) == 0):
    try:
        shutil.copyfile(source_logo, LOGO_DEST_JPG)
    except Exception:
        pass

# Word Repositories
WORD_BANKS = {
    "Easy": [
        "cat", "dog", "sun", "run", "sky", "red", "blue", "code", "fast",
        "game", "play", "jump", "tree", "book", "fire", "wind", "gold",
        "fish", "star", "moon", "hero", "path", "cool", "glow", "time",
        "ship", "bird", "lamp", "hill", "rain", "snow", "road", "leaf",
        "core", "echo", "bold", "wave", "neon", "rush", "apex", "dash"
    ],
    "Medium": [
        "python", "sprint", "speed", "keyboard", "challenge", "velocity",
        "screen", "player", "action", "reflex", "victory", "network",
        "program", "system", "dynamic", "focus", "battle", "target",
        "engine", "future", "matrix", "stream", "puzzle", "energy",
        "galaxy", "rocket", "quantum", "planet", "circuit", "digital",
        "arcade", "shield", "laser", "cascade", "impact", "reticle"
    ],
    "Hard": [
        "asynchronous", "polymorphism", "synchronization", "cryptography",
        "architecture", "multithreading", "encapsulation", "optimization",
        "troubleshooting", "infrastructure", "interoperability", "cybersecurity",
        "microservices", "computational", "telecommunications", "cryptocurrency",
        "orchestration", "parallelization", "superconductor", "electromagnetic"
    ],
    "Programming": [
        "variable", "function", "iteration", "boolean", "dictionary",
        "recursion", "exception", "algorithm", "compiler", "debugging",
        "terminal", "database", "parameter", "inheritance", "framework",
        "interface", "decorator", "generator", "middleware", "repository",
        "callback", "namespace", "immutable", "coroutine", "polymorphic"
    ]
}

SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "Practice and consistency are keys to typing velocity.",
    "Words cascade from the sky toward the laser barrier.",
    "Clean code always looks like someone cared about it.",
    "Keep your eyes locked on the falling target words.",
    "Speed without accuracy is like a car with no steering.",
    "High velocity reflexes will defend your shield integrity."
]

HIGH_SCORE_FILE = os.path.join(WORKSPACE_DIR, "highscores.json")

# Cyber Theme Color Palette
BG_DARK = "#090d16"        # Deep Space Navy
BG_CARD = "#131b2e"        # Cyber Blue-Slate
BG_CARD_LIGHT = "#1e293b"  # Border Slate
ACCENT_CYAN = "#06b6d4"    # Neon Cyan
ACCENT_GREEN = "#10b981"   # Neon Emerald
ACCENT_YELLOW = "#f59e0b"  # Electric Gold
ACCENT_RED = "#ef4444"     # Laser Red
ACCENT_PURPLE = "#a855f7"  # Synthwave Purple
TEXT_MAIN = "#f8fafc"      # Pure White / Slate 50
TEXT_MUTED = "#94a3b8"     # Slate 400


class TypingSprintApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⚡ Typing Sprint | Falling Words Velocity Challenge")
        self.geometry("1000x720")
        self.minsize(920, 640)
        self.configure(bg=BG_DARK)

        # Game Settings State
        self.sound_enabled = True
        self.settings = {
            "difficulty": "Medium",
            "duration": 30,
            "category": "Medium",
            "sound": True
        }

        # Game Session State
        self.current_mode = "Time Attack"
        self.game_active = False
        self.game_paused = False
        self.start_time = 0
        self.timer_seconds_left = 30
        self.timer_job = None
        self.physics_job = None
        self.spawn_job = None

        # Live Stats
        self.score = 0
        self.shields = 4
        self.max_shields = 4
        self.words_completed = 0
        self.words_breached = 0
        self.total_typed_chars = 0
        self.streak_count = 0
        self.highest_streak = 0

        # Falling Words Engine State
        self.falling_words = []   # List of active word objects
        self.active_target = None # The word currently locked on by user
        self.particles = []       # Active spark particles
        self.floating_popups = [] # Active score floating texts
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_frames_left = 0

        # Load Logo Assets
        self.init_logo_images()

        # Setup modern ttk styles
        self.setup_styles()

        # Root Layout: Navbar + Main Container
        self.create_navbar()

        self.container = tk.Frame(self, bg=BG_DARK)
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

        # View Dictionary
        self.views = {}
        self.init_views()

        # Start on Main Menu
        self.show_view("menu")

    # ========================================================
    #               LOGO ASSETS & RENDERING
    # ========================================================
    def init_logo_images(self):
        """Prepare logo images across UI sizes with Pillow or fallback vector."""
        self.logo_img_navbar = None
        self.logo_img_banner = None
        self.logo_img_hud = None
        self.logo_img_dialog = None
        self.logo_img_icon = None

        logo_path = None
        for p in [LOGO_DEST_JPG, bundled_logo, AI_GEN_LOGO]:
            if p and os.path.exists(p) and os.path.getsize(p) > 0:
                logo_path = p
                break

        if HAS_PIL and logo_path and os.path.exists(logo_path):
            try:
                base_img = Image.open(logo_path)
                
                # Navbar badge (42x42)
                res_nav = base_img.resize((42, 42), Image.Resampling.LANCZOS)
                self.logo_img_navbar = ImageTk.PhotoImage(res_nav)

                # Hero banner badge (110x110)
                res_banner = base_img.resize((110, 110), Image.Resampling.LANCZOS)
                self.logo_img_banner = ImageTk.PhotoImage(res_banner)

                # Arena HUD badge (26x26)
                res_hud = base_img.resize((26, 26), Image.Resampling.LANCZOS)
                self.logo_img_hud = ImageTk.PhotoImage(res_hud)

                # Dialog badge (70x70)
                res_dialog = base_img.resize((70, 70), Image.Resampling.LANCZOS)
                self.logo_img_dialog = ImageTk.PhotoImage(res_dialog)

                # Window Icon (32x32)
                res_icon = base_img.resize((32, 32), Image.Resampling.LANCZOS)
                self.logo_img_icon = ImageTk.PhotoImage(res_icon)
                self.iconphoto(True, self.logo_img_icon)

                # Also save PNG version for Windows system compatibility
                if not os.path.exists(LOGO_DEST_PNG):
                    base_img.save(LOGO_DEST_PNG)
            except Exception as e:
                print(f"PIL logo loading note: {e}")

    def draw_vector_logo(self, canvas, w, h):
        """Crisp cyber vector logo drawn on a canvas as a high-grade native fallback."""
        cx, cy = w / 2, h / 2
        r = min(w, h) * 0.44

        # Outer hexagon glow badge
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            points.extend([cx + r * math.cos(angle), cy + r * math.sin(angle)])
        canvas.create_polygon(points, fill="#0f172a", outline=ACCENT_CYAN, width=2)

        # Inner keyboard switch motif
        kw, kh = r * 0.7, r * 0.4
        canvas.create_rectangle(cx - kw, cy - kh, cx + kw, cy + kh, fill="#1e293b", outline="#334155", width=1)

        # Electric Lightning Bolt (Neon Amber / Cyan)
        bolt = [
            cx + 2, cy - r * 0.75,
            cx - r * 0.45, cy + 2,
            cx - 2, cy + 2,
            cx - 4, cy + r * 0.75,
            cx + r * 0.45, cy - 2,
            cx + 2, cy - 2
        ]
        canvas.create_polygon(bolt, fill=ACCENT_YELLOW, outline="#fef08a", width=1)

    # ========================================================
    #               AUDIO SYNTHESIZER (WINDOWS)
    # ========================================================
    def sfx_beep(self, freq, duration=35):
        if not self.sound_enabled or not HAS_WINSOUND:
            return
        def _play():
            try:
                winsound.Beep(int(freq), int(duration))
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()

    def sfx_melody(self, notes):
        if not self.sound_enabled or not HAS_WINSOUND:
            return
        def _play():
            try:
                for freq, dur in notes:
                    winsound.Beep(int(freq), int(dur))
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()

    def sound_key_click(self, char_idx=0):
        freq = 620 + min(char_idx * 45, 550)
        self.sfx_beep(freq, 22)

    def sound_typo(self):
        self.sfx_beep(210, 70)

    def sound_word_complete(self):
        self.sfx_melody([(950, 40), (1400, 60)])

    def sound_laser_breach(self):
        self.sfx_melody([(320, 60), (180, 100)])

    def sound_countdown(self, final=False):
        if final:
            self.sfx_melody([(784, 80), (1046, 120)])
        else:
            self.sfx_beep(520, 45)

    def sound_sudden_death_fail(self):
        self.sfx_melody([(440, 70), (330, 90), (180, 160)])

    def sound_victory(self):
        self.sfx_melody([(523, 70), (659, 70), (784, 70), (1046, 180)])

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.settings["sound"] = self.sound_enabled
        btn_text = "🔊 Sound: ON" if self.sound_enabled else "🔇 Sound: OFF"
        color = ACCENT_GREEN if self.sound_enabled else TEXT_MUTED
        if hasattr(self, "sound_nav_btn"):
            self.sound_nav_btn.config(text=btn_text, fg=color)
        if hasattr(self, "sound_chk_var"):
            self.sound_chk_var.set(self.sound_enabled)
        if self.sound_enabled:
            self.sound_word_complete()

    # ========================================================
    #                     STYLES & NAVIGATION
    # ========================================================
    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Custom.Treeview",
            background=BG_CARD,
            foreground=TEXT_MAIN,
            fieldbackground=BG_CARD,
            font=("Segoe UI", 10),
            rowheight=30
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=BG_CARD_LIGHT,
            foreground=ACCENT_CYAN,
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )
        style.map("Custom.Treeview", background=[("selected", ACCENT_CYAN)], foreground=[("selected", BG_DARK)])

    def create_navbar(self):
        self.nav_frame = tk.Frame(self, bg=BG_CARD, height=65)
        self.nav_frame.pack(fill=tk.X, side=tk.TOP, padx=0, pady=(0, 15))
        self.nav_frame.pack_propagate(False)

        # Brand Logo Section with Official Image
        brand_frame = tk.Frame(self.nav_frame, bg=BG_CARD)
        brand_frame.pack(side=tk.LEFT, padx=20)

        # Logo display (Image or vector fallback)
        if self.logo_img_navbar:
            self.nav_logo_lbl = tk.Label(brand_frame, image=self.logo_img_navbar, bg=BG_CARD)
            self.nav_logo_lbl.pack(side=tk.LEFT, padx=(0, 10))
        else:
            logo_canvas = tk.Canvas(brand_frame, width=38, height=38, bg=BG_CARD, highlightthickness=0)
            logo_canvas.pack(side=tk.LEFT, padx=(0, 10))
            self.draw_vector_logo(logo_canvas, 38, 38)

        title_container = tk.Frame(brand_frame, bg=BG_CARD)
        title_container.pack(side=tk.LEFT)

        tk.Label(
            title_container, text="TYPING SPRINT", font=("Segoe UI", 14, "bold"),
            fg=TEXT_MAIN, bg=BG_CARD
        ).pack(anchor="w")

        tk.Label(
            title_container, text="⚡ FALLING WORDS EDITION", font=("Segoe UI", 8, "bold"),
            fg=ACCENT_CYAN, bg=BG_CARD
        ).pack(anchor="w")

        # Right Navigation Buttons & Sound Toggle
        btn_bar = tk.Frame(self.nav_frame, bg=BG_CARD)
        btn_bar.pack(side=tk.RIGHT, padx=20)

        self.sound_nav_btn = tk.Button(
            btn_bar, text="🔊 Sound: ON", font=("Segoe UI", 9, "bold"),
            bg=BG_CARD, fg=ACCENT_GREEN, activebackground=BG_CARD_LIGHT,
            activeforeground=TEXT_MAIN, bd=0, padx=12, pady=7, cursor="hand2",
            command=self.toggle_sound
        )
        self.sound_nav_btn.pack(side=tk.LEFT, padx=(0, 10))

        nav_items = [
            ("1. Menu", "menu", ACCENT_CYAN),
            ("2. Games", "games", "#38bdf8"),
            ("3. Settings", "settings", ACCENT_PURPLE),
            ("4. Quit", "quit", ACCENT_RED)
        ]

        self.nav_buttons = {}
        for text, key, color in nav_items:
            action = self.confirm_quit if key == "quit" else (lambda k=key: self.navigate_to(k))
            btn = tk.Button(
                btn_bar, text=text, font=("Segoe UI", 10, "bold"),
                bg=BG_CARD, fg=TEXT_MUTED, activebackground=BG_CARD_LIGHT,
                activeforeground=color, bd=0, padx=12, pady=7, cursor="hand2",
                command=action
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.nav_buttons[key] = btn

    def navigate_to(self, key):
        if self.game_active:
            if not messagebox.askyesno("Exit Game", "An active sprint is running. Return to menu?"):
                return
            self.stop_game()
        self.show_view(key)

    def highlight_nav(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg=TEXT_MAIN, bg=BG_CARD_LIGHT)
            elif key == "quit":
                btn.configure(fg=ACCENT_RED, bg=BG_CARD)
            else:
                btn.configure(fg=TEXT_MUTED, bg=BG_CARD)

    # ========================================================
    #                     VIEW MANAGER
    # ========================================================
    def init_views(self):
        self.views["menu"] = self.create_menu_view()
        self.views["games"] = self.create_games_view()
        self.views["settings"] = self.create_settings_view()
        self.views["arena"] = self.create_arena_view()

    def show_view(self, key):
        self.highlight_nav(key if key in self.nav_buttons else None)
        for name, frame in self.views.items():
            if name == key:
                frame.pack(fill=tk.BOTH, expand=True)
                if hasattr(frame, "on_show"):
                    frame.on_show()
            else:
                frame.pack_forget()

    # ========================================================
    #               VIEW 1: MENU (DASHBOARD)
    # ========================================================
    def create_menu_view(self):
        view = tk.Frame(self.container, bg=BG_DARK)

        # Hero Banner with Official Logo
        banner = tk.Frame(view, bg=BG_CARD, bd=0, padx=25, pady=20)
        banner.pack(fill=tk.X, pady=(0, 16))

        # Left: Large Badge Logo
        logo_box = tk.Frame(banner, bg=BG_CARD)
        logo_box.pack(side=tk.LEFT, padx=(0, 25))

        if self.logo_img_banner:
            tk.Label(logo_box, image=self.logo_img_banner, bg=BG_CARD).pack()
        else:
            hero_canvas = tk.Canvas(logo_box, width=100, height=100, bg=BG_CARD, highlightthickness=0)
            hero_canvas.pack()
            self.draw_vector_logo(hero_canvas, 100, 100)

        # Right: Banner text & CTA
        banner_info = tk.Frame(banner, bg=BG_CARD)
        banner_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            banner_info, text="⚡ WELCOME TO TYPING SPRINT",
            font=("Segoe UI", 22, "bold"), fg=ACCENT_CYAN, bg=BG_CARD
        ).pack(anchor="w")

        tk.Label(
            banner_info, text="Falling Words Velocity Challenge — Destroy words cascading from top to bottom before they breach your shields!",
            font=("Segoe UI", 11), fg=TEXT_MUTED, bg=BG_CARD
        ).pack(anchor="w", pady=(4, 12))

        # CTA Button
        quick_btn = tk.Button(
            banner_info, text="🚀 START FALLING SPRINT (30s)", font=("Segoe UI", 11, "bold"),
            bg=ACCENT_GREEN, fg=BG_DARK, activebackground="#059669", activeforeground=TEXT_MAIN,
            bd=0, padx=22, pady=10, cursor="hand2",
            command=lambda: self.launch_game("Time Attack")
        )
        quick_btn.pack(anchor="w")

        # KPI Stats Cards Grid
        stats_frame = tk.Frame(view, bg=BG_DARK)
        stats_frame.pack(fill=tk.X, pady=(0, 16))

        self.kpi_best_wpm = self.create_kpi_card(stats_frame, "BEST VELOCITY", "0.0 WPM", ACCENT_CYAN, 0)
        self.kpi_best_acc = self.create_kpi_card(stats_frame, "HIGHEST ACCURACY", "0.0%", ACCENT_GREEN, 1)
        self.kpi_runs = self.create_kpi_card(stats_frame, "GAMES PLAYED", "0 RUNS", ACCENT_YELLOW, 2)

        # Navigation Options Box
        nav_box = tk.LabelFrame(
            view, text="  Select Option  ", font=("Segoe UI", 11, "bold"),
            bg=BG_CARD, fg=TEXT_MAIN, bd=1, padx=20, pady=12
        )
        nav_box.pack(fill=tk.BOTH, expand=True)

        opts = [
            ("⚡ 1. Menu (Quick Play)", "Start falling words sprint with current settings", lambda: self.launch_game("Time Attack")),
            ("🎮 2. Games & Modes", "Time Attack, Sudden Death, Word Cascade, Sentence Sprint", lambda: self.show_view("games")),
            ("⚙️ 3. Settings & Scores", "Difficulty, falling speed, categories & Hall of Fame", lambda: self.show_view("settings")),
            ("❌ 4. Quit Game", "Close Typing Sprint application", self.confirm_quit)
        ]

        for title, desc, cmd in opts:
            row = tk.Frame(nav_box, bg=BG_CARD, pady=5)
            row.pack(fill=tk.X)

            btn = tk.Button(
                row, text=title, font=("Segoe UI", 10, "bold"),
                bg=BG_CARD_LIGHT, fg=TEXT_MAIN, activebackground=ACCENT_CYAN,
                activeforeground=BG_DARK, bd=0, width=24, anchor="w",
                padx=14, pady=7, cursor="hand2", command=cmd
            )
            btn.pack(side=tk.LEFT)

            tk.Label(
                row, text=f"• {desc}", font=("Segoe UI", 10),
                fg=TEXT_MUTED, bg=BG_CARD
            ).pack(side=tk.LEFT, padx=15)

        def refresh_stats():
            scores = self.load_scores()
            if scores:
                best_w = max([s.get("wpm", 0) for s in scores], default=0)
                best_a = max([s.get("accuracy", 0) for s in scores], default=0)
                self.kpi_best_wpm.config(text=f"{best_w} WPM")
                self.kpi_best_acc.config(text=f"{best_a}%")
                self.kpi_runs.config(text=f"{len(scores)} RUNS")
            else:
                self.kpi_best_wpm.config(text="0.0 WPM")
                self.kpi_best_acc.config(text="0.0%")
                self.kpi_runs.config(text="0 RUNS")

        view.on_show = refresh_stats
        return view

    def create_kpi_card(self, parent, title, initial_val, accent_color, col_idx):
        card = tk.Frame(parent, bg=BG_CARD, padx=20, pady=14)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if col_idx == 0 else 10, 0))

        tk.Label(
            card, text=title, font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED, bg=BG_CARD
        ).pack(anchor="w")

        val_label = tk.Label(
            card, text=initial_val, font=("Segoe UI", 18, "bold"),
            fg=accent_color, bg=BG_CARD
        )
        val_label.pack(anchor="w", pady=(3, 0))
        return val_label

    # ========================================================
    #               VIEW 2: GAMES (MODE SELECTOR)
    # ========================================================
    def create_games_view(self):
        view = tk.Frame(self.container, bg=BG_DARK)

        header = tk.Frame(view, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            header, text="🎮 CHOOSE YOUR FALLING CHALLENGE",
            font=("Segoe UI", 20, "bold"), fg=TEXT_MAIN, bg=BG_DARK
        ).pack(anchor="w")

        tk.Label(
            header, text="Select how words cascade and test your reflexes under pressure.",
            font=("Segoe UI", 10), fg=TEXT_MUTED, bg=BG_DARK
        ).pack(anchor="w", pady=(2, 0))

        modes = [
            {
                "title": "⚡ Time Attack Sprint",
                "badge": "TIMED COUNTDOWN",
                "color": ACCENT_CYAN,
                "desc": "Words rain down toward the laser barrier! Eliminate as many falling words as possible before the clock expires.",
                "rules": "• Configurable 15s, 30s, or 60s timer\n• 4 Laser Shields protection\n• Multi-word cascade waves",
                "btn_text": "Play Time Attack ➔",
                "mode_key": "Time Attack"
            },
            {
                "title": "🎯 Accuracy Streak",
                "badge": "SUDDEN DEATH",
                "color": ACCENT_YELLOW,
                "desc": "Falling words require absolute precision. One single typo or letting a single word hit the laser line ends the run!",
                "rules": "• 1 Laser Shield only\n• 1 mistake = Instant Game Over\n• High-stakes reflex test",
                "btn_text": "Play Sudden Death ➔",
                "mode_key": "Accuracy Streak"
            },
            {
                "title": "📜 Sentence Velocity",
                "badge": "REALISTIC TEXT",
                "color": ACCENT_GREEN,
                "desc": "Natural phrases fall smoothly down the arena. Practice typing full sentences with punctuation before they hit bottom.",
                "rules": "• Real-world typing rhythm\n• Natural sentence flow\n• Accurate CPM & WPM feedback",
                "btn_text": "Play Sentence Sprint ➔",
                "mode_key": "Sentence Sprint"
            }
        ]

        cards_frame = tk.Frame(view, bg=BG_DARK)
        cards_frame.pack(fill=tk.BOTH, expand=True)

        for idx, m in enumerate(modes):
            card = tk.Frame(cards_frame, bg=BG_CARD, padx=20, pady=18)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if idx == 0 else 15, 0))

            tk.Label(
                card, text=m["badge"], font=("Segoe UI", 8, "bold"),
                bg=BG_CARD_LIGHT, fg=m["color"], padx=8, pady=3
            ).pack(anchor="w")

            tk.Label(
                card, text=m["title"], font=("Segoe UI", 14, "bold"),
                fg=TEXT_MAIN, bg=BG_CARD
            ).pack(anchor="w", pady=(10, 6))

            tk.Label(
                card, text=m["desc"], font=("Segoe UI", 10),
                fg=TEXT_MUTED, bg=BG_CARD, wraplength=230, justify="left"
            ).pack(anchor="w", pady=(0, 10))

            tk.Label(
                card, text=m["rules"], font=("Segoe UI", 9),
                fg=TEXT_MUTED, bg=BG_CARD, justify="left"
            ).pack(anchor="w", pady=(0, 20))

            play_btn = tk.Button(
                card, text=m["btn_text"], font=("Segoe UI", 10, "bold"),
                bg=m["color"], fg=BG_DARK, activebackground=TEXT_MAIN,
                activeforeground=BG_DARK, bd=0, padx=15, pady=9, cursor="hand2",
                command=lambda k=m["mode_key"]: self.launch_game(k)
            )
            play_btn.pack(side=tk.BOTTOM, fill=tk.X)

        return view

    # ========================================================
    #               VIEW 3: SETTINGS & LEADERBOARD
    # ========================================================
    def create_settings_view(self):
        view = tk.Frame(self.container, bg=BG_DARK)

        header = tk.Frame(view, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 14))

        tk.Label(
            header, text="⚙️ GAME SETTINGS & SCORES",
            font=("Segoe UI", 20, "bold"), fg=TEXT_MAIN, bg=BG_DARK
        ).pack(anchor="w")

        content = tk.Frame(view, bg=BG_DARK)
        content.pack(fill=tk.BOTH, expand=True)

        # Left Column: Configuration Controls
        left_col = tk.LabelFrame(
            content, text="  Configuration  ", font=("Segoe UI", 11, "bold"),
            bg=BG_CARD, fg=TEXT_MAIN, bd=1, padx=18, pady=12
        )
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 15), ipadx=10)

        # Sound
        tk.Label(left_col, text="Audio & Feedback:", font=("Segoe UI", 10, "bold"), fg=TEXT_MAIN, bg=BG_CARD).pack(anchor="w", pady=(0, 2))
        self.sound_chk_var = tk.BooleanVar(value=self.sound_enabled)
        chk = tk.Checkbutton(
            left_col, text="Enable Keystrokes & Laser SFX",
            variable=self.sound_chk_var, font=("Segoe UI", 9),
            fg=ACCENT_CYAN, bg=BG_CARD, selectcolor=BG_CARD_LIGHT,
            activebackground=BG_CARD, activeforeground=TEXT_MAIN,
            command=self.on_sound_checkbox_toggled
        )
        chk.pack(anchor="w", padx=5, pady=(0, 8))

        # Difficulty & Falling Velocity
        tk.Label(left_col, text="Falling Velocity & Shields:", font=("Segoe UI", 10, "bold"), fg=TEXT_MAIN, bg=BG_CARD).pack(anchor="w", pady=(4, 2))
        self.diff_var = tk.StringVar(value=self.settings["difficulty"])
        for diff in ["Easy (Gentle speed, 5 shields)", "Medium (Arcade speed, 4 shields)", "Hard (High velocity, 3 shields)"]:
            val = diff.split()[0]
            rb = tk.Radiobutton(
                left_col, text=diff, variable=self.diff_var, value=val,
                font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_CARD, selectcolor=BG_CARD_LIGHT,
                activebackground=BG_CARD, activeforeground=TEXT_MAIN, command=self.apply_settings
            )
            rb.pack(anchor="w", padx=8)

        # Duration
        tk.Label(left_col, text="Sprint Duration:", font=("Segoe UI", 10, "bold"), fg=TEXT_MAIN, bg=BG_CARD).pack(anchor="w", pady=(12, 2))
        self.dur_var = tk.IntVar(value=self.settings["duration"])
        dur_frame = tk.Frame(left_col, bg=BG_CARD)
        dur_frame.pack(anchor="w", padx=8)
        for dur in [15, 30, 60]:
            rb = tk.Radiobutton(
                dur_frame, text=f"{dur}s", variable=self.dur_var, value=dur,
                font=("Segoe UI", 9, "bold"), fg=ACCENT_CYAN, bg=BG_CARD, selectcolor=BG_CARD_LIGHT,
                activebackground=BG_CARD, activeforeground=TEXT_MAIN, command=self.apply_settings
            )
            rb.pack(side=tk.LEFT, padx=5)

        # Word Category
        tk.Label(left_col, text="Word Category:", font=("Segoe UI", 10, "bold"), fg=TEXT_MAIN, bg=BG_CARD).pack(anchor="w", pady=(12, 2))
        self.cat_var = tk.StringVar(value=self.settings["category"])
        cat_combo = ttk.Combobox(
            left_col, textvariable=self.cat_var, state="readonly",
            values=["Easy", "Medium", "Hard", "Programming"]
        )
        cat_combo.pack(anchor="w", padx=8, fill=tk.X)
        cat_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_settings())

        # Buttons
        tk.Button(
            left_col, text="Reset to Defaults", font=("Segoe UI", 9),
            bg=BG_CARD_LIGHT, fg=TEXT_MUTED, activebackground=ACCENT_RED, activeforeground=TEXT_MAIN,
            bd=0, pady=5, cursor="hand2", command=self.reset_settings
        ).pack(fill=tk.X, pady=(16, 5))

        tk.Button(
            left_col, text="Clear High Scores", font=("Segoe UI", 9),
            bg=BG_CARD_LIGHT, fg=ACCENT_RED, activebackground=ACCENT_RED, activeforeground=TEXT_MAIN,
            bd=0, pady=5, cursor="hand2", command=self.clear_high_scores
        ).pack(fill=tk.X)

        # Right Column: High Scores Table
        right_col = tk.LabelFrame(
            content, text="  🏆 High Scores Hall of Fame  ", font=("Segoe UI", 11, "bold"),
            bg=BG_CARD, fg=TEXT_MAIN, bd=1, padx=12, pady=12
        )
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        columns = ("rank", "mode", "wpm", "accuracy", "score", "date")
        self.tree = ttk.Treeview(right_col, columns=columns, show="headings", style="Custom.Treeview")
        self.tree.heading("rank", text="#")
        self.tree.heading("mode", text="Game Mode")
        self.tree.heading("wpm", text="WPM")
        self.tree.heading("accuracy", text="Accuracy")
        self.tree.heading("score", text="Score")
        self.tree.heading("date", text="Date")

        self.tree.column("rank", width=35, anchor="center")
        self.tree.column("mode", width=120, anchor="w")
        self.tree.column("wpm", width=80, anchor="center")
        self.tree.column("accuracy", width=80, anchor="center")
        self.tree.column("score", width=80, anchor="center")
        self.tree.column("date", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(right_col, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        view.on_show = self.load_leaderboard
        return view

    def on_sound_checkbox_toggled(self):
        new_state = self.sound_chk_var.get()
        if new_state != self.sound_enabled:
            self.toggle_sound()

    def apply_settings(self):
        self.settings["difficulty"] = self.diff_var.get()
        self.settings["duration"] = self.dur_var.get()
        self.settings["category"] = self.cat_var.get()

    def reset_settings(self):
        self.diff_var.set("Medium")
        self.dur_var.set(30)
        self.cat_var.set("Medium")
        self.sound_enabled = True
        self.sound_chk_var.set(True)
        self.sound_nav_btn.config(text="🔊 Sound: ON", fg=ACCENT_GREEN)
        self.apply_settings()
        self.sound_word_complete()
        messagebox.showinfo("Settings", "Settings restored to defaults!")

    def load_leaderboard(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        scores = self.load_scores()
        for idx, s in enumerate(scores, start=1):
            self.tree.insert("", tk.END, values=(
                f"#{idx}",
                s.get("mode", "N/A"),
                f"{s.get('wpm', 0)}",
                f"{s.get('accuracy', 0)}%",
                f"{s.get('score', 0)}",
                s.get("date", "N/A")
            ))

    def clear_high_scores(self):
        if messagebox.askyesno("Clear Scores", "Are you sure you want to clear all high scores?"):
            if os.path.exists(HIGH_SCORE_FILE):
                try:
                    os.remove(HIGH_SCORE_FILE)
                except Exception:
                    pass
            self.load_leaderboard()

    # ========================================================
    #               VIEW 4: FALLING WORDS ARENA
    # ========================================================
    def create_arena_view(self):
        view = tk.Frame(self.container, bg=BG_DARK)

        # 1. Top Live HUD Bar
        self.hud_frame = tk.Frame(view, bg=BG_CARD, padx=20, pady=10)
        self.hud_frame.pack(fill=tk.X, pady=(0, 10))

        # HUD Left: Mini Logo & Mode
        hud_left = tk.Frame(self.hud_frame, bg=BG_CARD)
        hud_left.pack(side=tk.LEFT)

        if self.logo_img_hud:
            tk.Label(hud_left, image=self.logo_img_hud, bg=BG_CARD).pack(side=tk.LEFT, padx=(0, 8))

        self.arena_mode_label = tk.Label(
            hud_left, text="TIME ATTACK SPRINT", font=("Segoe UI", 11, "bold"),
            fg=ACCENT_CYAN, bg=BG_CARD
        )
        self.arena_mode_label.pack(side=tk.LEFT)

        # HUD Center: Shields indicator
        self.hud_shields_frame = tk.Frame(self.hud_frame, bg=BG_CARD)
        self.hud_shields_frame.pack(side=tk.LEFT, padx=30)

        self.hud_shields_label = tk.Label(
            self.hud_shields_frame, text="SHIELDS: 🛡️🛡️🛡️🛡️", font=("Segoe UI", 10, "bold"),
            fg=ACCENT_GREEN, bg=BG_CARD
        )
        self.hud_shields_label.pack(side=tk.LEFT)

        # HUD Right: Timer / Streak / Live Speed / Score
        hud_right = tk.Frame(self.hud_frame, bg=BG_CARD)
        hud_right.pack(side=tk.RIGHT)

        self.hud_timer_label = tk.Label(
            hud_right, text="⏰ 30s", font=("Segoe UI", 12, "bold"),
            fg=ACCENT_YELLOW, bg=BG_CARD, padx=10
        )
        self.hud_timer_label.pack(side=tk.LEFT)

        self.hud_wpm_label = tk.Label(
            hud_right, text="0.0 WPM", font=("Segoe UI", 11, "bold"),
            fg=ACCENT_CYAN, bg=BG_CARD, padx=10
        )
        self.hud_wpm_label.pack(side=tk.LEFT)

        self.hud_acc_label = tk.Label(
            hud_right, text="100%", font=("Segoe UI", 11, "bold"),
            fg=TEXT_MAIN, bg=BG_CARD, padx=10
        )
        self.hud_acc_label.pack(side=tk.LEFT)

        self.hud_score_label = tk.Label(
            hud_right, text="0 PTS", font=("Segoe UI", 11, "bold"),
            fg=ACCENT_YELLOW, bg=BG_CARD, padx=10
        )
        self.hud_score_label.pack(side=tk.LEFT)

        # 2. Main Falling Words Arena Canvas
        canvas_container = tk.Frame(view, bg=BG_CARD, bd=1, relief="solid")
        canvas_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.arena_canvas = tk.Canvas(
            canvas_container, bg="#070b14", highlightthickness=0
        )
        self.arena_canvas.pack(fill=tk.BOTH, expand=True)
        self.arena_canvas.bind("<Configure>", self.on_canvas_resize)

        # 3. Cockpit Input & Target Reticle Controls
        cockpit = tk.Frame(view, bg=BG_CARD, padx=20, pady=12)
        cockpit.pack(fill=tk.X)

        # Target Reticle Status Bar
        status_bar = tk.Frame(cockpit, bg=BG_CARD)
        status_bar.pack(fill=tk.X, pady=(0, 8))

        self.target_reticle_label = tk.Label(
            status_bar, text="🎯 TARGET: [ Type first letter of any falling word to lock on ]",
            font=("Consolas", 12, "bold"), fg=ACCENT_CYAN, bg=BG_CARD
        )
        self.target_reticle_label.pack(side=tk.LEFT)

        self.combo_label = tk.Label(
            status_bar, text="COMBO: 0x", font=("Segoe UI", 11, "bold"),
            fg=ACCENT_YELLOW, bg=BG_CARD
        )
        self.combo_label.pack(side=tk.RIGHT)

        # Live Typing Entry Field
        input_row = tk.Frame(cockpit, bg=BG_CARD)
        input_row.pack(fill=tk.X)

        self.typing_entry = tk.Entry(
            input_row, font=("Consolas", 18, "bold"),
            bg=BG_CARD_LIGHT, fg=TEXT_MAIN, insertbackground=ACCENT_CYAN,
            bd=2, relief="flat", justify="center"
        )
        self.typing_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 12))
        self.typing_entry.bind("<KeyRelease>", self.on_key_release)
        self.typing_entry.bind("<Return>", self.on_word_submit)
        self.typing_entry.bind("<space>", self.on_word_submit)

        # Stop Button
        tk.Button(
            input_row, text="⏹ Stop Sprint", font=("Segoe UI", 10, "bold"),
            bg=BG_CARD_LIGHT, fg=TEXT_MUTED, activebackground=ACCENT_RED,
            activeforeground=TEXT_MAIN, bd=0, padx=16, pady=8, cursor="hand2",
            command=self.stop_and_return
        ).pack(side=tk.RIGHT)

        return view

    def on_canvas_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.laser_y = self.canvas_height - 50

    # ========================================================
    #                 FALLING WORDS ENGINE
    # ========================================================
    def launch_game(self, mode_name):
        self.current_mode = mode_name
        self.show_view("arena")

        # Initialize State
        self.game_active = True
        self.start_time = time.time()
        self.score = 0
        self.words_completed = 0
        self.words_breached = 0
        self.total_typed_chars = 0
        self.streak_count = 0
        self.highest_streak = 0
        self.falling_words = []
        self.active_target = None
        self.particles = []
        self.floating_popups = []

        # Setup Difficulty & Shields
        diff = self.settings["difficulty"]
        if mode_name == "Accuracy Streak":
            self.max_shields = 1
            self.base_speed = 1.6
            self.spawn_interval_ms = 2200
        elif diff == "Easy":
            self.max_shields = 5
            self.base_speed = 1.1
            self.spawn_interval_ms = 2600
        elif diff == "Hard":
            self.max_shields = 3
            self.base_speed = 2.4
            self.spawn_interval_ms = 1600
        else: # Medium
            self.max_shields = 4
            self.base_speed = 1.7
            self.spawn_interval_ms = 2000

        self.shields = self.max_shields
        self.update_shields_display()

        # Update HUD labels
        self.arena_mode_label.config(text=f"{mode_name.upper()}")
        self.hud_wpm_label.config(text="0.0 WPM")
        self.hud_acc_label.config(text="100%")
        self.hud_score_label.config(text="0 PTS")
        self.combo_label.config(text="COMBO: 0x")
        self.target_reticle_label.config(
            text="🎯 TARGET: [ Type first letter of any falling word to lock on ]",
            fg=ACCENT_CYAN
        )

        self.typing_entry.delete(0, tk.END)
        self.typing_entry.configure(bg=BG_CARD_LIGHT, fg=TEXT_MAIN)
        self.typing_entry.focus_set()

        # Start Timers
        if mode_name == "Time Attack":
            self.timer_seconds_left = self.settings["duration"]
            self.hud_timer_label.config(text=f"⏰ {self.timer_seconds_left}s", fg=ACCENT_YELLOW)
            self.schedule_timer_tick()
        elif mode_name == "Accuracy Streak":
            self.hud_timer_label.config(text=f"🔥 Sudden Death", fg=ACCENT_RED)
        elif mode_name == "Sentence Sprint":
            self.hud_timer_label.config(text="⏱ Sentence Wave", fg=ACCENT_GREEN)

        # Sound on sprint launch
        self.sound_countdown(final=True)

        # Spawn initial words
        self.spawn_word()
        if mode_name != "Sentence Sprint":
            self.after(1000, self.spawn_word)

        # Start Physics and Spawner Loops
        self.schedule_physics_tick()
        self.schedule_word_spawner()

    def update_shields_display(self):
        shield_icons = "🛡️" * self.shields + "🖤" * (self.max_shields - self.shields)
        color = ACCENT_GREEN if self.shields > 1 else ACCENT_RED
        self.hud_shields_label.config(text=f"SHIELDS: {shield_icons}", fg=color)

    def spawn_word(self):
        if not self.game_active:
            return

        cat = self.settings["category"]
        if self.current_mode == "Sentence Sprint":
            # Pick a short sentence phrase
            pool = [
                "Practice brings speed", "Code with passion", "Keep your focus sharp",
                "Speed requires accuracy", "Defend shield barrier", "Velocity is power"
            ]
            word_text = random.choice(pool)
        else:
            pool = WORD_BANKS.get(cat, WORD_BANKS["Medium"])
            # Try to pick a word whose first letter isn't already active (cleaner targeting)
            existing_first_chars = {w["text"][0].lower() for w in self.falling_words}
            candidates = [w for w in pool if w[0].lower() not in existing_first_chars]
            word_text = random.choice(candidates if candidates else pool)

        cw = getattr(self, "canvas_width", 900)
        # Avoid spawning right on borders
        min_x = 90
        max_x = max(cw - 180, 200)
        spawn_x = random.randint(min_x, max_x)

        # Slight speed variation for visual interest (+- 15%)
        speed_var = random.uniform(0.9, 1.15)
        word_obj = {
            "id": random.random(),
            "text": word_text,
            "x": spawn_x,
            "y": 25,
            "speed": self.base_speed * speed_var,
            "matched": 0,
            "highlight": False
        }
        self.falling_words.append(word_obj)

    def schedule_word_spawner(self):
        if not self.game_active:
            return

        # Cap max active words so screen isn't overwhelmed
        max_words = 4 if self.settings["difficulty"] == "Hard" else 3
        if self.current_mode == "Sentence Sprint":
            max_words = 2

        if len(self.falling_words) < max_words:
            self.spawn_word()

        self.spawn_job = self.after(self.spawn_interval_ms, self.schedule_word_spawner)

    def schedule_timer_tick(self):
        if not self.game_active or self.current_mode != "Time Attack":
            return
        if self.timer_seconds_left <= 0:
            self.finish_game("Time is up! Sprint Completed.")
            return

        self.hud_timer_label.config(text=f"⏰ {self.timer_seconds_left}s")

        if self.timer_seconds_left in [3, 2, 1]:
            self.sound_countdown(final=False)

        self.timer_seconds_left -= 1
        self.timer_job = self.after(1000, self.schedule_timer_tick)

    # ========================================================
    #                 PHYSICS & RENDER LOOP
    # ========================================================
    def schedule_physics_tick(self):
        if not self.game_active:
            return

        self.update_physics()
        self.render_arena()

        self.physics_job = self.after(30, self.schedule_physics_tick)

    def update_physics(self):
        cw = getattr(self, "canvas_width", 900)
        ch = getattr(self, "canvas_height", 460)
        laser_y = ch - 50

        # Update Screen Shake
        if self.shake_frames_left > 0:
            self.shake_offset_x = random.randint(-4, 4)
            self.shake_offset_y = random.randint(-4, 4)
            self.shake_frames_left -= 1
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

        # Move Falling Words
        words_to_keep = []
        for w in self.falling_words:
            w["y"] += w["speed"]

            # Check Laser Barrier Breach!
            if w["y"] >= laser_y:
                self.handle_laser_breach(w)
            else:
                words_to_keep.append(w)

        self.falling_words = words_to_keep

        # Update Spark Particles
        alive_particles = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.15 # Gravity
            p["life"] -= 0.05
            if p["life"] > 0:
                alive_particles.append(p)
        self.particles = alive_particles

        # Update Floating Score Popups
        alive_popups = []
        for pop in self.floating_popups:
            pop["y"] -= 1.2
            pop["life"] -= 0.035
            if pop["life"] > 0:
                alive_popups.append(pop)
        self.floating_popups = alive_popups

    def handle_laser_breach(self, breached_word):
        """Triggered when a falling word reaches the bottom laser barrier."""
        self.words_breached += 1
        self.streak_count = 0
        self.combo_label.config(text="COMBO: 0x", fg=TEXT_MUTED)

        # Sound & Shake
        self.sound_laser_breach()
        self.shake_frames_left = 7

        # Particle splash at laser line
        self.spawn_explosion_particles(breached_word["x"], self.laser_y, color=ACCENT_RED, count=15)
        self.spawn_floating_text(breached_word["x"], self.laser_y - 20, "-1 SHIELD!", ACCENT_RED)

        # Clear target lock if that was the target
        if self.active_target and self.active_target.get("id") == breached_word.get("id"):
            self.active_target = None
            self.typing_entry.delete(0, tk.END)
            self.target_reticle_label.config(
                text="🎯 TARGET: [ Target breached! Pick new word ]",
                fg=ACCENT_RED
            )

        # Deduct Shield
        self.shields -= 1
        self.update_shields_display()

        if self.shields <= 0:
            reason = "Laser shields breached! Defenses collapsed."
            if self.current_mode == "Accuracy Streak":
                reason = f"Sudden Death breach! Word '{breached_word['text']}' hit the barrier."
            self.sound_sudden_death_fail()
            self.finish_game(reason, play_victory_sound=False)

    def render_arena(self):
        """Draw falling words, laser line, reticles, and particle sparks on Canvas."""
        c = self.arena_canvas
        c.delete("all")

        cw = getattr(self, "canvas_width", 900)
        ch = getattr(self, "canvas_height", 460)
        laser_y = ch - 50
        ox = self.shake_offset_x
        oy = self.shake_offset_y

        # 1. Cyber Grid & Star Dust
        for y_line in range(40, laser_y, 70):
            c.create_line(0, y_line + oy, cw, y_line + oy, fill="#0d1527", width=1)
        for x_line in range(60, cw, 120):
            c.create_line(x_line + ox, 0, x_line + ox, laser_y + oy, fill="#0d1527", width=1)

        # 2. Electric Laser Barrier at Bottom
        laser_pulse_color = "#f43f5e" if (int(time.time() * 10) % 2 == 0) else ACCENT_RED
        # Laser glow bar
        c.create_line(0, laser_y - 1 + oy, cw, laser_y - 1 + oy, fill="#881337", width=4)
        c.create_line(0, laser_y + oy, cw, laser_y + oy, fill=laser_pulse_color, width=2)
        c.create_text(
            cw / 2 + ox, laser_y + 18 + oy,
            text="⚡ DEFENSE LASER BARRIER • PREVENT BREACH ⚡",
            font=("Segoe UI", 8, "bold"), fill="#f87171"
        )

        # 3. Draw Falling Words
        for w in self.falling_words:
            wx = w["x"] + ox
            wy = w["y"] + oy
            text = w["text"]
            matched_len = w.get("matched", 0)
            is_locked = (self.active_target and self.active_target.get("id") == w.get("id"))

            # Calculate word badge width
            char_w = 12 if len(text) > 12 else 14
            badge_w = max(len(text) * char_w + 30, 80)
            badge_h = 34

            x0 = wx - badge_w / 2
            y0 = wy - badge_h / 2
            x1 = wx + badge_w / 2
            y1 = wy + badge_h / 2

            # Proximity warning to laser line (turns pulsing red when near danger)
            dist_to_laser = laser_y - wy
            near_danger = dist_to_laser < 90

            # Badge Styling
            if is_locked:
                border_color = ACCENT_YELLOW
                bg_color = "#1e293b"
                border_width = 2
            elif near_danger:
                border_color = ACCENT_RED
                bg_color = "#3b0712"
                border_width = 2
            else:
                border_color = ACCENT_CYAN
                bg_color = "#0f172a"
                border_width = 1

            # Rounded pill badge
            c.create_rectangle(x0, y0, x1, y1, fill=bg_color, outline=border_color, width=border_width)

            # Locked Reticle Crosshair accents
            if is_locked:
                ret_len = 8
                # Top-left corner
                c.create_line(x0 - 4, y0 - 4, x0 - 4 + ret_len, y0 - 4, fill=ACCENT_YELLOW, width=2)
                c.create_line(x0 - 4, y0 - 4, x0 - 4, y0 - 4 + ret_len, fill=ACCENT_YELLOW, width=2)
                # Top-right corner
                c.create_line(x1 + 4, y0 - 4, x1 + 4 - ret_len, y0 - 4, fill=ACCENT_YELLOW, width=2)
                c.create_line(x1 + 4, y0 - 4, x1 + 4, y0 - 4 + ret_len, fill=ACCENT_YELLOW, width=2)
                # Bottom-left corner
                c.create_line(x0 - 4, y1 + 4, x0 - 4 + ret_len, y1 + 4, fill=ACCENT_YELLOW, width=2)
                c.create_line(x0 - 4, y1 + 4, x0 - 4, y1 + 4 - ret_len, fill=ACCENT_YELLOW, width=2)
                # Bottom-right corner
                c.create_line(x1 + 4, y1 + 4, x1 + 4 - ret_len, y1 + 4, fill=ACCENT_YELLOW, width=2)
                c.create_line(x1 + 4, y1 + 4, x1 + 4, y1 + 4 - ret_len, fill=ACCENT_YELLOW, width=2)

            # Split Text: Matched Prefix (Neon Emerald) vs Remaining Suffix (Cyan / White)
            matched_str = text[:matched_len]
            remaining_str = text[matched_len:]

            font_spec = ("Consolas", 14, "bold")
            if matched_len > 0:
                # Draw matched prefix on left, remaining on right
                full_w = len(text) * 10
                match_w = len(matched_str) * 10
                
                # Approximate start position
                start_x = wx - (full_w / 2) + 5
                
                # Matched part
                c.create_text(
                    start_x + (match_w / 2), wy,
                    text=matched_str, font=font_spec, fill=ACCENT_GREEN, anchor="center"
                )
                # Remaining part
                rem_w = len(remaining_str) * 10
                c.create_text(
                    start_x + match_w + (rem_w / 2), wy,
                    text=remaining_str, font=font_spec, fill=TEXT_MAIN, anchor="center"
                )
            else:
                c.create_text(
                    wx, wy, text=text, font=font_spec,
                    fill=ACCENT_CYAN if not near_danger else "#fca5a5", anchor="center"
                )

        # 4. Draw Floating Score Popups
        for pop in self.floating_popups:
            c.create_text(
                pop["x"] + ox, pop["y"] + oy,
                text=pop["text"], font=("Segoe UI", 12, "bold"), fill=pop["color"]
            )

        # 5. Draw Spark Particles
        for p in self.particles:
            sz = p.get("size", 3)
            c.create_oval(
                p["x"] - sz + ox, p["y"] - sz + oy,
                p["x"] + sz + ox, p["y"] + sz + oy,
                fill=p["color"], outline=""
            )

    def spawn_explosion_particles(self, x, y, color=ACCENT_CYAN, count=16):
        colors = [color, ACCENT_YELLOW, "#ffffff", ACCENT_GREEN]
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.5, 7.0)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 1.5,
                "size": random.randint(2, 4),
                "life": 1.0,
                "color": random.choice(colors)
            })

    def spawn_floating_text(self, x, y, text, color=ACCENT_YELLOW):
        self.floating_popups.append({
            "x": x,
            "y": y,
            "text": text,
            "color": color,
            "life": 1.0
        })

    # ========================================================
    #               INTERACTIVE TYPING INPUT HANDLER
    # ========================================================
    def on_key_release(self, event):
        if not self.game_active:
            return

        # Ignore non-character control keys
        if event.keysym in ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock", "Return"]:
            return

        typed = self.typing_entry.get()

        # Update live WPM & live accuracy HUD
        elapsed = max(time.time() - self.start_time, 0.5)
        live_chars = self.total_typed_chars + len(typed)
        live_wpm = (live_chars / 5.0) / (elapsed / 60.0)
        self.hud_wpm_label.config(text=f"{round(live_wpm, 1)} WPM")

        if not typed:
            # If user deleted everything, reset active target match length
            if self.active_target:
                self.active_target["matched"] = 0
            return

        # 1. Target Locking: If no target is locked, lock onto the falling word starting with typed
        if not self.active_target:
            candidates = [w for w in self.falling_words if w["text"].lower().startswith(typed.lower())]
            if candidates:
                # Prioritize candidate closest to the laser barrier (highest urgency)
                candidates.sort(key=lambda w: w["y"], reverse=True)
                self.active_target = candidates[0]
            else:
                # No word matches this starting character
                self.typing_entry.configure(bg="#450a0a", fg=ACCENT_RED)
                self.sound_typo()
                if self.current_mode == "Accuracy Streak":
                    self.sound_sudden_death_fail()
                    self.finish_game(f"Sudden Death typo! No falling word starts with '{typed}'.", play_victory_sound=False)
                return

        # 2. Check Match Against Locked Target
        target_text = self.active_target["text"]

        if target_text.lower().startswith(typed.lower()):
            # Valid partial match!
            self.active_target["matched"] = len(typed)
            self.typing_entry.configure(bg=BG_CARD_LIGHT, fg=ACCENT_GREEN)
            self.sound_key_click(len(typed))

            # Update target reticle status
            rem = target_text[len(typed):]
            self.target_reticle_label.config(
                text=f"🎯 LOCKED: [{typed.upper()}]{rem} • Type remaining letters to destroy!",
                fg=ACCENT_YELLOW
            )

            # Auto-complete word if user finished typing it completely!
            if len(typed) == len(target_text):
                self.complete_target_word()
        else:
            # Typo detected on locked word!
            self.typing_entry.configure(bg="#450a0a", fg=ACCENT_RED)
            self.sound_typo()

            if self.current_mode == "Accuracy Streak":
                self.sound_sudden_death_fail()
                self.finish_game(f"Sudden Death typo! Expected '{target_text}', typed '{typed}'.", play_victory_sound=False)

    def on_word_submit(self, event):
        """User pressed Space or Enter."""
        if not self.game_active:
            return "break"

        typed = self.typing_entry.get().strip()
        if not typed:
            return "break"

        if self.active_target and typed.lower() == self.active_target["text"].lower():
            self.complete_target_word()
        else:
            # Check if any falling word exactly matches
            matching = [w for w in self.falling_words if w["text"].lower() == typed.lower()]
            if matching:
                self.active_target = matching[0]
                self.complete_target_word()
            else:
                self.sound_typo()
                self.typing_entry.configure(bg="#450a0a", fg=ACCENT_RED)

        return "break"

    def complete_target_word(self):
        """Called when a falling word is typed completely."""
        if not self.active_target:
            return

        target = self.active_target
        word_text = target["text"]

        # Stats
        self.words_completed += 1
        self.total_typed_chars += len(word_text)
        self.streak_count += 1
        if self.streak_count > self.highest_streak:
            self.highest_streak = self.streak_count

        # Score calculation with combo multiplier
        combo_mult = 1.0 + min(self.streak_count * 0.1, 2.0)
        pts = int(len(word_text) * 15 * combo_mult)
        self.score += pts
        self.hud_score_label.config(text=f"{self.score} PTS")
        self.combo_label.config(text=f"COMBO: {round(combo_mult, 1)}x", fg=ACCENT_YELLOW)

        # Audio & Visual FX
        self.sound_word_complete()
        self.spawn_explosion_particles(target["x"], target["y"], color=ACCENT_CYAN, count=18)
        self.spawn_floating_text(target["x"], target["y"] - 15, f"+{pts} PTS", ACCENT_GREEN)

        # Remove from active falling list
        self.falling_words = [w for w in self.falling_words if w["id"] != target["id"]]
        self.active_target = None

        # Reset typing entry
        self.typing_entry.delete(0, tk.END)
        self.typing_entry.configure(bg=BG_CARD_LIGHT, fg=TEXT_MAIN)
        self.target_reticle_label.config(
            text="🎯 TARGET: [ Target destroyed! Pick next falling word ]",
            fg=ACCENT_CYAN
        )

        # In sentence sprint, spawn next sentence wave
        if self.current_mode == "Sentence Sprint" and len(self.falling_words) == 0:
            self.spawn_word()

    # ========================================================
    #                 GAME COMPLETION & RESULTS
    # ========================================================
    def finish_game(self, reason="Sprint Completed", play_victory_sound=True):
        self.stop_game()

        elapsed = max(time.time() - self.start_time, 0.5)
        minutes = elapsed / 60.0
        wpm = round((self.total_typed_chars / 5.0) / minutes, 1) if minutes > 0 else 0.0

        total_words = self.words_completed + self.words_breached
        accuracy = round((self.words_completed / max(total_words, 1)) * 100, 1) if total_words > 0 else 100.0

        # Save to Leaderboard
        self.save_score(self.current_mode, wpm, accuracy, self.score)

        if play_victory_sound:
            self.sound_victory()

        self.show_results_dialog(reason, wpm, accuracy, self.score, elapsed)

    def show_results_dialog(self, reason, wpm, accuracy, score, elapsed):
        dialog = tk.Toplevel(self)
        dialog.title("Sprint Results")
        dialog.geometry("460x480")
        dialog.configure(bg=BG_CARD)
        dialog.transient(self)
        dialog.grab_set()

        # Dialog Logo Header
        hdr_frame = tk.Frame(dialog, bg=BG_CARD)
        hdr_frame.pack(pady=(16, 5))

        if self.logo_img_dialog:
            tk.Label(hdr_frame, image=self.logo_img_dialog, bg=BG_CARD).pack()
        else:
            d_canvas = tk.Canvas(hdr_frame, width=54, height=54, bg=BG_CARD, highlightthickness=0)
            d_canvas.pack()
            self.draw_vector_logo(d_canvas, 54, 54)

        tk.Label(
            dialog, text="🏆 SPRINT RESULTS", font=("Segoe UI", 16, "bold"),
            fg=ACCENT_YELLOW, bg=BG_CARD
        ).pack(pady=(5, 3))

        tk.Label(
            dialog, text=reason, font=("Segoe UI", 10),
            fg=TEXT_MUTED, bg=BG_CARD, wraplength=380, justify="center"
        ).pack(pady=(0, 16))

        # Metrics Card
        card = tk.Frame(dialog, bg=BG_CARD_LIGHT, padx=22, pady=12)
        card.pack(fill=tk.X, padx=30, pady=(0, 18))

        rows = [
            ("Game Mode", self.current_mode),
            ("Typing Velocity", f"{wpm} WPM"),
            ("Accuracy", f"{accuracy}%"),
            ("Words Destroyed", f"{self.words_completed} words"),
            ("Laser Breaches", f"{self.words_breached} breached"),
            ("Final Score", f"{score} PTS"),
            ("Elapsed Time", f"{round(elapsed, 1)}s")
        ]
        if self.highest_streak > 0:
            rows.append(("Highest Combo", f"{self.highest_streak}x streak"))

        for label, val in rows:
            r = tk.Frame(card, bg=BG_CARD_LIGHT, pady=2)
            r.pack(fill=tk.X)
            tk.Label(r, text=label, font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_CARD_LIGHT).pack(side=tk.LEFT)
            tk.Label(r, text=val, font=("Segoe UI", 9, "bold"), fg=TEXT_MAIN, bg=BG_CARD_LIGHT).pack(side=tk.RIGHT)

        # Action Buttons
        btn_frame = tk.Frame(dialog, bg=BG_CARD)
        btn_frame.pack(fill=tk.X, padx=30)

        tk.Button(
            btn_frame, text="Play Again", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_CYAN, fg=BG_DARK, activebackground=TEXT_MAIN, bd=0,
            padx=15, pady=8, cursor="hand2",
            command=lambda: [dialog.destroy(), self.launch_game(self.current_mode)]
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        tk.Button(
            btn_frame, text="Main Menu", font=("Segoe UI", 10),
            bg=BG_CARD_LIGHT, fg=TEXT_MAIN, activebackground=ACCENT_RED, bd=0,
            padx=15, pady=8, cursor="hand2",
            command=lambda: [dialog.destroy(), self.show_view("menu")]
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))

    def stop_game(self):
        self.game_active = False
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        if self.physics_job:
            self.after_cancel(self.physics_job)
            self.physics_job = None
        if self.spawn_job:
            self.after_cancel(self.spawn_job)
            self.spawn_job = None

    def stop_and_return(self):
        self.stop_game()
        self.show_view("menu")

    # ========================================================
    #                     DATA PERSISTENCE
    # ========================================================
    def load_scores(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_score(self, mode, wpm, accuracy, score):
        scores = self.load_scores()
        scores.append({
            "mode": mode,
            "wpm": wpm,
            "accuracy": accuracy,
            "score": score,
            "date": time.strftime("%Y-%m-%d %H:%M")
        })
        scores.sort(key=lambda x: x.get("score", 0), reverse=True)
        scores = scores[:10]
        try:
            with open(HIGH_SCORE_FILE, "w") as f:
                json.dump(scores, f, indent=4)
        except Exception:
            pass

    def confirm_quit(self):
        if messagebox.askyesno("Quit Typing Sprint", "Are you sure you want to quit?"):
            self.stop_game()
            self.destroy()


if __name__ == "__main__":
    app = TypingSprintApp()
    app.mainloop()
