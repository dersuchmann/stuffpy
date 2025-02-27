{
  inputs =
    {
      # nixpkgs-unstable as of 2024-10-31T18:10+01:00
      nixpkgs.url = "github:NixOS/nixpkgs/2d2a9ddbe3f2c00747398f3dc9b05f7f2ebb0f53";
    }
  ;

  outputs = { self, nixpkgs }@inputs:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      systemShell = "/etc/profiles/per-user/dersuchmann/bin/zsh";
    in
    {
      devShells.${system}.default =
        # The value of the following expression is a derivation
        (import ./shell.nix { inherit pkgs systemShell; });
    }
  ;
}
