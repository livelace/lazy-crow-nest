import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import os
import pandas as pd
import plotly.express as px
import re

from dash.dependencies import Input, Output
from datetime import datetime
from zeep import Client


def get_exchange_rates():
    result = {}

    client = Client("https://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?wsdl")
    response = client.service.GetCursOnDate(datetime.today())

    for i in response["_value_1"]["_value_1"]:
        result[i["ValuteCursOnDate"]["VchCode"]] = float(i["ValuteCursOnDate"]["Vcurs"] / i["ValuteCursOnDate"]["Vnom"])

    return result


def get_top_horizontal_fig(data, limit, labels, title, height=500, width=480):
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
        title=title,
        height=height,
        width=width
    )

    fig.update_xaxes(tickformat="d", automargin=False)

    return fig


def get_top_vertical_fig(data, labels, title, height=500, width=400):
    if data.size > 0:
        x_values = data.keys()
        y_values = data.values
    else:
        x_values = [0]
        y_values = [0]

    fig = px.bar(
        data,
        x=x_values,
        y=y_values,
        labels=labels,
        title=title,
        height=height,
        width=width
    )

    fig.update_xaxes(tickformat="d", automargin=False)

    return fig


def get_salary_fig(data, height=500, width=400):
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
        barmode="group",
        color="Fork",
        title="Salary Range",
        height=height,
        width=width
    )

    fig.update_xaxes(tickformat="d", automargin=False)

    return fig


