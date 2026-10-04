# Typing Sprint ⚡

A high-velocity falling words arcade typing challenge with official esports logo branding. Words cascade from the top of the arena toward the laser barrier — lock on and type them before they breach your shields!

---

## 🚀 How to Run

### 1. Desktop GUI Edition (Recommended)
- **Direct Run:** Double-click [`Run_Typing_Sprint.bat`](file:///c:/Users/Usman%20Computers/OneDrive/Desktop/P3/Run_Typing_Sprint.bat).
- **Desktop Shortcut:** Double-click [`create_desktop_shortcut.py`](file:///c:/Users/Usman%20Computers/OneDrive/Desktop/P3/create_desktop_shortcut.py) once to pin the game with its custom logo icon directly onto your Windows Desktop.

### 2. Web Browser Edition
- Double-click [`index.html`](file:///c:/Users/Usman%20Computers/OneDrive/Desktop/P3/index.html) to open in Chrome, Edge, or Firefox.

---

## 🎮 Gameplay & Mechanics

1. **Cascading Words**: Words descend from the top of the arena toward the bottom laser line.
2. **Dynamic Target Lock**: Type the first letter of any active word to lock your targeting reticle onto it. The typed prefix illuminates with a glowing neon accent.
3. **Power-Ups**:
   - ❄️ **Frost**: Slows all falling words by 60% for 6.5 seconds.
   - 💥 **EMP Nuke**: Instantly clears all words on screen with massive bonus points.
   - 💚 **Shield Repair**: Restores +1 lost shield life (or +500 PTS at full shields).
   - ⭐ **2x Multiplier**: Doubles your score on every word eliminated for 8.5 seconds.
4. **Combos & Streaks**: Consecutive words without typos trigger scaling score multipliers (up to 3x!).
5. **Breach Warning**: When words enter the danger zone near the bottom, they pulse bright red. Breaching the baseline costs 1 shield life and triggers screen shake and damage feedback.

---

## ⚙️ Settings & Customization

- **Difficulty Levels**:
  - **Relaxed**: Gentle falling speed, 5 shields, relaxed spawn intervals.
  - **Standard**: Balanced arcade pace, 4 shields, 1.5x score bonus.
  - **Sprint (Hard)**: Rapid velocity, 3 shields, 2.2x score multiplier.
  - **Nightmare**: High velocity, 2 shields, 3.5x score multiplier.
  - **Custom Sliders**: Tune falling speed (0.6x – 4.0x), spawn rate (0.8s – 4.0s), and shields (1 – 10).
- **Word Lists**:
  - 💻 **Programming Terms**: JavaScript, Python, algorithms, async, hooks, recursion, syntax, memory.
  - 🌙 **Roman Urdu**: Rich vocabulary (`khushamdeed`, `zindagi`, `shukriya`, `mohabbat`, `intezaar`, `khawab`, etc.).
  - ⚡ **English Core**: Diverse vocabulary.
  - 🚀 **Cyberpunk**: Sci-fi and matrix terminology.
  - ✍️ **Custom Word List**: Type or paste any comma/space/line separated word list with live count and preset loaders.
- **Audio Synthesizer**: Procedural Web Audio API sound effects with melodic pitch climbing on each correct keystroke.

---

## 📈 Interactive WPM Velocity History Chart

- **High-DPI Canvas Chart**: Visualizes your Words Per Minute (WPM) across sessions with a smooth glowing bezier spline and gradient fill.
- **Interactive Tooltips**: Hover over data points to inspect date, time, WPM, accuracy, score, and difficulty mode.
- **Analytics KPIs**: Track All-time Best WPM, Average WPM, Total Words Cleared, and Runs Logged.
- **Data Export**: Export your complete typing history as JSON or reset history at any time.
