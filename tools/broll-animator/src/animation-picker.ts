/**
 * djb2 hash of a filename -> single unsigned 32-bit integer.
 * Used as the sole randomization seed for all animation parameters.
 */
export function djb2(str: string): number {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 33) ^ str.charCodeAt(i);
  }
  return hash >>> 0;
}
