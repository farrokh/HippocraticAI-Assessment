/**
 * Polls a URL with exponential backoff
 * @param url - The URL to poll
 * @param maxAttempts - Maximum number of attempts (default: 4)
 * @param maxWaitTime - Maximum total wait time in milliseconds (default: 60000 = 1 minute)
 * @returns Promise that resolves when polling succeeds or rejects after max attempts
 */
export async function pollWithExponentialBackoff<T = unknown>(
  url: string,
  maxAttempts: number = 4,
  maxWaitTime: number = 60000
): Promise<T> {
  const startTime = Date.now();
  let attempt = 0;
  
  while (attempt < maxAttempts) {
    // Check if we've exceeded the maximum wait time
    if (Date.now() - startTime > maxWaitTime) {
      throw new Error(`Polling timeout: exceeded maximum wait time of ${maxWaitTime}ms`);
    }
    
    try {
      const response = await fetch(url);
      
      if (response.ok) {
        const data = await response.json() as T;
        return data;
      }
      
      // If response is not ok, continue to next attempt
      console.log(`Polling attempt ${attempt + 1} failed with status: ${response.status}`);
    } catch (error) {
      console.log(`Polling attempt ${attempt + 1} failed with error:`, error);
    }
    
    attempt++;
    
    // If this isn't the last attempt, wait with exponential backoff
    if (attempt < maxAttempts) {
      const waitTime = Math.min(1000 * Math.pow(2, attempt - 1), 10000); // Cap at 10 seconds
      console.log(`Waiting ${waitTime}ms before next attempt...`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
  
  throw new Error(`Polling failed after ${maxAttempts} attempts`);
}
