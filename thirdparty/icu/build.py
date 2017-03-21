# coding: utf-8
"""Module fot buid ICU4C"""

import os
import shutil
import subprocess

_ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


class Builder:
    """ICU4C builder"""

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

        if target.startswith('win32-msvc'):
            self.dynamic_libs = ['icudt*.dll', 'icuin*.dll', 'icuuc*.dll']
            self.static_libs = []
            self._builder = self._build_win32
        elif target.startswith('linux-g++'):
            self.dynamic_libs = []
            self.static_libs = ['dl']
            self._builder = self._build_linux
        elif target.startswith('macx-clang'):
            self.dynamic_libs = []
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

    def _build_win32(self, env):
        # build
        project_dir = os.path.join(self.SOURCE_DIR, 'source', 'allinone')
        platform = env.get('PLATFORM', 'X86').upper()
        project_platform = {'X86': 'Win32', 'X64': 'x64'}[platform]
        cmd = ['msbuild', 'allinone.sln', '/m',
               '/p:Configuration=Release',
               '/p:Platform={}'.format(project_platform),
               '/p:PlatformToolset=v{}'.format(env['PLATFORM_TOOLSET']),
               '/p:TargetFrameworkMoniker=".NETFramework,Version=v3.5"',
              ]
        ucrt_version = env.get('UCRTVERSION')
        if ucrt_version:
            cmd.append('/p:WindowsTargetPlatformVersion={}'.format(ucrt_version))
        subprocess.check_call(' '.join(cmd), shell=True, env=env,
                              cwd=project_dir)

        # install
        suffix = {'X86': '', 'X64': '64'}[platform]
        for from_subdir, to_subdir in [('bin' + suffix, 'bin'),
                                       ('include', 'include'),
                                       ('lib' + suffix, 'lib')]:
            target_dir = os.path.join(self.install_dir, to_subdir)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.copytree(os.path.join(self.SOURCE_DIR, from_subdir), target_dir)

    def _build_linux(self, env):
        local_env = env.copy()
        local_env['CFLAGS'] = '-fPIC ' + local_env.get('CFLAGS', '')
        local_env['CXXFLAGS'] = '-fPIC ' + local_env.get('CXXFLAGS', '')
        self._build_posix('Linux/gcc', local_env)

    def _build_macx(self, env):
        self._build_posix('MacOSX', env)

    def _build_posix(self, target, env):
        source_dir = os.path.join(self.SOURCE_DIR, 'source')

        # configure
        cmd = './runConfigureICU {} --prefix="{}" --enable-shared=no ' \
              '--enable-static=yes'.format(target, self.install_dir),
        subprocess.check_call(cmd, shell=True, env=env, cwd=source_dir)

        # build
        subprocess.check_call(['make'], env=env, cwd=source_dir)
        subprocess.check_call(['make', 'install'], env=env, cwd=source_dir)
