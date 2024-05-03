#!/bin/bash

mise install python

mise plugin add poetry

# the following sed is a hack to get around poetry not following python shims by default (which are configured by mise)
# shellcheck disable=SC2016
sed -i '' -e 's/curl -sSL "$install_url"/curl -sSL "$install_url" | sed '\''s\/symlinks=False\/symlinks=True\/'\''/g' ~/.local/share/mise/plugins/poetry/bin/install

mise install

lefthook install