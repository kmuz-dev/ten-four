# Design System - Ten-Four (Tally Light)

This is the North Star for every visual, motion and sound decision in this fork.
Read it before changing any UI.
The interactive prototype that these decisions came from lives at https://claude.ai/artifact/JPwP2HpZ5e7F5xc8CWofoY.

## Product Context

- **What this is:** a local, private push-to-talk dictation app for macOS. Hold a key, speak, and the text is pasted where you are typing.
- **Who it's for:** one person, used a hundred times a day, so it has to disappear into their work.
- **Space:** dictation tools such as Wispr Flow, Superwhisper, MacWhisper, VoiceInk, Aqua Voice and Willow.
- **Project type:** a native-feeling desktop utility: a settings window, a recording overlay, a menu bar icon and sound cues.

## The One Thing

Ten-Four is a quiet instrument that looks like Apple shipped it.
Someone seeing it for the first time should feel "this is serious, and it's quiet," and trust it before it has done anything.
Every decision below serves that sentence.

## Aesthetic Direction

- **Direction:** "Tally Light." Graphite everywhere, controls in the system accent, and one color Ten-Four owns: the red record light that means you are live.
- **Decoration level:** minimal. Type, spacing and material do the work.
- **Mood:** calm, exact, native. Never cute, never "AI magic" (no orbs, gradient blobs or sparkles).
- **What we left behind:** the pink palette and the cartoon hand, which read as toy-ish.

## Typography

- **UI:** SF Pro, the system font (`-apple-system`). Any custom font inside a Mac settings window reads as a web app in a wrapper.
- **Data:** SF Mono (`ui-monospace`) with `tabular-nums` for timers, shortcuts, model sizes and timestamps.
- **Prose:** New York (`ui-serif`) for transcription history only, set like a notebook (`font-serif`).
- **Scale:** title 15/700, label 13/400, caption 11/400, data 11 mono, prose 15 with 1.45 line height.

## Color

- **Approach:** restrained. Monochrome graphite plus a single owned color.
- **Tally (record light and brand punctuation):** `#FF4A26` on light surfaces, `#FF6242` on dark surfaces and the overlay (`--color-tally-hud`). Outside locked identity artwork, it is used only for "you are live": the recording dot, the glow line and the menu bar control. The `10.4` wordmark period and full-color recorder mark retain Tally while idle.
- **Accent:** the user's macOS system accent color for controls, selection and focus.
- **Neutrals:**

| Token          | Light     | Dark      |
| -------------- | --------- | --------- |
| Background     | `#F2F1EE` | `#1C1C1E` |
| Sidebar        | `#E9E8E4` | `#232325` |
| Surface        | `#FFFFFF` | `#2A2A2D` |
| Control face   | `#FFFFFF` | `#3A3A3D` |
| Hairline       | `#E2E1DC` | `#38383B` |
| Text           | `#1D1D1F` | `#F2F2EF` |
| Secondary text | `#6E6E73` | `#9A9A9F` |

- **Semantic:** warning and error keep the existing tokens in `src/styles/theme.css`, which are separate from Tally.

## Layout

- **Settings window:** laid out like macOS System Settings. Grouped rows in rounded boxes, 13pt labels, controls on the trailing edge, a translucent sidebar with graphite icon tiles instead of colored ones.
- **Spacing:** 4pt base unit. Rows are at least 40pt tall with 12pt side padding.
- **Radius:** 6 for controls, 10 for grouped boxes, 12 for windows. Full rounding only for dots, toggles and the island.

## Recording Overlay: the Island (Glow line)

The overlay is a notch island.
It is the only overlay style that follows this document; Minimal and Live remain as the upstream styles.

- **Rest:** exactly the size and color of the MacBook notch, so it is invisible.
- **Recording:**
  - It grows out of the notch, 30pt wider on each side and 5pt taller, with concave shoulders where it meets the top edge of the screen.
  - A red dot sits in the left wing, dim while the microphone is still arming.
  - Your voice is a 2pt red line glowing along the bottom edge. It is widest and hottest in the middle and tapers to nothing at the tips; its width follows your voice, and each syllable flashes it slightly brighter.
  - Your words stream in under the notch as you speak. The island widens into a 420pt sheet and drops one line at a time, up to two, with older lines gliding up out of view.
  - Each word fades up out of a slight blur as it lands. Words the model may still revise sit at 50% white and brighten when it commits to them.
- **Transcribing:**
  - The dot dims.
  - The line becomes a faint full-width rail with light sweeping across it.
  - The words stay, all at full white.
- **Done (text pasted):**
  - A check draws in the right wing.
  - The line flashes white and fades.
  - After about 650ms the island retracts into the notch.
- **Cancelled or failed:** it retracts at once, with no check.
- **No notch** (external display, older Mac): the same island hangs as a tab from the top center of the screen.
- **Other platforms:** the Island setting falls back to the Minimal pill.
- **Clicks:** the island window ignores the mouse, so the sheet never blocks the app underneath.
- **Models that don't stream** produce no live words; the island stays a single row.

Implementation: `src-tauri/src/overlay.rs` (notch detection from `NSScreen`, top-edge placement, exit timing), `src/overlay/RecordingOverlay.tsx` + `.css`, and `src/overlay/voiceGlow.ts` (the voice line).

## Motion

