source "https://rubygems.org"

# Versions pinned to exactly what devenv.nix provides, so a Cloudflare Pages
# build produces the same output as a local `jekyll build`.
#
# Deliberately NOT the `github-pages` gem, even though devenv.nix installs it:
# bundler auto-requires it, which activates the whole GitHub Pages plugin suite
# (github-metadata, optional-front-matter, relative-links, titles-from-headings,
# ...). The local Nix build runs jekyll without bundler, so it only ever loads
# the plugins listed under `plugins:` in _config.yml -- the four below. Pinning
# them directly keeps the two builds equivalent, and avoids jekyll-github-metadata
# failing off of GitHub ("No repo name found").
gem "jekyll", "3.10.0"
gem "minima", "2.5.1"

# `kramdown: input: GFM` needs the GFM parser as a separate gem under kramdown 2.x.
gem "kramdown", "2.4.0"
gem "kramdown-parser-gfm", "1.1.0"

# Not a dependency of jekyll since Ruby 3.0; only needed for `jekyll serve`.
gem "webrick", "~> 1.9"

group :jekyll_plugins do
  gem "jekyll-paginate", "1.1.0"
  gem "jekyll-redirect-from", "0.16.0"
  gem "jekyll-seo-tag", "2.8.0"
  gem "jekyll-sitemap", "1.4.0"
end
