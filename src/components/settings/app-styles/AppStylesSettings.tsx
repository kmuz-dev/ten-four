import React, { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { commands, type AppCategory, type SeenApp } from "@/bindings";
import { SettingsGroup } from "../../ui/SettingsGroup";
import { SettingContainer } from "../../ui/SettingContainer";
import { Dropdown } from "../../ui/Dropdown";
import { AppStylesToggle } from "../AppStylesToggle";

const CATEGORIES: AppCategory[] = [
  "code",
  "terminal",
  "ai_chat",
  "email",
  "work_chat",
  "personal_chat",
  "notes",
  "other",
];

export const AppStylesSettings: React.FC = () => {
  const { t } = useTranslation();
  const [apps, setApps] = useState<SeenApp[]>([]);

  const refresh = useCallback(() => {
    commands.listSeenApps().then(setApps);
  }, []);

  // New apps appear as you dictate into them, so refresh when the window
  // regains focus as well as on first render.
  useEffect(() => {
    refresh();
    window.addEventListener("focus", refresh);
    return () => window.removeEventListener("focus", refresh);
  }, [refresh]);

  const handleCategory = async (app: SeenApp, category: string) => {
    const result = await commands.setAppCategory(
      app.bundle_id,
      category as AppCategory,
    );
    if (result.status === "error") {
      toast.error(result.error);
    }
    refresh();
  };

  const categoryOptions = CATEGORIES.map((category) => ({
    value: category,
    label: t(`settings.appStyles.categories.${category}.label`),
  }));

  return (
    <div className="max-w-3xl w-full mx-auto space-y-6">
      <SettingsGroup
        title={t("settings.appStyles.title")}
        description={t("settings.appStyles.description")}
      >
        <AppStylesToggle descriptionMode="inline" grouped={true} />
      </SettingsGroup>

      <SettingsGroup
        title={t("settings.appStyles.yourApps.title")}
        description={t("settings.appStyles.yourApps.description")}
      >
        {apps.length === 0 ? (
          <p className="px-3 py-3 text-sm text-text-secondary">
            {t("settings.appStyles.yourApps.empty")}
          </p>
        ) : (
          apps.map((app) => (
            <SettingContainer
              key={app.bundle_id}
              title={app.name}
              description={
                app.is_custom
                  ? t("settings.appStyles.yourApps.custom")
                  : t("settings.appStyles.yourApps.builtIn")
              }
              descriptionMode="inline"
              grouped={true}
            >
              <Dropdown
                options={categoryOptions}
                selectedValue={app.category}
                onSelect={(value) => handleCategory(app, value)}
              />
            </SettingContainer>
          ))
        )}
      </SettingsGroup>

      <SettingsGroup title={t("settings.appStyles.stylesTitle")}>
        {CATEGORIES.map((category) => (
          <div key={category} className="px-3 py-2.5 space-y-0.5">
            <p className="text-sm text-text">
              {t(`settings.appStyles.categories.${category}.label`)}
            </p>
            <p className="text-xs text-text-secondary">
              {t(`settings.appStyles.categories.${category}.description`)}
            </p>
          </div>
        ))}
      </SettingsGroup>
    </div>
  );
};
