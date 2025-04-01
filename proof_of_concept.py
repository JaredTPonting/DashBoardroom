import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import uuid
import json

from dash.exceptions import PreventUpdate

class DashBoardroom:
    def __init__(self, components=None):
        if components is None:
            components = []

        self.initial_layout = [] # Placeholder for saving and loading layouts
        self.available_components = components

        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

        self.app.layout = dbc.Container(
            [
                dcc.Store(id="layout-store", data=self.initial_layout),
                dcc.Store(id="selected-element", data=None),
                dcc.Store(id="mode", data="edit"),

                dbc.Row(
                    [dbc.Col(
                        [
                            html.H5("Components"),
                            html.Ul(
                                [
                                    html.Li(comp) for comp in self.available_components
                                ],
                                style={"listStyleType": "none", "padding": 0}
                            )
                        ],
                        width=2,
                        style={"border": "1px solid #ccc", "height": "90vh", "overflowY": "auto", "padding": "10px"}
                    ),
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Button("Switch Mode", id="switch-mode", color="primary", className="me-2")),
                                        dbc.Col(dbc.Button("Add Row", id="add-row", color="secondary", className="me-2")),
                                        dbc.Col(dbc.Button("Add Col", id="add-col", color="secondary", className="me-2")),
                                        dbc.Col(dbc.Button("Add Text", id="add-text", color="secondary", className="me-2")),
                                ], className="mb-3"
                            ),
                            html.Div(
                                id="playground",
                                style={"border": "1px solid #000", "minHeight": "80vh", "padding": "10px"}
                            )
                        ], width=10
                    )]
                )
            ], fluid=True
        )

        self._register_callbacks()

    def _render_element(self, element, selected_element):
        """
        recursively renders a layout element based on its type.
        """
        base_style = element.get("style", {}).copy()
        base_style.setdefault("zIndex", element.get("depth", 1))

        if selected_element and selected_element.get("id") == element["id"] and selected_element.get("type") == element["type"]:
            base_style.setdefault("backgroundColor", "#e0f7fa")

        children = element.get("children", [])
        rendered_children = [self._render_element(child, selected_element) for child in children] if children else []

        # depending on element type, need to wrap properly
        if element["type"] == "row":
            inner = dbc.Row(rendered_children, className="mb-3", style={"border": "1px solid #ccc", "padding": "10px", "cursor": "pointer"})
        elif element["type"] == "col":
            inner = dbc.Col(html.Div(rendered_children))
        elif element["type"] == "custom":
            inner = html.Div(rendered_children)
        else:
            inner = html.Div(rendered_children)

        return html.Div(
            inner,
            id={"type": f"playground-{element['type']}", "inner-type": element["type"], "id": element["id"], "depth": element.get("depth", 1)},
            n_clicks=0,
            n_clicks_timestamp=0,
            style=base_style
        )

    def _render_layout(self, layout_config, selected_element):
        """
        Recursivley renders the entire layout
        """
        return [self._render_element(element, selected_element) for element in layout_config]

    def _register_callbacks(self):
        """
        Register all dash callbacks for interactivity
        """
        app = self.app

        @app.callback(
            Output("playground", "children"),
            [
                Input("layout-store", "data"),
                Input("selected-element", "data")
            ]
        )
        def update_playground(layout_config, selected_element):
            """
            Updates the playground area when the layout or selection changes
            """
            return self._render_layout(layout_config, selected_element)

        @app.callback(
            Output("selected-element", "data"),
            [
                Input({"type": "playground-row", "id": dash.ALL}, "n_clicks_timestamp"),
                Input({"type": "playground-col", "id": dash.ALL}, "n_clicks_timestamp")
            ],
            State("selected-element", "data"),
            prevent_initial_call=True
        )
        def select_element(row_ts, col_ts, custom_ts, current_selected):
            """
            Determines which layout element was clicked most recently based on timestamps,
            returns a dictionary describing the selected element
            """
            ctx = callback_context
            if not ctx.triggered:
                return current_selected

            triggered = ctx.triggered

            try:
                triggered_sorted = sorted(triggered, key=lambda t: float(t.get("value") or 0), reverse=True)
            except Exception:
                return current_selected

            new_selected = None
            for t in triggered_sorted:
                try:
                    triggered_id = json.loads(t["prop_id"].split(".")[0])
                except Exception:
                    continue

                new_selected = {"type": triggered_id.get("type"), "id": triggered_id.get("id")}

                if current_selected == new_selected:
                    return None
                return new_selected

        @app.callback(
            [
                Output("mode", "data"),
                Output("switch-mode", "children")
            ],
            Input("switch-mode", "n_clicks"),
            State("mode", "data")
        )
        def  switch_mode(n_clicks, current_mode):
            """
            switches between edit and present mode
            """
            if not n_clicks:
                return current_mode, "Switch Mode: edit"
            new_mode = "present" if current_mode == "edit" else "edit"
            return new_mode, f"Switch Mode: {new_mode}"

        @app.callback(
            Output("layout-store", "data", allow_duplicate=True),
            Input("add-row", "n_clicks"),
            State("layout-store", "data"),
            State("selected-element", "data"),
            prevent_initial_call=True
        )
        def add_row(n_clicks, layout_config, selected_element):
            """
            adds a new row to the layout.
            """
            # TODO: Make a new function called add row beneath that replicates this funciton. Change this function to add a row within a column (if selected element is col)
            new_row = {
                "type": "row",
                "depth": 1,
                "id": str(uuid.uuid4()),
                "style": {},
                "children": []
            }
            layout_config.append(new_row)
            return layout_config

        @app.callback(
            Output("layout-store", "data", allow_duplicate=True),
            Input("add-col", "n_clicks"),
            State("layout-store", "data"),
            State("selected-element", "data"),
            prevent_initial_call=True
        )
        def add_col(n_clicks, layout_config, selected_element):
            """
            Adds a new column to the selected row

            Expects the selected element to be a row
            """
            # TODO: this needs to be change din the future to search for rows nested in rows and cols to see where to add the col
            if not selected_element or selected_element.get("type") != "row":
                return layout_config
            for element in layout_config:
                if element["type"] == "row" and element["id"] == selected_element["id"]:
                    new_col = {
                        "type": "col",
                        "depth": element.get("depth", 1) + 1,
                        "id": str(uuid.uuid4()),
                        "style": {},
                        "children": []
                    }
                    element["children"].append(new_col)
                    break
            return layout_config


    def run(self, **kwargs):
        """
        Runs the Dash server
        """
        self.app.run()


if __name__ == "__main__":
    temp_app = DashBoardroom(components=["Graph", "Text", "Image"])
    temp_app.run()








