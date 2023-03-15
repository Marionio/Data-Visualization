import os
import glob
import geoplot
import geopandas
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib as mpl
import geoplot.crs as gcrs #Projection
import matplotlib.pyplot as plt

space = np.linspace(0.5,1,280) # 280 equal numbers between 0.5 and 1
space = np.insert(space, 0,0) # adds a 0 before the 0.5 (0,0.5,...)
color_red = mpl.cm.Reds(space) # get the Reds colormap with these ^ specifications
color_red = mpl.colors.ListedColormap(color_red[0:,:-1]) # makes a colormap from a list of colors

color_blue = mpl.cm.Blues(np.linspace(0,0.5,10))
color_blue = mpl.colors.ListedColormap(color_blue)
im_blue = '#5AAADC' 

bank_data = pd.read_csv("US-Failed-Banks/banklist.csv") # https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/index.html FDIC failed banking institutions (03/13/23)
cities_data = pd.read_csv("US-Failed-Banks/uscities.csv") # https://simplemaps.com/data/us-cities aid dataset
contiguous_usa = geopandas.read_file(geoplot.datasets.get_path('contiguous_usa')) #geoplot native us data

bank_data.rename(columns={'Bank Name†':'Bank Name','City†':'city','State†':'state_id','Closing Date†':'Closing Date'},inplace=True)

#Merge the full name of the cities from the aid cities data
bank_data = pd.merge(bank_data[['Bank Name','Closing Date','city','state_id']],cities_data[['state_id','state_name']].drop_duplicates(subset=['state_id']),how="left", on="state_id")
#Merge the geometry from geoplot usa data
bank_data = pd.merge(bank_data, contiguous_usa[['state','geometry']], how='left', left_on='state_name',right_on='state')
#Make into a geodataframe
bank_data = geopandas.GeoDataFrame(bank_data)
#To datetime
bank_data['Closing Date'] = pd.to_datetime(bank_data['Closing Date'])
# Group by monthly data
monthly_states = bank_data.set_index('Closing Date').groupby(pd.Grouper(freq= 'M'))['state'].value_counts().unstack().fillna(0).astype(int).reindex()
# number of banks failed by state
count_states = pd.DataFrame(bank_data.state_name.value_counts()).reset_index().rename(columns={'index':'state','state_id':'Count'})
# add geometry to each state in the count dataframe
merged = pd.merge(count_states,contiguous_usa,how="left", on='state')
merged = geopandas.GeoDataFrame(merged)

output_path ='/US-Failed-Banks/images'

# months to iterate over
list_of_months = []
for x in range(0, 119):
  list_of_months.append(monthly_states.T.columns[x])

# set the min and max range for the choropleth map
vmin, vmax = 0, 90
proj = gcrs.AlbersEqualArea(central_latitude=39.5, central_longitude=-98.35)

monthly_states = pd.merge(monthly_states.T.reset_index(), contiguous_usa[['state','geometry']], how='right', left_on='state',right_on='state').fillna(0)
monthly_states.iloc[:, 1:-1] = monthly_states.iloc[:, 1:-1].cumsum(axis=1)

# print(monthly_states)
monthly_states = geopandas.GeoDataFrame(monthly_states)
print(monthly_states.iloc[:,119:120].nunique())
# start the for loop to create one map per year
for day in list_of_months: # create animation
    fig, ax = plt.subplots(subplot_kw={'projection':proj})
    geoplot.choropleth(
        monthly_states,
        hue= monthly_states[day], 
        cmap=color_red,
        zorder=-1,
        linewidth=0,
        norm=plt.Normalize(vmin=vmin, vmax=vmax),
        legend=True,
        edgecolor='white',
        ax= ax)
 
    # remove axis of chart
    plt.axis('off')

    # add text
    fig.suptitle('Banks closed in the US from OCT 2000\nTo '+ day.strftime('%b %Y').upper(), fontdict={'fontsize': '25', 'fontweight': '3'})
    plt.annotate('Source: FDIC Division of Insurance and Research', xy=(0.1, .08), xycoords='figure fraction', horizontalalignment='left', verticalalignment='top', fontsize=12, color='#555555')
    plt.annotate('Count: '+str(int(monthly_states[day].sum())), xy=(0.1, 0.9), xycoords='figure fraction', horizontalalignment='left', verticalalignment='top', fontsize=12, color='#555555')

    # this will save the figure as a png in the output path
    filepath = os.path.join(output_path, day.strftime('%b %Y').upper() + 'banks_close.png')
    chart = fig.get_figure()
    plt.savefig(filepath, dpi=150)
    plt.close()

