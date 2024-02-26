---
layout: post
title: "Home Assistant: Map Card, displaying Weather and Other Tile Layers"
categories: 
tags:
 - Home Assistant
 - Geography
 - Home Automation
 - OSS
image: /assets/post/2024/02/25/ha-map-card-displaying-weather-and-other-tilelayers/ha-map-card-weather-carto.png
excerpt: >
    <img src="/assets/post/2024/02/25/ha-map-card-displaying-weather-and-other-tilelayers/ha-map-card-with-weather-carto.png" alt="custom:map-card with a CARTO and Weather layer" height="148" width="157" style="float: left; padding: 30px;" />
    Displaying a weather map in Home Assistant got easier using [__ha-map-card__](https://github.com/nathan-gs/ha-map-card) and it's support for multiple __Tile Layers__. My open-source project `ha-map-card` provides a a new lovelace card, serving as an enhancement to the native Home Assistant [map-card](https://www.home-assistant.io/dashboards/map/), bringing a host of advanced features like __custom tile layers__, __entity__ display options. It is built on [leaflet](https://leafletjs.com/).

    In version `0.4.0` some new options are introduced to enable multiple Tile Layers, we are going to use this to visualize a Cloud map using [OpenWeatherMap](https://openweathermap.org/api/weathermaps).
---

<img src="/assets/post/2024/02/25/ha-map-card-displaying-weather-and-other-tilelayers/ha-map-card-with-weather-carto.png" alt="custom:map-card with a CARTO and Weather layer" height="148" width="157" style="float: left; padding: 30px;" />
Displaying a weather map in Home Assistant got easier using [__ha-map-card__](https://github.com/nathan-gs/ha-map-card) and it's support for multiple __Tile Layers__. My open-source project [nathan-gs/ha-map-card](https://github.com/nathan-gs/ha-map-card) provides a lovelace card, serving as an enhancement to the native Home Assistant [map-card](https://www.home-assistant.io/dashboards/map/), bringing a host of advanced features like __custom tile layers__, __entity__ display options. It is built on [leaflet](https://leafletjs.com/).

In version `0.4.0` some new options are introduced to enable multiple Tile Layers, we are going to use this to visualize a Cloud map using [OpenWeatherMap](https://openweathermap.org/api/weathermaps).

>##### TIP
>
> An earlier version was introduced in [Home Assistant: Map Card, a new leaflet based map with WMS and other advanced features](/2024/01/06/ha-map-card-a-new-and-alternative-leaflet-based-map/).
{: .block-tip}


### Obtaining an API key

OpenWeatherMap requires an API key, head to the [api keys portal](https://home.openweathermap.org/api_keys) to obtain one.

### Installation of map-card

See [nathan-gs/ha-map-card#installation](https://github.com/nathan-gs/ha-map-card#installation).

### Creating the map

In Home Assistant add the `custom:map-card`, and give it following config. 

```yaml
type: custom:map-card
zoom: 8
card_size: 10
entities:
  - entity: zone.home
    display: icon
    size: 40
tile_layers:
  - url: >-
      https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid={apikey}
    options:
      attribution: <a href="https://openweathermap.org/">OpenWeatherMap</a>
      apikey: YOUR_API_KEY
```

We are using the [OpenWeatherMaps Weather Map 1.0](https://openweathermap.org/api/weathermaps), to display the clouds. We can also display _precipitation_, _pressure_, _wind_ and _temperature_. The service requires an api key, see `line 10` and `13`.

This results in the following map:

<img src="/assets/post/2024/02/25/ha-map-card-displaying-weather-and-other-tilelayers/ha-map-card-with-weather.png" alt="custom:map-card with a Weather layer" height="228" width="447" />

Unfortunately it's a bit hard to read and there is no way to adjust the opacity in OpenWeatherMaps Maps 1.0 (there is in [2.0](https://openweathermap.org/api/weather-map-1h)).

### Selecting a darker base map

By selecting a darker base map (eg. Satellite) it will be easier to see the clouds forming. We are going to use the CARTO Dark Matter maps. 

> ##### TIP
> 
> [Leaflet Providers](https://leaflet-extras.github.io/leaflet-providers/preview/) has a huge overview of usable base tile layers.

```yaml
type: custom:map-card
zoom: 8
card_size: 10
entities:
  - entity: zone.home
    display: icon
    size: 30
tile_layer_url: https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png
tile_layer_attribution: >-
  <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>
  contributors &copy; <a href="https://carto.com/attributions">CARTO</a>
tile_layers:
  - url: >-
      https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid={apikey}
    options:
      attribution: <a href="https://openweathermap.org/">OpenWeatherMap</a>
      apikey: YOUR_API_KEY

```

<img src="/assets/post/2024/02/25/ha-map-card-displaying-weather-and-other-tilelayers/ha-map-card-with-weather-carto.png" alt="custom:map-card with a CARTO and Weather layer" />

## Conclusion

Whether you're a weather enthusiast, a smart home hobbyist, or simply someone who appreciates intuitive design, ha-map-card opens up a world of possibilities for visualizing data in your home automation setup. So why not take your dashboard to the next level and start exploring the weather and beyond with the ha-map-card today.