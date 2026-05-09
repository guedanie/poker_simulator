from shiny import App
from ui import app_ui


def server(input, output, session):
    pass


app = App(app_ui, server)
