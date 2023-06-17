<template>
  <div class="row">
    <div class="col-6">
      <card class="text-left">
        <div>
          <h2 class="card-title" style="font-size: 24pt;font-weight: bold">Air Conditioner</h2>
          <p class="card-text" style="font-size:16pt">Automation: {{ air_conditioner.automation }}</p>
          <p class="card-text" style="font-size:16pt">State: {{ air_conditioner.state }}</p>
          <br>
        </div>
        <div class="row">
          <div class="col-6">
            <base-button class="animation-on-hover" block type="info" @click="acClick1">
              Automation ON
            </base-button>
          </div>
          <div class="col-6">
            <base-button class="animation-on-hover" block type="danger" @click="acClick2">
              Automation OFF
            </base-button>
          </div>
        </div>
        <div class="row">
          <div class="col-4">
            <base-button class="animation-on-hover" block type="info" @click="acClick3">
              Cool Mode
            </base-button>
          </div>
          <div class="col-4">
            <base-button class="animation-on-hover" block type="primary" @click="acClick4">
              Heat Mode
            </base-button>
          </div>
          <div class="col-4">
            <base-button class="animation-on-hover" block type="danger" @click="acClick5">
              Turn OFF
            </base-button>
          </div>
        </div>
      </card>
    </div>
    <div class="col-6">
      <card class="text-left">
        <div>
          <h2 class="card-title" style="font-size: 24pt;font-weight: bold">Lamp</h2>
          <p class="card-text" style="font-size:16pt">Automation: {{ lamp.automation }}</p>
          <p class="card-text" style="font-size:16pt">State: {{ lamp.state }}</p>
          <br>
        </div>
        <div class="row">
          <div class="col-6">
            <base-button class="animation-on-hover" block type="info" @click="lampClick1">
              Automation ON
            </base-button>
          </div>
          <div class="col-6">
            <base-button class="animation-on-hover" block type="danger" @click="lampClick2">
              Automation OFF
            </base-button>
          </div>
        </div>
        <div class="row">
          <div class="col-6">
            <base-button class="animation-on-hover" block type="info" @click="lampClick3">
              Turn ON
            </base-button>
          </div>
          <div class="col-6">
            <base-button class="animation-on-hover" block type="danger" @click="lampClick4">
              Turn OFF
            </base-button>
          </div>
        </div>
      </card>
    </div>
  </div>
</template>
<script>
import axios from 'axios';
import NotificationSuccess from './Notifications/NotificationSuccess.vue';
import NotificationFail from "./Notifications/NotificationFail.vue";


