import { PracticeRunner } from "@/components/practice/practice-runner";

export default async function PracticeNodePage({
  params,
}: PageProps<"/practicar/[code]">) {
  const { code } = await params;
  return <PracticeRunner code={code} />;
}
