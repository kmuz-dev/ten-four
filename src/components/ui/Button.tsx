import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?:
    | "primary"
    | "primary-soft"
    | "secondary"
    | "warning"
    | "danger"
    | "danger-ghost"
    | "ghost";
  size?: "sm" | "md" | "lg";
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className = "",
  variant = "primary",
  size = "md",
  ...props
}) => {
  const baseClasses =
    "font-normal rounded-md border focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-default";

  const variantClasses = {
    primary:
      "text-white bg-accent border-transparent shadow-[0_1px_1.5px_rgb(0_0_0/0.15)] hover:brightness-110 active:brightness-95",
    "primary-soft":
      "text-accent bg-accent/12 border-transparent hover:bg-accent/20",
    secondary: "mac-control border-transparent text-text active:brightness-95",
    // Secondary's neutral resting look, but hover/focus use the semantic
    // --color-warning token (theme.css) instead of the accent — for
    // buttons sitting on warning surfaces like SecureInputWarning
    warning:
      "text-text bg-mid-gray/10 border-mid-gray/20 hover:bg-warning/15 hover:border-warning focus:ring-1 focus:ring-warning",
    danger:
      "text-white bg-red-600 border-mid-gray/20 hover:bg-red-700 hover:border-red-700 focus:ring-1 focus:ring-red-500",
    "danger-ghost":
      "text-red-400 border-transparent hover:text-red-300 hover:bg-red-500/10 focus:bg-red-500/20",
    ghost:
      "text-current border-transparent hover:bg-text/[0.07] active:bg-text/[0.12]",
  };

  const sizeClasses = {
    sm: "px-2 h-[22px] text-xs",
    md: "px-3 h-[24px] text-sm",
    lg: "px-4 h-[30px] text-sm",
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};
