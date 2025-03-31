import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc


class DashBoardroom:
    def __init__(self, layout, title="DashBoardroom Report"):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.title = title
        self.initial_layout = layout  # Store user-defined layout
        self.layout()

    def layout(self):
        self.app.layout = html.Div([
            dbc.Button("Switch to Edit Mode", id="toggle-mode", n_clicks=0, style={"margin-bottom": "20px"}),
            dcc.Store(id="mode", data="present"),
            html.Div(id="content")
        ])

        @self.app.callback(
            [Output("mode", "data"), Output("toggle-mode", "children")],
            Input("toggle-mode", "n_clicks"),
            State("mode", "data")
        )
        def toggle_mode(n_clicks, mode):
            new_mode = "edit" if mode == "present" else "present"
            button_text = "Switch to Present Mode" if new_mode == "edit" else "Switch to Edit Mode"
            return new_mode, button_text

        @self.app.callback(
            Output("content", "children"),
            Input("mode", "data")
        )
        def update_content(mode):
            children = []
            if mode == "edit":
                children.append(html.H2("Edit Mode"))
            else:
                children.append(html.H2("Presentation Mode"))

            for comp in self.initial_layout:
                if mode == "edit":
                    children.append(
                        html.Div(
                            comp,
                            draggable="true",
                            style={
                                "border": "2px dashed #aaa",
                                "padding": "10px",
                                "margin-bottom": "10px"
                            }
                        )
                    )
                else:
                    children.append(comp)

            return children

    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
    import plotly.express as px

    # Define the report layout manually
    fig1 = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")
    fig2 = px.bar(px.data.tips(), x="day", y="total_bill", color="sex", barmode="group")

    layout = [
        html.H1("My Report"),
        dcc.Graph(figure=fig1),
        dcc.Graph(figure=fig2),
        html.P("This is some explanatory text.")
    ]

    DashBoardroom(layout).run()
