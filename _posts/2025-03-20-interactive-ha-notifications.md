---
layout: post
title: "Interactive Home Assistant notifications: Charge your car with a Tap"
categories: 
tags:
 - Home Assistant
 - Home Automation
---

Home Assistant is an incredibly powerful platform for automating your home, and one of its standout features is the ability to create interactive notifications. Imagine this: it's 21:30, you're home, and your electric car isn't charging yet. Home Assistant can send a notification to your phone asking if you'd like to start charging at a specific time—and with a single tap, you can confirm it. In this blog post, I'll walk you through setting up a notification with an actionable response to control your car charger (and potentially other tasks) using Home Assistant automations.

We'll create two automations:
1. One to send a notification asking if you want to charge your car.
2. Another to handle your response and take action accordingly.

### Automation 1: Sending the Notification

This first automation triggers every evening at 21:30, checks if someone is home and if the car charger is off, and then sends a notification to your phone with an action button.

```yaml
automation:
  - id: 'system/car_charger.ask'
    alias: 'Ask to Charge Car at 21:30'
    trigger:
      - platform: time
        at: '21:30'
    condition:
      - condition: state
        entity_id: 'binary_sensor.anyone_home'
        state: 'on'
      - condition: state
        entity_id: 'switch.car_charger'
        state: 'off'
    action:
      - service: notify.notify
        data:
          title: "Enable car charger?"
          message: "Enable car charger?"
          data:
            tag: "car_charger_ask"
            persistent: true
            sticky: true
            actions:
              - action: "CAR_CHARGE_ON"
                title: "Yes, charge"
```

**What's Happening Here?**
- **Trigger**: The automation runs daily at (`21:30`).
- **Conditions**: 
  - Checks if anyone is home using `binary_sensor.anyone_home`.
  - Ensures the car charger (`switch.car_charger`) is off.
- **Action**: Sends a notification to your phone via the `notify.notify` service (you can also send it to a specific phone, using `notify.mobile_app_PHONE_NAME`).
  - The title and message display a message, you can use templates here.
  - The notification is persistent and sticky, meaning it won't disappear until you act on it (depending on OS).
  - It includes an action button labeled “Yes, charge” which sends the `CAR_CHARGE_ON` event when tapped.

#### Automation 2: Handling the Notification Response

The second automation listens for the action you take on the notification and responds by clearing the notification and enabling the charger.

```yaml
automation:
  - id: 'system/car_charger.ask_action'
    alias: 'Handle Car Charger Notification Action'
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "CAR_CHARGE_ON"
    action:
      - service: notify.notify
        data:
          message: "clear_notification"
          data:
            tag: "car_charger_ask"
      - service: switch.turn_on
        target:
          entity_id: switch.car_charger
```

**What's Happening Here?**
- **Trigger**: This automation listens for a `mobile_app_notification_action` event, specifically when you tap the “Yes, charge” button (`CAR_CHARGE_ON`).
- **Actions**:
  - Clears the persistent notification using the `clear_notification` message and the `car_charger_ask` tag.
  - Turns on an `switch` entity called `car_charger`.

## Conclusion

With these automations, you've got a smart, interactive way to manage your car charging in Home Assistant. The notification keeps you in control without needing to open the app, and the actions make it seamless to respond. Plus, this framework is flexible—swap out the car charger for lights, thermostats, or anything else you want to control with a tap.

Try it out, tweak it to your needs, and let Home Assistant make your life a little easier! What other tasks would you automate with actionable notifications? Let me know in the comments!