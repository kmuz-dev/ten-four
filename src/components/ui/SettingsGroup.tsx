import React from "react";

interface SettingsGroupProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
}

export const SettingsGroup: React.FC<SettingsGroupProps> = ({
  title,
  description,
  children,
}) => {
  return (
    <div className="space-y-2">
      {title && (
        <div className="px-1">
          <h2 className="text-sm font-semibold text-text">{title}</h2>
          {description && (
            <p className="text-xs text-text-secondary mt-0.5">{description}</p>
          )}
        </div>
      )}
      <div className="bg-surface border border-hairline rounded-[10px] overflow-visible">
        <div className="grouped-rows">{children}</div>
      </div>
    </div>
  );
};
