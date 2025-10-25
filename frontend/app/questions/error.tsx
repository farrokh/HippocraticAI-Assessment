"use client";

import { useEffect } from "react";
import NoComparison from "@/components/questions/NoComparison";

export default function Error({
  error,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("Comparison page error:", error);
  }, [error]);

  return (
    <NoComparison 
      message={error.message || "Something went wrong loading the comparison"}
      showBackButton={true}
    />
  );
}
