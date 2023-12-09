---
layout: post
title: "NixOS: adding a set of helper functions to Nix and importing these"
categories: 
tags:
 - NixOS
excerpt: >
    In my HomeAssistant setup, I rely on NixOS to streamline configuration management. To enhance the efficiency of writing Home Assistant YAML files, I sought a way to integrate custom helper functions seamlessly. My objective was to include 'ha' as an argument at the beginning of my configuration files, allowing for a more modular and organized setup.

    My goal is to be able to include `ha` as argument at the top of my file:
    ```nix
    { config, lib, pkgs, ha, ... }:
    ```
    
---

In my HomeAssistant setup, I rely on NixOS to streamline configuration management. To enhance the efficiency of writing Home Assistant YAML files, I sought a way to integrate custom helper functions seamlessly. My objective was to include 'ha' as an argument at the beginning of my configuration files, allowing for a more modular and organized setup.

My goal is to be able to include `ha` as argument at the top of my file:
```nix
{ config, lib, pkgs, ha, ... }:
```

<!--more-->

### Exploring some options

After exploring some capabilities in `flake.nix` (and failing), seeing [What’s the best way to add my own utility functions? on Nixos Discourse](https://discourse.nixos.org/t/whats-the-best-way-to-add-my-own-utility-functions/11576).

### Discovering the solution

Eventually, I stumbled upon the `_module.args` option, which was detailed in a [stackoverflow/nixos-module-imports-with-arguments](https://stackoverflow.com/a/47713963).

### Implementation

To implement this solution, I added the following snippet to any location in my `configuration.nix` file:

```nix
 _module.args.ha = import ../lib/ha.nix { lib = lib; };
```
Now, I can incorporate my custom helper functions from  [lib/ha.nix](https://github.com/nathan-gs/nix-conf/blob/main/lib/ha.nix) into any module as if they were native to the configuration.

For example, with this, I can do the following to switch on & off my Sonos soundbar:

```nix
{ config, pkgs, lib, ha, ... }:
{

  services.home-assistant.config = {
    "automation manual" = [ ]
      ++ (ha.automationOnOff "floor0/living/media/sonos"
      {
        triggersOn = [
          (ha.trigger.on "binary_sensor.floor0_living_appletv_woonkamer")          
        ];
        conditionsOn = [
          (ha.condition.time_after "10:30:00")
        ];
        triggersOff = [
          (ha.trigger.off_for "binary_sensor.floor0_living_appletv_woonkamer" "00:02:00")
        ];
        entities = [ "switch.floor0_living_plug_sonos_rear" ];
      });
  };
}
```


### Considerations

It's essential to note that while this method currently works with NixOS 23.11, it relies on the internal `_module`, which is considered both _internal_ and _fragile_. As mentioned in the [NixOS/nixpkgs](https://github.com/NixOS/nixpkgs/blob/695027f61c702ea0de6baa3122b282d672fede09/lib/modules.nix#L43), this aspect may be subject to changes in future releases.

### Conclusion

By leveraging NixOS and custom helper functions, I've significantly improved the efficiency of my HomeAssistant YAML configuration. While caution is advised due to the use of internal features, this approach has proven effective for my current setup on NixOS 23.11. Keep an eye on updates and changes to ensure compatibility with future releases.