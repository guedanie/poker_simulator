from shiny import render, reactive, ui
from simulation import parse_cards, run_simulation


def server(input, output, session):
    _result = reactive.value(None)
    _error = reactive.value("")

    @reactive.effect
    @reactive.event(input.run_btn)
    def _on_run():
        cards, err = parse_cards(input.hole_cards())
        if err:
            _error.set(err)
            _result.set(None)
            return
        _error.set("")
        data = run_simulation(cards, input.n_opponents())
        _result.set({
            "data": data,
            "label": (
                f"{input.hole_cards().strip().upper()} vs "
                f"{input.n_opponents()} opponent"
                f"{'s' if input.n_opponents() > 1 else ''}"
            ),
        })

    @output
    @render.ui
    def error_msg():
        msg = _error.get()
        if msg:
            return ui.p(msg, style="color: #e74c3c; margin-top: 8px;")
        return ui.div()

    @output
    @render.ui
    def results_panel():
        payload = _result.get()
        if payload is None:
            return ui.div()

        data = payload["data"]
        label = payload["label"]
        win_pct = data["win_pct"]
        won_with = data["won_with"]
        lost_to = data["lost_to"]
        banner_color = "#27ae60" if win_pct >= 50 else "#e74c3c"

        def bar_rows(hand_dict, color):
            total = sum(hand_dict.values())
            rows = []
            for name, count in sorted(hand_dict.items(), key=lambda x: x[1], reverse=True)[:5]:
                pct = round(count / total * 100, 1) if total > 0 else 0
                rows.append(ui.div(
                    ui.div(
                        ui.span(name),
                        ui.span(f"{pct}%", style=f"color: {color};"),
                        style="display:flex; justify-content:space-between; margin-bottom:3px;",
                    ),
                    ui.div(
                        ui.div(style=(
                            f"background:{color}; width:{pct}%; height:6px; border-radius:3px;"
                        )),
                        style="background:#444; border-radius:3px; height:6px; margin-bottom:10px;",
                    ),
                ))
            return rows

        return ui.div(
            ui.div(
                ui.h2(f"{win_pct}% Win Rate", style="margin:0; color:white;"),
                ui.p(
                    f"{label} — 5,000 hands",
                    style="margin:4px 0 0; color:rgba(255,255,255,0.8); font-size:0.9em;",
                ),
                style=(
                    f"background:{banner_color}; border-radius:8px;"
                    "padding:20px 24px; margin-bottom:20px;"
                ),
            ),
            ui.row(
                ui.column(
                    6,
                    ui.card(
                        ui.card_header(
                            ui.span("Won With", style="color:#2ecc71; font-weight:bold;")
                        ),
                        *bar_rows(won_with, "#2ecc71"),
                    ),
                ),
                ui.column(
                    6,
                    ui.card(
                        ui.card_header(
                            ui.span("Lost To", style="color:#e74c3c; font-weight:bold;")
                        ),
                        *bar_rows(lost_to, "#e74c3c"),
                    ),
                ),
            ),
        )
