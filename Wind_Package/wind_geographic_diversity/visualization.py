# GeographicDiversity_Package/Wind_Package/wind_geographic_diversity/visualization.py

import folium
import matplotlib.pyplot as plt
import seaborn as sns

def create_map(df_all, output_path='map_with_labels.html'):
    """Create and save a Folium map with location markers."""
    m = folium.Map(location=[40.0, -90.0], zoom_start=5)
    for _, row in df_all.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Name']}, {row['State']}",
            tooltip=row['Name']
        ).add_to(m)
    m.save(output_path)

def plot_absolute_difference(df_filtered, output_path='absolute_difference_plot.png'):
    """Plot the absolute difference in power outputs between two sites."""
    plt.figure(figsize=(12, 6))
    plt.plot(df_filtered['Time'], df_filtered['Absolute_Difference'],
             label='Absolute Difference', color='green', linestyle='--', marker='o')
    plt.title('Hourly Power Outputs and Absolute Difference')
    plt.xlabel('Date')
    plt.ylabel('Power Output (MW)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()