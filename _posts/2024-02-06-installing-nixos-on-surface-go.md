---
layout: post
title: "Installing NixOS on a Surface Go 1"
categories: 
tags:
 - NixOS
---

The Microsoft Surface Go 1, with its compact size and versatility, used to be an excellent choice for users seeking a portable computing solution. Unfortunately the performance is as is it's size, limited. My goal is to have a useable tablet sized linux device. 

### Why NixOS?

[NixOS](https://nixos.org) stands out among Linux distributions for its innovative approach to package management and system configuration. Using a declarative configuration language, NixOS enables users to define their system's state in a reproducible way. This makes it an ideal choice for those who value transparency, consistency, and the ability to roll back changes.

I'm following the steps from [linux-surface](https://github.com/linux-surface/linux-surface/wiki/Installation-and-Setup) with NixOS 23.11.

### Step 1: Getting NixOS and disabling secure boot

Begin by downloading the [NixOS ISO](https://nixos.org/download#nixos-iso) from the official website, and [write this to a usb-stick](https://nixos.org/manual/nixos/stable/index.html#sec-booting-from-usb). 

Before continuing the installation process, it's unfortunately required to disable Secure Boot on your system. Secure Boot is a security feature designed to prevent the execution of unsigned or unauthorized code during the boot process. While NixOS is a trusted and reputable operating system, it does not have a signed bootloader that aligns with Secure Boot requirements. Follow the Microsoft documentation to disable [SecureBoot](https://docs.microsoft.com/en-us/windows-hardware/manufacture/desktop/disabling-secure-boot).

### Step 2: NixOS Installation

Proceed with the installation by booting from the USB drive and follow the [standard installation](https://nixos.org/manual/nixos/stable/#sec-installation-graphical) instructions. Establish a connection to your Wi-Fi network and execute the customary installation steps.

Expect a smooth installation process without encountering any issues. 

### Step 3: Optionally configure NixOS Distributed builds

Given the speed (or lack of) and the need to compile your own kernel for nixos-hardware, it's best to enable a distributed builder, follow [Enabling Distributed Builds on NixOS](/2024/02/04/nixos-enable-distributed-builds/).

### Step 4: Use nixos-hardware for full support

The [nixos-hardware](https://github.com/NixOS/nixos-hardware/) project, provides different NixOS profiles to optimize settings for different hardware. It has quite extensive guidance for Surface devices. 

Configure `nixos-hardware` in your `flake.nix`.

```nix
{
  # Add nixos-hardware to your inputs
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    nixos-hardware.url = "github:NixOS/nixos-hardware/master";
  };

  outputs = { self, nixpkgs, nixos-hardware, ... }:
  {

    nixosConfigurations = {

      ngo = nixpkgs.lib.nixosSystem {
        modules = [
          # Point this to your original configuration.
          ./computers/ngo.nix
          nixos-hardware.nixosModules.microsoft-surface-go
        ];

        # Select the target system here.
        system = "x86_64-linux";
      };
    };
  };
}
```

The new `nixos-hardware` config will likely compile a linux kernel, which on the Surface Go 1 is a very slow affair, take a look at step 3 for remote building.

### Step 5a: Enable surface-control 

[Surface Control](https://github.com/linux-surface/surface-control) controls various aspects of Microsoft Surface devices on Linux from the Command-Line. 

```nix
config.microsoft-surface.surface-control.enable = true;

# Add surface-control to your user
users.users.nathan.extraGroups = [ "wheel" "docker" "media" "networkmanager" "surface-control" ];
```

### Step 5b: Make the Camera work for Firefox / Edge

For now the camera works with `libcamera` and Firefox.

```nix
nix-shell -p libcamera -p firefox --command "libcamerify firefox"
```

> #### TODO: Will update in the near future
> I have a general idea, but will need to experiment a bit more with video4l

### Step 5c: Configure a different Display Scale

By default Gnome only lists `100%` and `200%`, to enable more options execute this as your main user once:

```sh
dconf write /org/gnome/mutter/experimental-features "['scale-monitor-framebuffer']"
```

See details inside the [nixpkgs#114514](https://github.com/NixOS/nixpkgs/issues/114514) issue and [workaround](https://github.com/NixOS/nixpkgs/issues/114514#issuecomment-786933710).

## Conclusion

Installing NixOS on my Surface Go 1 revived this little device. The setup is relatively straightforward and quite rewarding. Exploring [distributed builds](/2024/02/04/nixos-enable-distributed-builds/), and [nixos-hardware](https://github.com/NixOS/nixos-hardware/) was a nice bonus! 