import { gsap, prefersReducedMotion } from '@/lib/gsap'

function panelEndRect() {
  const vw = window.innerWidth
  const vh = window.innerHeight
  const width = Math.min(vw * 0.92, 1200)
  const height = Math.min(vh * 0.86, 820)
  return {
    width,
    height,
    left: (vw - width) / 2,
    top: (vh - height) / 2,
  }
}

function transformToSource(sourceEl: HTMLElement) {
  const sr = sourceEl.getBoundingClientRect()
  const end = panelEndRect()
  const scaleX = Math.max(sr.width / end.width, 0.08)
  const scaleY = Math.max(sr.height / end.height, 0.08)
  const x = sr.left + sr.width / 2 - (end.left + end.width / 2)
  const y = sr.top + sr.height / 2 - (end.top + end.height / 2)
  return { end, x, y, scaleX, scaleY }
}

export function animateChartExpand(
  sourceEl: HTMLElement,
  panelEl: HTMLElement,
  backdropEl: HTMLElement,
  onComplete?: () => void,
) {
  if (prefersReducedMotion()) {
    gsap.set(backdropEl, { opacity: 1 })
    gsap.set(panelEl, { opacity: 1, x: 0, y: 0, scaleX: 1, scaleY: 1 })
    onComplete?.()
    return
  }

  const { end, x, y, scaleX, scaleY } = transformToSource(sourceEl)

  gsap.set(panelEl, {
    position: 'fixed',
    top: end.top,
    left: end.left,
    width: end.width,
    height: end.height,
    x,
    y,
    scaleX,
    scaleY,
    transformOrigin: 'center center',
    opacity: 0.9,
  })
  gsap.set(backdropEl, { opacity: 0 })

  const tl = gsap.timeline({ onComplete })
  tl.to(backdropEl, { opacity: 1, duration: 0.3, ease: 'power2.out' }, 0)
  tl.to(
    panelEl,
    {
      x: 0,
      y: 0,
      scaleX: 1,
      scaleY: 1,
      opacity: 1,
      duration: 0.5,
      ease: 'power3.out',
    },
    0,
  )
}

export function animateChartCollapse(
  sourceEl: HTMLElement,
  panelEl: HTMLElement,
  backdropEl: HTMLElement,
  onComplete?: () => void,
) {
  if (prefersReducedMotion()) {
    gsap.set(backdropEl, { opacity: 0 })
    onComplete?.()
    return
  }

  const { x, y, scaleX, scaleY } = transformToSource(sourceEl)

  const tl = gsap.timeline({ onComplete })
  tl.to(backdropEl, { opacity: 0, duration: 0.28, ease: 'power2.in' }, 0)
  tl.to(
    panelEl,
    {
      x,
      y,
      scaleX,
      scaleY,
      opacity: 0.88,
      duration: 0.42,
      ease: 'power3.in',
    },
    0,
  )
}
