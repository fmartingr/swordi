from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document


initial_msg = "Welcome to Swordi!\n\n"
log_buffer = Buffer(document=Document(text=initial_msg))
latency_buffer = Buffer(document=Document(text="Offline"))


class Logger:
    main = log_buffer
    latency = latency_buffer

    def log(self, text):
        self.main.newline()
        self.main.insert_text(text)
