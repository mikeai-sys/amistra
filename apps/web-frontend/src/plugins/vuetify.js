import '@mdi/font/css/materialdesignicons.css'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'

Vue.use(Vuetify)

export default new Vuetify({
  theme: {
    dark: true,
    themes: {
      dark: {
        primary: '#00f0ff',
        secondary: '#ff2bd6',
        accent: '#7c4dff',
        error: '#ff2e63',
        info: '#00b3ff',
        success: '#00ff9c',
        warning: '#ffb300',
        background: '#04060c',
        surface: '#0a1020'
      }
    }
  }
})
