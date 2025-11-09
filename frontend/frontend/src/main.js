import './assets/main.css'
import './assets/design-system.css'  // 全局设计系统

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Element Plus will be lazy loaded via unplugin-vue-components

app.mount('#app')
