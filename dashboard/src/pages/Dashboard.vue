<template>
  <div>
    <div class="row">
      <div class="col-12">
        <card type="chart">
          <template slot="header">
            <div class="row">
              <div class="col-sm-6" :class="isRTL ? 'text-right' : 'text-left'">
                <h5 class="card-category">{{ $t('dashboard.Environment') }}</h5>
                <h2 class="card-title">{{ this.cardTitle }}</h2>
              </div>
              <div class="col-sm-6">
                <div class="btn-group btn-group-toggle"
                     :class="isRTL ? 'float-left' : 'float-right'"
                     data-toggle="buttons">
                  <label v-for="(option, index) in bigLineChartCategories"
                         :key="option"
                         class="btn btn-sm btn-primary btn-simple"
                         :class="{active: bigLineChart.activeIndex === index}"
                         :id="index">
                    <input type="radio"
                           @click="initBigChart(index)"
                           name="options" autocomplete="off"
                           :checked="bigLineChart.activeIndex === index">
                    {{ option }}
                  </label>
                </div>
              </div>
            </div>
          </template>
          <div class="chart-area">
            <line-chart style="height: 100%"
                        ref="bigChart"
                        chart-id="big-line-chart"
                        :chart-data="bigLineChart.chartData"
                        :gradient-colors="bigLineChart.gradientColors"
                        :gradient-stops="bigLineChart.gradientStops"
                        :extra-options="bigLineChart.extraOptions">
            </line-chart>
          </div>
        </card>
      </div>
    </div>
    <div class="row">
      <div class="col-lg-6" :class="{'text-right': isRTL}">
        <card type="chart">
          <template slot="header">
            <h5 class="card-category">{{ $t('dashboard.cumulative') }}</h5>
            <h3 class="card-title"><i class="tim-icons icon-calendar-60 text-primary "></i> Average Daily Outdoor Temperature
            </h3>
          </template>
          <div class="chart-area">
            <line-chart style="height: 100%"
                        chart-id="green-line-chart"
                        :chart-data="purpleLineChart.chartData"

                        :gradient-stops="purpleLineChart.gradientStops"
                        :extra-options="purpleLineChart.extraOptions">
            </line-chart>
          </div>
        </card>
      </div>
      <div class="col-lg-6" :class="{'text-right': isRTL}">
        <card type="chart">
          <template slot="header">
            <h5 class="card-category">{{ $t('dashboard.cumulative') }}</h5>
            <h3 class="card-title"><i class="tim-icons icon-send text-info "></i> Air-Conditioner Usage Time</h3>
          </template>
          <div class="chart-area">
            <bar-chart style="height: 100%"
                       chart-id="blue-bar-chart"
                       :chart-data="blueBarChart.chartData"
                       :gradient-stops="blueBarChart.gradientStops"
                       :extra-options="blueBarChart.extraOptions">
            </bar-chart>
          </div>
        </card>
      </div>
    </div>
  </div>
</template>
<script>
import LineChart from '@/components/Charts/LineChart';
import BarChart from '@/components/Charts/BarChart';
import * as chartConfigs from '@/components/Charts/config';
import config from '@/config';
import axios from 'axios';
import Vue from "vue";

