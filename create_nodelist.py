import networkx as nx
import csv
from utils import *
import pandas as pd
import sys

def create_nodelist_combined(csv_filename_list, json_filename):
    start = time.time()
    node_dict = retrieve_nodes(get_path_file(json_filename, 'nodelists'))
    node_dict_zero = node_dict
    for key in node_dict_zero:
        node_dict_zero[key] = 0

    # Path to save to at the end    
    nodelist_path = get_path_file('nodelist.csv', 'csv')

    row_list = [['id', 'player_id', 'win','loss','draw','average_elo','max_elo','min_elo','average_elo_diff','below_neg_300','neg_200_to_300','neg_100_to_200','neg_50_to_100','zero_to_neg_50','zero','zero_to_50','pos_50_to_100','pos_100_to_200','pos_200_to_300','above_pos_300','max_elo_diff','min_elo_diff','game_count']]

    id = 1
    sys.stdout.write("\r \n######################################\n Reading and preprocessing {0} CSV files \n This may take some time. \n--------------------------------------\n".format(len(csv_filename_list)))
    merged_csv = []
    for csv_f in csv_filename_list:
        sys.stdout.write("\r Retriving data from {0}\n".format(csv_f))
        csv_path = get_path_file(csv_f, 'csv')
        edges = pd.read_csv(csv_path)[['id','date','time','event', 'white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff','eco','time_control', 'termination','moves']]
        edges = edges.drop(columns=['date','time','time_control','termination','moves'])
        edges['w'] = edges['white_id']
        edges['b'] = edges['black_id']
        merged_csv.append(edges)
        sys.stdout.write("\r {0} done.\n".format(csv_f))

    merged_csv = pd.concat(merged_csv)
    sys.stdout.write("\r Generating graph from edgelist. \n".format(csv_f))
    G = nx.from_pandas_edgelist(merged_csv, source='w', target='b', edge_attr=True)
    sys.stdout.write("\r Graph generated. \n\n".format(csv_f))
    for player in node_dict:
        sys.stdout.write("\r{1}/{2}:\t Player: {0}".format(player, id, len(node_dict)))
        sys.stdout.flush()

        game_count = 0
        opponent_list = [g for g in G[player]]
        elo_list = []
        elo_diff_list = []
        win_count = 0
        loss_count = 0
        draw_count = 0

        below_neg_300 = 0
        neg_200_to_300 = 0
        neg_100_to_200 = 0
        neg_50_to_100 = 0
        zero_to_neg_50 = 0
        zero = 0
        zero_to_50 = 0
        pos_50_to_100 = 0
        pos_100_to_200 = 0
        pos_200_to_300 = 0
        above_pos_300 = 0

        for g in opponent_list:
            # g = player ID
            game = G[player][g]
            white = game['white_id']
            game_count += 1
            if(white == player):
                elo_list.append(game['white_elo'])
                elo_diff_list.append(game['black_elo'] - game['white_elo'])
                if(game['result'] == '1-0'):
                    win_count += 1
                elif(game['result'] == '1/2-1/2'):
                    draw_count += 1
                else:
                    loss_count += 1
            else:
                #if player played as black 
                elo_list.append(game['black_elo'])
                elo_diff_list.append(game['white_elo'] - game['black_elo'])
                if(game['result'] == '0-1'):
                    win_count += 1
                elif(game['result'] == '1/2-1/2'):
                    draw_count += 1
                else:
                    loss_count += 1

        for elo in elo_diff_list:
            if(elo > 300):
                above_pos_300 += 1
            elif(elo > 200):
                pos_200_to_300 += 1
            elif(elo > 100):
                pos_100_to_200 += 1
            elif(elo > 50):
                pos_50_to_100 += 1
            elif(elo > 0):
                zero_to_50 += 1
            elif(elo == 0):
                zero += 1
            elif(elo > -50):
                zero_to_neg_50 += 1
            elif(elo > -100):
                neg_50_to_100 += 1
            elif(elo > -200):
                neg_100_to_200 += 1
            elif(elo > -300):
                neg_200_to_300 += 1
            else:
                below_neg_300 += 1

        max_elo = max(elo_list)
        min_elo = min(elo_list)
        avg_elo = sum(elo_list)/len(elo_list)
        max_elo_diff = max(elo_diff_list)
        min_elo_diff = min(elo_diff_list)
        avg_elo_diff = sum(elo_diff_list)/len(elo_diff_list)
        player_row = [id, player, win_count, loss_count, draw_count, avg_elo, max_elo, min_elo, avg_elo_diff,below_neg_300,neg_200_to_300,neg_100_to_200,neg_50_to_100,zero_to_neg_50,zero,zero_to_50,pos_50_to_100,pos_100_to_200,pos_200_to_300,above_pos_300, max_elo_diff, min_elo_diff, game_count]
        row_list.append(player_row)
        id += 1

    with open(nodelist_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(row_list)

    end = time.time()
    time_format(start,end, create_nodelist.__name__)


def create_nodelist_separate(csv_filename_list, json_filename):
    start = time.time()
    node_dict = retrieve_nodes(get_path_file(json_filename, 'nodelists'))
    node_dict_zero = node_dict
    for key in node_dict_zero:
        node_dict_zero[key] = 0

    # Path to save to at the end    
    nodelist_path = get_path_file('nodelist.csv', 'csv')

    row_list = [['id', 'player_id', 'win','loss','draw','average_elo','max_elo','min_elo','average_elo_diff','below_neg_300','neg_200_to_300','neg_100_to_200','neg_50_to_100','zero_to_neg_50','zero','zero_to_50','pos_50_to_100','pos_100_to_200','pos_200_to_300','above_pos_300','max_elo_diff','min_elo_diff','game_count']]

    id = 1
    sys.stdout.write("\r \n######################################\n Reading and preprocessing {0} CSV files \n This may take some time. \n--------------------------------------\n".format(len(csv_filename_list)))
    merged_csv = []
    for csv_f in csv_filename_list:
        sys.stdout.write("\r Retriving data from {0}\n".format(csv_f))
        csv_path = get_path_file(csv_f, 'csv')
        edges = pd.read_csv(csv_path)[['id','date','time','event', 'white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff','eco','time_control', 'termination','moves']]
        edges = edges.drop(columns=['date','time','time_control','termination','moves'])
        edges['w'] = edges['white_id']
        edges['b'] = edges['black_id']
        merged_csv.append(edges)
        sys.stdout.write("\r {0} done.\n".format(csv_f))

    merged_csv = pd.concat(merged_csv)
    sys.stdout.write("\r Generating graph from edgelist. \n".format(csv_f))
    G = nx.from_pandas_edgelist(merged_csv, source='w', target='b', edge_attr=True)
    sys.stdout.write("\r Graph generated. \n\n".format(csv_f))
    for player in node_dict:
        sys.stdout.write("\r{1}/{2}:\t Player: {0}".format(player, id, len(node_dict)))
        sys.stdout.flush()

        game_count = 0
        opponent_list = [g for g in G[player]]
        elo_list = []
        elo_diff_list = []
        win_count = 0
        loss_count = 0
        draw_count = 0

        below_neg_300 = 0
        neg_200_to_300 = 0
        neg_100_to_200 = 0
        neg_50_to_100 = 0
        zero_to_neg_50 = 0
        zero = 0
        zero_to_50 = 0
        pos_50_to_100 = 0
        pos_100_to_200 = 0
        pos_200_to_300 = 0
        above_pos_300 = 0

        for g in opponent_list:
            # g = player ID
            game = G[player][g]
            white = game['white_id']
            game_count += 1
            if(white == player):
                elo_list.append(game['white_elo'])
                elo_diff_list.append(game['black_elo'] - game['white_elo'])
                if(game['result'] == '1-0'):
                    win_count += 1
                elif(game['result'] == '1/2-1/2'):
                    draw_count += 1
                else:
                    loss_count += 1
            else:
                #if player played as black 
                elo_list.append(game['black_elo'])
                elo_diff_list.append(game['white_elo'] - game['black_elo'])
                if(game['result'] == '0-1'):
                    win_count += 1
                elif(game['result'] == '1/2-1/2'):
                    draw_count += 1
                else:
                    loss_count += 1

        for elo in elo_diff_list:
            if(elo > 300):
                above_pos_300 += 1
            elif(elo > 200):
                pos_200_to_300 += 1
            elif(elo > 100):
                pos_100_to_200 += 1
            elif(elo > 50):
                pos_50_to_100 += 1
            elif(elo > 0):
                zero_to_50 += 1
            elif(elo == 0):
                zero += 1
            elif(elo > -50):
                zero_to_neg_50 += 1
            elif(elo > -100):
                neg_50_to_100 += 1
            elif(elo > -200):
                neg_100_to_200 += 1
            elif(elo > -300):
                neg_200_to_300 += 1
            else:
                below_neg_300 += 1

        max_elo = max(elo_list)
        min_elo = min(elo_list)
        avg_elo = sum(elo_list)/len(elo_list)
        max_elo_diff = max(elo_diff_list)
        min_elo_diff = min(elo_diff_list)
        avg_elo_diff = sum(elo_diff_list)/len(elo_diff_list)
        player_row = [id, player, win_count, loss_count, draw_count, avg_elo, max_elo, min_elo, avg_elo_diff,below_neg_300,neg_200_to_300,neg_100_to_200,neg_50_to_100,zero_to_neg_50,zero,zero_to_50,pos_50_to_100,pos_100_to_200,pos_200_to_300,above_pos_300, max_elo_diff, min_elo_diff, game_count]
        row_list.append(player_row)
        id += 1

    with open(nodelist_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(row_list)

    end = time.time()
    time_format(start,end, create_nodelist.__name__)

csv_list = ['lichess_db_standard_rated_2014-01_cut.csv', 'lichess_db_standard_rated_2014-02_cut.csv', 'lichess_db_standard_rated_2014-03_cut.csv', 'lichess_db_standard_rated_2014-04_cut.csv', 'lichess_db_standard_rated_2014-05_cut.csv', 'lichess_db_standard_rated_2014-06_cut.csv', 'lichess_db_standard_rated_2014-07_cut.csv', 'lichess_db_standard_rated_2014-08_cut.csv', 'lichess_db_standard_rated_2014-09_cut.csv', 'lichess_db_standard_rated_2014-10_cut.csv', 'lichess_db_standard_rated_2014-11_cut.csv', 'lichess_db_standard_rated_2014-12_cut.csv']
#create_nodelist(csv_list, '2014_nodes.txt')