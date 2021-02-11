import chess.pgn
import csv
import os
import json
import sys
import time

class DirectoryNotFound(Exception):
    pass

def get_path_folder(folder=""):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if(folder == ""):
        # Return base directory
        return dir_path
    else:
        dir_path = dir_path + '\\' + folder
        if(os.path.exists(dir_path)):
            return dir_path
        else:
            raise DirectoryNotFound

def get_path_file(filename, folder):
    file_extension = filename.split(".")
    file_extension = file_extension[-1:]
    folder_path = get_path_folder(folder)
    file_path = folder_path + '\\' + filename
    return file_path

def time_format(start,end, f_name):
    diff = end - start
    h = diff // 3600
    m = (diff - h*3600) // 60
    s = round((diff - h*3600 - m*60),4)
    sys.stdout.write("\n\nFunction: {0}\nTime Elapsed: {1}h {2}m {3}s\n".format(f_name,h,m,s))

def set_zero_new(json_path):
    ''' Sets all values in a JSON dictionary to 0 and creates a new file
    filename_zeros.txt '''
    start = time.time()
    node_dict = retrieve_nodes(json_path)
    new_file_path = json_path[:-4] + '_zeros.txt'
    for key in node_dict:
        node_dict[key] = 0
    
    with open(new_file_path,'w') as file:
        file.write(json.dumps(node_dict))
    end = time.time()
    time_format(start,end, set_zero.__name__)

def set_zero(json_path):
    ''' Sets all values in a JSON dictionary to 0 and overwrites old file'''
    start = time.time()
    node_dict = retrieve_nodes(json_path)
    for key in node_dict:
        node_dict[key] = 0
    
    with open(json_path,'w') as file:
        file.write(json.dumps(node_dict))
    end = time.time()
    time_format(start,end, set_zero.__name__)

def retrieve_nodes(json_path):
    # JSON to python dictionary conversion
    # Input: JSON file path
    with open(json_path) as json_file:
        nodes_dict = json.load(json_file)
    return nodes_dict

def get_game_count(filepath):
    ''' Returns the game count for each month based on the figures on database.lichess.org
    Input: Original file name of the PGN files downloaded from the website (in the form: lichess_db_standard_rated_201x_mm.pgn)''' 
    if(filepath[:-4] == 'test_db'):
        return 167
    elif(filepath[:-4] == 'test_db_cut'):
        return 139
    
    file_date = filepath[26:][:7]
        
    game_count_dict_pgn = {"2020-12":89422803,"2020-11":78268317,"2020-10":70572373,"2020-09":68027862,"2020-08":71405167,"2020-07":70592022,"2020-06":70374749,"2020-05":75628855,"2020-04":73224608,"2020-03":55544817,"2020-02":44004185,"2020-01":46800709,"2019-12":44055757,"2019-11":40357832,"2019-10":40440254,"2019-09":36996010,"2019-08":36745427,"2019-07":35728182,"2019-06":33935786,"2019-05":35236588,"2019-04":33565536,"2019-03":34869171,"2019-02":31023718,"2019-01":33886899,"2018-12":31179146,"2018-11":26136657,"2018-10":24784600,"2018-09":22971939,"2018-08":22635642,"2018-07":21070917,"2018-06":20273737,"2018-05":21442600,"2018-04":19881929,"2018-03":20036271,"2018-02":17383410,"2018-01":17945784,"2017-12":16232215,"2017-11":14306375,"2017-10":13703878,"2017-09":12564109,"2017-08":12458761,"2017-07":12080314,"2017-06":11512600,"2017-05":11693919,"2017-04":11348506,"2017-03":11346745,"2017-02":10194939,"2017-01":10680708,"2016-12":9433412,"2016-11":8021509,"2016-10":7599868,"2016-09":6813113,"2016-08":6483257,"2016-07":6275933,"2016-06":6136419,"2016-05":6225957,"2016-04":5922667,"2016-03":5801234,"2016-02":5015361,"2016-01":4770357,"2015-12":4161162,"2015-11":3595776,"2015-10":3400418,"2015-09":2844677,"2015-08":2621861,"2015-07":2455141,"2015-06":2324106,"2015-05":2137557,"2015-04":1785418,"2015-03":1742733,"2015-02":1495553,"2015-01":1497237,"2014-12":1350176,"2014-11":1209291,"2014-10":1111302,"2014-09":1000056,"2014-08":1013294,"2014-07":1048440,"2014-06":961868,"2014-05":905374,"2014-04":810463,"2014-03":795173,"2014-02":692394,"2014-01":697600,"2013-12":578262,"2013-11":487012,"2013-10":411039,"2013-09":325098,"2013-08":325525,"2013-07":293459,"2013-06":224679,"2013-05":179550,"2013-04":157871,"2013-03":158635,"2013-02":123961,"2013-01":121332}
    game_count_dict_csv = {'2014-01': 691521, '2014-02': 686454, '2014-03': 785091, '2014-04': 799875, '2014-05': 902538, '2014-06': 961247, '2014-07': 1047989, '2014-08': 1012399, '2014-09': 999326, '2014-10': 1110572, '2014-11': 1206909, '2014-12': 1323444}
    if(filepath[-4:] == '.pgn'):
        return game_count_dict_pgn[file_date]
    elif(filepath[-4:] == '.csv'):
        return game_count_dict_csv[file_date]

