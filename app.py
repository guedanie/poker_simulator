from shiny import App, ui

app_ui = ui.page_fluid(ui.h2("Poker Hand Simulator"))

def server(input, output, session):
    pass

app = App(app_ui, server)
