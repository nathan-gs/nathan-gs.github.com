---
layout: post
title: "Calculating Degree Days in Home Assistant"
categories: 
excerpt: >
  Calculating [Degree Days](https://en.wikipedia.org/wiki/Degree_day) (or [Graaddag](https://nl.wikipedia.org/wiki/Graaddag) in Dutch) allows you to benchmark gas consumption in relation to temperature. The formula is quite simple, it uses as reference temperature 18°C minus the average temperature of the day, minimalized on 0°C. The concept is based on the idea that the amount of energy needed to maintain a comfortable indoor temperature increases as the difference between the indoor temperature and the outdoor temperature increases. By tracking the degree days, it is possible to estimate how much energy is needed to heat or cool a building and compare it to the actual energy usage.<br /><br />

  This configuration is using the [Home Assistant](https://home-assistant.io) platform to define two sensors: `degree_day_daily` and `gas_m3_per_degree_day`. The `degree_day_daily` sensor calculates the difference between a regularized temperature (18.0°C in this case) and the average linear temperature reported by the `sensor.garden_garden_temperature_noordkant_temperature` sensor over the past 24 hours. The `gas_m3_per_degree_day` sensor calculates the gas usage (as reported by the `sensor.gas_delivery_daily` sensor) per degree day, which is defined as the difference between the regularized temperature and the average linear temperature.
tags:
 - Home Assistant
 - Energy
 - Automation
---



Calculating [Degree Days](https://en.wikipedia.org/wiki/Degree_day) (or [Graaddag](https://nl.wikipedia.org/wiki/Graaddag) in Dutch) allows you to benchmark gas consumption in relation to temperature. The formula is quite simple, it uses as reference temperature 18°C minus the average temperature of the day, minimalized on 0°C. The concept is based on the idea that the amount of energy needed to maintain a comfortable indoor temperature increases as the difference between the indoor temperature and the outdoor temperature increases. By tracking the degree days, it is possible to estimate how much energy is needed to heat or cool a building and compare it to the actual energy usage.

This configuration is using the [Home Assistant](https://home-assistant.io) platform to define two sensors: `degree_day_daily` and `gas_m3_per_degree_day`. The `degree_day_daily` sensor calculates the difference between a regularized temperature (18.0°C in this case) and the average linear temperature reported by the `sensor.garden_garden_temperature_noordkant_temperature` sensor over the past 24 hours. The `gas_m3_per_degree_day` sensor calculates the gas usage (as reported by the `sensor.gas_delivery_daily` sensor) per degree day, which is defined as the difference between the regularized temperature and the average linear temperature.

Both sensors are triggered to update at the same time, 23:59:01 and 23:59:59 respectively, which corresponds to the end of the day. 

{% highlight yaml linenos %}
{% raw %}
sensor:
  - platform: statistics
    name: "outside_temperature_avg"
    entity_id: sensor.garden_garden_temperature_noordkant_temperature
    state_characteristic: average_linear
    max_age:
      hours: 24

template:
  - trigger:
      platform: time
      at: "23:59:01"
    sensor:
    - name: degree_day_daily
      state: >
        {% set regularized_temp = 18.0 | float %}
        {% set average_outside_temp = states('sensor.outside_temperature_avg') | float %}
        {% set dd = regularized_temp - average_outside_temp %}
        {% if dd > 0 %}
          {{ dd }}
        {% else %}
          0
        {% endif %}      
      unit_of_measurement: 'DD'
  - trigger:
      platform: time
      at: "23:59:59"
    sensor:
    - name: gas_m3_per_degree_day
      state: >
        {% set gas_usage = states('sensor.gas_delivery_daily') | float %}
        {% set dd = states('sensor.degree_day_daily') | float %}
        {% if dd > 0 %}
          {{ gas_usage / dd }}
        {% else %}
          0
        {% endif %}      
      unit_of_measurement: 'm³/DD'

{% endraw %}
{% endhighlight %}

You can find the implementation in my NixOS config [nathan-gs/nix-conf](https://github.com/nathan-gs/nix-conf/blob/main/smarthome/energy.nix#L379-L436) as well.

### Dashboard

Let's add a basic dashboard using [ApexCharts Card](https://github.com/RomRider/apexcharts-card): 
{% highlight yaml linenos %}
{% raw %}
type: custom:apexcharts-card
graph_span: 31d
span:
  start: month
show:
  last_updated: true
yaxis:
  - id: dd
    apex_config:
      forceNiceScale: true
      decimalsInFloat: 1
      tickAmount: 7
  - id: gas_per_dd
    opposite: true
    min: 0
    max: 4
    apex_config:
      forceNiceScale: false
      decimalsInFloat: 2
      tickAmount: 4
color_list:
  - '#1a4c6e'
header:
  show: true
  title: Degree Days
series:
  - entity: sensor.degree_day_daily
    name: Degree Day
    type: line
    group_by:
      func: last
      duration: 1d
    stroke_width: 2
    show:
      header_color_threshold: true
    yaxis_id: dd
  - entity: sensor.gas_m3_per_degree_day
    name: Gas m3 per DD
    type: line
    color: black
    group_by:
      func: last
      duration: 1d
    stroke_width: 2
    yaxis_id: gas_per_dd

{% endraw %}
{% endhighlight %}

{% include post_img img="degreedays.png" alt="Degree Days inside Home Assistant" %}