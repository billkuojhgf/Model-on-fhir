<template>
  <div>
    <Line :chart-data="chartData" :chart-options="chartOptions"/>
    <label>{{title + ": "}}</label>
    <input v-model="test">
  </div>
</template>

<script>
import {Line} from 'vue-chartjs'
import {Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, PointElement, LinearScale} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement)
export default {
  name: "LineChart",
  components: {Line},
  props: {
    title: String,
    chartLabel: Array,
    chartPoint: Array
  },
  data(){
    return {
      chartData: {
        labels: this.chartLabel,
        datasets: [
          {
            label: this.title,
            fill: false,
            tension: 0.1,
            borderColor: 'rgb(75, 192, 192)',
            data: this.chartPoint
          }
        ]
      },
      chartOptions: {
        onClick: (e) => {
          let clickedElement = e.chart.tooltip.dataPoints[0].raw
          this.test = clickedElement
        }
      },
      test: "hello",
    }
  },
  mounted() {
    // eslint-disable-next-line vue/no-mutating-props
    this.test = this.$props.chartPoint[this.chartPoint.length-1]
  },
  watch: {
      test(newValue) {
        this.$emit("valueChange", {
          "featureName": this.title,
          "featureValue": newValue
        })
      }
  },
}
</script>

<style scoped>

</style>