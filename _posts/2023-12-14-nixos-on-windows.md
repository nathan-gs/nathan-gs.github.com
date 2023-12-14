---
title: NixOS on Microsoft Windows 11 using WSL2
tags: 
 - nixos
 - windows
 - nix
 - wsl
 - windows subsystem for linux
 - linux
excerpt: >
  <img src="/assets/post/2019/04/12/nix-on-windows/nixos.png" alt="Nix" height="100" width="100" style="float: left; padding: 30px;" /> [NixOS](https://nixos.org) is my go-to Linux distribution, providing a Functional approach to packaging & configuration management. 

  There are a couple of steps to enable NixOS on top of the [Windows Subsystem for Linux 2](https://learn.microsoft.com/en-us/windows/wsl/).
  <p style="page-break-after: always;">&nbsp;</p>

image: /assets/post/2019/04/12/nix-on-windows/nixos.png
---


> [!NOTE]
> An earlier version was published as [Nix on Windows 10 (2019)](/2019/04/12/nix-on-windows).


<img src="/assets/post/2019/04/12/nix-on-windows/nixos.png" alt="Nix" height="100" width="100" style="float: left; padding: 30px;" /> [NixOS](https://nixos.org) is my go-to Linux distribution, providing a Functional approach to packaging & configuration management. 

There are a couple of steps to enable NixOS on top of the [Windows Subsystem for Linux 2](https://learn.microsoft.com/en-us/windows/wsl/).

<p style="page-break-after: always;">&nbsp;</p>

1. Enable WSL if you haven't done so.
```powershell
wsl --install --no-distribution
```
The `--no-distribution` just activates wsl2.
Reboot your pc.

2. We are going to use the [nix-community/NixOS-WSL](https://github.com/nix-community/NixOS-WSL) base.

3. Follow the instructions;

    1. Download the [latest release](https://github.com/nix-community/NixOS-WSL/releases/latest)

    2. Import the image to WSL

    ```powershell
    wsl --import NixOS .\Downloads\NixOS\nixos-wsl.tar.gz
    ```
    
    3. Run NixOS 
      
      ```powershell
      wsl -d NixOS
      ```

    4. Optionally make NixOS the default

      ```powershell
      wsl -s NixOS
      ```

4. A good first run within NixOS

    1. Run a `nix-channel` update as `root`

      ```bash
      sudo nix-channel --update
      ```

    2. You can start using NixOS

      e.g. `nix-shell -p htop`

    3. Definitely check 
    
      - [nixos.org quickstart](https://nixos.org/manual/nix/stable/quick-start.html)