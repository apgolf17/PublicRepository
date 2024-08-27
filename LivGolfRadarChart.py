import pandas as pd
import matplotlib.pyplot as plt
import pyodbc
import numpy as np
from math import acos, degrees, radians, cos, sin, atan
import plotly.graph_objects as go
import plotly.offline as pyo



majesticks_ids = ['11','32','61','40']

conn = pyodbc.connect(driver='{SQL Server}', server='(local)', database='LIVGolf',               
           trusted_connection='yes')

cursor = conn.cursor()


shot_call = f"""select *
from LIVGolf.dbo.HoleByHole

"""

df = pd.read_sql(shot_call, conn).drop_duplicates()



## Fairways
fairways = df.query('FIR == "true"').groupby(['playerId','tournamentId'])['FIR'].count().reset_index()

possible_fairways = df.query('holePar in ["4","5"]').groupby(['playerId','tournamentId'])['FIR'].count().reset_index()\
    .rename(columns = {'FIR':'possibleFairways'})

fairway_df = pd.merge(fairways, possible_fairways, how = 'left', on =['playerId','tournamentId'])

fairway_df['FIR%'] = fairway_df['FIR']/fairway_df['possibleFairways']



event_average_fwys = fairway_df.groupby('tournamentId')['FIR%'].mean().reset_index().rename(columns = {'FIR%':'fieldAvg'})
fairway_df = pd.merge(fairway_df, event_average_fwys, how= 'left', on = 'tournamentId')
fairway_df['pctAboveField'] = fairway_df['FIR%'] - fairway_df['fieldAvg']

season_fairways = fairway_df.groupby('playerId').agg(total = ('pctAboveField','sum'), count = ('pctAboveField','count')).reset_index()
season_fairways = season_fairways.query('count > 2')
season_fairways['fwyPctAboveField'] = season_fairways['total']/season_fairways['count']

season_fairways['fairwayRank']=season_fairways['fwyPctAboveField'].rank(method= 'min', ascending = False)
season_fairways['fairwayPercentileRank']=season_fairways['fwyPctAboveField'].rank(method = 'min', pct=True)

export_fairways = season_fairways[['playerId','fwyPctAboveField','fairwayRank','fairwayPercentileRank']]

a_fairway_df = fairway_df.groupby('playerId').agg(fairways = ('FIR','sum'),possibleFairways = ('possibleFairways','sum'), pctAboveField =('pctAboveField','mean'))
a_fairway_df['FIR%'] = a_fairway_df['fairways']/a_fairway_df['possibleFairways']
a_fairway_df['rank'] = a_fairway_df['FIR%'].rank(method= 'min', ascending = False)

## Greens
greens = df.query('GIR == "true"').groupby(['playerId','tournamentId'])['GIR'].count().reset_index()

possible_greens = df.groupby(['playerId','tournamentId'])['GIR'].count().reset_index()\
    .rename(columns = {'GIR':'possibleGreens'})

green_df = pd.merge(greens, possible_greens, how = 'left', on =['playerId','tournamentId'])

green_df['GIR%'] = green_df['GIR']/green_df['possibleGreens']

event_average_greens = green_df.groupby('tournamentId')['GIR%'].mean().reset_index().rename(columns = {'GIR%':'fieldAvg'})
green_df = pd.merge(green_df, event_average_greens, how= 'left', on = 'tournamentId')
green_df['pctAboveField'] = green_df['GIR%'] - green_df['fieldAvg']

season_greens = green_df.groupby('playerId').agg(total = ('pctAboveField','sum'), count = ('pctAboveField','count')).reset_index()
season_greens = season_greens.query('count > 2')
season_greens['greenPctAboveField'] = season_greens['total']/season_greens['count']

season_greens['greenRank']=season_greens['greenPctAboveField'].rank(method= 'min', ascending = False)
season_greens['greenPercentileRank']=season_greens['greenPctAboveField'].rank(method = 'min', pct=True)

export_greens = season_greens[['playerId','greenPctAboveField','greenRank','greenPercentileRank']]


a_green_df = green_df.groupby('playerId').agg(fairways = ('GIR','sum'),possibleFairways = ('possibleGreens','sum'), pctAboveField =('pctAboveField','mean'))
a_green_df['FIR%'] = a_green_df['fairways']/a_green_df['possibleFairways']
a_green_df['rank'] = a_green_df['FIR%'].rank(method= 'min', ascending = False)


