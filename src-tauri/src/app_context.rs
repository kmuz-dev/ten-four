//! Which app a dictation is going into, and the writing style that fits it.
//!
//! The app is read once, when recording stops (the paste lands in whatever is
//! frontmost then), mapped to a category, and the category contributes two
//! things: a line of style guidance appended to the Smart Format prompt, and
//! deterministic rules applied to the final text (e.g. no trailing period in
//! chat). The user can re-categorise any app in settings.

use crate::settings::{get_settings, write_settings};
use serde::{Deserialize, Serialize};
use specta::Type;
use std::collections::HashMap;
use tauri::AppHandle;

#[derive(Serialize, Deserialize, Debug, Clone, Copy, PartialEq, Eq, Hash, Type)]
#[serde(rename_all = "snake_case")]
pub enum AppCategory {
    Code,
    Terminal,
    AiChat,
    Email,
    WorkChat,
    PersonalChat,
    Notes,
    Other,
}

/// The app that has focus: its bundle id (stable key) and display name.
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Eq, Type)]
pub struct AppContext {
    pub bundle_id: String,
    pub name: String,
}

/// Read the frontmost app. `None` when it can't be determined (or off macOS).
#[cfg(target_os = "macos")]
pub fn frontmost_app() -> Option<AppContext> {
    use objc2_app_kit::NSWorkspace;
    let app = NSWorkspace::sharedWorkspace().frontmostApplication()?;
    let bundle_id = app.bundleIdentifier()?.to_string();
    let name = app
        .localizedName()
        .map(|n| n.to_string())
        .unwrap_or_else(|| bundle_id.clone());
    Some(AppContext { bundle_id, name })
}

#[cfg(not(target_os = "macos"))]
pub fn frontmost_app() -> Option<AppContext> {
    None
}

/// Built-in bundle id → category table. Exact ids first, then prefixes for
/// vendors that ship many apps (JetBrains).
const KNOWN_APPS: &[(&str, AppCategory)] = &[
    // Code editors
    ("com.todesktop.230313mzl4w4u92", AppCategory::Code), // Cursor
    ("com.microsoft.VSCode", AppCategory::Code),
    ("com.microsoft.VSCodeInsiders", AppCategory::Code),
    ("com.exafunction.windsurf", AppCategory::Code),
    ("dev.zed.Zed", AppCategory::Code),
    ("com.apple.dt.Xcode", AppCategory::Code),
    ("com.sublimetext.4", AppCategory::Code),
    ("com.panic.Nova", AppCategory::Code),
    ("com.rstudio.desktop", AppCategory::Code),
    // Terminals (often prompts for a command-line agent such as Claude Code)
    ("com.apple.Terminal", AppCategory::Terminal),
    ("com.googlecode.iterm2", AppCategory::Terminal),
    ("dev.warp.Warp-Stable", AppCategory::Terminal),
    ("com.mitchellh.ghostty", AppCategory::Terminal),
    ("org.alacritty", AppCategory::Terminal),
    ("net.kovidgoyal.kitty", AppCategory::Terminal),
    ("com.github.wez.wezterm", AppCategory::Terminal),
    // AI assistants
    ("com.anthropic.claudefordesktop", AppCategory::AiChat),
    ("com.openai.chat", AppCategory::AiChat),
    ("ai.perplexity.mac", AppCategory::AiChat),
    // Email
    ("com.apple.mail", AppCategory::Email),
    ("com.microsoft.Outlook", AppCategory::Email),
    ("com.readdle.SparkDesktop", AppCategory::Email),
    ("com.readdle.smartemail-Mac", AppCategory::Email),
    ("com.superhuman.electron", AppCategory::Email),
    ("com.mimestream.Mimestream", AppCategory::Email),
    ("it.bloop.airmail2", AppCategory::Email),
    // Work chat
    ("com.tinyspeck.slackmacgap", AppCategory::WorkChat),
    ("com.microsoft.teams2", AppCategory::WorkChat),
    ("com.microsoft.teams", AppCategory::WorkChat),
    // Personal chat
    ("com.apple.MobileSMS", AppCategory::PersonalChat),
    ("net.whatsapp.WhatsApp", AppCategory::PersonalChat),
    ("desktop.WhatsApp", AppCategory::PersonalChat),
    ("ru.keepcoder.Telegram", AppCategory::PersonalChat),
    ("org.telegram.desktop", AppCategory::PersonalChat),
    (
        "org.whispersystems.signal-desktop",
        AppCategory::PersonalChat,
    ),
    ("com.hnc.Discord", AppCategory::PersonalChat),
    ("com.facebook.archon", AppCategory::PersonalChat), // Messenger
    // Notes and documents
    ("com.apple.Notes", AppCategory::Notes),
    ("notion.id", AppCategory::Notes),
    ("md.obsidian", AppCategory::Notes),
    ("net.shinyfrog.bear", AppCategory::Notes),
    ("com.lukilabs.lukiapp", AppCategory::Notes), // Craft
    ("com.apple.iWork.Pages", AppCategory::Notes),
    ("com.microsoft.Word", AppCategory::Notes),
    ("com.apple.TextEdit", AppCategory::Notes),
];

