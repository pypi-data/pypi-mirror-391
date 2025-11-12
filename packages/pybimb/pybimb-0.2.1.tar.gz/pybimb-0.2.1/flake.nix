{
  description = "flake for bimb";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/?ref=nixos-25.05";
  };

  outputs = {
    self,
    nixpkgs,
  }: {
    # TODO add other platforms at some point
    devShell.x86_64-linux = let
      pkgs = import nixpkgs {system = "x86_64-linux";};
      python = pkgs.python312;
    in
      pkgs.mkShell {
        buildInputs = with pkgs; [
          rustc
          cargo
          clippy
          rustfmt
          pkgs.maturin
          python
          python.pkgs.pip
          python.pkgs.numpy
          python.pkgs.torch
          python.pkgs.torchvision
          python.pkgs.matplotlib
        ];

        shellHook = ''
          if [ ! -d .venv ]; then
            ${python}/bin/python -m venv .venv
          fi
          source .venv/bin/activate
        '';
      };
  };
}
