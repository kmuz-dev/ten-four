import React from "react";
import { useTranslation } from "react-i18next";
import { ToggleSwitch } from "../ui/ToggleSwitch";
import { useSettings } from "../../hooks/useSettings";

interface SmartFormatEveryDictationProps {
  descriptionMode?: "inline" | "tooltip";
  grouped?: boolean;
}

export const SmartFormatEveryDictation: React.FC<SmartFormatEveryDictationProps> =
  React.memo(({ descriptionMode = "tooltip", grouped = false }) => {
    const { t } = useTranslation();
    const { getSetting, updateSetting, isUpdating } = useSettings();
    const enabled = getSetting("post_process_on_main_hotkey") ?? false;

    return (
      <ToggleSwitch
        checked={enabled}
        onChange={(next) => updateSetting("post_process_on_main_hotkey", next)}
        isUpdating={isUpdating("post_process_on_main_hotkey")}
        label={t("settings.postProcessing.everyDictation.title")}
        description={t("settings.postProcessing.everyDictation.description")}
        descriptionMode={descriptionMode}
        grouped={grouped}
      />
    );
  });
