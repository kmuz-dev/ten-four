//! Deterministic rewrites of dictated text, applied after transcription and
//! before (or instead of) LLM post-processing.
//!
//! Anything with exactly one right answer lives here rather than in the LLM
//! prompt: spoken layout commands ("new paragraph") and snippet expansion.
//! Snippets are swapped for `{{S1}}`-style placeholders before the LLM runs so
//! the model can't reword the saved text, then restored afterwards.

use crate::settings::Snippet;
use once_cell::sync::Lazy;
use regex::Regex;

/// "new line" / "new paragraph", swallowing punctuation the speech model
/// attached to the command itself ("Hello. New paragraph. Next" → the "." after
/// "paragraph" belongs to the command, the one before it to the sentence).
static SPOKEN_BREAK: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"(?i)[ \t]*\bnew[ \t]+(paragraph|line)\b[.,;:!?]*[ \t]*").expect("valid regex")
});

/// Replace spoken layout commands with real line breaks, capitalising the
/// first letter after each inserted break.
// ponytail: a literal phrase like "a new line of products" also triggers;
// add a "literal" escape word if that bites in practice.
pub fn apply_spoken_commands(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut last = 0;
    let mut capitalize_at = Vec::new();
    for caps in SPOKEN_BREAK.captures_iter(text) {
        let whole = caps.get(0).expect("group 0 always matches");
        out.push_str(&text[last..whole.start()]);
        let is_paragraph = caps[1].eq_ignore_ascii_case("paragraph");
        // Don't stack breaks when the text already ends with one.
        let trimmed_len = out.trim_end_matches(['\n', ' ']).len();
        out.truncate(trimmed_len);
        capitalize_at.retain(|&pos| pos <= trimmed_len);
        if !out.is_empty() {
            out.push_str(if is_paragraph { "\n\n" } else { "\n" });
        }
        capitalize_at.push(out.len());
        last = whole.end();
    }
    out.push_str(&text[last..]);

    // Capitalise in reverse so earlier byte offsets stay valid.
    for pos in capitalize_at.into_iter().rev() {
        if let Some(c) = out[pos..].chars().next() {
            if c.is_lowercase() {
                let upper: String = c.to_uppercase().collect();
                out.replace_range(pos..pos + c.len_utf8(), &upper);
            }
        }
    }
    out
}

/// Text with snippet triggers swapped for placeholders, plus what each
/// placeholder expands to.
pub struct ProtectedText {
    pub text: String,
    expansions: Vec<String>,
    expanded: String,
}

static PLACEHOLDER: Lazy<Regex> = Lazy::new(|| Regex::new(r"\{\{S(\d+)\}\}").expect("valid regex"));

fn placeholder(index: usize) -> String {
    format!("{{{{S{}}}}}", index + 1)
}

impl ProtectedText {
    /// Put the snippet text back into `text` (usually LLM output), in one pass
    /// so expansions are never re-scanned. Returns `None` unless every
    /// placeholder appears exactly once — the caller then falls back to
    /// [`Self::expanded`] rather than paste a mangled result.
    pub fn restore(&self, text: &str) -> Option<String> {
        let mut seen = vec![0usize; self.expansions.len()];
        let mut valid = true;
        let out = PLACEHOLDER.replace_all(text, |caps: &regex::Captures| {
            let slot = caps[1]
                .parse::<usize>()
                .ok()
                .and_then(|n| n.checked_sub(1))
                .filter(|&i| i < self.expansions.len());
            match slot {
                Some(i) => {
                    seen[i] += 1;
                    self.expansions[i].clone()
                }
                // Not ours (e.g. the speaker literally said "{{S9}}"): a
                // placeholder we can't account for means we can't trust it.
                None => {
                    valid = false;
                    caps[0].to_string()
                }
            }
        });
        (valid && seen.iter().all(|&n| n == 1)).then(|| out.into_owned())
    }

    /// The text with every snippet expanded (no LLM involved).
    pub fn expanded(&self) -> &str {
        &self.expanded
    }
}

/// A word in the text: its byte span and a lowercase, punctuation-free form
/// used for matching.
struct Word {
    start: usize,
    end: usize,
    key: String,
}

fn words(text: &str) -> Vec<Word> {
    let mut out = Vec::new();
    let mut start = None;
    for (i, c) in text
        .char_indices()
        .chain(std::iter::once((text.len(), ' ')))
    {
        let is_word_char = c.is_alphanumeric() || c == '\'' || c == '’';
        match (start, is_word_char) {
            (None, true) => start = Some(i),
            (Some(s), false) => {
                let key = text[s..i]
                    .chars()
                    .filter(|c| c.is_alphanumeric())
                    .flat_map(char::to_lowercase)
                    .collect();
                out.push(Word {
                    start: s,
                    end: i,
                    key,
                });
                start = None;
            }
            _ => {}
        }
    }
    out
}

