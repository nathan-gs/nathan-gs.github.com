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

{% highlight yaml linenos %}
{% raw %}
utility_meter:
  electricity_delivery_15m:
    source: sensor.electricity_delivery
    cron: "*/15 * * * *"

{% endraw %}
{% endhighlight %}

#### Sidenote for Peak & Offpeak

If you receive data in `peak` & `offpeak` measurements; best to sum them before:
{% highlight yaml linenos %}
{% raw %}
template:
- sensor:
  - name: electricity_delivery
  unit_of_measurement: "kWh"
  state: "{{ ( states('sensor.electricity_peak_delivery') | float ) + ( states('sensor.electricity_offpeak_delivery') | float ) }}";
{% endraw %}
{% endhighlight %}

### Calculate the 15m power

We now have the numbers in kWh (energy) but we need to convert to kW (power); we do this by multiplying by 4 (1h per quarter).

{% highlight yaml linenos %}
{% raw %}
template:
- sensor:
  - name: electricity_delivery_power_15m
  unit_of_measurement: "kW"
  state: "{{ states('sensor.electricity_delivery_15m')  * 4 | float }}";
{% endraw %}
{% endhighlight %}

### Calculate the daily and monthly max

To calculate the 15m max for the day & month, we are using the following template, with a time_pattern trigger.

{% highlight yaml linenos %}
{% raw %}
template:
  trigger:
    platform: time_pattern
    minutes: "/15"
  sensor:
  - name: electricity_delivery_power_daily_15m_max
    state: >
      {% if is_number(states('sensor.electricity_delivery_power_daily_15m_max')) %}
        {% if ((now().hour == 0) and (now().minute < 15)) %}
          {{ states('sensor.electricity_delivery_power_15m') | float }}
        {% else %}
          {% if ((states('sensor.electricity_delivery_power_daily_15m_max') | float) < (states('sensor.electricity_delivery_power_15m')) | float) %}
            {{ states('sensor.electricity_delivery_power_15m') or 0 | float }}
          {% else %}
            {{ states('sensor.electricity_delivery_power_daily_15m_max') | float }} 
          {% endif %}
        {% endif %}
      {% else %}
        0
      {% endif %}
    unit_of_measurement: 'kW'
  - name: electricity_delivery_power_monthly_15m_max
    state: >
      {% if is_number(states('sensor.electricity_delivery_power_monthly_15m_max')) %}
        {% if ((now().day == 1) and (now().hour == 0) and (now().minute < 15)) %}
          {{ states('sensor.electricity_delivery_power_15m') | float }}
        {% else %}
          {% if ((states('sensor.electricity_delivery_power_monthly_15m_max') | float) < (states('sensor.electricity_delivery_power_15m')) | float) %}
            {{ states('sensor.electricity_delivery_power_15m') or 0 | float }}
          {% else %}
            {{ states('sensor.electricity_delivery_power_monthly_15m_max') | float }} 
          {% endif %}
        {% endif %}
      {% else %}
        0
      {% endif %}
    unit_of_measurement: 'kW'
    
{% endraw %}
{% endhighlight %}

### Visualizing

Making use of [Apexcharts Card](https://github.com/RomRider/apexcharts-card), visualizing some elements 

{% highlight yaml linenos %}
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
        name: 15m
        stroke_width: 2
        transform: return x * 1000;
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
        name: day
        stroke_width: 4
        transform: return x * 1000;
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
{% endhighlight %}

{% include post_img img="measurements1.png" alt="Measurements inside Home Assistant" width="30%" %}
{% include post_img img="measurements-day.png" alt="Measurements inside Home Assistant" width="30%" %}
{% include post_img img="measurements-month.png" alt="Measurements inside Home Assistant" width="30%" %}

### Triggering a warning on too much power use

Let's create a binary_sensor to trigger if we are using too much power. The following code will trigger if we consume more than 2800W for more than 2m.

{% highlight yaml linenos %}
{% raw %}
template:
- binary_sensor:
  - name: electricity_delivery_power_max_threshold_reached
    delay_on: 00:02:00
    delay_off: 00:01:00
    state: "{{ states('sensor.electricity_delivery') | float > 2800 }}"
{% endraw %}
{% endhighlight %}

### Final notes

Initially I started using the statistics model, however using `utility_meter` is likely more accurate.
