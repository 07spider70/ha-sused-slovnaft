# Sused Slovnaft for Home Assistant

[![HACS Valid](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/07spider70/ha-sused-slovnaft?style=for-the-badge)](https://github.com/07spider70/ha-sused-slovnaft/releases)
[![Tests](https://img.shields.io/github/actions/workflow/status/07spider70/ha-sused-slovnaft/tests.yml?style=for-the-badge)](https://github.com/07spider70/ha-sused-slovnaft/actions)

Oficiálna Home Assistant integrácia pre transparentné sledovanie kvality ovzdušia a plánovaných aktivít rafinérie Slovnaft v Bratislave (Rovinka, Vlčie hrdlo, Podunajské Biskupice).

A custom Home Assistant integration to track air quality and planned refinery activities for the Slovnaft refinery in Bratislava.

## Features
* **Air Quality Monitoring:** Real-time data for PM10, PM2.5, SO2, NO2, Ozone, and more.
* **Refinery Calendar:** A dedicated Home Assistant Calendar entity showing planned flaring, noise, odors, and maintenance.
* **Multiple Stations:** Select from Rovinka, Podunajské Biskupice, or Vlčie hrdlo.
* **Fully Localized:** Supports English and Slovak (Slovenčina) natively.

## Installation

### Method 1: HACS (Recommended)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=07spider70&repository=ha-sused-slovnaft&category=integration)
1. Open HACS in your Home Assistant instance.
2. Click the `⋮` menu in the top right and select **Custom repositories**.
3. Add `https://github.com/07spider70/ha-sused-slovnaft` and select **Integration** as the category.
4. Click **Download** and restart Home Assistant.
5. Go to **Settings > Devices & Services > Add Integration** and search for *Sused Slovnaft*.

### Method 2: Manual
1. Download the latest release.
2. Copy the `custom_components/slovnaft` folder into your Home Assistant `custom_components` directory.
3. Restart Home Assistant and set it up via the UI.

## Configuration
During setup, you can customize:
* Which APIs to enable (Air Quality / Calendar).
* Polling intervals (to avoid spamming the Slovnaft servers).
* Specific monitoring stations to create sensors for.

---
*Disclaimer: This is a community project and is not officially affiliated with Slovnaft a.s.*