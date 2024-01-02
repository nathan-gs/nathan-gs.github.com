---
layout: post
title: "Flanders/Belgium's Capacity Tariffs in Home Assistant with Improvements"
categories: []
tags:
 - Home Assistant
 - Home Energy Management
 - Home Automation
---

Flanders reformed the [nettariffs](https://www.vreg.be/nl/wat-zijn-de-nieuwe-nettarieven-en-hoe-worden-ze-berekend) for electricity transport, shifting a larger cost to peak usage. They do this by measuring your average consumption per 15m and the maximum quarter of the month counts as your tariff. Currently information and dashboards from Fluvius are cumbersome to use (CSV export and then leveraging Excel to spot the highest quarter). In a 2012 I wrote a quite popular blog post about [how to integrate capacity tariffs in Home Assistant](/2022/11/27/flanders-capacity-electricity-tariffs-in-home-assistant/).

After a year of living with capacity tariffs (and being annoyed with it...) I want to share certain improvements. 

## DSMR / P1 meter now reports on the delivery power 15m and the monthly peak

Likely with the latest firmware’s your DSMR/P1 meter includes the `electricity_delivery_power_15m` and the `electricity_delivery_power_monthly_15m_max` sensors. In the P1 meter I use it's reported under the `dsmr/consumption/quarter-hour-peak-electricity/average_delivered` and `dsmr/consumption/peak/running_month` topics.

I had to manually include `dsmr/consumption/peak/running_month` these in Home Assistant because they are not picked-up by the DSMR implementation. 

```yaml
mqtt:
  sensor:    
    - name = "electricity_delivery_power_monthly_15m_max";
      state_topic = "dsmr/consumption/peak/running_month";
      unit_of_measurement = "kW";
      device_class = "power";
      force_update = true;
      icon = "mdi:meter-electric";
```

## Unavailable metrics after a Home Assistant restart

The best solution is to configure [MQTT retention](http://www.steves-internet-guide.com/mqtt-retained-messages-example/) on your P1 meter, unfortunately my P1 meter doesn't support this. 

## Estimate your quarter peak consumption 

To be able to adjust your consumption early warnings are important! 

In the past I had a very simple notification mechanism based on a fixed threshold, if I currently consumed more than 2300W I receive a notification. 
{% raw %}
```yaml
trigger:
  - platform: template
    value_template: >
      {% set electricity_delivery_power_15m = states('sensor.electricity_delivery_power_15m') | float(0) %}
      {{ electricity_delivery_power_15m > 2.3 }}
action:
  - data:
      message: >
        {% set electricity_delivery_power_15m = states('sensor.electricity_delivery_power_15m') | float(0) %}

        {% set electricity_delivery_power_15m_estimated = states('sensor.electricity_delivery_power_15m_estimated') | float(0) %}

        {% set currently_delivered = states('sensor.dsmr_reading_electricity_currently_delivered') | float(0) * 1000 %}

        {% set minutes_remaining = (now().minute // 15 + 1) * 15 - now().minute %}

        Currently at capacity peak {{ electricity_delivery_power_15m }}kW,
        estimated to be {{ electricity_delivery_power_15m_estimated }}kW with {{minutes_remaining }}m remaining, current power {{ currently_delivered }}W
      title: Electricity Peak
    service: notify.notify
alias: electricity_delivery_power_max_threshold.notify
condition: []
mode: single
```
{% endraw %}

I improved this significantly by estimating what the current quarter peak will be in a new sensor:

{% raw %}
```yaml
# Let's smooth our consumption slightly 
sensor:
  - platform: statistics
    name: electricity_grid_consumed_power_avg_1m
    entity_id: sensor.electricity_grid_consumed_power
    sampling_size: 60
    state_characteristic: "average_linear"
    max_age:
        minutes: 60

template:
  - sensor:
    - name: "electricity_delivery_power_15m_estimated"
      unit_of_measurement: "kW"
      state: >
        {% set seconds_left = (15 - now().minute % 15) * 60 - now().second % 60 %}
        {# workaround because power_15m reports the previous value for ~ 10s after the quarter #}
        {% if seconds_left < (15 * 60 - 30)  %}
          {% set power_15m = states('sensor.electricity_delivery_power_15m') | float(0) %}
        {% else %}
          {% set power_15m = 0 %}
        {% endif %}
        {% set current_power = (states('sensor.electricity_grid_consumed_power_avg_1m') | float(states('sensor.electricity_grid_consumed_power') | float(0))) / 1000 %}
        {% set current_power_till_end = (current_power * seconds_left) / (3600 / 4) %}
        {{ ((current_power_till_end + power_15m)) | round(2) }}
      state_class: "measurement"
      device_class: "power"
```
{% endraw %}

Based on this I can get quite reliable estimations, based on the current power consumption and the delivery power. 

{% include post_img img="ha-estimated.png" alt="Estimations inside Home Assistant" width="100%" %}

## My config

I use NixOS and Nix for configuring Home Assistant, nonetheless it might still be useful for some, the config is part of [nathan-gs/nix-conf/smarthome/energy/capacity_peaks.nix](https://github.com/nathan-gs/nix-conf/blob/main/smarthome/energy/capacity_peaks.nix).

## Finally

Making use of good notifications, some common sense it's still difficult to remain under the 2500W barrier, especially because the way it's measured is quite unforgiving. 