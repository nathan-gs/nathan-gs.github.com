---
title: NixOS on Microsoft Windows 11 using WSL2
tags: 
- NixOS
- Windows Subsystem for Linux
- Microsoft Windows
- Linux
excerpt: >
  <img src="/assets/post/2019/04/12/nix-on-windows/nixos.png" alt="Nix" height="100" width="100" style="float: left; padding: 30px;" /> [NixOS](https://nixos.org) is my go-to Linux distribution, providing a Functional approach to packaging & configuration management. 

  There are a couple of steps to enable NixOS on top of the [Windows Subsystem for Linux 2](https://learn.microsoft.com/en-us/windows/wsl/).

image: /assets/post/2019/04/12/nix-on-windows/nixos.png
---

<img src="/assets/post/2019/04/12/nix-on-windows/nixos.png" alt="Nix" height="100" width="100" style="float: left; padding: 30px;" /> [NixOS](https://nixos.org) is my go-to Linux distribution, providing a Functional approach to packaging & configuration management. 

There are a couple of steps to enable NixOS on top of the [Windows Subsystem for Linux 2](https://learn.microsoft.com/en-us/windows/wsl/). Running native NixOS is a better approach then to use Nix on Windows (using Ubuntu).
<br style="clear: both;">

> ##### NOTE
>
> An earlier version was published as [Nix on Windows 10](/2019/04/12/nix-on-windows) in 2019.
{: .block-note }

#### Enable WSL if you haven't done so.

```powershell
wsl --install --no-distribution
```
The `--no-distribution` just activates wsl2, see [wsl docs](https://learn.microsoft.com/en-us/windows/wsl/basic-commands#install).

Reboot your pc.

#### Import & Install NixOS on WSL2

We are going to use the [nix-community/NixOS-WSL](https://github.com/nix-community/NixOS-WSL) base.

1. Download the [latest release](https://github.com/nix-community/NixOS-WSL/releases/latest)

2. Import the image to WSL

    ```powershell
    wsl --import NixOS %userprofile%\AppData\Local\WSL\NixOS .\Downloads\NixOS\nixos-wsl.tar.gz
    ```

    `%userprofile%\AppData\Local\WSL\NixOS` is an arbitrary location, adjust to your needs.

3. Run NixOS 
  
    ```powershell
    wsl -d NixOS
    ```

4. Optionally make NixOS the default

    ```powershell
    wsl -s NixOS
    ```

#### Our first run

1. Run a `nix-channel` update as `root`

    ```bash
    sudo nix-channel --update
    ```

2. You can start using NixOS

    e.g. `nix-shell -p htop`


Definitely check 
    
  - [nixos.org quick start](https://nixos.org/manual/nix/stable/quick-start.html)