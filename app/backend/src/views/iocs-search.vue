<template>
    <div class="backend-content" id="content">
        <div class="column col-12 col-xs-12">
          <h3 class="s-title">Search IOCs</h3>
          <div class="form-group">
            <textarea class="form-input" id="input-example-3" placeholder="Paste your IOCs here" rows="3" v-model="iocs"></textarea>
          </div>
          <div class="form-group">
            <button class="btn btn-primary col-12" v-on:click="search_iocs()">Search</button>
          </div>
          <div class="form-group" v-if="results.length>0 ">
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Indicator</th>
                            <th>Tag</th>
                            <th>TLP</th>
                            <th>Source</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="r in results" :key="r.tlp">
                            <td>{{ r.value }}</td>
                            <td class="upper">{{ r.tag }}</td>
                            <td><label :class="['tlp-' + r.tlp]">{{ r.tlp }}</label></td>
                            <td class="capi">{{ r.source }}</td>
                            <td><button class="btn btn-sm" v-on:click="remove(r)">Delete</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-else-if="first_search==false">
                <div v-if="loading">
                    <div class="empty">
                        <p class="empty-title h5">
                            <span class="loading loading-lg"></span>
                        </p>
                        <p class="empty-subtitle">Finding your IOC(s)...</p>
                    </div>
                </div>
                <div v-else>
                    <div class="empty">
                        <p class="empty-title h5">IOC<span v-if="this.iocs.match(/[^\r\n]+/g).length>1">s</span> not found.</p>
                        <p class="empty-subtitle">Try wildcard search to expend your search.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'iocs-search',   
    data() {
        return { 
            results: [],
            first_search: true,
            jwt:"",
            loading:false
        }
    },
    props: { },
    methods: {
        search_iocs: function() {
            this.results = []
            this.first_search = false
            this.loading = true;
            this.iocs.match(/[^\r\n]+/g).forEach(ioc => {
                ioc = ioc.trim()
                if("alert " != ioc.slice(0,6)) {
                    ioc = ioc.replace(" ", "")
                    ioc = ioc.replace("[", "")
                    ioc = ioc.replace("]", "")
                    ioc = ioc.replace("\\", "")
                    ioc = ioc.replace("(", "")
                    ioc = ioc.replace(")", "")
                }
                axios.get(`/api/ioc/search/${ioc}`, { timeout: 10000, headers: {'X-Token': this.jwt} })
                .then(response => {
                    if(response.data.results.length>0){
                        this.results = [].concat(this.results, response.data.results);
                    }
                    this.loading = false;
                })
                .catch(err => (console.log(err)))
            });
            return true;
        },
        remove: function(elem){
            axios.get(`/api/ioc/delete/${elem.id}`, { timeout: 10000, headers: {'X-Token': this.jwt} })
            .then(response => {
                if(response.data.status){
                    this.results = this.results.filter(function(el) { return el != elem; }); 
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
                    }
                })
                .catch(err => (console.log(err)))
        },
        async get_jwt(){
            await axios.get(`/api/get-token`, { timeout: 10000 })
                .then(response => {
                    if(response.data.token){
                        this.jwt = response.data.token
                    }
                })
            .catch(err => (console.log(err)))
        }
    },
    created: function() {
        this.get_jwt()
    }
}
</script>