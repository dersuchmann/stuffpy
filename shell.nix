{ pkgs, inputsFrom }:

let 
  packageOverrides = pkgs.callPackage ./python-packages.nix { };
in 
pkgs.mkShell {
  inherit inputsFrom;
  
  nativeBuildInputs =
    with pkgs; [
      python313
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
