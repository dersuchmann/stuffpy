{
  inputs = {
    # nixpkgs-unstable as of 2024-10-31T18:10+01:00
    nixpkgs.url = "github:NixOS/nixpkgs/2d2a9ddbe3f2c00747398f3dc9b05f7f2ebb0f53";
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-root.url = "github:srid/flake-root";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.flake-root.flakeModule
      ];
      systems = [ "x86_64-linux" ];
      perSystem = { config, self', inputs', pkgs, system, ... }: {
        # flake-root.projectRootFile = "flake.nix"; # this is the default
        devShells.default = import ./shell.nix {
          inherit pkgs;
          inputsFrom = [ config.flake-root.devShell ];
        };
      };
    };
}
