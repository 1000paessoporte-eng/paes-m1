export function niceMax(value: number): number {
  if (value <= 0) return 10;
  const steps = [5, 10, 15, 20, 30, 40, 50, 60, 90, 120, 180, 240, 300, 360, 480, 600];
  for (const step of steps) {
    if (value <= step) return step;
  }
  const magnitude = 10 ** Math.floor(Math.log10(value));
  return Math.ceil(value / magnitude) * magnitude;
}

export function roundedTopBarPath(
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number
): string {
  if (height <= 0) return "";
  const r = Math.min(radius, width / 2, height);
  return [
    `M${x},${y + height}`,
    `L${x},${y + r}`,
    `A${r},${r} 0 0 1 ${x + r},${y}`,
    `L${x + width - r},${y}`,
    `A${r},${r} 0 0 1 ${x + width},${y + r}`,
    `L${x + width},${y + height}`,
    "Z",
  ].join(" ");
}

const SHORT_DATE = new Intl.DateTimeFormat("es-CL", { day: "numeric", month: "short" });
const FULL_DATE = new Intl.DateTimeFormat("es-CL", {
  weekday: "long",
  day: "numeric",
  month: "long",
});

export function formatShortDate(iso: string): string {
  return SHORT_DATE.format(new Date(`${iso}T00:00:00`));
}

export function formatFullDate(iso: string): string {
  const s = FULL_DATE.format(new Date(`${iso}T00:00:00`));
  return s.charAt(0).toUpperCase() + s.slice(1);
}
