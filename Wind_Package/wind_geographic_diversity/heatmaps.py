# GeographicDiversity_Package/Wind_Package/wind_geographic_diversity/heatmaps.py

import pandas as pd
import plotly.graph_objects as go
from haversine import haversine, Unit
import numpy as np

def prepare_dataframe(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
    """
    Inspect and prepare the DataFrame for analysis.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        df_name (str): Name of the DataFrame (for logging).

    Returns:
        pd.DataFrame: The DataFrame with a 'time' column in datetime format.
    """
    print(f"Inspecting DataFrame '{df_name}':")
    print(df.head())  # Quick peek at the data

    # If 'time' is the index, reset to a column
    if df.index.name == 'time':
        df.reset_index(inplace=True)

    if 'time' not in df.columns:
        raise KeyError(f"'time' column is missing from the DataFrame '{df_name}'.")

    df['time'] = pd.to_datetime(df['time'])
    return df

def aggregate_windspeed_data(locations: dict, dataframes: dict) -> tuple:
    """
    Aggregates windspeed data into daily, weekly, monthly, and yearly DataFrames.

    Returns:
        tuple: (df_combined_daily, df_combined_weekly, df_combined_monthly, df_combined_yearly)
    """
    daily_data_list = []
    weekly_data_list = []
    monthly_data_list = []
    yearly_data_list = []

    for loc_name, (lat, lon) in locations.items():
        df_loc = prepare_dataframe(dataframes[loc_name], loc_name)

        # DAILY
        df_daily = df_loc.copy()
        df_daily.set_index('time', inplace=True)
        df_daily = df_daily.resample('D').mean().reset_index()
        df_daily['Year'] = df_daily['time'].dt.year
        df_daily['Location'] = loc_name
        df_daily['Latitude'] = lat
        df_daily['Longitude'] = lon
        df_daily['Day_Index'] = df_daily.groupby('Year').cumcount()
        daily_data_list.append(df_daily)

        # WEEKLY
        df_weekly = df_loc.copy()
        df_weekly.set_index('time', inplace=True)
        df_weekly = df_weekly.resample('W').mean().reset_index()
        df_weekly['Year'] = df_weekly['time'].dt.year
        df_weekly['Location'] = loc_name
        df_weekly['Latitude'] = lat
        df_weekly['Longitude'] = lon
        df_weekly['Week_Index'] = df_weekly.groupby('Year').cumcount()
        weekly_data_list.append(df_weekly)

        # MONTHLY
        df_monthly = df_loc.copy()
        df_monthly.set_index('time', inplace=True)
        df_monthly = df_monthly.resample('M').mean().reset_index()
        df_monthly['Year'] = df_monthly['time'].dt.year
        df_monthly['Location'] = loc_name
        df_monthly['Latitude'] = lat
        df_monthly['Longitude'] = lon
        df_monthly['Month_Index'] = df_monthly.groupby('Year').cumcount()
        monthly_data_list.append(df_monthly)

        # YEARLY
        df_yearly = df_loc.copy()
        df_yearly['Year'] = df_yearly['time'].dt.year
        df_yearly = df_yearly.groupby('Year', as_index=False).mean()
        df_yearly['Location'] = loc_name
        df_yearly['Latitude'] = lat
        df_yearly['Longitude'] = lon
        yearly_data_list.append(df_yearly)

    df_combined_daily = pd.concat(daily_data_list, ignore_index=True)
    df_combined_weekly = pd.concat(weekly_data_list, ignore_index=True)
    df_combined_monthly = pd.concat(monthly_data_list, ignore_index=True)
    df_combined_yearly = pd.concat(yearly_data_list, ignore_index=True)

    return df_combined_daily, df_combined_weekly, df_combined_monthly, df_combined_yearly

def calculate_min_max(df_combined_daily: pd.DataFrame,
                      df_combined_weekly: pd.DataFrame,
                      df_combined_monthly: pd.DataFrame,
                      df_combined_yearly: pd.DataFrame) -> dict:
    """
    Finds min/max wind speeds for daily, weekly, monthly, yearly DataFrames,
    and ensures we don't have a degenerate range (min == max).
    """
    daily_min = df_combined_daily['wspd'].min()
    daily_max = df_combined_daily['wspd'].max()

    weekly_min = df_combined_weekly['wspd'].min()
    weekly_max = df_combined_weekly['wspd'].max()

    monthly_min = df_combined_monthly['wspd'].min()
    monthly_max = df_combined_monthly['wspd'].max()

    yearly_min = df_combined_yearly['wspd'].min()
    yearly_max = df_combined_yearly['wspd'].max()

    def ensure_range(min_val, max_val):
        if min_val is None or max_val is None:
            return 0.0, 1.0
        if abs(max_val - min_val) < 1e-9:
            return min_val, min_val + 0.01
        return min_val, max_val

    daily_min, daily_max = ensure_range(daily_min, daily_max)
    weekly_min, weekly_max = ensure_range(weekly_min, weekly_max)
    monthly_min, monthly_max = ensure_range(monthly_min, monthly_max)
    yearly_min, yearly_max = ensure_range(yearly_min, yearly_max)

    return {
        'daily_min': daily_min,
        'daily_max': daily_max,
        'weekly_min': weekly_min,
        'weekly_max': weekly_max,
        'monthly_min': monthly_min,
        'monthly_max': monthly_max,
        'yearly_min': yearly_min,
        'yearly_max': yearly_max
    }

def create_interactive_heatmap(df_combined: pd.DataFrame,
                               frequency: str,
                               min_wspd: float,
                               max_wspd: float,
                               output_path: str) -> None:
    """
    Create a Plotly figure with a year dropdown + dynamic slider (for d/w/m)
    or a single slider (for y).
    In the yearly case, we create exactly one trace per year, so each location
    has its own color within that year.
    """

    if frequency == 'd':
        index_col = 'Day_Index'
        title_prefix = 'Daily Windspeed (m/s)'
    elif frequency == 'w':
        index_col = 'Week_Index'
        title_prefix = 'Weekly Windspeed (m/s)'
    elif frequency == 'm':
        index_col = 'Month_Index'
        title_prefix = 'Monthly Windspeed (m/s)'
    elif frequency == 'y':
        index_col = 'Year'
        title_prefix = 'Yearly Average Windspeed (m/s)'
    else:
        raise ValueError("Frequency must be 'd', 'w', 'm', or 'y'")

    all_years = sorted(df_combined['Year'].unique())
    fig = go.Figure()

    # For daily/weekly/monthly, keep your existing approach
    if frequency in ('d', 'w', 'm'):
        trace_metadata = []
        for year in all_years:
            df_year = df_combined[df_combined['Year'] == year]
            unique_indices = sorted(df_year[index_col].unique())

            for idx_val in unique_indices:
                subset = df_year[df_year[index_col] == idx_val]
                if subset.empty:
                    continue

                rep_date = subset['time'].min() if 'time' in subset.columns else None
                if frequency == 'd' and rep_date is not None:
                    date_label = rep_date.strftime('%Y-%m-%d')
                elif frequency == 'w' and rep_date is not None:
                    date_label = f"Week of {rep_date.strftime('%Y-%m-%d')}"
                elif frequency == 'm' and rep_date is not None:
                    date_label = rep_date.strftime('%B %Y')
                else:
                    date_label = f"{frequency.upper()} {idx_val}"

                trace_name = f"{frequency.upper()}_{year}_{date_label}"
                fig.add_trace(go.Scattergeo(
                    lon=subset['Longitude'],
                    lat=subset['Latitude'],
                    text=subset['Location'],
                    marker=dict(
                        size=18,
                        color=subset['wspd'],
                        colorscale='Portland',
                        cmin=min_wspd,
                        cmax=max_wspd,
                        line=dict(width=1, color='#222'),
                        colorbar=dict(title="Windspeed (m/s)", len=0.4)
                    ),
                    mode='markers',
                    name=trace_name,
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        f"Year: {year}<br>"
                        f"{frequency.upper()} Index: {idx_val}<br>"
                        "Windspeed: %{marker.color:.2f} m/s<extra></extra>"
                    ),
                    visible=False
                ))
                current_idx = len(fig.data) - 1
                trace_metadata.append((year, date_label, current_idx))

        # Make first trace visible
        if len(fig.data) > 0:
            fig.data[0].visible = True

        # Build a dummy slider with no steps initially
        slider_template = dict(
            active=0,
            pad={"t": 50, "b": 10},
            steps=[],
            currentvalue=dict(prefix="Date: ", font=dict(size=16, color='#000'))
        )

        # Build a year-based dropdown
        dropdown_buttons = []
        for year in all_years:
            year_traces = [t for t in trace_metadata if t[0] == year]
            steps_for_year = []
            for (yr, lbl, t_idx) in year_traces:
                step = dict(
                    method='update',
                    args=[
                        {'visible': [False]*len(fig.data)},
                        {'title': f"{title_prefix} - {year}"}
                    ],
                    label=lbl
                )
                step['args'][0]['visible'][t_idx] = True
                steps_for_year.append(step)

            visible_for_button = [False]*len(fig.data)
            if steps_for_year:
                first_idx = steps_for_year[0]['args'][0]['visible'].index(True)
                visible_for_button[first_idx] = True

            button = dict(
                label=str(year),
                method='update',
                args=[
                    {'visible': visible_for_button},
                    {
                        'title': f"{title_prefix} - {year}",
                        'sliders': [dict(
                            steps=steps_for_year,
                            active=0,
                            currentvalue=dict(prefix="Date: ", font=dict(size=16, color='#000'))
                        )]
                    }
                ]
            )
            dropdown_buttons.append(button)

        fig.update_layout(
            template='plotly_white',
            title=dict(text=title_prefix, x=0.5, xanchor='center'),
            geo=dict(
                scope='usa',
                projection_type='albers usa',
                showland=True,
                landcolor='#fafaf5',
                subunitcolor="#bdbdbd",
                countrycolor="#aaaaaa",
                coastlinecolor="#cccccc",
                showlakes=True,
                lakecolor="#e6f2ff"
            ),
            updatemenus=[dict(
                active=0,
                buttons=dropdown_buttons,
                x=0.0,
                y=1.15,
                xanchor='left',
                yanchor='top',
                pad={'r': 10, 't': 10},
                showactive=True,
                direction='down'
            )],
            sliders=[slider_template],
            paper_bgcolor='#f4f4f4',
            margin=dict(l=30, r=30, t=90, b=40),
            showlegend=False
        )

    else:
        # YEARLY: one trace per year => each location's wspd is an array
        unique_years = sorted(df_combined['Year'].unique())
        for year in unique_years:
            df_year = df_combined[df_combined['Year'] == year]

            # Single trace for this entire year
            fig.add_trace(go.Scattergeo(
                lon=df_year['Longitude'],
                lat=df_year['Latitude'],
                text=df_year['Location'],
                marker=dict(
                    size=18,
                    color=df_year['wspd'],  # array of speeds
                    colorscale='Portland',
                    cmin=min_wspd,
                    cmax=max_wspd,
                    line=dict(width=1, color='#222'),
                    colorbar=dict(title="Windspeed (m/s)", len=0.4)
                ),
                mode='markers',
                name=str(year),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    f"Year: {year}<br>"
                    "Windspeed: %{marker.color:.2f} m/s<extra></extra>"
                ),
                visible=False
            ))

        # Make the first year visible
        if len(fig.data) > 0:
            first_year = str(unique_years[0])
            for trace in fig.data:
                if trace.name == first_year:
                    trace.visible = True

        slider_steps = []
        for y in unique_years:
            step = dict(
                method='update',
                args=[
                    {'visible': [trace.name == str(y) for trace in fig.data]},
                    {'title': f"{title_prefix} - {y}"}
                ],
                label=str(y)
            )
            slider_steps.append(step)

        fig.update_layout(
            template='plotly_white',
            title=dict(text=title_prefix, x=0.5, xanchor='center'),
            geo=dict(
                scope='usa',
                projection_type='albers usa',
                showland=True,
                landcolor='#fafaf5',
                subunitcolor="#bdbdbd",
                countrycolor="#aaaaaa",
                coastlinecolor="#cccccc",
                showlakes=True,
                lakecolor="#e6f2ff"
            ),
            sliders=[dict(
                active=0,
                steps=slider_steps,
                currentvalue=dict(prefix="Year: ", font=dict(size=16, color='#000'))
            )],
            paper_bgcolor='#f4f4f4',
            margin=dict(l=30, r=30, t=90, b=40),
            showlegend=False
        )

    fig.write_html(output_path)
    print(f"{frequency.upper()} heatmap saved to '{output_path}'")