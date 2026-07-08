/** 将高频回调合并到下一帧，减少流式更新造成的卡顿。 */
export function useRafBatch(onFlush: () => void) {
  let scheduled = false
  let rafId = 0

  const schedule = () => {
    if (scheduled) return
    scheduled = true
    rafId = requestAnimationFrame(() => {
      scheduled = false
      onFlush()
    })
  }

  const flushNow = () => {
    if (scheduled) {
      cancelAnimationFrame(rafId)
      scheduled = false
    }
    onFlush()
  }

  const cancel = () => {
    if (scheduled) {
      cancelAnimationFrame(rafId)
      scheduled = false
    }
  }

  return { schedule, flushNow, cancel }
}
