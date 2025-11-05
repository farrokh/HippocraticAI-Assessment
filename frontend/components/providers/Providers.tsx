"use client";

import { QuestionRefreshProvider } from "@/contexts/QuestionRefreshContext";
import { ReactNode } from "react";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <QuestionRefreshProvider>
      {children}
    </QuestionRefreshProvider>
  );
}

