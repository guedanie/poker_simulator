from shiny import ui
import shinyswatch

app_ui = ui.page_fluid(
    ui.div(
        ui.h2("Poker Hand Simulator"),
        style="margin: 16px 0 24px;",
    ),
    ui.row(
        ui.column(
            4,
            ui.card(
                ui.card_header("Setup"),
                ui.input_numeric(
                    "n_opponents", "Number of opponents",
                    value=2, min=1, max=5, step=1,
                ),
                ui.input_text(
                    "hole_cards", "Your hole cards",
                    placeholder="AH KS",
                ),
                ui.p(
                    ui.em("Ranks: 2–9 T J Q K A  |  Suits: H D C S"),
                    style="color: #aaa; font-size: 0.85em; margin-top: -8px;",
                ),
                ui.input_action_button(
                    "run_btn", "Run Simulation",
                    class_="btn-success w-100 mt-2",
                ),
                ui.output_ui("error_msg"),
            ),
        ),
        ui.column(
            8,
            ui.output_ui("results_panel"),
        ),
    ),
    theme=shinyswatch.theme.darkly,
)
