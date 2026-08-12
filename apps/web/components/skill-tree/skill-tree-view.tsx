"use client";

import { motion } from "framer-motion";
import type { ReactElement } from "react";
import { cn } from "@paes-m1/utils";
import type { SkillNode } from "@/lib/api";

type AxisMeta = {
  label: string;
  iconBg: string;
  iconColor: string;
  border: string;
  bar: string;
  icon: () => ReactElement;
};

const AXIS_META: Record<SkillNode["axis"], AxisMeta> = {
  numeros: {
    label: "Números",
    iconBg: "bg-sky-500/10",
    iconColor: "text-sky-400",
    border: "hover:border-sky-500/50",
    bar: "bg-sky-400",
    icon: NumbersIcon,
  },
  algebra: {
    label: "Álgebra",
    iconBg: "bg-violet-500/10",
    iconColor: "text-violet-400",
    border: "hover:border-violet-500/50",
    bar: "bg-violet-400",
    icon: AlgebraIcon,
  },
  geometria: {
    label: "Geometría",
    iconBg: "bg-emerald-500/10",
    iconColor: "text-emerald-400",
    border: "hover:border-emerald-500/50",
    bar: "bg-emerald-400",
    icon: GeometryIcon,
  },
  probabilidad: {
    label: "Probabilidad",
    iconBg: "bg-amber-500/10",
    iconColor: "text-amber-400",
    border: "hover:border-amber-500/50",
    bar: "bg-amber-400",
    icon: DiceIcon,
  },
};

const AXIS_ORDER: SkillNode["axis"][] = [
  "numeros",
  "algebra",
  "geometria",
  "probabilidad",
];

interface SkillTreeViewProps {
  nodes: SkillNode[];
}

export function SkillTreeView({ nodes }: SkillTreeViewProps) {
  const nameByCode = new Map(nodes.map((n) => [n.code, n.name]));

  const columns = AXIS_ORDER.map((axis) => ({
    axis,
    nodes: nodes
      .filter((n) => n.axis === axis)
      .sort((a, b) => a.tier - b.tier || a.display_order - b.display_order),
  }));

  return (
    <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 xl:grid-cols-4">
      {columns.map((column) => {
        const meta = AXIS_META[column.axis];
        return (
          <div key={column.axis} className="flex flex-col gap-4">
            <div className="flex items-center gap-2.5">
              <span
                className={cn(
                  "flex h-7 w-7 items-center justify-center rounded-md",
                  meta.iconBg,
                  meta.iconColor
                )}
              >
                <meta.icon />
              </span>
              <h2 className="text-sm font-medium text-foreground">
                {meta.label}
              </h2>
            </div>

            <ol
              className="relative flex flex-col gap-3 pl-5"
              style={{
                backgroundImage: `linear-gradient(to bottom, var(--border-strong), transparent)`,
                backgroundRepeat: "no-repeat",
                backgroundSize: "1px 100%",
              }}
            >
              {column.nodes.map((node, i) => {
                const isRoot = node.prerequisite_codes.length === 0;
                return (
                  <motion.li
                    key={node.code}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.06, duration: 0.35, ease: "easeOut" }}
                    className={cn(
                      "card-hover -ml-[25px] list-none overflow-hidden rounded-xl border border-border bg-surface transition-colors",
                      meta.border,
                      !isRoot && "opacity-80"
                    )}
                  >
                    <div className="flex">
                      <span className={cn("w-1 shrink-0", meta.bar, !isRoot && "opacity-40")} />
                      <div className="flex-1 p-4">
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-xs font-medium text-muted">
                            Nivel {node.tier}
                          </span>
                          <span
                            className={cn(
                              "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium",
                              isRoot
                                ? "bg-success/15 text-success"
                                : "bg-surface-hover text-muted"
                            )}
                          >
                            {isRoot ? <UnlockIcon /> : <LockIcon />}
                            {isRoot ? "Desbloqueado" : "Bloqueado"}
                          </span>
                        </div>

                        <p className="mt-2 text-sm font-medium text-foreground">
                          {node.name}
                        </p>

                        {node.prerequisite_codes.length > 0 && (
                          <p className="mt-2 text-xs text-muted">
                            Requiere:{" "}
                            {node.prerequisite_codes
                              .map((code) => nameByCode.get(code) ?? code)
                              .join(", ")}{" "}
                            · ≥{Math.round(node.unlock_threshold * 100)}% acierto
                          </p>
                        )}
                      </div>
                    </div>
                  </motion.li>
                );
              })}
            </ol>
          </div>
        );
      })}
    </div>
  );
}

function NumbersIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M5 9h14M5 15h14M9 4L7 20M17 4l-2 16" />
    </svg>
  );
}

function AlgebraIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 6h4l4 12h4M4 18h4l1.5-4.5" />
    </svg>
  );
}

function GeometryIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round">
      <path d="M12 4l8 16H4z" />
      <circle cx="12" cy="14" r="2.2" />
    </svg>
  );
}

function DiceIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="4" width="16" height="16" rx="3" />
      <circle cx="9" cy="9" r="1" fill="currentColor" stroke="none" />
      <circle cx="15" cy="9" r="1" fill="currentColor" stroke="none" />
      <circle cx="9" cy="15" r="1" fill="currentColor" stroke="none" />
      <circle cx="15" cy="15" r="1" fill="currentColor" stroke="none" />
      <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </svg>
  );
}

function UnlockIcon() {
  return (
    <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 7.5-2" />
    </svg>
  );
}
