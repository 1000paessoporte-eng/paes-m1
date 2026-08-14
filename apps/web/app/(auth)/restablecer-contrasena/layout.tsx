// La página es un Client Component y no puede exportar `metadata`; el
// título vive acá, que sí se resuelve en el servidor.
export const metadata = {
  title: "Nueva contraseña",
  description: "Define una contraseña nueva para tu cuenta.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
