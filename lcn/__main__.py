import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import re

from dash.dependencies import Input, Output


def get_top_fig(data, limit, labels, title, height=450, width=480):
    if data.size > 0:
        x_values = data.values[limit:]
        y_values = data.keys()[limit:]
    else:
        x_values = [0]
        y_values = [0]

    fig = px.bar(
        data,
        x=x_values,
        y=y_values,
        labels=labels,
        orientation="h",
        height=height,
        width=width
    )

    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "y": 0.95,
            "xanchor": "center",
            "yanchor": "top"}
    )

    return fig


def get_salary_fig(data, height=450, width=480):
    if data.size > 0:
        min_from, min_to = int(data["salary_from"].min()), int(data["salary_to"].min())
        max_from, max_to = int(data["salary_from"].max()), int(data["salary_to"].max())

        # Calc mean/median only for salary_from/salary_to != 0 (not set).
        salary_filled = data[(data["salary_from"] > 0) & (data["salary_to"] > 0)]

        if salary_filled.size > 0:
            mean_from = int(salary_filled["salary_from"].mean())
            mean_to = int(salary_filled["salary_to"].mean())
            median_from = int(salary_filled["salary_from"].median())
            median_to = int(salary_filled["salary_to"].median())
        else:
            mean_from, mean_to, median_from, median_to = 0, 0, 0, 0
    else:
        min_from, min_to, max_from, max_to = 0, 0, 0, 0
        mean_from, mean_to, median_from, median_to = 0, 0, 0, 0

    salary_df = pd.DataFrame({
        "Salary": [
            "Min", "Min", "Max", "Max",
            "Mean", "Mean", "Median", "Median"
        ],
        "Money": [
            min_from, min_to,
            max_from, max_to,
            mean_from, mean_to,
            median_from, median_to
        ],
        "Fork": [
            "From", "To", "From", "To",
            "From", "To", "From", "To"
        ]
    })

    fig = px.bar(
        salary_df,
        x="Salary",
        y="Money",
        color="Fork",
        barmode="group",
        height=height,
        width=width
    )

    fig.update_layout(
        title={
            "text": "Salary Range",
            "x": 0.5,
            "y": 0.95,
            "xanchor": 'center',
            "yanchor": 'top'}
    )

    return fig


