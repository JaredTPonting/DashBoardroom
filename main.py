import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px

class DashBoardroom:
    def __init__(self, title="DashBoardroom Report"):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.title = title
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
            fig = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")
            if mode == "edit":
                return html.Div([
                    html.H2("Edit Mode"),
                    html.Div(
                        "Drag and drop components here...",
                        style={"border": "2px dashed #aaa", "padding": "20px", "minHeight": "200px", "marginBottom": "20px"}
                    ),
                    dbc.Input(placeholder="Enter new text here", type="text", style={"marginBottom": "10px"}),
                    dbc.Button("Add Text Block", id="add-text", n_clicks=0)
                ])
            else:
                return html.Div([
                    html.H2("Presentation Mode"),
                    dcc.Graph(figure=fig)
                ])

    def run(self):
        self.app.run(debug=True)

if __name__ == "__main__":
    DashBoardroom().run()
