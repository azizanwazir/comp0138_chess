import chess.pgn
import csv
import os
import json
import sys
import time
from utils import * 

# Convert PGN files to CSV
def ConvertPGNtoCSV(filename):
    start = time.time()
    sys.stdout.write("\r \n######################################\nConverting {0} from PGN to CSV\n--------------------------------------\n".format(filename))

    # Get file path
    csv_name = filename[:-4] + ".csv"

    pgn_path = getFilePath(filename, "pgn")
    csv_path = getFilePath(csv_name, "csv")

    # Open PGN file 
    pgn = open(pgn_path, encoding='utf-8-sig')

    # Initialise headers
    # Abridged list of headers, only those used in processing
    row_list = [['id','date','white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff']]
    
    # Includes unused headers 
    # row_list = [['id','date','time','event', 'white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff','eco','time_control', 'termination','moves']]
    
    game_id = 1
    invalid = 0
    game_count = getGameCount(filename)
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
            # game_time       = game.headers['UTCTime']
            # game_event      = game.headers['Event']
            game_white      = game.headers['White']
            game_black      = game.headers['Black']
            game_result     = game.headers['Result']
            game_white_elo  = game.headers['WhiteElo']
            game_white_diff = game.headers['WhiteRatingDiff']
            game_black_elo  = game.headers['BlackElo']
            game_black_diff = game.headers['BlackRatingDiff']
            # game_eco        = game.headers['ECO']
            # game_t_control  = game.headers['TimeControl']
            # game_term       = game.headers['Termination']
            # board           = str(game.variations[0])
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
        # game_list.append(game_time)
        # game_list.append(game_event)
        game_list.append(game_white)
        game_list.append(game_black)
        game_list.append(game_result)
        game_list.append(game_white_elo)
        game_list.append(game_white_diff)
        game_list.append(game_black_elo)
        game_list.append(game_black_diff)
        # game_list.append(game_eco)
        # game_list.append(game_t_control)
        # game_list.append(game_term)
        # game_list.append(board)
        game_id += 1
        row_list.append(game_list)

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(row_list)

    sys.stdout.write("\r \n-------------------------------------- \n{0} Converted to {1} \n######################################".format(filename, csv_name))

    end = time.time()
    timeFormat(start, end, ConvertPGNtoCSV.__name__)

# Obtain games that only contain player ids from a predefined dictionary
def SelectedNodesOnly(csv_filename_list, json_filename):
    # List of all relevant elements
    start = time.time()
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    total_removed = 0
    total_game_count = 0
    for csv_filename in csv_filename_list:
        row_list = []
        csv_list = []
        removed = 0
        csv_path = getFilePath(csv_filename, 'csv')
        node_dict = retrieveNodes(getFilePath(json_filename, 'nodelists'))
        game_count = getGameCount(csv_filename)
        csv_list.append(getLichessDBDate(csv_filename))
        
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
        sys.stdout.write("\r Added: {0}, Removed: {1}/{2} from {3}>".format(len(row_list),removed, game_count - i, getLichessDBDate(csv_filename)))

        new_csv_name = csv_filename[:-4] + "_cut.csv"
        new_csv_path = getFilePath(new_csv_name, 'csv')

        with open(new_csv_path, "w", newline="") as f:
            # Abridged list of headers
            writer = csv.DictWriter(f, ['id','date', 'white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff'])
            
            # Full list of headers
            # writer = csv.DictWriter(f, ['id','date','time','event', 'white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff','eco','time_control', 'termination','moves'])

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
    timeFormat(start, end, SelectedNodesOnly.__name__)

# Obtain a dictionary of unique nodes in a CSV file
def getNodeDict(csv_filename):
    '''Used to obtain a dictionary of all the nodes in a PGN file and '''
    start = time.time()
    node_dict = {}

    # Get path names
    csv_folder = 'csv'
    txt_folder = 'nodelists'
    txt_filename = csv_filename[:-4] + '_cut.txt'
    csv_path = getFilePath(csv_filename, csv_folder)
    txt_path = getFilePath(txt_filename, txt_folder)

    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # csv_path = dir_path + '\\' + csv_filename
    # txt_path = csv_path[:-4] + '_nodes.txt'
    # game_count = getGameCount(csv_filename)

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
    timeFormat(start,end, getNodeDict.__name__)

