/** 侧栏菜单（BI 大屏由首页按钮进入，不在侧栏展示） */

export interface NavItem {
  path: string
  labelKey: string
  icon: 'app' | 'atom' | 'map' | 'bell' | 'user' | 'list' | 'caps' | 'chart'
}

export interface NavSection {
  titleKey: string
  items: NavItem[]
}

export const NAV_SECTION_DEFS: NavSection[] = [
  {
    titleKey: 'nav.overview',
    items: [{ path: '/', labelKey: 'nav.home', icon: 'app' }],
  },
  {
    titleKey: 'nav.dataAnalysis',
    items: [
      { path: '/bda1', labelKey: 'nav.bda1', icon: 'atom' },
      { path: '/bda2', labelKey: 'nav.bda2', icon: 'map' },
      { path: '/bda3', labelKey: 'nav.bda3', icon: 'bell' },
      { path: '/bda4', labelKey: 'nav.bda4', icon: 'user' },
      { path: '/bda5', labelKey: 'nav.bda5', icon: 'list' },
    ],
  },
  {
    titleKey: 'nav.mlPredict',
    items: [
      { path: '/predict/soc', labelKey: 'nav.predictSoc', icon: 'caps' },
      { path: '/predict/duration', labelKey: 'nav.predictDuration', icon: 'caps' },
      { path: '/predict/fee', labelKey: 'nav.predictFee', icon: 'caps' },
      { path: '/predict/platform', labelKey: 'nav.predictPlatform', icon: 'caps' },
    ],
  },
]

export const BI_ENTRY = {
  labelKey: 'nav.biEntry',
  path: '/mr-bi',
  external: false,
} as const

export const SECTION_TITLE_KEY = 'nav.sectionTitle'
