#
# --------------------------------------------------------------------------------------------------
#     __  ______  ____  __    ________________
#    / / / / __ \/ __ \/ /   /  _/_  __/ ____/
#   / /_/ / / / / /_/ / /    / /  / / / __/
#  / __  / /_/ / ____/ /____/ /  / / / /___
# /_/ /_/\____/_/   /_____/___/ /_/ /_____/   (v1.0 . Achilles)
#
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# --------------------------------------------------------------------------------------------------
"""
Stub for LLVM I/O interface
"""
import os
import subprocess
import distutils.dir_util

import hoplitebase

class LLVM(hoplitebase.HopliteBase):
    """docstring for LLVM"""
    def __init__(self, parent=None, work_path=None, log=None):
        super(LLVM, self).__init__('llvm', parent, work_path, log)
        self._llvm_wp = os.path.join(self._work_path, 'llvm')

    def pre(self):
        """ The pre function in the LLVM I/O interface checks
        if the _llvm_wp exists and whether LLVM is installed.
        """
        self.debug('llvm.pre() begin')

        self._check_llvm_wp()
        self._check_install()

        self.debug('llvm.pre() end')

    def get_graph(self, source):

        self.debug('llvm.get_graph() begin')

        if source.split('.')[-1] in ['c', 'cpp']:
            source = self._compile(source)
        rawsg = self._extract(source)
        self._populate(rawsg)

        self.debug('llvm.get_graph() end')

    def get_wl(self):

        self.debug('llvm.get_wl() begin')

        self.warning('llvm.get_wl() not implemented yet.')

        self.debug('llvm.get_wl() end')

    def cleanup(self):
        """ Simply remove _llvm_wp
        """

        self.debug('llvm.cleanup() begin')

        if os.path.exists(self._llvm_wp):
            distutils.dir_util.remove_tree(self._llvm_wp)

        self.debug('llvm.cleanup() end')

    def _check_llvm_wp(self):
        """ Cleans-up the work path for the tool.
        """
        if os.path.exists(self._llvm_wp):
            distutils.dir_util.remove_tree(self._llvm_wp)
        os.makedirs(self._llvm_wp)

    def _check_install(self):
        """ Checks that the graph extractor is installed, installs it otherwise.
        """
        tool = os.path.join(self.config['llvm_path'], 'Release+Asserts', 'lib', '%s.so' % self.config['tool_name'])

        if os.path.isfile(tool):
            self.debug('HOPLITE LLVM tool is installed.')
            return

        self.info('HOPLITE LLVM tool not installed. Attempting to auto-install now.')
        self._install()
        # If the second check keeps failing, raise and exception and exit.
        if not os.path.isfile(tool):
            self.fatal('HOPLITE LLVM tool could not be found or failed to compile.')

    def _install(self):
        """ Call to installation of HOPLITE LLVM tool.
        """

        # Copy the appropriate resources to the LLVM path.
        src_dir = os.path.join(self._parent.config['base_path'], 'res', 'llvm')
        dst_dir = os.path.join(self.config['llvm_path'], 'lib', 'Transforms', self.config['tool_name'])
        distutils.dir_util.copy_tree(src_dir, dst_dir)

        # Change directory to the tool one, call make and return to the previous one.
        owd = os.getcwd()
        os.chdir(dst_dir)
        subprocess.call('make')
        os.chdir(owd)

    def _compile(self, source):
        """ Generate the compile command and execute it.
        """
        output = '%s.bc' % '.'.join(os.path.basename(source).split('.')[:-1])
        destination = os.path.join(self._llvm_wp, output)
        cmd = 'clang -O3 -emit-llvm %s -c -o %s' % (source, destination)
        try:
            self.info('Compiling code.')
            subprocess.call(cmd, shell=True)
        except OSError:
            self.fatal('Source file could not be built. Is CLANG installed?')
        return destination

    def _extract(self, source):

        tool = os.path.join(self.config['llvm_path'], 'Release+Asserts', 'lib', '%s.so' % self.config['tool_name'])
        cmd = 'opt -load %s -hoplite_gx' % (tool)

        owd = os.getcwd()
        os.chdir(self._llvm_wp)
        with open(source, 'r') as stream:
            subprocess.call(cmd, shell=True, stdin=stream)

        if not os.path.isfile('llvm_sg_dump.log'):
            self.fatal('There was an error extracting the system graph.')

        with open('llvm_sg_dump.log', 'r') as stream:
            extracted = eval(stream.read())

        os.chdir(owd)

        return extracted

    def _populate(self, rawdata):
        sg = self._parent.systemgraph

# --------------------------------------------------------------------------------------------------
#   0    1    1    2    2    3    3    4    4    5    5    6    6    7    7    8    8    9    9    0
#   5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0
