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

  

  # https://devenv.sh/languages/
  # languages.rust.enable = true;

  # https://devenv.sh/processes/
  # processes.cargo-watch.exec = "cargo-watch";

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/scripts/
  scripts.watch.exec = ''
    jekyll serve --incremental --host 0.0.0.0
  '';

  scripts.build-prod.exec = ''    
    JEKYLL_ENV=production jekyll build --strict_front_matter --destination /home/nathan/projects/nathan.gs-website-raw
    cd /home/nathan/projects/nathan.gs-website-raw
    git add -A
    git commit -a -m "$(date "+%Y-%m-%d %H:%M")"
  '';

  enterShell = ''
    hello
    git --version
  '';

  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';

}
