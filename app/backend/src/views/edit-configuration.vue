<template>
    <div class="backend-content" id="content">
        <div v-bind:class="{ 'alert-toaster-visible' : toaster.show, 'alert-toaster-hidden' : !toaster.show }">{{toaster.message}}</div>
        <div class="column col-8 col-xs-12">
            <h3 class="s-title">Configuration </h3>
            <div class="form-group">
                <label class="form-label" for="user-login">Device UUID (read-only)</label>
                <div class="input-group">
                    <input class="form-input read-only" id="device-id" v-model="config.device_uuid" readonly="readonly">
                </div>
            </div>
            <h5 class="s-subtitle">Device configuration</h5>
            <div class="form-group">
                <label class="form-switch">
                    <input type="checkbox" @change="switch_config('frontend', 'virtual_keyboard')" v-model="config.frontend.virtual_keyboard">
                    <i class="form-icon"></i> Use virtual keyboard (for touch screen)
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="switch_config('frontend', 'shutdown_option')" v-model="config.frontend.shutdown_option">
                    <i class="form-icon"></i> Allow the end-user to shutdown the device.
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="switch_config('frontend', 'backend_option')" v-model="config.frontend.backend_option">
                    <i class="form-icon"></i> Allow the end-user to access to the backend.
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="switch_config('network', 'tokenized_ssids')" v-model="config.network.tokenized_ssids">
                    <i class="form-icon"></i> Use tokenized SSIDs (eg. [ssid-name]-[hex-str]).
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="switch_config('frontend', 'download_links')" v-model="config.frontend.download_links">
                    <i class="form-icon"></i> Use in-browser download for network captures.
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="switch_config('frontend', 'sparklines')" v-model="config.frontend.sparklines">
                    <i class="form-icon"></i> Show background sparklines during the capture.
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="switch_config('frontend', 'remote_access')" v-model="config.frontend.remote_access">
                    <i class="form-icon"></i> Allow remote access to the frontend.
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="switch_config('backend', 'remote_access')" v-model="config.backend.remote_access">
                    <i class="form-icon"></i> Allow remote access to the backend.
                </label>
            </div>
            <h5 class="s-subtitle">User credentials</h5>
            <div class="form-group">
                <div class="column col-10 col-xs-12">
                    <div class="form-group">
                        <label class="form-label" for="user-login">User login</label>
                        <div class="input-group">
                            <input class="form-input" id="user-login" type="text" v-model="config.backend.login">
                            <button class="btn btn-primary input-group-btn px150" @click="change_login()">Update it</button>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="user-login">User password</label>
                        <div class="input-group">
                            <input class="form-input" id="user-login" type="password" placeholder="●●●●●●" v-model="config.backend.password">
                            <button class="btn btn-primary input-group-btn px150" @click="change_password()">Update it</button>
                        </div>
                    </div>
                    <div class="whitespace"></div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'edit-configuration',
    data() {
        return {
            config: {},
            check_certificate: false,
            certificate: "",
            iocs_tags: [],
            toaster: { show: false, message : "", type : null }
        }
    },
    props: {},
    methods: {
        switch_config: function(cat, key) {
            axios.get(`/api/config/switch/${cat}/${key}`, {
                    timeout: 10000,
                    headers: { 'X-Token': this.jwt }
                }).then(response => {
                    if (response.data.status) {
                        if (response.data.message == "Key switched to true") {
                            this.toaster = { show : true, message : "Configuration updated", type : "success" }
                            setTimeout(function () { this.toaster = { show : false } }.bind(this), 1000)
                            this.config[cat][key] = true
                        } else if (response.data.message == "Key switched to false") {
                            this.toaster = { show : true, message : "Configuration updated", type : "success" }
                            setTimeout(function () { this.toaster = { show : false } }.bind(this), 1000)
                            this.config[cat][key] = false
                        } else {
                            this.toaster = { show : true, message : "The key doesn't exist", type : "error" }
                            setTimeout(function () { this.toaster = { show : false } }.bind(this), 1000)
                        }
                    }
                })
                .catch(err => (console.log(err)))
        },
        load_config: function() {
            axios.get(`/api/config/list`, {
                    timeout: 10000,
                    headers: { 'X-Token': this.jwt }
                }).then(response => {
                    if (response.data) {
                        this.config = response.data
                        this.config.backend.password = ""
                    }
                })
                .catch(err => (console.log(err)))
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
        change_login: function() {
            axios.get(`/api/config/edit/backend/login/${this.config.backend.login}`, {
                    timeout: 10000,
                    headers: { 'X-Token': this.jwt }
            }).then(response => {
                if (response.data.status) {
                    this.toaster = { show : true, message : "Login changed", type : "success" }
                    setTimeout(function () { this.toaster = { show : false } }.bind(this), 1000)
                } else {
                    this.toaster = { show : true, message : "Login not changed", type : "error" }
                    setTimeout(function () { this.toaster = { show : false } }.bind(this), 1000)
                }
            })
            .catch(err => (console.log(err)))
        },
        change_password: function() {
            axios.get(`/api/config/edit/backend/password/${this.config.backend.password}`, {
                    timeout: 10000,
                    headers: { 'X-Token': this.jwt }
                }).then(response => {
                    if (response.data.status) {
                        this.toaster = { show : true, message : "Password changed", type : "success" }
                        setTimeout(function () { this.toaster = { show : false } }.bind(this), 1000)
                    } else {
                        this.toaster = { show : true, message : "Password not changed", type : "error" }
                        setTimeout(function () { this.toaster = { show : false } }.bind(this), 1000)
                    }
                })
                .catch(err => (console.log(err)))
        }
    },
    created: function() {
        this.get_jwt().then(() => {
            this.load_config();
        });
    }
}
</script>
