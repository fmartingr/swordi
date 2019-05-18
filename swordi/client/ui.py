import asyncio

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout

from swordi.client.log import log_buffer, latency_buffer


class SwordiCommand:
    cmd = ""  # The command to type


class QuitCommand(SwordiCommand):
    cmd = "quit"

    def call(self):
        clientui.exit()


COMMANDS = {cmd.cmd: cmd() for cmd in (QuitCommand,)}


class CommandsCompleter(Completer):
    def get_completions(self, document, complete_event):
        for command in COMMANDS:
            if command.startswith(document.text) and document.text != command:
                yield Completion(command, start_position=document.cursor_position * -1)


def dummy(buffer: Buffer):
    command = buffer.text
    buffer.reset()
    if command in COMMANDS.keys():
        COMMANDS[command].call()
    else:
        log_buffer.newline()
        log_buffer.insert_text(f"Command '{command}' not found.")
    return False


input_buffer = Buffer(
    accept_handler=dummy, multiline=False, completer=CommandsCompleter()
)
root_container = HSplit(
    [
        Window(content=BufferControl(buffer=log_buffer, focusable=False)),
        VSplit(
            [
                Window(height=1, char="-"),
                Window(
                    width=9,
                    content=FormattedTextControl("Latency: "),
                    align=WindowAlign.RIGHT,
                ),
                Window(
                    width=12,
                    align=WindowAlign.RIGHT,
                    content=BufferControl(latency_buffer, focusable=False),
                ),
                Window(height=1, width=1, char="-"),
            ]
        ),
        Window(height=1, content=BufferControl(buffer=input_buffer)),
    ]
)

layout = Layout(root_container)

clientui = Application(layout=layout, full_screen=True)