for f in range(10): # fade in 
    fig, ax1 = plt.subplots(subplot_kw={'projection':proj})
    geoplot.choropleth(
        df=merged,
        hue= 'state_name',
        cmap=color_red,
        norm=plt.Normalize(vmin=vmin, vmax=vmax),
        projection = proj,
        legend=True, 
        ax=ax1
    )
    geoplot.polyplot(
        contiguous_usa,
        zorder=-1,
        projection = proj,
        linewidth=0,
        edgecolor='white',
        facecolor=color_blue(f),
        figsize=(12, 7),
        ax=ax1
    )

    # add text
    fig.suptitle('Banks closed in the US from OCT 2000\nTo '+ "OCT 2020", fontdict={'fontsize': '25', 'fontweight': '3'})
    plt.annotate('Source: FDIC Division of Insurance and Research', xy=(0.1, .08), xycoords='figure fraction', horizontalalignment='left', verticalalignment='top', fontsize=12, color='#555555')
    plt.annotate('Count: '+str(int(monthly_states[day].sum())), xy=(0.1, 0.8), xycoords='figure fraction', horizontalalignment='left', verticalalignment='top', fontsize=12, color='#555555')
    plt.annotate('States where a bank\n did not close', xy=(0.1, 0.9), xycoords='figure fraction', horizontalalignment='left', verticalalignment='top', fontsize=12, color=color_blue(f))

    # this will save the figure as a png in the output path
    filepath = os.path.join(output_path,str(f)+'th fade in')
    chart = fig.get_figure()
    plt.savefig(filepath, dpi=150)
    plt.close()

for f in range(10): # static image with color
    fig, ax1 = plt.subplots(subplot_kw={'projection':proj})
    geoplot.choropleth(
        df=merged,
        hue= 'state_name',
        norm=plt.Normalize(vmin=vmin, vmax=vmax),
        cmap=color_red,
        projection = proj,
        legend=True, 
        ax=ax1
    )
    geoplot.polyplot(
        contiguous_usa,
        zorder=-1,
        projection = proj,
        linewidth=0,
        edgecolor='white',
        facecolor=im_blue,
        figsize=(12, 7),
        ax=ax1
    )
    
    # add text
    fig.suptitle('Banks closed in the US from OCT 2000\nTo '+ "OCT 2020", fontdict={'fontsize': '25', 'fontweight': '3'})
    plt.annotate('Source: FDIC Division of Insurance and Research', xy=(0.1, .08), xycoords='figure fraction', horizontalalignment='left', verticalalignment='top', fontsize=12, color='#555555')
    plt.annotate('Count: '+str(int(monthly_states[day].sum())), xy=(0.1, 0.8), xycoords='figure fraction', horizontalalignment='left', verticalalignment='top', fontsize=12, color='#555555')
    plt.annotate('States where a bank\n did not close', xy=(0.1, 0.9), xycoords='figure fraction', horizontalalignment='left', verticalalignment='top', fontsize=12, color=im_blue)
    
    # this will save the figure as a png in the output path
    filepath = os.path.join(output_path,str(f)+'th static frame')
    chart = fig.get_figure()
    plt.savefig(filepath, dpi=150)
    plt.close()

# Create the frames
frames = []
imgs = glob.glob("/US-Failed-Banks/images/*.png")
imgs.sort(key=os.path.getmtime)
for i in imgs:
    new_frame = Image.open(i)
    frames.append(new_frame)

# Save into a GIF file that loops forever
frames[0].save('/US-Failed-Banks/map.gif', format='GIF',
               append_images=frames[1:],
               save_all=True,
               duration=300, loop=1)
