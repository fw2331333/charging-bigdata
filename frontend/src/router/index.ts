import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { public: true },
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('@/views/ForgotPasswordView.vue'),
      meta: { public: true },
    },
    {
      path: '/set-password',
      name: 'set-password',
      component: () => import('@/views/SetPasswordView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      children: [
        { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },

        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue'),
          meta: { requiresAuth: true, panelTitleKey: 'profile.title' },
        },

        {
          path: 'bda1',
          name: 'bda1',
          component: () => import('@/views/ChargingAnalysisView.vue'),
          meta: { keepAlive: true, requiresAuth: true },
        },
        {
          path: 'bda2',
          name: 'bda2',
          component: () => import('@/views/SocAnalysisView.vue'),
          meta: { keepAlive: true, requiresAuth: true },
        },
        {
          path: 'bda3',
          name: 'bda3',
          component: () => import('@/views/Bda3ChargingTimeView.vue'),
          meta: { keepAlive: true, requiresAuth: true },
        },
        {
          path: 'bda4',
          name: 'bda4',
          component: () => import('@/views/ChargeRateView.vue'),
          meta: { keepAlive: true, requiresAuth: true },
        },
        {
          path: 'bda5',
          name: 'bda5',
          component: () => import('@/views/MetricsReportView.vue'),
          meta: { keepAlive: true, requiresAuth: true },
        },

        {
          path: 'predict/soc',
          name: 'predict-soc',
          component: () => import('@/views/PredictSocPage.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'predict/duration',
          name: 'predict-duration',
          component: () => import('@/views/PredictDurationPage.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'predict/fee',
          name: 'predict-fee',
          component: () => import('@/views/PredictFeePage.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'predict/platform',
          name: 'predict-platform',
          component: () => import('@/views/PredictPlatformPage.vue'),
          meta: { requiresAuth: true },
        },

        {
          path: 'mr-bi',
          name: 'mr-bi',
          component: () => import('@/views/MrBiView.vue'),
          meta: { hidePanelHeader: true, keepAlive: true, requiresAuth: true },
        },
      ],
    },

    { path: '/charging', redirect: '/bda1' },
    { path: '/soc', redirect: '/bda2' },
    { path: '/soc-heatmap', redirect: '/bda2' },
    { path: '/charge-rate', redirect: '/bda4' },
    { path: '/predict', redirect: '/predict/soc' },

    { path: '/page4', redirect: '/predict/soc' },
    { path: '/page4ds1', redirect: '/predict/duration' },
    { path: '/page4ds2', redirect: '/predict/fee' },
    { path: '/page4ds3', redirect: '/predict/platform' },
  ],
})

let sessionRestored = false

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!sessionRestored) {
    await auth.restoreSession()
    sessionRestored = true
  }

  const publicNames = new Set(['login', 'register', 'forgot-password', 'set-password'])
  if (publicNames.has(String(to.name)) && auth.isLoggedIn) {
    return (to.query.redirect as string) || '/'
  }

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

export default router
