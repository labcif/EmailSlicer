def write(output_directory, date_list):
    """
    The dateReport function writes date information in a TSV report. No input args as the filename
    is static within the HTML dashboard
    :return: None
    """
    with open(output_directory + '/heatmap.tsv', 'w+', encoding='utf-8') as outfile:
        outfile.write("day\thour\tvalue\n")
        for date, hours_list in enumerate(date_list):
            for hour, count in hours_list.items():
                to_write = str(date+1) + "\t" + str(hour) + "\t" + str(count) + "\n"
                outfile.write(to_write)
            outfile.flush()
        outfile.close()