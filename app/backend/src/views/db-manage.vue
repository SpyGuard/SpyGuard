<template>
    <div class="backend-content" id="content">
        <div class="column col-8 col-xs-12">
          <h3 class="s-title">Manage database</h3>
          <ul class="tab tab-block">
            <li class="tab-item">
                <a href="#" v-on:click="switch_tab('import')" v-bind:class="{ active: tabs.import }">Import database</a>
            </li>
            <li class="tab-item">
                <a href="#" v-on:click="switch_tab('export')" v-bind:class="{ active: tabs.export }">Export database</a>
            </li>
          </ul>
          <div v-if="tabs.export">
            <iframe :src="export_url" class="frame-export"></iframe>
          </div>
          <div v-if="tabs.import">
                <label class="form-upload empty" for="upload">
                    <input type="file" class="upload-field" id="upload" @change="import_from_file">
                    <p class="empty-title h5">Drop or select a database to import.</p>
                    <p class="empty-subtitle">The database needs to be an export from a SpyGuard instance.</p>
                </label>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'db-manage',   
    data() {
        return { 
            tabs: { "import" : true, "export" : false },
            jwt:""
        }
    },
    props: { },
    methods: {
        switch_tab: function(tab) {
            Object.keys(this.tabs).forEach(key => {
                if( key == tab ){
                    this.tabs[key] = true
                } else {
                    this.tabs[key] = false
                }
            });
        },
        import_from_file: function(ev) {
            var formData = new FormData();
            formData.append("file", ev.target.files[0]);
            axios.post('/api/config/db/import', formData, {
                headers: {
                    "Content-Type" : "multipart/form-data",
                    "X-Token" : this.jwt
                }
            })
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
        this.get_jwt().then(() => {
           this.export_url = `/api/config/db/export?token=${this.jwt}`
        });
    }
}
</script>