# Obtain the number of games each player has played and removes players with no games played for the month
def getNodeCount(csv_filename, json_filename):
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
    csv_path = getFilePath(csv_filename, csv_folder)
    # txt_path = getFilePath(txt_filename, json_folder)
    json_path = getFilePath(json_filename, json_folder)
    setZero(json_path)
    node_dict = retrieveNodes(json_path)
    game_count = getGameCount(csv_filename)

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
    timeFormat(start,end, getNodeCount.__name__)

# ConvertPGNtoCSV('test_db.pgn')
# ConvertPGNtoCSV('test_db.pgn')
# getNodeDict('test_db.csv')

# ConvertPGNtoCSV('lichess_db_standard_rated_2015-01.pgn')
# ConvertPGNtoCSV('lichess_db_standard_rated_2015-02.pgn')
# ConvertPGNtoCSV('lichess_db_standard_rated_2015-03.pgn')

# ConvertPGNtoCSV('lichess_db_standard_rated_2015-04.pgn')
# ConvertPGNtoCSV('lichess_db_standard_rated_2015-05.pgn')
# ConvertPGNtoCSV('lichess_db_standard_rated_2015-06.pgn')
# ConvertPGNtoCSV('lichess_db_standard_rated_2015-07.pgn')
# ConvertPGNtoCSV('lichess_db_standard_rated_2015-08.pgn')
# ConvertPGNtoCSV('lichess_db_standard_rated_2015-09.pgn')
# ConvertPGNtoCSV('lichess_db_standard_rated_2015-10.pgn')
# ConvertPGNtoCSV('lichess_db_standard_rated_2015-11.pgn')
# ConvertPGNtoCSV('lichess_db_standard_rated_2015-12.pgn')

# getNodeCount('lichess_db_standard_rated_2014-01.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-02.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-03.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-04.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-05.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-06.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-07.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-08.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-09.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-10.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-11.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')
# getNodeCount('lichess_db_standard_rated_2014-12.csv', 'lichess_db_standard_rated_2014-12_nodes_zeros.txt')

# getNodeCount('test_db.csv', 'lichess_db_standard_rated_2014-12_nodes.txt')

# setZeroNew(getFilePath('lichess_db_standard_rated_2014-12_nodes.txt', 'nodelists'))

# SelectedNodesOnly(['lichess_db_standard_rated_2014-04.csv','lichess_db_standard_rated_2014-05.csv','lichess_db_standard_rated_2014-06.csv'], 'lichess_db_standard_rated_2014-12_nodes.txt')
# SelectedNodesOnly(['lichess_db_standard_rated_2014-07.csv','lichess_db_standard_rated_2014-08.csv','lichess_db_standard_rated_2014-09.csv'], 'lichess_db_standard_rated_2014-12_nodes.txt')
# SelectedNodesOnly(['lichess_db_standard_rated_2014-10.csv','lichess_db_standard_rated_2014-11.csv','lichess_db_standard_rated_2014-12.csv'], 'lichess_db_standard_rated_2014-12_nodes.txt')

# year_list = ['lichess_db_standard_rated_2014-01.csv', 'lichess_db_standard_rated_2014-02.csv', 'lichess_db_standard_rated_2014-03.csv', 'lichess_db_standard_rated_2014-04.csv', 'lichess_db_standard_rated_2014-05.csv', 'lichess_db_standard_rated_2014-06.csv', 'lichess_db_standard_rated_2014-07.csv', 'lichess_db_standard_rated_2014-08.csv', 'lichess_db_standard_rated_2014-09.csv', 'lichess_db_standard_rated_2014-10.csv', 'lichess_db_standard_rated_2014-11.csv', 'lichess_db_standard_rated_2014-12.csv']
# year_list = ['lichess_db_standard_rated_2014-04.csv', 'lichess_db_standard_rated_2014-05.csv', 'lichess_db_standard_rated_2014-06.csv']
# year_list = ['lichess_db_standard_rated_2014-07.csv', 'lichess_db_standard_rated_2014-08.csv', 'lichess_db_standard_rated_2014-09.csv']
# year_list = ['lichess_db_standard_rated_2014-10.csv', 'lichess_db_standard_rated_2014-11.csv', 'lichess_db_standard_rated_2014-12.csv']

SelectedNodesOnly(['lichess_db_standard_rated_2015-01.csv'], 'lichess_db_standard_rated_2014-12_nodes.txt')

# print(get_csv_length('csv\lichess_db_standard_rated_2015-01.csv'))