def main():
    # ---------------------------------------------------------------------------------
    # Load data.
    os.environ.setdefault("DATA_PATH", "/data")
    data_path = os.environ["DATA_PATH"]

    df_file = "{}/common.pickle".format(data_path)
    keywords_file = "{}/common-keywords.pickle".format(data_path)
    tags_file = "{}/common-tags.pickle".format(data_path)

    df: pd.DataFrame = pd.read_pickle(df_file)
    keywords: pd.Series = pd.read_pickle(keywords_file)
    tags: pd.Series = pd.read_pickle(tags_file)

    # ---------------------------------------------------------------------------------
    # Derive common variables.

    date_min = df["date"].min()
    date_max = df["date"].max()

    if "generated" in df.attrs:
        dataset_generated = df.attrs["generated"]
    else:
        dataset_generated = "unknown"

    salary: pd.DataFrame = df[(df["salary_from"] > 0) & (df["salary_to"] > 0)]

    style = {"display": "inline-block"}

    # ---------------------------------------------------------------------------------
    # Forming Dash.
    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(children=[
        dcc.Tabs(id="tabs", value="tab1", children=[
            dcc.Tab(label="Overview", value="tab1"),
            dcc.Tab(label="Filtering", value="tab2"),
        ]),
        html.Div(id='tabs-content')
    ])

    @app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
    def render_content(tab):
        if tab == 'tab1':
            return html.Div(children=[
                html.Div(children=[
                    html.Div(children=[
                        dcc.Markdown("""
                            ##### Application description: 
                            The main purpose of this app is to give a quick overview  
                            of job market in Russia, specifically - computer science.  
                            Dataset is based on publicly available information from  
                            such sites as [hh.ru](https://hh.ru). Data gathering is performed  
                            with help of an in-house tool - [gosquito](https://github.com/livelace/gosquito).  

                            """),
                    ]),
                    html.Div(children=[
                        dcc.Markdown("""
                            ##### Dataset information:  

                            Total cities: **{0}**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    
                            Total companies: **{1}**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;        
                            Total vacancies: **{2}**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    
                            """.format(
                            df["city"].value_counts().count(),
                            df["company"].value_counts().count(),
                            df["company"].count()
                        ))
                    ], style=style),
                    html.Div(children=[
                        dcc.Markdown("""
                            Total keywords: **{0}**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    
                            Total tags: **{1}**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  
                            &nbsp;&nbsp;&nbsp;&nbsp;            
                            """.format(
                            keywords.value_counts().count(),
                            tags.value_counts().count(),
                        ))
                    ], style=style),
                    html.Div(children=[
                        dcc.Markdown("""       
                            Filled salaries: **{0}**  
                            Position titles: **{1}**  

                            Period From: **{2}**    
                            Period To:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**{3}**    

                            Generated: **{4}**  
                            &nbsp;  
                            &nbsp;  
                            """.format(
                            salary["company"].count(),
                            df["title"].value_counts().count(),
                            date_min,
                            date_max,
                            dataset_generated
                        ))
                    ])
                ], style=style),
                html.Div(children=[
                    dcc.Graph(
                        id="tab1-top-city-graph",
                        figure=get_top_fig(
                            df["city"].value_counts(ascending=True),
                            -10,
                            {"x": "Vacancy", "y": "City"},
                            "City: Top10"
                        ),
                        style=style
                    ),
                    dcc.Graph(
                        id="tab1-top-company-graph",
                        figure=get_top_fig(
                            df["company"].value_counts(ascending=True),
                            -10,
                            {"x": "Vacancy", "y": "Company"},
                            "Company: Top10"
                        ),
                        style=style
                    ),
                    dcc.Graph(
                        id="tab1-top-position-graph",
                        figure=get_top_fig(
                            df["title"].value_counts(ascending=True),
                            -10,
                            {"x": "Amount", "y": "Position"},
                            "Position: Top10"
                        ),
                        style=style
                    )
                ], style=style),
                html.Div(children=[
                    dcc.Graph(
                        id="tab1-top-keyword-graph",
                        figure=get_top_fig(
                            keywords.value_counts(ascending=True),
                            -10,
                            {"x": "Amount", "y": "Keyword"},
                            "Keyword: Top10"
                        ),
                        style=style
                    ),
                    dcc.Graph(
                        id="tab1-top-tag-graph",
                        figure=get_top_fig(
                            tags.value_counts(ascending=True),
                            -10,
                            {"x": "Amount", "y": "Tag"},
                            "Tag: Top10"
                        ),
                        style=style
                    ),
                    dcc.Graph(id="tab1-salary-range", figure=get_salary_fig(salary), style=style)
                ], style=style)
            ])

        elif tab == 'tab2':
            return html.Div(children=[
                html.Div(children=[
                    html.Div(children=[
                        html.H5("Filter options:"),
                        dcc.Input(
                            id="tab2-position-input",
                            type="text",
                            placeholder="Python"
                        ),
                        dcc.Input(
                            id="tab2-city-input",
                            type="text",
                            placeholder="Москва"
                        ),
                        dcc.Input(
                            id="tab2-company-input",
                            type="text",
                            placeholder="Яндекс",
                        ),
                        dcc.Input(
                            id="tab2-salary-from-input",
                            type="number",
                            placeholder="from 100000",
                        ),
                        dcc.Input(
                            id="tab2-salary-to-input",
                            type="number",
                            placeholder="to 300000",
                        ),
                    ], style=style),
                    html.Div(children=[
                        dcc.Markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
                    ], style=style),
                    html.Div(children=[
                        html.H5("Limit options:"),
                        dcc.Input(
                            id="tab2-keyword-max-input",
                            type="number",
                            placeholder="Keyword"
                        ),
                        dcc.Input(
                            id="tab2-tag-max-input",
                            type="number",
                            placeholder="Tag"
                        ),
                    ], style=style),
                    html.Div(children=[
                        dcc.Markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
                    ], style=style),
                    html.Div(children=[
                        html.H5("Date options:"),
                        dcc.DatePickerRange(
                            id="tab2-date-input",
                            start_date=date_min.date(),
                            end_date=date_max.date(),
                            min_date_allowed=date_min.date(),
                            max_date_allowed=date_max.date()
                        )
                    ], style=style)
                ]),
                html.Div(children=[
                    dcc.Graph(
                        id="tab2-city-graph",
                        figure=get_top_fig(
                            df["city"].value_counts(ascending=True),
                            -10,
                            {"x": "Amount", "y": "City"},
                            "City"
                        ),
                        style=style
                    ),
                    dcc.Graph(
                        id="tab2-company-graph",
                        figure=get_top_fig(
                            df["company"].value_counts(ascending=True),
                            -10,
                            {"x": "Amount", "y": "Company"},
                            "Company"
                        ),
                        style=style
                    ),
                    dcc.Graph(
                        id="tab2-position-graph",
                        figure=get_top_fig(
                            df["title"].value_counts(ascending=True),
                            -10,
                            {"x": "Amount", "y": "Position"},
                            "Position"
                        ),
                        style=style
                    )
                ]),
                html.Div(children=[
                    dcc.Graph(
                        id="tab2-keyword-graph",
                        figure=get_top_fig(
                            keywords.value_counts(ascending=True),
                            -10,
                            {"x": "Amount", "y": "Keyword"},
                            "Keyword: Top10"
                        ),
                        style=style
                    ),
                    dcc.Graph(
                        id="tab2-tag-graph",
                        figure=get_top_fig(
                            tags.value_counts(ascending=True),
                            -10,
                            {"x": "Amount", "y": "Tag"},
                            "Tag: Top10"
                        ),
                        style=style
                    ),
                    dcc.Graph(id="tab2-salary-range", figure=get_salary_fig(salary), style=style)
                ])
            ])

    @app.callback(
        [
            Output("tab2-city-graph", "figure"),
            Output("tab2-company-graph", "figure"),
            Output("tab2-position-graph", "figure"),
            Output("tab2-keyword-graph", "figure"),
            Output("tab2-tag-graph", "figure"),
            Output("tab2-salary-range", "figure")
        ],
        [
            Input("tab2-position-input", "value"),
            Input("tab2-city-input", "value"),
            Input("tab2-company-input", "value"),
            Input("tab2-salary-from-input", "value"),
            Input("tab2-salary-to-input", "value"),
            Input("tab2-keyword-max-input", "value"),
            Input("tab2-tag-max-input", "value"),
            Input("tab2-date-input", "start_date"),
            Input("tab2-date-input", "end_date"),
        ]
    )
    def update_tab2_graph(*args):
        position, city, company, salary_from, salary_to, keyword_max, tag_max, start_date, end_date = args
        data = df

        if position:
            position_escaped = re.escape(position)
            data = data[data["title"].str.match(position_escaped, case=False)]

        if city:
            city_escaped = re.escape(city)
            data = data[data["city"].str.match(city_escaped, case=False)]

        if company:
            company_escaped = re.escape(company)
            data = data[data["company"].str.match(company_escaped, case=False)]

        # Salary.
        if salary_from and salary_to:
            data = data[(data["salary_from"] >= salary_from) & (data["salary_from"] <= salary_to) &
                        (data["salary_to"] >= salary_from) & (data["salary_to"] <= salary_to)]
        elif salary_from:
            data = data[data["salary_from"] >= salary_from]
        elif salary_to:
            data = data[data["salary_to"] <= salary_to]

        if start_date and end_date:
            data = data[(data["date"] >= start_date) & (data["date"] <= end_date)]
        elif start_date:
            data = data[data["date"] >= start_date]
        elif end_date:
            data = data[data["date"] <= end_date]

        # Resize bars if needed.
        if keyword_max and keyword_max > 10:
            keyword_height = (480 / 10) * keyword_max
            keyword_max *= -1
        else:
            keyword_height = 480
            keyword_max = -10

        if tag_max and tag_max > 10:
            tag_height = (480 / 10) * tag_max
            tag_max *= -1
        else:
            tag_height = 480
            tag_max = -10

        figs = [
            get_top_fig(
                data["city"].value_counts(ascending=True),
                -10,
                {"x": "Amount", "y": "City"},
                "City"
            ),
            get_top_fig(
                data["company"].value_counts(ascending=True),
                -10,
                {"x": "Amount", "y": "Company"},
                "Company"
            ),
            get_top_fig(
                data["title"].value_counts(ascending=True),
                -10,
                {"x": "Amount", "y": "Position"},
                "Position"
            ),
            get_top_fig(
                data["keywords"].explode().value_counts(ascending=True),
                keyword_max,
                {"x": "Amount", "y": "Keyword"},
                "Keyword",
                height=keyword_height
            ),
            get_top_fig(
                data["tags"].explode().value_counts(ascending=True),
                tag_max,
                {"x": "Amount", "y": "Tag"},
                "Tag",
                height=tag_height
            ),
            get_salary_fig(
                data
            )
        ]

        return figs

    app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False, host="0.0.0.0")


if __name__ == "__main__":
    main()
