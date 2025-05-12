# Copyright 2025 by John Lamb
# Analyse a sleep position log from RPi Pico based sleep position monitor

import pandas as pd
import matplotlib.pyplot as plt
import math

inFileName='SM204526.csv'

positionValues={'Supine':0,'Prone':-2,'Left':-1,'Right':1,'Standing':2}
lastPosition='Supine'
lastPosNumeric=0

# Import into a new Pandas dataframe
header_list=["Time","Position"]
parse_dates=['Time']
f=open(inFileName,'r')
df = pd.read_csv(f,names=header_list,parse_dates=parse_dates)
f.close()

df['Position']=df['Position'].map(lambda name: name.strip())
df['PosNumeric']=df['Position'].map(lambda x: positionValues[x])
df['Position']=df['Position'].astype('string')
df['Duration']=0.0

start_datetime_str=df.at[0,'Time'].strftime('%d %b %Y, %I:%M%p')
end_datetime_str=df.at[len(df)-1,'Time'].strftime('%d %b %Y, %I:%M%p')
delta=df.at[len(df)-1,'Time']-df.at[0,'Time']
elapsed_time=delta.total_seconds()/60
elapsed_time_str=f"{elapsed_time//60:.0f} hours {elapsed_time%60:.0f} minutes"

#Calculate durations from timestamps
for i in range(0,len(df)-1):
    a=df.at[i,'Time']
    b=df.at[i+1,'Time']
    df.at[i,'Duration']=(b-a).total_seconds()

# Generate a totals_df dataframe for the summary
totals_df=df.groupby('Position')['Duration'].sum()/60
totals_df=totals_df.reset_index()
totals_df['Duration'] = totals_df['Duration'].apply(lambda x: math.ceil(x))

# Generate a pie plot for the durations
pie_fig, ax = plt.subplots()
pie_fig.set_size_inches(4,4)
totals_df.plot.pie(ax=ax,x='Position',y='Duration',labels=totals_df['Position'],autopct='%1.1f%%')
ax.set_ylabel(None)
ax.legend_ = None
#plt.show()

# Set index to enable resampling
df = df.set_index('Time')

# Resample to every second, filling missing readings with last valid reading
# then resample to minutely

# Upsample to seconds
rdf= df.asfreq(freq='1s', method='ffill')
rdf=rdf.asfreq(freq='60s')

# Generate a timeline plot
linechart_fig,ax=plt.subplots()
linechart_fig.set_figwidth(11.2)
linechart_fig.set_figheight(2)
rdf.plot(ax=ax, kind='line',y='PosNumeric')
ax.set_yticks([-2,-1, 0, 1,2])
ax.set_yticklabels(("Prone","Left","Supine","Right","Standing"))
ax.legend_ = None
#plt.show()

