<template>
  <!-- v-on:valueChange is a label from LineChart $emit   -->
  <h1>{{ title }}</h1>
  <LineChart
      v-for="x in dataData.length"
      :key="x"
      :chart-label="dataLabel[x-1]"
      :chart-point="dataData[x-1]"
      :title="dataTitle[x-1]"
      @takeChange="changedTake_Obj"
  ></LineChart>
</template>

<script>
import LineChart from "@/components/LineChart";

export default {
  name: "ModelChart",
  components: {
    LineChart
  },
  props: {
    title: String,
    chartUsed: String
  },
  data() {
    return {
      dataTitle: [],
      dataData: [],
      dataLabel: [],
      indexOfModelFeatureArray: 0,
    }
  },
  methods: {
    changedTake_Obj(valueObj) {
      /**
       * valueObj.key: featureName: this.title, featureValue: {changedValue}
       */
      valueObj.index = this.indexOfModelFeatureArray
      this.$store.dispatch('featureTakeChanged', valueObj)

    }
  },
  created() {
    let featureObj = undefined
    let count = 0
    for (const arr of this.$store.state.modelFeatureArray) {
      if (arr.name === this.title) {
        featureObj = arr.resources
        this.indexOfModelFeatureArray = count
        break
      }
      count++;
    }

    if (featureObj === undefined)
      return

    Object.entries(featureObj).forEach(([key, valueObj]) => {
      this.dataTitle.push(key)
      this.dataLabel.push(valueObj.date)
      this.dataData.push(valueObj.value)
    })
  },
  computed: {
    getModelObject() {
      // 取得Model 的feature Object
      return this.$store.state.modelFeatureArray[this.indexOfModelFeatureArray]
    },
    getChangeStatus() {
      return this.$store.state.dateChanged
    }
  },
}
</script>

<style scoped>
p {
  font-size: 20px;
}

</style>