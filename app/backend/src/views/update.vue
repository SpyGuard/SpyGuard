<template>
    <div class="backend-content" id="content">
        <div class="column col-8 col-xs-12">
            <br />
            <p><strong>A new SpyGuard version is available ({{next_version}}).</strong><br />
                <span v-if="!update_launched">Please click on the button below to update your instance.</span>
                <span v-if="update_launched&&!update_finished">Updating SpyGuard, please wait. You'll be redirected once updated.</span>     
                <span v-if="update_launched&&update_finished" class="color-green">✓ Update finished!</span>
            </p>
            <button class="btn btn-primary" :class="[ update_launched ? 'loading' : '' ]" v-on:click="launch_update()" v-if="!update_finished">Update Spyguard</button>
        </div>
    </div>
</template>

<script>
    import axios from 'axios'

    export default {
        name: 'update',
        data() {
            return {
                translation: {},
                update_launched: null,
                check_interval: null,
                next_version: null,
                current_version: null,
                update_finished: false,
                jwt: "",
            }
        },
        methods: {
            check_version: function() {
                axios.get('/api/update/get-version', { timeout: 60000, headers: { 'X-Token': this.jwt } })
                .then(response => { 
                    if(response.data.status) {
                        if(response.data.current_version == this.next_version){
                            window.current_version = response.data.current_version
                            this.update_finished = true
                            clearInterval(this.check_interval);
                            setTimeout(function () { window.location.href = "/"; }, 3000) 
                        }
                    }
                })
                .catch(error => { console.log(error) });
            },
            launch_update: function() {
                axios.get(`/api/update/process`, { timeout: 60000, headers: { 'X-Token': this.jwt } })
                .then(response => {
                    if(response.data.status) {
                        if(response.data.message == "Update successfully launched"){
                            this.update_launched = true
                            this.check_interval = setInterval(function(){ this.check_version(); }.bind(this), 3000);
                        }
                    }
                })
                .catch(error => { console.log(error) });
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
            get_versions: function() {
                axios.get('/api/update/check', { timeout: 60000, headers: { 'X-Token': this.jwt } })
                .then(response => { 
                    if(response.data.status){
                        this.current_version = response.data.current_version
                        this.next_version = response.data.next_version
                        if(this.current_version == this.next_version) window.location.href = "/";
                    }
                })
                .catch(error => { console.log(error) });
            },
        },
        created: function() {
            this.get_jwt().then(() => {
                this.get_versions();
            });
        }
    }
</script>
