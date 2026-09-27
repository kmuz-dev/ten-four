import React from "react";
import { useTranslation } from "react-i18next";
import { ToggleSwitch } from "../ui/ToggleSwitch";
import { useSettings } from "../../hooks/useSettings";

interface SpokenCommandsProps {
  descriptionMode?: "inline" | "tooltip";
  grouped?: boolean;
}

export const SpokenCommands: React.FC<SpokenCommandsProps> = React.memo(
  ({ descriptionMode = "tooltip", grouped = false }) => {
    const { t } = useTranslation();
    const { getSetting, updateSetting, isUpdating } = useSettings();
    const enabled = getSetting("spoken_commands_enabled") ?? true;

    return (
      <ToggleSwitch
        checked={enabled}
        onChange={(next) => updateSetting("spoken_commands_enabled", next)}
        isUpdating={isUpdating("spoken_commands_enabled")}
        label={t("settings.snippets.spokenCommands.title")}
        description={t("settings.snippets.spokenCommands.description")}
        descriptionMode={descriptionMode}
        grouped={grouped}
      />
    );
  },
);
