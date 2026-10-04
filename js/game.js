/**
 * Typing Sprint - Core Game Engine
 * Manages falling words, typing targeting, collisions, particles, and live WPM.
 */

import { getRandomWord } from './words.js';
import { sound } from './audio.js';
import { DIFFICULTY_PRESETS } from './storage.js';

export class GameEngine {
  constructor(arenaContainer, particleCanvas, options = {}) {
    this.container = arenaContainer;
    this.canvas = particleCanvas;
    this.ctx = particleCanvas.getContext('2d');

    this.settings = options.settings || {};
    this.customWords = options.customWords || [];
    this.callbacks = options.callbacks || {};

    // Game state
    this.state = 'idle'; // 'idle', 'running', 'paused', 'gameover'
    this.words = []; // Active Word objects
    this.targetedWord = null;
    this.particles = [];
    this.floatingTexts = [];

    // Stats
    this.score = 0;
    this.lives = 4;
    this.maxLives = 4;
    this.streak = 0;
    this.longestStreak = 0;
    this.correctChars = 0;
    this.totalKeystrokes = 0;
    this.wordsCleared = 0;
    this.wordsMissed = 0;
    this.startTime = 0;
    this.elapsedTime = 0;
    this.wpm = 0;
    this.peakWpm = 0;
    this.accuracy = 100;

    // Powerups / Timers
    this.activeEffects = {
      frostUntil: 0,
      doubleScoreUntil: 0
    };

    // Spawn parameters
    this.lastSpawnTime = 0;
    this.spawnInterval = 2000;
    this.fallSpeedBase = 1.0;
    this.scoreMultiplier = 1.0;

    // Animation frame handle
    this.animId = null;
    this.lastFrameTime = 0;

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    if (!this.canvas || !this.container) return;
    const rect = this.container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.resetTransform?.();
    this.ctx.scale(dpr, dpr);
    this.arenaWidth = rect.width;
    this.arenaHeight = rect.height;
  }

  applyConfig(settings, customWords) {
    this.settings = settings;
    this.customWords = customWords || [];

    const preset = DIFFICULTY_PRESETS[settings.difficulty] || DIFFICULTY_PRESETS.normal;

    if (settings.difficulty === 'custom' && settings.customConfig) {
      this.fallSpeedBase = (settings.customConfig.speedMultiplier || 1.6) * 65; // px per second
      this.spawnInterval = (settings.customConfig.spawnIntervalSec || 2.0) * 1000;
      this.maxLives = settings.customConfig.maxLives || 4;
      this.scoreMultiplier = 1.2;
    } else {
      this.fallSpeedBase = preset.speedMultiplier * 60; // px per sec
      this.spawnInterval = preset.spawnIntervalSec * 1000;
      this.maxLives = preset.maxLives;
      this.scoreMultiplier = preset.scoreMultiplier;
    }
  }

  start() {
    this.reset();
    this.state = 'running';
    this.startTime = performance.now();
    this.lastFrameTime = performance.now();
    this.lastSpawnTime = performance.now() - this.spawnInterval + 800; // spawn first word quickly

    this.loop = this.tick.bind(this);
    this.animId = requestAnimationFrame(this.loop);

    if (this.callbacks.onStateChange) {
      this.callbacks.onStateChange(this.state);
    }
  }

  pause() {
    if (this.state !== 'running') return;
    this.state = 'paused';
    cancelAnimationFrame(this.animId);
    if (this.callbacks.onStateChange) {
      this.callbacks.onStateChange(this.state);
    }
  }

  resume() {
    if (this.state !== 'paused') return;
    this.state = 'running';
    this.lastFrameTime = performance.now();
    this.animId = requestAnimationFrame(this.loop);
    if (this.callbacks.onStateChange) {
      this.callbacks.onStateChange(this.state);
    }
  }

  reset() {
    cancelAnimationFrame(this.animId);
    this.clearAllWordElements();
    this.words = [];
    this.targetedWord = null;
    this.particles = [];
    this.floatingTexts = [];

    this.score = 0;
    this.lives = this.maxLives;
    this.streak = 0;
    this.longestStreak = 0;
    this.correctChars = 0;
    this.totalKeystrokes = 0;
    this.wordsCleared = 0;
    this.wordsMissed = 0;
    this.wpm = 0;
    this.peakWpm = 0;
    this.accuracy = 100;
    this.elapsedTime = 0;
    this.activeEffects.frostUntil = 0;
    this.activeEffects.doubleScoreUntil = 0;

    this.updateStatsDOM();
  }