## Greens from Fairway
greens_fwy = df.query('GIR == "true" and (FIR == "true" or holePar == "3")').groupby(['playerId','tournamentId'])['GIR'].count().reset_index()

possible_greens_fwy = df.query('(FIR == "true" or holePar == "3")').groupby(['playerId','tournamentId'])['GIR'].count().reset_index()\
    .rename(columns = {'GIR':'possibleGreens'})

greens_fwy_df = pd.merge(greens_fwy, possible_greens_fwy, how = 'left', on =['playerId','tournamentId'])

greens_fwy_df['GIR%'] = greens_fwy_df['GIR']/greens_fwy_df['possibleGreens']

event_average_greens_fwy = greens_fwy_df.groupby('tournamentId')['GIR%'].mean().reset_index().rename(columns = {'GIR%':'fieldAvg'})
greens_fwy_df = pd.merge(greens_fwy_df, event_average_greens_fwy, how= 'left', on = 'tournamentId')
greens_fwy_df['pctAboveField'] = greens_fwy_df['GIR%'] - greens_fwy_df['fieldAvg']

season_greens_fwy = greens_fwy_df.groupby('playerId').agg(total = ('pctAboveField','sum'), count = ('pctAboveField','count')).reset_index()
season_greens_fwy = season_greens_fwy.query('count > 2')
season_greens_fwy['greenFwyPctAboveField'] = season_greens_fwy['total']/season_greens_fwy['count']

season_greens_fwy['greenFwyRank']=season_greens_fwy['greenFwyPctAboveField'].rank(method= 'min', ascending = False)
season_greens_fwy['greenFwyPercentileRank']=season_greens_fwy['greenFwyPctAboveField'].rank(method = 'min', pct=True)

export_greens_fwy = season_greens_fwy[['playerId','greenFwyPctAboveField','greenFwyRank','greenFwyPercentileRank']]


## Greens from Rough
greens_rgh = df.query('GIR == "true" and (FIR == "false" and holePar != "3")').groupby(['playerId','tournamentId'])['GIR'].count().reset_index()

possible_greens_rgh = df.query('(FIR == "false" or holePar != "3")').groupby(['playerId','tournamentId'])['GIR'].count().reset_index()\
    .rename(columns = {'GIR':'possibleGreens'})

greens_rgh_df = pd.merge(greens_rgh, possible_greens_rgh, how = 'left', on =['playerId','tournamentId'])

greens_rgh_df['GIR%'] = greens_rgh_df['GIR']/greens_rgh_df['possibleGreens']

event_average_greens_rgh = greens_rgh_df.groupby('tournamentId')['GIR%'].mean().reset_index().rename(columns = {'GIR%':'fieldAvg'})
greens_rgh_df = pd.merge(greens_rgh_df, event_average_greens_rgh, how= 'left', on = 'tournamentId')
greens_rgh_df['pctAboveField'] = greens_rgh_df['GIR%'] - greens_rgh_df['fieldAvg']

season_greens_rgh = greens_rgh_df.groupby('playerId').agg(total = ('pctAboveField','sum'), count = ('pctAboveField','count')).reset_index()
season_greens_rgh = season_greens_rgh.query('count > 2')
season_greens_rgh['greenRghPctAboveField'] = season_greens_rgh['total']/season_greens_rgh['count']

season_greens_rgh['greenRghRank']=season_greens_rgh['greenRghPctAboveField'].rank(method= 'min', ascending = False)
season_greens_rgh['greenRghPercentileRank']=season_greens_rgh['greenRghPctAboveField'].rank(method = 'min', pct=True)

export_greens_rgh = season_greens_rgh[['playerId','greenRghPctAboveField','greenRghRank','greenRghPercentileRank']]







## Driving Distance
driveDistance = df[df['driveDistance'].notnull()]
driveDistance['driveDistance'] = driveDistance['driveDistance'].astype(float)

distance_df = driveDistance.groupby(['playerId','tournamentId','roundNum'])['driveDistance'].mean().reset_index()
event_round_avg_distance = distance_df.groupby(['tournamentId','roundNum'])['driveDistance'].mean().reset_index().rename(columns = {'driveDistance':'fieldAvg'})

