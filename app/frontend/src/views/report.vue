<template>
    <div>
        <div v-if="results">
            <div v-if="grep_keyword('STALKERWARE', 'high')" class="high-wrapper">
                <div class="center">
                    <h1 class="warning-title" v-html="$t('report.stalkerware_msg')"></h1>
                    <button class="btn btn-report-low-light" v-on:click="new_capture()">{{ $t("report.start_new_capture") }}</button>
                    <button class="btn btn-report-high" @click="show_report=true;results=false;">{{ $t("report.show_full_report") }}</button>
                </div>
            </div>
            <div v-else-if="alerts.high.length >= 1" class="high-wrapper">
                <div class="center">
                    <h1 class="warning-title" v-html="$t('report.high_msg', { nb: $i18n.messages[$i18n.locale].report.numbers[alerts.high.length] })"></h1>
                    <button class="btn btn-report-low-light" v-on:click="new_capture()">{{ $t("report.start_new_capture") }}</button>
                    <button class="btn btn-report-high" @click="show_report=true;results=false;">{{ $t("report.show_full_report") }}</button>
                </div>
            </div>
            <div v-else-if="alerts.moderate.length >= 1" class="med-wrapper">
                <div class="center">
                    <h1 class="warning-title" v-html="$t('report.moderate_msg', { nb: $i18n.messages[$i18n.locale].report.numbers[alerts.moderate.length] })"></h1>
                    <button class="btn btn-report-low-light" v-on:click="new_capture()">{{ $t("report.start_new_capture") }}</button>
                    <button class="btn btn-report-moderate" @click="show_report=true;results=false;">{{ $t("report.show_full_report") }}</button>
                </div>
            </div>
            <div v-else-if="alerts.low.length >= 1" class="low-wrapper">
                <div class="center">
                    <h1 class="warning-title" v-html="$t('report.low_msg', { nb: $i18n.messages[$i18n.locale].report.numbers[alerts.low.length] })"></h1>
                    <button class="btn btn-report-low-light" v-on:click="new_capture()">{{ $t("report.start_new_capture") }}</button>
                    <button class="btn btn-report-low" @click="show_report=true;results=false;">{{ $t("report.show_full_report") }}</button>
                </div>
            </div>
            <div v-else class="none-wrapper">
                <div class="center">
                    <h1 class="warning-title" v-html="$t('report.fine_msg')"></h1>
                    <button class="btn btn-report-low-light"  @click="show_report=true;results=false;">{{ $t("report.show_full_report") }}</button>
                    <button class="btn btn-report-low" v-on:click="new_capture()">{{ $t("report.start_new_capture") }}</button>
                </div>
            </div>
        </div>
        <div v-else-if="show_report" class="wrapper">
            <div class="report-wrapper">
                <div class="device-ctx">
                    <h3 style="margin: 0; padding-left:10px;">{{ $t("report.report_of") }} {{device.name}}</h3>
                    <div class="device-ctx-legend">
                        {{ $t("report.pcap_sha1") }} {{ pcap.SHA1 }}<br />
                        {{ $t("report.capture_started") }} {{ pcap["First packet time"].split(",")[0] }}<br />
                        {{ $t("report.capture_ended") }} {{ pcap["Last packet time"].split(",")[0] }}<br />
                        {{ $t("report.detection_methods") }} {{ detection_methods }}
                    </div>
                </div>
                <div v-if="alerts">
                    <ul class="alerts">
                        <li class="alert" v-for="alert in alerts.high" :key="alert.message">
                            <div class="alert-header">
                                <span class="high-label">{{ $t("report.high") }}</span>
                                <span class="alert-id">{{ alert.id }}</span> 
                                <span class="btn-whitelist" v-on:click="add_whitelist(alert.host)">Add to the whitelist</span>
                            </div>
                            <div class="alert-body">
                                <span class="title">{{ alert.title }}</span>
                                <p class="description">{{ alert.description }}</p>
                            </div>
                        </li>
                        <li class="alert" v-for="alert in alerts.moderate" :key="alert.message">
                            <div class="alert-header">
                                <span class="moderate-label">{{ $t("report.moderate") }}</span>
                                <span class="alert-id">{{ alert.id }}</span> 
                                <span class="btn-whitelist" v-on:click="add_whitelist(alert.host)">Add to the whitelist</span>
                            </div>
                            <div class="alert-body">
                                <span class="title">{{ alert.title }}</span>
                                <p class="description">{{ alert.description }}</p>
                            </div>
                        </li>
                        <li class="alert" v-for="alert in alerts.low" :key="alert.message">
                            <div class="alert-header">
                                <span class="moderate-label">{{ $t("report.low") }}</span>
                                <span class="alert-id">{{ alert.id }}</span> 
                                <span class="btn-whitelist" v-on:click="add_whitelist(alert.host)">Add to the whitelist</span>
                            </div>
                            <div class="alert-body">
                                <span class="title">{{ alert.title }}</span>
                                <p class="description">{{ alert.description }}</p>
                            </div>
                        </li>
                    </ul>
                </div>
                <div class="no-alerts-to-show" v-else>
                    <span class="main-text">{{ $t("report.no_alerts_title") }}</span><br />
                    <span class="second-text">{{ $t("report.no_alerts_subtext") }}</span>
                </div>
                <h5 class="title-report" v-if="uncategorized_records.length>0">{{ $t("report.uncat_coms_table") }}</h5>
                <div v-if="uncategorized_records.length>0">
                    <table class="table-uncat">
                        <thead>
                            <tr>
                                <td>{{ $t("report.protocol") }}</td>
                                <td>{{ $t("report.domain_name") }}</td>
                                <td>{{ $t("report.ip_address") }}</td>
                                <td>{{ $t("report.port") }}</td>
                            </tr>
                        </thead>
                        <tr v-for="record in uncategorized_records" :key="record.ip_dst">
                            <td>{{ Object.keys(record.protocols).map(key => record.protocols[key].name).join(", ") }}</td>
                            <td v-on:click="add_whitelist(record.domains[0])">{{ record.domains.join(", ") }}</td>
                            <td v-on:click="add_whitelist(record.ip_dst)">{{ record.ip_dst }}</td>
                            <td>{{ Object.keys(record.protocols).map(key => record.protocols[key].port).join(", ") }}</td>
                        </tr>
                    </table>
                </div>
                <h5 class="title-report" v-if="whitelisted_records.length>0">{{ $t("report.whitelisted_coms_table") }}</h5>
                <div v-if="whitelisted_records.length>0">
                    <table class="table-uncat">
                        <thead>
                            <tr>
                                <td>{{ $t("report.protocol") }}</td>
                                <td>{{ $t("report.domain_name") }}</td>
                                <td>{{ $t("report.ip_address") }}</td>
                                <td>{{ $t("report.port") }}</td>
                            </tr>
                        </thead>
                        <tr v-for="record in whitelisted_records" :key="record.ip_dst">
                            <td>{{ Object.keys(record.protocols).map(key => record.protocols[key].name).join(", ") }}</td>
                            <td>{{ record.domains.join(", ") }}</td>
                            <td>{{ record.ip_dst }}</td>
                            <td>{{ Object.keys(record.protocols).map(key => record.protocols[key].port).join(", ") }}</td>
                        </tr>
                    </table>
                </div>
                <div id="controls-analysis">
                    <div class="column col-6">
                        <button class="btn btn btn-primary width-100" v-on:click="save_capture()">{{ $t("report.save") }}</button>
                    </div>
                    <div class="column col-6">
                        <button class="btn width-100" @click="$router.push('generate-ap')">{{ $t("report.start_new_capture") }}</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>


