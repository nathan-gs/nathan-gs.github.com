---
layout: post
title: "NixOS: adding a set of helper functions to Nix and importing these"
categories: 
tags:
 - NixOS
---

For my HomeAssistant setup I leverage NixOS and wanted to create certain helper functions in aiding writing HA yaml more efficiently. 

My goal is to be able to include `ha` as argument at the top of my file:
```nix
{ config, lib, pkgs, ha, ... }:
```

After exploring some capabilities in `flake.nix` (and failing), seeing [What’s the best way to add my own utility functions? on Nixos Discourse](https://discourse.nixos.org/t/whats-the-best-way-to-add-my-own-utility-functions/11576).

I came across the ` _module.args` option at [stackoverflow/nixos-module-imports-with-arguments](https://stackoverflow.com/a/47713963).

I just add the following to any spot in `configuration.nix`:

```nix
 _module.args.ha = import ../lib/ha.nix { lib = lib; };
```

The result I can use my [lib/ha.nix](https://github.com/nathan-gs/nix-conf/blob/main/lib/ha.nix) helper functions inside any module, as if it were native. 

A small word of warning, this works with NixOS 23.11, but it uses the internal `_module` which is _internal_ and _fragile_, as you can read in the [NixOS/nixpkgs](https://github.com/NixOS/nixpkgs/blob/695027f61c702ea0de6baa3122b282d672fede09/lib/modules.nix#L43).

