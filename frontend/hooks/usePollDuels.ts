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
 * Custom hook to poll for duels with exponential backoff
 * Automatically refreshes the page when duels become available
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
    const intervalRef = { current: initialInterval };
    const startTime = Date.now();
    let cancelled = false;

    const poll = async () => {
      if (cancelled || Date.now() - startTime > maxPollingTime) {
        return;
      }

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/questions/${questionId}/duels/next`
        );

        if (cancelled) return;

        if (response.status === 202) {
          // Still processing, schedule next poll with exponential backoff
          const nextInterval = intervalRef.current;
          intervalRef.current = Math.min(intervalRef.current * 1.2, maxInterval);
          timeoutId = setTimeout(poll, nextInterval);
        } else if (response.ok) {
          callbacksRef.current.onSuccess?.();
          router.refresh();
        } else if (response.status === 404) {
          callbacksRef.current.onError?.(new Error("Question not found"));
        } else {
          callbacksRef.current.onError?.(new Error(`Failed to fetch duel: ${response.status}`));
        }
      } catch {
        // Continue polling on network errors
        if (!cancelled) {
          const nextInterval = intervalRef.current;
          intervalRef.current = Math.min(intervalRef.current * 2, maxInterval);
          timeoutId = setTimeout(poll, nextInterval);
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

