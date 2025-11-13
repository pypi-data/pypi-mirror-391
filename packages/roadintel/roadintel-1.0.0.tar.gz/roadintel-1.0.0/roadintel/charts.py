"""
RoadIntel - Road Accident Data Visualization Library
--------------------------------------------------
A Python module for visualizing road accident data using Plotly Express.
Contains reusable chart functions and automated insight generation.
"""

import plotly.express as px
import pandas as pd


# ==============================================================
# 1️⃣ India's Map
# ==============================================================

def create_india_map_chart(dff, geojson_data, template):
    """
    Creates a choropleth map of India showing accident counts by state.

    Parameters
    ----------
    dff : pandas.DataFrame
        The dataset containing at least 'State Name' and 'Accident Count' columns.
    geojson_data : dict
        GeoJSON data containing state boundaries.
    template : str
        Plotly template (e.g., 'plotly_dark', 'plotly_white').

    Returns
    -------
    plotly.graph_objects.Figure
        A Plotly choropleth map figure.
    """
    map_data = dff.groupby("State Name")["Accident Count"].sum().reset_index()

    fig = px.choropleth_map(
        map_data,
        geojson=geojson_data,
        featureidkey="properties.NAME_1",
        locations="State Name",
        color="Accident Count",
        color_continuous_scale="Reds",
        map_style="carto-darkmatter",
        center={"lat": 22.9734, "lon": 78.6569},
        zoom=3.5,
        title="State-wise Road Accident Count in India",
        template=template,
    )

    fig.update_layout(
        paper_bgcolor="#222222",
        plot_bgcolor="#222222",
        font_color="white",
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )
    return fig


def create_empty_map(dff, geojson_data, template):
    """
    Creates an empty dark-themed map of India.
    Useful when no valid data is available for visualization.

    Parameters
    ----------
    dff : pandas.DataFrame
        Input dataset (used only to check emptiness).
    geojson_data : dict
        GeoJSON data containing state boundaries.
    template : str
        Plotly template for consistent styling.

    Returns
    -------
    plotly.graph_objects.Figure
        An empty map figure.
    """
    if dff is None or dff.empty:
        fig = px.choropleth_map(
            geojson=geojson_data,
            locations=[],
            color_continuous_scale="Reds",
            map_style="carto-darkmatter",
            center={"lat": 22.9734, "lon": 78.6569},
            zoom=3.5,
            title="State-wise Road Accident Count in India",
            template=template,
        )
        fig.update_layout(
            paper_bgcolor="#222222",
            plot_bgcolor="#222222",
            font_color="white",
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
        )
        return fig


# ==============================================================
# 2️⃣ Monthly Accident Trend
# ==============================================================

def create_monthly_trend_chart(dff, template):
    """
    Creates a line chart showing monthly trends of total accident counts.

    Parameters
    ----------
    dff : pandas.DataFrame
        Dataset containing 'Month', 'Month_Num', and 'Accident Count' columns.
    template : str
        Plotly visualization template.

    Returns
    -------
    plotly.graph_objects.Figure
        Line chart displaying monthly accident trends.
    """
    monthly_data = (
        dff.groupby(['Month', 'Month_Num'])['Accident Count']
        .sum()
        .reset_index()
        .sort_values('Month_Num')
    )

    fig = px.line(
        monthly_data,
        x='Month',
        y='Accident Count',
        title='Monthly Accident Trend',
        labels={'Month': '', 'Accident Count': 'Total Accidents'},
        template=template,
        markers=True,
    )

    fig.update_layout(plot_bgcolor='#222222', paper_bgcolor='#222222')
    return fig


# ==============================================================
# 3️⃣ Top States by Accident Count
# ==============================================================