distance_df = pd.merge(distance_df, event_round_avg_distance, how = 'left',on = ['tournamentId','roundNum'])
distance_df['distanceAboveField'] = distance_df['driveDistance'] - distance_df['fieldAvg']


season_distance = distance_df.groupby('playerId').agg(total = ('distanceAboveField','sum'), count = ('distanceAboveField','count')).reset_index()
season_distance = season_distance.query('count > 6')
season_distance['distanceAboveField'] = season_distance['total']/season_distance['count']

season_distance['distanceRank']=season_distance['distanceAboveField'].rank(method= 'min', ascending = False)
season_distance['distancePercentileRank']=season_distance['distanceAboveField'].rank(method = 'min', pct=True)

export_distance = season_distance[['playerId','distanceAboveField','distanceRank','distancePercentileRank']]


a_distance_df = distance_df.groupby('playerId').agg(distance = ('driveDistance','mean'),fieldAvg = ('fieldAvg','mean'), pctAboveField =('distanceAboveField','mean'))
a_distance_df['rank'] = a_distance_df['distance'].rank(method= 'min', ascending = False)



# Putts per GIR
gir = df.query('GIR == "true"').groupby(['playerId','tournamentId'])['GIR'].count().reset_index()
putts = df.query('GIR == "true"').groupby(['playerId','tournamentId'])['putts'].sum().reset_index()


putts_df = pd.merge(putts, gir, how = 'left', on =['playerId','tournamentId'])

putts_df['puttsPerGIR'] = putts_df['putts']/putts_df['GIR']

event_average_putts = putts_df.groupby('tournamentId')['puttsPerGIR'].mean().reset_index().rename(columns = {'puttsPerGIR':'fieldAvg'})
putts_df = pd.merge(putts_df, event_average_putts, how= 'left', on = 'tournamentId')
putts_df['puttsAboveField'] = putts_df['puttsPerGIR'] - putts_df['fieldAvg']

season_putts = putts_df.groupby('playerId').agg(total = ('puttsAboveField','sum'), count = ('puttsAboveField','count')).reset_index()
season_putts = season_putts.query('count > 2')
season_putts['puttsAboveField'] = season_putts['total']/season_putts['count']

season_putts['puttRank']=season_putts['puttsAboveField'].rank(method= 'min', ascending = True)
season_putts['puttPercentileRank']=season_putts['puttsAboveField'].rank(method = 'min', pct=True, ascending = False)

export_putts = season_putts[['playerId','puttsAboveField','puttRank','puttPercentileRank']]



# Putts per Round
putts_per_round = df.groupby(['playerId','tournamentId','roundNum'])['putts'].sum().reset_index().query('putts> 0')

event_average_putts_per_round = putts_per_round.groupby(['tournamentId','roundNum'])['putts'].mean().reset_index().rename(columns = {'putts':'fieldAvg'})


putts_per_round = pd.merge(putts_per_round, event_average_putts_per_round, how= 'left', on = ['tournamentId','roundNum'])
putts_per_round['puttsAboveField'] = putts_per_round['putts'] - putts_per_round['fieldAvg']

season_putts_per_round = putts_per_round.groupby('playerId').agg(total = ('puttsAboveField','sum'), count = ('puttsAboveField','count'), putts = ('putts','mean')).reset_index()
season_putts_per_round = season_putts_per_round.query('count > 6')
season_putts_per_round['puttsPerRoundAboveField'] = season_putts_per_round['total']/season_putts_per_round['count']

season_putts_per_round['puttsRankAfter'] = season_putts_per_round['putts'].rank(method= 'min', ascending = True)
season_putts_per_round['puttPerRoundRank']=season_putts_per_round['puttsPerRoundAboveField'].rank(method= 'min', ascending = True)
season_putts_per_round['puttPerRoundPercentileRank']=season_putts_per_round['puttsPerRoundAboveField'].rank(method = 'min', pct=True, ascending = False)

export_putts_per_round = season_putts_per_round[['playerId','puttsPerRoundAboveField','puttPerRoundRank','puttPerRoundPercentileRank']]

