import Vue from 'vue'
import App from './App.vue'
import router from './router'
Vue.config.productionTip = true
Vue.config.devtools = true

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')