const KNOWN_PREFIXES: &[(&str, AppCategory)] = &[("com.jetbrains.", AppCategory::Code)];

/// The category Handy assigns to an app before any user override.
// ponytail: browsers stay Other because the site (Gmail vs Docs) decides the
// style; read the tab URL if per-site styles are ever wanted.
pub fn builtin_category(bundle_id: &str) -> AppCategory {
    KNOWN_APPS
        .iter()
        .find(|(id, _)| id.eq_ignore_ascii_case(bundle_id))
        .or_else(|| {
            KNOWN_PREFIXES
                .iter()
                .find(|(prefix, _)| bundle_id.starts_with(prefix))
        })
        .map(|(_, category)| *category)
        .unwrap_or(AppCategory::Other)
}

/// The category in effect: the user's override if any, else the built-in one.
pub fn category_for(bundle_id: &str, overrides: &HashMap<String, AppCategory>) -> AppCategory {
    overrides
        .get(bundle_id)
        .copied()
        .unwrap_or_else(|| builtin_category(bundle_id))
}

impl AppCategory {
    /// Style guidance added to the Smart Format prompt. `None` = no change.
    fn style(self) -> Option<&'static str> {
        match self {
            Self::Code => Some(
                "It is a prompt or note in a code editor, often for an AI coding assistant. \
                 Keep code identifiers, file paths and commands exactly as spoken, write plain \
                 direct sentences, and add no greeting or sign-off.",
            ),
            Self::Terminal => Some(
                "It is typed into a terminal, usually a prompt for a command-line AI agent. \
                 Keep commands, flags, file paths and identifiers exactly as spoken, write plain \
                 sentences, and add no greeting or sign-off.",
            ),
            Self::AiChat => Some(
                "It is a prompt for an AI assistant. Keep it clear and direct in the speaker's \
                 own wording, with no greeting or sign-off.",
            ),
            Self::Email => Some(
                "It is an email. Use complete sentences and a clear, professional tone. If the \
                 speaker says a greeting or sign-off, put each on its own line.",
            ),
            Self::WorkChat => Some(
                "It is a work chat message. Keep it concise and conversational, and add no \
                 greeting or sign-off.",
            ),
            Self::PersonalChat => Some(
                "It is a personal chat message. Keep it casual and keep the speaker's informal \
                 wording.",
            ),
            Self::Notes => Some(
                "It is a note or document. Use clear sentences, and use lists where the speaker \
                 enumerates.",
            ),
            Self::Other => None,
        }
    }

    /// Chat messages read as stiff with a full stop at the end.
    fn drops_trailing_period(self) -> bool {
        matches!(self, Self::WorkChat | Self::PersonalChat)
    }
}

/// The line appended to the Smart Format prompt for this app, if any.
pub fn style_note(app: &AppContext, category: AppCategory) -> Option<String> {
    category
        .style()
        .map(|style| format!("The text will be typed into {}. {}", app.name, style))
}

/// Deterministic per-category rules applied to the final text.
pub fn apply_category_rules(text: &str, category: AppCategory) -> String {
    if category.drops_trailing_period() && is_short_single_line(text) {
        if let Some(stripped) = text.strip_suffix('.') {
            if !stripped.ends_with('.') {
                return stripped.to_string();
            }
        }
    }
    text.to_string()
}

/// One line with at most two sentences: a quick chat message, not a paragraph.
fn is_short_single_line(text: &str) -> bool {
    !text.contains('\n') && text.matches(['.', '!', '?']).count() <= 2
}

/// How many recently used apps settings keeps for the App Styles list.
const SEEN_APPS_LIMIT: usize = 30;

