if !has('python')
  finish
endif

let s:save_cpo = &cpo
set cpo&vim

function! ghp#Start() abort
  python ghp.start()
endfunction

function! ghp#Preview() abort
  python ghp.preview()
endfunction

function! ghp#Stop() abort
  python ghp.stop()
endfunction

let &cpo = s:save_cpo
unlet s:save_cpo
