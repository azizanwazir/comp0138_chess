import chess.pgn
import csv
import os
import json
import sys
import time
import random

class DirectoryNotFound(Exception):
    pass

def getFolderPath(folder=""):
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

def getFilePath(filename, folder):
    file_extension = filename.split(".")
    file_extension = file_extension[-1:]
    folder_path = getFolderPath(folder)
    file_path = folder_path + '\\' + filename
    return file_path

def timeFormat(start,end, f_name):
    diff = end - start
    h = diff // 3600
    m = (diff - h*3600) // 60
    s = round((diff - h*3600 - m*60),4)
    sys.stdout.write("\n\nFunction: {0}\nTime Elapsed: {1}h {2}m {3}s\n".format(f_name,h,m,s))

def setZeroNew(json_path):
    ''' Sets all values in a JSON dictionary to 0 and creates a new file
    filename_zeros.txt '''
    start = time.time()
    node_dict = retrieveNodes(json_path)
    new_file_path = json_path[:-4] + '_zeros.txt'
    for key in node_dict:
        node_dict[key] = 0
    
    with open(new_file_path,'w') as file:
        file.write(json.dumps(node_dict))
    end = time.time()
    timeFormat(start,end, setZero.__name__)

def setZero(json_path):
    ''' Sets all values in a JSON dictionary to 0 and overwrites old file'''
    start = time.time()
    node_dict = retrieveNodes(json_path)
    for key in node_dict:
        node_dict[key] = 0
    
    with open(json_path,'w') as file:
        file.write(json.dumps(node_dict))
    end = time.time()
    timeFormat(start,end, setZero.__name__)

def retrieveNodes(json_path):
    # JSON to python dictionary conversion
    # Input: JSON file path
    with open(json_path) as json_file:
        nodes_dict = json.load(json_file)
    return nodes_dict

def getLichessDBDate(filename):
    if(filename[:26] == 'lichess_db_standard_rated_'):
        return filename [26:][:7]
    elif(filename == 'test_db.csv'):
        return '2010-01'

def getGameCount(filepath):
    ''' Returns the game count for each month based on the figures on database.lichess.org
    Input: Original file name of the PGN files downloaded from the website (in the form: lichess_db_standard_rated_201x_mm.pgn)''' 
    if(filepath[:-4] == 'test_db'):
        return 167
    elif(filepath[:-4] == 'test_db_cut'):
        return 139
    
    file_date = filepath[26:][:7]
        
    game_count_dict_pgn = {"2020-12":89422803,"2020-11":78268317,"2020-10":70572373,"2020-09":68027862,"2020-08":71405167,"2020-07":70592022,"2020-06":70374749,"2020-05":75628855,"2020-04":73224608,"2020-03":55544817,"2020-02":44004185,"2020-01":46800709,"2019-12":44055757,"2019-11":40357832,"2019-10":40440254,"2019-09":36996010,"2019-08":36745427,"2019-07":35728182,"2019-06":33935786,"2019-05":35236588,"2019-04":33565536,"2019-03":34869171,"2019-02":31023718,"2019-01":33886899,"2018-12":31179146,"2018-11":26136657,"2018-10":24784600,"2018-09":22971939,"2018-08":22635642,"2018-07":21070917,"2018-06":20273737,"2018-05":21442600,"2018-04":19881929,"2018-03":20036271,"2018-02":17383410,"2018-01":17945784,"2017-12":16232215,"2017-11":14306375,"2017-10":13703878,"2017-09":12564109,"2017-08":12458761,"2017-07":12080314,"2017-06":11512600,"2017-05":11693919,"2017-04":11348506,"2017-03":11346745,"2017-02":10194939,"2017-01":10680708,"2016-12":9433412,"2016-11":8021509,"2016-10":7599868,"2016-09":6813113,"2016-08":6483257,"2016-07":6275933,"2016-06":6136419,"2016-05":6225957,"2016-04":5922667,"2016-03":5801234,"2016-02":5015361,"2016-01":4770357,"2015-12":4161162,"2015-11":3595776,"2015-10":3400418,"2015-09":2844677,"2015-08":2621861,"2015-07":2455141,"2015-06":2324106,"2015-05":2137557,"2015-04":1785418,"2015-03":1742733,"2015-02":1495553,"2015-01":1497237,"2014-12":1350176,"2014-11":1209291,"2014-10":1111302,"2014-09":1000056,"2014-08":1013294,"2014-07":1048440,"2014-06":961868,"2014-05":905374,"2014-04":810463,"2014-03":795173,"2014-02":692394,"2014-01":697600,"2013-12":578262,"2013-11":487012,"2013-10":411039,"2013-09":325098,"2013-08":325525,"2013-07":293459,"2013-06":224679,"2013-05":179550,"2013-04":157871,"2013-03":158635,"2013-02":123961,"2013-01":121332}
    game_count_dict_csv = {'2015-01': 1473375, '2014-01': 691521, '2014-02': 686454, '2014-03': 785091, '2014-04': 799875, '2014-05': 902538, '2014-06': 961247, '2014-07': 1047989, '2014-08': 1012399, '2014-09': 999326, '2014-10': 1110572, '2014-11': 1206909, '2014-12': 1323444}
    if(filepath[-4:] == '.pgn'):
        return game_count_dict_pgn[file_date]
    elif(filepath[-4:] == '.csv'):
        return game_count_dict_csv[file_date]

