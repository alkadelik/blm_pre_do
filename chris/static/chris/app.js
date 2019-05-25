
// Vue.component("greeting", {
//   template: "<p>Hey there, I'm a re-usable component</p>"
// });
Vue.component('progress-bar', {
  template:
  `<div id="progress">
  <div class=""></div>
  <div class="step"></div><div class="step"></div><div class="step"></div><div class="step active"></div><div class=""></div></div>`
});
new Vue({
  delimiters: ['[[', ']]'],
  el: "#app",
  data: {
    budget: "",
    present: true,
    charmax: 30,
    step: 1,
    showprev: true,
    // showprev: false,
    menu: false,
    shownext: true,
    showsubmit: false,
    budgets: false,
    linkedBanks: false,
    settings: false,
  },
  methods: {
    charcount: function() {
      return this.charmax - this.budget.length;
    },
    next() {
      if (this.step < 8) {
        this.step++;
        this.showprev = true;
      } else if (this.step === 8) {
        this.step++;
        this.shownext = false;
        this.showsubmit = true;
      }
    },
    prev() {
      if (this.step >= 3) {
        this.step--;
        this.shownext = true;
        this.showsubmit = false;
      } else if (this.step === 2) {
        this.step--;
        this.showprev = false;
      }
    },
    menuAction() {
      if(this.menu == false){
        this.menu = true
      } else {
        this.menu = false
      }
    },
  },
  computed: {
    toggleView: function(){
      return {
        unhide: this.unhide,
      }
    },
  }
});
