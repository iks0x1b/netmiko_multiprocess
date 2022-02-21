import json
import getpass
import locale
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from netmiko import ConnectHandler


LOCALE = locale.getdefaultlocale()


def load_json(jsonfile):
    """
    I get tired of rewriting this common code block
    it loads a json
    """
    with open(jsonfile, "r", encoding=LOCALE[1]) as jsoninput:
        jsondata = json.load(jsoninput)
    return jsondata


def ssh_handler(target, command):
    """
    wrap ConnectHandler in function with exception handling
    """
    nm_handle = ConnectHandler(**target)
    try:
        result = nm_handle.send_command(command)
    except:  # pylint: disable=bare-except
        print("Its broken: ")
    return result


def process_handler(targets, command, concurrency):
    """
    leverage concurrent.futures ProcessPoolExecutor to send concurrent ssh sessions to devices
    """
    data = {}
    with ProcessPoolExecutor(max_workers=(int(concurrency))) as executor:
        result = executor.map(ssh_handler, targets, repeat(command))
        for device, output in zip(targets, result):
            data[device["ip"]] = output
    return data


def main():
    """
    call functions and do the thing you can tell by the way that it is
    """
    auth = {}
    auth["username"] = input("Username: ")
    auth["password"] = getpass.getpass()
    auth["secret"] = auth["password"]

    devices = load_json("hosts.json")
    for device in devices:
        device.update(auth)

    cf_scrape = process_handler(devices, "show interfaces", 2)
    print(json.dumps(cf_scrape, indent=4))


if __name__ == "__main__":
    main()
