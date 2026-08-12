import type { ButtonHTMLAttributes } from "react";
import { cn } from "@paes-m1/utils";

type Variant = "primary" | "secondary" | "ghost";

const VARIANT_CLASSES: Record<Variant, string> = {
  primary: "btn-glow text-accent-foreground",
  secondary:
    "border border-border text-foreground hover:bg-surface-hover hover:border-border-strong",
  ghost: "text-muted hover:bg-surface-hover hover:text-foreground",
};

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

export function Button({
  variant = "primary",
  className,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50",
        VARIANT_CLASSES[variant],
        className
      )}
      {...props}
    />
  );
}
