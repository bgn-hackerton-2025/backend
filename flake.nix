{
  description = "BGN Hackathon Classifier";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (pkgs:
        {
          default = pkgs.mkShell {
            buildInputs = with pkgs; [
              python313
              python313Packages.pip
              gcc
              stdenv.cc.cc.lib
              podman
            ];

            shellHook = ''
              export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc.lib]}:$LD_LIBRARY_PATH
            '';
          };
        }
      );
    };
}