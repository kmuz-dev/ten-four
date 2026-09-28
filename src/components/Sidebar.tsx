import React from "react";
import { useTranslation } from "react-i18next";
import {
  Cog,
  FlaskConical,
  History,
  Info,
  Sparkles,
  Cpu,
  SlidersHorizontal,
  TextQuote,
  AppWindow,
} from "lucide-react";
import { HandyLogo } from "./icons/HandyMark";
import { useSettings } from "../hooks/useSettings";
import {
  GeneralSettings,
  AdvancedSettings,
  HistorySettings,
  DebugSettings,
  AboutSettings,
  PostProcessingSettings,
  ModelsSettings,
  SnippetsSettings,
  AppStylesSettings,
} from "./settings";

export type SidebarSection = keyof typeof SECTIONS_CONFIG;

interface IconProps {
  width?: number | string;
  height?: number | string;
  size?: number | string;
  className?: string;
  [key: string]: any;
}

interface SectionConfig {
  labelKey: string;
  icon: React.ComponentType<IconProps>;
  component: React.ComponentType;
  enabled: (settings: any) => boolean;
}

export const SECTIONS_CONFIG = {
  general: {
    labelKey: "sidebar.general",
    icon: SlidersHorizontal,
    component: GeneralSettings,
    enabled: () => true,
  },
  history: {
    labelKey: "sidebar.history",
    icon: History,
    component: HistorySettings,
    enabled: () => true,
  },
  models: {
    labelKey: "sidebar.models",
    icon: Cpu,
    component: ModelsSettings,
    enabled: () => true,
  },
  advanced: {
    labelKey: "sidebar.advanced",
    icon: Cog,
    component: AdvancedSettings,
    enabled: () => true,
  },
  snippets: {
    labelKey: "sidebar.snippets",
    icon: TextQuote,
    component: SnippetsSettings,
    enabled: () => true,
  },
  appstyles: {
    labelKey: "sidebar.appStyles",
    icon: AppWindow,
    component: AppStylesSettings,
    enabled: () => true,
  },
  postprocessing: {
    labelKey: "sidebar.postProcessing",
    icon: Sparkles,
    component: PostProcessingSettings,
    enabled: (settings) => settings?.post_process_enabled ?? false,
  },
  debug: {
    labelKey: "sidebar.debug",
    icon: FlaskConical,
    component: DebugSettings,
    enabled: (settings) => settings?.debug_mode ?? false,
  },
  about: {
    labelKey: "sidebar.about",
    icon: Info,
    component: AboutSettings,
    enabled: () => true,
  },
} as const satisfies Record<string, SectionConfig>;

interface SidebarProps {
  activeSection: SidebarSection;
  onSectionChange: (section: SidebarSection) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSectionChange,
}) => {
  const { t } = useTranslation();
  const { settings } = useSettings();

  const availableSections = Object.entries(SECTIONS_CONFIG)
    .filter(([_, config]) => config.enabled(settings))
    .map(([id, config]) => ({ id: id as SidebarSection, ...config }));

  // System Settings-style source list: graphite icon tiles, accent selection.
  // The top padding clears the macOS traffic lights (overlay title bar).
  return (
    <nav className="titlebar-pad flex flex-col w-[188px] shrink-0 h-full bg-sidebar border-e border-hairline px-2.5">
      <div data-tauri-drag-region className="px-1.5 pt-1 pb-4">
        <HandyLogo iconSize={26} className="pointer-events-none" />
      </div>
      <div className="flex flex-col w-full gap-0.5">
        {availableSections.map((section) => {
          const Icon = section.icon;
          const isActive = activeSection === section.id;

          return (
            <button
              type="button"
              key={section.id}
              aria-current={isActive ? "page" : undefined}
              className={`flex gap-2 items-center h-7 px-1.5 w-full rounded-md text-start cursor-default transition-colors duration-100 ${
                isActive ? "bg-accent text-white" : "hover:bg-text/[0.06]"
              }`}
              onClick={() => onSectionChange(section.id)}
            >
              <span
                className={`grid place-items-center size-5 shrink-0 rounded-[5px] ${
                  isActive
                    ? "bg-white/20"
                    : "bg-gradient-to-b from-[#98989d] to-[#6e6e73]"
                }`}
              >
                <Icon width={13} height={13} strokeWidth={2} color="white" />
              </span>
              <span
                className="text-[13px] truncate"
                title={t(section.labelKey)}
              >
                {t(section.labelKey)}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
