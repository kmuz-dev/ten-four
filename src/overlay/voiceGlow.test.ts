import assert from "node:assert/strict";
import { glowGradient, VoiceFollower } from "./voiceGlow";

const FRAME = 1 / 60;
const quiet = new Array(16).fill(0.1);
const speech = new Array(16).fill(0).map((_, i) => (i < 8 ? 0.7 : 0.3));
const softSpeech = speech.map((v) => v * 0.55);

/** Feed `buckets` at ~23 Hz for `seconds`, stepping at 60 fps. Returns levels. */
function run(f: VoiceFollower, buckets: number[], seconds: number) {
  const levels: number[] = [];
  let untilFeed = 0;
  for (let t = 0; t < seconds; t += FRAME) {
    if (untilFeed <= 0) {
      f.feed(buckets);
      untilFeed = 1 / 23;
    }
    untilFeed -= FRAME;
    levels.push(f.step(FRAME).level);
  }
  return levels;
}

// Silence stays still: the room never animates the line.
{
  const f = new VoiceFollower();
  const levels = run(f, quiet, 3);
  assert.ok(Math.max(...levels.slice(-60)) < 0.05, "silence stays near 0");
}

// Speech lifts the line quickly (attack), and it falls back more slowly.
{
  const f = new VoiceFollower();
  run(f, quiet, 1);
  const up = run(f, speech, 0.15);
  assert.ok(up[up.length - 1] > 0.6, "attack reaches most of the way in 150ms");
  const down = run(f, quiet, 0.12);
  assert.ok(down[down.length - 1] > 0.15, "release is slower than attack");
}

// Smooth, even though input steps at 23 Hz: the line never moves more than a
// fifth of its width in a frame, and its speed never changes abruptly (a speed
// change is a visible corner; that is what "jagged" was).
{
  const f = new VoiceFollower();
  run(f, quiet, 1);
  const levels = [
    ...run(f, speech, 0.4),
    ...run(f, quiet, 0.2),
    ...run(f, speech, 0.3),
  ];
  const speed = levels.slice(1).map((v, i) => v - levels[i]);
  const maxStep = Math.max(...speed.map(Math.abs));
  const maxKink = Math.max(
    ...speed.slice(1).map((v, i) => Math.abs(v - speed[i])),
  );
  assert.ok(maxStep < 0.21, `max per-frame move ${maxStep.toFixed(3)}`);
  assert.ok(maxKink < 0.08, `max per-frame speed change ${maxKink.toFixed(3)}`);
}

// Automatic gain: a soft voice still fills most of the line once it settles.
{
  const f = new VoiceFollower();
  run(f, quiet, 1);
  const levels = run(f, softSpeech, 4);
  assert.ok(levels[levels.length - 1] > 0.6, "soft speech is amplified");
}

// Syllable onsets flash; a steady tone does not keep flashing.
{
  const f = new VoiceFollower();
  run(f, quiet, 1);
  f.feed(speech);
  assert.ok(f.step(FRAME).pulse > 0.3, "onset flashes");
  run(f, speech, 1);
  assert.ok(f.step(FRAME).pulse < 0.05, "a held vowel settles");
}

// Gradient: symmetric, brightest in the middle, faded at the tips.
{
  const css = glowGradient({
    level: 0.5,
    pulse: 0,
    spectrum: new Array(12).fill(0.5),
  });
  const alphas = [...css.matchAll(/rgba\([^)]*,([\d.]+)\)/g)].map((m) =>
    Number(m[1]),
  );
  assert.equal(alphas.length, 25);
  assert.equal(alphas[0], 0);
  assert.equal(alphas[24], 0);
  assert.equal(Math.max(...alphas), alphas[12]);
  assert.deepEqual(alphas, [...alphas].reverse());
}

console.log("voiceGlow: all assertions passed");