a_putts_df = putts_per_round.groupby('playerId').agg(putts = ('putts','mean'),fieldAvg = ('fieldAvg','mean'), pctAboveField =('puttsAboveField','mean'))
a_putts_df['rank'] = a_putts_df['putts'].rank(method= 'min', ascending = True)


################################################################################################
## scoring info
scoring_info = df[df['strokes'].notnull()].query('strokes != "0"')
scoring_info['strokes'] = scoring_info['strokes'].astype(int)
scoring_info['scoreToPar'] = scoring_info['scoreToPar'].replace('E','0').astype(int)

## overall scoring

scores = scoring_info.groupby(['playerId','tournamentId','roundNum'])['strokes'].sum().reset_index().rename(columns = {'strokes':'roundScore'})
field_avg_score = scores.groupby(['tournamentId','roundNum'])['roundScore'].mean().reset_index().rename(columns = {'roundScore':'fieldAvg'})


scores = pd.merge(scores, field_avg_score, how = 'left',on = ['tournamentId','roundNum'])
scores['strokesGained'] = scores['fieldAvg'] - scores['roundScore']

season_strokes_gained = scores.groupby('playerId').agg(total = ('strokesGained','sum'), count = ('strokesGained','count'), strokes = ('roundScore','mean')).reset_index()
season_strokes_gained = season_strokes_gained.query('count > 6')
season_strokes_gained['strokesGained'] = season_strokes_gained['total']/season_strokes_gained['count']

season_strokes_gained['rankscroingavg'] = season_strokes_gained['strokes'].rank(method= 'min', ascending = True)
season_strokes_gained['strokesGainedRank']=season_strokes_gained['strokesGained'].rank(method= 'min' , ascending = False)
season_strokes_gained['strokesGainedPercentileRank']=season_strokes_gained['strokesGained'].rank(method = 'min', pct=True)

export_strokes_gained = season_strokes_gained[['playerId','strokesGained','strokesGainedRank','strokesGainedPercentileRank']]

## par 3 scoring

par_3_scoring = scoring_info.query('holePar == "3"').groupby(['playerId','tournamentId','roundNum'])['strokes'].mean().reset_index().rename(columns = {'strokes':'par3Scores'})
field_avg_score = par_3_scoring.groupby(['tournamentId','roundNum'])['par3Scores'].mean().reset_index().rename(columns = {'par3Scores':'fieldAvg'})

par_3_scoring = pd.merge(par_3_scoring, field_avg_score, how = 'left',on = ['tournamentId','roundNum'])
par_3_scoring['strokesGained'] = par_3_scoring['fieldAvg'] - par_3_scoring['par3Scores']

season_par_3 = par_3_scoring.groupby('playerId').agg(total = ('strokesGained','sum'), count = ('strokesGained','count'), strokes = ('par3Scores','sum')).reset_index()
season_par_3 = season_par_3.query('count > 6')
season_par_3['par3strokesGained'] = season_par_3['total']/season_par_3['count']

season_par_3['strokes'] = season_par_3['strokes']/season_par_3['count']
season_par_3['strokeRank'] = season_par_3['strokes'].rank(method= 'min', ascending = True)
season_par_3['par3Rank']=season_par_3['par3strokesGained'].rank(method= 'min' , ascending = False)
season_par_3['par3PercentileRank']=season_par_3['par3strokesGained'].rank(method = 'min', pct=True)

export_par_3 = season_par_3[['playerId','par3strokesGained','par3Rank','par3PercentileRank']]

## par 4 scoring
par_4_scoring = scoring_info.query('holePar == "4"').groupby(['playerId','tournamentId','roundNum'])['strokes'].mean().reset_index().rename(columns = {'strokes':'par4Scores'})
field_avg_score = par_4_scoring.groupby(['tournamentId','roundNum'])['par4Scores'].mean().reset_index().rename(columns = {'par4Scores':'fieldAvg'})

par_4_scoring = pd.merge(par_4_scoring, field_avg_score, how = 'left',on = ['tournamentId','roundNum'])
par_4_scoring['strokesGained'] = par_4_scoring['fieldAvg'] - par_4_scoring['par4Scores']

