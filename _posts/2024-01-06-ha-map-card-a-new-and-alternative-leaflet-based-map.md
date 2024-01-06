---
layout: post
title: "Home Assistant: Map Card, a new leaflet based map with WMS and other advanced features"
categories: 
tags:
 - Home Assistant
 - Geography
 - Home Automation
 - OSS
image: /assets/post/2024/01/06/ha-map-card-a-new-and-alternative-leaflet-based-map/ha-map-card-pm25.png
excerpt: >
    <img src="/assets/post/2024/01/06/ha-map-card-a-new-and-alternative-leaflet-based-map/ha-map-card-pm25.png" alt="custom:map-card with a WMS layer" height="166" width="252" style="float: left; padding: 30px;" />
    Introducing [ha-map-card](https://github.com/nathan-gs/ha-map-card) a new lovelace card, serving as an enhancement to the native Home Assistant [map-card](https://www.home-assistant.io/dashboards/map/), bringing a host of advanced features to the forefront. Built on the foundation of [leaflet](https://leafletjs.com/). The main features are:  __Custom Tile Layers__ and __WMS Layers Support__.

---

<img src="/assets/post/2024/01/06/ha-map-card-a-new-and-alternative-leaflet-based-map/ha-map-card-pm25.png" alt="custom:map-card with a WMS layer" height="166" width="252" style="float: left; padding: 30px;" />
Introducing [ha-map-card](https://github.com/nathan-gs/ha-map-card) a new lovelace card, serving as an enhancement to the native Home Assistant [map-card](https://www.home-assistant.io/dashboards/map/), bringing a host of advanced features to the forefront. Built on the foundation of [leaflet](https://leafletjs.com/).

The main features are:

- __Custom Tile Layers__: One of the standout features is the ability to use custom map tiles. Tailor your map to suit your preferences, ensuring a personalized and visually appealing dashboard. This makes it easy to use [OpenStreetMap](https://www.openstreetmap.org) and other maps inside your dashboards.
- __WMS Layer Support__: ha-map-card goes beyond the basics by offering support for Web Map Service (WMS) layers. This advanced functionality allows users to overlay additional map information, such as weather data or satellite imagery.
- more to come, like ImageOverlay & VideoOverlays, legends, etc

> #### TIP
>
> Home Assistant contains a [native map](https://www.home-assistant.io/dashboards/map/) card, if you don't need advanced features like WMS layers it might be a better choice.

### Integrating ha-map-card into Your Setup

#### Installation

Use [HACS](https://hacs.xyz) and point it to `https://github.com/nathan-gs/ha-map-card` or do a manual install; copy the `map-card.js` to your `/var/lib/hass/www` folder.

#### Usage

The most minimal config:

```yaml
type: custom:map-card
'x': 51.2
'y': 3.6
```

The [full set of options](https://github.com/nathan-gs/ha-map-card#options) can be found in the readme.

### A more advanced example: Measuring PM2.5 air quality for my home

Using the Belgium's [IRCELINE WMS service](https://www.irceline.be/en/documentation/open-data) we are going to overlay a map over my home to show the Particulate Matter. 

```yaml
type: custom:map-card
'x': 51.2
'y': 3.6
zoom: 8
card_size: 6
wms:
  - url: https://geo.irceline.be/rioifdm/wms
    options:
      layers: pm25_hmean
      transparent: true
      format: image/png
      opacity: 0.7
      tiled: true
      time: now
      attribution: '<a href="https://www.irceline.be/">IRCELINE</a>'
tile_layer_url: 'https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png'
tile_layer_attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions">CARTO</a>'
entities:
  - zone.home
``` 

We are also overriding the `tile_layer_url` to make use of the same tile layer Home Assistant uses ([CARTO](https://carto.com/)), always be careful to give proper attribution. By default it will use the [OpenStreetMap tiles](https://wiki.openstreetmap.org/wiki/Tiles).

#### The result 

<img src="/assets/post/2024/01/06/ha-map-card-a-new-and-alternative-leaflet-based-map/ha-map-card-pm25.png" alt="custom:map-card with a WMS layer" width="100%" />. 

## Conclusion

Unlock the full potential of geospatial inside Home Assistant with the [ha-map-card](https://github.com/nathan-gs/ha-map-card)'s advanced features, customizability, and support for WMS layers.