import assert from "node:assert/strict";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import {
  HandyAppIcon,
  HandyLogo,
  TenFourNumericWordmark,
  TenFourWordmark,
} from "./HandyMark";

const nameLockup = renderToStaticMarkup(
  <HandyLogo iconSize={26} wordmark="name" />,
);
assert.match(nameLockup, /aria-label="Ten-Four"/);
assert.match(nameLockup, /viewBox="0 0 61 8"/);

const numericLockup = renderToStaticMarkup(
  <HandyLogo iconSize={52} wordmark="numeric" />,
);
assert.match(numericLockup, /viewBox="0 0 49 16"/);
assert.match(numericLockup, /fill="var\(--color-tally\)"/);

const numericWordmark = renderToStaticMarkup(
  <TenFourNumericWordmark height={16} />,
);
assert.match(numericWordmark, /width="49"/);

const nameWordmark = renderToStaticMarkup(<TenFourWordmark height={8} />);
assert.match(nameWordmark, /width="61"/);

const appIcon = renderToStaticMarkup(<HandyAppIcon size={64} />);
assert.match(appIcon, /viewBox="8 8 112 112"/);
assert.equal(
  (appIcon.match(/#FF4A26/g) ?? []).length,
  2,
  "app icon keeps Tally for the 10.4 decimal and the record control only",
);
assert.match(
  appIcon,
  /<rect x="12" y="12" width="104" height="104" rx="23.5"/,
  "the squircle is the recorder face itself, edge to edge",
);

console.log("HandyMark: all assertions passed");
