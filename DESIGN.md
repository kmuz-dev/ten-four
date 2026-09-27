# Design System - Handy (Tally Light)

This is the North Star for every visual, motion and sound decision in this fork.
Read it before changing any UI.
The interactive prototype that these decisions came from lives at https://claude.ai/artifact/JPwP2HpZ5e7F5xc8CWofoY.

## Product Context

- **What this is:** a local, private push-to-talk dictation app for macOS. Hold a key, speak, and the text is pasted where you are typing.
- **Who it's for:** one person, used a hundred times a day, so it has to disappear into their work.
- **Space:** dictation tools such as Wispr Flow, Superwhisper, MacWhisper, VoiceInk, Aqua Voice and Willow.
- **Project type:** a native-feeling desktop utility: a settings window, a recording overlay, a menu bar icon and sound cues.

## The One Thing

Handy is a quiet instrument that looks like Apple shipped it.
Someone seeing it for the first time should feel "this is serious, and it's quiet," and trust it before it has done anything.
Every decision below serves that sentence.

## Aesthetic Direction

- **Direction:** "Tally Light." Graphite everywhere, controls in the system accent, and one color Handy owns: the red record light that means you are live.
- **Decoration level:** minimal. Type, spacing and material do the work.
- **Mood:** calm, exact, native. Never cute, never "AI magic" (no orbs, gradient blobs or sparkles).
- **What we left behind:** the pink palette and the cartoon hand, which read as toy-ish.

## Typography

- **UI:** SF Pro, the system font (`-apple-system`). Any custom font inside a Mac settings window reads as a web app in a wrapper.
- **Data:** SF Mono (`ui-monospace`) with `tabular-nums` for timers, shortcuts, model sizes and timestamps.
- **Prose:** New York (`ui-serif`) for transcription history only, set like a notebook. Not yet built.
- **Scale:** title 15/700, label 13/400, caption 11/400, data 11 mono, prose 15 with 1.45 line height.

## Color

- **Approach:** restrained. Monochrome graphite plus a single owned color.
- **Tally (record light):** `#FF4A26` on light surfaces, `#FF6242` on dark surfaces and the overlay (`--color-tally-hud`). Used only for "you are live": the recording dot, the glow line and the menu bar LED. Never for buttons, links or decoration.
- **Accent:** the user's macOS system accent color for controls, selection and focus.
- **Neutrals:**

| Token          | Light     | Dark      |
| -------------- | --------- | --------- |
| Background     | `#F6F5F2` | `#1B1B1D` |
| Surface        | `#FFFFFF` | `#262628` |
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
  - Your voice is a 2pt red line glowing along the bottom edge. Its width follows the input level.
- **Transcribing:**
  - The dot dims.
  - The line becomes a faint full-width rail with light sweeping across it.
- **Done (text pasted):**
  - A check draws in the right wing.
  - The line flashes white and fades.
  - After about 650ms the island retracts into the notch.
- **Cancelled or failed:** it retracts at once, with no check.
- **No notch** (external display, older Mac): the same island hangs as a tab from the top center of the screen.
- **Other platforms:** the Island setting falls back to the Minimal pill.

Implementation: `src-tauri/src/overlay.rs` (notch detection from `NSScreen`, top-edge placement, exit timing) and `src/overlay/RecordingOverlay.tsx` + `.css`.

## Motion

- **Approach:** intentional and quiet. One grow, one settle, nothing ambient.
- **Grow:** 420ms spring with a 4% overshoot (`linear()` spring, `cubic-bezier(.2,.9,.25,1.04)` fallback).
- **Retract:** 340ms `cubic-bezier(.3,0,.2,1)`, no overshoot.
- **Level smoothing:** fast attack and slow release (about 60ms up, 220ms down), so the line never flickers.
- **Check:** draws in 180ms after a 120ms delay.
- **Reduce Motion:** size changes snap and sweeps stop; state is still readable from color and the check.

## Sound

- **Cue family:** Microcassette. A dictaphone thumb slide: a short friction sweep, then a detent click.
- **Start:** slide sweeping 1.5 to 3.6 kHz over 40ms, detent tick at 4.3 kHz, 230 Hz body. About 60ms total.
- **Stop:** slide sweeping 3.6 to 1.4 kHz over 45ms, detent tick at 3 kHz, 190 Hz body. About 65ms total.
- **Level:** about 6 dB under macOS system alerts.
- **No success sound.** The pasted text is the confirmation.
- The exact synthesis lives in the prototype (`CUES['micro-start']` and `CUES['micro-stop']`). Not yet rendered to WAV or wired into the app.

## Mark

- **Keycap + LED:** a single key seen from above with a small caps-lock style LED in the corner. Push and talk in one object.
- **App icon:** a graphite squircle, a graphite keycap, and the LED as the only color, in Tally with a soft glow.
- **Menu bar:** a template-image keycap outline. The LED fills with Tally only while recording.
- Not yet built. The SVG source is in the prototype.

## Not Yet Designed

These parts of the app still carry the old look.
They should be brought into line with this document in later passes:

- The settings window and onboarding.
- History (New York prose layout).
- The app icon, tray icons and sound files.

## Decisions Log

| Date       | Decision                                                | Rationale                                                                                          |
| ---------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 2026-09-27 | Tally Light direction                                   | User wants a quiet instrument that looks like Apple shipped it; the pink and hand read as toy-ish. |
| 2026-09-27 | SF Pro + SF Mono, New York for history                  | First-party feel; custom fonts in a Mac settings window read as web.                               |
| 2026-09-27 | One owned color (Tally red), system accent for controls | Handy disappears until it is live; no competitor follows the system accent.                        |
| 2026-09-27 | Island overlay, Glow line variant                       | Picked from five variants (Split, Shelf, Glow line, Live text, Reels) as the most ambient.         |
| 2026-09-27 | Keycap + LED mark                                       | Picked over Level H and Tally ring.                                                                |
| 2026-09-27 | Microcassette cues                                      | Picked over Felt, Click, Tape deck and Walkman.                                                    |
