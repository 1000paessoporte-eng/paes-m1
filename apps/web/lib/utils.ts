// Reexporta el `cn` canónico del monorepo para que shadcn/ui lo encuentre en
// `@/lib/utils` (su ruta por defecto) sin duplicar la implementación: la
// única versión de `cn` vive en `packages/utils`.
export { cn } from "@paes-m1/utils";
