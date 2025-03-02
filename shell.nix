{ pkgs, inputsFrom }:

let 
  packageOverrides = pkgs.callPackage ./python-packages.nix { };
  python313WithOverrides = pkgs.python313.override { inherit packageOverrides; };
in 
pkgs.mkShell {
  inherit inputsFrom;
  
  nativeBuildInputs =
    with pkgs; [
      (python313WithOverrides.withPackages (pypkgs: with pypkgs; [
        pyyaml
        jtd
        #solara # is installed separately in .venv
      ]))
    ]
  ;

  # for solara's numpy:
  env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ 
    pkgs.stdenv.cc.cc.lib
    pkgs.libz
  ];

  shellHook =
    ''
      source "$FLAKE_ROOT/.venv/bin/activate"
      exec "$SHELL"
    ''
  ;
}
