#!/bin/bash

# shellcheck disable=SC2016
sed -i '' -e 's/curl -sSL "$install_url"/curl -sSL "$install_url" | sed '\''s\/symlinks=False\/symlinks=True\/'\''/g' ~/.local/share/mise/plugins/poetry/bin/install

mise install