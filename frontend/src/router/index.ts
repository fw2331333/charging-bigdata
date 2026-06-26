import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/mr-bi', name: 'mr-bi', component: () => import('@/views/MrBiView.vue') },
    { path: '/soc', name: 'soc', component: () => import('@/views/SocAnalysisView.vue') },
    { path: '/soc-heatmap', name: 'soc-heatmap', component: () => import('@/views/SocHeatmapView.vue') },
    { path: '/charging', name: 'charging', component: () => import('@/views/ChargingAnalysisView.vue') },
    { path: '/charge-rate', name: 'charge-rate', component: () => import('@/views/ChargeRateView.vue') },
    { path: '/predict', name: 'predict', component: () => import('@/views/PredictView.vue') },
  ],
})

export default router
