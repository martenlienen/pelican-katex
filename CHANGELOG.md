# Changelog

## 1.2.0

- Restructure the plugin into a client-server architecture to eliminate the
  overhead of loading nodejs and KaTeX once per math block/role

### Fixes

- Do not fail on newlines in interpreted text
- Reraise errors that happen during rendering of interpreted text
