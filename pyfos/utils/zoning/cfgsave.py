#!/usr/bin/env python3

# Copyright 2017 Brocade Communications Systems, Inc.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may also obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

:mod:`cfgsave` - PyFOS util for specific Zoning use case.
***********************************************************************************
The :mod:`cfgsave` provides for specific Zoning use case.

This module is a standalone script and API that can be used to save
pending changes to Zone DB.

* inputs:
    * -L=<login>: Login ID. If not provided, interactive
        prompt will request one.
    * -P=<password>: Password. If not provided, interactive
        prompt will request one.
    * -i=<IP address>: IP address
    * -f=<VFID>: VFID or -1 if VF is disabled. If unspecified,
        VFID of 128 is assumed.

* outputs:
    * Python dictionary content with RESTCONF response data

"""

import pyfos.pyfos_auth as pyfos_auth
import pyfos.pyfos_zone as pyfos_zone
import pyfos.pyfos_util as pyfos_util
import sys
import pyfos.utils.brcd_util as brcd_util

isHttps = "0"


def cfgsave(session, checksum):
    """Save pending Zone DB transaction

    Example usage of the method::

        result = cfgsave(session, checksum)

    :param session: session returned by login
    :param checksum: database checksum from effective configuration
    :rtype: dictionary of return status matching rest response

    *use cases*

        1. save pending Zone DB changes

    """

    new_effective = pyfos_zone.effective_configuration()
    new_effective.set_cfg_action(pyfos_zone.CFG_ACTION_SAVE)
    new_effective.set_checksum(checksum)
    result = new_effective.patch(session)
    return result


def usage():
    print("usage:")
    print('cfgsave.py -i <ipaddr>')


def exit_handler():
    global session
    if session is not None:
        pyfos_auth.logout(session)


def main(argv):
    inputs = brcd_util.generic_input(argv, usage)

    session = pyfos_auth.login(inputs["login"], inputs["password"],
                               inputs["ipaddr"], isHttps)
    if pyfos_auth.is_failed_login(session):
        print("login failed because",
              session.get(pyfos_auth.CREDENTIAL_KEY)
              [pyfos_auth.LOGIN_ERROR_KEY])
        usage()
        sys.exit()

    brcd_util.exit_register(session)

    vfid = None
    if 'vfid' in inputs:
        vfid = inputs['vfid']

    if vfid is not None:
        pyfos_auth.vfid_set(session, vfid)

    current_effective = pyfos_zone.effective_configuration.get(session)
    result = cfgsave(current_effective.peek_checksum())
    pyfos_util.response_print(result)

    pyfos_auth.logout(session)


if __name__ == "__main__":
    main(sys.argv)
