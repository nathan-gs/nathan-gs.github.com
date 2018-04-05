with (import <nixpkgs> {});
let
  gems = bundlerEnv {
    name = "nathan.gs";
    inherit ruby;
    gemdir = ./.;
  };
in stdenv.mkDerivation {
  name = "nathan.gs";
  buildInputs = [gems ruby];  
}