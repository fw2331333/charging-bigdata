import type { ScrollTrigger } from 'gsap/ScrollTrigger'
import { ScrollTrigger as ST } from '@/lib/gsap'

/** 异步图表加载后刷新 ScrollTrigger 布局（ECharts 改变高度时调用） */
export function refreshScrollTriggers(): void {
  ST.refresh()
}

export type { ScrollTrigger }
