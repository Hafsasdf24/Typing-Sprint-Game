/**
 * Typing Sprint - Main Application Controller
 * Connects GameEngine, WpmChart, SoundEngine, StorageManager, and UI interactions.
 */

import { storage, DIFFICULTY_PRESETS } from './storage.js';
import { sound } from './audio.js';
import { parseCustomWords } from './words.js';
import { GameEngine } from './game.js';
import { WpmChart } from './chart.js';

class TypingSprintApp {
  constructor() {
    this.settings = storage.getSettings();
    this.customWords = storage.getCustomWords();

    this.cacheDOMElements();
    this.initAudioSettings();
    this.initGameEngine();
    this.initWpmChart();
    this.bindEvents();
    this.applySettingsToUI();
  }

  cacheDOMElements() {
    // HUD elements
    this.dom = {
      activeListBadge: document.getElementById('active-list-badge'),
      hudWpm: document.getElementById('hud-wpm'),
      hudAccuracy: document.getElementById('hud-accuracy'),
      hudStreak: document.getElementById('hud-streak'),
      hudScore: document.getElementById('hud-score'),
      hudLives: document.getElementById('hud-lives'),

      // Header buttons
      btnSoundToggle: document.getElementById('btn-sound-toggle'),
      btnOpenHistory: document.getElementById('btn-open-history'),
      btnOpenSettings: document.getElementById('btn-open-settings'),

      // Arena & overlays
      arenaContainer: document.getElementById('arena-container'),
      particleCanvas: document.getElementById('particle-canvas'),
      startOverlay: document.getElementById('start-overlay'),
      pauseOverlay: document.getElementById('pause-overlay'),
      gameoverOverlay: document.getElementById('gameover-overlay'),

      // Live typing box
      liveTargetText: document.getElementById('live-target-text'),
      livePlaceholder: document.getElementById('live-placeholder'),

      // Start screen controls
      btnStartGame: document.getElementById('btn-start-game'),
      quickWordlistPills: document.getElementById('quick-wordlist-pills'),
      quickDifficultyPills: document.getElementById('quick-difficulty-pills'),

      // Pause screen controls
      btnResumeGame: document.getElementById('btn-resume-game'),
      btnRestartFromPause: document.getElementById('btn-restart-from-pause'),

      // Game over screen controls
      resWpm: document.getElementById('res-wpm'),
      resPeakWpm: document.getElementById('res-peak-wpm'),
      resAccuracy: document.getElementById('res-accuracy'),
      resCleared: document.getElementById('res-cleared'),
      resStreak: document.getElementById('res-streak'),
      resScore: document.getElementById('res-score'),
      btnPlayAgain: document.getElementById('btn-play-again'),
      btnViewChartFromGameover: document.getElementById('btn-view-chart-from-gameover'),

      // History Modal
      modalHistory: document.getElementById('modal-history'),
      btnCloseHistory: document.getElementById('btn-close-history'),
      btnDoneHistory: document.getElementById('btn-done-history'),
      chartCanvas: document.getElementById('wpm-chart-canvas'),
      chartTooltip: document.getElementById('chart-tooltip'),
      chartFilterPills: document.getElementById('chart-filter-pills'),
      histBestWpm: document.getElementById('hist-best-wpm'),
      histAvgWpm: document.getElementById('hist-avg-wpm'),
      histTotalWords: document.getElementById('hist-total-words'),
      histTotalRuns: document.getElementById('hist-total-runs'),
      historyTableBody: document.getElementById('history-table-body'),
      btnExportHistory: document.getElementById('btn-export-history'),
      btnClearHistory: document.getElementById('btn-clear-history'),

      // Settings Modal
      modalSettings: document.getElementById('modal-settings'),
      btnCloseSettings: document.getElementById('btn-close-settings'),
      btnSaveSettings: document.getElementById('btn-save-settings'),
      settingsDifficultyOptions: document.getElementById('settings-difficulty-options'),
      customSlidersBox: document.getElementById('custom-sliders-box'),
      sliderSpeed: document.getElementById('slider-speed'),
      sliderSpeedVal: document.getElementById('slider-speed-val'),
      sliderSpawn: document.getElementById('slider-spawn'),
      sliderSpawnVal: document.getElementById('slider-spawn-val'),
      sliderLives: document.getElementById('slider-lives'),
      sliderLivesVal: document.getElementById('slider-lives-val'),

      // Word list options in settings
      settingsWordlistOptions: document.getElementById('settings-wordlist-options'),
      customWordsEditor: document.getElementById('custom-words-editor'),
      customWordsTextarea: document.getElementById('custom-words-textarea'),
      customWordCountBadge: document.getElementById('custom-word-count-badge'),
      presetLoadWeb: document.getElementById('preset-load-web'),
      presetLoadUrdu: document.getElementById('preset-load-urdu'),
      presetLoadScience: document.getElementById('preset-load-science'),
      presetClearWords: document.getElementById('preset-clear-words'),

      // Audio & feedback controls
      sliderVolume: document.getElementById('slider-volume'),
      sliderVolVal: document.getElementById('slider-vol-val'),
      checkScreenShake: document.getElementById('check-screen-shake'),
      checkSoundEnabled: document.getElementById('check-sound-enabled')
    };
  }

