---
title: OneDrive on NixOS using Docker
tags: 
 - NixOS
 - Linux
 - Docker
---

My NAS is a Atom based Thecus running [NixOS](https://nixos.org). NixOS is a Linux distribution with a functional, as in _functional programming_, approach to package and configuration management. It contains many [packages](https://nixos.org/nixos/packages.html) and [services](https://nixos.org/nixos/options.html#). In most cases enabling a new service is as easy as adding `services.openssh.enable = true` to `/etc/nixos/configuration.nix`.<br/>
Unfortunately [skilion/onedrive](https://github.com/skilion/onedrive), a [D-lang](http://dlang.org) based [OneDrive](https://onedrive.live.com/) client, is not available on NixOS and building it required a different version of the DMD compiler. <br />
I was a bit lazy and also wanted to experiment with [docker](https://docker.com) on NixOS so I decided to run _skilion/onedrive_ as _docker_ container on _NixOS_.

> ##### NATIVE PACKAGE AVAILABLE
>
> Onedrive is now available as a native [NixOS package](https://search.nixos.org/packages?channel=23.11&show=onedrive&from=0&size=50&sort=relevance&type=packages&query=onedrive).
{: .block-warning }

## Enabling Docker in NixOS

Enabling Docker on NixOS is as easy as adding the following to `/etc/nixos/configuration.nix`:

```nix
# Enable Docker
virtualisation.docker.enable = true;

# Allow my regular user to control docker.
users.extraUsers.USER.extraGroups = [ "docker" ];
```

## Setting up _croc/onedrive_
#### Finding the right Docker Image
First of all I had to find the right docker image on [Docker Hub](https://hub.docker.com), the most popular image [kukki/docker-onedrive](https://hub.docker.com/r/kukki/docker-onedrive/) is out of date, luckily [croc/onedrive](https://hub.docker.com/r/croc/onedrive/) is more up to date.

#### Initialize the container
```bash
# All these commands are as USER, not root.
# Create some directories, where we going to store our data and some state & config
mkdir -p /home/USER/onedrive
mkdir -p /home/USER/onedrive-config

# Pull the image
docker pull croc/onedrive
```

#### Acquiring the access token

```bash
# Run it once, to acquire the access token
docker run -ti \
    --name onedrive \
    --user $UID:`id --group` \ 
    -v /home/USER/onedrive-config:/config \
    -v /home/USER/onedrive:/onedrive \
    croc/onedrive
# Line 4 is important to run the container under our own user, instead of root.
```

The container will start, authorize the application by:

* open the URL (Authorize this app visiting)
* do the necessary steps (login on onedrive, etc...)
* paste the long URL after the login


The application will start syncing, as soon as it starts, you can quit the synchronization using `CTRL-C`. 

## Running OneDrive as a SystemD service

Following some guidance of running [Docker Containers on SystemD](https://container-solutions.com/running-docker-containers-with-systemd/) I adapted this to NixOS.


```nix
systemd.services.docker-onedrive-USER = {
    # Make sure docker is started. 
    after = [ "docker.service" ];
    # To avoid race conditions
    requires = [ "docker.service" ];

    
    serviceConfig = {
        # Pulling an image might take a lot of time. 0 turns of the timeouts
        TimeoutStartSec = "0";
        # Restart policy, other relevant options are: 
        # - no
        # - on-failure 
        # Look at the man page:
        # man systemd.service
        Restart = "always";
    };

    # Let's stop the running container , remove the image.
    # The "|| true" is used because systemd expects that a everything succeeds, 
    # while failure is sometimes expected (eg. container was not running).  
    # Pull the image, ideally a version would be specified.     
    preStart = ''
${pkgs.docker}/bin/docker stop docker-onedrive-USER || true;
${pkgs.docker}/bin/docker rm docker-onedrive-USER || true;
${pkgs.docker}/bin/docker pull croc/onedrive
    '';

    # Start the container.
    script = ''
${pkgs.docker}/bin/docker run \ 
  --name docker-onedrive-USER \ 
  --user 2000:100 \
  --log-driver none \
  -v /home/USER/onedrive-config:/config \
  -v /home/USER/onedrive:/onedrive \
  croc/onedrive
    '';

    # When the systemd service stops, stop the docker container.
    preStop = ''
${pkgs.docker}/bin/docker kill docker-onedrive-USER
    '';
};

```

__L31__ `${pkgs.docker}` refers to the Nix docker package. <br />
__L32__ `--name docker-onedrive-USER` Give the running container a name. <br />
__L33__ `--user 2000:100` Set the UID & group id, use the same values as you used in [Acquiring the access token](#acquiring-the-access-token). <br />
__L34__ `--log-driver none` dockerd logs the output of a container to systemd, while we also attach the systemd service ddirectly. This avoids duplicate log messages. <br />
__L35__ `-v /home/USER/onedrive-config:/config` bind the config directory. <br />
__L36__ `-v /home/USER/onedrive:/onedrive` bind the data directory. <br />
__L37__ `croc/onedrive` the container name. <br />

#### Applying the changes we made.

NixOS configuration needs to be applied to take affect.

```bash
nixos-rebuild --switch
```

You can monitor the newly created service.
```bash
# Will show status, the latest log lines
systemd status docker-onedrive-USER.service 

# The journal contains the full history
journalctl -u docker-onedrive-USER.service 
```

{% include post_img img='terminal-systemd.png' alt="systemd status in action." %}

Restarting the service is no different than any other systemd service
```bash
systemd restart docker-onedrive-USER.service 
systemd stop docker-onedrive-USER.service 
```


If we made a mistake, it's very easy to revert to the previous NixOS _generation_.
```bash
nixos-rebuild --rollback
```

## Conclusion

> #### Warning
> 
> We are using an open-source, unofficial OneDrive client. Which might break, delete your data, corrupt your data, etc... Also trusting a third party docker container can come with risks, it might steal your credentials, etc.
{: .block-warning }

#### Conclusion

Running Docker containers on [NixOS](http://nixos.org) works as a charm, using a few steps they are managed as if they were native systemd services. NixOS allows quick rollbacks and makes configuration management tools unnecessary.

The docker container used [croc/onedrive](https://hub.docker.com/r/croc/onedrive/) could be made a lot smaller, by using the [alpine](https://hub.docker.com/_/alpine/) image, and should be versioned.

The NixOS community is very active, mostly on [GitHub](https://github.com/nixos/nixpkgs) and the [mailing list](https://groups.google.com/forum/#!forum/nix-devel).

In conclusion having OneDrive on my NAS means I can integrate it with my backup and snapshot flows.