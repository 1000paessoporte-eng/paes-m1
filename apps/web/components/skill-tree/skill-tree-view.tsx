"use client";

import { motion } from "framer-motion";
import { cn } from "@paes-m1/utils";
import type { SkillNode } from "@/lib/api";

const AXIS_META: Record<
  SkillNode["axis"],
  { label: string; accent: string; dot: string }
> = {
  numeros: {
    label: "Números",
    accent: "border-sky-500/40 hover:border-sky-500/70",
    dot: "bg-sky-400",
  },
  algebra: {
    label: "Álgebra",
    accent: "border-violet-500/40 hover:border-violet-500/70",
    dot: "bg-violet-400",
  },
  geometria: {
    label: "Geometría",
    accent: "border-emerald-500/40 hover:border-emerald-500/70",
    dot: "bg-emerald-400",
  },
  probabilidad: {
    label: "Probabilidad",
    accent: "border-amber-500/40 hover:border-amber-500/70",
    dot: "bg-amber-400",
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
      {columns.map((column) => (
        <div key={column.axis} className="flex flex-col gap-4">
          <div className="flex items-center gap-2">
            <span
              className={cn("h-2 w-2 rounded-full", AXIS_META[column.axis].dot)}
            />
            <h2 className="text-sm font-medium text-muted">
              {AXIS_META[column.axis].label}
            </h2>
          </div>

          <ol className="relative flex flex-col gap-3 border-l border-border pl-5">
            {column.nodes.map((node, i) => {
              const isRoot = node.prerequisite_codes.length === 0;
              return (
                <motion.li
                  key={node.code}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.06, duration: 0.35, ease: "easeOut" }}
                  className={cn(
                    "-ml-[25px] list-none rounded-lg border bg-surface p-4 transition-colors",
                    AXIS_META[column.axis].accent,
                    !isRoot && "opacity-70"
                  )}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-medium text-muted">
                      Nivel {node.tier}
                    </span>
                    <span
                      className={cn(
                        "rounded-full px-2 py-0.5 text-[10px] font-medium",
                        isRoot
                          ? "bg-success/15 text-success"
                          : "bg-surface-hover text-muted"
                      )}
                    >
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
                </motion.li>
              );
            })}
          </ol>
        </div>
      ))}
    </div>
  );
}