/// Move `app` to the front of the recently-used list (persisted only when the
/// list actually changes, i.e. when you switch apps).
pub fn remember_seen_app(handle: &AppHandle, app: &AppContext) {
    let mut settings = get_settings(handle);
    if settings.seen_apps.first() == Some(app) {
        return;
    }
    settings
        .seen_apps
        .retain(|seen| seen.bundle_id != app.bundle_id);
    settings.seen_apps.insert(0, app.clone());
    settings.seen_apps.truncate(SEEN_APPS_LIMIT);
    write_settings(handle, settings);
}

/// A recently used app as the App Styles page shows it.
#[derive(Serialize, Debug, Clone, Type)]
pub struct SeenApp {
    pub bundle_id: String,
    pub name: String,
    pub category: AppCategory,
    /// Whether `category` is the user's choice rather than the built-in one.
    pub is_custom: bool,
}

#[tauri::command]
#[specta::specta]
pub fn list_seen_apps(app: AppHandle) -> Vec<SeenApp> {
    let settings = get_settings(&app);
    settings
        .seen_apps
        .iter()
        .map(|seen| SeenApp {
            bundle_id: seen.bundle_id.clone(),
            name: seen.name.clone(),
            category: category_for(&seen.bundle_id, &settings.app_category_overrides),
            is_custom: settings
                .app_category_overrides
                .contains_key(&seen.bundle_id),
        })
        .collect()
}

/// Set an app's category. Choosing its built-in category clears the override.
#[tauri::command]
#[specta::specta]
pub fn set_app_category(
    app: AppHandle,
    bundle_id: String,
    category: AppCategory,
) -> Result<(), String> {
    let mut settings = get_settings(&app);
    if category == builtin_category(&bundle_id) {
        settings.app_category_overrides.remove(&bundle_id);
    } else {
        settings.app_category_overrides.insert(bundle_id, category);
    }
    write_settings(&app, settings);
    Ok(())
}

#[tauri::command]
#[specta::specta]
pub fn change_app_styles_enabled_setting(app: AppHandle, enabled: bool) -> Result<(), String> {
    let mut settings = get_settings(&app);
    settings.app_styles_enabled = enabled;
    write_settings(&app, settings);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn app(bundle_id: &str, name: &str) -> AppContext {
        AppContext {
            bundle_id: bundle_id.to_string(),
            name: name.to_string(),
        }
    }

    #[test]
    fn known_apps_map_to_their_category() {
        assert_eq!(
            builtin_category("com.todesktop.230313mzl4w4u92"),
            AppCategory::Code
        );
        assert_eq!(builtin_category("com.apple.mail"), AppCategory::Email);
        assert_eq!(
            builtin_category("com.jetbrains.intellij"),
            AppCategory::Code
        );
        assert_eq!(builtin_category("com.apple.Safari"), AppCategory::Other);
    }

    #[test]
    fn user_override_wins() {
        let overrides = HashMap::from([("com.apple.Safari".to_string(), AppCategory::Email)]);
        assert_eq!(
            category_for("com.apple.Safari", &overrides),
            AppCategory::Email
        );
        assert_eq!(
            category_for("com.apple.mail", &overrides),
            AppCategory::Email
        );
    }

    #[test]
    fn style_note_names_the_app() {
        let note = style_note(&app("com.apple.mail", "Mail"), AppCategory::Email).unwrap();
        assert!(note.starts_with("The text will be typed into Mail."));
        assert!(style_note(&app("x", "X"), AppCategory::Other).is_none());
    }

    #[test]
    fn chat_drops_the_final_period_of_a_short_message() {
        assert_eq!(
            apply_category_rules("Sounds good, see you at 3.", AppCategory::WorkChat),
            "Sounds good, see you at 3"
        );
        assert_eq!(
            apply_category_rules("Wait for it...", AppCategory::PersonalChat),
            "Wait for it..."
        );
    }

    #[test]
    fn long_or_multiline_chat_and_other_categories_keep_periods() {
        let long = "One. Two. Three.";
        assert_eq!(apply_category_rules(long, AppCategory::WorkChat), long);
        let multi = "Hi.\nThanks.";
        assert_eq!(apply_category_rules(multi, AppCategory::WorkChat), multi);
        assert_eq!(apply_category_rules("Done.", AppCategory::Email), "Done.");
    }
}