def main():
    # ---------------------------------------------------------------------------------
    # Load data.
    os.environ.setdefault("DATA_PATH", "/data")
    data_path = os.environ["DATA_PATH"]

    df_file = "{}/common.pickle".format(data_path)
    df = pd.read_pickle(df_file)

    keywords_exploded = df["keywords"].explode()
    tags_exploded = df["tags"].explode()

    keywords_unique = keywords_exploded.unique().size
    tags_unique = tags_exploded.unique().size

    keywords_values = keywords_exploded.value_counts(ascending=True)
    tags_values = keywords_exploded.value_counts(ascending=True)

    cities_unique = df["city"].unique().size
    companies_unique = df["company"].unique().size
    positions_unique = df["title"].unique().size
    vacancies_total = df["company"].count()

    cities_values = df["city"].value_counts(ascending=True)
    companies_values = df["company"].value_counts(ascending=True)
    positions_values = df["title"].value_counts(ascending=True)
    lang_values = df["lang"].value_counts()
    salary_currency_values = df["salary_currency"].value_counts(ascending=True)

    years_values = df["year"].value_counts(ascending=True)
    months_values = df["month"].value_counts(ascending=True)
    days_values = df["day"].value_counts(ascending=True)
    week_days_values = df["week_day"].value_counts(ascending=True)
    hours_values = df["hour"].value_counts(ascending=True)
    minutes_values = df["minute"].value_counts(ascending=True)

    # ---------------------------------------------------------------------------------
    # Styles.
    currency_style = {"width": "50px"}

    date_style = {"height": "30px"}

    default_style = {"display": "inline-block"}

    input_style = {"width": "150px"}

    tabs_style = {"height": "35px"}

    tab_style = {
        "borderBottom": "1px solid #d6d6d6",
        "padding": "6px",
    }

    tab_selected_style = {
        "borderTop": "1px solid #d6d6d6",
        "borderBottom": "1px solid #d6d6d6",
        "fontWeight": "bold",
        "padding": "6px"
    }

    # ---------------------------------------------------------------------------------
    # Derive common variables.

    date_min = df["date"].min()
    date_max = df["date"].max()

    if "generated" in df.attrs:
        dataset_generated = df.attrs["generated"]
    else:
        dataset_generated = "unknown"

    default_top_limit = -15

    salary_full_amount = df[(df["salary_from"] > 0) & (df["salary_to"] > 0)]["company"].count()
    salary_from_amount = df[(df["salary_from"] > 0) & (df["salary_to"] == 0)]["company"].count()
    salary_to_amount = df[(df["salary_from"] == 0) & (df["salary_to"] > 0)]["company"].count()

    # ---------------------------------------------------------------------------------
    # Forming Dash.
    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SIMPLEX])
    app.layout = html.Div(children=[
        dcc.Tabs(id="tabs", value="tab1", children=[
            dcc.Tab(label="Overview", id="tab1", value="tab1", style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label="Details", id="tab2", value="tab2", style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label="Timeline", id="tab3", value="tab3", style=tab_style, selected_style=tab_selected_style),
        ], style=tabs_style),
        html.Div(id="tabs-content")
    ])

    @app.callback(Output("tabs-content", "children"), Input("tabs", "value"))
    def render_content(tab):
        if tab == "tab1":
            return html.Div(children=[
                html.Div(children=[
                    html.Div(children=[
                        dcc.Markdown("""
                            ##### Application description: 
                            The main purpose of [this app](https://github.com/livelace/lazy-crow-nest) is to give a 
                            quick overview&nbsp;&nbsp;&nbsp;&nbsp;  
                            of job market in Russia, specifically - computer science.  
                            Dataset is based on publicly available information from  
                            such sites as [hh.ru](https://hh.ru). Data gathering is performed  
                            with help of an in-house tool - [gosquito](https://github.com/livelace/gosquito).  
                              
                            """),
                    ]),
                    html.Div(children=[
                        dcc.Markdown("""
                            ##### Dataset information:  

                            Unique cities: **{0}**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    
                            Unique companies: **{1}**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;        
                            Total vacancies: **{2}**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    
                            """.format(
                            cities_unique,
                            companies_unique,
                            vacancies_total
                        ))
                    ], style=default_style),
                    html.Div(children=[
                        dcc.Markdown("""
                            Unique keywords: **{0}**  
                            Unique tags: **{1}**   
                            Unique positions: **{2}**           
                            """.format(
                            keywords_unique,
                            tags_unique,
                            positions_unique,
                        ))
                    ], style=default_style),
                    html.Div(children=[
                        dcc.Markdown("""       
                            Salaries Filled Full:&nbsp;&nbsp;
                            **{0}**  
                            Salaries Only From: **{1}**  
                            Salaries Only To:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**{2}**  
                            
                            Period From: **{3}**    
                            Period To:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**{4}**    

                            Generated: **{5}**  
                            &nbsp;  
                            &nbsp;  
                            """.format(
                            salary_full_amount,
                            salary_from_amount,
                            salary_to_amount,
                            date_min,
                            date_max,
                            dataset_generated
                        ))
                    ])
                ], style=default_style),
                html.Div(children=[
                    dcc.Graph(
                        id="tab1-top-city-graph",
                        figure=get_top_horizontal_fig(
                            cities_values,
                            default_top_limit,
                            {"x": "Vacancy", "y": "City"},
                            "City: Top15"
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab1-top-company-graph",
                        figure=get_top_horizontal_fig(
                            companies_values,
                            default_top_limit,
                            {"x": "Vacancy", "y": "Company"},
                            "Company: Top15"
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab1-top-position-graph",
                        figure=get_top_horizontal_fig(
                            positions_values,
                            default_top_limit,
                            {"x": "Amount", "y": "Position"},
                            "Position: Top15"
                        ),
                        style=default_style
                    )
                ], style=default_style),
                html.Div(children=[
                    dcc.Graph(
                        id="tab1-top-keyword-graph",
                        figure=get_top_horizontal_fig(
                            keywords_values,
                            default_top_limit,
                            {"x": "Amount", "y": "Keyword"},
                            "Keyword: Top15",
                            width=350
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab1-top-tag-graph",
                        figure=get_top_horizontal_fig(
                            tags_values,
                            default_top_limit,
                            {"x": "Amount", "y": "Tag"},
                            "Tag: Top15",
                            width=350
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab1-top-lang",
                        figure=get_top_vertical_fig(
                            lang_values,
                            {"index": "Language", "y": "Amount"},
                            "Vacancy Language",
                            width=350
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab1-salary-range",
                        figure=get_salary_fig(df, width=350),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab1-top-salary-currency",
                        figure=get_top_vertical_fig(
                            salary_currency_values,
                            {"index": "Currency", "y": "Amount"},
                            "Salary Currency",
                            width=350
                        ),
                        style=default_style
                    ),
                ], style=default_style)
            ])

        elif tab == "tab2":
            return html.Div(children=[
                html.Div(children=[
                    html.Div(children=[
                        html.H5("Filters:"),
                        dcc.Input(
                            id="tab2-position-input",
                            type="text",
                            placeholder="Python",
                            style=input_style
                        ),
                        dcc.Input(
                            id="tab2-city-input",
                            type="text",
                            placeholder="Москва",
                            style=input_style
                        ),
                        dcc.Input(
                            id="tab2-company-input",
                            type="text",
                            placeholder="Яндекс",
                            style=input_style
                        ),
                        dcc.Input(
                            id="tab2-keyword-input",
                            type="text",
                            placeholder="Akka",
                            style=input_style
                        ),
                        dcc.Input(
                            id="tab2-tag-input",
                            type="text",
                            placeholder="Scala",
                            style=input_style
                        ),
                    ], style=default_style),
                    html.Div(children=[
                        dcc.Markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
                    ], style=default_style),
                    html.Div(children=[
                        html.H5("Salary:"),
                        dcc.Input(
                            id="tab2-salary-from-input",
                            type="number",
                            placeholder="from 100000",
                            style=input_style
                        ),
                        dcc.Input(
                            id="tab2-salary-to-input",
                            type="number",
                            placeholder="to 300000",
                            style=input_style
                        ),
                        html.Datalist(id="currencies", children=[
                            html.Option(value="RUB"),
                            html.Option(value="USD"),
                            html.Option(value="EUR"),
                        ]),
                        dcc.Input(
                            id="tab2-salary-currency-input",
                            type="text",
                            list="currencies",
                            placeholder="RUB",
                            style=currency_style
                        ),
                    ], style=default_style),
                    html.Div(children=[
                        dcc.Markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
                    ], style=default_style),
                    html.Div(children=[
                        html.H5("Limits:"),
                        dcc.Input(
                            id="tab2-keyword-max-input",
                            type="number",
                            placeholder="Keyword",
                            style=input_style

                        ),
                        dcc.Input(
                            id="tab2-tag-max-input",
                            type="number",
                            placeholder="Tag",
                            style=input_style
                        ),
                    ], style=default_style),
                    html.Div(children=[
                        dcc.Markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
                    ], style=default_style),
                    html.Div(children=[
                        html.H5("Date:"),
                        dcc.DatePickerRange(
                            id="tab2-date-input",
                            min_date_allowed=date_min.date(),
                            max_date_allowed=date_max.date(),
                            style=date_style
                        )
                    ], style=default_style)
                ]),
                html.Div(children=[
                    dcc.Graph(
                        id="tab2-city-graph",
                        figure=get_top_horizontal_fig(
                            cities_values,
                            default_top_limit,
                            {"x": "Amount", "y": "City"},
                            "City"
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab2-company-graph",
                        figure=get_top_horizontal_fig(
                            companies_values,
                            default_top_limit,
                            {"x": "Amount", "y": "Company"},
                            "Company"
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab2-position-graph",
                        figure=get_top_horizontal_fig(
                            positions_values,
                            default_top_limit,
                            {"x": "Amount", "y": "Position"},
                            "Position"
                        ),
                        style=default_style
                    )
                ]),
                html.Div(children=[
                    dcc.Graph(
                        id="tab2-keyword-graph",
                        figure=get_top_horizontal_fig(
                            keywords_values,
                            default_top_limit,
                            {"x": "Amount", "y": "Keyword"},
                            "Keyword"
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab2-tag-graph",
                        figure=get_top_horizontal_fig(
                            tags_values,
                            default_top_limit,
                            {"x": "Amount", "y": "Tag"},
                            "Tag"
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab2-salary-range",
                        figure=get_salary_fig(df),
                        style=default_style
                    )
                ])
            ])

        elif tab == "tab3":
            return html.Div(children=[
                html.Div(children=[
                    html.H5("Filters:"),
                    dcc.Input(
                        id="tab3-position-input",
                        type="text",
                        placeholder="Python"
                    ),
                    dcc.Input(
                        id="tab3-city-input",
                        type="text",
                        placeholder="Москва"
                    ),
                    dcc.Input(
                        id="tab3-company-input",
                        type="text",
                        placeholder="Яндекс",
                    ),
                ], style={"width": "100%", "display": "flex", "align-items": "center", "justify-content": "center"}),
                html.Div(children=[
                    dcc.Graph(
                        id="tab3-timeline-year-graph",
                        figure=get_top_vertical_fig(
                            years_values,
                            {"index": "Year", "y": "Amount"},
                            "Per Year",
                            width=500
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab3-timeline-month-graph",
                        figure=get_top_vertical_fig(
                            months_values,
                            {"index": "Month", "y": "Amount"},
                            "Per Month",
                            width=500
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab3-timeline-day-graph",
                        figure=get_top_vertical_fig(
                            days_values,
                            {"index": "Month Day", "y": "Amount"},
                            "Per Day",
                            width=500
                        ),
                        style=default_style
                    )
                ]),
                html.Div(children=[
                    dcc.Graph(
                        id="tab3-timeline-weekday-graph",
                        figure=get_top_vertical_fig(
                            week_days_values,
                            {"index": "Week Day", "y": "Amount"},
                            "Per Week Day",
                            width=500
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab3-timeline-hour-graph",
                        figure=get_top_vertical_fig(
                            hours_values,
                            {"index": "Hour", "y": "Amount"},
                            "Per Hour",
                            width=500
                        ),
                        style=default_style
                    ),
                    dcc.Graph(
                        id="tab3-timeline-minute-graph",
                        figure=get_top_vertical_fig(
                            minutes_values,
                            {"index": "Minute", "y": "Amount"},
                            "Per Minute",
                            width=500
                        ),
                        style=default_style
                    )
                ])
            ])

    # ---------------------------------------------------------------------------------
    # Callback functions.

    # Tab 2.
    @app.callback(
        [
            Output("tab2", "label"),
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
            Input("tab2-keyword-input", "value"),
            Input("tab2-tag-input", "value"),
            Input("tab2-salary-from-input", "value"),
            Input("tab2-salary-to-input", "value"),
            Input("tab2-salary-currency-input", "value"),
            Input("tab2-keyword-max-input", "value"),
            Input("tab2-tag-max-input", "value"),
            Input("tab2-date-input", "start_date"),
            Input("tab2-date-input", "end_date"),
        ]
    )
    def update_tab2(*args):
        begin_time = time.time()

        position, city, company, keyword, tag, salary_from, salary_to, salary_currency, keyword_max, tag_max, \
            start_date, end_date = args
        data = df

        # Primary filters.
        if position:
            data = data[data["title"].str.match(re.escape(position), case=False)]

        if city:
            data = data[data["city"].str.match(re.escape(city), case=False)]

        if company:
            data = data[data["company"].str.match(re.escape(company), case=False)]

        if keyword:
            keywords_index = keywords_exploded.str.contains(keyword, case=False, na=False)
            keywords_index = keywords_index[keywords_index == True]
            keywords_index = keywords_index[~keywords_index.index.duplicated(keep='first')]
            data = data[data.index.isin(keywords_index.index)]

        if tag:
            tags_index = tags_exploded.str.contains(tag, case=False, na=False)
            tags_index = tags_index[tags_index == True]
            tags_index = tags_index[~tags_index.index.duplicated(keep='first')]
            data = data[data.index.isin(tags_index.index)]

        # Salary.
        if not salary_currency:
            salary_currency = "RUB"

        if salary_from and salary_to:
            data = data[(data["salary_from"] >= salary_from) & (data["salary_from"] <= salary_to) &
                        (data["salary_to"] >= salary_from) & (data["salary_to"] <= salary_to) &
                        (data["salary_currency"] == salary_currency)]
        elif salary_from:
            data = data[(data["salary_from"] >= salary_from) & (data["salary_currency"] == salary_currency)]
        elif salary_to:
            data = data[(data["salary_to"] <= salary_to) & (data["salary_currency"] == salary_currency)]

        # Date.
        if start_date and end_date:
            data = data[(data["date"] >= start_date) & (data["date"] <= end_date)]
        elif start_date:
            data = data[data["date"] >= start_date]
        elif end_date:
            data = data[data["date"] <= end_date]

        # Resize bars if needed.
        if keyword_max and keyword_max > 15:
            keyword_height = (500 / 15) * keyword_max
            keyword_max *= -1
        else:
            keyword_height = 500
            keyword_max = default_top_limit

        if tag_max and tag_max > 15:
            tag_height = (500 / 15) * tag_max
            tag_max *= -1
        else:
            tag_height = 500
            tag_max = default_top_limit

        end_time = time.time()

        figs = [
            "Details ({:.2f}s)".format(end_time - begin_time),
            get_top_horizontal_fig(
                data["city"].value_counts(ascending=True),
                default_top_limit,
                {"x": "Amount", "y": "City"},
                "City"
            ),
            get_top_horizontal_fig(
                data["company"].value_counts(ascending=True),
                default_top_limit,
                {"x": "Amount", "y": "Company"},
                "Company"
            ),
            get_top_horizontal_fig(
                data["title"].value_counts(ascending=True),
                default_top_limit,
                {"x": "Amount", "y": "Position"},
                "Position"
            ),
            get_top_horizontal_fig(
                data["keywords"].explode().value_counts(ascending=True),
                keyword_max,
                {"x": "Amount", "y": "Keyword"},
                "Keyword",
                height=keyword_height
            ),
            get_top_horizontal_fig(
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

    # Tab 3.
    @app.callback(
        [
            Output("tab3", "label"),
            Output("tab3-timeline-year-graph", "figure"),
            Output("tab3-timeline-month-graph", "figure"),
            Output("tab3-timeline-day-graph", "figure"),
            Output("tab3-timeline-weekday-graph", "figure"),
            Output("tab3-timeline-hour-graph", "figure"),
            Output("tab3-timeline-minute-graph", "figure"),
        ],
        [
            Input("tab3-position-input", "value"),
            Input("tab3-city-input", "value"),
            Input("tab3-company-input", "value")
        ]
    )
    def update_tab3(*args):
        begin_time = time.time()

        position, city, company = args
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

        end_time = time.time()

        figs = [
            "Timeline ({:.2f}s)".format(end_time - begin_time),
            get_top_vertical_fig(
                data["year"].value_counts(ascending=True),
                {"index": "Year", "y": "Amount"},
                "Per Year",
                width=500
            ),
            get_top_vertical_fig(
                data["month"].value_counts(ascending=True),
                {"index": "Month", "y": "Amount"},
                "Per Month",
                width=500
            ),
            get_top_vertical_fig(
                data["day"].value_counts(ascending=True),
                {"index": "Month Day", "y": "Amount"},
                "Per Day",
                width=500
            ),
            get_top_vertical_fig(
                data["week_day"].value_counts(ascending=True),
                {"index": "Week Day", "y": "Amount"},
                "Per Week Day",
                width=500
            ),
            get_top_vertical_fig(
                data["hour"].value_counts(ascending=True),
                {"index": "Hour", "y": "Amount"},
                "Per Hour",
                width=500
            ),
            get_top_vertical_fig(
                data["minute"].value_counts(ascending=True),
                {"index": "Minute", "y": "Amount"},
                "Per Minute",
                width=500
            )
        ]

        return figs

    app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False, host="0.0.0.0")


if __name__ == "__main__":
    main()
