import csv

"""
[
    'row_id', 'sender', 'receiver', 'count', 
    'rou_id', 'subject', 'location', 'date'
]
"""
def write(output_directory, file_name, headers, data, return_data, return_data_counts, parameters, flag=False):
    with open(output_directory + '/' + file_name + '.csv', 'w+', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)#,dialect='excel')
        writer.writerow(headers)
        if flag:
            for single_data in data:
                writer.writerow(single_data)
                return_data.append({parameters[0]: single_data[0], parameters[1]: single_data[1]})
            
            outfile.close()
            return return_data
        else:
            if len(return_data_counts) == 0:
                #rowID = 0
                #currUser = 0
                index = 0
                for single_data in data:
                    index += 1
                    writer.writerow(single_data)
                    #if currUser == 0:
                    #    currUser = single_data[2]
                    #    rowID += 1
                    return_data.append({parameters[0]: index, parameters[1]: single_data[0], parameters[2]: single_data[1], parameters[3]: single_data[2]})
                    return_data_counts.append(single_data[2])
                    #currUser -= 1
                outfile.close()
                return return_data, return_data_counts
            else:
                rowID = 0
                currUser = 0
                index = -1
                for single_data in data:
                    writer.writerow(single_data)
                    if currUser == 0:
                        index += 1
                        currUser = return_data_counts[index]
                        rowID += 1
                    return_data.append({parameters[0]: rowID, parameters[1]: single_data[0], parameters[2]: single_data[1], parameters[3]: get_date_time(single_data[2])})
                    currUser -= 1
                outfile.close()
                return return_data

"""
[
    'row_id', 'sender', 'receiver', 'count', 
    'rou_id', 'subject', 'location', 'date'
]
"""

import datetime

def get_date_time(date_epoch):
    try:
        date_time = datetime.datetime.fromtimestamp(
            date_epoch).strftime('%Y-%m-%d %H:%M:%S')  # .strftime('%c')
    except:
        date_time = 'NULL'
    finally:
        return date_time
