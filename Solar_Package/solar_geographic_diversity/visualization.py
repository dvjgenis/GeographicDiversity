# GeographicDiversity_Package/Solar_Package/solar_geographic_diversity/visualization.py

import folium
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os

def create_map(df_locations, output_path='map_with_labels.html'):
    m = folium.Map(location=[38.5, -90.0], zoom_start=6)
    for _, row in df_locations.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Name']}, {row['State']}",
            tooltip=row['Name']
        ).add_to(m)
    m.save(output_path)

def plot_power_comparison(df1_filtered, df2_filtered, label1, label2, start_date, end_date, output_path='power_comparison.png'):
    plt.figure(figsize=(14, 7))
    plt.plot(df1_filtered['Datetime'], df1_filtered['Power_Output'], marker='o', label=f'{label1}')
    plt.plot(df2_filtered['Datetime'], df2_filtered['Power_Output'], marker='o', label=f'{label2}')
    plt.xlabel('Date and Time')
    plt.ylabel('Power Output (MW)')
    plt.title(f'Power Output Comparison\n{label1} vs {label2} ({start_date} - {end_date})')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_interactive_heatmap(df_combined, frequency, min_val, max_val, title, output_path):
    fig = go.Figure()

    if frequency == 'D':
        index_col = 'Day_Index'
    elif frequency == 'W':
        index_col = 'Week_Index'
    elif frequency == 'M':
        index_col = 'Month_Index'
    else:
        raise ValueError("Frequency must be 'D', 'W', or 'M'")

    unique_indices = df_combined[index_col].unique()

    for idx in unique_indices:
        subset = df_combined[df_combined[index_col] == idx]
        fig.add_trace(go.Scattergeo(
            lon=subset['Longitude'],
            lat=subset['Latitude'],
            text=subset.apply(lambda row: f"{row['Location']} ({row.get('Date', row.get('Month', idx))}): {row['Total_Irradiance']:.2f} Wh/m²", axis=1),
            marker=dict(
                size=25,
                color=subset['Total_Irradiance'],
                colorscale='Viridis',
                cmin=min_val,
                cmax=max_val,
                colorbar_title="Irradiance (Wh/m²)"
            ),
            mode='markers',
            name=str(idx),
            visible=False
        ))

    # Make the first trace visible
    if len(fig.data) > 0:
        fig.data[0].visible = True

    steps = []
    for i, idx in enumerate(unique_indices):
        step = dict(
            method='update',
            args=[{'visible': [False]*len(fig.data)}, {'title': title}],
            label=str(idx)
        )
        step['args'][0]['visible'][i] = True
        steps.append(step)

    sliders = [dict(
        active=0,
        pad={"t": 50, "b": 10},
        steps=steps,
        currentvalue=dict(prefix=f"{frequency}: ", font=dict(size=16, color='#000'))
    )]

    fig.update_layout(
        template='plotly_white',
        title=dict(text=title, x=0.5),
        geo=dict(scope='usa'),
        sliders=sliders,
        margin=dict(l=20, r=20, t=80, b=20)
    )

    fig.write_html(output_path)