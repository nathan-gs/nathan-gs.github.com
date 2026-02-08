{ pkgs, lib, config, inputs, ... }:

{  

  # https://devenv.sh/packages/
  packages = [ 
    pkgs.git 
    pkgs.rubyPackages.jekyll 
    pkgs.rubyPackages.jekyll-seo-tag 
    pkgs.rubyPackages.jekyll-paginate 
    pkgs.rubyPackages.minima
    pkgs.rubyPackages.webrick 
    pkgs.rubyPackages.github-pages 
  ];

  languages.python.enable = true;
  languages.python.package = pkgs.python3.withPackages (ps: with ps; [
    requests
  ]);

  # Suppress warnings from Ruby bundled gems with unbuilt native extensions (debug, racc, rbs)
  # These are shipped with Ruby 3.3 but not compiled in Nix - they're not needed for Jekyll
  env.RUBYOPT = "-W0";

  

  # https://devenv.sh/languages/
  # languages.rust.enable = true;

  # https://devenv.sh/processes/
  # processes.cargo-watch.exec = "cargo-watch";

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/scripts/
  scripts.watch.exec = ''
    jekyll serve --host 0.0.0.0
  '';

  scripts.watch-incremental.exec = ''
    jekyll serve --host 0.0.0.0 --incremental
  '';

  scripts.build-prod.exec = ''    
    JEKYLL_ENV=production jekyll build --strict_front_matter --destination ../nathan.gs-website-raw
    cd ../nathan.gs-website-raw
    git add -A
    git commit -a -m "$(date "+%Y-%m-%d %H:%M")"
  '';

  scripts.publish-prod.exec = ''
    cd ../nathan.gs-website-raw
    git push
  '';

  scripts.ha-map-card-gallery.exec = ''
    cd $DEVENV_ROOT
    rm -rf _tmp_ha_map_card
    git clone git@github.com:nathan-gs/ha-map-card.git _tmp_ha_map_card
    #cp -r /home/nathan/projects/ha-map-card _tmp_ha_map_card
    cd _tmp_ha_map_card/showcase
    for i in *; do
      if [ "$i" = "README.md" ]; then
        continue
      fi
      echo "Creating post for $i"
      mkdir -p $DEVENV_ROOT/ha-map-card/$i
      cp -r $i/README.md $DEVENV_ROOT/_ha_map_card/$i.md
      find "$i" -maxdepth 1 -type f ! -name "README.md" -exec cp -r {} "$DEVENV_ROOT/ha-map-card/$i/" \;
    done
    cd $DEVENV_ROOT
    rm -rf _tmp_ha_map_card
  '';

  enterShell = ''
    git --version
  '';

  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';

}
