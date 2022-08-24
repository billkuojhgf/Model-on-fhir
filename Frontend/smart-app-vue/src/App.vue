<template>
  <img alt="Vue logo" src="./assets/logo.png">
<!--  <HelloWorld msg="Welcome to Your Vue.js App"/>-->
  <div id="divChart">
    <LineChart
        v-for="x in dataData.length"
        v-on:valueChange="changedValue"
        :key="x"
        :title="dataTitle[x-1]"
        :chart-label= "dataLabel[x-1]"
        :chart-point= "dataData[x-1]"
    ></LineChart>
  </div>
</template>

<script>
// import HelloWorld from './components/HelloWorld.vue'
import LineChart from "./components/LineChartView";
import axios from "axios";

export default {
  name: 'App',
  components: {
    LineChart
  },
  data() {
    return {
      dataTitle: [],
      dataData: [],
      dataLabel: [],
      testing: this.LineChart
    }
  },
  methods : {
    // data is on ObjectType send by LineChartView.$emit
    changedValue(data){
      console.log("test " + data["featureName"] + " " + data["featureValue"])
    }
  },
  watch: {

  },
  created () {
    // axios({
    //   method: 'get',
    //   baseURL: 'http://127.0.0.1:5000',
    //   url: '/diabetes',
    //   params:{'id': "test-03121002"},
    //   "Content-Type": 'application/json'
    // }).then((response) => {
    //   const result = response.data
    //   delete result['predict_value']
    //   for(let key in result){
    //     this.$data.dataTitle.push(key)
    //     this.$data.dataData.push([result[key]["value"]])
    //     this.$data.dataLabel.push([result[key]["date"]])
    //   }
    // }).catch((error) => {
    //   console.error(error)
    // })
    // TODO: 這裡之後要改成可以接收FeatureTable的欄位並進行取值，effectiveDateTime與effectivePeriod.start之間的取值要先搞定
    let array = ['8302-2', '29463-7']
    let array2 = ['height', 'weight']
    for(let temp = 0; temp < array.length; temp++){
      axios({
        method: 'get',
        baseURL: 'http://ming-desktop.ddns.net:8192/fhir',
        url: '/Observation',
        params: {
          subject: "test-03121002",
          code: array[temp],
          _sort: "date",
        },
        'Access-Control-Allow-Origin': '*',
      }).then((response) => {
        const result = response.data.entry
        console.log(result)
        this.$data.dataTitle.push(array2[temp])
        let tempDataArray = []
        let tempLabelArray = []
        for(let i = 0; i < result.length; i++){
          tempDataArray.push(result[i].resource.valueQuantity.value)
          // maybe using effectiveDateTime? is a good idea!
          tempLabelArray.push(result[i].resource.effectiveDateTime)
        }
        this.$data.dataData.push(tempDataArray)
        this.$data.dataLabel.push(tempLabelArray)
      }).catch(error => {
        console.log(error)
      })
    }

  },
}
</script>

<style>
#app {
  display: flex;
  height: 500px;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  border-style: double;
}
#divChart{
  overflow: auto;
}
</style>
