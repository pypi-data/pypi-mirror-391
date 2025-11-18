# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.d2 — Development flake
# :Created:   sab 10 ago 2024, 16:18:25
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2024, 2025 Lele Gaifax
#

{
  description = "metapensiero.sphinx.d2 development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    gitignore = {
      url = "github:hercules-ci/gitignore.nix";
      # Use the same nixpkgs
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, gitignore }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (builtins) fromTOML readFile;
        pinfo = (fromTOML (readFile ./pyproject.toml)).project;
        pkgs = import nixpkgs { inherit system; };
        inherit (gitignore.lib) gitignoreFilterWith;

        getSource = name: path: pkgs.lib.cleanSourceWith {
          name = name;
          src = path;
          filter = gitignoreFilterWith { basePath = path; };
        };

        pkg = pkgs.python3Packages.buildPythonPackage {
          pname = pinfo.name;
          version = pinfo.version;
          src = getSource "d2" ./.;
          pyproject = true;
          doCheck = false;
          buildInputs = [
            pkgs.python3Packages.pdm-backend
          ];
          dependencies = [
            pkgs.d2
            pkgs.python3Packages.sphinx
          ];
        };

        pythonEnv = pkgs.python3.withPackages (ps: [
          ps.bump-my-version
          pkg
        ]);
      in {
        devShells = {
          default = pkgs.mkShell {
            name = "Dev shell for metapensiero.sphinx.d2";

            packages = [
              pythonEnv
            ] ++ (with pkgs; [
              d2
              just
              twine
            ]) ++ (with pkgs.python3Packages; [
              build
              sphinx
              tomli
            ]);

            shellHook = ''
              TOP_DIR=$(pwd)

              cd() {
                builtin cd "''${1:-$TOP_DIR}"
              }

              export PYTHONPATH="$(pwd)/src''${PYTHONPATH:+:}$PYTHONPATH"
            '';
          };
        };

        packages = {
          d2 = pkg;
        };
      });
}
