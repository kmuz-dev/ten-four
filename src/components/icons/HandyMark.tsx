import React, { useId } from "react";

// Code identifiers retain the upstream Handy name. The visible identity is
// Ten-Four: a pocket recorder mark and two approved wordmarks.
const PRODUCT_NAME = "Ten-Four";

interface SizeProps {
  size?: number;
  className?: string;
}

interface WordmarkProps {
  height?: number;
  className?: string;
}

// Custom vector lettering keeps the brand deterministic across platforms.
const NUMERIC_WORDMARK_PATH =
  "M0 4 4 0H9V16H4.2V5.2L0 8ZM11 3 14 0H23L26 3V13L23 16H14L11 13ZM16 4V12H21V4ZM39 0H46V9H49V13H46V16H41V13H30V8L37 0H42L36 9H41V5Z";

const NAME_WORDMARK_PATH =
  "M0 0H6V1.6H3.9V8H2.1V1.6H0ZM8 0H14V1.5H9.8V3.2H13.3V4.7H9.8V6.5H14V8H8ZM16 8V0H17.8L20.2 4.5V0H22V8H20.2L17.8 3.5V8ZM24 3.3H28.5V4.8H24ZM30.5 0H36.5V1.5H32.3V3.3H35.8V4.8H32.3V8H30.5ZM38.5 1.5 40 0H43L44.5 1.5V6.5L43 8H40L38.5 6.5ZM40.3 2V6H42.7V2ZM46.5 0H48.3V6H50.7V0H52.5V6.4L50.9 8H48.1L46.5 6.4ZM54.5 0H59L60.5 1.5V3.5L59.3 4.7L61 8H59L57.6 5H56.3V8H54.5ZM56.3 1.6V3.5H58.5V1.6Z";

/** The approved numeric wordmark. The orange period is part of the identity. */
export const TenFourNumericWordmark: React.FC<WordmarkProps> = ({
  height = 16,
  className,
}) => (
  <svg
    width={(height * 49) / 16}
    height={height}
    viewBox="0 0 49 16"
    className={className}
    aria-hidden
  >
    <path d={NUMERIC_WORDMARK_PATH} fill="currentColor" fillRule="evenodd" />
    <circle cx="28.5" cy="13" r="2.25" fill="var(--color-tally)" />
  </svg>
);

/** The approved TEN-FOUR wordmark from the secondary lockup. */
export const TenFourWordmark: React.FC<WordmarkProps> = ({
  height = 8,
  className,
}) => (
  <svg
    width={(height * 61) / 8}
    height={height}
    viewBox="0 0 61 8"
    className={className}
    aria-hidden
  >
    <path d={NAME_WORDMARK_PATH} fill="currentColor" fillRule="evenodd" />
  </svg>
);

/** Full-color app icon: the squircle is the recorder face, edge to edge. */
export const HandyAppIcon: React.FC<SizeProps> = ({ size = 64, className }) => {
  const id = useId().replace(/:/g, "");
  return (
    <svg
      width={size}
      height={size}
      viewBox="8 8 112 112"
      className={className}
      aria-hidden
    >
      <defs>
        <linearGradient id={`${id}base`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#E8E2D5" />
          <stop offset="1" stopColor="#B2A997" />
        </linearGradient>
        <filter id={`${id}shadow`} x="-30%" y="-30%" width="160%" height="170%">
          <feDropShadow dx="0" dy="3" stdDeviation="3" floodOpacity=".28" />
        </filter>
      </defs>

      <rect
        x="12"
        y="12"
        width="104"
        height="104"
        rx="23.5"
        fill={`url(#${id}base)`}
        filter={`url(#${id}shadow)`}
      />
      <rect
        x="12.4"
        y="12.4"
        width="103.2"
        height="103.2"
        rx="23.1"
        fill="none"
        stroke="rgba(255,255,255,.51)"
        strokeWidth="0.8"
      />

      <rect x="22" y="22" width="84" height="40" rx="10" fill="#29292C" />
      <g transform="translate(29.7 30.8) scale(1.4)" fill="#F2F1EE">
        <path d={NUMERIC_WORDMARK_PATH} fillRule="evenodd" />
        <circle cx="28.5" cy="13" r="2.25" fill="#FF4A26" />
      </g>

      <g fill="#343438">
        <rect x="22" y="70" width="26" height="36" rx="8" />
        <rect x="51" y="70" width="26" height="36" rx="8" />
        <rect x="80" y="70" width="26" height="36" rx="8" />
      </g>
      <circle cx="35" cy="88" r="7" fill="#FF4A26" />
      <rect x="59.5" y="83.5" width="9" height="9" rx="1.2" fill="#DDD6C7" />
      <path d="m89 82 10 6-10 6Z" fill="#DDD6C7" />
    </svg>
  );
};

/** One-color recorder mark for small UI and tray-sized applications. */
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
    <path
      d="M21.5 5V2.5a2 2 0 0 1 4 0V5M7 5h18a4 4 0 0 1 4 4v17a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V9a4 4 0 0 1 4-4Z"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinejoin="round"
    />
    <rect
      x="7"
      y="9"
      width="18"
      height="8"
      rx="2"
      stroke="currentColor"
      strokeWidth="1.7"
    />
    <circle
      cx="10"
      cy="23"
      r="2.3"
      fill={live ? "var(--color-tally-hud)" : "currentColor"}
    />
    <rect x="14" y="20.7" width="4.6" height="4.6" rx="1" fill="currentColor" />
    <path d="m21.5 20.5 5 2.8-5 2.8Z" fill="currentColor" />
  </svg>
);

interface HandyLogoProps {
  iconSize?: number;
  className?: string;
  wordmark?: "name" | "numeric";
}

/** Pocket recorder icon paired with either approved Ten-Four wordmark. */
export const HandyLogo: React.FC<HandyLogoProps> = ({
  iconSize = 36,
  className = "",
  wordmark = "name",
}) => (
  <div
    className={`flex items-center gap-2.5 text-text ${className}`}
    role="img"
    aria-label={PRODUCT_NAME}
  >
    <HandyAppIcon size={iconSize} className="shrink-0 drop-shadow-sm" />
    {wordmark === "numeric" ? (
      <TenFourNumericWordmark height={iconSize * 0.38} />
    ) : (
      <TenFourWordmark height={iconSize * 0.32} />
    )}
  </div>
);