def getDateIDDict(csv_filename):
    # Input format: "yyyy-mm"
    # Output format: {'dd':n}, where dd = date, n = id for the month
    date = getLichessDBDate(csv_filename)
    day_count_dict = {'01': 31, '02': 28, '03': 31, '04': 30, '05': 31, '06': 30, '07': 31, '08': 31, '09': 30, '10': 31, '11': 30, '12': 31}
    y, m = date.split("-")

    day_count = day_count_dict[m] + 1
    date_dict = dict()
    if(m == '01'): # Month is January
        prev_y = str(int(y) - 1)
        prev_y_date = '.'.join([prev_y, '12','31'])
        date_dict[prev_y_date] = 0
        for i in range(1,day_count):
            i_str = str(i)
            if(i < 10):
                i_str = "0" + str(i)
            add_date = '.'.join([y,m,i_str])
            date_dict[add_date] = i
        return day_count, date_dict

    if(y == '2016' and m == '02'): # leap year
        prev_date = '2016.01.31'
        date_dict[prev_date] = 0
        for i in range(1, 29):
            i_str = str(i)
            if(i < 10):
                i_str = "0" + str(i)
            add_date = '.'.join([y,m,i_str])
            date_dict[add_date] = i
        return day_count, date_dict
    
    prev_m = int(m) - 1
    if(prev_m < 10):
        prev_m = "0" + str(prev_m)
    else:
        prev_m = str(prev_m)

    prev_date = '.'.join([y,prev_m, str(day_count_dict[prev_m])])
    date_dict[prev_date] = 0
    
    for i in range(1, day_count):
        i_str = str(i)
        if(i < 10):
            i_str = "0" + str(i)
        add_date = '.'.join([y,m,i_str])
        date_dict[add_date] = i
    return day_count, date_dict

def averageTimeBetweenSessions(game_ls):
    # Find total number of zeros in the list (days on which player played no games: days of inactivity) and divide by number of periods of inactivity (consecutive days of inactivity)
    # i.e. [0, 1, 1, 0, 0, 1, 1, 0] --> 4 days of inactivity, 3 periods of activity
    # return 4/3 = 1.34 days between sessions on average

    # TODO: Ignore leading and trailing zeros
    # i.e. [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0] gives average 0 days between sessions instead of 4 (8 inactive days/2 inactive periods)
    
    inactive_days = 0
    inactive_periods = 0
    # active_periods = 0
    for d in range(0, len(game_ls)):
        if(d == len(game_ls) - 1):
            if(game_ls[d] == 0):
                inactive_days += 1
                inactive_periods += 1
        else:
            if(game_ls[d] == 0):
                inactive_days += 1
                if(game_ls[d+1] != 0):
                    inactive_periods += 1
                else:
                    # active_periods += 1
                    pass
                
            
    if(inactive_periods == 0):
        return 0
    else:
        return inactive_days/inactive_periods

