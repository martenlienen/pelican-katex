# Changelog

## 1.8.1

- Ignore delimiters in markdown that are followed by alphanumeric characters

## 1.8.0

- Allow escaping dollar delimiters in markdown with backslash

## 1.7.0

- Update the bundled katex to 0.16.7

## 1.6.1

- Serialize the namespace of `math` elements in markdown properly

## 1.6.0

- Add per-file preambles
- Two small bugfixes

## 1.5.0

- Add support for a shared preamble across math blocks

## 1.4.0

- Make it work on Windows

## 1.2.0

- Restructure the plugin into a client-server architecture to eliminate the
  overhead of loading nodejs and KaTeX once per math block/role

### Fixes

- Do not fail on newlines in interpreted text
- Reraise errors that happen during rendering of interpreted text
