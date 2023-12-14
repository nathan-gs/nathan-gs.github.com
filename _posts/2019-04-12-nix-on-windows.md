---
title: Nix on Microsoft Windows 10
tags: 
 - nixos
 - windows
 - nix
 - wsl
 - windows subsystem for linux
 - linux
excerpt: >
   <img src="/assets/post/2019/04/12/nix-on-windows/nixos.png" alt="Nix" height="100" width="100" style="float: left; margin: 10px" /> 
   Using [nix](https://nixos.org/nix), the _functional_ package manager on the [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/about) is fairly easy, however a couple of additional steps need to be done. We will be using Ubuntu from the Microsoft Store, apply some workarounds, and install *nix*. Nix is also the basis of [NixOS](https://nixos.org) a purely functional linux distribution.
   
   
   <br />
   <img src="/assets/post/2019/04/12/nix-on-windows/nix-on-windows.png" alt="Nix on Windows 10" />

image: /assets/post/2019/04/12/nix-on-windows/nixos.png
---

> [!WARNING]
> An update is published, [using wsl2 & NixOS](/2023/12/14/nixos-on-windows)


<img src="/assets/post/2019/04/12/nix-on-windows/nixos.png" alt="Nix" height="100" width="100" style="float: left; padding: 30px;" />  Using [nix](https://nixos.org/nix), the _functional_ package manager on the [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/about) is fairly easy, however a couple of additional steps need to be done. 

1. Enable WSL, see [Windows Subsystem for Linux Installation Guide for Windows 10](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
2. Pick Ubuntu inside the Microsoft Store
3. Update Ubuntu
  ```bash
    sudo apt update
    sudo apt upgrade
  ```
4. Create the `/etc/nix` directory
  ```bash
  mkdir -p /etc/nix
  ```
5. Create & edit `/etc/nix/nix.conf`, add following items:
  ```bash
    sandbox = false
    use-sqlite-wal = false
  ```
  Unfortunately there are still some things that require this workaround:
    
    * `sandbox = false` is following bug: [NixOS/nix#2651: Installing Nix fails on Ubuntu 18.04.1 LTS Error: cloning builder process: Invalid argument](https://github.com/NixOS/nix/issues/2651)
    * `use-sqlite-wal = false` are following bugs: [NixOS/nix#2292: WSL Nix installation db.sqlite is busy](https://github.com/NixOS/nix/issues/2292) and [NixOS/nix#1203: nix-shell under Windows WSL is broken](https://github.com/NixOS/nix/issues/1203)

6. Install nix:
  ```bash
    curl https://nixos.org/nix/install | sh
  ```

You are done, let's test it:
```bash
  nix-shell -p busybox --run 'echo $PATH'
```

{% include post_img img="nix-on-windows.png" alt="Nix on Windows" %}


Some extra useful links:
* [tweag.io: Nix on the Windows Subsystem for Linux](https://www.tweag.io/posts/2017-11-10-nix-on-wsl.html)
* [nixos.org/nix](https://nixos.org/nix/)