export default {
  data() {
    return {
      air_conditioner: {
        automation: '',
        state: ''
      },
      lamp: {
        automation: '',
        state: ''
      }
    }
  },

  created() {
    this.$eventBus.$on('refreshData', () => {
      this.refreshData();
    });
    this.getChartData();
  },

  beforeDestroy() {
    this.$eventBus.$off('refreshData');
  },

  methods: {
    getChartData() {
      axios.post('/api/device-info').then(response => {
        let lamp = response.data.lamp;
        if (lamp[0] === 0) {
          this.lamp.state = "OFF";
        } else if (lamp[0] === 1) {
          this.lamp.state = "ON";
        }
        if (lamp[1] === 0) {
          this.lamp.automation = "OFF";
        } else if (lamp[1] === 1) {
          this.lamp.automation = "ON";
        }
        let ac = response.data.ac;
        if (ac[0] === 0) {
          this.air_conditioner.state = "OFF";
        } else if (ac[0] === 1) {
          this.air_conditioner.state = "COOL";
        } else if (ac[0] === 2) {
          this.air_conditioner.state = "HEAT";
        }
        if (ac[1] === 0) {
          this.air_conditioner.automation = "OFF";
        } else if (ac[1] === 1) {
          this.air_conditioner.automation = "ON";
        }

      }).catch(error => {
        console.log(error);
      });

    },

    notifyVueSuccess(verticalAlign, horizontalAlign) {
      this.$notify({
        component: NotificationSuccess,
        icon: "tim-icons icon-check-2",
        horizontalAlign: horizontalAlign,
        verticalAlign: verticalAlign,
        type: 'success',
        timeout: 0
      });
    },
    notifyVueError(verticalAlign, horizontalAlign) {
      this.$notify({
        component: NotificationFail,
        icon: "tim-icons icon-alert-circle-exc",
        horizontalAlign: horizontalAlign,
        verticalAlign: verticalAlign,
        type: 'danger',
        timeout: 0
      });
    },

    acClick1() {
      let fd = new FormData()
      fd.append('device', 'ac')
      fd.append('state', '-1')
      fd.append('automation', '1')
      axios({
        method: 'post',
        url: '/api/device-control',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        console.log(response)
        let code = response.data.code;
        console.log(code)
        if (code === 0) {
          this.notifyVueSuccess('bottom', 'center');
          this.air_conditioner.automation = 'ON';
        } else {
          this.notifyVueError('bottom', 'center');
        }
      }).catch(error => {
        console.log(error);
      });
    },

    acClick2() {
      let fd = new FormData()
      fd.append('device', 'ac')
      fd.append('state', '-1')
      fd.append('automation', '0')
      axios({
        method: 'post',
        url: '/api/device-control',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        let code = response.data.code;
        if (code === 0) {
          this.notifyVueSuccess('bottom', 'center');
          this.air_conditioner.automation = 'OFF';
        } else {
          this.notifyVueError('bottom', 'center');
        }
      }).catch(error => {
        console.log(error);
      });
    },

    acClick3() {
      let fd = new FormData()
      fd.append('device', 'ac')
      fd.append('state', '1')
      fd.append('automation', '-1')
      axios({
        method: 'post',
        url: '/api/device-control',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        let code = response.data.code;
        if (code === 0) {
          this.notifyVueSuccess('bottom', 'center');
          this.air_conditioner.state = 'COOL';
          this.air_conditioner.automation = 'OFF';
        } else {
          this.notifyVueError('bottom', 'center');
        }
      }).catch(error => {
        console.log(error);
      });
    },

    acClick4() {
      let fd = new FormData()
      fd.append('device', 'ac')
      fd.append('state', '2')
      fd.append('automation', '-1')
      axios({
        method: 'post',
        url: '/api/device-control',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        let code = response.data.code;
        if (code === 0) {
          this.notifyVueSuccess('bottom', 'center');
          this.air_conditioner.state = 'HEAT';
          this.air_conditioner.automation = 'OFF';
        } else {
          this.notifyVueError('bottom', 'center');
        }
      }).catch(error => {
        console.log(error);
      });
    },

    acClick5() {
      let fd = new FormData()
      fd.append('device', 'ac')
      fd.append('state', '0')
      fd.append('automation', '-1')
      axios({
        method: 'post',
        url: '/api/device-control',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        let code = response.data.code;
        if (code === 0) {
          this.notifyVueSuccess('bottom', 'center');
          this.air_conditioner.state = 'OFF';
          this.air_conditioner.automation = 'OFF';
        } else {
          this.notifyVueError('bottom', 'center');
        }
      }).catch(error => {
        console.log(error);
      });
    },

    lampClick1() {
      let fd = new FormData()
      fd.append('device', 'lamp')
      fd.append('state', '-1')
      fd.append('automation', '1')
      axios({
        method: 'post',
        url: '/api/device-control',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        let code = response.data.code;
        if (code === 0) {
          this.notifyVueSuccess('bottom', 'center');
          this.lamp.automation = 'ON';
        } else {
          this.notifyVueError('bottom', 'center');
        }
      }).catch(error => {
        console.log(error);
      });
    },

    lampClick2() {
      let fd = new FormData()
      fd.append('device', 'lamp')
      fd.append('state', '-1')
      fd.append('automation', '0')
      axios({
        method: 'post',
        url: '/api/device-control',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        let code = response.data.code;
        if (code === 0) {
          this.notifyVueSuccess('bottom', 'center');
          this.lamp.automation = 'OFF';
        } else {
          this.notifyVueError('bottom', 'center');
        }
      }).catch(error => {
        console.log(error);
      });
    },

    lampClick3() {
      let fd = new FormData()
      fd.append('device', 'lamp')
      fd.append('state', '1')
      fd.append('automation', '-1')
      axios({
        method: 'post',
        url: '/api/device-control',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        let code = response.data.code;
        if (code === 0) {
          this.notifyVueSuccess('bottom', 'center');
          this.lamp.state = 'ON';
          this.lamp.automation = 'OFF';
        } else {
          this.notifyVueError('bottom', 'center');
        }
      }).catch(error => {
        console.log(error);
      });
    },

    lampClick4() {
      let fd = new FormData()
      fd.append('device', 'lamp')
      fd.append('state', '0')
      fd.append('automation', '-1')
      axios({
        method: 'post',
        url: '/api/device-control',
        data: fd,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        let code = response.data.code;
        if (code === 0) {
          this.notifyVueSuccess('bottom', 'center');
          this.lamp.state = 'OFF';
          this.lamp.automation = 'OFF';
        } else {
          this.notifyVueError('bottom', 'center');
        }
      }).catch(error => {
        console.log(error);
      });
    },

  }
}
</script>
