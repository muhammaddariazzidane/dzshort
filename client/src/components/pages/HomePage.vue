<script setup lang="ts">
import axios from 'axios';
import { onMounted, ref } from 'vue'
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { SendHorizontal } from 'lucide-vue-next';
import { useToast } from '@/components/ui/toast/use-toast'

const { toast } = useToast()
const url = ref<string>('')
const shortUrl = ref<string>('')
const longUrl = ref<string>('')

async function shortenUrl(): Promise<any> {
  try {
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/create-short-url`, {
      url: url.value
    }, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

   if(response.status === 200) {
    longUrl.value = response.data.long_url;
    shortUrl.value = response.data.short_url

    localStorage.setItem('shortUrl', shortUrl.value)
    localStorage.setItem('longUrl', longUrl.value)

    toast({
      title: 'Success',
      description: 'URL shortened successfully',
      variant: 'default',
    })
    }
  } catch (error: any) {
    if (error.response.data.message) {
      toast({title: 'error',description: error.response.data.message,variant: 'destructive'})
    } else {
      toast({
        title: 'error',
        description: 'Something went wrong',
        variant: 'destructive'
      })
    }
  } finally {
    url.value = ""
  }
}

onMounted(() => {
  shortUrl.value = localStorage.getItem('shortUrl') || ''
  longUrl.value = localStorage.getItem('longUrl') || ''
})

</script>

<template>
  <main class="max-w-xl mx-auto p-4">
    <h1 class="text-2xl font-bold text-center py-10">DZShort - URL Shortener</h1>
    <div>
      <form class="flex flex-col gap-4 items-center" @submit.prevent="shortenUrl">
        <div class="border w-full p-4 shadow rounded-md">
          <div class="relative w-full max-w-md items-center ">
            <Input type="text" v-model="url" placeholder="Enter URL" class="pe-10" />
            <span class="absolute end-0 inset-y-0 flex items-center justify-center pl-2">
              <Button size="icon" variant="default" type="submit">
                <SendHorizontal class="size-6 " />
              </Button>
            </span>
          </div>
        </div>
      </form>
      <div class="py-4 px-1.5" v-if="shortUrl">
        Shortened URL: <a :href="longUrl" class="hover:underline text-primary" target="_blank">{{ shortUrl }}</a>
      </div>
    </div>
  </main>
</template>