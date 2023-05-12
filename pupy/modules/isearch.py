# -*- encoding: utf-8 -*-

from pupylib.PupyModule import config, PupyModule, PupyArgumentParser
from pupylib.PupyOutput import Table, TruncateToTerm
from argparse import REMAINDER

from datetime import datetime

__class_name__='IndexSearchModule'

# ZOMG Kill me please
def escape(x):
    if "'" in x:
        x = x.replace("'", "")

    return f"'{x}'"

@config(cat='gather', compat='windows')
class IndexSearchModule(PupyModule):
    ''' Use Windows Search Index to search for data '''

    dependencies = [
        'win32com', 'win32api', 'winerror',
        'numbers', 'decimal', 'adodbapi', 'isearch'
    ]

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(prog='isearch', description=cls.__doc__)
        cls.arg_parser.add_argument(
            '-L', '--limit', type=int, help='Limit records (default 50)',
            default=50)
        cls.arg_parser.add_argument('-v', '--verbose', action='store_true',
                                    default=False, help='Show SQL query')
        cls.arg_parser.add_argument('-t', '--text', help='Text to search')
        cls.arg_parser.add_argument('-p', '--path', help='Path to search')
        cls.arg_parser.add_argument('-d', '--directory', help='Directory to limit output')
        cls.arg_parser.add_argument(
            '-R', '--raw', metavar='SELECT ... FROM SYSTEMINDEX ...',
            nargs=REMAINDER, help='RAW SQL Query to search '\
            '(https://docs.microsoft.com/en-us/windows/'\
            'desktop/search/-search-3x-advancedquerysyntax)')

    def run(self, args):
        query = self.client.remote('isearch', 'query')

        request = []
        if args.raw:
            request = args.raw
        else:
            request.append(
                f'SELECT TOP {args.limit} System.ItemUrl, System.Size, System.DateModified FROM SYSTEMINDEX'
            )
            where = []
            if args.text:
                where.append(f'FREETEXT({escape(args.text)})')
            if args.directory:
                where.append(f"SCOPE={escape(f'file:{args.directory}')}")
            if args.path:
                where.append(f'CONTAINS(System.FileName, {escape(args.path)})')

            if where:
                request.append('WHERE')
                request.append('AND'.join(where))

            request.append('ORDER BY System.DateModified DESC')

        if not request:
            self.error('You should specify request')
            return

        text = ' '.join(request)

        if args.verbose:
            self.info(f'QUERY: {text}')

        idx, cidx, data, error = query(text, args.limit)
        if error:
            self.error(error)
        elif not data:
            self.warning('No data found')
        else:
            objects = []
            header = []
            legend = True

            if args.raw:
                legend = False
                objects.extend(
                    {str(idx): v for idx, v in enumerate(record)}
                    for record in data
                )
                header = [
                    str(x) for x in xrange(cidx+1)
                ]
            else:
                header = ['File', 'Size', 'Modified']
                objects.extend(
                    {
                        'File': record[0][5:]
                        if record[0].startswith('file:')
                        else record[0],
                        'Size': record[1],
                        'Modified': datetime.fromtimestamp(record[2]),
                    }
                    for record in data
                )
            self.log(TruncateToTerm(Table(objects, header, legend=legend)))
