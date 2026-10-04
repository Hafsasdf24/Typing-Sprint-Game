/**
 * Typing Sprint - Web Audio Synthesizer
 * Pure procedural audio engine with no external audio file dependencies.
 */

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.muted = false;
    this.volume = 0.5;
    this.initialized = false;
  }

  init() {
    if (this.initialized) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
        this.initialized = true;
      }
    } catch (e) {
      console.warn('AudioContext not available:', e);
    }
  }

  ensureContext() {
    if (!this.initialized) {
      this.init();
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  setMuted(muted) {
    this.muted = !!muted;
  }

  setVolume(vol) {
    this.volume = Math.max(0, Math.min(1, vol));
  }

  /**
   * Ascending melodic click when typing correct letters of a targeted word
   */
  playKeypress(progress = 0, total = 5) {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    // Pentatonic scale frequency calculation based on letter progress
    const baseFreq = 440;
    const semitones = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21];
    const step = Math.min(progress, semitones.length - 1);
    const freq = baseFreq * Math.pow(2, semitones[step] / 12);

    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, now);
    osc.frequency.exponentialRampToValueAtTime(freq * 1.05, now + 0.05);

    const keyVol = this.volume * 0.25;
    gain.gain.setValueAtTime(keyVol, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 0.07);
  }

  /**
   * Shimmering chord burst when a word is completed successfully
   */
  playWordComplete(isPowerup = false) {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    const freqs = isPowerup ? [587.33, 739.99, 880, 1174.66] : [523.25, 659.25, 783.99, 1046.5];
    const duration = isPowerup ? 0.35 : 0.22;

    freqs.forEach((freq, i) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = isPowerup ? 'triangle' : 'sine';
      osc.frequency.setValueAtTime(freq, now + i * 0.02);

      const chordVol = (this.volume * 0.22) / freqs.length;
      gain.gain.setValueAtTime(0.0001, now + i * 0.02);
      gain.gain.linearRampToValueAtTime(chordVol, now + i * 0.02 + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + duration + i * 0.02);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now + i * 0.02);
      osc.stop(now + duration + i * 0.02 + 0.05);
    });
  }

  /**
   * Deep warning buzzer when a word hits the bottom barrier
   */
  playDamage() {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(140, now);
    osc.frequency.exponentialRampToValueAtTime(45, now + 0.28);

    const dmgVol = this.volume * 0.45;
    gain.gain.setValueAtTime(dmgVol, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.3);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 0.32);
  }

  /**
   * Sound effect when user mistypes or misses
   */
  playMistype() {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'triangle';
    osc.frequency.setValueAtTime(180, now);
    osc.frequency.linearRampToValueAtTime(120, now + 0.08);

    const misVol = this.volume * 0.18;
    gain.gain.setValueAtTime(misVol, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.09);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 0.1);
  }

  /**
   * High combo milestone chime
   */
  playComboPing(streak) {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    const freq = Math.min(1600, 800 + streak * 35);
    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, now);
    osc.frequency.exponentialRampToValueAtTime(freq * 1.5, now + 0.15);

    gain.gain.setValueAtTime(this.volume * 0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.2);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 0.22);
  }

  /**
   * Game Over descending motif
   */
  playGameOver() {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    const notes = [392.00, 349.23, 311.13, 261.63]; // G4, F4, Eb4, C4

    notes.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(freq, now + idx * 0.15);

      gain.gain.setValueAtTime(this.volume * 0.25, now + idx * 0.15);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.15 + 0.28);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now + idx * 0.15);
      osc.stop(now + idx * 0.15 + 0.3);
    });
  }
}

export const sound = new SoundEngine();
