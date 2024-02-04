---
layout: post
title: "Enabling Distributed Builds on NixOS"
categories: 
tags:
 - NixOS
---

NixOS, known for its declarative and functional approach to package management, provides a quite easy way to enable distributed builds. Distributed builds involve distributing the compilation workload across multiple machines, often connected over a network. NixOS achieves this by utilizing the Nix package manager's built-in support for distributed builds. 

Distributed builds involve distributing the compilation workload across multiple machines connected over a network. NixOS seamlessly achieves this by utilizing the built-in support for distributed builds in the Nix package manager. This becomes particularly valuable when you need to build a specific Nix derivation on slower devices while harnessing the computational power of a faster server. I'm following roughly the [Distributed Builds](https://nixos.wiki/wiki/Distributed_build) on the NixOS Wiki.

## Approach

The client's nix-daemon (running as root) will connect over ssh to an unpriviledged user on the server, on the server the derivation will be build and after copied back to the client.

### Step 1: Generate a ssh-key on the client

As root generate a new ssh key, with a specific name

```sh
ssh-keygen -f ~/.ssh/nixdist
```

### Step 2: Configure the host

The host is just a machine with Nix (not necessarily NixOS) installed, and a `ssh` connection. Best is to configure a dedicated user for this, and add it to the trusted `nix` users.

```nix
  users.users.nixdist = {
    isSystemUser = true;
    createHome = false;
    uid = 500;
    openssh.authorizedKeys.keys = [
      # COPY_THE_PUB_KEY_FROM_STEP1
    ];
    group = "nixdist";
    useDefaultShell = true;
  };

  users.groups.nixdist = {
    gid = 500;
  };
  
  nix.settings.trusted-users = [ "nixdist" ];
```

### Step 3: Configure the client

```nix
nix = {
  distributedBuilds = true;
  extraOptions = ''
    builders-use-substitutes = true
  '';

  # Optionally disable local building
  settings.max-jobs = 0;

  buildMachines = [ 
    {
      hostName = "buildhost.example.org";
      system = "x86_64-linux";
      maxJobs = 2;
      speedFactor = 2;
      # Supported features is badly documented, important to add these, otherwise many big packages will still get build locally.
      supportedFeatures = [ "nixos-test" "benchmark" "big-parallel" "kvm" ];
      mandatoryFeatures = [ ];
    }
  ];
};
```

### Step 4: Test if the connection is working

As root on the client, do the following

```sh
nix store ping --store ssh://nixdist@buildhost.example.org?ssh-key=/root/.ssh/nixdist
```

### Conclustions

Remote building is a great way to speed up your `nixos-rebuild switch` on older and less powerful hardware if you have a more powerful machine available. Luckily not a lot needs to be build anyway due the use of the binary cache.