"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface QuestionRefreshContextType {
  refreshTrigger: number;
  triggerRefresh: () => void;
}

const QuestionRefreshContext = createContext<QuestionRefreshContextType | undefined>(undefined);

export function QuestionRefreshProvider({ children }: { children: ReactNode }) {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const triggerRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <QuestionRefreshContext.Provider value={{ refreshTrigger, triggerRefresh }}>
      {children}
    </QuestionRefreshContext.Provider>
  );
}

export function useQuestionRefresh() {
  const context = useContext(QuestionRefreshContext);
  if (context === undefined) {
    throw new Error("useQuestionRefresh must be used within a QuestionRefreshProvider");
  }
  return context;
}

