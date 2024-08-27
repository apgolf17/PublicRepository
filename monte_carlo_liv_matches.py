import random
import pandas as pd
import matplotlib.pyplot as plt


smash_captain = 'Ian Poulter'
smash_player_2 = 'Lee Westwood'
smash_player_3 = 'Henrik Stenson'
smash_player_4 = 'Sam Horsfield'

winners_dfs = []

team = 'Niblicks GC'

captain = 'Harold Varner III'
player_2 = 'James Piot'
player_3 = 'Hudson Swafford'
player_4 ='Turk Pettit'

sg_df = pd.read_excel('LIV/Strokes_Gained_as_of_10_20_2022.xlsx', index_col = 0)

first_ten = pd.concat([sg_df.iloc[:10]]*5)
ten_to_twenty = pd.concat([sg_df.iloc[10:20]]*4)
twenty_to_thirty = pd.concat([sg_df.iloc[20:30]]*3)
thirty_to_fourty = pd.concat([sg_df.iloc[30:40]]*2)
last_ten = sg_df.iloc[40:]

adj_sg_df = pd.concat([first_ten, ten_to_twenty,twenty_to_thirty,thirty_to_fourty, last_ten])

smash_captain_scores = adj_sg_df[smash_captain].to_list()
smash_2_scores = adj_sg_df[smash_player_2].to_list()
smash_3_scores = adj_sg_df[smash_player_3].to_list()
smash_4_scores = adj_sg_df[smash_player_4].to_list()


opp_captain_scores = adj_sg_df[captain].to_list()
opp_2_scores = adj_sg_df[player_2].to_list()
opp_3_scores = adj_sg_df[player_3].to_list()
opp_4_scores = adj_sg_df[player_4].to_list()


num_simulations = 10000


def single_match(team_1, team_2, team_1_name, team_2_name):

    num_wins = 0
    
    for i in range(num_simulations):
        
        team_1_score = random.choice(team_1)
        team_2_score = random.choice(team_2)
        
        if team_1_score > team_2_score:
            num_wins += 1
    
    match_info = {'Opponent':team,
                  'Match':team_1_name+' v '+team_2_name,
                  'Smash_Wins':num_wins}
    wins_df = pd.DataFrame(match_info, index = [0])
    
    return wins_df


winners_dfs.append(single_match(smash_captain_scores,opp_captain_scores, smash_captain, captain))

winners_dfs.append(single_match(smash_2_scores,opp_2_scores, smash_player_2, player_2))
winners_dfs.append(single_match(smash_2_scores,opp_3_scores, smash_player_2, player_3))
winners_dfs.append(single_match(smash_2_scores,opp_4_scores, smash_player_2, player_4))

winners_dfs.append(single_match(smash_3_scores,opp_2_scores, smash_player_3, player_2))
winners_dfs.append(single_match(smash_3_scores,opp_3_scores, smash_player_3, player_3))
winners_dfs.append(single_match(smash_3_scores,opp_4_scores, smash_player_3, player_4))


winners_dfs.append(single_match(smash_4_scores,opp_2_scores, smash_player_4, player_2))
winners_dfs.append(single_match(smash_4_scores,opp_3_scores, smash_player_4, player_3))
winners_dfs.append(single_match(smash_4_scores,opp_4_scores, smash_player_4, player_4))

def team_match(team_1_a,team_1_b, team_2_a, team_2_b, team_1_a_name, team_1_b_name, team_2_a_name, team_2_b_name):

    num_wins = 0
    
    for i in range(num_simulations):
        
        team_1_score = random.choice(team_1_a)+random.choice(team_1_b)
        team_2_score = random.choice(team_2_a)+random.choice(team_2_b)
        
        if team_1_score > team_2_score:
            num_wins += 1
    match_info = {'Opponent':team,
                  'Match':team_1_a_name+ ' & '+team_1_b_name+' v '+team_2_a_name+ ' & '+team_2_b_name,
                  'Smash_Wins':num_wins,
                  }
    wins_df = pd.DataFrame(match_info, index = [0])
    return wins_df


winners_dfs.append(team_match(smash_2_scores,smash_3_scores,opp_2_scores,opp_3_scores, smash_player_2, smash_player_3, player_2, player_3))
winners_dfs.append(team_match(smash_2_scores,smash_3_scores,opp_2_scores,opp_4_scores, smash_player_2, smash_player_3, player_2, player_4))
winners_dfs.append(team_match(smash_2_scores,smash_3_scores,opp_3_scores,opp_4_scores, smash_player_2, smash_player_3, player_3, player_4))

winners_dfs.append(team_match(smash_3_scores,smash_4_scores,opp_2_scores,opp_3_scores, smash_player_3, smash_player_4, player_2, player_3))
winners_dfs.append(team_match(smash_3_scores,smash_4_scores,opp_2_scores,opp_4_scores, smash_player_3, smash_player_4, player_2, player_4))
winners_dfs.append(team_match(smash_3_scores,smash_4_scores,opp_3_scores,opp_4_scores, smash_player_3, smash_player_4, player_3, player_4))


winners_dfs.append(team_match(smash_2_scores,smash_4_scores,opp_2_scores,opp_3_scores, smash_player_2, smash_player_4, player_2, player_3))
winners_dfs.append(team_match(smash_2_scores,smash_4_scores,opp_2_scores,opp_4_scores, smash_player_2, smash_player_4, player_2, player_4))
winners_dfs.append(team_match(smash_2_scores,smash_4_scores,opp_3_scores,opp_4_scores, smash_player_2, smash_player_4, player_3, player_4))



match_info_df = pd.concat(winners_dfs).drop_duplicates()