def create_state_bar_chart(dff, template):
    """
    Creates a horizontal bar chart showing the top 10 states by accident count.

    Parameters
    ----------
    dff : pandas.DataFrame
        Dataset containing 'State Name' and 'Accident Count' columns.
    template : str
        Plotly template.

    Returns
    -------
    plotly.graph_objects.Figure
        Horizontal bar chart figure.
    """
    state_data = (
        dff.groupby('State Name')['Accident Count']
        .sum()
        .nlargest(10)
        .reset_index()
        .sort_values('Accident Count', ascending=True)
    )

    fig = px.bar(
        state_data,
        x='Accident Count',
        y='State Name',
        orientation='h',
        title='Top 10 States by Accident Count',
        labels={'State Name': '', 'Accident Count': 'Total Accidents'},
        template=template,
        text='Accident Count',
    )

    fig.update_layout(plot_bgcolor='#222222', paper_bgcolor='#222222')
    return fig


# ==============================================================
# 4️⃣ Accident Severity Distribution
# ==============================================================

def create_severity_donut_chart(dff, template):
    """
    Creates a donut chart showing the proportion of accidents by severity level.

    Parameters
    ----------
    dff : pandas.DataFrame
        Dataset containing 'Accident Severity' and 'Accident Count' columns.
    template : str
        Plotly template.

    Returns
    -------
    plotly.graph_objects.Figure
        Donut chart figure representing severity distribution.
    """
    severity_data = dff.groupby('Accident Severity')['Accident Count'].sum().reset_index()

    fig = px.pie(
        severity_data,
        names='Accident Severity',
        values='Accident Count',
        title='Accident Severity Distribution',
        hole=0.4,
        template=template,
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#000000', width=2)),
    )
    fig.update_layout(plot_bgcolor='#222222', paper_bgcolor='#222222')
    return fig


# ==============================================================
# 5️⃣ Severity by Road Type
# ==============================================================

def create_road_type_chart(dff, template):
    """
    Creates a grouped bar chart showing accident severity across different road types.

    Parameters
    ----------
    dff : pandas.DataFrame
        Dataset with 'Road Type', 'Accident Severity', and 'Accident Count' columns.
    template : str
        Plotly template.

    Returns
    -------
    plotly.graph_objects.Figure
        Grouped bar chart comparing severity by road type.
    """
    grouped_data = dff.groupby(['Road Type', 'Accident Severity'])['Accident Count'].sum().reset_index()

    fig = px.bar(
        grouped_data,
        x='Road Type',
        y='Accident Count',
        color='Accident Severity',
        barmode='group',
        title='Accident Severity by Road Type',
        labels={'Road Type': '', 'Accident Count': 'Total Accidents'},
        template=template,
    )

    fig.update_layout(plot_bgcolor='#222222', paper_bgcolor='#222222')
    return fig


# ==============================================================
# 6️⃣ Top 5 Vehicle Types Involved
# ==============================================================

def create_vehicle_bar_chart(dff, template):
    """
    Creates a vertical bar chart showing the top 5 vehicle types involved in accidents.

    Parameters
    ----------
    dff : pandas.DataFrame
        Dataset containing 'Vehicle Type Involved' and 'Accident Count' columns.
    template : str
        Plotly template.

    Returns
    -------
    plotly.graph_objects.Figure
        Vertical bar chart figure.
    """
    vehicle_data = (
        dff.groupby('Vehicle Type Involved')['Accident Count']
        .sum()
        .nlargest(5)
        .reset_index()
        .sort_values('Accident Count', ascending=False)
    )

    fig = px.bar(
        vehicle_data,
        x='Vehicle Type Involved',
        y='Accident Count',
        title='Top 5 Vehicle Types Involved In Accidents',
        labels={'Vehicle Type Involved': '', 'Accident Count': 'Total Accidents'},
        template=template,
        text='Accident Count',
    )

    fig.update_layout(plot_bgcolor='#222222', paper_bgcolor='#222222')
    fig.update_xaxes(tickangle=0)
    return fig


# ==============================================================
# 7️⃣ Alcohol Involvement
# ==============================================================

def create_alcohol_pie_chart(dff, template):
    """
    Creates a donut chart showing accidents involving alcohol.

    Parameters
    ----------
    dff : pandas.DataFrame
        Dataset containing 'Alcohol Involvement' and 'Accident Count' columns.
    template : str
        Plotly template.

    Returns
    -------
    plotly.graph_objects.Figure
        Donut chart showing alcohol involvement distribution.
    """
    alcohol_data = dff.groupby('Alcohol Involvement')['Accident Count'].sum().reset_index()

    fig = px.pie(
        alcohol_data,
        names='Alcohol Involvement',
        values='Accident Count',
        title='Alcohol Involvement in Accidents',
        template=template,
        hole=0.4,
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#000000', width=2)),
    )
    fig.update_layout(plot_bgcolor='#222222', paper_bgcolor='#222222')
    return fig


