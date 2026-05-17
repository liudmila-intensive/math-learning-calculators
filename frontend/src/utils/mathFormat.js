const subMap = {
  0: "₀",
  1: "₁",
  2: "₂",
  3: "₃",
  4: "₄",
  5: "₅",
  6: "₆",
  7: "₇",
  8: "₈",
  9: "₉",
};

function digitsToSubscript(digits) {
  return digits
    .split("")
    .map((digit) => subMap[digit] || digit)
    .join("");
}

export function toSubscript(text) {
  if (text === null || text === undefined) return "";

  return String(text).replace(/([xABuvΔ])_?(\d+)/g, (_, letter, digits) => {
    return `${letter}${digitsToSubscript(digits)}`;
  });
}
