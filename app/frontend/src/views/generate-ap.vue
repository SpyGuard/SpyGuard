<template>
    <div class="wrapper">
        <div class="center">
            <div v-if="(error == false)">
                <div v-if="ssid_name">
                    <div class="card apcard" v-on:click="generate_ap()">
                        <div class="columns">
                            <div class="column col-5">
                                <center><img :src="ssid_qr" id="qrcode"></center>
                            </div>
                            <div class="divider-vert white-bg" data-content="OR"></div>
                            <div class="column col-5"><br />
                                <span class="light-grey">{{ $t("generate-ap.network_name") }} </span><br />
                                <h4>{{ ssid_name }}</h4>
                                <span class="light-grey">{{ $t("generate-ap.network_password") }} </span><br />
                                <h4>{{ ssid_password }}</h4>
                            </div>
                        </div>
                    </div>
                    <br /><br /><br /><br /> <br /><br /><br /><br /><br /><br />
                    <!-- Requite a CSS MEME for that shit :) -->
                    <span class="legend">{{ $t("generate-ap.tap_msg") }}</span>
                </div>
                <div v-else>
                    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin: auto; background: none; display: block; shape-rendering: auto;" width="194px" height="194px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
                        <circle cx="50" cy="50" r="0" fill="none" stroke="#dfdfdf" stroke-width="1">
                        <animate attributeName="r" repeatCount="indefinite" dur="2.941176470588235s" values="0;43" keyTimes="0;1" keySplines="0 0.2 0.8 1" calcMode="spline" begin="0s"></animate>
                        <animate attributeName="opacity" repeatCount="indefinite" dur="2.941176470588235s" values="1;0" keyTimes="0;1" keySplines="0.2 0 0.8 1" calcMode="spline" begin="0s"></animate>
                        </circle><circle cx="50" cy="50" r="0" fill="none" stroke="#dadada" stroke-width="1">
                        <animate attributeName="r" repeatCount="indefinite" dur="2.941176470588235s" values="0;43" keyTimes="0;1" keySplines="0 0.2 0.8 1" calcMode="spline" begin="-1.4705882352941175s"></animate>
                        <animate attributeName="opacity" repeatCount="indefinite" dur="2.941176470588235s" values="1;0" keyTimes="0;1" keySplines="0.2 0 0.8 1" calcMode="spline" begin="-1.4705882352941175s"></animate>
                        </circle>
                    </svg>
                    <p class="legend">{{ $t("generate-ap.generate_ap_msg") }}</p>
                </div>
            </div>
            <div v-else>
                <p>
                    <strong v-html="$t('generate-ap.error_msg1')"></strong>
                    <br /><br />
                    <span v-html="$t('generate-ap.error_msg2')"></span>
                    <br /><br /> 
                </p>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import router from '../router'

export default {
    name: 'generate-ap',
    components: {},
    data() {
        return {
            ssid_name: false,
            ssid_qr: false,
            ssid_password: false,
            capture_token: false,
            capture_start: false,
            interval: false,
            error: false,
            reboot_option: window.config.reboot_option,
            attempts: 3
        }
    },
    methods: {
        generate_ap: function() {
            console.log("[generate-ap.vue] Trying to start a new access point");
            clearInterval(this.interval);
            this.ssid_name = false
            axios.get('/api/network/ap/start', { timeout: 30000 })
                .then(response => (this.show_ap(response.data)))
        },
        show_ap: function(data) {
            if (data.status) {
                console.log("[generate-ap.vue] Access point created, showing SSID");
                window.access_point = data.ssid
                this.ssid_name = data.ssid
                this.ssid_password = data.password
                this.ssid_qr = data.qrcode
                this.start_capture()
            } else {
                console.log("[generate-ap.vue] Issue when creating AP, let's retry");
                if(this.attempts != 0){
                    setTimeout(function () { this.generate_ap() }.bind(this), 10000)
                    this.attempts -= 1;
                } else {
                    console.log("[generate-ap.vue] Fatal error when creating AP, showing the error message");
                    this.error = true
                }
            }
        },
        start_capture: function() {
            console.log("[generate-ap.vue] Starting the capture in background");
            axios.get('/api/capture/start', { timeout: 30000 })
                .then(response => (this.get_capture_token(response.data)))
        },
        reboot: function() {
            console.log("[generate-ap.vue] Rebooting the device");
            axios.get('/api/misc/reboot', { timeout: 30000 })
                .then(response => { console.log(response)})
        },
        get_capture_token: function(data) {
            if (data.status) {
                console.log("[generate-ap.vue] Capture token retrieved, waiting a device to connect");
                this.capture_token = data.capture_token
                this.capture_start = Date.now()
                this.get_device()
            }
        },
        get_device: function() {
            this.interval = setInterval(() => {
                axios.get(`/api/device/get/${this.capture_token}`, { timeout: 30000 })
                    .then(response => (this.check_device(response.data)))
            }, 500);
        },
        check_device: function(data) {
            if (data.status) {
                console.log("[generate-ap.vue] Device connected, going to capture view.");
                clearInterval(this.interval);
                var capture_token = this.capture_token
                var capture_start = this.capture_start
                var device_name = data.name
                router.replace({
                    name: 'capture',
                    params: {
                        capture_token: capture_token,
                        capture_start: capture_start,
                        device_name: device_name
                    }
                });
            }
        }
    },
    created: function() {
        console.log("[generate-ap.vue] Showing generate-ap.vue")
        this.generate_ap();
    }
}
</script>

