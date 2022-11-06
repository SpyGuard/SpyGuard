<template>
    <div class="wrapper">
        <svg id="sparkline" stroke-width="3" :width="sparkwidth" :height="sparkheight" v-if="sparklines"></svg>
        <div class="center">
            <div class="footer">
                <h3 class="timer">{{timer_hours}}:{{timer_minutes}}:{{timer_seconds}}</h3>
                <p>{{$t("capture.intercept_coms_msg")}} {{device_name}}.</p>
                <div class="empty-action">
                    <button class="btn btn-primary" v-on:click="stop_capture()">{{$t("capture.stop_btn")}}</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import router from '../router'
import sparkline from '@fnando/sparkline'

export default {
    name: 'capture',
    components: {},
    data() {
        return {
            timer_hours: "00",
            timer_minutes: "00",
            timer_seconds: "00",
            stats_interval: false,
            chrono_interval: false,
            sparklines: false
        }
    },
    props: {
        capture_token: String,
        device_name: String
    },
    methods: {
        set_chrono: function() {
            console.log("[capture.vue] Setting up the chrono")
            this.chrono_interval = setInterval(() => { this.chrono(); }, 10);
        },
        stop_capture: function() {
            console.log("[capture.vue] Stoping the capture")
            axios.get('/api/capture/stop', { timeout: 30000 })
            clearInterval(this.chrono_interval);
            clearInterval(this.stats_interval);
            window.access_point = ""
            var capture_token = this.capture_token
            router.replace({ name: 'analysis', params: { capture_token: capture_token } });
        },
        get_stats: function() {
            console.log("[capture.vue] Getting capture statistics")
            axios.get('/api/capture/stats', { timeout: 30000 })
                .then(response => (this.handle_stats(response.data)))
        },
        handle_stats: function(data) {
            if (data.packets.length) sparkline(document.querySelector('#sparkline'), data.packets);
        },
        chrono: function() {
            var time = Date.now() - this.capture_start
            this.timer_hours = Math.floor(time / (60 * 60 * 1000));
            this.timer_hours = (this.timer_hours < 10) ? '0' + this.timer_hours : this.timer_hours
            time = time % (60 * 60 * 1000);
            this.timer_minutes = Math.floor(time / (60 * 1000));
            this.timer_minutes = (this.timer_minutes < 10) ? '0' + this.timer_minutes : this.timer_minutes
            time = time % (60 * 1000);
            this.timer_seconds = Math.floor(time / 1000);
            this.timer_seconds = (this.timer_seconds < 10) ? '0' + this.timer_seconds : this.timer_seconds
        },
        setup_sparklines: function() {
            axios.get('/api/misc/config', { timeout: 60000 })
                .then(response => {
                    if(response.data.sparklines){
                        console.log("[capture.vue] Setting up sparklines")
                        this.sparklines = true
                        this.sparkwidth = window.screen.width + 'px';
                        this.sparkheight = Math.trunc(window.screen.height / 5) + 'px';
                        this.stats_interval = setInterval(() => { this.get_stats(); }, 500);
                    }
                })
                .catch(error => {
                    console.log(error)
                });
        }
    },
    created: function() {
        console.log("[capture.vue] Showing capture.vue")

        // Get the config for the sparklines.
        this.setup_sparklines()

        // Start the chrono and get the first stats.
        this.capture_start = Date.now()
        this.set_chrono();
    }
}
</script>