def get_lichess_db_date(filename):
    if(filename[:26] == 'lichess_db_standard_rated_'):
        return filename [26:][:7]
    elif(filename == 'test_db.csv'):
        return '2010-01'

def get_game_count_csv(csv_filename):
    ''' Returns the game count extracted into the CSV file (without incomplete games)
    Input: File name of the CSV files processed from datasheets from the website (in the form: lichess_db_standard_rated_201x_mm.csv)''' 
    if(csv_filename == 'test_db.csv'):
        return 167
    elif(csv_filename == 'test_db_cut.csv'):
        return 139
    csv_date = get_lichess_db_date(csv_filename)
    game_count_dict_csv = {'2014-01': 691521, '2014-02': 686454, '2014-03': 785091, '2014-04': 799875, '2014-05': 902538, '2014-06': 961247, '2014-07': 1047989, '2014-08': 1012399, '2014-09': 999326, '2014-10': 1110572, '2014-11': 1206909, '2014-12': 1323444}
    return game_count_dict_csv[csv_date]

def get_csv_length(csv_filename):
    ''' Returns number of rows in a csv file
    Input: File name of CSV file'''
    file = open(csv_filename)
    reader = csv.reader(file)
    lines = len(list(reader))

    return lines

def get_csv_game_count_dict(year):
    def_string = "lichess_db_standard_rated_"
    game_count_dict = {}
    for i in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        file_name = str(year) + '-' + i + '.csv'
        full_file_name = def_string + file_name
        file = open(full_file_name)
        reader = csv.reader(file)
        game_count_dict[file_name[:-4]] = len(list(reader))

    return game_count_dict



''' CSV headers for Lichess files '''
# csv_headers = ['id',
#                'date',
#                'event', 
#                'white_id',
#                'black_id',
#                'result',
#                'white_elo',
#                'white_elo_diff',
#                'black_elo',
#                'black_elo_diff',
#                'eco'
#                ]


# Don't use these two function. They were originally written to extract data from PGN files
# but processing CSV files is much, much faster
def get_node_count(pgn_filename, json_filename):
    '''Iterates through the nodes in pgn_filename, checks each game for 
    white_id and black_id to see if they are in node_dict (json_filename)
    and adds one to their respective dictionary entry if they are present.
    Ignores otherwise. Finally, removes any elements in the dictionary
    which have a count of zero

    Input: name of PGN and JSON files with their extensions and the number of games
    in the PGN file (from Lichess.org)'''
    start = time.time()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    pgn_path = dir_path + '\\' + pgn_filename
    pgn_name = pgn_filename[26:][:7]
    json_path = dir_path + '\\' + json_filename[:-4] + '_' + pgn_name +'.txt'
    node_dict = retrieve_nodes(json_filename)
    game_count = get_game_count(pgn_filename)
    pgn = open(pgn_path, encoding='utf-8-sig')

    for i in range(0,game_count):
        game = chess.pgn.read_game(pgn)
        white_id = game.headers['White']
        black_id = game.headers['Black']

        if(white_id in node_dict):
            node_dict[white_id] += 1
        if(black_id in node_dict):
            node_dict[black_id] += 1

        sys.stdout.write("\r Processed: {0}/{1}".format(i+1,game_count))
        sys.stdout.flush()
    
    for key in list(node_dict):
        if(node_dict[key] == 0):
            node_dict.pop(key, None)

    with open(json_path,'w') as file:
        file.write(json.dumps(node_dict))
    end = time.time()
    time_format(start,end)

def get_node_dict(filename):
    '''Used to obtain a dictionary of all the nodes in a PGN file
    '''
    start = time.time()
    pgn_folder = 'pgn'
    txt_folder = 'nodelist'
    txt_filename = filename[:-4] + '.txt'
    pgn_path = get_path_file(filename, pgn_folder)
    txt_path = get_path_file(txt_filename, txt_folder)

    node_dict = {}
    game_count = get_game_count(filename)

    pgn = open(pgn_path, encoding='utf-8-sig')

    for i in range(0,game_count):
        game = chess.pgn.read_game(pgn)
        white_id = game.headers['White']
        black_id = game.headers['Black']
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
    
    with open(txt_path,'w') as file:
        file.write(json.dumps(node_dict))
    end = time.time()
    time_format(start,end, get_node_dict.__name__)
    