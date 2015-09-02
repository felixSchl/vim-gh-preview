# Vim - Github Markdown Preview

[![npm version](https://badge.fury.io/js/gh-preview.svg)](http://badge.fury.io/js/gh-preview)

> Vim plugin for [gh-preview](https://github.com/felixschl/gh-preview), GFM
> preview, as you type.

![preview](https://raw.githubusercontent.com/felixSchl/felixSchl.github.io/master/gh-preview/preview.gif)

## Getting started

Install and run [gh-preview](https://github.com/felixschl/gh-preview):

```
$ npm install -g gh-preview
$ gh-preview
```

### Options

```vim
" Should the server start automatically when editing markdown files?
let g:ghp_start_server = 1

" Should the browser page be opened automatically?
let g:ghp_open_browser = 1

" The port to listen on / start `gh-preview` at
let g:ghp_port = 1234
```

#### Installation - Plugged.vim

```vim
Plug 'felixschl/vim-gh-preview'
```

#### Installation - Vundle.vim

```vim
Plugin 'felixschl/vim-gh-preview'
```
