import chess.pgn
import csv
import os
import json
import sys
import time
from utils import * 

# Convert PGN files to CSV
def db_to_csv(filename):
    start = time.time()
    sys.stdout.write("\r \n######################################\nConverting {0} from PGN to CSV\n--------------------------------------\n".format(filename))

    # Get file path
    csv_name = filename[:-4] + ".csv"

    pgn_path = get_path_file(filename, "pgn")
    csv_path = get_path_file(csv_name, "csv")

    # Open PGN file 
    pgn = open(pgn_path, encoding='utf-8-sig')

    # Initialise headers
    row_list = [['id','date','time','event', 'white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff','eco','time_control', 'termination','moves']]
    
    game_id = 1
    invalid = 0
    game_count = get_game_count(filename)
    for i in range(0,game_count): #TODO: iterate over all games
        try:
            game = chess.pgn.read_game(pgn)
        except ValueError:
            invalid += 1
            continue
        except:
            invalid += 1
            continue

        game_list = []
        sys.stdout.write("\r Current ID: {0}/{1} | Invalid: {2}".format(i+1,game_count, invalid))
        sys.stdout.flush()
        
        try:
            game_date       = game.headers['UTCDate']
            game_time       = game.headers['UTCTime']
            game_event      = game.headers['Event']
            game_white      = game.headers['White']
            game_black      = game.headers['Black']
            game_result     = game.headers['Result']
            game_white_elo  = game.headers['WhiteElo']
            game_white_diff = game.headers['WhiteRatingDiff']
            game_black_elo  = game.headers['BlackElo']
            game_black_diff = game.headers['BlackRatingDiff']
            game_eco        = game.headers['ECO']
            game_t_control  = game.headers['TimeControl']
            game_term       = game.headers['Termination']
            board           = str(game.variations[0])
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

        game_list.append(game_id)
        game_list.append(game_date)   
        game_list.append(game_time)
        game_list.append(game_event)
        game_list.append(game_white)
        game_list.append(game_black)
        game_list.append(game_result)
        game_list.append(game_white_elo)
        game_list.append(game_white_diff)
        game_list.append(game_black_elo)
        game_list.append(game_black_diff)
        game_list.append(game_eco)
        game_list.append(game_t_control)
        game_list.append(game_term)
        game_list.append(board)
        game_id += 1
        row_list.append(game_list)

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(row_list)

    sys.stdout.write("\r \n-------------------------------------- \n{0} Converted to {1} \n######################################".format(filename, csv_name))

    end = time.time()
    time_format(start, end, db_to_csv.__name__)

