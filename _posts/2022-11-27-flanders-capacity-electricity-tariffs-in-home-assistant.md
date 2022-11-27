---
layout: post
title: "Flanders/Belgium's Capacity Tariffs in Home Assistant"
categories: []
tags:
 - Home Assistant
 - Energy
 - Automation
---

Flanders will reform the [nettariffs](https://www.vreg.be/nl/wat-zijn-de-nieuwe-nettarieven-en-hoe-worden-ze-berekend) for electricity transport, shifting a larger cost to peak usage. They do this by measuring your average consumption per 15m and the maximum quarter of the month counts as your tariff. Currently information and dashboards from Fluvius are cumbersome to use (CSV export and then leveraging Excel to spot the highest quarter).

I'm tracking my Electricty / Gas / Water in [Home Assistant](https://home-assistant.io/) already, so let's take a look what we need to do.

### Track quarterly values

We will be using the [statistics](https://www.home-assistant.io/integrations/statistics/) integration to generate these values:

```yaml
sensor:
  - platform: statistics
    name: electricity_delivery_power_rolling_15m
    entity_id: sensor.dsmr_reading_electricity_currently_delivered
    state_characteristic: average_linear
    max_age:
      minutes: 15
    sampling_size: 30
    precision: 1
```

### Calculate the maximum for 15m, day and month

To calculate the peak of the month, we are going to use the [statistics](https://www.home-assistant.io/integrations/statistics) integration:

```yaml
template:
  sensor:
    - name: electricity_delivery_power_daily_15m_max
      state: >
        {% if ((now().hour == 1) and (now().minute < 15)) %}
          {{ states('sensor.electricity_delivery_power_15m') or 0 | float }}
        {% elif (states('sensor.electricity_delivery_power_daily_15m_max') or 0 | float < states('sensor.electricity_delivery_power_15m') or 0 | float) %}
          {{ states('sensor.electricity_delivery_power_15m') or 0 | float }}
        {% else %}
          {{ states('sensor.electricity_delivery_power_daily_15m_max') or 0 | float }} 
        {% endif %}
      unit_of_measurement: 'W'
    - name: electricity_delivery_power_monthly_15m_max
      state: >
        {% if ((now().day == 1) and (now().hour == 1) and (now().minute < 15)) %}
          {{ states('sensor.electricity_delivery_power_15m') or 0 | float }}
        {% elif (states('sensor.electricity_delivery_power_monthly_15m_max') or 0 | float < states('sensor.electricity_delivery_power_15m') or 0 | float) %}
          {{ states('sensor.electricity_delivery_power_15m') or 0 | float }}
        {% else %}
          {{ states('sensor.electricity_delivery_power_monthly_15m_max') or 0 | float }} 
        {% endif %}
unit_of_measurement: 'kW'
  trigger:
    platform: time_pattern
    minutes: "/15"
  sensor:
    - name: electricity_delivery_power_15m
      state: "{{ states('sensor.electricity_delivery_power_rolling_15m') }}"
      unit_of_measurement: 'kW'
```

### Visualizing

Making use of [Apexcharts Card](https://github.com/RomRider/apexcharts-card), visualizing some elements 

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - entity: sensor.electricity_delivery_power_rolling_15m
      - entity: sensor.electricity_delivery_power_15m
      - entity: sensor.electricity_delivery_power_daily_15m_max
      - entity: sensor.electricity_delivery_power_monthly_15m_max
    state_color: false
    title: Capacity Tariffs
  - type: custom:apexcharts-card
    graph_span: 24h
    header:
      show: true
      title: Capacity Tariffs Peaks last 24h
    apex_config:
      yaxis:
        - id: first
          forceNiceScale: true
          decimalsInFloat: 2
          opposite: false
          name: Energie
    all_series_config:
      stroke_width: 1
    series:
      - entity: sensor.electricity_delivery_power_15m
        unit: W
        type: column
        transform: return x * 1000;
        name: 15m
        stroke_width: 3
        group_by:
          duration: 15m
        show:
          datalabels: false
          extremas: true
      - entity: sensor.electricity_delivery_power_monthly_15m_max
        unit: W
        type: line
        name: monthly
        transform: return x * 1000;
        show:
          datalabels: false
          extremas: false
      - entity: sensor.electricity_delivery_power_rolling_15m
        unit: W
        type: line
        transform: return x * 1000;
        name: 15m
        show:
          datalabels: false
          extremas: false
```