season_par_4 = par_4_scoring.groupby('playerId').agg(total = ('strokesGained','sum'), count = ('strokesGained','count'), strokes = ('par4Scores','sum')).reset_index()
season_par_4 = season_par_4.query('count > 6')
season_par_4['par4strokesGained'] = season_par_4['total']/season_par_4['count']


season_par_4['strokes'] = season_par_4['strokes']/season_par_4['count']
season_par_4['strokeRank'] = season_par_4['strokes'].rank(method= 'min', ascending = True)

season_par_4['par4Rank']=season_par_4['par4strokesGained'].rank(method= 'min' , ascending = False)
season_par_4['par4PercentileRank']=season_par_4['par4strokesGained'].rank(method = 'min', pct=True)

export_par_4 = season_par_4[['playerId','par4strokesGained','par4Rank','par4PercentileRank']]


## par 5 scoring

par_5_scoring = scoring_info.query('holePar == "5"').groupby(['playerId','tournamentId','roundNum'])['strokes'].mean().reset_index().rename(columns = {'strokes':'par5Scores'})
field_avg_score = par_5_scoring.groupby(['tournamentId','roundNum'])['par5Scores'].mean().reset_index().rename(columns = {'par5Scores':'fieldAvg'})

par_5_scoring = pd.merge(par_5_scoring, field_avg_score, how = 'left',on = ['tournamentId','roundNum'])
par_5_scoring['strokesGained'] = par_5_scoring['fieldAvg'] - par_5_scoring['par5Scores']

season_par_5 = par_5_scoring.groupby('playerId').agg(total = ('strokesGained','sum'), count = ('strokesGained','count'), strokes = ('par5Scores','sum')).reset_index()
season_par_5 = season_par_5.query('count > 6')
season_par_5['par5strokesGained'] = season_par_5['total']/season_par_5['count']


season_par_5['strokes'] = season_par_5['strokes']/season_par_5['count']
season_par_5['strokeRank'] = season_par_5['strokes'].rank(method= 'min', ascending = True)

season_par_5['par5Rank']=season_par_5['par5strokesGained'].rank(method= 'min' , ascending = False)
season_par_5['par5PercentileRank']=season_par_5['par5strokesGained'].rank(method = 'min', pct=True)

export_par_5 = season_par_5[['playerId','par5strokesGained','par5Rank','par5PercentileRank']]


# ## Birdies

birdie_df = scoring_info.query('scoreToPar < 0').groupby(['playerId','tournamentId','roundNum'])['strokes'].count().reset_index().rename(columns = {'strokes':'parBreakers'})
field_avg_score = birdie_df.groupby(['tournamentId','roundNum'])['parBreakers'].mean().reset_index().rename(columns = {'parBreakers':'fieldAvg'})

birdie_df = pd.merge(birdie_df, field_avg_score, how = 'left',on = ['tournamentId','roundNum'])
birdie_df['parBreakersAboveField'] = birdie_df['parBreakers'] - birdie_df['fieldAvg'] 

season_birdies= birdie_df.groupby('playerId').agg(total = ('parBreakersAboveField','sum'), count = ('parBreakersAboveField','count')).reset_index()
season_birdies = season_birdies.query('count > 6')
season_birdies['parBreakersAboveField'] = season_birdies['total']/season_birdies['count']

season_birdies['parBreakerRank']=season_birdies['parBreakersAboveField'].rank(method= 'min' , ascending = False)
season_birdies['parBreakerPercentileRank']=season_birdies['parBreakersAboveField'].rank(method = 'min', pct=True)

export_birdies = season_birdies[['playerId','parBreakersAboveField','parBreakerRank','parBreakerPercentileRank']]

## Bogies

bogey_df = scoring_info.query('scoreToPar > 0').groupby(['playerId','tournamentId','roundNum'])['strokes'].count().reset_index().rename(columns = {'strokes':'overParScores'})
field_avg_score = bogey_df.groupby(['tournamentId','roundNum'])['overParScores'].mean().reset_index().rename(columns = {'overParScores':'fieldAvg'})

bogey_df = pd.merge(bogey_df, field_avg_score, how = 'left',on = ['tournamentId','roundNum'])
bogey_df['overParAboveField'] = bogey_df['overParScores'] - bogey_df['fieldAvg'] 

