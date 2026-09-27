import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import type { Snippet } from "@/bindings";
import { useSettings } from "../../../hooks/useSettings";
import { SettingsGroup } from "../../ui/SettingsGroup";
import { Input } from "../../ui/Input";
import { Textarea } from "../../ui/Textarea";
import { Button } from "../../ui/Button";
import { SpokenCommands } from "../SpokenCommands";

// Mirror text_rules.rs: words are runs of letters, digits and apostrophes;
// apostrophes are dropped and case is ignored.
const triggerKey = (trigger: string) =>
  (trigger.toLowerCase().match(/[\p{L}\p{N}'’]+/gu) ?? [])
    .map((word) => word.replace(/['’]/g, ""))
    .filter(Boolean)
    .join(" ");

export const SnippetsSettings: React.FC = () => {
  const { t } = useTranslation();
  const { getSetting, updateSetting, isUpdating } = useSettings();
  const snippets: Snippet[] = getSetting("snippets") ?? [];
  const [trigger, setTrigger] = useState("");
  const [expansion, setExpansion] = useState("");
  const updating = isUpdating("snippets");
  const canAdd = triggerKey(trigger) !== "" && expansion.trim() !== "";

  const handleAdd = () => {
    if (!canAdd) return;
    if (snippets.some((s) => triggerKey(s.trigger) === triggerKey(trigger))) {
      toast.error(
        t("settings.snippets.duplicate", { trigger: trigger.trim() }),
      );
      return;
    }
    updateSetting("snippets", [
      ...snippets,
      { trigger: trigger.trim(), expansion },
    ]);
    setTrigger("");
    setExpansion("");
  };

  const handleRemove = (index: number) => {
    updateSetting(
      "snippets",
      snippets.filter((_, i) => i !== index),
    );
  };

  return (
    <div className="max-w-3xl w-full mx-auto space-y-6">
      <SettingsGroup
        title={t("settings.snippets.title")}
        description={t("settings.snippets.description")}
      >
        <div className="p-4 space-y-3">
          <div className="space-y-1">
            <label
              htmlFor="snippet-trigger"
              className="text-sm font-semibold block"
            >
              {t("settings.snippets.triggerLabel")}
            </label>
            <Input
              id="snippet-trigger"
              type="text"
              className="w-full"
              value={trigger}
              onChange={(e) => setTrigger(e.target.value)}
              placeholder={t("settings.snippets.triggerPlaceholder")}
              disabled={updating}
            />
          </div>
          <div className="space-y-1">
            <label
              htmlFor="snippet-expansion"
              className="text-sm font-semibold block"
            >
              {t("settings.snippets.expansionLabel")}
            </label>
            <Textarea
              id="snippet-expansion"
              className="w-full"
              value={expansion}
              onChange={(e) => setExpansion(e.target.value)}
              placeholder={t("settings.snippets.expansionPlaceholder")}
              disabled={updating}
            />
          </div>
          <Button
            onClick={handleAdd}
            disabled={!canAdd || updating}
            variant="primary"
            size="md"
          >
            {t("settings.snippets.add")}
          </Button>
        </div>

        {snippets.length === 0 ? (
          <p className="px-4 py-3 text-sm text-mid-gray">
            {t("settings.snippets.empty")}
          </p>
        ) : (
          snippets.map((snippet, index) => (
            <div
              key={`${snippet.trigger}-${index}`}
              className="px-4 py-3 flex items-start justify-between gap-4"
            >
              <div className="min-w-0 space-y-1">
                <p className="text-sm font-semibold">“{snippet.trigger}”</p>
                <p className="text-sm text-mid-gray whitespace-pre-wrap break-words">
                  {snippet.expansion}
                </p>
              </div>
              <Button
                onClick={() => handleRemove(index)}
                disabled={updating}
                variant="secondary"
                size="sm"
                aria-label={t("settings.snippets.remove", {
                  trigger: snippet.trigger,
                })}
              >
                {t("settings.snippets.removeShort")}
              </Button>
            </div>
          ))
        )}
      </SettingsGroup>

      <SettingsGroup title={t("settings.snippets.commandsTitle")}>
        <SpokenCommands descriptionMode="inline" grouped={true} />
      </SettingsGroup>
    </div>
  );
};
