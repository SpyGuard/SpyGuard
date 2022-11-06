<template>
    <div class="wrapper">
        <div class="center">
            <h3 class="lobster">{{ $t("home.welcome_msg") }}</h3>
            <p>{{ $t("home.help_msg") }}</p>
            <button class="btn btn-primary" v-on:click="next()">{{ $t("home.start_btn") }}</button>
        </div>
    </div>
</template>

<script>
import router from '../router'

export default {
    name: 'home',
    methods: {
        next: function() {
            router.push({ name: 'generate-ap' });
        }
    }
}
</script>
