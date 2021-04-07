import chess.pgn
import csv
import os
import json
import sys
import time
from utils import * 

def SelectedOnlyPGNtoCSV(filename, json_filename):
    start = time.time()
    sys.stdout.write("\r \n######################################\nConverting {0} from PGN to CSV\n--------------------------------------\n".format(filename))

    # Get file path
    # csv_name = filename[:-4] + "_cut.csv"
    bullet_name = filename[:-4] + "_bullet_cut.csv"
    blitz_name = filename[:-4] + "_blitz_cut.csv"
    rapid_name = filename[:-4] + "_rapid_cut.csv"
    classical_name = filename[:-4] + "_classical_cut.csv"

    pgn_path = getFilePath(filename, "pgn")
    # csv_path = getFilePath(csv_name, "csv")
    bullet_path = getFilePath(bullet_name, "csv")
    blitz_path = getFilePath(blitz_name, "csv")
    rapid_path = getFilePath(rapid_name, "csv")
    classical_path = getFilePath(classical_name, "csv")

    # Open PGN file 
    pgn = open(pgn_path, encoding='utf-8-sig')

    # Initialise headers
    # row_list = [['id','date','white_id', 'black_id','result','white_rating','black_rating', 'event', 'opening']]
    bullet_row_list = [['id','date','white_id', 'black_id','result','white_rating','black_rating','white_rating_change','black_rating_change', 'opening']]
    blitz_row_list = [['id','date','white_id', 'black_id','result','white_rating','black_rating','white_rating_change','black_rating_change', 'opening']]
    rapid_row_list = [['id','date','white_id', 'black_id','result','white_rating','black_rating','white_rating_change','black_rating_change', 'opening']]
    classical_row_list = [['id','date','white_id', 'black_id','result','white_rating','black_rating','white_rating_change','black_rating_change', 'opening']]

    # total_removed = 0

    node_dict_filepath = getFilePath(json_filename, 'nodelists')
    node_dict = retrieveNodes(node_dict_filepath)

    removed = 0
    game_id = 1
    invalid = 0

    # game_count = getGameCount(filename)
    bullet_count = 0
    blitz_count = 0
    rapid_count = 0
    classical_count = 0
    game = 1
    while(game):
    # for i in range(0, game_count):
        try:
            game = chess.pgn.read_game(pgn)
        except ValueError:
            invalid += 1
            game = 1
            continue
        except:
            invalid += 1
            game = 1
            continue

        game_list = []
        # sys.stdout.write("\r Processed: {0}/{1} | Bullet: {4} | Blitz: {5} | Rapid: {6} | Classical: {7} | Invalid: {2} |  Removed: {3}".format(i+1,game_count, invalid, removed, bullet_count, blitz_count, rapid_count, classical_count))
        sys.stdout.write("\r Processed: {0} | Bullet: {3} | Blitz: {4} | Rapid: {5} | Classical: {6} | Invalid: {1} |  Removed: {2}".format(game_id, invalid, removed, bullet_count, blitz_count, rapid_count, classical_count))

        sys.stdout.flush()
        
        try:
            game_date                 = game.headers['UTCDate']
            game_white                = game.headers['White']
            game_black                = game.headers['Black']
            game_result               = game.headers['Result']
            game_white_rating         = game.headers['WhiteElo']
            game_black_rating         = game.headers['BlackElo']
            game_white_rating_change  = game.headers['WhiteRatingDiff']
            game_black_rating_change  = game.headers['BlackRatingDiff']
            game_event                = game.headers['Event']
            game_opening              = game.headers['ECO']
        except KeyError:
            invalid += 1
            continue
        except ValueError:
            invalid += 1
            continue
        except IndexError:
            invalid += 1
            continue
        except:
            invalid += 1
            continue

        # Don't add any games that are not played by at least one player in the node dict
        if(game_white not in node_dict and game_black not in node_dict):
            removed += 1
            continue
        else:
            if(game_white in node_dict):
                game_white = node_dict[game_white]
            else:
                game_white = "stranger"
            if(game_black in node_dict):
                game_black = node_dict[game_black]
            else:
                game_black = "stranger"
        game_event = game_event.split(' ')[1]

        if(game_event == 'Bullet'):
            bullet_count += 1
            game_list.append(bullet_count)
            game_list.append(game_date)   
            game_list.append(game_white)
            game_list.append(game_black)
            game_list.append(game_result)
            game_list.append(game_white_rating)
            game_list.append(game_black_rating)
            game_list.append(game_white_rating_change)
            game_list.append(game_black_rating_change)
            game_list.append(game_opening)
            bullet_row_list.append(game_list)

        elif(game_event == 'Blitz'):
            blitz_count += 1
            game_list.append(blitz_count)
            game_list.append(game_date)   
            game_list.append(game_white)
            game_list.append(game_black)
            game_list.append(game_result)
            game_list.append(game_white_rating)
            game_list.append(game_black_rating)
            game_list.append(game_white_rating_change)
            game_list.append(game_black_rating_change)
            game_list.append(game_opening)
            blitz_row_list.append(game_list)

        elif(game_event == 'Rapid'):
            rapid_count += 1
            game_list.append(rapid_count)
            game_list.append(game_date)   
            game_list.append(game_white)
            game_list.append(game_black)
            game_list.append(game_result)
            game_list.append(game_white_rating)
            game_list.append(game_black_rating)
            game_list.append(game_white_rating_change)
            game_list.append(game_black_rating_change)
            game_list.append(game_opening)
            rapid_row_list.append(game_list)

        elif(game_event == 'Classical'):
            classical_count += 1
            game_list.append(classical_count)
            game_list.append(game_date)   
            game_list.append(game_white)
            game_list.append(game_black)
            game_list.append(game_result)
            game_list.append(game_white_rating)
            game_list.append(game_black_rating)
            game_list.append(game_white_rating_change)
            game_list.append(game_black_rating_change)
            game_list.append(game_opening)
            classical_row_list.append(game_list)
        # if(game_event[0] == 'B'):
        #     game_event = game_event[:2]
        # else:
        #     game_event = game_event[0]

        # game_list.append(game_id)
        # game_list.append(game_date)   
        # game_list.append(game_white)
        # game_list.append(game_black)
        # game_list.append(game_result)
        # game_list.append(game_white_rating)
        # game_list.append(game_black_rating)
        # # game_list.append(game_event)
        # game_list.append(game_opening)
        game_id += 1
        # row_list.append(game_list)

    with open(bullet_path, "w", newline="") as f:
        writer = csv.writer(f)
        # writer.writerheader()
        writer.writerows(bullet_row_list)

    with open(blitz_path, "w", newline="") as f:
        writer = csv.writer(f)
        # writer.writerheader()
        writer.writerows(blitz_row_list)

    with open(rapid_path, "w", newline="") as f:
        writer = csv.writer(f)
        # writer.writerheader()
        writer.writerows(rapid_row_list)

    with open(classical_path, "w", newline="") as f:
        writer = csv.writer(f)
        # writer.writerheader()
        writer.writerows(classical_row_list)

    sys.stdout.write("\r \n-------------------------------------- \nDone.\n######################################")

    end = time.time()
    timeFormat(start, end, SelectedOnlyPGNtoCSV.__name__)

json_nodelist = 'player_nodelist_map.txt'
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-01.pgn', json_nodelist)
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-02.pgn', json_nodelist)
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-03.pgn', json_nodelist)
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-04.pgn', json_nodelist)
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-05.pgn', json_nodelist)
SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-06.pgn', json_nodelist)
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-07.pgn', json_nodelist)
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-08.pgn', json_nodelist)
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-09.pgn', json_nodelist)
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-10.pgn', json_nodelist)
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-11.pgn', json_nodelist)
# SelectedOnlyPGNtoCSV('lichess_db_standard_rated_2015-12.pgn', json_nodelist)