# ==============================================================
# 8️⃣ Weather & Lighting Impact
# ==============================================================

def create_weather_light_chart(dff, template):
    """
    Creates a grouped bar chart analyzing the combined effect of weather and lighting conditions.

    Parameters
    ----------
    dff : pandas.DataFrame
        Dataset containing 'Weather Conditions', 'Lighting Conditions', and 'Accident Count'.
    template : str
        Plotly template.

    Returns
    -------
    plotly.graph_objects.Figure
        Grouped bar chart showing accident counts under various conditions.
    """
    grouped_data = dff.groupby(['Weather Conditions', 'Lighting Conditions'])['Accident Count'].sum().reset_index()

    fig = px.bar(
        grouped_data,
        x='Weather Conditions',
        y='Accident Count',
        color='Lighting Conditions',
        barmode='group',
        title='Weather & Lighting Impact on Accidents',
        labels={'Weather Conditions': '', 'Accident Count': 'Total Accidents'},
        template=template,
    )

    fig.update_layout(plot_bgcolor='#222222', paper_bgcolor='#222222')
    fig.update_xaxes(tickangle=0)
    return fig


# ==============================================================
# 9️⃣ Driver Age vs Casualties
# ==============================================================

def create_age_casualty_bar_chart(dff, template):
    """
    Creates a bar chart showing the total number of casualties by driver age category.

    Parameters
    ----------
    dff : pandas.DataFrame
        Dataset containing 'Driver Age Category' and 'Number of Casualties' columns.
    template : str
        Plotly template.

    Returns
    -------
    plotly.graph_objects.Figure
        Bar chart representing casualties across driver age groups.
    """
    age_data = dff.groupby('Driver Age Category')['Number of Casualties'].sum().reset_index()

    fig = px.bar(
        age_data,
        x='Driver Age Category',
        y='Number of Casualties',
        color='Driver Age Category',
        title='Total Casualties by Driver Age',
        template=template,
        labels={'Driver Age Category': 'Driver Age Group', 'Number of Casualties': 'Total Casualties'},
    )

    fig.update_layout(plot_bgcolor='#222222', paper_bgcolor='#222222', showlegend=False)
    fig.update_xaxes(tickangle=-45)
    return fig


# ==============================================================
# 🔍 Insight Generator
# ==============================================================

def calculating_insights(dff):
    """
    Generates textual insights and a brief conclusion based on the filtered dataset.

    Parameters
    ----------
    dff : pandas.DataFrame
        Dataset containing accident details.

    Returns
    -------
    tuple
        A tuple of 5 strings:
        (insight_1, insight_2, insight_3, insight_4, conclusion)
    """
    try:
        top_state = dff['State Name'].mode()[0]
        top_time = dff['Part of Day'].mode()[0]
        top_vehicle = dff['Vehicle Type Involved'].mode()[0]
        top_weather = dff['Weather Conditions'].mode()[0]

        fatal_df = dff[dff['Accident Severity'] == 'Fatal']
        if not fatal_df.empty:
            top_fatal_vehicle = fatal_df['Vehicle Type Involved'].mode()[0]
        else:
            top_fatal_vehicle = "N/A"

        insight_1 = f"The highest number of accidents occurred in: {top_state}"
        insight_2 = f"Fatal accidents are most frequently linked with: {top_fatal_vehicle}"
        insight_3 = f"Accidents are most common during the: {top_time}"
        insight_4 = f"The most involved vehicle type is: {top_vehicle} (in {top_weather} weather)"
        conclusion = f"Based on the filters, safety measures should focus on {top_state}, particularly for {top_vehicle}s during {top_time} hours."

    except Exception:
        insight_1 = "Could not calculate insights."
        insight_2 = insight_3 = insight_4 = conclusion = ""

    return insight_1, insight_2, insight_3, insight_4, conclusion
