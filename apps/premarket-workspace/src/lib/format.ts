export function formatNumber(value: unknown, digits = 2): string {
  if (value === null || value === undefined || value === "") return "N/A";
  const numeric = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numeric) ? numeric.toLocaleString("en-US", {maximumFractionDigits: digits}) : String(value);
}

export function formatPercent(value: unknown, digits = 2): string {
  if (value === null || value === undefined || value === "") return "N/A";
  const numeric = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numeric) ? `${(numeric * 100).toFixed(digits)}%` : String(value);
}

export function humanize(value: string): string {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function evidenceValue(value: unknown): unknown {
  if (value && typeof value === "object" && "value" in value) return (value as {value: unknown}).value;
  return value;
}
