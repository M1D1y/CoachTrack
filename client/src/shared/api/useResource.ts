import { useEffect, useState } from 'react'

export function useResource<T>(key: string, load: (signal: AbortSignal) => Promise<T>) {
  const [state, setState] = useState<{ data: T | null; loading: boolean; error: string }>({ data: null, loading: true, error: '' })
  const [revision, setRevision] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    setState({ data: null, loading: true, error: '' })
    load(controller.signal).then(
      (data) => { if (!controller.signal.aborted) setState({ data, loading: false, error: '' }) },
      (error: Error) => { if (!controller.signal.aborted) setState({ data: null, loading: false, error: error.message }) },
    )
    return () => controller.abort()
  }, [key, revision])

  return { ...state, refresh: () => setRevision((value) => value + 1) }
}