- **Approach:** intentional and quiet. One grow, one settle, nothing ambient.
- **Grow:** 420ms spring with a 4% overshoot (`linear()` spring, `cubic-bezier(.2,.9,.25,1.04)` fallback).
- **Retract:** 340ms `cubic-bezier(.3,0,.2,1)`, no overshoot.
- **Voice line:** runs on its own frame loop, not on mic events, which arrive only about 23 times a second.
  - Automatic gain measures loudness against a tracked noise floor and recent peak, so a quiet voice still fills the line.
  - A spring chases that loudness: about 100ms up, 220ms down, a touch of overshoot. The target is eased before the spring, so speed never changes abruptly and the line has no corners.
  - A sudden rise in loudness (a syllable onset) flashes the line brighter for about 140ms, so the light follows the cadence of speech.
  - `bun run test:voice-glow` pins these properties.
- **Words:** fade and unblur in 280ms `cubic-bezier(.16,1,.3,1)`; a wrapped line glides up in 300ms on the same curve.
- **Check:** draws in 180ms after a 120ms delay.
- **Reduce Motion:** size changes snap and sweeps stop; state is still readable from color and the check. The voice line keeps its width but drops the texture and syllable flash, and words fade in without moving.

## Sound

- **Cue family:** Microcassette. A dictaphone thumb slide: a short friction sweep, then a detent click.
- **Start:** slide sweeping 1.5 to 3.6 kHz over 40ms, detent tick at 4.3 kHz, 230 Hz body. About 60ms total.
- **Stop:** slide sweeping 3.6 to 1.4 kHz over 45ms, detent tick at 3 kHz, 190 Hz body. About 65ms total.
- **Level:** about 6 dB under macOS system alerts.
- **No success sound.** The pasted text is the confirmation.
- Rendered deterministically by `scripts/gen_microcassette_sounds.py` (edit a number and re-run) to `src-tauri/resources/microcassette_{start,stop}.wav`. It is the default sound theme.

## Mark

- **Pocket recorder:** a compact cassette recorder and walkie-talkie hybrid with a channel display, short antenna, and record, stop, and play controls.
- **Numeric wordmark:** custom `10.4` vector lettering with a permanently orange period. It is used for onboarding and larger identity moments.
- **Name wordmark:** custom uppercase `TEN-FOUR` vector lettering from the approved secondary lockup. It is used in compact horizontal application chrome.
- **App icon:** the warm squircle is the pocket recorder face itself, edge to edge: a full-width `10.4` display over three transport keys. No recorder drawn inside the tile.
- **Menu bar:** a one-color recorder outline. Its record control fills with Tally only while recording.
- Drawn by `scripts/gen_brand_assets.py`, which writes every tray icon and the 1024px master `src-tauri/icons/app-icon.png`.
  `bun run tauri icon src-tauri/icons/app-icon.png` regenerates the platform icon sets.
  In the UI: `HandyAppIcon`, `HandyMark` and `HandyLogo` in `src/components/icons/HandyMark.tsx`.

## Implementation Notes

- Tokens live in `src/styles/theme.css` as light/dark pairs and are registered with Tailwind in `src/App.css`: `bg-background`, `bg-sidebar`, `bg-surface`, `border-hairline`, `text-text`, `text-text-secondary`, `bg-accent`, `bg-tally`.
- `--color-accent` is `-apple-system-control-accent` in WebKit on macOS, so controls follow the System Settings accent. Elsewhere it falls back to Apple blue.
- Tailwind's text scale is pinned to macOS points (`text-xs` 11, `text-sm` and `text-base` 13, `text-lg` 15) on a 13px root.
- Shared control styles in `App.css`: `.grouped-rows` (inset hairlines), `.mac-control` (raised pop-up and secondary button face), `.mac-range` (slider).
- The macOS window has a transparent title bar with the traffic lights inside the sidebar (`lib.rs`), padded by `.titlebar-pad` and `.titlebar-strip`.

## Still in the Old Look

- Onboarding screens beyond the new logo (model cards, permission steps).
- The Minimal and Live overlay styles, which stay upstream's; the Island is the designed one.

## Decisions Log

| Date       | Decision                                                | Rationale                                                                                                                                                 |
| ---------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-09-27 | Tally Light direction                                   | User wants a quiet instrument that looks like Apple shipped it; the pink and hand read as toy-ish.                                                        |
| 2026-09-27 | SF Pro + SF Mono, New York for history                  | First-party feel; custom fonts in a Mac settings window read as web.                                                                                      |
| 2026-09-27 | One owned color (Tally red), system accent for controls | Handy disappears until it is live; no competitor follows the system accent.                                                                               |
| 2026-09-27 | Island overlay, Glow line variant                       | Picked from five variants (Split, Shelf, Glow line, Live text, Reels) as the most ambient.                                                                |
| 2026-09-27 | Keycap + LED mark                                       | Picked over Level H and Tally ring.                                                                                                                       |
| 2026-09-27 | Microcassette cues                                      | Picked over Felt, Click, Tape deck and Walkman.                                                                                                           |
| 2026-09-28 | Settings window, icons and sounds moved to Tally Light  | Pink and the hand removed; System Settings layout, system accent, keycap mark, Microcassette cues.                                                        |
| 2026-09-28 | Live words under the island; voice line on a spring     | User wanted to see words as they speak, and a line that follows their voice smoothly.                                                                     |
| 2026-09-28 | Renamed the app from Handy to Ten-Four                  | "Handy" never read as dictation. Radio slang for "message received" fits speaking orders to agents. Code identifiers stay "handy".                        |
| 2026-09-28 | Pocket recorder identity selected                       | Cassette Futurism connects the radio name to a clear handheld object. The recorder icon, `TEN-FOUR` lockup, and `10.4` wordmark were explicitly approved. |
