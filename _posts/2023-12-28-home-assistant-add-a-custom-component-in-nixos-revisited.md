---
layout: post
title: "Home Assistant: Adding a custom_component in NixOS - revisited"
categories: 
tags:
 - NixOS
 - Home Assistant
 - IoT
---

Since NixOS 23.11 there is a [new way of packaging Home Assistant custom components](https://github.com/NixOS/nixpkgs/tree/master/pkgs/servers/home-assistant/custom-components), making some of the work written in [earlier](/2023/03/29/home-assistant-add-a-custom-component-in-nixos/) [blog](/2023/07/03/home-assistant-add-a-custom-component-in-nixos-part2/) posts irrelevant. Let's repackage the [electrolux_status](https://github.com/mauro-midolo/homeassistant_electrolux_status) and it's dependency [tomeko12/pyelectroluxconnect](https://github.com/tomeko12/pyelectroluxconnect). 

If you're looking for a way to add custom components to your [Home Assistant](https://home-assistant.io/) setup, then NixOS has a good solution. [NixOS](https://nixos.org) is an open source Linux distribution that is designed to be _functional_. This can be a good alternative to have a more declarative configuration in contrast to [HACS](https://hacs.xyz/). 

### First of all let's create a package for the dependency pyElectroluxConnect

Unfortunately `pyelectroluxconnect` is not part of the NixOS packages yet, so we need to do it ourselves.

```nix
{ stdenv, pkgs, lib, buildPythonPackage, fetchFromGitHub }:

buildPythonPackage rec {
  pname = "pyelectroluxconnect";
  version = "0.3.20";

  src = fetchFromGitHub {
    owner = "tomeko12";
    repo = "pyelectroluxconnect";
    rev = version;
    sha256 = "sha256-5eTHJsE5Jof5WSZFkf8/1UQafpgxpGTPuDWQMENgAG0=";
  };

  propagatedBuildInputs = [
    pkgs.python311Packages.requests
    pkgs.python311Packages.beautifulsoup4
  ];

  doCheck = false;

  pythonImportsCheck = [ "pyelectroluxconnect" ];

  meta = with lib; {
    description = "Python client package to communicate with the Electrolux Connectivity Platform";
    homepage = "https://github.com/tomeko12/pyelectroluxconnect";
    license = licenses.asl20;
    maintainers = with maintainers; [ nathan-gs ];
  };
}
```

This package setup is very basic, we use the [buildPythonPackage](https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md#building-packages-and-applications-building-packages-and-applications) function, it uses `fetchFromGitHub` to retrieve the latest release. We can retrieve the `sha256` hash using the following cli `nix-shell -p nix-prefetch-github --run "nix-prefetch-github --rev 0.3.20 tomeko12 pyelectroluxconnect"` which fetches the git repo, and figures out the sha256 of the repo. 

We declare the [requests](https://search.nixos.org/packages?channel=23.11&show=python311Packages.requests&from=0&size=50&sort=relevance&type=packages&query=requests) and [beautifulsoup4](https://search.nixos.org/packages?channel=23.11&from=0&size=50&sort=relevance&type=packages&query=beautifulsoup4) dependencies, these were already part of NixOS. 

### Creating a custom component from `electrolux_status`

Using the new [buildHomeAssistantComponent](https://github.com/NixOS/nixpkgs/tree/master/pkgs/servers/home-assistant/custom-components) we declare a package. 

```nix
{ stdenv, pkgs, fetchFromGitHub, buildHomeAssistantComponent, pyelectroluxconnect }:

buildHomeAssistantComponent rec {

  owner = "mauro-modolo";
  domain = "electrolux_status";
  version = "4.1.0";

  src = fetchFromGitHub {
    owner = "mauro-midolo";
    repo = "homeassistant_electrolux_status";
    rev = "v${version}";
    sha256 = "sha256-85p4eG0ePW2EI6vzksSbWLhNfkdrzCiu1KChuPwSobU=";
  };

  propagatedBuildInputs = [
    pyelectroluxconnect
  ];

}
```

Note the `pyelectroluxconnect` dependency, both at the top as in the `propagatedBuildInputs`.

### Adding the `electrolux_status` component to Home Assistant

Since NixOS 23.11 there is a new [services.home-assistant.customComponents](https://search.nixos.org/options?channel=23.11&show=services.home-assistant.customComponents&from=0&size=50&sort=relevance&type=packages&query=home-assistant.) option. There is a [small list of already packaged components](https://search.nixos.org/packages?channel=unstable&from=0&size=50&sort=relevance&type=packages&query=home-assistant-custom-components) in NixOS unstable.

```nix
services.home-assistant.customComponents = [
    (pkgs.callPackage ../pkgs/home-assistant/custom_components/solis-sensor.nix {})
    (pkgs.callPackage ../pkgs/home-assistant/custom_components/electrolux-status.nix {
      pyelectroluxconnect = (pkgs.python311Packages.callPackage ../pkgs/python/pyelectroluxconnect.nix {});
    })
  ];
```

I'm adding 2 custom components, `solis-sensor` only depending on packages already part of NixOS and the just packaged `electrolux_status` component. For the `electrolux_status` component, we need to inject the `pyelectroluxconnect` package.

> ##### NOTE
>
> In an earlier version I leveraged an `activationScript` to make symlinks to the correct packages, this is no longer necessary and will no longer work.
{: .block-note }


### Conclusions 

Finally we apply our config using `nixos-rebuild switch` and we reload Home Assistant. If you want to take a look at more examples, and a slightly more extensive Home Assistant in NixOS setup, take a look at [nathan-gs/nix-conf](https://github.com/nathan-gs/nix-conf). 

Your Home Assistant `custom_component` is now ready for use. 