def ActiveInactiveDaysAndPeriods(game_ls):
    # Find total number of zeros in the list (days on which player played no games: days of inactivity) and divide by number of periods of inactivity (consecutive days of inactivity)
    # i.e. [0, 1, 1, 0, 0, 1, 1, 0] --> 4 days of inactivity, 3 periods of activity
    # return 4/3 = 1.34 days between sessions on average

    # TODO: Ignore leading and trailing zeros
    # i.e. [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0] gives average 0 days between sessions instead of 4 (8 inactive days/2 inactive periods)
    
    inactive_days = 0
    inactive_periods = 0
    active_days = 0
    active_periods = 0
    for d in range(0, len(game_ls)):
        if(d == len(game_ls) - 1):
            if(game_ls[d] == 0):
                inactive_days += 1
                inactive_periods += 1
            else:
                active_days += 1
                active_periods += 1
        else:
            if(game_ls[d] == 0):
                inactive_days += 1
                if(game_ls[d+1] != 0):
                    inactive_periods += 1
            else:
                active_days += 1
                if(game_ls[d+1] == 0):
                    active_periods += 1

                   
                
    return active_days, inactive_days, active_periods, inactive_periods

def averageSessionDays(game_ls):
    # Find total number of zeros in the list (days on which player played no games: days of inactivity) and divide by number of periods of inactivity (consecutive days of inactivity)
    # i.e. [0, 1, 1, 0, 0, 1, 1, 0] --> 4 days of inactivity, 3 periods of activity
    # return 4/3 = 1.34 days between sessions on average

    # TODO: Ignore leading and trailing zeros
    # i.e. [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0] gives average 0 days between sessions instead of 4 (8 inactive days/2 inactive periods)
    
    active_days = 0
    active_periods = 0

    for d in range(0, len(game_ls)):
        if(d == len(game_ls) - 1):
            if(game_ls[d] != 0):
                active_days += 1
                active_periods += 1
        else:
            if(game_ls[d] != 0):
                active_days += 1
                if(game_ls[d+1] == 0):
                    active_periods += 1
                
    if(active_periods == 0):
        return 0
    else:
        return active_days/active_periods

# https://stackoverflow.com/questions/55771644/max-consecutive-ones
def findMaxStreaks(nums):
    slow, fast, glo_max, loc_max = 0, 0, 0, 0
    while fast < len(nums):
        if nums[fast] == 0 or nums[fast] == -1:
            loc_max = fast - slow  
            glo_max = max(glo_max, loc_max)
            slow = fast + 1      # need to add one more because we haven't incremented fast yet

        fast += 1
    loc_max = fast - slow        # end check for cases that end with 1
    max_win_streak = max(loc_max, glo_max)

    slow, fast, glo_max, loc_max = 0, 0, 0, 0
    while fast < len(nums):
        if nums[fast] == 0 or nums[fast] == 1:
            loc_max = fast - slow  
            glo_max = max(glo_max, loc_max)
            slow = fast + 1      # need to add one more because we haven't incremented fast yet

        fast += 1
    loc_max = fast - slow        # end check for cases that end with 1
    max_lose_streak = max(loc_max, glo_max)
    return max_win_streak, max_lose_streak


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

# Assigns a numerical ID to each user
# DO NOT PUBLISH
# REMOVE SEED
def anonymiseJSON(json_filename):
    node_dict = retrieveNodes(getFilePath(json_filename, 'nodelists'))
    new_dict = dict()
    seed = 10 # Remove
    i = 0
    index_list = [x for x in range(1, len(node_dict) + 1)]
    
    random.Random(seed).shuffle(index_list)
    for key in node_dict:
        new_dict[key] = index_list[i]
        i += 1

    txt_folder = 'nodelists'
    txt_filename = 'id_nodelist_new.txt'
    txt_path = getFilePath(txt_filename, txt_folder)
    with open(txt_path,'w') as file:
        file.write(json.dumps(new_dict))

