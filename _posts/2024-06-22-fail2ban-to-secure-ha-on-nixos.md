---
layout: post
title: "Using fail2ban to secure Home Assistant on NixOS"
categories: 
tags:
 - Home Assistant
 - NixOS
---

[Home Assistant](/tags/home-assistant) is a popular open-source platform for home automation, and securing its login attempts is crucial to ensure the safety of your smart home setup. One effective way to enhance security is by using [Fail2ban](https://github.com/fail2ban/fail2ban), a tool that monitors log files and bans IP addresses that show malicious signs, such as too many password failures. In this blog post, we will guide you through setting up Fail2ban to monitor Home Assistant login attempts using journald on NixOS. 

### Prerequisites

Before we start, make sure you have the following:

- A running instance of Home Assistant on NixOS
- A working Fail2ban
- Configuring of [banning inside Home Assistant](https://www.home-assistant.io/integrations/http/#ip_ban_enabled)

## Create a filter for Home Assistant

Based on the [Home Assistant fail2ban docs](https://www.home-assistant.io/integrations/fail2ban/#create-a-filter-for-the-home-assistant-jail) we create a new filter:

```ini
[Definition]
failregex = ^.* \[homeassistant\.components\.http\.ban\] Login attempt or request with invalid authentication from <HOST>.*$

ignoreregex =

journalmatch = _SYSTEMD_UNIT=home-assistant.service + _COMM=home-assistant

datepattern = {^LN-BEG}
```

### Testing the fail2ban regex

Fail2ban provides a `fail2ban-regex` program, to test your regex:

```sh
fail2ban-regex \
  "hass[3519397]: 2024-06-21 07:08:44.470 WARNING (MainThread) [homeassistant.components.http.ban] Login attempt or request with invalid authentication from bad-actor.example.org (128.66.0.2). Requested URL: '/'. (Mozilla/5.0 (Linux i570 x86_64) Gecko/20130401 Firefox/45.6)" \
  '^.* \[homeassistant\.components\.http\.ban\] Login attempt or request with invalid authentication from <HOST> .*$'
```

This provides the following feedback:

```
Running tests
=============

Use   failregex line : ^.* \[homeassistant\.components\.http\.ban\] Login...
Use      single line : hass[3519397]: 2024-06-21 07:08:44.470 WARNING (Ma...


Results
=======

Failregex: 1 total
|-  #) [# of hits] regular expression
|   1) [1] ^.* \[homeassistant\.components\.http\.ban\] Login attempt or request with invalid authentication from <HOST> .*$
`-

Ignoreregex: 0 total

Date template hits:
|- [# of hits] date format
|  [1] ExYear(?P<_sep>[-/.])Month(?P=_sep)Day(?:T|  ?)24hour:Minute:Second(?:[.,]Microseconds)?(?:\s*Zone offset)?
`-

Lines: 1 lines, 0 ignored, 1 matched, 0 missed
[processed in 0.05 sec]

```

### Deviations from Home Assistant documentation

We are retrieving the log from `journald` instead of the log-file, in addition we do a closer check of the correct component.

### File Location

If using nixos, include it in your config repository, otherwise create it directly in `/etc/fail2ban/filter.d/homeassistant.conf`.



## Enable the filter on NixOS

```nix
environment.etc."fail2ban/filter.d/home-assistant.conf".source = ./fail2ban/home-assistant.conf;

services.fail2ban.jails = {
  home-assistant = {
    filter = "home-assistant";
    enabled = true;
  };
};
```

And apply the config `nixos-rebuild switch`.

### Verify the configuration

You can verify that your Fail2ban jail is working correctly by checking the status:

```
sudo fail2ban-client status homeassistant  
```

This command should show you the status of the homeassistant jail and any banned IP addresses.

## Conclusion

By following these steps, you have successfully configured Fail2ban to monitor and ban IP addresses with failed login attempts to Home Assistant on NixOS. This setup helps enhance the security of your Home Assistant instance, protecting it from unauthorized access.