// The island's glow line (DESIGN.md, "Recording Overlay"): a red line of light
// that breathes with the voice.
//
// Mic levels arrive as 16 spectrum buckets at ~23 Hz (overlay.rs `emit_levels`).
// Driving CSS straight from those events steps the line every ~43 ms, which reads
// as jagged. Instead a follower turns them into a continuous signal, stepped on
// every display frame:
//
// - Automatic gain: loudness is measured against a slowly tracked noise floor
//   and recent peak, so a quiet voice still fills the line and a loud one never
//   pins it.
// - A spring (not a lerp) chases that loudness, eased first so each input step
//   arrives gradually: fast attack, slow release, a touch of overshoot. Speed
//   changes continuously, so the line never shows a corner.
// - Syllable onsets (a sudden rise in loudness) flash the line brighter and
//   decay quickly, so the light follows the cadence of speech, not just volume.
//
// The line itself is a horizontal gradient: widest and hottest at the center,
// tapering to nothing, with a faint texture from the voice's spectrum.

const SPEECH_BUCKETS = 12; // ~400 Hz - 3 kHz of the 400 - 4000 Hz buckets
const TALLY: RGB = [255, 98, 66]; // --color-tally-hud
const HOT: RGB = [255, 222, 208]; // the filament at a syllable's peak

type RGB = [number, number, number];

export interface VoiceFrame {
  /** Smoothed loudness, 0..1 (may overshoot slightly above 1). */
  level: number;
  /** Onset flash, 0..1, decaying after each syllable. */
  pulse: number;
  /** Smoothed spectrum over the speech buckets, each 0..1. */
  spectrum: number[];
}

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

/** Exponential approach factor for a time constant, independent of frame rate. */
const approach = (dt: number, tau: number) => 1 - Math.exp(-dt / tau);

export class VoiceFollower {
  private floor = 0.12;
  private peak = 0.35;
  private target = 0;
  private eased = 0;
  private lastTarget = 0;
  private level = 0;
  private velocity = 0;
  private pulse = 0;
  private pendingOnset = 0;
  private rawSpectrum = new Array<number>(SPEECH_BUCKETS).fill(0);
  private spectrum = new Array<number>(SPEECH_BUCKETS).fill(0);
  private sinceFeed = 0;

  /** Take one mic-level event (16 buckets, 0..1). */
  feed(buckets: readonly number[]): void {
    const speech = buckets.slice(0, SPEECH_BUCKETS).map((v) => clamp01(v || 0));
    // Loudness = mean of the four strongest bands: robust to one noisy band,
    // but much more sensitive than a mean over all of them.
    const top = [...speech].sort((a, b) => b - a).slice(0, 4);
    const energy = top.reduce((sum, v) => sum + v, 0) / top.length;

    // Noise floor: falls quickly to quiet moments, creeps up very slowly, so
    // speech never gets mistaken for the room.
    const dt = Math.max(this.sinceFeed, 1 / 60);
    this.sinceFeed = 0;
    this.floor +=
      (energy - this.floor) * approach(dt, energy < this.floor ? 0.25 : 12);
    // Peak: jumps to new highs at once, relaxes over a few seconds, and never
    // drops so low that silence gets amplified into motion.
    this.peak =
      energy > this.peak
        ? energy
        : Math.max(
            this.floor + 0.18,
            this.peak - (this.peak - energy) * approach(dt, 2.5),
          );

    const norm = clamp01(
      (energy - this.floor - 0.03) / (this.peak - this.floor),
    );
    this.target = Math.pow(norm, 0.8);
    this.pendingOnset = Math.max(
      this.pendingOnset,
      this.target - this.lastTarget,
    );
    this.lastTarget = this.target;
    this.rawSpectrum = speech;
  }

