import React from "react";
import { SettingContainer } from "./SettingContainer";

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  isUpdating?: boolean;
  label: string;
  description: string;
  descriptionMode?: "inline" | "tooltip";
  grouped?: boolean;
  tooltipPosition?: "top" | "bottom";
}

export const ToggleSwitch: React.FC<ToggleSwitchProps> = ({
  checked,
  onChange,
  disabled = false,
  isUpdating = false,
  label,
  description,
  descriptionMode = "tooltip",
  grouped = false,
  tooltipPosition = "top",
}) => {
  return (
    <SettingContainer
      title={label}
      description={description}
      descriptionMode={descriptionMode}
      grouped={grouped}
      disabled={disabled}
      tooltipPosition={tooltipPosition}
    >
      <label
        className={`flex items-center ${disabled || isUpdating ? "cursor-not-allowed" : "cursor-pointer"}`}
      >
        <input
          type="checkbox"
          value=""
          className="sr-only peer"
          checked={checked}
          disabled={disabled || isUpdating}
          onChange={(e) => onChange(e.target.checked)}
        />
        {/* macOS switch: 32x18 track, 16px knob that springs across. */}
        <div className="relative w-[32px] h-[18px] rounded-full bg-text/15 shadow-[inset_0_0_0_0.5px_rgb(0_0_0/0.08)] transition-colors duration-200 peer-checked:bg-accent peer-focus-visible:ring-2 peer-focus-visible:ring-accent/50 peer-focus-visible:ring-offset-1 peer-disabled:opacity-50 after:content-[''] after:absolute after:top-px after:start-px after:size-4 after:rounded-full after:bg-white after:shadow-[0_0_0_0.5px_rgb(0_0_0/0.15),0_1px_2px_rgb(0_0_0/0.25)] after:transition-transform after:duration-200 after:ease-[cubic-bezier(.2,.9,.25,1.04)] peer-checked:after:translate-x-[14px] rtl:peer-checked:after:-translate-x-[14px]"></div>
      </label>
      {isUpdating && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}
    </SettingContainer>
  );
};
