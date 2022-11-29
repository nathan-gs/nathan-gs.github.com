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

{% include post_img img="measurements-day.png" alt="Measurements inside Home Assistant" %}

I'm tracking my Electricity / Gas / Water in [Home Assistant](https://home-assistant.io/) already, so let's take a look what we need to do. This was inspired by a Forum thread at [Capaciteitstarief maandpiek zichtbaar maken in home assistant (userbase.be)](https://userbase.be/forum/viewtopic.php?p=945740#p945740).

### Track 15m values

We will be using the [utility_meter](https://www.home-assistant.io/integrations/utility_meter/) integration to generate these values:

```yaml
{% raw %}
utility_meter:
  electricity_delivery_15m:
    source: sensor.electricity_delivery
    cron: "*/15 * * * *"

{% endraw %}
```

##### Sidenote for Peak & Offpeak

If you receive data in `peak` & `offpeak` measurements; best to sum them before:
```yaml
{% raw %}
template:
- sensor:
  - name: electricity_delivery
  unit_of_measurement: "kWh"
  state: "{{ ( states('sensor.electricity_peak_delivery') | float ) + ( states('sensor.electricity_offpeak_delivery') | float ) }}";
{% endraw %}
```

### Calculate the 15m power

We now have the numbers in kWh (energy) but we need to convert to kW (power); we do this by multiplying by 4 (1h per quarter).

```yaml
{% raw %}
template:
- sensor:
  - name: electricity_delivery_power_15m
  unit_of_measurement: "kW"
  state: "{{ states('sensor.electricity_delivery_15m')  * 4 | float }}";
{% endraw %}
```

### Calculate the daily and monthly max

To calculate the 15m max for the day & month, we are using the following template, with a time_pattern trigger.

```yaml
{% raw %}
template:
  trigger:
    platform: time_pattern
    minutes: "/15"
  sensor:
  - name: electricity_delivery_power_daily_15m_max
    state: >
      {% if ((now().hour == 1) and (now().minute < 15)) or (states('sensor.electricity_delivery_power_daily_15m_max') in ["unavailable", "unknown"]) %}
        {{ states('sensor.electricity_delivery_power_15m') or 0 | float }}
      {% elif ((states('sensor.electricity_delivery_power_daily_15m_max') | float) < (states('sensor.electricity_delivery_power_15m') or 0) | float) %}
        {{ states('sensor.electricity_delivery_power_15m') or 0 | float }}
      {% else %}
        {{ states('sensor.electricity_delivery_power_daily_15m_max') or 0 | float }} 
      {% endif %}
    unit_of_measurement: 'kW'
  - name: electricity_delivery_power_monthly_15m_max
    state: >
      {% if ((now().day == 1) and (now().hour == 1) and (now().minute < 15)) or (states('sensor.electricity_delivery_power_monthly_15m_max') in ["unavailable", "unknown"]) %}
        {{ states('sensor.electricity_delivery_power_15m') or 0 | float }}
      {% elif ((states('sensor.electricity_delivery_power_monthly_15m_max') | float) < (states('sensor.electricity_delivery_power_15m') or 0) | float) %}
        {{ states('sensor.electricity_delivery_power_15m') or 0 | float }}
      {% else %}
        {{ states('sensor.electricity_delivery_power_monthly_15m_max') or 0 | float }} 
      {% endif %}
    unit_of_measurement: 'kW'
    
{% endraw %}
```

### Visualizing

Making use of [Apexcharts Card](https://github.com/RomRider/apexcharts-card), visualizing some elements 

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - entity: sensor.dsmr_reading_electricity_currently_delivered
      - entity: sensor.electricity_delivery_power_15m
      - entity: sensor.electricity_delivery_power_daily_15m_max
      - entity: sensor.electricity_delivery_power_monthly_15m_max
    state_color: false
    title: Capacity Tariffs
  - type: custom:apexcharts-card
    graph_span: 24h
    span:
      start: day
    header:
      show: true
      title: Capacity Tariffs Peaks last day
    apex_config:
      yaxis:
        - id: first
          forceNiceScale: true
          decimalsInFloat: 0
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
        stroke_width: 2
        group_by:
          duration: 15m
          func: last
        show:
          datalabels: false
          extremas: true
      - entity: sensor.electricity_delivery_power_monthly_15m_max
        unit: W
        type: line
        name: monthly
        transform: return x * 1000;
        group_by:
          duration: 15m
          func: last
        show:
          datalabels: false
          extremas: false
      - entity: sensor.electricity_delivery_power_rolling_15m
        unit: W
        type: line
        transform: return x * 1000;
        name: rolling
        group_by:
          duration: 15m
          func: last
        show:
          datalabels: false
          extremas: false
  - type: custom:apexcharts-card
    graph_span: 31d
    span:
      start: month
    header:
      show: true
      title: Capacity Tariffs Peaks last month
    apex_config:
      yaxis:
        - id: first
          forceNiceScale: true
          decimalsInFloat: 0
          opposite: false
          name: Energie
    all_series_config:
      stroke_width: 1
    series:
      - entity: sensor.electricity_delivery_power_daily_15m_max
        unit: W
        type: column
        transform: return x * 1000;
        name: day
        stroke_width: 4
        group_by:
          duration: 1d
          func: max
        show:
          datalabels: false
          extremas: true
      - entity: sensor.electricity_delivery_power_monthly_15m_max
        unit: W
        type: line
        name: monthly
        transform: return x * 1000;
        group_by:
          duration: 15m
          func: last
        show:
          datalabels: false
          extremas: false
```

{% include post_img img="measurements1.png" alt="Measurements inside Home Assistant" %}
{% include post_img img="measurements-day.png" alt="Measurements inside Home Assistant" %}
{% include post_img img="measurements-month.png" alt="Measurements inside Home Assistant" %}