# coding: utf-8
"""Module fot buid OpenSSL"""

import os
import subprocess

_ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


class Builder:
    """OpenSSL builder"""

    SOURCE_DIR = os.path.join(_ROOT_DIR, 'src')

    def __init__(self, target, install_dir):
        """
        Args:
            target (str): Target platform
            install_dir (str): Install directory path
        """
        self.install_dir = os.path.abspath(install_dir)
        self.bin_dir = os.path.join(self.install_dir, 'bin')
        self.include_dir = os.path.join(self.install_dir, 'include')
        self.lib_dir = os.path.join(self.install_dir, 'lib')

        self.dynamic_libs = []

        if target.startswith('win32-msvc'):
            self.static_libs = ['ssleay32', 'libeay32', 'advapi32', 'crypt32',
                                'gdi32', 'user32', 'ws2_32']
            self._builder = self._build_win32
        elif target.startswith('linux-g++'):
            self.static_libs = ['ssl', 'crypto', 'dl']
            self._builder = self._build_linux
        elif target.startswith('macx-clang'):
            self.static_libs = []
            self._builder = self._build_macx
        else:
            raise ValueError('Invalid platform {}'.format(target))

    def build(self, env):
        """Build OpenSSL
        Args:
            env (set(str:str)): Environment variables for building OpenSSL
        """
        if not os.path.exists(self.install_dir):
            os.makedirs(self.install_dir)

        self._builder(env)

    def _build_win32(self, env, shared=False):
        # configure
        platform = env.get('PLATFORM', 'X86').upper()
        config = {'X86': 'VC-WIN32', 'X64': 'VC-WIN64A'}[platform]
        subprocess.check_call(['perl', 'Configure', config, 'no-asm',
                               '--prefix={}'.format(self.install_dir)],
                              env=env, cwd=self.SOURCE_DIR)
        script = {'X86': 'do_ms', 'X64': 'do_win64a'}[platform]
        subprocess.check_call(os.path.join('ms', script), shell=True, env=env,
                              cwd=self.SOURCE_DIR)

        # build
        makefile = 'ntdll.mak' if shared else 'nt.mak'
        makefile_path = os.path.join('ms', makefile)
        subprocess.check_call(['nmake', '-f', makefile_path],
                              shell=True, env=env, cwd=self.SOURCE_DIR)
        subprocess.check_call(['nmake', '-f', makefile_path, 'test'],
                              shell=True, env=env, cwd=self.SOURCE_DIR)
        subprocess.check_call(['nmake', '-f', makefile_path, 'install'],
                              shell=True, env=env, cwd=self.SOURCE_DIR)


    def _build_linux(self, env):
        # configure
        cmd = './config --prefix="{}" -fPIC'.format(self.install_dir)
        subprocess.check_call(cmd, shell=True, env=env, cwd=self.SOURCE_DIR)

        # build
        subprocess.check_call(['make'], env=env, cwd=self.SOURCE_DIR)
        subprocess.check_call(['make', 'test'], env=env, cwd=self.SOURCE_DIR)
        subprocess.check_call(['make', 'install'], env=env, cwd=self.SOURCE_DIR)


    def _build_macx(self, env, amd64=True):
        # configure
        target = 'darwin64-x86_64-cc' if amd64 else 'darwin64-i386-cc'
        cmd = './Configure {} --prefix="{}"'.format(target, self.install_dir)
        subprocess.check_call(cmd, shell=True, env=env, cwd=self.SOURCE_DIR)

        # build
        subprocess.check_call(['make'], env=env, cwd=self.SOURCE_DIR)
        subprocess.check_call(['make', 'test'], env=env, cwd=self.SOURCE_DIR)
        subprocess.check_call(['make', 'install'], env=env, cwd=self.SOURCE_DIR)
