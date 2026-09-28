import React, { useId } from "react";

// The Handy mark (DESIGN.md, "Mark"): one keycap seen from above with a
// caps-lock style LED. The LED is the only color, and it is Tally.

// The product name is a brand wordmark, not translatable copy.
const PRODUCT_NAME = "Handy";

interface SizeProps {
  size?: number;
  className?: string;
}

/** Full-color app icon: graphite squircle, graphite keycap, Tally LED. */
export const HandyAppIcon: React.FC<SizeProps> = ({ size = 64, className }) => {
  // Gradient/filter ids must be unique per instance on a page.
  const id = useId().replace(/:/g, "");
  return (
    <svg
      width={size}
      height={size}
      viewBox="12 12 104 104"
      className={className}
      aria-hidden
    >
      <defs>
        <linearGradient id={`${id}b`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#3C3C40" />
          <stop offset="1" stopColor="#1C1C1F" />
        </linearGradient>
        <linearGradient id={`${id}s`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#4B4B50" />
          <stop offset="1" stopColor="#27272A" />
        </linearGradient>
        <linearGradient id={`${id}t`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#606066" />
          <stop offset="1" stopColor="#46464B" />
        </linearGradient>
        <filter id={`${id}g`} x="-2" y="-2" width="5" height="5">
          <feGaussianBlur stdDeviation="3.5" />
        </filter>
      </defs>
      <rect
        x="12"
        y="12"
        width="104"
        height="104"
        rx="23.5"
        fill={`url(#${id}b)`}
      />
      <rect
        x="12.5"
        y="12.5"
        width="103"
        height="103"
        rx="23"
        fill="none"
        stroke="rgba(255,255,255,.1)"
      />
      <rect
        x="30"
        y="31"
        width="68"
        height="68"
        rx="17"
        fill={`url(#${id}s)`}
      />
      <rect
        x="38"
        y="35"
        width="52"
        height="52"
        rx="13"
        fill={`url(#${id}t)`}
      />
      <rect
        x="38.5"
        y="35.5"
        width="51"
        height="51"
        rx="12.5"
        fill="none"
        stroke="rgba(255,255,255,.14)"
      />
      <circle
        cx="78"
        cy="47"
        r="7"
        fill="#FF4A26"
        opacity=".55"
        filter={`url(#${id}g)`}
      />
      <circle cx="78" cy="47" r="3.6" fill="#FF5A36" />
    </svg>
  );
};

/** One-color keycap for small sizes; `live` lights the LED in Tally. */
export const HandyMark: React.FC<SizeProps & { live?: boolean }> = ({
  size = 16,
  className,
  live = false,
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 32 32"
    fill="none"
    className={className}
    aria-hidden
  >
    <rect
      x="3"
      y="3"
      width="26"
      height="26"
      rx="7"
      stroke="currentColor"
      strokeWidth="2"
    />
    <rect
      x="7.5"
      y="6"
      width="17"
      height="17"
      rx="4.5"
      stroke="currentColor"
      strokeWidth="1.5"
    />
    <circle
      cx="19.8"
      cy="10.3"
      r="1.9"
      fill={live ? "var(--color-tally-hud)" : "currentColor"}
    />
  </svg>
);

/** App icon beside the "Handy" wordmark, set in SF Pro like a system app. */
export const HandyLogo: React.FC<{ iconSize?: number; className?: string }> = ({
  iconSize = 36,
  className = "",
}) => (
  <div className={`flex items-center gap-2.5 ${className}`}>
    <HandyAppIcon size={iconSize} className="shrink-0 drop-shadow-sm" />
    <span
      className="font-semibold tracking-tight text-text"
      style={{ fontSize: iconSize * 0.5 }}
    >
      {PRODUCT_NAME}
    </span>
  </div>
);
