import json
import requests
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, dash_table

# Charger le JSON depuis le lien web
url = "https://www.hcp.ma/region-eddakhla/docs/docs/odd_targets_indicators.json"
response = requests.get(url)
data = response.json()

# Liste des ODDs
goals = sorted(set(d["ODD"] for d in data))
goal_names = {
    "ODD 1": "Pas de pauvreté",
    "ODD 2": "Faim zéro",
    "ODD 3": "Bonne santé",
    "ODD 4": "Éducation de qualité",
    "ODD 5": "Égalité entre les sexes",
    "ODD 6": "Eau propre",
    "ODD 7": "Énergie propre",
    "ODD 8": "Travail décent",
    "ODD 9": "Industrie et innovation",
    "ODD 10": "Inégalités réduites",
    "ODD 11": "Villes durables",
    "ODD 12": "Consommation responsable",
    "ODD 13": "Lutte contre changement climatique",
    "ODD 14": "Vie aquatique",
    "ODD 15": "Vie terrestre",
    "ODD 16": "Paix et justice",
    "ODD 17": "Partenariats"
}
sdg_images = {f"ODD {i}": f"https://sdgs.un.org/sites/default/files/2020-07/Goal{i}_01.png" for i in range(1, 18)}

def translate(label, lang):
    translations = {
        "fr": {
            "title": "Objectifs de Développement Durable",
            "select_lang": "Langue",
            "targets": "Cibles",
            "indicators": "Indicateurs",
            "lang_fr": "Français",
            "lang_ar": "Arabe"
        },
        "ar": {
            "title": "أهداف التنمية المستدامة",
            "select_lang": "اللغة",
            "targets": "الأهداف الفرعية",
            "indicators": "المؤشرات",
            "lang_fr": "الفرنسية",
            "lang_ar": "العربية"
        }
    }
    return translations[lang].get(label, label)

app = Dash(__name__)
app.layout = html.Div([
    html.H2(id="title", style={"textAlign": "center"}),
    html.Div([
        html.Label(id="select_lang_label"),
        dcc.Dropdown(
            id="lang",
            value="fr",
            style={"width": "200px"}
        )
    ], style={"padding": "10px"}),
    html.Div([
        html.Div([dcc.Graph(id="donut")],
                 style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),
        html.Div(id="details",
                 style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "padding": "20px", "overflowX": "auto"})
    ])
])

@app.callback(
    Output("donut", "figure"),
    Output("title", "children"),
    Output("select_lang_label", "children"),
    Output("lang", "options"),
    Input("lang", "value")
)
def update_donut(lang):
    labels = [f"{i+1}. {goal_names[g]}" for i, g in enumerate(goals)]
    colors = [
        "#E5243B", "#DDA63A", "#4C9F38", "#C5192D", "#FF3A21", "#26BDE2",
        "#FCC30B", "#A21942", "#FD6925", "#DD1367", "#FD9D24", "#BF8B2E",
        "#3F7E44", "#0A97D9", "#56C02B", "#00689D", "#19486A"
    ]
    fig = go.Figure(go.Pie(
        labels=labels,
        values=[1]*len(goals),
        hole=0.35,
        marker=dict(colors=colors),
        textinfo="text",
        hoverinfo="label",
        text=[f"<b style='color:{c}'>{labels[i]}</b>" for i, c in enumerate(colors)]
    ))
    fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        annotations=[dict(text="SDG", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    options = [
        {"label": translate("lang_fr", lang), "value": "fr"},
        {"label": translate("lang_ar", lang), "value": "ar"}
    ]
    return fig, translate("title", lang), translate("select_lang", lang), options

@app.callback(
    Output("details", "children"),
    Input("donut", "clickData"),
    State("lang", "value")
)
def display_goal_info(clickData, lang):
    if clickData is None:
        return html.P("↩️ " + ("Cliquez sur un objectif" if lang == "fr" else "انقر على هدف"))
    label_clicked = clickData["points"][0]["label"]
    goal_clicked = [k for k, v in goal_names.items() if v in label_clicked][0]
    entries = [d for d in data if d["ODD"] == goal_clicked]
    table_data = [{"Cible": d["Cible"], "Indicateur": d["Indicateur international"]} for d in entries]
    return html.Div([
        html.H3(label_clicked),
        html.Img(src=sdg_images[goal_clicked], style={"height": "100px"}),
        html.H4(f"{translate('targets', lang)} & {translate('indicators', lang)}"),
        dash_table.DataTable(
            data=table_data,
            columns=[
                {"name": translate("targets", lang), "id": "Cible"},
                {"name": translate("indicators", lang), "id": "Indicateur"}
            ],
            style_cell={
                "textAlign": "left",
                "padding": "5px",
                "whiteSpace": "normal",
                "height": "auto"
            },
            style_header={"fontWeight": "bold"},
            page_size=10
        )
    ])

if __name__ == "__main__":
    app.run(debug=True, port=8051)