  clearAllWordElements() {
    const existing = this.container.querySelectorAll('.falling-word');
    existing.forEach(el => el.remove());
  }

  /**
   * Main Game Loop
   */
  tick(currentTime) {
    if (this.state !== 'running') return;

    const delta = Math.min((currentTime - this.lastFrameTime) / 1000, 0.1); // in seconds
    this.lastFrameTime = currentTime;
    this.elapsedTime = (currentTime - this.startTime) / 1000;

    this.update(delta, currentTime);
    this.renderCanvas();

    this.animId = requestAnimationFrame(this.loop);
  }

  update(delta, currentTime) {
    // 1. Spawning words
    const isFrostActive = currentTime < this.activeEffects.frostUntil;
    const currentSpawnInterval = isFrostActive ? this.spawnInterval * 1.5 : this.spawnInterval;

    // Slightly accelerate spawn rate over time up to 35%
    const timeSpeedBonus = Math.min(0.35, (this.elapsedTime / 180));
    const effectiveInterval = currentSpawnInterval * (1 - timeSpeedBonus * 0.4);

    if (currentTime - this.lastSpawnTime >= effectiveInterval) {
      this.spawnWord();
      this.lastSpawnTime = currentTime;
    }

    // 2. Move active words
    const dangerBaseline = this.arenaHeight * 0.88;
    const speedMultiplier = isFrostActive ? 0.4 : 1.0;

    for (let i = this.words.length - 1; i >= 0; i--) {
      const wordObj = this.words[i];
      const effectiveSpeed = wordObj.speed * this.fallSpeedBase * (1 + timeSpeedBonus * 0.5) * speedMultiplier;
      wordObj.y += effectiveSpeed * delta;

      // Update DOM element position
      wordObj.domEl.style.transform = `translate3d(${wordObj.x}px, ${wordObj.y}px, 0)`;

      // Proximity warning to danger line
      const distToDanger = dangerBaseline - wordObj.y;
      if (distToDanger < 90 && distToDanger > 0) {
        wordObj.domEl.classList.add('in-danger');
      } else {
        wordObj.domEl.classList.remove('in-danger');
      }

      // Check collision with ground/laser
      if (wordObj.y >= dangerBaseline) {
        this.handleWordHitGround(wordObj, i);
      }
    }

    // 3. Update WPM & live stats
    this.calculateStats();

    // 4. Update particles & floating texts
    this.updateParticles(delta);

    // 5. Trigger callbacks for UI
    this.updateStatsDOM();
  }

  spawnWord() {
    if (this.words.length >= 8) return; // Prevent overcrowding

    const text = getRandomWord(this.settings.wordList, this.customWords);
    if (!text) return;

    // Check if duplicate of an existing active word to avoid ambiguity
    const exists = this.words.some(w => w.text === text);
    if (exists && Math.random() > 0.15) return;

    // Random powerup chance (10% chance)
    let powerupType = null;
    const rand = Math.random();
    if (rand < 0.04) powerupType = 'frost';
    else if (rand < 0.07) powerupType = 'nuke';
    else if (rand < 0.09) powerupType = 'heal';
    else if (rand < 0.12) powerupType = 'double';

    // Calculate X coordinate avoiding tight clumping
    const wordWidthApprox = Math.max(90, text.length * 15 + 40);
    const minX = 25;
    const maxX = Math.max(minX + 20, this.arenaWidth - wordWidthApprox - 25);

    // Try finding non-colliding column
    let bestX = minX + Math.random() * (maxX - minX);
    for (let attempts = 0; attempts < 5; attempts++) {
      const candidateX = minX + Math.random() * (maxX - minX);
      const isTooClose = this.words.some(w => Math.abs(w.x - candidateX) < 110 && w.y < 120);
      if (!isTooClose) {
        bestX = candidateX;
        break;
      }
    }

    // Create DOM representation
    const el = document.createElement('div');
    el.className = `falling-word ${powerupType ? 'powerup-' + powerupType : ''}`;

    let iconPrefix = '';
    if (powerupType === 'frost') iconPrefix = '<span class="pw-icon">❄️</span>';
    if (powerupType === 'nuke') iconPrefix = '<span class="pw-icon">💥</span>';
    if (powerupType === 'heal') iconPrefix = '<span class="pw-icon">💚</span>';
    if (powerupType === 'double') iconPrefix = '<span class="pw-icon">⭐</span>';

    el.innerHTML = `
      <div class="word-card">
        <span class="target-bracket left">[</span>
        ${iconPrefix}
        <span class="typed-part"></span><span class="untyped-part">${text}</span>
        <span class="target-bracket right">]</span>
      </div>
    `;

    this.container.appendChild(el);

    const wordObj = {
      id: 'w_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
      text: text,
      typedIndex: 0,
      x: bestX,
      y: -35,
      speed: 0.85 + Math.random() * 0.35, // slight speed variance
      powerup: powerupType,
      domEl: el
    };

    this.words.push(wordObj);
  }