  /** Advance by `dt` seconds and return the frame to draw. */
  step(dt: number): VoiceFrame {
    this.sinceFeed += dt;
    // Sub-step so the spring stays stable after a dropped frame.
    let remaining = Math.min(dt, 0.1);
    while (remaining > 0) {
      const h = Math.min(remaining, 1 / 240);
      remaining -= h;
      // The target itself steps at the input rate; easing it first means the
      // spring never gets an acceleration kick, so even speed changes are smooth.
      this.eased += (this.target - this.eased) * approach(h, 0.035);
      const rising = this.eased > this.level;
      // Attack settles in ~100 ms, release in ~220 ms (DESIGN.md, Motion).
      const omega = 2 * Math.PI * (rising ? 4.5 : 2.2);
      const zeta = rising ? 0.72 : 0.9;
      const accel =
        omega * omega * (this.eased - this.level) -
        2 * zeta * omega * this.velocity;
      this.velocity += accel * h;
      this.level += this.velocity * h;
    }
    this.level = Math.max(0, this.level);

    // An onset bigger than a small wobble flashes the line; the flash decays
    // over ~140 ms so consecutive syllables read as separate beats.
    if (this.pendingOnset > 0.08) {
      this.pulse = Math.max(
        this.pulse,
        clamp01((this.pendingOnset - 0.08) * 2.2),
      );
    }
    this.pendingOnset = 0;
    this.pulse *= 1 - approach(dt, 0.14);

    const k = approach(dt, 0.09);
    this.spectrum = this.spectrum.map(
      (v, i) => v + (this.rawSpectrum[i] - v) * k,
    );

    return { level: this.level, pulse: this.pulse, spectrum: this.spectrum };
  }
}

const mix = (a: RGB, b: RGB, t: number): RGB =>
  a.map((v, i) => Math.round(v + (b[i] - v) * t)) as RGB;

/**
 * The line as a CSS gradient. `still` drops the spectral texture and the onset
 * flash (Reduce Motion) but keeps the width, which is the level itself.
 */
export function glowGradient(
  frame: VoiceFrame,
  { samples = 25, still = false } = {},
): string {
  const level = clamp01(frame.level);
  const pulse = still ? 0 : frame.pulse;
  // At silence an ember stays lit in the center: the island is listening.
  const halfWidth = 0.1 + 0.9 * level;
  const peakSpectrum = Math.max(0.05, ...frame.spectrum);
  const stops: string[] = [];
  for (let i = 0; i < samples; i++) {
    const x = (i / (samples - 1)) * 2 - 1; // -1..1, center 0
    const e = clamp01(1 - Math.abs(x) / halfWidth);
    const envelope = e * e * (3 - 2 * e); // smoothstep: tapered, no hard ends
    // Low frequencies sit in the middle, highs toward the tips.
    const bucket = Math.min(
      frame.spectrum.length - 1,
      Math.floor(Math.abs(x) * frame.spectrum.length),
    );
    const texture = still
      ? 1
      : 0.72 + 0.28 * (frame.spectrum[bucket] / peakSpectrum);
    const brightness = 0.5 + 0.5 * Math.min(1, level * 1.15 + pulse);
    const alpha = envelope * texture * brightness;
    const [r, g, b] = mix(TALLY, HOT, 0.4 * pulse * envelope);
    stops.push(
      `rgba(${r},${g},${b},${alpha.toFixed(3)}) ${((i / (samples - 1)) * 100).toFixed(1)}%`,
    );
  }
  return `linear-gradient(90deg,${stops.join(",")})`;
}

/**
 * Run the follower on every display frame, writing `--voice` (the gradient)
 * and `--voice-energy` (0..1, for the bloom) onto `el`. Returns a stop function.
 */
export function runVoiceGlow(
  el: HTMLElement,
  follower: VoiceFollower,
  still: boolean,
): () => void {
  let raf = 0;
  let last = performance.now();
  const frame = (now: number) => {
    const dt = Math.min(0.1, (now - last) / 1000);
    last = now;
    const f = follower.step(dt);
    el.style.setProperty("--voice", glowGradient(f, { still }));
    el.style.setProperty(
      "--voice-energy",
      clamp01(0.3 + 0.6 * f.level + (still ? 0 : 0.4 * f.pulse)).toFixed(3),
    );
    raf = requestAnimationFrame(frame);
  };
  raf = requestAnimationFrame(frame);
  return () => {
    cancelAnimationFrame(raf);
    el.style.removeProperty("--voice");
    el.style.removeProperty("--voice-energy");
  };
}
