# -*- coding: utf-8 -*-

from pupylib.PupyModule import config, PupyModule, PupyArgumentParser

__class_name__="GetDomain"

@config(compat="windows", cat="admin")
class GetDomain(PupyModule):
    """ Get primary domain controller """

    dependencies = ['pupwinutils.getdomain']

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(prog="getdomain", description=cls.__doc__)

    def run(self, args):
        get_domain_controller = self.client.remote('pupwinutils.getdomain', 'get_domain_controller')

        if primary_domain := get_domain_controller():
            self.success(f"Primary domain controller: {primary_domain}")
        else:
            self.error("This host is not part of a domain.")