  initAudioSettings() {
    sound.setMuted(!this.settings.soundEnabled);
    sound.setVolume(this.settings.soundVolume);
    this.updateSoundButtonUI();
  }

  initGameEngine() {
    this.game = new GameEngine(this.dom.arenaContainer, this.dom.particleCanvas, {
      settings: this.settings,
      customWords: this.customWords,
      callbacks: {
        onStatsUpdate: (stats) => this.onGameStatsUpdate(stats),
        onStateChange: (state) => this.onGameStateChange(state),
        onGameOver: (summary) => this.onGameOver(summary)
      }
    });

    this.game.applyConfig(this.settings, this.customWords);
    this.updateLivesDisplay(this.game.maxLives, this.game.maxLives);
  }

  initWpmChart() {
    this.chart = new WpmChart(this.dom.chartCanvas, this.dom.chartTooltip);
  }

  bindEvents() {
    // Global Keyboard Typing Handler
    window.addEventListener('keydown', (e) => this.handleGlobalKeyDown(e));

    // Header buttons
    this.dom.btnSoundToggle.addEventListener('click', () => this.toggleSound());
    this.dom.btnOpenHistory.addEventListener('click', () => this.openHistoryModal());
    this.dom.btnOpenSettings.addEventListener('click', () => this.openSettingsModal());

    // Start screen actions
    this.dom.btnStartGame.addEventListener('click', () => this.startGame());
    this.bindQuickPills();

    // Pause screen actions
    this.dom.btnResumeGame.addEventListener('click', () => this.game.resume());
    this.dom.btnRestartFromPause.addEventListener('click', () => this.startGame());

    // Game over screen actions
    this.dom.btnPlayAgain.addEventListener('click', () => this.startGame());
    this.dom.btnViewChartFromGameover.addEventListener('click', () => {
      this.dom.gameoverOverlay.classList.add('hidden');
      this.openHistoryModal();
    });

    // History modal actions
    this.dom.btnCloseHistory.addEventListener('click', () => this.closeHistoryModal());
    this.dom.btnDoneHistory.addEventListener('click', () => this.closeHistoryModal());
    this.dom.btnExportHistory.addEventListener('click', () => this.exportHistoryData());
    this.dom.btnClearHistory.addEventListener('click', () => this.clearHistoryData());
    this.bindChartFilters();

    // Settings modal actions
    this.dom.btnCloseSettings.addEventListener('click', () => this.closeSettingsModal());
    this.dom.btnSaveSettings.addEventListener('click', () => this.saveSettingsFromUI());
    this.bindSettingsFormEvents();
  }

