#! /usr/bin/env python3

# -*- coding: utf8 -*-

import argparse
import shutil
from tqdm import tqdm
from subprocess import check_output, run

parser = argparse.ArgumentParser(description='Update every entries found in cask folder.')
parser.add_argument('--pretend', dest='pretend', action='store_true',
                    help='Pretend to take action.')
parser.add_argument('--forceuninstall', dest='forceuninstall', action='store_true',
                    help='Force uninstall before install.')
parser.add_argument('--checkfonts', dest='checkfonts', action='store_true',
                    help='Enable check of font casks.')
parser.add_argument('--checklatest', dest='checklatest', action='store_true',
                    help='Enable update of casks that use latest as version.')
parser.set_defaults(pretend=False, forceuninstall=False, checkfonts=False, checklatest=False)
args = parser.parse_args()

brew_bin = 'brew'
if not shutil.which(brew_bin):
    raise FileExistsError(brew_bin + ' not exists')

update_command = [
    brew_bin,
    'update'
]

run(update_command)

list_command = [
    brew_bin,
    'cask',
    'list'
]

list_installed = str.split(check_output(list_command).decode(), '\n')
list_installed = [i for i in list_installed if i is not '']
if not args.checkfonts:
    list_installed = [i for i in list_installed if not i.startswith('font-')]
if list_installed:
    updated_count = 0
    pbar = tqdm(list_installed)
    for cask in pbar:
        pbar.set_description(cask)
        info_command = [
            brew_bin,
            'cask',
            'info',
            cask
        ]
        try:
            install_status = str.splitlines(check_output(info_command).decode())
            version = str.strip(str.split(install_status[0], ':')[1])
            is_version_installed = False
            for line in install_status:
                if not line.startswith(cask) and cask in line and version in line:
                    is_version_installed = True
            if version == 'latest' and args.checklatest:
                is_version_installed = False

            if not is_version_installed:
                install_command = [
                    brew_bin,
                    'cask',
                    'install',
                    '--force',
                    cask
                ]
                if args.pretend:
                    print(' '.join(install_command))
                else:
                    if args.forceuninstall:
                        uninstall_command = [
                            brew_bin,
                            'cask',
                            'uninstall',
                            '--force',
                            cask
                        ]
                        run(uninstall_command)
                    run(install_command)
                updated_count += 1
        except:
            print(cask + ' installation is broken')

    print(str(updated_count) + ' cask(s) updated')
else:
    print('0 cask installed')