export default {
  components: {
    LineChart,
    BarChart
  },
  data() {
    return {
      cardTitle: '',
      bigLineChart: Vue.observable({
        allData: [],
        activeIndex: 0,
        chartData: {
          datasets: [{}],
          labels: [
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
            '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23'
          ],
        },
        extraOptions: chartConfigs.purpleChartOptions,
        gradientColors: config.colors.primaryGradient,
        gradientStops: [1, 0.4, 0],
        categories: []
      }),
      purpleLineChart: Vue.observable({
        extraOptions: chartConfigs.greenChartOptions,
        chartData: {
          labels: [],
          datasets: [{
            label: "Celsius",
            fill: true,
            borderColor: config.colors.danger,
            borderWidth: 2,
            borderDash: [],
            borderDashOffset: 0.0,
            pointBackgroundColor: config.colors.danger,
            pointBorderColor: 'rgba(255,255,255,0)',
            pointHoverBackgroundColor: config.colors.danger,
            pointBorderWidth: 20,
            pointHoverRadius: 4,
            pointHoverBorderWidth: 15,
            pointRadius: 4,
            data: [],
          }]
        },
        gradientColors: ['rgba(66,134,121,0.15)', 'rgba(66,134,121,0.0)', 'rgba(66,134,121,0)'],
        gradientStops: [1, 0.4, 0],
      }),
      blueBarChart: Vue.observable({
        extraOptions: chartConfigs.barChartOptions,
        chartData: {
          labels: [],
          datasets: [{
            label: "Hours",
            fill: true,
            borderColor: config.colors.info,
            borderWidth: 2,
            borderDash: [],
            borderDashOffset: 0.0,
            data: [],
          }]
        },
        gradientColors: config.colors.primaryGradient,
        gradientStops: [1, 0.4, 0],
      })
    }
  },
  created() {
    this.$eventBus.$on('refreshData', () => {
      this.refreshData();
    });
    this.getChartData();
  },
  computed: {
    enableRTL() {
      return this.$route.query.enableRTL;
    },
    isRTL() {
      return this.$rtl.isRTL;
    },
    bigLineChartCategories() {
      return this.$t('dashboard.chartCategories');
    }
  },
  methods: {
    initBigChart(index) {
      let chartData = {
        datasets: [{
          fill: true,
          borderColor: config.colors.primary,
          borderWidth: 2,
          borderDash: [],
          borderDashOffset: 0.0,
          pointBackgroundColor: config.colors.primary,
          pointBorderColor: 'rgba(255,255,255,0)',
          pointHoverBackgroundColor: config.colors.primary,
          pointBorderWidth: 20,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 15,
          pointRadius: 4,
          data: this.bigLineChart.allData[index]
        }],
        labels: this.bigLineChart.chartData.labels,
      }
      this.$refs.bigChart.updateGradients(chartData);
      this.bigLineChart.chartData = chartData;
      this.bigLineChart.activeIndex = index;
    },
    getChartData() {
      this.bigLineChart.allData = [];
      let fd = new FormData()
      fd.append('data_type', 'temperature_in');
      axios({
        method: 'post',
        url: '/api/data-fetch',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        },
      }).then(response => {
        // console.log(response.data);
        this.cardTitle = response.data.day;
        this.bigLineChart.allData.push(response.data.temps);
      }).catch(error => {
        console.log(error);
      });

      fd = new FormData()
      fd.append('data_type', 'temperature_out');
      axios({
        method: 'post',
        url: '/api/data-fetch',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        },
      }).then(response => {
        // console.log(response.data);
        this.bigLineChart.allData.push(response.data.temps);
      }).catch(error => {
        console.log(error);
      });

      fd = new FormData()
      fd.append('data_type', 'light_intensity');
      axios({
        method: 'post',
        url: '/api/data-fetch',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        // console.log(response.data);
        this.bigLineChart.allData.push(response.data.lights);
      }).catch(error => {
        console.log(error);
      });

      fd = new FormData()
      fd.append('data_type', 'avg_temp_out');
      axios({
        method: 'post',
        url: '/api/data-fetch',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        // console.log(response.data);
        console.log(this.purpleLineChart.chartData.datasets[0].data);
        this.purpleLineChart.chartData.labels = response.data.day_labels;
        this.purpleLineChart.chartData.datasets[0].data = response.data.avg_temps;
        console.log(this.purpleLineChart.chartData.datasets[0].data);
      }).catch(error => {
        console.log(error);
      });

      fd = new FormData()
      fd.append('data_type', 'air_conditioner_usage_time');
      axios({
        method: 'post',
        url: '/api/data-fetch',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        },
      }).then(response => {
        // console.log(this.blueBarChart.chartData.datasets.data);
        this.blueBarChart.chartData.labels = response.data.day_labels;
        this.blueBarChart.chartData.datasets[0].data = response.data.using_times;
        // console.log(this.blueBarChart.chartData.datasets.data);
        // Vue.set(this.blueBarChart.chartData, 'labels', response.data.day_labels);
        // Vue.set(this.blueBarChart.chartData.datasets, 'data', response.data.using_times);
      }).catch(error => {
        console.log(error);
      });
    },

    refreshData() {
      this.getChartData();
      let current_index = this.bigLineChart.activeIndex;
      this.initBigChart(current_index);
    }

  },
  mounted() {
    this.i18n = this.$i18n;
    if (this.enableRTL) {
      this.i18n.locale = 'ar';
      this.$rtl.enableRTL();
    }
    this.initBigChart(0);
  },
  beforeDestroy() {
    if (this.$rtl.isRTL) {
      this.i18n.locale = 'en';
      this.$rtl.disableRTL();
    }
    this.$eventBus.$off('refreshData');
  }
};
</script>
<style>
</style>
