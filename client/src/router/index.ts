import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes :[
    {
        path:'/',
        name: 'Home',
        component: () => import('@/components/pages/HomePage.vue')
    },
    {
      path: '/:id',
      name: 'Redirect',
      component: () => import('@/components/pages/RedirectPage.vue')
    }
  ]
})

export default router