/// Swap every snippet trigger in `text` for a placeholder. Triggers match
/// whole words, ignoring case and punctuation ("My email." matches "my
/// email"); longer triggers win when two overlap.
// ponytail: exact word match only; reuse apply_custom_words' fuzzy matcher if
// the speech model keeps mishearing a trigger.
pub fn protect_snippets(text: &str, snippets: &[Snippet]) -> ProtectedText {
    let mut triggers: Vec<(Vec<String>, &str)> = snippets
        .iter()
        .map(|s| {
            let keys: Vec<String> = words(&s.trigger).into_iter().map(|w| w.key).collect();
            (keys, s.expansion.as_str())
        })
        .filter(|(keys, _)| !keys.is_empty())
        .collect();
    triggers.sort_by_key(|(keys, _)| std::cmp::Reverse(keys.len()));

    let text_words = words(text);
    let mut out = String::with_capacity(text.len());
    let mut expansions = Vec::new();
    let mut expanded = String::with_capacity(text.len());
    let mut last = 0;
    let mut i = 0;
    while i < text_words.len() {
        let hit = triggers.iter().find(|(keys, _)| {
            text_words.len() - i >= keys.len()
                && keys.iter().zip(&text_words[i..]).all(|(k, w)| *k == w.key)
        });
        match hit {
            Some((keys, expansion)) => {
                out.push_str(&text[last..text_words[i].start]);
                out.push_str(&placeholder(expansions.len()));
                expanded.push_str(&text[last..text_words[i].start]);
                expanded.push_str(expansion);
                expansions.push(expansion.to_string());
                last = text_words[i + keys.len() - 1].end;
                i += keys.len();
            }
            None => i += 1,
        }
    }
    out.push_str(&text[last..]);
    expanded.push_str(&text[last..]);
    ProtectedText {
        text: out,
        expansions,
        expanded,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn snippet(trigger: &str, expansion: &str) -> Snippet {
        Snippet {
            trigger: trigger.to_string(),
            expansion: expansion.to_string(),
        }
    }

    #[test]
    fn new_paragraph_becomes_blank_line() {
        assert_eq!(
            apply_spoken_commands("Hello there. New paragraph. next topic."),
            "Hello there.\n\nNext topic."
        );
    }

    #[test]
    fn new_line_becomes_line_break() {
        assert_eq!(
            apply_spoken_commands("Dear Sam, new line thanks for this"),
            "Dear Sam,\nThanks for this"
        );
    }

    #[test]
    fn line_after_paragraph_keeps_one_break() {
        assert_eq!(
            apply_spoken_commands("Hi. New paragraph. New line. über alles"),
            "Hi.\nÜber alles"
        );
    }

    #[test]
    fn leading_command_adds_no_break() {
        assert_eq!(apply_spoken_commands("New line. Hello"), "Hello");
    }

    #[test]
    fn repeated_commands_do_not_stack() {
        assert_eq!(
            apply_spoken_commands("One. New paragraph. New paragraph. Two."),
            "One.\n\nTwo."
        );
    }

    #[test]
    fn text_without_commands_is_unchanged() {
        let text = "Nothing to see here, lineage and newline stay.";
        assert_eq!(apply_spoken_commands(text), text);
    }

    #[test]
    fn snippet_trigger_is_replaced_ignoring_case_and_punctuation() {
        let p = protect_snippets(
            "Send it to My Email.",
            &[snippet("my email", "kuda@example.com")],
        );
        assert_eq!(p.text, "Send it to {{S1}}.");
        assert_eq!(p.expanded(), "Send it to kuda@example.com.");
    }

    #[test]
    fn longer_trigger_wins() {
        let p = protect_snippets(
            "my work email please",
            &[snippet("my email", "a"), snippet("my work email", "b")],
        );
        assert_eq!(p.expanded(), "b please");
    }

    #[test]
    fn partial_word_does_not_match() {
        let p = protect_snippets("my emails", &[snippet("my email", "x")]);
        assert_eq!(p.text, "my emails");
    }

    #[test]
    fn restore_round_trips_through_reworded_text() {
        let p = protect_snippets("so um sign off", &[snippet("sign off", "Best,\nKuda")]);
        assert_eq!(p.restore("{{S1}}").as_deref(), Some("Best,\nKuda"));
    }

    #[test]
    fn restore_rejects_lost_or_duplicated_placeholders() {
        let p = protect_snippets("sign off", &[snippet("sign off", "Best")]);
        assert_eq!(p.restore("Goodbye"), None);
        assert_eq!(p.restore("{{S1}} {{S1}}"), None);
    }

    #[test]
    fn expansion_containing_a_placeholder_does_not_break_anything() {
        let p = protect_snippets(
            "alpha and beta",
            &[snippet("alpha", "x {{S2}} y"), snippet("beta", "B")],
        );
        assert_eq!(p.expanded(), "x {{S2}} y and B");
        assert_eq!(p.restore(&p.text).as_deref(), Some("x {{S2}} y and B"));
    }

    #[test]
    fn literal_placeholder_in_speech_falls_back_safely() {
        let p = protect_snippets("say {{S1}} then sign off", &[snippet("sign off", "Bye")]);
        assert_eq!(p.expanded(), "say {{S1}} then Bye");
        assert_eq!(p.restore(&p.text), None);
    }

    #[test]
    fn unknown_placeholder_is_rejected() {
        let p = protect_snippets("sign off", &[snippet("sign off", "Bye")]);
        assert_eq!(p.restore("{{S1}} {{S7}}"), None);
    }

    #[test]
    fn empty_trigger_is_ignored() {
        let p = protect_snippets("hello", &[snippet("  ", "x")]);
        assert_eq!(p.expanded(), "hello");
    }
}
