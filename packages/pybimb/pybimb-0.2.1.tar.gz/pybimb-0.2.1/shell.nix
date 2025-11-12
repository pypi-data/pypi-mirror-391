{
  pkgs ? import <nixpkgs> {},
  unstablePkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz") {},
}:
pkgs.mkShell {
  buildInputs = with pkgs; [
    rustc
    cargo
    clippy
    rustfmt
    unstablePkgs.maturin
    python312
    python312Packages.pip
    python312Packages.numpy
    python312Packages.torch
    python312Packages.torchvision
    python312Packages.matplotlib
  ];
  shellHook = ''
    python3.12 -m venv .venv
    source .venv/bin/activate
  '';
}
