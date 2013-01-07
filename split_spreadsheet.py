import os
import csv
import sys
import optparse


def spreadsheet_length(input_filename):
    """Number of rows for this spreadsheet
    """
    i = 0
    for row in csv.reader(open(input_filename)):
        i += 1
    if i > 0:
        # don't count header row
        i -= 1
    return i


def split_spreadsheet(input_filename, max_rows):
    """Split spreadsheet into smaller spreadsheets of maximum max_rows rows
    Returns the list of filenames
    """
    # need to split large spreadsheet
    num_rows = spreadsheet_length(input_filename)
    print 'num rows:', num_rows
    output_filenames = []
    if num_rows > max_rows:
        header = None
        row_i = 0 # row in complete input spreadsheet
        spreadsheet_i = 0 # row in current spreadsheet
        for row in csv.reader(open(input_filename)):
            if header:
                if spreadsheet_i == 0:
                    basename, ext = os.path.splitext(input_filename)
                    output_filename = '%s.%d-%d%s' % (basename, row_i + 1, min(row_i + max_rows, num_rows), ext)
                    print 'Writing to', output_filename
                    output_filenames.append(output_filename)
                    writer = csv.writer(open(output_filename, 'w'))
                    writer.writerow(header)
                writer.writerow(row)
                spreadsheet_i += 1
                row_i += 1
                if spreadsheet_i == max_rows:
                    spreadsheet_i = 0
            else:
                header = row
    return output_filenames


if __name__ == '__main__':
    parser = optparse.OptionParser(usage='%prog [options] spreadsheet-1 [spreadsheet-2 ...]')
    parser.add_option('-m', '--max-rows', dest='max_rows', type='int', help='The maximum number of rows per spreadsheet', default=50000)
    options, args = parser.parse_args()
    if not args:
        parser.error('What spreadsheet to split?')
    
    for filename in args:
        print 'splitting', filename
        split_spreadsheet(filename, options.max_rows)
