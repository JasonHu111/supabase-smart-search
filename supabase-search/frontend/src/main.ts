import { createApp } from 'vue'
import App from './App.vue'

// 检查环境变量
if (!import.meta.env.VITE_SUPABASE_URL) {
  console.warn('⚠️ VITE_SUPABASE_URL 未配置，请在 .env.local 中设置')
}
if (!import.meta.env.VITE_SUPABASE_ANON_KEY) {
  console.warn('⚠️ VITE_SUPABASE_ANON_KEY 未配置，请在 .env.local 中设置')
}

createApp(App).mount('#app')