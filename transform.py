# Transform file between formats

import os
import sys
import csv
csv.field_size_limit(sys.maxint)

try:
    import simplejson as json
except ImportError:
    import json
try:
    import xml.etree.ElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree


class Transform:
    """Base Tranform module
    """
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        """Read contents of file and return an iterator of lists for each record
        """
        raise NotImplementedError()

    def write(self, data):
        """Write contents of iterator to file
        """
        raise NotImplementedError()


class CsvTransform(Transform):
    def delimiter(self):
        return ','

    def read(self):
        return csv.reader(open(self.filename), delimiter=self.delimiter())

    def clean(self, s):
        try:
            return s.encode('utf-8', 'ignore') if s else s
        except Exception, e:
            print 'Encode error:', e
            return s

    def write(self, records):
        writer = csv.writer(open(self.filename, 'w'), delimiter=self.delimiter())
        for record in records:
            writer.writerow([self.clean(col) for col in record])


class TsvTransform(CsvTransform):
    def delimiter(self):
        return '\t'


class JsonTransform(Transform):
    def read(self):
        header = None
        for data in json.loads(open(self.filename).read()):
            if not header:
                # XXX lose of track of order in dict
                header = data.keys()
                yield header
            yield [data.get(col) for col in header]
        raise StopIteration()

    def write(self, filename):
        header = None
        # XXX avoid storing in memory
        for record in records:
            if header:
                output.append(dict([(field, record[i]) for i, field in enumerate(header)]))
            else:
                header = record
        open(self.filename, 'w').write(json.dumps(output))


class XmlTransform(Transform):
    def read(self):
        # iteratively parse the XML file so not kept in memory
        context = etree.iterparse(self.filename, events=('start', 'end'))
        # keep track of the root element to can clear entire tree when processed record
        _, root = context.next()
        # this is the record element
        _, record = context.next()
        
        header = []
        d = {}
        i = 0
        for event, e in context:
            if event == 'end':
                # finished processing a tag
                if e.tag == record.tag:
                    # finished processing a record
                    if i == 0:
                        # first record to send header
                        yield header
                    i += 1
                    if i % 100000 == 0:
                        print i
                    yield [d.get(col) for col in header]
                    d = {}
                    root.clear() # clear from memory
                else:
                    # save value of tag
                    d[e.tag] = e.text
                    if e.tag not in header:
                        header.append(e.tag)
        raise StopIteration()

    def write(self, records):
        header = None
        output = []
        fp = open(self.filename, 'w')
        fp.write('<?xml version="1.0" ?>\n')
        fp.write('<records>\n')
        for record in records:
            if header:
                fp.write('<record>')
                for k, v in zip(header, record):
                    fp.write('<%s>%s</%s>' % (k, v, k))
                fp.write('</record>\n')
            else:
                header = record
        fp.write('</records>\n')
        open(self.filename, 'w').write(json.dumps(output))


class XlsTransform(Transform):
    def __init__(self, filename):
        import pyExcelerator
        global pyExcelerator
        Transform.__init__(self, filename)
    
    def read(self):
        book = pyExcelerator.parse_xls(self.filename)
        # a dictionary of value at each coordinate
        parsed_dictionary = book[0][1]
        # find maximum ID's of coordinates
        rows, cols = zip(*parsed_dictionary.keys())
        num_rows = max(rows) + 1
        num_cols = max(cols) + 1
        for row in range(num_rows):
            record = [parsed_dictionary.get((row, col)) for col in range(num_cols)]
            yield record
        raise StopIteration()

    def write(self, records):
        wb = pyExcelerator.Workbook()
        ws0 = wb.add_sheet('0')
        for x, record in enumerate(records):
            for y, v in enumerate(record):
                # write value to a specific coordinate
                try:
                    ws0.write(x, y, v)
                except Exception, e:
                    print 'Failed to write', v
                    print e
        wb.save(self.filename)


def get_transform(filename):
    """Return transform that supports this extension
    """
    ext = filename.rpartition('.')[-1].lower()
    if ext == 'csv':
        transform = CsvTransform(filename)
    elif ext == 'tsv':
        transform = TsvTransform(filename)
    elif ext == 'json':
        transform = JsonTransform(filename)
    elif ext == 'xml':
        transform = XmlTransform(filename)
    elif ext == 'xls':
        transform = XlsTransform(filename)
    else:
        raise Exception('Unsupported filename extension: ' + filename)
    return transform


def usage():
    print 'Usage: %s <input file> <output file>' % sys.argv[0]
    sys.exit()


def main(input_file, output_file):
    if not os.path.exists(input_file):
        raise Exception('Input file does not exist: ' + input_file)
    if input_file == output_file:
        raise Exception('Input file can not be the same as output file')

    input_transform = get_transform(input_file)
    output_transform = get_transform(output_file)
    print 'Reading', input_file
    records = input_transform.read()
    print 'Writing', output_file
    output_transform.write(records)


if __name__ == '__main__':
    try:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    except IndexError:
        usage()
    else:
        main(input_file, output_file)
