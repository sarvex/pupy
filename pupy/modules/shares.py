# -*- coding: utf-8 -*-

from pupylib.PupyOutput import Table
from pupylib.PupyModule import config, PupyModule, PupyArgumentParser
from netaddr import IPNetwork

__class_name__="Shares"

@config(category="admin", compat=["windows", "linux"])
class Shares(PupyModule):
    """ List local and remote shared folder and permission """

    dependencies = {
        'windows': [
            'win32api', 'win32com', 'pythoncom',
            'winerror', 'wmi', 'pupwinutils.drives',
        ],
        'all': [
            'impacket', 'calendar', 'pupyutils.share_enum'
        ]
    }

    @classmethod
    def init_argparse(cls):
        example = 'Examples:\n' + '>> run shares local\n'
        example += '>> run shares remote -u john -p password1 -d DOMAIN -t 192.168.0.1\n'
        example += '>> run shares remote -u john -H \'aad3b435b51404eeaad3b435b51404ee:da76f2c4c96028b7a6111aef4a50a94d\' -t 192.168.0.1\n'

        cls.arg_parser = PupyArgumentParser(prog="shares", description=cls.__doc__, epilog=example)
        subparsers = cls.arg_parser.add_subparsers(title='Enumerate shared folders')

        local = subparsers.add_parser('local', help='Retrieve local shared folders')
        local.set_defaults(local="list_shared_folders")

        remote = subparsers.add_parser('remote', help='Retrieve remote shared folders and permission')
        remote.add_argument("-u", metavar="USERNAME", dest='user', default='', help="Username, if omitted null session assumed")
        remote.add_argument("-p", metavar="PASSWORD", dest='passwd', default='', help="Password")
        remote.add_argument("-H", metavar="HASH", dest='hash', default='', help='NTLM hash')
        remote.add_argument("-d", metavar="DOMAIN", dest='domain', default="WORKGROUP", help="Domain name (default WORKGROUP)")
        remote.add_argument("-P", dest='port', type=int, choices={139, 445}, default=445, help="SMB port (default 445)")
        remote.add_argument("-t", dest='target', type=str, help="The target range or CIDR identifier")


    def run(self, args):

        # Retrieve local shared folders
        try:
            if args.local:
                if self.client.is_windows():
                    shared_folders = self.client.remote('pupwinutils.drives', 'shared_folders')

                    if folders := shared_folders():
                        self.log(Table([{
                            'Name': share_name,
                            'Path': share_path
                        } for share_name, share_path in folders], ['Name', 'Path']))

                    else:
                        return

                else:
                    self.warning('this module works only for windows. Try using: run shares remote -t 127.0.0.1')
                return
        except:
            pass

        # Retrieve remote shared folders
        if not args.target:
            self.error("target (-t) parameter must be specify")
            return

        hosts = IPNetwork(args.target) if "/" in args.target else [args.target]
        connect = self.client.remote('pupyutils.share_enum', 'connect')

        for host in hosts:
            result = connect(
                str(host), args.port, args.user,
                args.passwd, args.hash, args.domain)

            if 'error' in result:
                if 'os' in result:
                    self.error(
                        f"{host}:{args.port} OS={result['os']} NAME={result['name']}: {result['error']}"
                    )
                else:
                    self.error(f"{host}:{args.port}: {result['error']}")
            else:
                self.success(
                    f"{host}:{args.port} OS=[{result['os']}] NAME=[{result['name']}] AUTH={result['auth']}"
                )
                shares = [{
                    'SHARE': x[0],
                    'ACCESS': x[1]
                } for x in result['shares']]

                self.table(shares, ['SHARE', 'ACCESS'])
