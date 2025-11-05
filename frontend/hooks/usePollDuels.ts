import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

interface UsePollDuelsOptions {
  questionId: string;
  initialDelay?: number;
  initialInterval?: number;
  maxInterval?: number;
  maxPollingTime?: number;
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Polls the duels endpoint with exponential backoff until duels are ready.
 * Used in ProcessingQuestion component to detect when generation completes.
 */
export function usePollDuels({
  questionId,
  initialDelay = 1000,
  initialInterval = 2000,
  maxInterval = 32000,
  maxPollingTime = 60000,
  onSuccess,
  onError,
}: UsePollDuelsOptions) {
  const router = useRouter();
  const callbacksRef = useRef({ onSuccess, onError });
  
  useEffect(() => {
    callbacksRef.current = { onSuccess, onError };
  }, [onSuccess, onError]);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    let interval = initialInterval;
    const startTime = Date.now();
    let cancelled = false;

    const poll = async () => {
      if (cancelled || Date.now() - startTime > maxPollingTime) return;

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/questions/${questionId}/duels/next`
        );

        if (cancelled) return;

        // Still processing (202) - continue polling with backoff
        if (response.status === 202) {
          interval = Math.min(interval * 1.2, maxInterval);
          timeoutId = setTimeout(poll, interval);
        } 
        // Duels ready (200) or all completed (204) - refresh page
        else if (response.ok || response.status === 204) {
          callbacksRef.current.onSuccess?.();
          router.refresh();
        } 
        // Error states
        else if (response.status === 404) {
          callbacksRef.current.onError?.(new Error("Question not found"));
        } 
        else {
          callbacksRef.current.onError?.(new Error(`Unexpected status: ${response.status}`));
        }
      } catch {
        // Network error - continue polling with increased backoff
        if (!cancelled) {
          interval = Math.min(interval * 2, maxInterval);
          timeoutId = setTimeout(poll, interval);
        }
      }
    };

    timeoutId = setTimeout(poll, initialDelay);

    return () => {
      cancelled = true;
      clearTimeout(timeoutId);
    };
  }, [questionId, router, initialDelay, initialInterval, maxInterval, maxPollingTime]);
}
