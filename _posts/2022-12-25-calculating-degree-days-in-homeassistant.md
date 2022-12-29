---
layout: post
title: "Calculating Degree Days in Home Assistant"
categories: []
tags:
 - Home Assistant
 - Energy
 - Automation
---

Calculating [Degree Days](https://en.wikipedia.org/wiki/Degree_day) (or [Graaddag](https://nl.wikipedia.org/wiki/Graaddag) in Dutch) allows you to benchmark gas consumption in relation to temperature. The formula is quite simple, it uses as reference temperature 18°C minus the average temperature of the day, minimalized on 0°C.

For this we will use the `statistics` and template sensors. 

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

