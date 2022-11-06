<template>
    <div class="backend-content" id="content">
        <div class="column col-12 col-xs-12">
          <h3 class="s-title">Search whitelisted elements</h3>
          <div class="form-group">
            <textarea class="form-input" id="input-example-3" placeholder="Paste the elements here" rows="3" v-model="elements"></textarea>
          </div>
          <div class="form-group">
            <button class="btn btn-primary col-12"  v-on:click="search_elements()">Search</button>
          </div>
          <div class="form-group" v-if="results.length>0 ">
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Element</th>
                            <th>Element type</th>
                            <th> </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="r in results" :key="r.element">
                            <td>{{ r.element }}</td>
                            <td>{{ r.type }}</td>
                            <td><button class="btn btn-sm" v-on:click="remove(r)">Delete</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-else-if="first_search==false">
                <div class="empty">
                    <p class="empty-title h5">Element<span v-if="this.elements.match(/[^\r\n]+/g).length>1">s</span> not found.</p>
                    <p class="empty-subtitle">Try wildcard search to expend your search.</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'elements-search',   
    data() {
        return { 
            results: [],
            first_search: true,
            jwt:""
        }
    },
    props: { },
    methods: {
        search_elements: function() {
            this.results = []
            this.first_search = false
            this.elements.match(/[^\r\n]+/g).forEach(elem => {
                axios.get(`/api/whitelist/search/${elem.trim()}`, { 
                    timeout: 10000, 
                    headers: {'X-Token': this.jwt} 
                }).then(response => {
                    if(response.data.results.length>0){
                        this.results = [].concat(this.results, response.data.results);
                    }
                })
                .catch(err => (console.log(err)))
            });
            return true;
        },
        remove: function(elem){
            axios.get(`/api/whitelist/delete/${elem.id}`, { 
                timeout: 10000, 
                headers: {'X-Token': this.jwt} 
            }).then(response => {
                if(response.data.status){
                    this.results = this.results.filter(function(el) { return el != elem; }); 
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