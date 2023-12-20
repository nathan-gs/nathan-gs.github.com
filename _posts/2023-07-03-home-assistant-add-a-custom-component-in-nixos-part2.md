---
layout: post
title: "Home Assistant: Adding a custom_component in NixOS - part 2"
categories: 
tags:
 - NixOS
 - Home Assistant
 - IoT
---

See [part 1 for the actual setup of a custom_component in NixOS]({% post_url 2023-03-29-home-assistant-add-a-custom-component-in-nixos %}). 
During part 2 we will look how to package an additional python dependency, not part of NixOS yet.

We are going to package the [tomeko12/pyelectroluxconnect](https://github.com/tomeko12/pyelectroluxconnect) package. 

### First of all declare a `package`

```nix
{ lib
, buildPythonPackage
, requests
, beautifulsoup4
, fetchFromGitHub
}:

buildPythonPackage rec {
  pname = "pyelectroluxconnect";
  version = "0.3.19";

  src = fetchFromGitHub {
    owner = "tomeko12";
    repo = "pyelectroluxconnect";
    rev = version;
    sha256 = "1jkbmaiwad5kmryqmm83jvab8vy6kxvj2v8vn0jggsa4xm7rzgwm";
  };

  propagatedBuildInputs = [ requests beautifulsoup4 ];

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

We save this to a file `pyelectroluxconnect.nix`.

### Import the package 

In `services.home-assistant.extraPackages` we can declare extra dependencies. 

```nix
extraPackages = ps: with ps; [
  (callPackage pyelectroluxconnect.nix {})
  spotipy
];
```

In this case `spotipy` is an already packaged dependency in NixOS (ever growing), be sure to first check [search.nixos.org](https://search.nixos.org).

`(callPackage pyelectroluxconnect.nix {})` is a function call that evaluates the Nix expression in the file `pyelectroluxconnect.nix` with an empty set {} as the argument. 

### Conclusions 

Finally we apply our config using `nixos-rebuild switch` and we reload Home Assistant. 

Your Home Assistant `custom_component` with extra dependencies is now ready for use. 

