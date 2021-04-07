import networkx as nx
import csv
from utils import *
import pandas as pd
import sys

def RawPlayerData(csv_f, json_filename):
    start = time.time()
    node_dict = retrieveNodes(getFilePath(json_filename, 'nodelists'))

    sys.stdout.write("\r \n######################################\n Reading and preprocessing CSV file \n This may take some time. \n--------------------------------------\n")

    # row_list = [['player','avg_daily_games', 'active_days','inactive_days','active_periods','inactive_periods','full_day_count','ratings', 'games']]
    row_list = [['player', 'ratings', 'opp_ratings', 'opp_rating_diff', 'results', 'full_day_count', 'sides', 'openings']]
    sys.stdout.write("\r Retriving data from {0}\n".format(csv_f))
    csv_path = getFilePath(csv_f, 'csv')
    
    # csv_date = getLichessDBDate(csv_f)
    split_name = csv_f.split("_")
    csv_date = split_name[4]
    game_type = split_name[5]
    nodelist_filename = 'nodelist_{0}_{1}.csv'.format(csv_date, game_type)

    # Path to save to at the end    
    nodelist_path = getFilePath(nodelist_filename, 'csv')

    # Abridged list of headers
    edges = pd.read_csv(csv_path)
    edges['w'] = edges['white_id']
    edges['b'] = edges['black_id']

    sys.stdout.write("\r {0} done.\n".format(csv_f))

    sys.stdout.write("\r Generating graph from edgelist {0}. \n".format(csv_f))
    G = nx.from_pandas_edgelist(edges, source='w', target='b', edge_attr=True, create_using=nx.MultiGraph())
    sys.stdout.write("\r Graph generated from {0}. \n\n".format(csv_f))

    # Get month and year info from csv file name
    day_count, date_dict = getDateIDDict(csv_f)
    player_count = 0
    removed = 0
    for p in node_dict:
        player = node_dict[p]
        player_count += 1
        sys.stdout.write("\rPlayer: {0}, Count: {1}, Removed: {2}".format(player, player_count, removed))
        sys.stdout.flush()

        # Format: 1800.500.0 1400.-300.1
        #   -->     opponent rating . rated higher, lower or even . rating difference . win, loss, draw
        #   Opponent rating = natural number
        #   Rating difference = integer
        #   Win, lose, draw = -1 lose, 0 even, 1 win
        #   Delimited by space
        # games = []
        opp_ratings = []
        opp_rating_diff = []
        win_loss_draw = []        
        
        # Full list of player's own rating 
        ratings = []

        # Full list of sides of a player
        sides = []

        # Full list of openings
        openings = []

        # List of games played on each day of a given month
        #   --> daily_game_count
        #       format: 1.0.5.0.1. (etc) means one day 1, 1 game was played. on day 2, 10 games, etc.
        daily_game_count = [0] * day_count

        # Unique list of opponents the player has played
        try:
            opponent_list = [g for g in G[str(player)]]
        except KeyError:
            removed += 1
            continue

        for opp in opponent_list:
            # opponent_list is a list of unique player IDs the player (player) has played against
            # each opponent (opp) in opponent_list may have more than one game played against the player
            game_list = G[str(player)][opp]
            # game_list = G[player][opp]
            for g in game_list:
                # game_data = [0, 0, 0]

                # each game played between a particular opponent opp and the player is g
                game = game_list[g]
                white = game['white_id']
                # format: yyyy.mm.dd
                date = game['date']
                date_index = date_dict[date]
                daily_game_count[date_index] += 1

                # If the player played as white
                
                if(white == 'stranger'):
                    # to avoid ValueError in the next line, set white to something that != player
                    # so it defaults to player playing as black
                    white = int(player) - 1

                if(int(white) == int(player)):
                    # if(flag_it = )
                    # Add player's Elo before the match
                    ratings.append(game['white_rating'])
                    # Add Elo rating difference 
                    opp_rating = game['black_rating']
                    rating_difference = game['black_rating'] - game['white_rating']
                    # game_data[0] = opp_rating
                    # game_data[1] = rating_difference
                    opp_ratings.append(opp_rating)
                    opp_rating_diff.append(rating_difference)
                    
                    sides.append('w')

                    openings.append(game['opening'])

                    # If the game was won
                    if(game['result'] == '1-0'):
                        # Add '1' indicating a victory
                        # game_data[2] = 1
                        win_loss_draw.append(1)
                    # If the game was a draw
                    elif(game['result'] == '1/2-1/2'):
                        # Add '0' indicating a draw
                        # game_data[2] = 0
                        win_loss_draw.append(0)
                    else:
                        # Add '-1' indicating a loss
                        # game_data[2] = -1
                        win_loss_draw.append(-1)

                    # games.append('.'.join(str(i) for i in game_data))

                # If player played as black 
                else:
                    ratings.append(game['black_rating'])
                    opp_rating = game['white_rating']
                    rating_difference = game['white_rating'] - game['black_rating']
                    # game_data[0] = opp_rating
                    # game_data[1] = rating_difference
                    opp_ratings.append(opp_rating)
                    opp_rating_diff.append(rating_difference)

                    sides.append('b')

                    openings.append(game['opening'])

                    if(game['result'] == '0-1'):
                        # game_data[2] = 1
                        win_loss_draw.append(1)
                    elif(game['result'] == '1/2-1/2'):
                        # game_data[2] = 0
                        win_loss_draw.append(0)
                    else:
                        # game_data[2] = -1
                        win_loss_draw.append(-1)

                    # games.append('.'.join(str(i) for i in game_data))


        rating_list = ' '.join([str(r) for r in ratings])
        opp_ratings = ' '.join([str(r) for r in opp_ratings])
        opp_rating_diff = ' '.join([str(d) for d in opp_rating_diff])
        win_loss_draw = ' '.join([str(r) for r in win_loss_draw])
        full_day_count =  ' '.join([str(i) for i in daily_game_count])
        sides_list = ' '.join([str(s) for s in sides])
        openings_list = ' '.join([str(o) for o in openings])

        # game_list = ' '.join([str(g) for g in games])

        # avg_daily_games = sum(daily_game_count)/len(daily_game_count)
        # active_days, inactive_days, active_periods, inactive_periods = ActiveInactiveDaysAndPeriods(daily_game_count)
        # perspective_3 = [avg_daily_games, active_days, inactive_days, active_periods, inactive_periods, full_day_count]

        # player_row = [player] + [full_day_count] + [rating_list] + [game_list]
        player_row = [player, rating_list, opp_ratings, opp_rating_diff, win_loss_draw, full_day_count, sides_list, openings_list]
        row_list.append(player_row)

    sys.stdout.write("\r\n Total: {0}, Removed: {1}\n".format(player_count, removed))


    sys.stdout.write("\r Writing to {0}\n\n".format(nodelist_filename))
    with open(nodelist_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(row_list)
            
    end = time.time()
    timeFormat(start,end, RawPlayerData.__name__)


# csv_list = ['lichess_db_standard_rated_2014-01_cut.csv', 'lichess_db_standard_rated_2014-02_cut.csv', 'lichess_db_standard_rated_2014-03_cut.csv', 'lichess_db_standard_rated_2014-04_cut.csv', 'lichess_db_standard_rated_2014-05_cut.csv', 'lichess_db_standard_rated_2014-06_cut.csv', 'lichess_db_standard_rated_2014-07_cut.csv', 'lichess_db_standard_rated_2014-08_cut.csv', 'lichess_db_standard_rated_2014-09_cut.csv', 'lichess_db_standard_rated_2014-10_cut.csv', 'lichess_db_standard_rated_2014-11_cut.csv', 'lichess_db_standard_rated_2014-12_cut.csv']
# csv_ls = ['lichess_db_standard_rated_2014-01_cut.csv', 'lichess_db_standard_rated_2014-02_cut.csv']
#create_nodelist(csv_list, '2014_nodes.txt')

# CreateNodelistSeparate(csv_list, '2014_nodes.txt')
# csv_list = ['lichess_db_standard_rated_2015-01_cut.csv', 'lichess_db_standard_rated_2015-02_cut.csv', 'lichess_db_standard_rated_2015-03_cut.csv', 'lichess_db_standard_rated_2015-04_cut.csv', 'lichess_db_standard_rated_2015-05_cut.csv', 'lichess_db_standard_rated_2015-06_cut.csv', 'lichess_db_standard_rated_2015-07_cut.csv', 'lichess_db_standard_rated_2015-08_cut.csv', 'lichess_db_standard_rated_2015-09_cut.csv', 'lichess_db_standard_rated_2015-10_cut.csv', 'lichess_db_standard_rated_2015-11_cut.csv', 'lichess_db_standard_rated_2015-12_cut.csv']
# month_list = ['0{0}'.format(x) for x in range(7,10)] + [str(x) for x in range(10,13)]
# month_list = ['0{0}'.format(x) for x in range(7,12)]
month_list = ['0{0}'.format(x) for x in range(1,7)]

# bullet_list = ['lichess_db_standard_rated_2015-{0}_bullet_cut.csv'.format(x) for x in month_list]
blitz_list_14 = ['lichess_db_standard_rated_2014-{0}_blitz_cut.csv'.format(x) for x in month_list]
blitz_list_15 = ['lichess_db_standard_rated_2015-{0}_blitz_cut.csv'.format(x) for x in month_list]
# classical_list = ['lichess_db_standard_rated_2015-{0}_classical_cut.csv'.format(x) for x in month_list]

for csv_f in bullet_list:
    RawPlayerData(csv_f, 'id_nodelist.txt')
# for csv_f in blitz_list_14:
#     RawPlayerData(csv_f, 'id_nodelist.txt')

# for csv_f in blitz_list_15:
#     RawPlayerData(csv_f, 'id_nodelist.txt')
# for csv_f in classical_list:
#     RawPlayerData(csv_f, 'id_nodelist.txt')
# RawPlayerData('lichess_db_standard_rated_2014-01_blitz_cut.csv', 'id_nodelist.txt')