  /**
   * Handle user typing character
   */
  handleKeyInput(char) {
    if (this.state !== 'running') return;
    const lowerChar = char.toLowerCase();
    this.totalKeystrokes++;

    // If we have an active target
    if (this.targetedWord) {
      const expectedChar = this.targetedWord.text[this.targetedWord.typedIndex]?.toLowerCase();

      if (lowerChar === expectedChar) {
        // Correct next letter!
        this.correctChars++;
        this.targetedWord.typedIndex++;
        this.updateWordDOM(this.targetedWord);

        sound.playKeypress(this.targetedWord.typedIndex, this.targetedWord.text.length);

        // Little spark on the word
        this.createSparks(
          this.targetedWord.x + (this.targetedWord.typedIndex * 12),
          this.targetedWord.y + 20,
          '#00f5d4',
          4
        );

        // Check if word completed
        if (this.targetedWord.typedIndex >= this.targetedWord.text.length) {
          this.completeWord(this.targetedWord);
          this.targetedWord = null;
        }
      } else {
        // Mistype on current target
        this.handleMistype(this.targetedWord);
      }
      return;
    }

    // No target currently: find matching words
    // Candidates starting with typed letter
    const candidates = this.words.filter(w => w.text[0]?.toLowerCase() === lowerChar);

    if (candidates.length > 0) {
      // Pick candidate lowest on screen (closest to danger)
      candidates.sort((a, b) => b.y - a.y);
      const chosen = candidates[0];

      this.targetedWord = chosen;
      this.targetedWord.typedIndex = 1;
      this.correctChars++;
      this.updateWordDOM(this.targetedWord);
      this.targetedWord.domEl.classList.add('is-targeted');

      sound.playKeypress(1, chosen.text.length);

      // Check if 1-letter word (rare, but supported)
      if (this.targetedWord.typedIndex >= chosen.text.length) {
        this.completeWord(this.targetedWord);
        this.targetedWord = null;
      }
    } else {
      // Missed key: no word starts with this
      this.handleMistype(null);
    }
  }

  handleMistype(wordObj) {
    this.streak = 0;
    sound.playMistype();

    if (wordObj && wordObj.domEl) {
      wordObj.domEl.classList.add('mistake-shake');
      setTimeout(() => wordObj.domEl?.classList.remove('mistake-shake'), 250);
    }

    if (this.settings.screenShake) {
      this.container.classList.add('screen-shake');
      setTimeout(() => this.container.classList.remove('screen-shake'), 180);
    }

    this.calculateStats();
    this.updateStatsDOM();
  }

  updateWordDOM(wordObj) {
    if (!wordObj || !wordObj.domEl) return;
    const typedPart = wordObj.text.slice(0, wordObj.typedIndex);
    const untypedPart = wordObj.text.slice(wordObj.typedIndex);

    const typedEl = wordObj.domEl.querySelector('.typed-part');
    const untypedEl = wordObj.domEl.querySelector('.untyped-part');

    if (typedEl) typedEl.textContent = typedPart;
    if (untypedEl) untypedEl.textContent = untypedPart;
  }

