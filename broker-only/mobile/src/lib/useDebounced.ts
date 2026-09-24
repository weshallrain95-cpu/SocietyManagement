import { useEffect, useState } from 'react';

/** The value, but only after it stops changing for `ms` — for search-as-you-type without a request per key. */
export function useDebounced<T>(value: T, ms: number): T {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), ms);
    return () => clearTimeout(t);
  }, [value, ms]);
  return v;
}