# Obtain games that only contain player ids from a predefined dictionary
def selected_nodes_only(csv_filename_list, json_filename):
    # List of all relevant elements
    start = time.time()
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    total_removed = 0
    total_game_count = 0
    for csv_filename in csv_filename_list:
        row_list = []
        csv_list = []
        removed = 0
        csv_path = get_path_file(csv_filename, 'csv')
        node_dict = retrieve_nodes(get_path_file(json_filename, 'nodelists'))
        game_count = get_game_count(csv_filename)
        csv_list.append(get_lichess_db_date(csv_filename))
        
        with open(csv_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            i = 0
            for row in csv_reader:
                white_id = row["white_id"]
                black_id = row["black_id"]
                if(white_id not in node_dict and black_id not in node_dict):
                    removed += 1
                else:
                    row_list.append(row)
                sys.stdout.write("\r Added: {0}, Removed: {1}, Remaining: {2}>".format(len(row_list),removed, game_count - i))
                sys.stdout.flush()
                i += 1
        sys.stdout.write("\r Added: {0}, Removed: {1}/{2} from {3}>".format(len(row_list),removed, game_count - i, get_lichess_db_date(csv_filename)))

        new_csv_name = csv_filename[:-4] + "_cut.csv"
        new_csv_path = get_path_file(new_csv_name, 'csv')

        with open(new_csv_path, "w", newline="") as f:
            # writer = csv.DictWriter(f, ['id','date','event', 'white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff','eco'])
            writer = csv.DictWriter(f, ['id','date','time','event', 'white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff','eco','time_control', 'termination','moves'])

            writer.writeheader()
            writer.writerows(row_list)

        total_removed += removed
        total_game_count += game_count
        sys.stdout.write("\n\n Dataset: {0} processed\n\n".format(csv_filename))

    sys.stdout.write("\n\n Processed the following datasets: \n")
    for i in range(1,len(csv_filename_list)+1):
        sys.stdout.write("{0}. {1}\n".format(i, csv_filename_list[i-1]))

    sys.stdout.write("\n\n\r {0} rows deleted from an original count of {1}. {2} rows remaining.".format(total_removed,total_game_count, total_game_count - total_removed))
    end = time.time()
    time_format(start, end, selected_nodes_only.__name__)

# Obtain a dictionary of unique nodes in a CSV file
def get_node_dict_csv(csv_filename):
    '''Used to obtain a dictionary of all the nodes in a PGN file and '''
    start = time.time()
    node_dict = {}

    # Get path names
    csv_folder = 'csv'
    txt_folder = 'nodelists'
    txt_filename = csv_filename[:-4] + '_cut.txt'
    csv_path = get_path_file(csv_filename, csv_folder)
    txt_path = get_path_file(txt_filename, txt_folder)

    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # csv_path = dir_path + '\\' + csv_filename
    # txt_path = csv_path[:-4] + '_nodes.txt'
    # game_count = get_game_count(csv_filename)

    i = 0
    with open(csv_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        for row in csv_reader:
            white_id = row["white_id"]
            black_id = row["black_id"]
            if(white_id not in node_dict):
                node_dict[white_id] = 1
            else:
                node_dict[white_id] += 1
            if(black_id not in node_dict):
                node_dict[black_id] = 1
            else:
                node_dict[black_id] += 1
            sys.stdout.write("\r Processed: {0}, Number of Nodes: {1}>".format(i+1,len(node_dict)))
            sys.stdout.flush()
            i += 1

    with open(txt_path,'w') as file:
        file.write(json.dumps(node_dict))
    end = time.time()
    time_format(start,end, get_node_dict_csv.__name__)

# Obtain the number of games each player has played and removes players with no games played for the month
def get_node_count_csv(csv_filename, json_filename):
    '''Iterates through the nodes in csv_filename, checks each game for 
    white_id and black_id to see if they are in node_dict (json_filename)
    and adds one to their respective dictionary entry if they are present.
    Ignores otherwise. Finally, removes any elements in the dictionary
    which have a count of zero

    Input: name of CSV and JSON files with their extensions and the number of games
    in the CSV file (processed after download from Lichess.org)'''
    start = time.time()

    # Get path names
    csv_folder = 'csv'
    json_folder = 'nodelists'
    # txt_filename = csv_filename[:-4] + '.txt'
    csv_path = get_path_file(csv_filename, csv_folder)
    # txt_path = get_path_file(txt_filename, json_folder)
    json_path = get_path_file(json_filename, json_folder)
    set_zero(json_path)
    node_dict = retrieve_nodes(json_path)
    game_count = get_game_count(csv_filename)

    with open(csv_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            white_id = row["white_id"]
            black_id = row["black_id"]
            if(white_id in node_dict):
                node_dict[white_id] += 1
            if(black_id in node_dict):
                node_dict[black_id] += 1
            sys.stdout.write("\r Processed: {0}/{1}>".format(i+1,game_count))
            sys.stdout.flush()
            i += 1
    
    i = 0
    og_len = len(node_dict)
    for key in list(node_dict):
        if(node_dict[key] == 0):
            node_dict.pop(key, None)
        else:
            i += 1

    sys.stdout.write("\n\n\r {0} nodes deleted from an original count of {1}".format(og_len - len(node_dict), og_len))
    with open(json_path,'w') as file:
        file.write(json.dumps(node_dict))
    end = time.time()
    time_format(start,end, get_node_count_csv.__name__)

# db_to_csv('test_db.pgn')
# db_to_csv('test_db.pgn')
# get_node_dict_csv('test_db.csv')

# db_to_csv('lichess_db_standard_rated_2014-01.pgn')
# db_to_csv('lichess_db_standard_rated_2014-02.pgn')
# db_to_csv('lichess_db_standard_rated_2014-03.pgn')
# db_to_csv('lichess_db_standard_rated_2014-04.pgn')
# db_to_csv('lichess_db_standard_rated_2014-05.pgn')
# db_to_csv('lichess_db_standard_rated_2014-06.pgn')
# db_to_csv('lichess_db_standard_rated_2014-07.pgn')
# db_to_csv('lichess_db_standard_rated_2014-08.pgn')
# db_to_csv('lichess_db_standard_rated_2014-09.pgn')
# db_to_csv('lichess_db_standard_rated_2014-10.pgn')
# db_to_csv('lichess_db_standard_rated_2014-11.pgn')
# db_to_csv('lichess_db_standard_rated_2014-12.pgn')

# get_node_count_csv('lichess_db_standard_rated_2014-01.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-02.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-03.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-04.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-05.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-06.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-07.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-08.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-09.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-10.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-11.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# get_node_count_csv('lichess_db_standard_rated_2014-12.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')

# get_node_count_csv('test_db.csv', 'lichess_db_standard_rated_2014-12_nodes.txt')

# set_zero_new(get_path_file('lichess_db_standard_rated_2014-12_nodes.txt', 'nodelists'))

# selected_nodes_only(['lichess_db_standard_rated_2014-04.csv','lichess_db_standard_rated_2014-05.csv','lichess_db_standard_rated_2014-06.csv'], 'lichess_db_standard_rated_2014-12_nodes.txt')
# selected_nodes_only(['lichess_db_standard_rated_2014-07.csv','lichess_db_standard_rated_2014-08.csv','lichess_db_standard_rated_2014-09.csv'], 'lichess_db_standard_rated_2014-12_nodes.txt')
# selected_nodes_only(['lichess_db_standard_rated_2014-10.csv','lichess_db_standard_rated_2014-11.csv','lichess_db_standard_rated_2014-12.csv'], 'lichess_db_standard_rated_2014-12_nodes.txt')

# year_list = ['lichess_db_standard_rated_2014-01.csv', 'lichess_db_standard_rated_2014-02.csv', 'lichess_db_standard_rated_2014-03.csv', 'lichess_db_standard_rated_2014-04.csv', 'lichess_db_standard_rated_2014-05.csv', 'lichess_db_standard_rated_2014-06.csv', 'lichess_db_standard_rated_2014-07.csv', 'lichess_db_standard_rated_2014-08.csv', 'lichess_db_standard_rated_2014-09.csv', 'lichess_db_standard_rated_2014-10.csv', 'lichess_db_standard_rated_2014-11.csv', 'lichess_db_standard_rated_2014-12.csv']
# year_list = ['lichess_db_standard_rated_2014-04.csv', 'lichess_db_standard_rated_2014-05.csv', 'lichess_db_standard_rated_2014-06.csv']
# year_list = ['lichess_db_standard_rated_2014-07.csv', 'lichess_db_standard_rated_2014-08.csv', 'lichess_db_standard_rated_2014-09.csv']
# year_list = ['lichess_db_standard_rated_2014-10.csv', 'lichess_db_standard_rated_2014-11.csv', 'lichess_db_standard_rated_2014-12.csv']