  completeWord(wordObj) {
    this.wordsCleared++;
    this.streak++;
    if (this.streak > this.longestStreak) {
      this.longestStreak = this.streak;
    }

    // Combo multiplier calculation
    let comboMultiplier = 1.0;
    if (this.streak >= 25) comboMultiplier = 3.0;
    else if (this.streak >= 15) comboMultiplier = 2.5;
    else if (this.streak >= 10) comboMultiplier = 2.0;
    else if (this.streak >= 5) comboMultiplier = 1.5;

    // Check 2x score powerup
    const isDoubleActive = performance.now() < this.activeEffects.doubleScoreUntil;
    const doubleMultiplier = isDoubleActive ? 2.0 : 1.0;

    // Base score based on word length & difficulty
    const basePts = wordObj.text.length * 20;
    const earnedPts = Math.round(basePts * this.scoreMultiplier * comboMultiplier * doubleMultiplier);
    this.score += earnedPts;

    // Audio & visuals
    sound.playWordComplete(!!wordObj.powerup);
    if (this.streak > 0 && this.streak % 10 === 0) {
      sound.playComboPing(this.streak);
    }

    // Particles explosion
    this.createExplosion(wordObj.x + 60, wordObj.y + 15, wordObj.powerup ? '#ffbe0b' : '#00f5d4');

    // Floating score notification
    const comboText = comboMultiplier > 1 ? ` (${comboMultiplier}x)` : '';
    this.addFloatingText(`+${earnedPts}${comboText}`, wordObj.x + 30, wordObj.y, '#00f5d4');

    // Handle Powerup activation
    if (wordObj.powerup) {
      this.triggerPowerup(wordObj.powerup, wordObj.x, wordObj.y);
    }

    // Remove from array and DOM
    this.removeWord(wordObj);
  }

  triggerPowerup(type, x, y) {
    if (type === 'frost') {
      this.activeEffects.frostUntil = performance.now() + 6500;
      this.addFloatingText('❄️ CHILL ACTIVATED (-60% SPEED)', x - 40, y - 25, '#48cae4', 20);
      this.createShockwave(x, y, '#48cae4');
    } else if (type === 'nuke') {
      this.addFloatingText('💥 EMP NUKE: FIELD CLEARED!', x - 40, y - 25, '#ffbe0b', 22);
      this.clearAllActiveWordsWithBonus();
      this.createShockwave(this.arenaWidth / 2, this.arenaHeight / 2, '#ffbe0b');
    } else if (type === 'heal') {
      if (this.lives < this.maxLives) {
        this.lives++;
        this.addFloatingText('💚 +1 SHIELD REPAIRED', x - 20, y - 25, '#06d6a0', 18);
      } else {
        this.score += 500;
        this.addFloatingText('⭐ MAX SHIELD BONUS: +500 PTS', x - 40, y - 25, '#06d6a0', 18);
      }
    } else if (type === 'double') {
      this.activeEffects.doubleScoreUntil = performance.now() + 8500;
      this.addFloatingText('⭐ 2X SCORE MULTIPLIER ACTIVE!', x - 40, y - 25, '#ff007a', 20);
    }
  }

  clearAllActiveWordsWithBonus() {
    const list = [...this.words];
    list.forEach(w => {
      this.createExplosion(w.x + 50, w.y + 15, '#ffbe0b', 16);
      this.score += w.text.length * 10;
      this.wordsCleared++;
      this.removeWord(w);
    });
    this.targetedWord = null;
  }

  handleWordHitGround(wordObj, index) {
    this.wordsMissed++;
    this.lives--;
    this.streak = 0;

    sound.playDamage();

    // Red sparks at collision point
    this.createExplosion(wordObj.x + 50, this.arenaHeight * 0.88, '#ff0055', 24);
    this.addFloatingText('BREACH! -1 LIFE', wordObj.x, this.arenaHeight * 0.86, '#ff0055', 18);

    if (this.settings.screenShake) {
      this.container.classList.add('screen-shake-heavy');
      setTimeout(() => this.container.classList.remove('screen-shake-heavy'), 300);
    }

    if (this.targetedWord === wordObj) {
      this.targetedWord = null;
    }

    this.removeWord(wordObj);

    if (this.lives <= 0) {
      this.gameOver();
    }
  }

  removeWord(wordObj) {
    const idx = this.words.indexOf(wordObj);
    if (idx !== -1) {
      this.words.splice(idx, 1);
    }
    if (wordObj.domEl) {
      wordObj.domEl.classList.add('word-destroyed');
      setTimeout(() => wordObj.domEl?.remove(), 250);
    }
  }

  calculateStats() {
    if (this.elapsedTime > 0) {
      const minutes = this.elapsedTime / 60;
      // Standard WPM: (correct characters / 5) / minutes
      this.wpm = Math.max(0, Math.round((this.correctChars / 5) / minutes));
      if (this.wpm > this.peakWpm) {
        this.peakWpm = this.wpm;
      }
    }

    if (this.totalKeystrokes > 0) {
      this.accuracy = Math.round((this.correctChars / this.totalKeystrokes) * 100);
    } else {
      this.accuracy = 100;
    }
  }

