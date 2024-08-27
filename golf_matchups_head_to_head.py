# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 16:10:11 2021

@author: Austin Powell
"""
import pandas as pd
from datetime import datetime

now=datetime.now()
today=now.strftime("%Y-%m-%d")

market_list=['tournament_matchups','round_matchups']

for market in market_list:

    ####Grabs the matchup odds from data golf APIand cleans for the sportbook we can access
    CSV_URL='https://feeds.datagolf.com/betting-tools/matchups?tour=pga&market='+market+'&file_format=csv&odds_format=decimal&key=e372499bd7c3b6da5defd535d951'
    
    matchups=pd.read_csv(CSV_URL)
    start_cols=['event_name','market','p1_dg_id','p1_player_name','p2_dg_id','p2_player_name','datagolf_p1','datagolf_p2']
    last_cols=[col for col in matchups.columns if col not in start_cols]
    last_cols=sorted(last_cols)
    columns=start_cols + last_cols
    columns.append(columns.pop(columns.index('last_updated')))
    matchups=matchups[columns]
    
    
    implied_url='https://feeds.datagolf.com/betting-tools/matchups?tour=pga&market='+market+'&file_format=csv&odds_format=percent&key=e372499bd7c3b6da5defd535d951'
    implied_matchups=pd.read_csv(implied_url)
    implied_matchups=implied_matchups[['p1_dg_id','p2_dg_id','ties','datagolf_p1','datagolf_p2']]
    
    matchups=pd.merge(matchups,implied_matchups,how='left',on=['ties','p1_dg_id','p2_dg_id']).rename(columns={'datagolf_p1_x':'datagolf_p1_odds','datagolf_p2_x':'datagolf_p2_odds',
                                                                                                              'datagolf_p1_y':'datagolf_p1_%','datagolf_p2_y':'datagolf_p2_%'})
    
    start_cols=['event_name','market','p1_dg_id','p1_player_name','p2_dg_id','p2_player_name','datagolf_p1_%','datagolf_p2_%','datagolf_p1_odds','datagolf_p2_odds']
    last_cols=[col for col in matchups.columns if col not in start_cols]
    last_cols=sorted(last_cols)
    columns=start_cols + last_cols
    columns.append(columns.pop(columns.index('last_updated')))
    matchups=matchups[columns]
    matchups=matchups[matchups['ties']=='void'].drop(columns='ties')
    
    ###get the OWGR and the Golf Data Rankings
    rankings_url='https://feeds.datagolf.com/preds/get-dg-rankings?file_format=csv&key=e372499bd7c3b6da5defd535d951'
    
    rankings=pd.read_csv(rankings_url)
    rankings=rankings[['dg_id','datagolf_rank','owgr_rank','player_name']]
    
    
    ###merge the rankings and the bets and return only pertitnent columns
    matchups=pd.merge(matchups,rankings[['dg_id','datagolf_rank','owgr_rank']].add_prefix('p1_'),how='left',left_on='p1_dg_id',right_on='p1_dg_id')
    matchups=pd.merge(matchups,rankings[['dg_id','datagolf_rank','owgr_rank']].add_prefix('p2_'),how='left',left_on='p2_dg_id',right_on='p2_dg_id')
    
    if market=='round_matchups':
        start_cols=['event_name','round_num','market','p1_dg_id','p1_player_name','p2_dg_id','p2_player_name','p1_datagolf_rank','p2_datagolf_rank','p1_owgr_rank','p2_owgr_rank','datagolf_p1_%','datagolf_p2_%','datagolf_p1_odds','datagolf_p2_odds']
    else:
        start_cols=['event_name','market','p1_dg_id','p1_player_name','p2_dg_id','p2_player_name','p1_datagolf_rank','p2_datagolf_rank','p1_owgr_rank','p2_owgr_rank','datagolf_p1_%','datagolf_p2_%','datagolf_p1_odds','datagolf_p2_odds']
    last_cols=[col for col in matchups.columns if col not in start_cols]
    last_cols=[x for x in last_cols if "tie" not in x]
    last_cols=sorted(last_cols)
    columns=start_cols + last_cols
    columns.append(columns.pop(columns.index('last_updated')))
    matchups=matchups[columns].drop(columns=['last_updated','p1_win_prob','p2_win_prob'])
    try:
        matchups=matchups.drop(columns=['bet365_tie'])
    except:
        print('No tie stuff')
    try:
        matchups=matchups.drop(columns=['datagolf_tie'])
    except:
        print('No tie stuff')
    
    tournament=matchups['event_name'].unique()[0]
    matchups.to_csv('data/matchup_bets/'+market+'_'+tournament+'_'+today+'_golf_matchups.csv',index=False)
    
    
    ####### compares the differences of bovada and betonline lines versus the datagolf line, then finds when there is over a 2% difference and classifies
    ######## as a good bet
    differences=matchups
    
    last_cols=[col for col in differences.columns if col not in start_cols]
    last_cols=sorted(last_cols)
    columns=start_cols + last_cols
    differences=differences[columns]
    
    good_bets_list=[]
    for col in last_cols:
        if 'p1' in col:
            differences[col+'_exp_value']=differences['datagolf_p1_%']*differences[col]
            differences=differences.drop(columns=col)
        elif 'p2' in col:
            differences[col+'_exp_value']=differences['datagolf_p2_%']*differences[col]
            differences=differences.drop(columns=col)
            
    for col in last_cols:
            good_bets=differences[differences[col+'_exp_value']>=1]
            good_bets_list.append(good_bets)
    
    all_good_bets=pd.concat(good_bets_list).drop_duplicates()
    all_good_bets.to_csv('data/good_bets/'+market+'_'+tournament+'_'+today+'.csv',index=False)
    

    print('*******DONE!!!!*******')

print('**********NOW TIME FOR 3-BALLS*************')

market='3_balls'
CSV_URL='https://feeds.datagolf.com/betting-tools/matchups?tour=pga&market='+market+'&file_format=csv&odds_format=decimal&key=e372499bd7c3b6da5defd535d951'
    
matchups=pd.read_csv(CSV_URL)
start_cols=['event_name','market','p1_dg_id','p1_player_name','p2_dg_id','p2_player_name','p3_dg_id','p3_player_name','datagolf_p1','datagolf_p2','datagolf_p3']
last_cols=[col for col in matchups.columns if col not in start_cols]
last_cols=sorted(last_cols)
columns=start_cols + last_cols
columns.append(columns.pop(columns.index('last_updated')))
matchups=matchups[columns]


implied_url='https://feeds.datagolf.com/betting-tools/matchups?tour=pga&market='+market+'&file_format=csv&odds_format=percent&key=e372499bd7c3b6da5defd535d951'
implied_matchups=pd.read_csv(implied_url)
implied_matchups=implied_matchups[['p1_dg_id','p2_dg_id','p3_dg_id','ties','datagolf_p1','datagolf_p2','datagolf_p3']]

matchups=pd.merge(matchups,implied_matchups,how='left',on=['ties','p1_dg_id','p2_dg_id','p3_dg_id']).rename(columns={'datagolf_p1_x':'datagolf_p1_odds','datagolf_p2_x':'datagolf_p2_odds','datagolf_p3_x':'datagolf_p3_odds',
                                                                                                          'datagolf_p1_y':'datagolf_p1_%','datagolf_p2_y':'datagolf_p2_%','datagolf_p3_y':'datagolf_p3_%'})

start_cols=['event_name','round_num','market','p1_dg_id','p1_player_name','p2_dg_id','p2_player_name','p3_dg_id','p3_player_name','datagolf_p1_%','datagolf_p2_%','datagolf_p3_%','datagolf_p1_odds','datagolf_p2_odds','datagolf_p3_odds']
last_cols=[col for col in matchups.columns if col not in start_cols]
last_cols=sorted(last_cols)
columns=start_cols + last_cols
columns.append(columns.pop(columns.index('last_updated')))
matchups=matchups[columns].drop(columns='ties')


###get the OWGR and the Golf Data Rankings
rankings_url='https://feeds.datagolf.com/preds/get-dg-rankings?file_format=csv&key=e372499bd7c3b6da5defd535d951'

rankings=pd.read_csv(rankings_url)
rankings=rankings[['dg_id','datagolf_rank','owgr_rank','player_name']]


###merge the rankings and the bets and return only pertitnent columns
matchups=pd.merge(matchups,rankings[['dg_id','datagolf_rank','owgr_rank']].add_prefix('p1_'),how='left',left_on='p1_dg_id',right_on='p1_dg_id')
matchups=pd.merge(matchups,rankings[['dg_id','datagolf_rank','owgr_rank']].add_prefix('p2_'),how='left',left_on='p2_dg_id',right_on='p2_dg_id')
matchups=pd.merge(matchups,rankings[['dg_id','datagolf_rank','owgr_rank']].add_prefix('p3_'),how='left',left_on='p3_dg_id',right_on='p3_dg_id')

start_cols=['event_name','round_num','market','p1_dg_id','p1_player_name','p2_dg_id','p2_player_name','p3_dg_id','p3_player_name','p1_datagolf_rank','p2_datagolf_rank','p3_datagolf_rank','p1_owgr_rank','p2_owgr_rank','p3_owgr_rank','datagolf_p1_%','datagolf_p2_%','datagolf_p3_%','datagolf_p1_odds','datagolf_p2_odds','datagolf_p3_odds']
last_cols=[col for col in matchups.columns if col not in start_cols]
last_cols=[x for x in last_cols if "tie" not in x]
last_cols=sorted(last_cols)
columns=start_cols + last_cols
columns.append(columns.pop(columns.index('last_updated')))
matchups=matchups[columns].drop(columns=['last_updated'])

tournament=matchups['event_name'].unique()[0]
matchups.to_csv('data/matchup_bets/'+market+'_'+tournament+'_'+today+'_golf_matchups.csv',index=False)


differences=matchups
    
last_cols=[col for col in differences.columns if col not in start_cols]
last_cols=sorted(last_cols)
columns=start_cols + last_cols
differences=differences[columns]

good_bets_list=[]
for col in last_cols:
    if 'p1' in col:
        differences[col+'_exp_value']=differences['datagolf_p1_%']*differences[col]
        differences=differences.drop(columns=col)
    elif 'p2' in col:
        differences[col+'_exp_value']=differences['datagolf_p2_%']*differences[col]
        differences=differences.drop(columns=col)
    elif 'p3' in col:
        differences[col+'_exp_value']=differences['datagolf_p3_%']*differences[col]
        differences=differences.drop(columns=col)
        
for col in last_cols:
        good_bets=differences[differences[col+'_exp_value']>=1]
        good_bets_list.append(good_bets)

all_good_bets=pd.concat(good_bets_list).drop_duplicates()
all_good_bets.to_csv('data/good_bets/'+market+'_'+tournament+'_'+today+'.csv',index=False)
