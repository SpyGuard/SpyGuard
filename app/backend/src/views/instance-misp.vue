<template>
    <div class="backend-content" id="content">
        <div class="column col-8 col-xs-12">
            <h3 class="s-title">Manage MISP instances</h3>
            <ul class="tab tab-block">
                <li class="tab-item">
                    <a href="#" v-on:click="switch_tab('addmisp')" v-bind:class="{ active: tabs.addmisp }">Add instance</a>
                </li>
                <li class="tab-item">
                    <a href="#" v-on:click="switch_tab('instances')" v-bind:class="{ active: tabs.instances }">Existing instances</a>
                </li>
            </ul>
            <div v-if="tabs.addmisp">
                <div class="misp-form">
                    <label class="misp-label">Instance name</label><span></span>
                    <input class="form-input" type="text" ref="misp_name" placeholder="CYBERACME MISP" v-model="mispinst.name" required>
                    <label class="misp-label">Instance URL</label><span></span>
                    <input class="form-input" type="text" ref="misp_url" placeholder="https://misp.cyberacme.com" v-model="mispinst.url" required>
                    <label class="misp-label">Authentication key</label><span></span>
                    <input class="form-input" type="text" ref="misp_key" placeholder="OqHSMyAuth3ntic4t10nK3y0MyAuth3ntic4t10nK3y3iiH" v-model="mispinst.key" required>
                    <label class="misp-label" v-if="mispinst.url.startsWith('https://')">Verify certificate? </label><span  v-if="mispinst.url.startsWith('https://')"></span>
                    <div style="flex:50%" v-if="mispinst.url.startsWith('https://')"><label class="form-switch">
                    <input type="checkbox" v-model="mispinst.ssl">
                    <i class="form-icon"></i>
                    </label></div>
                </div>
                <button class="btn-primary btn col-12" v-on:click="add_instance()">Add MISP instance</button>
                <div class="form-group" v-if="added">
                    <div class="toast toast-success">
                        ✓ MISP instance added successfully. Redirecting to instances in 2 seconds. 
                    </div>
                </div>
                <div class="form-group" v-if="error">
                    <div class="toast toast-error">
                        ✗ MISP instance not added. {{error}}
                    </div>
                </div>
            </div>
            <div class="form-group" v-if="tabs.instances">
                <div v-if="instances.length">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Server</th>
                                <th>Authkey</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="i in instances" v-bind:key="i.id">
                                <td>{{ i.name }}</td>
                                <td>{{ i.url.replace('https://', '') .replace('http://', '') }}</td>
                                <td>{{ i.apikey.slice(0,5) }} [...] {{ i.apikey.slice(35,40) }}</td>
                                <td>
                                    <span v-if="i.connected" class="instance-online tooltip" :data-tooltip="i.lastsync">✓ ONLINE</span>
                                    <span v-else class="instance-offline tooltip" :data-tooltip="i.lastsync">⚠ OFFLINE</span>
                                </td>
                                <td><button class="btn btn-sm" v-on:click="delete_instance(i)">Delete</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div v-else>
                    <div class="empty">
                        <div v-if="loading">
                            <p class="empty-title h5">
                                <span class="loading loading-lg"></span>
                            </p>
                            <p class="empty-subtitle">Testing and loading your MISP instances.</p>
                        </div>
                        <div v-else>
                            <p class="empty-title h5">No MISP instance found.</p>
                            <p class="empty-subtitle">Do not hesitate to add a MISP instance.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>

import axios from 'axios'

export default {
    name: 'managemisp',   
    data() {
        return { 
            error:false,
            loading:false,
            added:false,
            mispinst:{ name:'', url:'',key:'', ssl:false },
            instances:[],
            tabs: { "addmisp" : true, "instances" : false },
            jwt:""
        }
    },
    props: { },
    methods: {
        add_instance: function()
        {  
            this.added = false;
            this.error = false;
            if (this.mispinst.name && this.mispinst.url && this.mispinst.key)
            {
                axios.post(`/api/misp/add`, { data: { instance: this.mispinst } }, { headers: {'X-Token': this.jwt} }).then(response => {
                    if(response.data.status){
                        this.added = true;
                        setTimeout(function (){ 
                            this.switch_tab('instances')
                            this.mispinst = { name:'', url:'',key:'', ssl:false } 
                            this.added = false
                        }.bind(this), 2000);
                    } else {
                        this.error = response.data.message;
                    }
                })
                .catch(err => (console.log(err)))
            }
        },
        delete_instance(elem)
        {
            axios.get(`/api/misp/delete/${elem.id}`, { timeout: 10000, headers: {'X-Token': this.jwt} })
            .then(response => {
                if(response.data.status){
                    this.instances = this.instances.filter(function(el) { return el != elem; }); 
                }
            })
            .catch(err => (console.log(err)))
        },
        get_misp_instances()
        {
            this.loading = true;
            this.instances = []
            axios.get(`/api/misp/get_all`, { timeout: 10000, headers: {'X-Token': this.jwt} })
            .then(response => {
                if(response.data.results){
                    this.instances = response.data.results;
                    this.instances.forEach(e => { 
                        var lastsync = parseInt((Date.now()/1000 - e.lastsync) / 86400)
                        e.lastsync = (!lastsync)? "Synchronized today" : `Synchronized ${lastsync} day(s) ago`
                        } )
                }
                this.loading = false
            })
            .catch(err => (console.log(err)))
        },
        switch_tab: function(tab) {

            Object.keys(this.tabs).forEach(key => {
                if( key == tab ){
                    this.tabs[key] = true
                    if (key == "instances") this.get_misp_instances();
                } else {
                    this.tabs[key] = false
                }
            });
        },
        get_jwt(){
            axios.get(`/api/get-token`, { timeout: 10000 })
                .then(response => {
                    if(response.data.token){
                        this.jwt = response.data.token
                    }
                })
            .catch(err => (console.log(err)))
        }
    },
    created: function() {
        this.get_jwt();
    }
}
</script>
