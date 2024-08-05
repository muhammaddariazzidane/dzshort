<script setup lang="ts">
import axios from 'axios';
import { useRoute } from 'vue-router';
import { onMounted } from 'vue';

const route = useRoute();
const { id } = route.params;

onMounted(async () => {
    try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/${id}`);
        if (response.status === 200) window.location.href =  response.data.long_url;
    } catch (error) {
        console.error('Failed to fetch URL:', error);
    }
});

</script>

<template>
    <main class="min-h-screen flex items-center justify-center text-primary text-xl">Redirecting...</main>
</template> 
