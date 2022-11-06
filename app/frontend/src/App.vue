<template>
  <div id="app">
    <Modals />
    <router-view />
    <Controls />
  </div>
</template>

<style>
  @import './assets/spectre.min.css';
  @import './assets/custom.css';
</style>

<script>
  import axios from 'axios'
  import Controls from "@/components/Controls.vue"
  import Modals from "@/components/Modals.vue"

  document.title = 'SPYGUARD'

  export default {
    name: 'app',
    components: {
        Controls,
        Modals
    }, data() {
            return {
                splash: false
            }
    },
    methods: {
        set_lang: function() {
            if (window.config.user_lang) {
                var lang = window.config.user_lang
                if (Object.keys(this.$i18n.messages).includes(lang)) {
                    this.$i18n.locale = lang
                    document.querySelector('html').setAttribute('lang', lang)
                }
            }
        },
        get_config: function() {
            axios.get('/api/misc/config', { timeout: 60000 })
            .then(response => { 
              window.config = response.data 
              this.set_lang();
            })
            .catch(error => { console.log(error) });
        }
    },
    watch: {
        $route (){
            if ( ["loader"].includes(this.$router.currentRoute.name)){
                this.splash = true;
            } else {
                this.splash = false;
            }
        }
    },
    created: function() {
        window.config = {}
        this.get_config();
    }
  }
</script>

