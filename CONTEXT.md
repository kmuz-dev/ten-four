# Ten-Four Brand Identity

This context defines the approved language and decision boundaries for Ten-Four's visual identity.

## Language

**Ten-Four**:
The product display name, from the radio reply "10-4", meaning "message received."
The repo, bundle identifier (`com.kuda.handy`), binary, and code identifiers keep the old "handy" name on purpose.
_Avoid_: Handy, TenFour

**Pocket recorder mark**:
The approved standalone symbol.
It combines a handheld cassette recorder with a compact walkie-talkie: a channel display, short antenna, and record, stop, and play controls.
_Avoid_: Keycap, battery glyph, generic letter O, microphone

**App icon**:
The platform-specific warm equipment squircle containing the full-color **Pocket recorder mark**.
_Avoid_: Replacing the recorder with an abstract symbol

**Name wordmark**:
The custom uppercase `TEN-FOUR` lettering selected from the secondary lockup.
It is the default wordmark beside the icon in compact application chrome.
_Avoid_: A system-font rendering of "Ten-Four"

**Numeric wordmark**:
The custom `10.4` lettering selected from the monochrome mark.
Its period is always Tally orange, including idle brand applications.
It is the preferred display wordmark for onboarding and larger identity moments.
_Avoid_: `10-4`, `104`, or a monochrome period

**Tally punctuation**:
Tally orange is permanently allowed for the period in the **Numeric wordmark** and for the record control in the full-color **App icon**.
Outside locked identity artwork, Tally remains reserved for active recording state.

## Relationships

- The **Pocket recorder mark** identifies the product without either wordmark.
- The **App icon** contains the full-color **Pocket recorder mark** and the `10.4` channel display.
- The **Name wordmark** pairs with the icon in the settings sidebar and other compact horizontal lockups.
- The **Numeric wordmark** pairs with the icon in onboarding and larger brand moments.
- The one-color tray mark reduces the recorder to its enclosure, display, antenna, and three controls.
- The tray record control uses Tally only while recording so activity remains legible.
- The orange period remains part of the **Numeric wordmark** in light, dark, and idle contexts.

## Approved source

- Direction: `design/ten-four-logo-exploration/aesthetic-variations/cassette-futurism/concept-board-v2.png`
- Decision record: `design/ten-four-logo-exploration/direction-approved.md`
- Frontend vectors: `src/components/icons/HandyMark.tsx`
- Platform generator: `scripts/gen_brand_assets.py`

## Example dialogue

> **Designer:** "Which wordmark belongs in the sidebar?"
> **Domain expert:** "Use the `TEN-FOUR` name wordmark there. Reserve the wider `10.4` wordmark for onboarding and larger identity moments."

## Flagged ambiguity

"Logo" previously referred to the mark, app icon, and both wordmarks.
These are four related assets with distinct jobs and should be named precisely.
