---
layout: post
title: "Home Assistant: Adding a custom_component in NixOS - part 1"
categories: 
tags:
 - NixOS
 - Home Assistant
 - Home Automation
---

If you're looking for a way to add custom components to your [Home Assistant](https://home-assistant.io/) setup, then NixOS has a good solution. [NixOS](https://nixos.org) is an open source Linux distribution that is designed to be _functional_. This can be a good alternative to have a more declarative configuration in contrast to [HACS](https://hacs.xyz/). 

> ##### WARNING
>
> This approach stopped working in NixOS 23.11, take a look at [Home Assistant: Adding a custom_component in NixOS - revisited](/2023/12/28/home-assistant-add-a-custom-component-in-nixos-revisited) for a new and more native approach. 
{: .block-warning }

I'm using the [hultenvp/solis-sensor](https://github.com/hultenvp/solis-sensor) HA component as an example here.

### First of all declare a `package`

```nix
{ stdenv, pkgs, fetchFromGitHub }:

stdenv.mkDerivation rec {
  name = "ha-solis-sensor";
  src = fetchFromGitHub {
    owner = "hultenvp";
    repo = "solis-sensor";
    rev = "v3.3.2";
    sha256 = "uPGqK6qyglz9aIU3iV/VQbwXXsaBw4HyW7LqtP/xnMg=";
  };

  
  installPhase = ''cp -a custom_components/solis $out'';
}
```

This package setup is very basic, it uses `fetchFromGitHub` to retrieve the latest release. We can retrieve the `sha256` hash using the following cli `nix-shell -p nix-prefetch-github --run "nix-prefetch-github --rev v3.3.2 hultenvp solis-sensor"` which fetches the git repo, and figures out the sha256 of the repo. 

By default the nix package will run `make install` to install to the correct location, however since we just want to copy the right files we can override this: 

`installPhase = ''cp -a custom_components/solis $out'';`

### Import the package

Home Assistant expects custom packages to be installed under `/var/lib/hass/custom_components/{component_name}`. 

We can leverage an `activationScript` to install and symlink the package:

```nix
  system.activationScripts.ha-solis.text = ''
    mkdir -p "/var/lib/hass/custom_components"
    ln -sfn "${(pkgs.callPackage ./apps/ha-solis-sensor.nix {})}" "/var/lib/hass/custom_components/solis"
  '';  
```

We directly use `callPackage` to make sure it's available, this will behind the scenes download and install the package in the nix store under `/nix/store`. Do note the `ln -sfn`, otherwise [we won't overwrite the symlink](https://unix.stackexchange.com/questions/207294/create-symlink-overwrite-if-one-exists/207296#207296) but add it to the directory.

### Conclusions 

Finally we apply our config using `nixos-rebuild switch` and we reload Home Assistant. 

Your Home Assistant `custom_component` is now ready for use. 

#### Part 2

In [Part 2]({% post_url 2023-07-03-home-assistant-add-a-custom-component-in-nixos-part2 %}) we will take a look at adding an extra dependency which hasn't been packed yet. 
) we will take a look at adding an extra dependency which hasn't been packed yet. 

#### In the future

In the future this functionality will likely be fully integrated in the [Home Assistant](https://search.nixos.org/options?channel=22.11&from=0&size=50&sort=relevance&type=packages&query=home-assistant) NixOS module, see the following PR [NixOS/nixpkgs/pull/160346](https://github.com/NixOS/nixpkgs/pull/160346).