#!/usr/bin/env python
# coding: utf-8
"""Script for building Qt from source"""

from __future__ import print_function
import glob
import os
import platform
import shutil
import subprocess
import sys
import tools
from tools import vctools

_ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(_ROOT_DIR, 'thirdparty'))
import icu
import openssl


def _print_message(text):
    print(text)
    sys.stdout.flush()


def _print_warning(text):
    print('Warning: {}'.format(text), file=sys.stderr)
    sys.stderr.flush()


QT_SOURCE = os.path.join(_ROOT_DIR, 'qt')

def _build_qt(target, install_dir, env, config_options=None,
              include_dirs=None, lib_dirs=None, libs=None):
    """Build and install Qt
    Args:
        target (str): Target platform
        install_dir (str): Install directory path
        env (set(str:str)): Environment variables for building Qt and Qt and
                            third party libraries
        config_options (list(str)): Additional options for Qt configure script
        include_dirs (list(str)): Path to directories with include files from
                                  third party libraries
        lib_dirs (list(str)): Path to directories with static library files from
                              third party libraries
        libs (list(str)): Static library names for link with Qt
    """

    # directories
    install_dir = os.path.abspath(install_dir)

    # clean config
    if os.path.exists(os.path.join(QT_SOURCE, 'Makefile')):
        print('Warning: Qt already configured. It don\'t reconfigure.', )

    # configure
    config_cmd = [
        './configure' if os.name == 'posix' else 'configure',
        '-prefix', '"{}"'.format(install_dir),
        '-platform', target,
        '-opensource',
        '-confirm-license',
        '-nomake', 'examples',
        '-nomake', 'tests',
    ]

    if config_options:
        config_cmd += config_options

    if include_dirs:
        for include_dir in include_dirs:
            config_cmd += ['-I', '"{}"'.format(include_dir)]
    if lib_dirs:
        for lib_dir in lib_dirs:
            config_cmd += ['-L', '"{}"'.format(lib_dir)]
    if libs:
        for lib in libs:
            config_cmd += ['-l', lib]
    subprocess.check_call(' '.join(config_cmd), shell=True, env=env,
                          cwd=QT_SOURCE)

    # build
    tools.jom.make(env=env, cwd=QT_SOURCE)
    tools.jom.make(['install'], env=env, cwd=QT_SOURCE)

    # qt.conf
    shutil.copy(os.path.join(_ROOT_DIR, 'qt.conf'),
                os.path.join(install_dir, 'bin'))


