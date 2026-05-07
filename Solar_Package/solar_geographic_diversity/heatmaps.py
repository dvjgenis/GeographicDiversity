# GeographicDiversity_Package/Solar_Package/solar_geographic_diversity/heatmaps.py

import pandas as pd
import numpy as np
import plotly.graph_objects as go

def prepare_solar_dataframe(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
    """
    Inspect the DataFrame and ensure we have a 'Datetime' or 'time' column,
    standardizing it to 'time'.
    """
    print(f"[SolarHeatmaps] Inspecting DataFrame '{df_name}':")
    print(df.head())

    if 'Datetime' in df.columns:
        df['time'] = df['Datetime']
    elif 'time' in df.columns:
        pass
    else:
        raise KeyError(f"[SolarHeatmaps] No 'Datetime' or 'time' column in '{df_name}'.")

    df['time'] = pd.to_datetime(df['time'])
    return df

def aggregate_solar_data(locations: dict, dataframes: dict) -> tuple:
    """
    Aggregates solar data for daily, weekly, monthly, yearly intervals, expecting columns 'DNI' and 'DHI'.
    Creates 'Total_Irradiance' = DNI + DHI for each location.

    Returns four combined DataFrames:
      df_daily_combined, df_weekly_combined, df_monthly_combined, df_yearly_combined
    """
    daily_list, weekly_list, monthly_list, yearly_list = [], [], [], []

    for loc_name, (lat, lon) in locations.items():
        df_loc = dataframes[loc_name].copy()
        df_loc = prepare_solar_dataframe(df_loc, df_name=loc_name)

        # Add up DNI + DHI -> Total_Irradiance
        df_loc['Total_Irradiance'] = df_loc['DNI'] + df_loc['DHI']

        # --- Daily ---
        df_daily = (
            df_loc
            .set_index('time')
            .resample('D')
            .mean(numeric_only=True)
            .reset_index()
        )
        df_daily['Year'] = df_daily['time'].dt.year
        df_daily['Location'] = loc_name
        df_daily['Latitude'] = lat
        df_daily['Longitude'] = lon
        df_daily['Day_Index'] = df_daily.groupby('Year').cumcount()
        daily_list.append(df_daily)

        # --- Weekly ---
        df_weekly = (
            df_loc
            .set_index('time')
            .resample('W')
            .mean(numeric_only=True)
            .reset_index()
        )
        df_weekly['Year'] = df_weekly['time'].dt.year
        df_weekly['Location'] = loc_name
        df_weekly['Latitude'] = lat
        df_weekly['Longitude'] = lon
        df_weekly['Week_Index'] = df_weekly.groupby('Year').cumcount()
        weekly_list.append(df_weekly)

        # --- Monthly ---
        df_monthly = (
            df_loc
            .set_index('time')
            .resample('M')
            .mean(numeric_only=True)
            .reset_index()
        )
        df_monthly['Year'] = df_monthly['time'].dt.year
        df_monthly['Location'] = loc_name
        df_monthly['Latitude'] = lat
        df_monthly['Longitude'] = lon
        df_monthly['Month_Index'] = df_monthly.groupby('Year').cumcount()
        monthly_list.append(df_monthly)

        # --- Yearly ---
        df_yearly = df_loc.copy()
        df_yearly['Year'] = df_yearly['time'].dt.year
        df_yearly = df_yearly.groupby('Year', as_index=False).mean(numeric_only=True)
        df_yearly['Location'] = loc_name
        df_yearly['Latitude'] = lat
        df_yearly['Longitude'] = lon
        yearly_list.append(df_yearly)

    df_daily_combined = pd.concat(daily_list, ignore_index=True)
    df_weekly_combined = pd.concat(weekly_list, ignore_index=True)
    df_monthly_combined = pd.concat(monthly_list, ignore_index=True)
    df_yearly_combined = pd.concat(yearly_list, ignore_index=True)

    return (df_daily_combined,
            df_weekly_combined,
            df_monthly_combined,
            df_yearly_combined)

def calculate_min_max_by_category(df_daily, df_weekly, df_monthly, df_yearly) -> dict:
    """
    For each category (daily, weekly, monthly, yearly),
    find the overall min/max of 'Total_Irradiance' across all years in that category.
    """
    daily_min = df_daily['Total_Irradiance'].min()
    daily_max = df_daily['Total_Irradiance'].max()

    weekly_min = df_weekly['Total_Irradiance'].min()
    weekly_max = df_weekly['Total_Irradiance'].max()

    monthly_min = df_monthly['Total_Irradiance'].min()
    monthly_max = df_monthly['Total_Irradiance'].max()

    yearly_min = df_yearly['Total_Irradiance'].min()
    yearly_max = df_yearly['Total_Irradiance'].max()

    return {
        'daily_min': daily_min, 'daily_max': daily_max,
        'weekly_min': weekly_min, 'weekly_max': weekly_max,
        'monthly_min': monthly_min, 'monthly_max': monthly_max,
        'yearly_min': yearly_min, 'yearly_max': yearly_max
    }

def create_interactive_heatmap(df_combined: pd.DataFrame,
                               frequency: str,
                               cmin: float,
                               cmax: float,
                               output_path: str,
                               title_prefix: str = "Solar Irradiance"):
    """
    Creates an interactive Plotly-based map with:
      - A year dropdown
      - A slider for the index (Day_Index, Week_Index, Month_Index) or simpler approach for 'Year'
   
    Uses the provided cmin/cmax across ALL years in that category,
    so the color scale is consistent for that category (daily, weekly, monthly, or yearly).
    """
    fig = go.Figure()

    if frequency == 'D':
        index_col = 'Day_Index'
        freq_label = 'Day'
        base_title = f"{title_prefix} (Daily)"
    elif frequency == 'W':
        index_col = 'Week_Index'
        freq_label = 'Week'
        base_title = f"{title_prefix} (Weekly)"
    elif frequency == 'M':
        index_col = 'Month_Index'
        freq_label = 'Month'
        base_title = f"{title_prefix} (Monthly)"
    elif frequency == 'Y':
        index_col = 'Year'
        freq_label = 'Year'
        base_title = f"{title_prefix} (Yearly)"
    else:
        raise ValueError("frequency must be ['D','W','M','Y']")

    all_years = sorted(df_combined['Year'].unique())

    # If yearly, simpler approach
    if frequency == 'Y':
        for year_val in all_years:
            subset = df_combined[df_combined['Year'] == year_val]
            fig.add_trace(go.Scattergeo(
                lon=subset['Longitude'],
                lat=subset['Latitude'],
                text=subset['Location'],
                marker=dict(
                    size=15,
                    color=subset['Total_Irradiance'],
                    colorscale='Viridis',
                    cmin=cmin,
                    cmax=cmax,
                    line=dict(width=1, color='black'),
                    colorbar=dict(title="Irradiance (W/m²)", len=0.4)
                ),
                mode='markers',
                name=str(year_val),
                visible=False,
                hovertemplate=(f"<b>%{{text}}</b><br>Year: {year_val}<br>"
                               "Irradiance: %{marker.color:.2f} W/m²<extra></extra>")
            ))
        # Make the first year's trace visible
        if len(fig.data) > 0:
            fig.data[0].visible = True

        slider_steps = []
        for i, year_val in enumerate(all_years):
            step = dict(
                method='update',
                args=[
                    {'visible': [False]*len(fig.data)},
                    {'title': f"{base_title} - Year {year_val}"}
                ],
                label=str(year_val)
            )
            step['args'][0]['visible'][i] = True
            slider_steps.append(step)

        fig.update_layout(
            template='plotly_white',
            title=dict(text=base_title, x=0.5),
            geo=dict(scope='usa'),
            sliders=[dict(
                active=0,
                steps=slider_steps,
                currentvalue=dict(prefix="Year: ", font=dict(size=16, color='#000'))
            )],
            margin=dict(l=30, r=30, t=80, b=40),
            showlegend=False
        )
    else:
        # daily, weekly, monthly
        trace_meta = []
        for year_val in all_years:
            df_year = df_combined[df_combined['Year'] == year_val]
            unique_indices = sorted(df_year[index_col].unique())
            for idx_val in unique_indices:
                slice_data = df_year[df_year[index_col] == idx_val]
                if slice_data.empty:
                    continue

                rep_time = slice_data['time'].min() if 'time' in slice_data.columns else None
                if frequency == 'D':
                    date_label = rep_time.strftime('%Y-%m-%d') if rep_time else f"{freq_label} {idx_val}"
                elif frequency == 'W':
                    date_label = f"Week of {rep_time.strftime('%Y-%m-%d')}" if rep_time else f"{freq_label} {idx_val}"
                else:  # M
                    date_label = rep_time.strftime('%B %Y') if rep_time else f"{freq_label} {idx_val}"

                trace_name = f"{frequency}_{year_val}_{idx_val}"
                fig.add_trace(go.Scattergeo(
                    lon=slice_data['Longitude'],
                    lat=slice_data['Latitude'],
                    text=slice_data['Location'],
                    marker=dict(
                        size=15,
                        color=slice_data['Total_Irradiance'],
                        colorscale='Viridis',
                        cmin=cmin,  # single scale for entire category
                        cmax=cmax,
                        line=dict(width=1, color='black'),
                        colorbar=dict(title="Irradiance (W/m²)", len=0.4)
                    ),
                    mode='markers',
                    name=trace_name,
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        f"Year: {year_val}<br>"
                        f"{freq_label} Index: {idx_val}<br>"
                        "Irradiance: %{marker.color:.2f} W/m²<extra></extra>"
                    ),
                    visible=False
                ))
                current_trace_index = len(fig.data) - 1
                trace_meta.append((year_val, date_label, current_trace_index))

        if len(fig.data) > 0:
            fig.data[0].visible = True

        slider_template = dict(
            active=0,
            pad={"t": 50, "b": 10},
            steps=[],
            currentvalue=dict(prefix=f"{freq_label}: ", font=dict(size=16, color='#000'))
        )

        dropdown_buttons = []
        for y in all_years:
            # gather traces for that year
            year_traces = [t for t in trace_meta if t[0] == y]
            steps_for_year = []
            for (yr, lbl, trace_idx) in year_traces:
                step = dict(
                    method='update',
                    args=[
                        {'visible': [False]*len(fig.data)},
                        {'title': f"{base_title} - Year {y}"}
                    ],
                    label=lbl
                )
                step['args'][0]['visible'][trace_idx] = True
                steps_for_year.append(step)

            visible_for_button = [False]*len(fig.data)
            if steps_for_year:
                first_idx = steps_for_year[0]['args'][0]['visible'].index(True)
                visible_for_button[first_idx] = True

            button = dict(
                label=str(y),
                method='update',
                args=[
                    {'visible': visible_for_button},
                    {
                        'title': f"{base_title} - Year {y}",
                        'sliders': [dict(
                            steps=steps_for_year,
                            active=0,
                            currentvalue=dict(prefix=f"{freq_label}: ", font=dict(size=16, color='#000'))
                        )]
                    }
                ]
            )
            dropdown_buttons.append(button)

        fig.update_layout(
            template='plotly_white',
            title=dict(text=base_title, x=0.5),
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
            updatemenus=[
                dict(
                    active=0,
                    buttons=dropdown_buttons,
                    x=0.0, y=1.15,
                    xanchor='left', yanchor='top',
                    pad={'r': 10, 't': 10},
                    showactive=True,
                    direction='down'
                )
            ],
            sliders=[slider_template],
            paper_bgcolor='#f4f4f4',
            margin=dict(l=30, r=30, t=90, b=40),
            showlegend=False
        )

    fig.write_html(output_path)
    print(f"[Heatmaps] {frequency.upper()} interactive heatmap saved -> {output_path}")