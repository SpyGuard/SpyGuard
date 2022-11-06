<template>
    <div class="backend-content" id="content">
        <div v-bind:class="{ 'alert-toaster-visible' : toaster.show, 'alert-toaster-hidden' : !toaster.show }">{{toaster.message}}</div>
        <div class="column col-8 col-xs-12">
            <h3 class="s-title">Detection engine configuration</h3>
            <h5 class="s-subtitle">Detection methods</h5>
            <div class="form-group">
                <label class="form-switch">
                    <input type="checkbox" @change="local_analysis('analysis', 'heuristics')" v-model="config.analysis.heuristics">
                    <i class="form-icon"></i> Use heuristic detection for suspect behaviour.
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="local_analysis('analysis', 'iocs')" v-model="config.analysis.iocs">
                    <i class="form-icon"></i> Use Indicator of Compromise (IoC) based detection.
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="local_analysis('analysis', 'whitelist')" v-model="config.analysis.whitelist">
                    <i class="form-icon"></i> Use whitelist to prevent false positives.
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="local_analysis('analysis', 'active')" v-model="config.analysis.active">
                    <i class="form-icon"></i> Use active analysis (Dig, Whois, OpenSSL...).
                </label>
                <label class="form-switch">
                    <input type="checkbox" @change="switch_iocs_types('all')" :checked="config.analysis.indicators_types.includes('all')">
                    <i class="form-icon"></i> Detect threats by using all IOCs.
                </label>
            </div>
            <div class="form-group" v-if="!config.analysis.indicators_types.includes('all')">
                <h5 class="s-subtitle">IOCs categories</h5>
                <label class="form-switch" v-for="tag in iocs_tags" :key="tag">
                    <input type="checkbox" @change="switch_iocs_types(tag)"  :checked="config.analysis.indicators_types.includes(tag)">
                    <i class="form-icon"></i> Use IOCs related to {{ tag.toUpperCase() }} threat.
                </label>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'analysis-engine',
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
        local_analysis: function(cat, key) {
            this.switch_config(cat, key);
            if (this.config.analysis.remote != false)
                this.switch_config("analysis", "remote");
        },
        load_config: function() {
            axios.get(`/api/config/list`, {
                    timeout: 10000,
                    headers: { 'X-Token': this.jwt }
                }).then(response => {
                    if (response.data) {
                        this.config = response.data
                        this.config.backend.password = ""
                        console.log(this.config.analysis.indicators_types);
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
        get_iocs_tags: function() {
            axios.get(`/api/ioc/get/tags`, { 
                timeout: 10000, 
                headers: {'X-Token': this.jwt} 
            })
            .then(response => {
                if(response.data.tags) this.iocs_tags = response.data.tags
            })
            .catch(err => (console.log(err)));
        },
        switch_iocs_types: function(tag) {
            if (this.config.analysis.indicators_types.includes(tag)){
                axios.get(`/api/config/ioc-type/delete/${tag}`, {
                        timeout: 10000,
                        headers: { 'X-Token': this.jwt }
                }).then(response => {
                    if (response.data.status) { this.load_config(); }
                })
                .catch(err => (console.log(err)))
            } else {
                axios.get(`/api/config/ioc-type/add/${tag}`, {
                        timeout: 10000,
                        headers: { 'X-Token': this.jwt }
                }).then(response => {
                    if (response.data.status) { this.load_config(); }
                })
                .catch(err => (console.log(err)))
                this.load_config();
            }
        }
    },
    created: function() {
        this.get_jwt().then(() => {
            this.load_config();
            this.get_iocs_tags();
        });
    }
}
</script>