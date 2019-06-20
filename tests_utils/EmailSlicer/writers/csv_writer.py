import csv


def write(file_name, headers, data, return_data, parameters):
    with open('output_files/' + file_name + '.csv', 'w+', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)#,dialect='excel')
        writer.writerow(headers)
        for single_data in data:
            writer.writerow(single_data)
            if single_data[1] > 1:
                return_data.append({parameters[0]: single_data[0], parameters[1]: single_data[1]})
        outfile.close()
    return return_data