<style>
#app {
    overflow-y: visible;
}   
</style>

<script>
import router from '../router'
import axios from 'axios'
import { EventBus } from "../main.js"

export default {
    name: 'report',   
    data() {
        return {
            results: true,
            detection_methods: "",
            uncategorized_records: [],
            whitelisted_records: []
        }
    },
    props: {
        device: Object,
        methods: Object,
        pcap: Object,
        records: Array,
        alerts: Array,
        capture_token: String
    },
    methods: {
        save_capture: function() {
            console.log("[report.vue] Saving the capture");
            router.replace({ name: 'save-capture', params: { capture_token: this.capture_token } });
        },
        new_capture: function() {
            console.log("[report.vue] Deleting the capture and creating a new AP");
            axios.get('/api/misc/delete-captures', { timeout: 30000 })
            .then(() => { router.push({ name: 'generate-ap' }) })
            .catch(error => { console.log(error) })
        },
        grep_keyword: function(kw, level){
            try {
                if(this.alerts[level].length){
                    var idx;
                    var found;
                    this.alerts[level].forEach((a) => { 
                        idx = a.title.indexOf(kw)
                        if(!found) found = idx>0;
                    }); 
                    return found; 
                } else {
                    return false;
                }
            } catch (error){ console.log(error); }
        },
        get_detection_methods: function(){
            this.detection_methods += (this.methods.iocs == true)? `☑ ${this.$t("report.indicators")} ` : `☐ ${this.$t("report.indicators")} `
            this.detection_methods += (this.methods.heuristics == true)? `☑ ${this.$t("report.heuristics")} ` : `☐ ${this.$t("report.heuristics")} `
            this.detection_methods += (this.methods.active == true)? `☑ ${this.$t("report.active")} ` : `☐ ${this.$t("report.active")} `
        },
        add_whitelist: function(host){
            EventBus.$emit("showModal", {"action" : "whitelist", "host" : host})
        },
        get_records: function(){
            this.records.forEach( r => {
                if (!r.suspicious && !r.whitelisted){
                    this.uncategorized_records.push(r);
                } else if (r.whitelisted){
                    this.whitelisted_records.push(r);
                }
            })
        }
    },
    created: function() {
        console.log("[report.vue] Showing report.vue");
        this.get_detection_methods();
        this.get_records();
    }
}
</script>
