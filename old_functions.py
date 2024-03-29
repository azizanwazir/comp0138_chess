
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
    #row_list = [['id','date','white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff']]
    row_list = [['ID','Date','White ID', 'Black ID','Result','White Rating','White Rating Change','Black Rating','Black Rating Change']]

    game_id = 1
    invalid = 0
    game_count = getGameCount(filename)
    for i in range(0, game_count):
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
            game_white      = game.headers['White']
            game_black      = game.headers['Black']
            game_result     = game.headers['Result']
            game_white_elo  = game.headers['WhiteElo']
            game_white_diff = game.headers['WhiteRatingDiff']
            game_black_elo  = game.headers['BlackElo']
            game_black_diff = game.headers['BlackRatingDiff']
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
        game_list.append(game_white)
        game_list.append(game_black)
        game_list.append(game_result)
        game_list.append(game_white_elo)
        game_list.append(game_white_diff)
        game_list.append(game_black_elo)
        game_list.append(game_black_diff)
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
    #final_headers = {'id': 'ID', 'date': 'Date', 'white_id': 'White ID', 'black_id': 'Black ID', 'result': 'Results', 'white_elo': 'White Rating', 'white_elo_diff': 'White Rating Change', 'black_elo': 'Black Rating', 'black_elo_diff': 'Black Rating Change'}
    start = time.time()
    total_removed = 0

    for csv_filename in csv_filename_list:
        row_list = []
        removed = 0
        csv_path = getFilePath(csv_filename, 'csv')
        node_dict_filepath = getFilePath(json_filename, 'nodelists')
        node_dict = retrieveNodes(node_dict_filepath)
    
        with open(csv_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            i = 0
            for row in csv_reader:
                white_id = row["white_id"]
                black_id = row["black_id"]
                if(white_id not in node_dict and black_id not in node_dict):
                    removed += 1
                else:
                    if(white_id in node_dict):
                        row["white_id"] = node_dict[white_id]
                    else:
                        row["white_id"] = "stranger"
                    if(black_id in node_dict):
                        row["black_id"] = node_dict[black_id]
                    else:
                        row["black_id"] = "stranger"

                    row_list.append(row)
                sys.stdout.write("\r Added: {0}, Removed: {1}>".format(len(row_list),removed))
                sys.stdout.flush()
                i += 1

        sys.stdout.write("\r Added: {0}, Removed: {1} from {2}>".format(len(row_list),removed, getLichessDBDate(csv_filename)))

        new_csv_name = csv_filename[:-4] + "_cut.csv"
        new_csv_path = getFilePath(new_csv_name, 'csv')

        with open(new_csv_path, "w", newline="") as f:
            # Abridged list of headers
            # writer = csv.DictWriter(f, ['id','date', 'white_id','black_id','result','white_elo','white_elo_diff','black_elo','black_elo_diff'], extrasaction='ignore')
            writer = csv.DictWriter(f, ['ID','Date','White ID', 'Black ID','Result','White Rating','White Rating Change','Black Rating','Black Rating Change'], extrasaction='ignore')
            writer.writeheader
            writer.writerows(row_list)

        total_removed += removed
        sys.stdout.write("\n\n Dataset: {0} processed\n\n".format(csv_filename))

    sys.stdout.write("\n\n Processed the following datasets: \n")
    
    for i in range(1,len(csv_filename_list)+1):
        sys.stdout.write("{0}. {1}\n".format(i, csv_filename_list[i-1]))

    sys.stdout.write("\n\n\r {0} rows deleted.".format(total_removed))
    end = time.time()
    timeFormat(start, end, SelectedNodesOnly.__name__)

def ProcessPGN(pgn_list, json_nodelist):
    # Converts PGN to CSV
    # Then gets only selected nodes from the new CSV file
    # TODO: Delete the old CSV file
    for pgn_file in pgn_list:
        csv_filename = pgn_file[:-3] + 'csv'
        start = time.time()
        ConvertPGNtoCSV(pgn_file)
        SelectedNodesOnly([csv_filename], json_nodelist)
        end = time.time()
        timeFormat(start, end, ProcessPGN.__name__)


def CreateNodelistSeparate(csv_filename_list, json_filename):
    start = time.time()
    node_dict = retrieveNodes(getFilePath(json_filename, 'nodelists'))
    node_dict_zero = node_dict
    for key in node_dict_zero:
        node_dict_zero[key] = 0

    sys.stdout.write("\r \n######################################\n Reading and preprocessing {0} CSV files \n This may take some time. \n--------------------------------------\n".format(len(csv_filename_list)))

    for csv_f in csv_filename_list:
        row_list = [['id', 'player', 'start_elo', 'end_elo', 'max_elo', 'min_elo', 'avg_elo', 'w_below_neg_300', 'w_neg_200_to_299', 'w_neg_100_to_199', 'w_neg_50_to_99', 'w_neg_1_to_49', 'w_zero', 'w_1_to_49', 'w_50_to_99', 'w_100_to_199', 'w_200_to_299', 'w_above_pos_300', 'l_below_neg_300', 'l_neg_200_to_299', 'l_neg_100_to_199', 'l_neg_50_to_99', 'l_neg_1_to_49', 'l_zero', 'l_1_to_49', 'l_50_to_99', 'l_100_to_199', 'l_200_to_299', 'l_above_pos_300', 'd_below_neg_300', 'd_neg_200_to_299', 'd_neg_100_to_199', 'd_neg_50_to_99', 'd_neg_1_to_49', 'd_zero', 'd_1_to_49', 'd_50_to_99', 'd_100_to_199', 'd_200_to_299', 'd_above_pos_300', 'w_Grandmaster', 'w_Master',  'w_ClassA',  'w_ClassB',  'w_ClassC',  'w_ClassD',  'w_Novice',  'l_Grandmaster',  'l_Master', 'l_ClassA', 'l_ClassB', 'l_ClassC', 'l_ClassD', 'l_Novice',  'd_Grandmaster',  'd_Master',  'd_ClassA',  'd_ClassB',  'd_ClassC',  'd_ClassD',  'd_Novice', 'win_count',  'loss_count',  'draw_count', 'win_loss_ratio',  'max_win_streak',  'max_lose_streak', 'max_elo_diff',  'min_elo_diff',  'avg_elo_diff',  'win_higher_count',  'win_lower_count',  'win_even_count',  'loss_higher_count',  'loss_lower_count',  'loss_even_count',  'draw_higher_count',  'draw_lower_count',  'draw_even_count',  'opponent_count', 'game_count',  'avg_daily_games',  'avg_weekly_games',  'avg_days_between_sessions',  'full_day_count']]
 
        id = 1
        sys.stdout.write("\r Retriving data from {0}\n".format(csv_f))
        csv_path = getFilePath(csv_f, 'csv')
        
        csv_date = getLichessDBDate(csv_f)
        nodelist_filename = 'nodelist_{0}.csv'.format(csv_date)

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

        for player in node_dict:
            sys.stdout.write("\r{1}/{2}:\t Player: {0}".format(player, id, len(node_dict)))
            sys.stdout.flush()

            # 1st perspective: Progress
            # Starting, ending, average, min and max elo (of the player) for a time frame 
            #   --> start_elo, end_elo, avg_elo, min_elo, max_elo
            start_elo = 0
            end_elo = 0
            avg_elo = 0
            min_elo = 0
            max_elo = 0

            # Win, loss and draw counts, max win streak, max lose streak 
            #   --> win_count, loss_count, draw_count, max_win_streak, max_lose_streak

            win_count = 0
            loss_count = 0
            draw_count = 0
            win_loss_ratio = 0
            max_win_streak = 0
            max_lose_streak = 0

            # Win, loss and draw counts against higher and lower ranked opponents
            #   --> w_below_neg_300, w_neg_200_to_299, w_neg_100_to_199, w_neg_50_to_99, w_neg_1_to_49
            #   --> w_zero
            #   --> w_1_to_49, w_50_to_99, w_100_to_199, w_200_to_299, w_above_300

            w_below_neg_300 = 0
            w_neg_200_to_299 = 0
            w_neg_100_to_199 = 0
            w_neg_50_to_99 = 0
            w_neg_1_to_49 = 0
            w_zero = 0
            w_1_to_49 = 0
            w_50_to_99 = 0
            w_100_to_199 = 0
            w_200_to_299 = 0
            w_above_pos_300 = 0

            # and the same for loss (i.e. l_below_neg_300..)
            l_below_neg_300 = 0
            l_neg_200_to_299 = 0
            l_neg_100_to_199 = 0
            l_neg_50_to_99 = 0
            l_neg_1_to_49 = 0
            l_zero = 0
            l_1_to_49 = 0
            l_50_to_99 = 0
            l_100_to_199 = 0
            l_200_to_299 = 0
            l_above_pos_300 = 0

            # and the same for loss (i.e. l_below_neg_300..)
            d_below_neg_300 = 0
            d_neg_200_to_299 = 0
            d_neg_100_to_199 = 0
            d_neg_50_to_99 = 0
            d_neg_1_to_49 = 0
            d_zero = 0
            d_1_to_49 = 0
            d_50_to_99 = 0
            d_100_to_199 = 0
            d_200_to_299 = 0
            d_above_pos_300 = 0

            '''New'''
            # Progress (Absolute)
            # Number of wins, losses and draws against players of a particular Elo rating (in ranges)
            w_Grandmaster = 0    # > 2300 
            w_Master = 0  # 2000 > x > 2300
            w_ClassA = 0  # 1800 > x > 2000
            w_ClassB = 0  # 1600 > x > 1800
            w_ClassC = 0  # 1400 > x > 1600
            w_ClassD = 0  # 1200 > x > 1400
            w_Novice = 0 # < 1200 
            
            l_Grandmaster = 0    # > 2300 
            l_Master = 0  # 2000 > x > 2300
            l_ClassA = 0  # 1800 > x > 2000
            l_ClassB = 0  # 1600 > x > 1800
            l_ClassC = 0  # 1400 > x > 1600
            l_ClassD = 0  # 1200 > x > 1400
            l_Novice = 0 # < 1200 

            d_Grandmaster = 0    # > 2300 
            d_Master = 0  # 2000 > x > 2300
            d_ClassA = 0  # 1800 > x > 2000
            d_ClassB = 0  # 1600 > x > 1800
            d_ClassC = 0  # 1400 > x > 1600
            d_ClassD = 0  # 1200 > x > 1400
            d_Novice = 0 # < 1200 

            # 2nd perspective: Strategy
            # Average, min, max elo (opponent elo - player elo = elo_diff, i.e. negative = lower rated)
            #   --> avg_elo_diff, min_elo_diff, max_elo_diff
            max_elo_diff = 0
            min_elo_diff = 0
            avg_elo_diff = 0

            # Matches played against higher and lower rated opponents
            #   --> Sum of win, loss, draw counts of higher, lower and zero difference from 1st perspective
            #   --> win_higher_count, win_lower_count, win_even_count (and the same for loss and draw)
            win_higher_count = 0
            win_lower_count = 0
            win_even_count = 0
            loss_higher_count = 0
            loss_lower_count = 0
            loss_even_count = 0
            draw_higher_count = 0
            draw_lower_count = 0
            draw_even_count = 0

            # 3rd perspective: Activity
            # Number of games played
            #   --> game_count
            game_count = 0

            # Average daily and weekly games
            #   --> avg_daily_games, avg_weekly_games
            avg_daily_games = 0
            avg_weekly_games = 0

            # Average time between games
            #   --> avg_time_between_games
            avg_days_between_sessions = 0

            # List of games played on each day of a given month
            #   --> daily_game_count
            #       format: 1.0.5.0.1. (etc) means one day 1, 1 game was played. on day 2, 10 games, etc.
            daily_game_count = [0] * day_count

            # Unique list of opponents the player has played
            opponent_list = [g for g in G[player]]
            
            elo_list = []

            # The elo_diff_list and win_loss_list will be of the same size. The elo_diff_list contains the 
            # actual difference in Elo between the player and opponent (e.g, [-10, -100, 50, -25])
            # Whereas the win_loss_list contains the results of each match (e.g. [1, -1, 0, 1])
            # This indicates that the player won, loss, drew and won for -10, -100, 50 and -25 respectively
            elo_diff_list = []
            win_loss_list = []

            for opp in opponent_list:
                # opponent_list is a list of unique player IDs the player (player) has played against
                # each opponent (opp) in opponent_list may have more than one game played against the player
                game_list = G[player][opp]
                for g in game_list:
                    # each game played between a particular opponent opp and the player is g
                    game = game_list[g]
                    white = game['white_id']
                    game_count += 1

                    # format: yyyy.mm.dd
                    date = game['date']
                    date_index = date_dict[date]
                    daily_game_count[date_index] += 1
                    # If the player played as white
                    if(white == player):
                        # Add player's Elo before the match
                        elo_list.append(game['white_elo'])
                        # Add Elo rating difference 
                        opp_elo = game['black_elo']
                        elo_difference = game['black_elo'] - game['white_elo']
                        elo_diff_list.append(elo_difference)

                        # If the game was won
                        if(game['result'] == '1-0'):
                            # Add '1' indicating a victory
                            win_loss_list.append(1)
                            
                            # Add to respective sum of games won against higher, lower or evenly rated opponents
                            if(elo_difference > 0):
                                win_higher_count += 1
                            elif(elo_difference < 0):
                                win_lower_count += 1
                            else:
                                win_even_count += 1
                            
                            if(opp_elo >= 2300):
                                w_Grandmaster += 1
                            elif(opp_elo >= 2000):
                                w_Master += 1
                            elif(opp_elo >= 1800):
                                w_ClassA += 1
                            elif(opp_elo >= 1600):
                                w_ClassB += 1
                            elif(opp_elo >= 1400):
                                w_ClassC += 1
                            elif(opp_elo >= 1200):
                                w_ClassD += 1
                            else:
                                w_Novice += 1

                                
                        # If the game was a draw
                        elif(game['result'] == '1/2-1/2'):
                            # Add '0' indicating a draw
                            win_loss_list.append(0)

                            # Add to respective sum of games drawn against higher, lower or evenly rated opponents
                            if(elo_difference > 0):
                                draw_higher_count += 1
                            elif(elo_difference < 0):
                                draw_lower_count += 1
                            else:
                                draw_even_count += 1

                            if(opp_elo >= 2300):
                                d_Grandmaster += 1
                            elif(opp_elo >= 2000):
                                d_Master += 1
                            elif(opp_elo >= 1800):
                                d_ClassA += 1
                            elif(opp_elo >= 1600):
                                d_ClassB += 1
                            elif(opp_elo >= 1400):
                                d_ClassC += 1
                            elif(opp_elo >= 1200):
                                d_ClassD += 1
                            else:
                                d_Novice += 1
                        else:
                            # Add '-1' indicating a loss
                            win_loss_list.append(-1)

                            # Add to respective sum of games lost against higher, lower or evenly rated opponents
                            if(elo_difference > 0):
                                loss_higher_count += 1
                            elif(elo_difference < 0):
                                loss_lower_count += 1
                            else:
                                loss_even_count += 1
                            
                            if(opp_elo >= 2300):
                                l_Grandmaster += 1
                            elif(opp_elo >= 2000):
                                l_Master += 1
                            elif(opp_elo >= 1800):
                                l_ClassA += 1
                            elif(opp_elo >= 1600):
                                l_ClassB += 1
                            elif(opp_elo >= 1400):
                                l_ClassC += 1
                            elif(opp_elo >= 1200):
                                l_ClassD += 1
                            else:
                                l_Novice += 1

                    # If player played as black 
                    else:
                        elo_list.append(game['black_elo'])
                        opp_elo = game['white_elo']
                        elo_difference = game['white_elo'] - game['black_elo']

                        elo_diff_list.append(elo_difference)
                        if(game['result'] == '0-1'):
                            win_loss_list.append(1)
                            if(elo_difference > 0):
                                win_higher_count += 1
                            elif(elo_difference < 0):
                                win_lower_count += 1
                            else:
                                win_even_count += 1
                            
                            if(opp_elo >= 2300):
                                w_Grandmaster += 1
                            elif(opp_elo >= 2000):
                                w_Master += 1
                            elif(opp_elo >= 1800):
                                w_ClassA += 1
                            elif(opp_elo >= 1600):
                                w_ClassB += 1
                            elif(opp_elo >= 1400):
                                w_ClassC += 1
                            elif(opp_elo >= 1200):
                                w_ClassD += 1
                            else:
                                w_Novice += 1

                        elif(game['result'] == '1/2-1/2'):
                            win_loss_list.append(0)
                            if(elo_difference > 0):
                                draw_higher_count += 1
                            elif(elo_difference < 0):
                                draw_lower_count += 1
                            else:
                                draw_even_count += 1
                            if(opp_elo >= 2300):
                                d_Grandmaster += 1
                            elif(opp_elo >= 2000):
                                d_Master += 1
                            elif(opp_elo >= 1800):
                                d_ClassA += 1
                            elif(opp_elo >= 1600):
                                d_ClassB += 1
                            elif(opp_elo >= 1400):
                                d_ClassC += 1
                            elif(opp_elo >= 1200):
                                d_ClassD += 1
                            else:
                                d_Novice += 1
                        else:
                            win_loss_list.append(-1)
                            if(elo_difference > 0):
                                loss_higher_count += 1
                            elif(elo_difference < 0):
                                loss_lower_count += 1
                            else:
                                loss_even_count += 1
                            
                            if(opp_elo >= 2300):
                                l_Grandmaster += 1
                            elif(opp_elo >= 2000):
                                l_Master += 1
                            elif(opp_elo >= 1800):
                                l_ClassA += 1
                            elif(opp_elo >= 1600):
                                l_ClassB += 1
                            elif(opp_elo >= 1400):
                                l_ClassC += 1
                            elif(opp_elo >= 1200):
                                l_ClassD += 1
                            else:
                                l_Novice += 1

            for i in range(0,len(elo_diff_list)):
                elo = elo_diff_list[i]
                result = win_loss_list[i]
                if(result == 1):
                    # Win
                    if(elo >= 300):
                        w_above_pos_300 += 1
                        continue
                    elif(elo >= 200):
                        w_200_to_299 += 1
                        continue
                    elif(elo >= 100):
                        w_100_to_199 += 1
                        continue
                    elif(elo >= 50):
                        w_50_to_99 += 1
                        continue
                    elif(elo > 0):
                        w_1_to_49 += 1
                        continue
                    elif(elo == 0):
                        w_zero += 1
                        continue
                    elif(elo >= -50):
                        w_neg_1_to_49 += 1
                        continue
                    elif(elo >= -100):
                        w_neg_50_to_99 += 1
                        continue
                    elif(elo >= -200):
                        w_neg_100_to_199 += 1
                        continue
                    elif(elo >= -300):
                        w_neg_200_to_299 += 1
                        continue
                    else:
                        w_below_neg_300 += 1
                        continue



                elif(result == -1):
                    # Loss
                    if(elo >= 300):
                        l_above_pos_300 += 1
                        continue
                    elif(elo >= 200):
                        l_200_to_299 += 1
                        continue
                    elif(elo >= 100):
                        l_100_to_199 += 1
                        continue
                    elif(elo >= 50):
                        l_50_to_99 += 1
                        continue
                    elif(elo > 0):
                        l_1_to_49 += 1
                        continue
                    elif(elo == 0):
                        l_zero += 1
                        continue
                    elif(elo >= -50):
                        l_neg_1_to_49 += 1
                        continue
                    elif(elo >= -100):
                        l_neg_50_to_99 += 1
                        continue
                    elif(elo >= -200):
                        l_neg_100_to_199 += 1
                        continue
                    elif(elo >= -300):
                        l_neg_200_to_299 += 1
                        continue
                    else:
                        l_below_neg_300 += 1
                        continue
                else:
                    # Draw
                    if(elo >= 300):
                        d_above_pos_300 += 1
                        continue
                    elif(elo >= 200):
                        d_200_to_299 += 1
                        continue
                    elif(elo >= 100):
                        d_100_to_199 += 1
                        continue
                    elif(elo >= 50):
                        d_50_to_99 += 1
                        continue
                    elif(elo > 0):
                        d_1_to_49 += 1
                        continue
                    elif(elo == 0):
                        d_zero += 1
                        continue
                    elif(elo >= -50):
                        d_neg_1_to_49 += 1
                        continue
                    elif(elo >= -100):
                        d_neg_50_to_99 += 1
                        continue
                    elif(elo >= -200):
                        d_neg_100_to_199 += 1
                        continue
                    elif(elo >= -300):
                        d_neg_200_to_299 += 1
                        continue
                    else:
                        d_below_neg_300 += 1
                        continue

            # Perspective 1: Progress
            start_elo = elo_list[0]
            end_elo = elo_list[-1]
            max_elo = max(elo_list)
            min_elo = min(elo_list)
            avg_elo = sum(elo_list)/len(elo_list)

            win_stats = [w_below_neg_300, w_neg_200_to_299, w_neg_100_to_199, w_neg_50_to_99, w_neg_1_to_49, w_zero, w_1_to_49, w_50_to_99, w_100_to_199, w_200_to_299, w_above_pos_300]
            loss_stats = [l_below_neg_300, l_neg_200_to_299, l_neg_100_to_199, l_neg_50_to_99, l_neg_1_to_49, l_zero, l_1_to_49, l_50_to_99, l_100_to_199, l_200_to_299, l_above_pos_300]
            draw_stats = [d_below_neg_300, d_neg_200_to_299, d_neg_100_to_199, d_neg_50_to_99, d_neg_1_to_49, d_zero, d_1_to_49, d_50_to_99, d_100_to_199, d_200_to_299, d_above_pos_300]
            
            win_stats_absolute = [w_Grandmaster, w_Master, w_ClassA, w_ClassB, w_ClassC, w_ClassD, w_Novice]
            loss_stats_absolute = [l_Grandmaster, l_Master, l_ClassA, l_ClassB, l_ClassC, l_ClassD, l_Novice]   
            draw_stats_absolute = [d_Grandmaster, d_Master, d_ClassA, d_ClassB, d_ClassC, d_ClassD, d_Novice]

            win_count = sum(win_stats)
            loss_count = sum(loss_stats)
            draw_count = sum(draw_stats)
            if(loss_count > 0):
                win_loss_ratio = win_count/loss_count
            else:
                win_loss_ratio = win_count
            max_win_streak, max_lose_streak = findMaxStreaks(win_loss_list)

            perspective_1 = [start_elo, end_elo, max_elo, min_elo, avg_elo] + win_stats + loss_stats + draw_stats + win_stats_absolute + loss_stats_absolute + draw_stats_absolute + [win_count, loss_count, draw_count, win_loss_ratio, max_win_streak, max_lose_streak]

            # Perspective 2: Strategy
            max_elo_diff = max(elo_diff_list)
            min_elo_diff = min(elo_diff_list)
            avg_elo_diff = sum(elo_diff_list)/len(elo_diff_list)
            opponent_count = len(opponent_list)

            win_higher_count = w_above_pos_300 + w_200_to_299 + w_100_to_199 + w_50_to_99 + w_1_to_49
            win_lower_count = w_below_neg_300 + w_neg_200_to_299 + w_neg_100_to_199 + w_neg_50_to_99 + w_neg_1_to_49
            win_even_count = w_zero
            loss_higher_count = l_above_pos_300 + l_200_to_299 + l_100_to_199 + l_50_to_99 + l_1_to_49
            loss_lower_count = l_below_neg_300 + l_neg_200_to_299 + l_neg_100_to_199 + l_neg_50_to_99 + l_neg_1_to_49
            loss_even_count = l_zero
            draw_higher_count = d_above_pos_300 + d_200_to_299 + d_100_to_199 + d_50_to_99 + d_1_to_49
            draw_lower_count = d_below_neg_300 + d_neg_200_to_299 + d_neg_100_to_199 + d_neg_50_to_99 + d_neg_1_to_49
            draw_even_count = d_zero

            perspective_2 = [max_elo_diff, min_elo_diff, avg_elo_diff, win_higher_count, win_lower_count, win_even_count, loss_higher_count, loss_lower_count, loss_even_count, draw_higher_count, draw_lower_count, draw_even_count, opponent_count]

            # Perspective 3: Activity
            # game_count
            avg_daily_games = sum(daily_game_count)/len(daily_game_count)
            avg_weekly_games = avg_daily_games * 7
            avg_days_between_sessions = averageTimeBetweenSessions(daily_game_count)
            full_day_count = ".".join([str(i) for i in daily_game_count])
            perspective_3 = [game_count, avg_daily_games, avg_weekly_games, avg_days_between_sessions, full_day_count]

            # player_row = [id, player, win_count, loss_count, draw_count, avg_elo, max_elo, min_elo, avg_elo_diff,below_neg_300,neg_200_to_300,neg_100_to_200,neg_50_to_100,zero_to_neg_50,zero,zero_to_50,pos_50_to_100,pos_100_to_200,pos_200_to_300,above_pos_300, max_elo_diff, min_elo_diff, game_count]
            player_row = [id, player] + perspective_1 + perspective_2 + perspective_3
            row_list.append(player_row)
            id += 1

        sys.stdout.write("\r Writing to {0}\n\n".format(nodelist_filename))
        with open(nodelist_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(row_list)

    end = time.time()
    timeFormat(start,end, CreateNodelistSeparate.__name__)
    
# used for testing, ignore.
def test_func():
    json_filename = 'lichess_db_standard_rated_2014-01_nodes.txt' 
    csv_f = 'lichess_db_standard_rated_2014-01.csv'

    node_dict = retrieveNodes(getFilePath(json_filename, 'nodelists'))
    csv_path = getFilePath(csv_f, 'csv')

    edges = pd.read_csv(csv_path)
    edges['w'] = edges['white_id']
    edges['b'] = edges['black_id']

    GraphType = nx.MultiGraph()
    G = nx.from_pandas_edgelist(edges, source='w', target='b', edge_attr=True, create_using=GraphType)
    player = 'Zeffer'
    opponent_list = [g for g in G[player]]

    return G, opponent_list, player