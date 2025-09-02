import altair as alt


def altair_theme():
    return {
        "config": {
            "title": {
                "fontSize": 18,
                "font": "Arial",
                "anchor": "start",
                "color": "#333"
            },
            "axis": {
                "labelFont": "Arial",
                "labelFontSize": 12,
                "titleFont": "Arial",
                "titleFontSize": 14,
                "gridColor": "#e6e6e6"
            },
            "legend": {
                "labelFont": "Arial",
                "labelFontSize": 12,
                "titleFont": "Arial",
                "titleFontSize": 14
            },
            "header": {
                "labelFont": "Arial",
                "labelFontSize": 12,
                "titleFont": "Arial",
                "titleFontSize": 14
            },
            "view": {"stroke": "transparent"},
            "range": {
                "category": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
            },
            "mark": {"color": "#1f77b4"},
            "area": {
                "line": {"color": "#1f77b4"},
                "color": {
                    "x1": 1, "y1": 1, "x2": 1, "y2": 0,
                    "gradient": "linear",
                    "stops": [
                        {"offset": 0, "color": "white"},
                        {"offset": 1, "color": "#1f77b4"}
                    ]
                }
            }
        }
    }


alt.themes.register("retail_insights_theme", altair_theme) 
alt.themes.enable("retail_insights_theme")