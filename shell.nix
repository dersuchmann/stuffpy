{ pkgs, systemShell }:

let 
  packageOverrides = pkgs.callPackage ./python-packages.nix { };
  python313WithOverrides = pkgs.python313.override { inherit packageOverrides; };
in 
pkgs.mkShell {
  nativeBuildInputs =
    with pkgs; [
      nodejs_22  # 22.10.0
      pnpm  # 9.12.2

      (python313WithOverrides.withPackages (pypkgs: with pypkgs; [
        pyyaml
        jtd
        #solara
      ]))

      #postgresql  # 16.4
      #typst  # 0.12.0
    ]
  ;

  # for solara's numpy:
  env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ 
    pkgs.stdenv.cc.cc.lib
    pkgs.libz
  ];

  shellHook =
    ''
      echo "Now switching from bash back into system shell..." | ${pkgs.lolcat}/bin/lolcat
      exec ${systemShell}
    ''
  ;
}
