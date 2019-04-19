---
layout: post
title: Using Jekyll and Nix to blog
tags: 
 - nixos
 - jekyll
 - nix
 - github pages
 - github
---

For my blogging I use [Jekyll](https://jekyllrb.com) and [Nix](https://nixos.org/nix), hosted on [Github Pages](https://pages.github.com/). Now that we have a [working Nix on Windows setup]({% post_url 2019-04-12-nix-on-windows %}), we can start to blog. 

### Gemfile

It all starts with a simple, [Gemfile](https://github.com/nathan-gs/nathan-gs.github.com/blob/master/Gemfile) where I specify the dependencies needed. 
It should look something like this:

```ruby
source 'https://rubygems.org'
gem 'github-pages', group: :jekyll_plugins
gem "minima"
gem 'jekyll-seo-tag'
gem 'jekyll-paginate'
```

### Bundler updating, locking and downloading dependencies via [bundix](https://github.com/manveru/bundix)

1. Update all gems to the latest allowed version: `bundler update`
1. Lock `Gemfile.lock`, using `bundler lock`
1. Package all dependencies: `bundler package --no-install --path vendor`
1. Apply [bundix](https://github.com/manveru/bundix): `bundix`
    Bundix is going to generate a `gemset.nix`, and mode the gems into the _nix store_.
1. Cleanup: `rm -rf vendor/*`

Bringing this all together into a [simple script](https://github.com/nathan-gs/nathan-gs.github.com/blob/master/bin/initialize-or-update.sh):

```bash
#!/usr/bin/env bash

nix-shell -p bundler -p bundix --run 'bundler update; bundler lock; bundler package --no-install --path vendor; bundix; rm -rf vendor'

echo "You can now run nix-shell"
```

The script is idempotent, so you can run this as many times as needed. Using `nix-shell -p PACKAGENAME` you obtain a new shell with the package, and all it's dependencies downloaded, installed and added to the path. Once you exit the shell it is as it was never installed (although the package and it's dependencies are still in the `/nix/store`).

### Running Jekyll

We can now have a `default.nix` with all the right links to the *bundixed* packages, something similar to this:

```nix
with import <nixpkgs> { };

let jekyll_env = bundlerEnv rec {
    name = "jekyll_env";
    inherit ruby;
    gemfile = ./Gemfile;
    lockfile = ./Gemfile.lock;
    gemset = ./gemset.nix;
  };
in
  stdenv.mkDerivation rec {
    name = "nathan.gs";
    buildInputs = [ jekyll_env bundler ruby ];

    shellHook = ''
      exec ${jekyll_env}/bin/jekyll serve --watch
    '';
  }
```

Now you can just run `nix-shell` to have a working jekyll environment.

{% include post_img img="nix-shell.png" alt="Jekyll using Nix" %}


### Credits

* [Building a Jekyll Environment with NixOS](https://stesie.github.io/2016/08/nixos-github-pages-env) by [Stefan Siegl](https://stesie.github.io/)
    
    Main difference is that it's no longer necessary to remove `, group: :jekyll_plugins` from your `Gemfile`
