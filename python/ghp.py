"""
# The GHP engine #

> Post buffer contents to the ghp preview server.
>
> NOTE: The server is available as the npm package `gh-preview`. To install it
>       run `npm install -g gh-preview@1.0.0-next`.

This module is more fluff than anything, getting around VIM's single-threaded
architecture i.o. to have the HTTP requests run asynchronously and to manage the
ghp-server subprocess if required.
"""

import os
import signal
import time
import Queue
import httplib
import threading
import subprocess
import json
import vim
import sys
import socket

# Error types
ERROR_PROCESS_FAILED_TO_START='ERROR_PROCESS_FAILED_TO_START'
ERROR_FAILED_TO_CONTACT_SERVER='ERROR_FAILED_TO_CONTACT_SERVER'
GHP_CONTACT_FAIL_THRESHOLD=5

# The neccessary evil - global variables.
ghp_process = None
ghp_t = None
ghp_t_stop = None
ghp_started = False
ghp_queue = Queue.Queue(1)
ghp_process_failed = False
ghp_contact_failed = 0
ghp_browser_opened = False
ghp_errors_reported = {}

def terminate_process(pid):
    """
    Terminate the managed ghp server process.
    """

    if sys.platform == 'win32':
        import ctypes
        PROCESS_TERMINATE = 1
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
        ctypes.windll.kernel32.TerminateProcess(handle, -1)
        ctypes.windll.kernel32.CloseHandle(handle)
    else:
        os.kill(pid, signal.SIGKILL)


def start_browser(url):
    """
    Start an external server at `url`
    """

    command =\
         'open -g'  if sys.platform.startswith('darwin')\
    else 'start'    if sys.platform.startswith('win')\
    else 'xdg-open'
    os.system(command + ' ' + url)


def process_queue(stop_event, port, auto_open_browser, auto_start_server):
    """
    Interact with the ghp server in the background.
    """

    global ghp_process
    global ghp_process_failed
    global ghp_browser_opened
    global ghp_contact_failed
    ghp_process_failed = False
    ghp_browser_opened = False
    ghp_contact_failed = 0

    while not stop_event.is_set() and not ghp_process_failed:
        data = ghp_queue.get()

        try:
            connection = httplib.HTTPConnection('localhost', port, timeout=1)
            connection.request('POST', '/api/doc/', data, {
                'Content-Type': 'application/json'
            })
            connection.close()
            ghp_contact_failed = 0
            if not ghp_browser_opened and auto_open_browser:
                ghp_browser_opened = True
                try:
                    start_browser('http://localhost:' + port)
                except:
                    # Just ignore for now...
                    pass
        except (socket.error, socket.timeout, httplib.HTTPException):
            # Auto-start `gh-preview` if necessary
            if not ghp_process \
               and not ghp_process_failed \
               and auto_start_server:
                startupinfo = None
                if sys.platform == 'win32':
                    command = 'gh-preview.cmd'
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    pipe = None
                else:
                    command = 'gh-preview'
                    pipe = subprocess.PIPE

                try:
                    ghp_process = subprocess.Popen(
                        [command, '--port=%s' % port],
                        bufsize=0,
                        startupinfo=startupinfo,
                        stdin=pipe,
                        stdout=pipe,
                        stderr=pipe,
                    )
                except Exception, e:
                    ghp_process_failed = True
        except Exception, e:
            ghp_contact_failed += 1

        ghp_queue.task_done()

    if ghp_process is not None:
        terminate_process(ghp_process.pid)


def check():
    """
    Check the status of the GHP engine and report any errors. This is needed
    because vim is single-threaded. This function simply needs to be called
    regularly enough...
    """

    global ghp_process_failed
    global ghp_errors_reported

    if ghp_process_failed:
        if not ERROR_PROCESS_FAILED_TO_START in ghp_errors_reported:
            ghp_errors_reported[ERROR_PROCESS_FAILED_TO_START] = True
            vim.command(
                'echohl ErrorMsg | echomsg \'%s\' | echohl None' % (
                    'ERROR: ' +
                    'The ghp-preview server could not be started. ' +
                    'To install run `npm i -g gh-preview@1.0.0-next`'
                ))
        return False
    elif ghp_contact_failed > GHP_CONTACT_FAIL_THRESHOLD:
        if not ERROR_FAILED_TO_CONTACT_SERVER in ghp_errors_reported:
            ghp_errors_reported[ERROR_FAILED_TO_CONTACT_SERVER] = True
            port = vim.eval('g:ghp_port'),
            vim.command(
                'echohl WarningMsg | echo \'%s\' | echohl None' % (
                    ('WARN: Failed to contact gh-preview server on port %s'
                        % port
                )))
    return True


def preview():
    """
    Submit the current buffer for preview to the ghp-server.
    """

    if not check():
        return

    global ghp_queue

    # Calculate the line
    scroll_offset = 10
    lines = len(vim.current.buffer)
    (line, _) = vim.current.window.cursor
    first_line = int(vim.eval('line("w0")'))
    last_line = int(vim.eval('line("w$")'))
    if (last_line - first_line) > scroll_offset:
        if (line - first_line) < scroll_offset and \
           (first_line > scroll_offset):
            line = first_line + scroll_offset
        elif (last_line - line) < scroll_offset and \
             (last_line < lines - scroll_offset):
            line = last_line - scroll_offset

    try:
        ghp_queue.put(
            json.dumps({
                'file':     vim.current.buffer.name,
                'markdown': '\n'.join(vim.current.buffer).decode('utf-8'),
                'cursor':   line,
                'lines':    lines,
            }),
            block=False,
        )
    except:
        pass

def stop():
    """
    Stop the GHP engine. Calls to `Preview` will now have no effect.
    """

    global ghp_t
    global ghp_t_stop
    global ghp_started
    global ghp_process

    if not ghp_started:
        return
    ghp_started = False

    ghp_t_stop.set()
    ghp_t._Thread__stop()

    if ghp_process is not None:
        terminate_process(ghp_process.pid)

def start():
    """
    Start the GHP engine. Calls to `Preview` will now have the effect of
    submitting the document to the ghp-server and subsequently render on all
    connected clients.
    """

    if not check():
        return

    global ghp_t
    global ghp_t_stop
    global ghp_started
    global ghp_process

    if ghp_started:
        return
    ghp_started = True

    ghp_t_stop = threading.Event()
    ghp_t = threading.Thread(target=process_queue, args=(
        ghp_t_stop,
        vim.eval('g:ghp_port'),
        vim.eval('g:ghp_open_browser'),
        vim.eval('g:ghp_start_server'),
    ))
    ghp_t.start()
