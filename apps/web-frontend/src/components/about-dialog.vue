// Stellarium Web - Copyright (c) 2022 - Stellarium Labs SRL
//
// This program is licensed under the terms of the GNU AGPL v3, or
// alternatively under a commercial licence.
//
// The terms of the AGPL v3 license can be found in the main directory of this
// repository.

<template>
<v-dialog fullscreen hide-overlay transition="dialog-bottom-transition" v-model="$store.state.showAboutDialog">
  <v-card v-if="$store.state.showAboutDialog" style="padding-top: 32px !important;">
    <v-toolbar flat color="transparent" style="padding-top: 16px !important;">
      <v-btn icon @click="goBack">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-toolbar-title>About Amistra</v-toolbar-title>
    </v-toolbar>
    <v-card-text>
      <p><strong>Amistra</strong> is an open-source mobile planetarium that turns your Android device into a window on the night sky. Point it up to identify stars, planets, constellations, black holes and deep sky objects in real-time.</p>

      <h3>About this project</h3>
      <p>Amistra was put together by <strong>Mike</strong> — it is made for <strong>Ami</strong>.</p>
      <p class="about-dedication">made by mike &hearts; for my beautiful girl</p>

      <h3>Development</h3>
      <ul class="about-credits">
        <li>Fork of the Stellarium Web Engine (AGPL-3.0)</li>
        <li>Custom black hole catalogue and renderer</li>
        <li>Cyberpunk UI theme</li>
        <li>Gyroscope sky tracking + AR camera overlay</li>
        <li>Offline-first Android build via Capacitor</li>
      </ul>

      <h3>Built on</h3>
      <p><strong>Stellarium Web Engine</strong> — high-performance astronomical rendering by Stellarium Labs SRL.</p>

      <h3>Source</h3>
      <p><a href="https://github.com/DesolateSea/Astara_stellarium-web-engine" target="_blank" rel="noopener">https://github.com/DesolateSea/Astara_stellarium-web-engine</a></p>

      <h3>Data credits</h3>
      <p>Astronomical data from Gaia, Hipparcos, HyperLeda, SIMBAD and more.</p>
      <v-btn small outlined color="primary" @click="openDataCredits" class="mb-4">
        View Data Credits
      </v-btn>

      <h3>License</h3>
      <p>Amistra is licensed under the <strong>GNU Affero General Public License v3.0</strong> (AGPL-3.0), inherited from Stellarium Web Engine.</p>
      <p><br></p>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer><v-btn text class="blue--text darken-1" @click.native="$store.state.showAboutDialog = false">Close</v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>
</template>

<script>
export default {
  name: 'AboutDialog',
  methods: {
    goBack () {
      this.$store.state.showAboutDialog = false
      this.$store.state.showSettingsPanel = true
    },
    openDataCredits () {
      this.$store.state.showAboutDialog = false
      this.$store.state.showDataCreditsDialog = true
    }
  }
}
</script>

<style>
.about-credits {
  padding-left: 30px;
}
.about-dedication {
  color: #ff2bd6;
  font-style: italic;
  letter-spacing: 0.5px;
}
a {
  color: #82b1ff;
}
</style>
