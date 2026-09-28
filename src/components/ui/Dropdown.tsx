import React, { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

export interface DropdownOption {
  value: string;
  label: string;
  description?: string;
  disabled?: boolean;
}

interface DropdownProps {
  options: DropdownOption[];
  className?: string;
  menuClassName?: string;
  selectedValue: string | null;
  onSelect: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  onRefresh?: () => void;
}

export const Dropdown: React.FC<DropdownProps> = ({
  options,
  selectedValue,
  onSelect,
  className = "",
  menuClassName,
  placeholder = "Select an option...",
  disabled = false,
  onRefresh,
}) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const selectedOption = options.find(
    (option) => option.value === selectedValue,
  );

  const handleSelect = (value: string) => {
    onSelect(value);
    setIsOpen(false);
  };

  const handleToggle = () => {
    if (disabled) return;
    if (!isOpen && onRefresh) onRefresh();
    setIsOpen(!isOpen);
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        type="button"
        className={`mac-control ps-2.5 pe-1.5 h-[24px] text-sm rounded-md min-w-[180px] w-full text-start grid grid-cols-[1fr_auto] gap-2 items-center focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 ${
          disabled ? "opacity-50 cursor-not-allowed" : "cursor-default"
        }`}
        onClick={handleToggle}
        disabled={disabled}
      >
        <span className="truncate">{selectedOption?.label || placeholder}</span>
        {/* macOS pop-up button chevrons */}
        <svg
          className="w-4 h-4 text-text-secondary"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 16 16"
          aria-hidden
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.4}
            d="M5.5 6.5 8 4l2.5 2.5M5.5 9.5 8 12l2.5-2.5"
          />
        </svg>
      </button>
      {isOpen && !disabled && (
        <div
          className={`absolute top-full mt-1 p-1 bg-surface border border-hairline rounded-lg shadow-[0_10px_30px_rgb(0_0_0/0.18)] z-50 max-h-60 overflow-y-auto ${
            menuClassName ?? "left-0 right-0"
          }`}
        >
          {options.length === 0 ? (
            <div className="px-2 py-1 text-sm text-mid-gray">
              {t("common.noOptionsFound")}
            </div>
          ) : (
            options.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`group w-full text-sm text-start rounded-[5px] hover:bg-accent hover:text-white cursor-default ${
                  option.description ? "px-2.5 py-1.5" : "px-2.5 py-1"
                } ${option.disabled ? "opacity-50 cursor-not-allowed" : ""}`}
                onClick={() => handleSelect(option.value)}
                disabled={option.disabled}
              >
                <span
                  className={`block whitespace-normal break-words ${
                    option.description || selectedValue === option.value
                      ? "font-medium"
                      : ""
                  }`}
                >
                  {option.label}
                </span>
                {option.description && (
                  <span className="mt-0.5 block whitespace-normal text-xs font-normal leading-snug text-text-secondary group-hover:text-white/80">
                    {option.description}
                  </span>
                )}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
};
