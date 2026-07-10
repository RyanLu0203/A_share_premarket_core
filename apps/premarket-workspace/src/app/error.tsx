"use client";

import { ErrorState } from "@/components/ui";

export default function ErrorPage({error}: {error: Error}) {
  return <ErrorState message={error.message} />;
}
