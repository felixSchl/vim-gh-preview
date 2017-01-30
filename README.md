# Vim - Github Markdown Preview

[![npm version](https://badge.fury.io/js/gh-preview.svg)](http://badge.fury.io/js/gh-preview)

> Vim plugin for [gh-preview](https://github.com/felixSchl/gh-preview) &mdash;
> Github markdown preview, as you type.

![preview](https://raw.githubusercontent.com/felixSchl/felixSchl.github.io/master/gh-preview/preview.gif)

## Getting started

Install [gh-preview](https://github.com/felixSchl/gh-preview):

```
$ npm install -g gh-preview@1.0.0-next
```

Once installed, `vim-gh-preview` *should just work*.

### Options

Below are the overridable **defaults** for the options exposed by this plugin:

```vim
" Should the server start automatically when editing markdown files?
" If something is already listening at `g:ghp_port`, it is assumed to be an
" existing gh-preview server and a new server is *NOT* started.
let g:ghp_start_server = 1

" Should the browser page be opened automatically?
let g:ghp_open_browser = 1

" The port `gh-preview` (is running | will be started) at
let g:ghp_port = 1234
```

#### Installation - Plugged.vim

```vim
Plug 'felixSchl/vim-gh-preview'
```

#### Installation - Vundle.vim

```vim
Plugin 'felixSchl/vim-gh-preview'
```
