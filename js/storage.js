/**
 * Typing Sprint - LocalStorage & State Persistence
 */

import { DEFAULT_CUSTOM_WORDS } from './words.js';

const STORAGE_KEYS = {
  SETTINGS: 'typing_sprint_settings_v1',
  HISTORY: 'typing_sprint_history_v1',
  CUSTOM_WORDS: 'typing_sprint_custom_words_v1',
  STATS: 'typing_sprint_all_time_stats_v1'
};

export const DEFAULT_SETTINGS = {
  difficulty: 'normal', // 'relaxed', 'normal', 'sprint', 'nightmare', 'custom'
  wordList: 'programming', // 'programming', 'romanUrdu', 'english', 'cyberpunk', 'custom'
  soundEnabled: true,
  soundVolume: 0.6,
  screenShake: true,
  particlesEnabled: true,
  customConfig: {
    speedMultiplier: 1.6,
    spawnIntervalSec: 2.0,
    maxLives: 4
  }
};

export const DIFFICULTY_PRESETS = {
  relaxed: {
    label: 'Relaxed',
    desc: 'Gentle speed, 5 lives, slow waves. Perfect for warm-up.',
    speedMultiplier: 1.0,
    spawnIntervalSec: 2.8,
    maxLives: 5,
    scoreMultiplier: 1.0,
    badgeColor: '#00f5d4'
  },
  normal: {
    label: 'Standard',
    desc: 'Balanced speed and rhythm with 4 lives.',
    speedMultiplier: 1.6,
    spawnIntervalSec: 2.0,
    maxLives: 4,
    scoreMultiplier: 1.5,
    badgeColor: '#3a86ff'
  },
  sprint: {
    label: 'Sprint (Hard)',
    desc: 'Fast pace, rapid spawns, 3 lives. For sharp typists.',
    speedMultiplier: 2.4,
    spawnIntervalSec: 1.35,
    maxLives: 3,
    scoreMultiplier: 2.2,
    badgeColor: '#ff007a'
  },
  nightmare: {
    label: 'Nightmare',
    desc: 'Extreme velocity, relentless waves, only 2 lives!',
    speedMultiplier: 3.3,
    spawnIntervalSec: 0.95,
    maxLives: 2,
    scoreMultiplier: 3.5,
    badgeColor: '#ffbe0b'
  },
  custom: {
    label: 'Custom',
    desc: 'Tuned precisely to your preference.',
    speedMultiplier: 1.6,
    spawnIntervalSec: 2.0,
    maxLives: 4,
    scoreMultiplier: 1.2,
    badgeColor: '#c77dff'
  }
};

class StorageManager {
  // Load settings
  getSettings() {
    try {
      const raw = localStorage.getItem(STORAGE_KEYS.SETTINGS);
      if (raw) {
        const parsed = JSON.parse(raw);
        return { ...DEFAULT_SETTINGS, ...parsed };
      }
    } catch (e) {
      console.warn('Failed to parse settings from storage:', e);
    }
    return { ...DEFAULT_SETTINGS };
  }

  // Save settings
  saveSettings(settings) {
    try {
      localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
    } catch (e) {
      console.error('Failed to save settings:', e);
    }
  }

  // Get custom words array
  getCustomWords() {
    try {
      const raw = localStorage.getItem(STORAGE_KEYS.CUSTOM_WORDS);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch (e) {
      console.warn('Failed to read custom words:', e);
    }
    return [...DEFAULT_CUSTOM_WORDS];
  }

  // Save custom words
  saveCustomWords(words) {
    try {
      localStorage.setItem(STORAGE_KEYS.CUSTOM_WORDS, JSON.stringify(words));
    } catch (e) {
      console.error('Failed to save custom words:', e);
    }
  }

  // Get full history records
  getHistory() {
    try {
      const raw = localStorage.getItem(STORAGE_KEYS.HISTORY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) return parsed;
      }
    } catch (e) {
      console.warn('Failed to read history:', e);
    }
    return [];
  }

  // Append new game record
  saveGameRecord(record) {
    try {
      const history = this.getHistory();
      const newRecord = {
        id: 'rec_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
        timestamp: Date.now(),
        dateFormatted: new Intl.DateTimeFormat('default', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }).format(new Date()),
        ...record
      };

      history.push(newRecord);
      // Keep up to 250 past runs
      if (history.length > 250) {
        history.shift();
      }
      localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(history));

      // Update all-time stats
      this.updateAllTimeStats(newRecord);
      return newRecord;
    } catch (e) {
      console.error('Failed to save game record:', e);
      return null;
    }
  }

  // Update cumulative statistics
  updateAllTimeStats(record) {
    const stats = this.getAllTimeStats();
    stats.gamesPlayed = (stats.gamesPlayed || 0) + 1;
    stats.totalWordsCleared = (stats.totalWordsCleared || 0) + (record.wordsCleared || 0);
    stats.bestWpm = Math.max(stats.bestWpm || 0, record.wpm || 0);
    stats.highestScore = Math.max(stats.highestScore || 0, record.score || 0);
    stats.longestStreak = Math.max(stats.longestStreak || 0, record.longestStreak || 0);

    try {
      localStorage.setItem(STORAGE_KEYS.STATS, JSON.stringify(stats));
    } catch (e) {}
  }

  getAllTimeStats() {
    try {
      const raw = localStorage.getItem(STORAGE_KEYS.STATS);
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    return {
      gamesPlayed: 0,
      totalWordsCleared: 0,
      bestWpm: 0,
      highestScore: 0,
      longestStreak: 0
    };
  }

  // Clear all game history
  clearHistory() {
    try {
      localStorage.removeItem(STORAGE_KEYS.HISTORY);
      localStorage.removeItem(STORAGE_KEYS.STATS);
    } catch (e) {}
  }
}

export const storage = new StorageManager();
