<template>
  <div class="backend-container off-canvas off-canvas-sidebar-show">
    <div class="backend-navbar">
      <a class="off-canvas-toggle btn btn-link btn-action" href="#sidebar">
        <i class="icon icon-menu"></i>
      </a>
    </div>
    <div class="backend-sidebar off-canvas-sidebar" id="sidebar">
      <div class="backend-brand">
          <h2 @click="goto_frontend()" class="title">{{ title }}</h2>
          <span class="version" v-if="current_version">{{current_version}}</span>
      </div>
      <div class="backend-nav">
        <div class="accordion-container">
          <div class="accordion">
            <input id="accordion-configuration" type="checkbox" name="backend-accordion-checkbox" hidden="">
            <label class="accordion-header c-hand" for="accordion-configuration">Manage Device</label>
            <div class="accordion-body">
              <ul class="menu menu-nav">
                <li class="menu-item">
                  <span @click="$router.push('/device/configuration')">Device config</span>
                </li>
                <li class="menu-item">
                  <span @click="$router.push('/engine/configuration')">Analysis engine</span>
                </li>
                <li class="menu-item">
                  <span @click="$router.push('/device/network')">Network config</span>
                </li>
                <li class="menu-item">
                  <span @click="$router.push('/device/db')">Manage database</span>
                </li>
              </ul>
            </div>
          </div>
          <div class="accordion">
            <input id="accordion-iocs" type="checkbox" name="backend-accordion-checkbox" hidden="">
            <label class="accordion-header c-hand" for="accordion-iocs">Manage IOCs</label>
            <div class="accordion-body">
              <ul class="menu menu-nav">
                <li class="menu-item">
                  <span @click="$router.push('/iocs/manage')">Manage IOCs</span>
                </li>
                <li class="menu-item">
                  <span @click="$router.push('/iocs/search')">Search IOCs</span>
                </li>
              </ul>
            </div>
          </div>
          <div class="accordion">
            <input id="accordion-whitelist" type="checkbox" name="backend-accordion-checkbox" hidden=""/>
            <label class="accordion-header c-hand" for="accordion-whitelist">Manage Whitelist</label>
            <div class="accordion-body">
              <ul class="menu menu-nav">
                <li class="menu-item">
                  <span @click="$router.push('/whitelist/manage')">Manage elements</span>
                </li>
                <li class="menu-item">
                  <span @click="$router.push('/whitelist/search')">Search elements</span>
                </li>
              </ul>
            </div>
          </div>
          <div class="accordion">
            <input id="accordion-instances" type="checkbox" name="backend-accordion-checkbox" hidden=""/>
            <label class="accordion-header c-hand" for="accordion-instances">External sources</label>
            <div class="accordion-body">
              <ul class="menu menu-nav">
                <li class="menu-item">
                  <span @click="$router.push('/instances/watchers')">Watchers Instances</span>
                </li>
                <li class="menu-item">
                  <span @click="$router.push('/instances/misp')">MISP Instances</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    <a class="off-canvas-overlay" href="#close"></a>
    <div class="off-canvas-content">
      <div id="update-banner" v-if="update_available" @click="$router.push('/update')">A new version is available, click on the banner to install it.</div>
      <transition name="fade" mode="out-in">
        <router-view/>
      </transition>
    </div>
  </div>
</template>

<style>
  @import './assets/spectre.min.css';
  @import './assets/spectre-exp.min.css';
  @import './assets/spectre-icons.min.css';
  @import './assets/custom.css';
  /* Face style for router stuff. */
  .fade-enter-active,
  .fade-leave-active {
    transition-duration: 0.3s;
    transition-property: opacity;
    transition-timing-function: ease;
  }

  .fade-enter,
  .fade-leave-active {
    opacity: 0
  }
</style>
<script>
  import axios from 'axios'
  document.title = 'SpyGuard Backend'

  export default {
      name: 'backend',
      components: {},
      data() {
          return {
              title: "SPYGUARD",
              current_version: false,
              jwt: "",
              update_available: false,
              letters: ["SSS§ṠSSSSS","PPPþ⒫PPPP","YYYÿYYYÿYȲYY","GGḠGGGǤG¬G","UÚUUÜUɄUUU", "AAAAÄA¬AAA", "RЯRɌRRRɌʭR", "DD¬DDDDƋDD"]
          }
      },
      methods: {
          generate_random: function(min = 0, max = 1000) {
              let difference = max - min;
              let rand = Math.random();
              rand = Math.floor( rand * difference);
              rand = rand + min;
              return rand;
          },
          goto_frontend: function() {
            window.location.href= `http://${location.hostname}:8000`
          },
          async get_jwt() {
              await axios.get(`/api/get-token`, { timeout: 10000 })
                  .then(response => {
                      if (response.data.token) {
                          this.jwt = response.data.token
                      }
                  })
                  .catch(err => (console.log(err)))
          },
          get_version: function() {
              axios.get('/api/update/get-version', { timeout: 60000, headers: { 'X-Token': this.jwt } })
              .then(response => { 
                  if(response.data.status) this.current_version = response.data.current_version
              })
              .catch(error => { console.log(error) });
          },
          check_update: function() {
              axios.get('/api/update/check', { timeout: 60000, headers: { 'X-Token': this.jwt } })
              .then(response => { 
                  if(response.data.message == "A new version is available"){
                      this.update_available = true;
                  }
              })
              .catch(error => { console.log(error) });
          }
      },
      created: function() {
          this.get_jwt().then(() => {
            this.get_version();
            this.check_update();
          });
          setInterval(function(){
                  let res = ""
                  this.letters.forEach(l => { res += l.charAt(this.generate_random(0, 9)) })
                  this.title = res;
              setTimeout(function(){
                  this.title = "SPYGUARD";
              }.bind(this), this.generate_random(30, 100));
          }.bind(this), this.generate_random(500, 10000));
      }
  }
</script>