def renameNodes(csv_file, nodes):
    start = time.time()
    node_dict = retrieveNodes(getFilePath(nodes, 'nodelists'))
    # Get path names
    csv_folder = 'csv'
    csv_path = getFilePath(csv_file, csv_folder)
    row_list = []

    i = 1
    with open(csv_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        for row in csv_reader:
            white_id = row["white_id"]
            black_id = row["black_id"]
            if(white_id not in node_dict and black_id not in node_dict):
                continue
            if(white_id in node_dict):
                row["white_id"] = node_dict[white_id]
            else:
                row["white_id"] = "stranger"
            if(black_id in node_dict):
                row["black_id"] = node_dict[black_id]
            else:
                row["black_id"] = "stranger"
            row_list.append(row)

            sys.stdout.write("\r Added: {0}>".format(len(row_list)))
            sys.stdout.flush()

    with open(csv_path, "w", newline="") as f:
        # Abridged list of headers
        writer = csv.DictWriter(f, ['id','date', 'white_id','black_id','result','white_rating','black_rating'], extrasaction='ignore')
        writer.writeheader()
        writer.writerows(row_list)

    end = time.time()
    timeFormat(start,end, getNodeDict.__name__)

def renameHeaders(csv_file, rename=False, json=None):
    
    # Current headers of the CSV file
    original_headers = ['id','date', 'white_id','black_id','result','white_elo','black_elo']
    
    # Headers to change to
    final_headers = {'id': 'id', 'date': 'date', 'white_id': 'white_id', 'black_id': 'black_id', 'result': 'result', 'white_elo': 'white_rating', 'black_elo': 'black_rating'}

    row_list = []
    csv_path = getFilePath(csv_file, 'csv')

    if(rename == False):
        with open(csv_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            i = 0
            for row in csv_reader:
                row_list.append(row)
                sys.stdout.write("\r Added {0} lines.".format(i))
                i += 1
    else:
        node_dict = retrieveNodes(getFilePath(json, 'nodelists'))
        with open(csv_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                white_id = row["white_id"]
                black_id = row["black_id"]
                if(white_id in node_dict):
                    row["white_id"] = node_dict[white_id]
                else:
                    row["white_id"] = "stranger"
                if(black_id in node_dict):
                    row["black_id"] = node_dict[black_id]
                else:
                    row["black_id"] = "stranger"
                row_list.append(row)

                sys.stdout.write("\r Added: {0}>".format(len(row_list)))
                sys.stdout.flush()

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, original_headers, extrasaction='ignore')
        writer.writerow(final_headers)
        writer.writerows(row_list)


def anonList(json_f):
    node_dict = retrieveNodes(getFilePath(json_f, 'nodelists'))
    new_dict = dict()

    for key in node_dict:
        new_dict[node_dict[key]] = node_dict[key]

    txt_folder = 'nodelists'
    txt_filename = 'id_nodelist.txt'
    txt_path = getFilePath(txt_filename, txt_folder)
    with open(txt_path,'w') as file:
        file.write(json.dumps(new_dict))

def removeNodes(full, cut):
    full_dict = retrieveNodes(getFilePath(full, 'nodelists'))
    cut_dict = retrieveNodes(getFilePath(cut, 'nodelists'))
    new_dict = dict()
    for key in cut_dict:
        new_dict[key] = full_dict[key]

    txt_folder = 'nodelists'
    txt_filename = 'cut_id_nodelist.txt'
    txt_path = getFilePath(txt_filename, txt_folder)
    with open(txt_path,'w') as file:
        file.write(json.dumps(new_dict))


# renameHeaders('lichess_db_standard_rated_2014-12_cut.csv')
# renameHeaders('lichess_db_standard_rated_2014-11_cut.csv')
# renameHeaders('lichess_db_standard_rated_2014-10_cut.csv')
# renameHeaders('lichess_db_standard_rated_2014-09_cut.csv')
# renameHeaders('lichess_db_standard_rated_2014-08_cut.csv')
# renameHeaders('lichess_db_standard_rated_2014-07_cut.csv')
# renameHeaders('lichess_db_standard_rated_2014-06_cut.csv')
# renameHeaders('lichess_db_standard_rated_2014-05_cut.csv')
# renameHeaders('lichess_db_standard_rated_2014-04_cut.csv')
# renameHeaders('lichess_db_standard_rated_2014-01_cut.csv')

# renameNodes('lichess_db_standard_rated_2014-01_cut.csv', 'player_nodelist_map.txt')

# renameHeaders('lichess_db_standard_rated_2014-01_cut - Copy.csv', True, 'id_nodelist.txt')
# multiple(['lichess_db_standard_rated_2015-01_cut.csv','lichess_db_standard_rated_2015-02_cut.csv','lichess_db_standard_rated_2015-03_cut.csv', 'lichess_db_standard_rated_2015-04_cut.csv'])
# multiple(['lichess_db_standard_rated_2015-05_cut.csv','lichess_db_standard_rated_2015-06_cut.csv', 'lichess_db_standard_rated_2015-07_cut.csv'])
# multiple(['lichess_db_standard_rated_2015-08_cut.csv','lichess_db_standard_rated_2015-09_cut.csv', 'lichess_db_standard_rated_2015-10_cut.csv'])
# multiple(['lichess_db_standard_rated_2015-11_cut.csv','lichess_db_standard_rated_2015-12_cut.csv'])
# removeNodes('id_nodelist.txt', 'id_nodelist_new.txt')

