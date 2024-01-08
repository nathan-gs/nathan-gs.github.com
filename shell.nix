with import <nixpkgs> { };
{ incremental? false }:
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

    # use with --arg incremental true
    shellHook = ''
      exec ${jekyll_env}/bin/jekyll serve --profile --watch --future --host 0.0.0.0 ${lib.strings.optionalString incremental "--incremental"}
    '';
  }