  updateStatsDOM() {
    if (this.callbacks.onStatsUpdate) {
      this.callbacks.onStatsUpdate({
        score: this.score,
        lives: this.lives,
        maxLives: this.maxLives,
        wpm: this.wpm,
        peakWpm: this.peakWpm,
        accuracy: this.accuracy,
        streak: this.streak,
        longestStreak: this.longestStreak,
        wordsCleared: this.wordsCleared,
        targetedWord: this.targetedWord
      });
    }
  }

  gameOver() {
    this.state = 'gameover';
    cancelAnimationFrame(this.animId);
    sound.playGameOver();

    const summary = {
      score: this.score,
      wpm: this.wpm,
      peakWpm: this.peakWpm,
      accuracy: this.accuracy,
      wordsCleared: this.wordsCleared,
      wordsMissed: this.wordsMissed,
      longestStreak: this.longestStreak,
      difficulty: this.settings.difficulty,
      wordList: this.settings.wordList,
      durationSec: Math.round(this.elapsedTime)
    };

    if (this.callbacks.onGameOver) {
      this.callbacks.onGameOver(summary);
    }
    if (this.callbacks.onStateChange) {
      this.callbacks.onStateChange(this.state);
    }
  }

  // ==================== PARTICLE ENGINE ====================

  createSparks(x, y, color = '#00f5d4', count = 6) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 25 + Math.random() * 55;
      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 15,
        color,
        size: 2 + Math.random() * 2.5,
        life: 0.35 + Math.random() * 0.25,
        maxLife: 0.5
      });
    }
  }

  createExplosion(x, y, color = '#00f5d4', count = 22) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 50 + Math.random() * 120;
      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        color,
        size: 2.5 + Math.random() * 3.5,
        life: 0.45 + Math.random() * 0.4,
        maxLife: 0.7
      });
    }
  }

  createShockwave(x, y, color = '#00f5d4') {
    this.particles.push({
      x,
      y,
      vx: 0,
      vy: 0,
      isWave: true,
      radius: 5,
      maxRadius: 180,
      color,
      life: 0.6,
      maxLife: 0.6
    });
  }

  addFloatingText(text, x, y, color = '#00f5d4', size = 15) {
    this.floatingTexts.push({
      text,
      x: Math.max(20, Math.min(x, this.arenaWidth - 140)),
      y,
      color,
      size,
      vy: -55,
      life: 0.85,
      maxLife: 0.85
    });
  }

  updateParticles(delta) {
    // Update sparks/bursts
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life -= delta;
      if (p.life <= 0) {
        this.particles.splice(i, 1);
        continue;
      }
      if (p.isWave) {
        p.radius += (p.maxRadius / p.maxLife) * delta;
      } else {
        p.x += p.vx * delta;
        p.y += p.vy * delta;
        p.vy += 110 * delta; // gravity
      }
    }

    // Update floating texts
    for (let i = this.floatingTexts.length - 1; i >= 0; i--) {
      const t = this.floatingTexts[i];
      t.life -= delta;
      if (t.life <= 0) {
        this.floatingTexts.splice(i, 1);
        continue;
      }
      t.y += t.vy * delta;
    }
  }

  renderCanvas() {
    this.ctx.clearRect(0, 0, this.arenaWidth, this.arenaHeight);

    // 1. Render Shockwaves & Sparks
    this.particles.forEach(p => {
      const alpha = Math.max(0, p.life / p.maxLife);
      if (p.isWave) {
        this.ctx.save();
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        this.ctx.strokeStyle = p.color;
        this.ctx.globalAlpha = alpha * 0.7;
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
        this.ctx.restore();
      } else {
        this.ctx.save();
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, p.size * alpha, 0, Math.PI * 2);
        this.ctx.fillStyle = p.color;
        this.ctx.globalAlpha = alpha;
        this.ctx.shadowColor = p.color;
        this.ctx.shadowBlur = 6;
        this.ctx.fill();
        this.ctx.restore();
      }
    });

    // 2. Render Floating Text
    this.floatingTexts.forEach(t => {
      const alpha = Math.max(0, t.life / t.maxLife);
      this.ctx.save();
      this.ctx.font = `700 ${t.size}px "Space Grotesk", sans-serif`;
      this.ctx.fillStyle = t.color;
      this.ctx.globalAlpha = alpha;
      this.ctx.shadowColor = t.color;
      this.ctx.shadowBlur = 8;
      this.ctx.fillText(t.text, t.x, t.y);
      this.ctx.restore();
    });
  }
}
