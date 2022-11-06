<template>
    <div class="controls" v-if="display">
        <i class="battery" :class="[battery_icon]"></i>
        <div v-if="iface_out.startsWith('wl')" class="dropup">
            <i :class="[wifi_icon]" class="wifi"></i>
            <div class="dropup-content">
                <ul>
                    <li v-for="network in wifi_networks" v-on:click="show_modal_wifi(network.name)" v-bind:key="network">
                        <i :class="[get_wifi_icon(network.signal)]" class="wifi_mini"> </i>{{ network.name }}
                    </li>
                </ul>   
            </div>
        </div>
        
        <i class="iocs-number"  v-bind:class="{ 'border-green': iocs_number }">{{ iocs_number }} IOCs</i>
        <i v-if="ip_address" class="ip_addr" v-bind:class="{ 'border-green': internet }">{{ ip_address }} </i>
        <i v-else class="ip_addr">Not connected</i>
        <i class="home-icon" v-on:click="goto_home()"></i>
        <i class="config-icon" v-on:click="goto_backend()" v-if="backend_option"></i>
        <i class="shutdown-icon" v-on:click="show_modal_shutdown()" v-if="shutdown_option"></i>
    </div>
</template>

<script>
import axios from 'axios'
import { EventBus } from "../main.js"

export default {
    name: 'Controls',
    data: function (){
        return {
            display: true,
            update_available: false,
            update_possible: false,
            shutdown_option: false,
            backend_option: false,
            remote_backend: false,
            iface_out: "",
            battery_icon: "",
            wifi_icon: "",
            wifi_networks: [],
            iocs_number: 0,
            internet: false
            }
    },
    methods: {
        check_update: function() {
            axios.get('/api/update/check', { timeout: 60000 })
            .then(response => { 
              if(response.data.status) {
                if(response.data.message == "A new version is available"){

                  // Allow to show the warning chip.
                  this.update_available = true
                  this.update_possible = true

                  // Pass the versions as "global vars" through window variable.
                  window.current_version = response.data.current_version
                  window.next_version = response.data.next_version
                }
              } else {  
                  this.update_possible = false
              }
            })
            .catch(error => { console.log(error) });
        },
        goto_backend: function() {
            if(this.remote_backend){
                window.location.href= `https://${location.hostname}:8443`
            }
            else {
                window.location.href= `http://${location.hostname}:8443`
            }
        },
        goto_home: function() {
            window.location.href = "/"
        },
        load_config: function() {
            setInterval(() => {
                axios.get(`/api/misc/config`, { timeout: 60000 })
                    .then(response => {
                        this.shutdown_option = response.data.shutdown_option
                        this.backend_option = response.data.backend_option
                        this.remote_backend = response.data.remote_backend
                        this.battery_icon = this.get_battery_icon(response.data.battery_level)
                        this.wifi_icon = this.get_wifi_icon(response.data.wifi_level)
                        this.iocs_number = response.data.iocs_number
                        this.iface_out = response.data.iface_out
                    })
                    .catch(error => { console.log(error) });
            }, 1000);
        },
        get_battery_icon: function(level){
            if (level == 101){
                return "battery_charging"
            }  else if (level >= 90) {
                return "battery_full"
            } else if (level >= 80) {
                return "battery_80"
            } else if (level >= 60) {
                return "battery_60"
            } else if (level >= 40) {
                return "battery_40"
            } else if (level >= 25) {
                return "battery_25"
            } else if (level < 25) {
                return "battery_15"
            } else {
                return "battery_critical"
            }
        },
        get_wifi_icon: function(level){
            if (level >= 80) {
                return "wifi_5"
            } else if (level >= 60) {
                return "wifi_4"
            } else if (level >= 40) {
                return "wifi_3"
            } else if (level >= 20) {
                return "wifi_2"
            } else if (level >= 1) {
                return "wifi_1"
            } else {
                return "wifi_0"
            }
        }, 
        show_modal_shutdown: function(){
            EventBus.$emit("showModal", {"action" : "shutdown"})
        },
        show_modal_wifi: function(network_name){
            EventBus.$emit("showModal", {"action" : "wifi", "network_name" : network_name})
        },
        get_wifi_networks: function(){
            setInterval(() => {
                axios.get('/api/network/wifi/list', { timeout: 10000 })
                .then(response => { 
                    this.wifi_networks = []
                    response.data.networks.forEach( network => {
                        if(network.name != window.access_point){
                            this.wifi_networks.push(network);
                        }
                    })
                }).catch(error => {
                    console.log(error)
                });
            }, 1000);
        },
        check_internet: function() {
            setInterval(() => {
                axios.get('/api/network/status', { timeout: 30000 })
                .then(response => {
                    if (response.data.internet){
                        this.internet = true
                        this.ip_address = response.data.ip_out
                    } else {
                        this.internet = false
                        this.ip_address = false
                    }
                })
                .catch(err => (console.log(err)))
            }, 1000);
        },
    },
    watch: {
        $route (){
            if ( ["loader"].includes(this.$router.currentRoute.name)){
                this.display = false;
            } else {
                this.display = true;
            }
        }
    },
    created: function() {
        this.load_config();
        this.check_internet();
        this.get_wifi_networks();
    }
}
</script>