  bindQuickPills() {
    // Quick Word List Pills on Start Screen
    this.dom.quickWordlistPills.querySelectorAll('.select-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        this.dom.quickWordlistPills.querySelectorAll('.select-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        const listKey = pill.getAttribute('data-list');
        this.settings.wordList = listKey;
        storage.saveSettings(this.settings);
        this.game.applyConfig(this.settings, this.customWords);
        this.updateBadge();
        this.syncSettingsUIWithState();
      });
    });

    // Quick Difficulty Pills on Start Screen
    this.dom.quickDifficultyPills.querySelectorAll('.select-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        this.dom.quickDifficultyPills.querySelectorAll('.select-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        const diffKey = pill.getAttribute('data-diff');
        this.settings.difficulty = diffKey;
        storage.saveSettings(this.settings);
        this.game.applyConfig(this.settings, this.customWords);
        this.updateLivesDisplay(this.game.maxLives, this.game.maxLives);
        this.syncSettingsUIWithState();
      });
    });
  }

  bindChartFilters() {
    this.dom.chartFilterPills.querySelectorAll('.select-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        this.dom.chartFilterPills.querySelectorAll('.select-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        const range = pill.getAttribute('data-range');
        this.chart.setData(storage.getHistory(), range);
      });
    });
  }

  bindSettingsFormEvents() {
    // Difficulty Option Cards
    this.dom.settingsDifficultyOptions.querySelectorAll('.setting-option-card').forEach(card => {
      card.addEventListener('click', () => {
        this.dom.settingsDifficultyOptions.querySelectorAll('.setting-option-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        const diff = card.getAttribute('data-diff');
        this.dom.customSlidersBox.style.display = (diff === 'custom') ? 'flex' : 'none';
      });
    });

    // Word List Option Cards
    this.dom.settingsWordlistOptions.querySelectorAll('.setting-option-card').forEach(card => {
      card.addEventListener('click', () => {
        this.dom.settingsWordlistOptions.querySelectorAll('.setting-option-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        const list = card.getAttribute('data-list');
        this.dom.customWordsEditor.style.display = (list === 'custom') ? 'flex' : 'none';
      });
    });

    // Sliders live value updates
    this.dom.sliderSpeed.addEventListener('input', (e) => {
      this.dom.sliderSpeedVal.textContent = `${e.target.value}x`;
    });
    this.dom.sliderSpawn.addEventListener('input', (e) => {
      this.dom.sliderSpawnVal.textContent = `${e.target.value}s`;
    });
    this.dom.sliderLives.addEventListener('input', (e) => {
      this.dom.sliderLivesVal.textContent = e.target.value;
    });
    this.dom.sliderVolume.addEventListener('input', (e) => {
      const pct = Math.round(e.target.value * 100);
      this.dom.sliderVolVal.textContent = `${pct}%`;
      sound.setVolume(parseFloat(e.target.value));
    });

    // Custom words textarea live counter
    this.dom.customWordsTextarea.addEventListener('input', () => {
      this.updateCustomWordBadgeCount();
    });

    // Preset words buttons
    this.dom.presetLoadWeb.addEventListener('click', () => {
      const webPreset = 'react, angular, vue, svelte, nextjs, typescript, vite, nodejs, express, mongodb, graphql, docker, kubernetes, tailwind, redux, prisma, redis, postman, git, github';
      this.dom.customWordsTextarea.value = webPreset;
      this.updateCustomWordBadgeCount();
    });

    this.dom.presetLoadUrdu.addEventListener('click', () => {
      const urduPreset = 'ishq, junoon, mohabbat, zindagani, armaan, dastaan, afsana, firaaq, wafa, deewangi, jazbaat, sukoon, khushboo, tamanna, tasawwur, hasrat, chahat, bekhudi, rooh, khamoshi';
      this.dom.customWordsTextarea.value = urduPreset;
      this.updateCustomWordBadgeCount();
    });

    this.dom.presetLoadScience.addEventListener('click', () => {
      const sciPreset = 'gravity, quantum, entropy, nebula, galaxy, electron, photon, relativity, supernova, asteroid, telescope, chromosome, ecosystem, catalyst, thermodynamics';
      this.dom.customWordsTextarea.value = sciPreset;
      this.updateCustomWordBadgeCount();
    });

    this.dom.presetClearWords.addEventListener('click', () => {
      this.dom.customWordsTextarea.value = '';
      this.updateCustomWordBadgeCount();
    });
  }

  updateCustomWordBadgeCount() {
    const parsed = parseCustomWords(this.dom.customWordsTextarea.value);
    this.dom.customWordCountBadge.textContent = `${parsed.length} words loaded`;
  }

  handleGlobalKeyDown(e) {
    // If a modal is open or focusing an input, let default behaviors occur
    const isModalOpen = this.dom.modalHistory.classList.contains('open') || 
                        this.dom.modalSettings.classList.contains('open');
    if (isModalOpen) {
      if (e.key === 'Escape') {
        this.closeHistoryModal();
        this.closeSettingsModal();
      }
      return;
    }

    // Toggle Sound shortcut 'm' or 'M'
    if (e.key === 'm' || e.key === 'M') {
      if (this.game.state === 'idle' || this.game.state === 'paused') {
        this.toggleSound();
        return;
      }
    }

    // Start / Play Again with Space or Enter
    if (this.game.state === 'idle') {
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault();
        this.startGame();
        return;
      }
    } else if (this.game.state === 'gameover') {
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault();
        this.startGame();
        return;
      }
    } else if (this.game.state === 'paused') {
      if (e.key === 'Escape') {
        e.preventDefault();
        this.game.resume();
        return;
      }
    } else if (this.game.state === 'running') {
      if (e.key === 'Escape') {
        e.preventDefault();
        this.game.pause();
        return;
      }

      // Backspace clears target lock
      if (e.key === 'Backspace') {
        e.preventDefault();
        if (this.game.targetedWord) {
          this.game.targetedWord.typedIndex = 0;
          this.game.targetedWord.domEl?.classList.remove('is-targeted');
          this.game.updateWordDOM(this.game.targetedWord);
          this.game.targetedWord = null;
          this.onGameStatsUpdate({ targetedWord: null });
        }
        return;
      }

      // Printable single character inputs
      if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
        e.preventDefault();
        this.game.handleKeyInput(e.key);
      }
    }
  }

  startGame() {
    this.dom.startOverlay.classList.add('hidden');
    this.dom.pauseOverlay.classList.add('hidden');
    this.dom.gameoverOverlay.classList.add('hidden');
    this.game.start();
  }

  toggleSound() {
    this.settings.soundEnabled = !this.settings.soundEnabled;
    storage.saveSettings(this.settings);
    sound.setMuted(!this.settings.soundEnabled);
    this.updateSoundButtonUI();
  }

  updateSoundButtonUI() {
    if (this.settings.soundEnabled) {
      this.dom.btnSoundToggle.classList.remove('active');
      this.dom.btnSoundToggle.title = 'Sound FX Enabled (Press M)';
      this.dom.btnSoundToggle.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
        </svg>
      `;
    } else {
      this.dom.btnSoundToggle.classList.add('active');
      this.dom.btnSoundToggle.title = 'Sound FX Muted (Press M)';
      this.dom.btnSoundToggle.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
          <line x1="23" y1="9" x2="17" y2="15"></line>
          <line x1="17" y1="9" x2="23" y2="15"></line>
        </svg>
      `;
    }
  }

  onGameStatsUpdate(stats) {
    if (stats.wpm !== undefined) this.dom.hudWpm.textContent = stats.wpm;
    if (stats.accuracy !== undefined) this.dom.hudAccuracy.textContent = `${stats.accuracy}%`;
    if (stats.streak !== undefined) this.dom.hudStreak.textContent = `${stats.streak}x`;
    if (stats.score !== undefined) this.dom.hudScore.textContent = stats.score;

    if (stats.lives !== undefined && stats.maxLives !== undefined) {
      this.updateLivesDisplay(stats.lives, stats.maxLives);
    }

    // Live Target typing box preview
    if (stats.targetedWord) {
      const typed = stats.targetedWord.text.slice(0, stats.targetedWord.typedIndex);
      const remaining = stats.targetedWord.text.slice(stats.targetedWord.typedIndex);
      this.dom.liveTargetText.innerHTML = `<span style="color:var(--primary-cyan)">${typed}</span><span style="color:#ffffff">${remaining}</span>`;
      this.dom.livePlaceholder.style.display = 'none';
    } else {
      this.dom.liveTargetText.textContent = '';
      this.dom.livePlaceholder.style.display = 'inline';
    }
  }

  updateLivesDisplay(currentLives, maxLives) {
    this.dom.hudLives.innerHTML = '';
    for (let i = 0; i < maxLives; i++) {
      const pip = document.createElement('span');
      pip.className = `life-pip ${i >= currentLives ? 'lost' : ''}`;
      this.dom.hudLives.appendChild(pip);
    }
  }

  onGameStateChange(state) {
    if (state === 'running') {
      this.dom.startOverlay.classList.add('hidden');
      this.dom.pauseOverlay.classList.add('hidden');
      this.dom.gameoverOverlay.classList.add('hidden');
    } else if (state === 'paused') {
      this.dom.pauseOverlay.classList.remove('hidden');
    } else if (state === 'idle') {
      this.dom.startOverlay.classList.remove('hidden');
    }
  }

  onGameOver(summary) {
    // Save to storage
    storage.saveGameRecord(summary);

    // Populate Game Over overlay
    this.dom.resWpm.textContent = summary.wpm;
    this.dom.resPeakWpm.textContent = summary.peakWpm;
    this.dom.resAccuracy.textContent = `${summary.accuracy}%`;
    this.dom.resCleared.textContent = summary.wordsCleared;
    this.dom.resStreak.textContent = summary.longestStreak;
    this.dom.resScore.textContent = summary.score;

    this.dom.gameoverOverlay.classList.remove('hidden');
  }

  // ==================== HISTORY MODAL & ANALYTICS ====================
  openHistoryModal() {
    if (this.game.state === 'running') {
      this.game.pause();
    }

    const history = storage.getHistory();
    const stats = storage.getAllTimeStats();

    // Fill KPI summary cards
    const wpms = history.map(h => h.wpm || 0);
    const avgWpm = wpms.length > 0 ? Math.round(wpms.reduce((a, b) => a + b, 0) / wpms.length) : 0;

    this.dom.histBestWpm.textContent = `${stats.bestWpm || 0} WPM`;
    this.dom.histAvgWpm.textContent = `${avgWpm} WPM`;
    this.dom.histTotalWords.textContent = stats.totalWordsCleared || 0;
    this.dom.histTotalRuns.textContent = history.length;

    // Populate table of runs (newest first)
    this.dom.historyTableBody.innerHTML = '';
    const reversed = [...history].reverse();

    if (reversed.length === 0) {
      this.dom.historyTableBody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align:center; color:var(--text-muted); padding:20px;">
            No sprint records found. Play a round to start logging!
          </td>
        </tr>
      `;
    } else {
      reversed.slice(0, 30).forEach(run => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${run.dateFormatted || 'Recent'}</td>
          <td><span style="color:${DIFFICULTY_PRESETS[run.difficulty]?.badgeColor || '#fff'}">${run.difficulty?.toUpperCase()}</span></td>
          <td>${run.wordList?.toUpperCase()}</td>
          <td style="color:var(--primary-cyan); font-weight:700;">${run.wpm}</td>
          <td>${run.accuracy}%</td>
          <td style="color:var(--accent-gold);">${run.score || 0}</td>
        `;
        this.dom.historyTableBody.appendChild(tr);
      });
    }

    this.dom.modalHistory.classList.add('open');

    // Trigger chart render on the next frame so container dimensions are known
    setTimeout(() => {
      this.chart.setData(history, 'all');
    }, 50);
  }

  closeHistoryModal() {
    this.dom.modalHistory.classList.remove('open');
  }

  exportHistoryData() {
    const history = storage.getHistory();
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(history, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `typing_sprint_history_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  }

  clearHistoryData() {
    if (confirm('Are you sure you want to reset all your typing sprint history and WPM records?')) {
      storage.clearHistory();
      this.openHistoryModal(); // Refresh modal view
    }
  }

  // ==================== SETTINGS MODAL ====================
  openSettingsModal() {
    if (this.game.state === 'running') {
      this.game.pause();
    }
    this.syncSettingsUIWithState();
    this.dom.modalSettings.classList.add('open');
  }

  closeSettingsModal() {
    this.dom.modalSettings.classList.remove('open');
  }

  syncSettingsUIWithState() {
    // Difficulty cards
    this.dom.settingsDifficultyOptions.querySelectorAll('.setting-option-card').forEach(card => {
      if (card.getAttribute('data-diff') === this.settings.difficulty) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });

    this.dom.customSlidersBox.style.display = (this.settings.difficulty === 'custom') ? 'flex' : 'none';

    // Sliders
    if (this.settings.customConfig) {
      this.dom.sliderSpeed.value = this.settings.customConfig.speedMultiplier || 1.6;
      this.dom.sliderSpeedVal.textContent = `${this.dom.sliderSpeed.value}x`;
      this.dom.sliderSpawn.value = this.settings.customConfig.spawnIntervalSec || 2.0;
      this.dom.sliderSpawnVal.textContent = `${this.dom.sliderSpawn.value}s`;
      this.dom.sliderLives.value = this.settings.customConfig.maxLives || 4;
      this.dom.sliderLivesVal.textContent = this.dom.sliderLives.value;
    }

    // Word list cards
    this.dom.settingsWordlistOptions.querySelectorAll('.setting-option-card').forEach(card => {
      if (card.getAttribute('data-list') === this.settings.wordList) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });

    this.dom.customWordsEditor.style.display = (this.settings.wordList === 'custom') ? 'flex' : 'none';
    this.dom.customWordsTextarea.value = this.customWords.join(', ');
    this.updateCustomWordBadgeCount();

    // Volume & Feedback
    this.dom.sliderVolume.value = this.settings.soundVolume;
    this.dom.sliderVolVal.textContent = `${Math.round(this.settings.soundVolume * 100)}%`;
    this.dom.checkScreenShake.checked = !!this.settings.screenShake;
    this.dom.checkSoundEnabled.checked = !!this.settings.soundEnabled;

    this.updateBadge();
  }

  saveSettingsFromUI() {
    // Selected difficulty
    const activeDiffCard = this.dom.settingsDifficultyOptions.querySelector('.setting-option-card.active');
    if (activeDiffCard) {
      this.settings.difficulty = activeDiffCard.getAttribute('data-diff');
    }

    // Custom config
    if (this.settings.difficulty === 'custom') {
      this.settings.customConfig = {
        speedMultiplier: parseFloat(this.dom.sliderSpeed.value),
        spawnIntervalSec: parseFloat(this.dom.sliderSpawn.value),
        maxLives: parseInt(this.dom.sliderLives.value, 10)
      };
    }

    // Selected word list
    const activeListCard = this.dom.settingsWordlistOptions.querySelector('.setting-option-card.active');
    if (activeListCard) {
      this.settings.wordList = activeListCard.getAttribute('data-list');
    }

    // Custom words
    if (this.settings.wordList === 'custom') {
      const parsed = parseCustomWords(this.dom.customWordsTextarea.value);
      this.customWords = parsed.length > 0 ? parsed : ['challenge', 'sprint', 'velocity'];
      storage.saveCustomWords(this.customWords);
    }

    // Audio & Feedback
    this.settings.soundVolume = parseFloat(this.dom.sliderVolume.value);
    this.settings.soundEnabled = this.dom.checkSoundEnabled.checked;
    this.settings.screenShake = this.dom.checkScreenShake.checked;

    storage.saveSettings(this.settings);
    this.initAudioSettings();
    this.game.applyConfig(this.settings, this.customWords);
    this.updateLivesDisplay(this.game.maxLives, this.game.maxLives);
    this.updateBadge();

    // Sync start screen pills
    this.dom.quickWordlistPills.querySelectorAll('.select-pill').forEach(pill => {
      pill.classList.toggle('active', pill.getAttribute('data-list') === this.settings.wordList);
    });
    this.dom.quickDifficultyPills.querySelectorAll('.select-pill').forEach(pill => {
      pill.classList.toggle('active', pill.getAttribute('data-diff') === this.settings.difficulty);
    });

    this.closeSettingsModal();
  }

  applySettingsToUI() {
    this.updateBadge();
    this.syncSettingsUIWithState();

    // Sync quick pills on start screen
    this.dom.quickWordlistPills.querySelectorAll('.select-pill').forEach(pill => {
      pill.classList.toggle('active', pill.getAttribute('data-list') === this.settings.wordList);
    });
    this.dom.quickDifficultyPills.querySelectorAll('.select-pill').forEach(pill => {
      pill.classList.toggle('active', pill.getAttribute('data-diff') === this.settings.difficulty);
    });
  }

  updateBadge() {
    const listLabels = {
      programming: 'PROGRAMMING',
      romanUrdu: 'ROMAN URDU',
      english: 'ENGLISH CORE',
      cyberpunk: 'CYBERPUNK',
      custom: 'CUSTOM LIST'
    };
    this.dom.activeListBadge.textContent = listLabels[this.settings.wordList] || 'PROGRAMMING';
  }
}

// Instantiate and launch when DOM is ready
window.addEventListener('DOMContentLoaded', () => {
  window.app = new TypingSprintApp();
});
