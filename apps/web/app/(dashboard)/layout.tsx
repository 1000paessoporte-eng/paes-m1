import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { TOKEN_COOKIE } from "@/lib/auth";

export default async function DashboardLayout({ children }: LayoutProps<"/">) {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value;
  if (!token) redirect("/login");

  return <div className="mx-auto w-full max-w-6xl flex-1 p-6">{children}</div>;
}