def build_all(args):
    """Analyzes the command-line options and build Qt with third party
    libraries"""

    def _add_to_path_variable(env, value):
        if not value:
            return

        if 'PATH' in env:
            env['PATH'] = value + os.pathsep + env['PATH']
        else:
            env['PATH'] = value

    def _clean(directory):
        clean_cmd = ['git', 'clean', '-dxf']
        subprocess.check_call(clean_cmd, cwd=directory)
        foreach_cmd = ['git', 'submodule', 'foreach', '--recursive']
        subprocess.check_call(foreach_cmd + clean_cmd, cwd=directory)

    # environment
    if args.target == 'win32-msvc':
        vc_tools = vctools.VCTools(args.vs_version, args.platform)
        env = vc_tools.environ.copy()
        # workaround for Visual C++ Build Tools
        if env.get('VISUALSTUDIOVERSION') is None:
            env['VISUALSTUDIOVERSION'] = \
                '{}.0'.format(vc_tools.VERSIONS[vc_tools.version_name])
        env['GYP_MSVS_VERSION'] = vc_tools.version_name
        env['GYP_MSVS_OVERRIDE_PATH'] = os.path.normpath(
            os.path.join(vc_tools.get_vc_install_dir(), '..', 'Common7', 'IDE'))
        env['CL'] = '/wd4334'
        target = 'win32-msvc' + vc_tools.version_name
        platform_dir = target + '_' + args.platform
    elif args.target == 'linux-gcc':
        env = os.environ.copy()
        target = 'linux-g++-' + \
            ('64' if platform.architecture()[0] == '64bit' else '32')
        platform_dir = target
    elif args.target == 'macx-clang':
        env = os.environ.copy()
        target = 'macx-clang' + ('-32' if args.platform == 'x86' else '')
        platform_dir = target
    else:
        raise AttributeError('Unsupported target ' + args.target)

    # directories
    build_dir = os.path.join(_ROOT_DIR, 'build', platform_dir)

    if args.install is not None:
        install_dir = args.install
    else:
        install_dir = os.path.join(_ROOT_DIR, 'install', platform_dir)

    qt_include_dirs = []
    qt_lib_dirs = []
    qt_static_libs = []
    qt_dynamic_libs = []

    # config
    qt_config_options = args.config_option if args.config_option else []

    # clean
    if args.rebuild:
        _print_message('Cleaning...\n')
        for path in [build_dir, install_dir]:
            if os.path.exists(path):
                shutil.rmtree(path)
        _clean(QT_SOURCE)

    # build icu
    if not args.skip_icu_build:
        _print_message('Building ICU...\n')
        icu_install_dir = os.path.join(build_dir, 'icu',)
        icu_builder = icu.Builder(target, icu_install_dir)

        if args.rebuild:
            _clean(icu_builder.SOURCE_DIR)

        icu_builder.build(env)

        qt_include_dirs += [icu_builder.include_dir]
        qt_lib_dirs += [icu_builder.lib_dir]
        qt_static_libs += icu_builder.static_libs

        if icu_builder.bin_dir:
            qt_dynamic_libs += [os.path.join(icu_builder.bin_dir, name)
                                for name in icu_builder.dynamic_libs]
            _add_to_path_variable(env, icu_builder.bin_dir)

        qt_config_options += ['-icu']

    # build openssl
    if not args.skip_openssl_build:
        _print_message('Building OpenSSL...\n')
        openssl_install_dir = os.path.join(build_dir, 'openssl')
        openssl_builder = openssl.Builder(target, openssl_install_dir)

        if args.rebuild:
            _clean(openssl_builder.SOURCE_DIR)

        openssl_builder.build(env)

        qt_include_dirs += [openssl_builder.include_dir]
        qt_lib_dirs += [openssl_builder.lib_dir]
        qt_static_libs += openssl_builder.static_libs

        if openssl_builder.bin_dir:
            qt_dynamic_libs += [os.path.join(openssl_builder.bin_dir, name)
                                for name in openssl_builder.dynamic_libs]
            _add_to_path_variable(env, openssl_builder.bin_dir)

        qt_config_options += ['-openssl-linked']

    # build qt
    _print_message('Building Qt...\n')
    _build_qt(target, install_dir, env, qt_config_options, qt_include_dirs,
              qt_lib_dirs, qt_static_libs)

    # copy runtime binary files
    qt_bin_dir = os.path.join(install_dir, 'bin')
    for mask in qt_dynamic_libs:
        for path in glob.glob(mask):
            shutil.copy(path, qt_bin_dir)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(add_help=True,
                                     description='Qt build script.')
    parser.add_argument('--install', '-i', help='Install directory')
    parser.add_argument('--rebuild', '-r', action='store_true',
                        help='Rebuild (warning this option remove all'
                             'untracked files from submodules')
    parser.add_argument('--config-option', '-c', action='append',
                        help='Additional option for Qt configure script')
    parser.add_argument('--skip-icu-build', action='store_true',
                        help='Skip build ICU library')
    parser.add_argument('--skip-openssl-build', action='store_true',
                        help='Skip build OpenSSL library')
    subparsers = parser.add_subparsers(dest='target', help='Target platform')

    parser_win32_msvc = subparsers.add_parser('win32-msvc',
                                              help='Build for Windows with '
                                                   'Microsoft Visual C++')
    parser_win32_msvc.add_argument('vs_version', nargs='?',
                                   choices=vctools.VCTools.VERSIONS.keys(),
                                   help='Visual Studio version')
    parser_win32_msvc.add_argument('--platform', '-p', default='x86',
                                   choices=['x86', 'amd64'],
                                   help='Platform architecture')

    parser_linux_gcc = subparsers.add_parser('linux-gcc',
                                             help='Build for Linux with GCC')

    parser_macx_clang = subparsers.add_parser('macx-clang',
                                              help='Build for Mac OS X with '
                                                   'Clang')
    parser_macx_clang.add_argument('--platform', '-p', default='amd64',
                                   choices=['x86', 'amd64'],
                                   help='Platform architecture')

    build_all(parser.parse_args())
