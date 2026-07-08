/**
 * Vue 版 useGSAP：gsap.context + 卸载时 revert（对齐 gsap-skills 规范）
 */
import { onMounted, onUnmounted, watch, type Ref } from 'vue'
import { gsap, prefersReducedMotion } from '@/lib/gsap'

type GsapCallback = () => void

export function useGsap(
  callback: GsapCallback,
  scope: Ref<HTMLElement | null | undefined>,
  options?: { deps?: () => unknown[] },
) {
  let ctx: gsap.Context | null = null

  const run = () => {
    ctx?.revert()
    ctx = null
    if (prefersReducedMotion()) return
    const el = scope.value
    if (!el) return
    ctx = gsap.context(callback, el)
  }

  onMounted(run)

  onUnmounted(() => {
    ctx?.revert()
    ctx = null
  })

  if (options?.deps) {
    watch(options.deps, () => run(), { flush: 'post' })
  }

  return { rerun: run }
}

export { gsap, prefersReducedMotion }
