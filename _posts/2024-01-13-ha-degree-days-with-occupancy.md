---
layout: post
title: "Degree Days with Occupancy adjustments in Home Assistant"
categories: 
excerpt: >
  [Degree Days](https://en.wikipedia.org/wiki/Degree_day) (or [Graaddag](https://nl.wikipedia.org/wiki/Graaddag) in Dutch) allows you to benchmark energy consumption in relation to temperature.While it definitely is a useful benchmark it falls short into taking account if people are home or not. Based on the Degree Day calculation, and the # of hours anyone is at home, I will calculate a new metric: `(DD/gas m3)*(1+(24-hours))/(1+24)`.
tags:
 - Home Assistant
 - Home Energy Management
 - Home Automation
---

[Degree Days](https://en.wikipedia.org/wiki/Degree_day) (or [Graaddag](https://nl.wikipedia.org/wiki/Graaddag) in Dutch) allows you to benchmark energy consumption in relation to temperature.While it definitely is a useful benchmark it falls short into taking account if people are home or not. Based on the Degree Day calculation, and the # of hours anyone is at home, I will calculate a new metric: `(DD/gas m3)*(1+(24-hours))/(1+24)`.

> #### TIP
> 
> This calculation builds on [Calculating Degree Days in Home Assistant](/2022/12/30/calculating-degree-days-in-ha/)

### Explanation

`(DD/gas m3)*(1+(24-hours))/(1+24)`

- __DD__: Degree Days, a measure of how much the outside air temperature deviates from a base temperature
- __gas m3__: Gas consumption
- __hours__: Hours of occupancy

If we break down the formula:

1. `(1 + (24-hours))`: This term adjusts the hours by adding 1 and represents a scaling factor. It ensures that the adjustment factor is at least 1, preventing the possibility of having a 0 result. 
2. `(1 + 24)`: Similarly, this part of the formula ensures there's a minimum value of 1 for the denominator.
3. `(DD/gas m3) * ...`: The main part of the formula multiplies the Degree Days to gas consumption ratio by the adjustment factor calculated from the hours. This multiplication adjusts the original ratio based on the duration for which someone was at home (and therefore the heating needs increased).

## Implementation in Home Assistant

### Occupancy and Hours at Home

Let's first start with measuring our occupancy, a binary sensor named `anyone_home` is created in Home Assistant to intuitively capture the occupancy status.

{% raw %}
```yaml
template:
  - binary_sensor:
    - name: anyone_home
      state: {{ states.person | selectattr('state','eq','home') | list | count > 0 }}
      device_class: occupancy
```
{% endraw %}

Let's calculate the hours we are at home per day, utilizing the [history_stats](https://www.home-assistant.io/integrations/history_stats/) integration, to create a sensor named `occupancy_anyone_home_daily`. The history_stats platform is employed here to calculate the total time the binary sensor has been in the `on` state within the specified time range, starting from midnight and ending at the current time. 

{% raw %}
```yaml
sensor:
  - platform: history_stats
    name: 'occupancy_anyone_home_daily'
    entity_id: "binary_sensor.anyone_home"
    state: "on"
    type: "time"
    start: "{{ now().replace(hour=0, minute=0, second=0, microsecond=0) }}"
    end: "{{ now() }}"
```
{% endraw %}

### Calculating the degree day daily and the occupancy rate

Based on the sensors `degree_day_daily` and `gas_m3_per_degree_day` as we defined in [Calculating Degree Days in Home Assistant](/2022/12/30/calculating-degree-days-in-ha/). 

{% raw %}
```yaml
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
      at: "23:59:30"
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
```
{% endraw %}

We are going to define a new sensor `gas_m3_per_degree_day_occupancy_adjusted` using a scheduled trigger in Home Assistant to calculate and update at 1s before midnight. The sensor's value is determined by multiplying the previously calculated `gas_m3_per_degree_day` by the `occupancy_rate`. The `occupancy_rate` is derived from the daily duration of occupancy tracked by the `occupancy_anyone_home_daily` sensor, divided by 24h to represent the fraction of the day with occupants present. This dynamic computation results in a metric that adjusts gas consumption in relation to Degree Days based on the occupancy of the house, providing a more refined understanding of energy usage.

{% raw %}
```yaml
template:
  - trigger:
      platform: time
      at: "23:59:59"
    sensor:
    - name: gas_m3_per_degree_day_occupancy_adjusted
      state: >
        {% set gas_m3_per_degree_day = states('sensor.gas_m3_per_degree_day') | float(0) %}
        {% set occupancy_rate = (1 + (states('sensor.occupancy_anyone_home_daily') | float(0)) / (1 + 24)) %}
        {{ gas_m3_per_degree_day * occupancy_rate }}    
      unit_of_measurement: '(m³/DD)*O'
```
{% endraw %}

### Dashboard

The dashboards visualizing Degree Days, Gas m3 per DD, and the Adjusted metric empower homeowners to make informed decisions about energy usage. The inclusion of an occupancy-adjusted metric, represented graphically, enables a more comprehensive analysis of energy efficiency and consumption patterns.

{% raw %}
```yaml
- type: custom:apexcharts-card
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
        min: 0
        max: 15
    - id: gas_per_dd
      opposite: true
      min: 0
      max: 0.8
      apex_config:
        forceNiceScale: false
        decimalsInFloat: 2
        tickAmount: 4
  color_list:
    - '#1a4c6e'
    - '#3498db'
    - '#f3721e'
  header:
    show: true
    title: Degree Days
  series:
    - entity: sensor.degree_day_daily
      name: Degree Day
      type: column
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
      group_by:
        func: last
        duration: 1d
      stroke_width: 2
      yaxis_id: gas_per_dd
    - entity: sensor.gas_m3_per_degree_day_occupancy_adjusted
      name: Adjusted
      type: line
      group_by:
        func: last
        duration: 1d
      stroke_width: 2
      yaxis_id: gas_per_dd
```
{% endraw %}

## Conclusion

In conclusion, incorporating occupancy adjustments into the Degree Day calculation within Home Assistant adds a valuable layer of precision to our energy management efforts. While Degree Days serve as an effective benchmark for gas consumption in relation to temperature, they may fall short in reflecting the real-life dynamics of a household, especially the presence or absence of occupants.

By integrating occupancy and hours at home metrics, we have created a more nuanced metric: (DD/gas m3)*hours/24. This new calculation considers the influence of human presence, providing a more accurate reflection of energy needs. The implementation in Home Assistant, including the measurement of occupancy, hours at home, and the daily Degree Day calculation, allows us to fine-tune our understanding of energy consumption.