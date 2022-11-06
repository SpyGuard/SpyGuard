<template>
    <div class="wrapper-dark">
        <div class="center">
            <h1 id="title">{{ title }}</h1>
            <span class="loading loading-lg loadingsplash"></span><span class="message_splash">{{message}}</span>
        </div>
    </div>
</template>

<script>
    import router from '../router'
    import axios from 'axios'

    export default {
        name: 'splash-screen',
        components: {},
        data() {
            return {
                internet: false,
                message: "",
                title: "SPYGUARD",
                letters: ["SSS§ṠSSSSS","PPPþ⒫PPPP","YYYÿYYYÿYȲYY","GGḠGGGǤG¬G","UÚUUÜUɄUUU", "AAAAÄA¬AAA", "RЯRɌRRRɌʭR", "DD¬DDDDƋDD"]
            }
        },
        methods: {
            delete_captures: function() {
                this.message = "Doing some cleaning..."
                console.log("[splash-screen.vue] Deleting previous captures...");
                axios.get('/api/misc/delete-captures', { timeout: 30000 });
                
                setTimeout(function () { this.goto_home(); }.bind(this), 2000);
            }, 
            goto_home: function() {
                console.log("[splash-screen.vue] Going to home...");
                this.message = "Going to home..."
                router.replace({ name: 'home' });
            },
            generate_random: function(min = 0, max = 1000) {
                let difference = max - min;
                let rand = Math.random();
                rand = Math.floor( rand * difference);
                rand = rand + min;
                return rand;
            },
        },
        created: function() {
            window.access_point = ""
            console.log("[splash-screen.vue] Welcome to SPYGUARD");
            setInterval(function(){
                    let res = ""
                    this.letters.forEach(l => { res += l.charAt(this.generate_random(0, 9)) })
                    this.title = res;
                setTimeout(function(){
                    this.title = "SPYGUARD";
                }.bind(this), this.generate_random(30, 100));
            }.bind(this), this.generate_random(500, 4000));
            this.delete_captures();
        }
    }
</script>
