import React from "react";
import { useTranslation } from "react-i18next";
import { ToggleSwitch } from "../ui/ToggleSwitch";
import { useSettings } from "../../hooks/useSettings";

interface AppStylesToggleProps {
  descriptionMode?: "inline" | "tooltip";
  grouped?: boolean;
}

export const AppStylesToggle: React.FC<AppStylesToggleProps> = React.memo(
  ({ descriptionMode = "tooltip", grouped = false }) => {
    const { t } = useTranslation();
    const { getSetting, updateSetting, isUpdating } = useSettings();
    const enabled = getSetting("app_styles_enabled") ?? true;

    return (
      <ToggleSwitch
        checked={enabled}
        onChange={(next) => updateSetting("app_styles_enabled", next)}
        isUpdating={isUpdating("app_styles_enabled")}
        label={t("settings.appStyles.toggle.title")}
        description={t("settings.appStyles.toggle.description")}
        descriptionMode={descriptionMode}
        grouped={grouped}
      />
    );
  },
);
