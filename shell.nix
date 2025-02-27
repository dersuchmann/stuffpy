{ pkgs }:

let 
  packageOverrides = pkgs.callPackage ./python-packages.nix { };
  python313WithOverrides = pkgs.python313.override { inherit packageOverrides; };
in 
pkgs.mkShell {
  nativeBuildInputs =
    with pkgs; [
      (python313WithOverrides.withPackages (pypkgs: with pypkgs; [
        pyyaml
        jtd
        #solara # has to be installed separately
      ]))
    ]
  ;

  # for solara's numpy:
  env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ 
    pkgs.stdenv.cc.cc.lib
    pkgs.libz
  ];
}
