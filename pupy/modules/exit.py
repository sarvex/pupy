# -*- coding: utf-8 -*-

from pupylib.PupyModule import PupyModule, PupyArgumentParser
from pupylib.PupyErrors import PupyModuleError

__class_name__="ExitModule"

class ExitModule(PupyModule):
    """ exit the client on the other side """
    is_module=False

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(prog="exit", description=cls.__doc__)
        cls.arg_parser.add_argument('--yes', action="store_true", help='exit confirmation')

    def run(self, args):
        if not args.yes:
            raise PupyModuleError('Please conform with --yes to perform this action.')
        try:
            self.client.conn.exit()
        except Exception:
            pass
