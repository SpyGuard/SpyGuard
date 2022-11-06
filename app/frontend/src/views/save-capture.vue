<template>
    <div class="wrapper">
        <div class="center" v-if="save_usb && init">
            <div class="canvas-anim" :class="{'anim-connect': !saved && !usb}" v-on:click="new_capture()">
                <div class="icon-spinner" v-if="!saved && usb"></div>
                <div class="icon-success" v-if="saved"></div>
                <div class="icon-usb"></div>
                <div class="icon-usb-plug"></div> 
            </div>
            <p class="legend" v-if="!saved && !usb"><br />{{ $t("save-capture.please_connect") }}</p>
            <p class="legend" v-if="!saved && usb"><br />{{ $t("save-capture.we_are_saving") }}</p>
            <p class="legend" v-if="saved"><br />{{ $t("save-capture.tap_msg") }}</p>
        </div>
        <div class="center" v-else-if="!save_usb && init">
            <div>
                <p class="legend">{{ $t("save-capture.capture_download") }}<br /><br /><br /></p>
                <button class="btn btn-primary" v-on:click="new_capture()">{{ $t("save-capture.start_capture_btn") }}</button>
                <iframe :src="download_url" class="frame-download"></iframe>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
    
    .canvas-anim {
    height: 120px;
    margin: 0 auto;
    position: relative;
    width: 205px;
    
    &.anim-connect {
        width: 300px;

        .icon-usb {
            -webkit-animation: slide-right 1s cubic-bezier(0.455, 0.030, 0.515, 0.955) infinite alternate both;
            animation: slide-right 1s cubic-bezier(0.455, 0.030, 0.515, 0.955) infinite alternate both;
        }
    }
}
</style>

<script>
import axios from 'axios'
import router from '../router'

export default {
    name: 'save-capture',
    components: {},
    data() {
        return { 
            usb: false,
            saved: false,
            save_usb: false,
            init: false
        }
    },
    props: {
        capture_token: String
    },
    methods: {
        check_usb: function() {
            console.log("[save-capture.vue] Checking connected USB device...");
            axios.get(`/api/save/usb-check`, { timeout: 30000 })
                .then(response => {
                    if(response.data.status) {
                        this.usb = true
                        clearInterval(this.interval)
                        this.save_capture()
                    }
                })
        },
        save_capture: function() {
            var capture_token = this.capture_token
            console.log("[save-capture.vue] Saving the capture on USB");
            axios.get(`/api/save/save-capture/${capture_token}/usb`, { timeout: 30000 })
                .then(response => {
                    if(response.data.status){
                        this.saved = true
                        console.log("[save-capture.vue] Capture saved, going back to main view");
                        this.timeout = setTimeout(() => router.push('/'), 60000);
                    } 
                })
        },
        new_capture: function() {
            console.log("[save-capture.vue] Capture saved, generating a new access point");
            clearTimeout(this.timeout);
            router.push({ name: 'generate-ap' })
        }
    },
    created: function() {
        console.log("[save-capture.vue] Showing save-capture.vue");
        if(window.config.download_links){
            console.log("[save-capture.vue] Using download links instead of USB key");
            this.init = true
            this.save_usb = false
            this.download_url = `/api/save/save-capture/${this.capture_token}/url`
        } else {
            console.log("[save-capture.vue] Using USB key to save the capture");
            this.init = true
            this.save_usb = true
            this.interval = setInterval(() => { this.check_usb() }, 500);
        }
    }
}
</script>