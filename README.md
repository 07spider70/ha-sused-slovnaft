# Sused Slovnaft for Home Assistant

[![HACS Valid](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/07spider70/ha-sused-slovnaft?style=for-the-badge)](https://github.com/07spider70/ha-sused-slovnaft/releases)
[![Tests](https://img.shields.io/github/actions/workflow/status/07spider70/ha-sused-slovnaft/tests.yml?style=for-the-badge)](https://github.com/07spider70/ha-sused-slovnaft/actions)

Neoficiálna Home Assistant integrácia pre transparentné sledovanie kvality ovzdušia a plánovaných aktivít rafinérie Slovnaft v Bratislave (Rovinka, Vlčie hrdlo, Podunajské Biskupice).

A unofficial custom Home Assistant integration to track air quality and planned refinery activities for the Slovnaft refinery in Bratislava.

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
### ⚠️ Disclaimer (English)

*This is an unofficial, community-created integration and is not affiliated with,
endorsed by, or supported by Slovnaft, a.s., or the MOL Group in any way.
All product and company names, including "Slovnaft" and "Sused Slovnaft",
are the registered trademarks of their respective owners.
The use of any trade name or trademark within this project is for identification
and reference purposes only (nominative fair use).*

*This software is provided "AS IS", without warranty of any kind.
By using this integration, you agree that the author is not responsible
for any potential issues arising from its use, including but not limited to,
temporary or permanent account bans, API access blocks,
or any damage to your Home Assistant instance.*

*__Important Note__: This integration interacts with an undocumented API.
Please be respectful to the servers. Do not decrease the default polling
intervals to avoid overloading their systems. The API may change, break,
or become entirely unavailable at any time without notice.*

### ⚠️ Vyhlásenie o odmietnutí zodpovednosti (Disclaimer)

*Táto integrácia je neoficiálnym komunitným projektom a nie je nijako spojená,
schválená, ani inak podporovaná spoločnosťou Slovnaft, a.s., ani skupinou MOL.
Všetky názvy produktov a spoločností, vrátane slova „Slovnaft“ a „Sused Slovnaft“,
sú registrovanými ochrannými známkami ich príslušných vlastníkov.
Použitie akéhokoľvek obchodného názvu alebo ochrannej známky v tomto projekte
slúži výlučne na účely identifikácie a referencie.*

*Tento softvér je poskytovaný „TAK, AKO JE“ (AS IS), bez akejkoľvek záruky.
Používaním tejto integrácie súhlasíte s tým, že autor nenesie zodpovednosť
za žiadne potenciálne problémy vyplývajúce z jej používania, vrátane,
ale nie výlučne, dočasného alebo trvalého zablokovania vášho používateľského účtu,
zablokovania prístupu k API alebo akéhokoľvek poškodenia vašej inštalácie Home Assistant.*

*__Dôležité upozornenie__: Táto integrácia využíva neverejné API.
Buďte prosím ohľaduplní k serverom poskytovateľa. Nezmenšujte predvolené
intervaly obnovovania dát (polling), aby ste predišli ich preťaženiu.
Toto API sa môže kedykoľvek zmeniť alebo prestať fungovať úplne bez predchádzajúceho upozornenia.*