{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc ];
  buildInputs = with pkgs; [
    python313

    # Other necessary build tools
    gcc
    pkg-config
    stdenv

    # python313.withPackages (p: with p; [
    #   grpcio
    #   grpcio-tools
    #   # other Python packages
    # ])
  ];

  shellHook = ''
    echo "Entering Python 3.13 development shell"
    source .venv/bin/activate
  '';
}