season_bogies= bogey_df.groupby('playerId').agg(total = ('overParAboveField','sum'), count = ('overParAboveField','count')).reset_index()
season_bogies = season_bogies.query('count > 6')
season_bogies['overParAboveField'] = season_bogies['total']/season_bogies['count']

season_bogies['overParRank']=season_bogies['overParAboveField'].rank(method= 'min' )
season_bogies['overParPercentileRank']=season_bogies['overParAboveField'].rank(method = 'min', pct=True, ascending = False)

export_bogies = season_bogies[['playerId','overParAboveField','overParRank','overParPercentileRank']]



########################################################################################################
total_df = pd.merge(export_fairways, export_greens, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_greens_rgh, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_greens_fwy, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_distance, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_putts, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_putts_per_round, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_strokes_gained, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_par_3, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_par_4, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_par_5, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_birdies, how = 'left', on ='playerId')
total_df = pd.merge(total_df, export_bogies, how = 'left', on ='playerId')


this_df = total_df.query('playerId == "40"')

player = 'Lee Westwood'

title = f"<b>{player} 2022 LIV Stats<b>"
title_2 = f"<b>{player} 2022 LIV Scoring Stats<b>"

fairway_rank = round(this_df['fairwayPercentileRank'].item()*100)
distance_rank = round(this_df['distancePercentileRank'].item()*100)
green_rank = round(this_df['greenPercentileRank'].item()*100)
green_fwy_rank = round(this_df['greenFwyPercentileRank'].item()*100)
green_rgh_rank = round(this_df['greenRghPercentileRank'].item()*100)
putting_rank = round(this_df['puttPercentileRank'].item()*100)
putting_per_round = round(this_df['puttPerRoundPercentileRank'].item()*100)
strokes_gained_rank = round(this_df['strokesGainedPercentileRank'].item()*100)
par_3_rank = round(this_df['par3PercentileRank'].item()*100)
par_4_rank = round(this_df['par4PercentileRank'].item()*100)
par_5_rank = round(this_df['par5PercentileRank'].item()*100)
birdie_rank = round(this_df['parBreakerPercentileRank'].item()*100)
bogey_rank = round(this_df['overParPercentileRank'].item()*100)


categories = ['<b>Driving <br>Accuracy<b>', '<b>Driving <br>Distance<b>', '<b>Greens <br>in Regulation<b>', '<b>GIR from <br>Fairway<b>', '<b>GIR from <br>Non-Fairway<b>', '<b>Putts <br>per GIR<b>','<b>Putts <br>per Round<b>']
categories_2 =['<b>Scoring <br>Average<b>','<b>Par 3 <br>Scoring<b>','<b>Par 4 <br>Scoring<b>','<b>Par 5 <br>Scoring<b>','<b>Par <br>Breakers<b>','<b>Bogey+ <br>Avoidance<b>']


categories = [*categories, categories[0]]
categories_2 = [*categories_2, categories_2[0]]


stats = [fairway_rank, distance_rank, green_rank,green_fwy_rank,green_rgh_rank, putting_rank, putting_per_round] 
stats_2 = [strokes_gained_rank, par_3_rank, par_4_rank, par_5_rank, birdie_rank, bogey_rank]

stats = [*stats, stats[0]]
stats_2 = [*stats_2, stats_2[0]]



list_1 = [stats, categories, title]
list_2 = [stats_2, categories_2, title_2]


fig = go.Figure(
    data=[
        go.Scatterpolar(mode = 'lines+text',
                        r=list_1[0], 
                        theta=list_1[1],
                        fill = 'toself', 
                        text = list_1[0], 
                        textposition='top center',
                        textfont=dict(
                        size=25,
                        color="black"
                    )),
    ],
    layout=go.Layout(
        title=go.layout.Title(text=list_1[2],
                              font = {'family':'tahoma',
                                      'size':48},
                              xref = 'paper',
                              xanchor = 'center',
                              x=.5),
        polar={'radialaxis': {'visible': True,
                              'range':[0,100],
                              'tickfont':{'size':10}},
               'angularaxis':{'tickfont':{'size':28}}},
        
    )
)
fig.update_layout(
    font=dict(
        family="Oswald, sans-serif",
        size=18,  # Set the font size here
    )
)
fig.update_traces( line = {'color':'blue'})

pyo.plot(fig)

