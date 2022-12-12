<template>
  <p>Authenticating...</p>
</template>

<script>
// import FHIR from "fhirclient"
import {launch} from "@/baseModel/launch_auth"
export default {
  name: 'SmartLaunch',
  async created() {
    await launch()
  }

}
</script>

<style scoped>

</style>