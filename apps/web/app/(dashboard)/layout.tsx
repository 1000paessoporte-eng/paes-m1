export default function DashboardLayout({ children }: LayoutProps<"/">) {
  return <div className="mx-auto w-full max-w-6xl flex-1 p-6">{children}</div>;
}
