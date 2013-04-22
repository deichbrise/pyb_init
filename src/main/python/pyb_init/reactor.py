# coding=utf-8
#
# pyb_init - pybuilder project initialization
#
# Copyright (C) 2013 Maximilien Riehl <maximilien.riehl@gmail.com>
#
#        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.

from __future__ import absolute_import
import os

from pyb_init.tasks import ShellCommandTask, PreconditionTask
from pyb_init.vcs_tools import determine_project_name_from_git_url

VIRTUALENV_NAME = 'virtualenv'


def for_local_initialization():
    reactor = TaskReactor()
    _add_common_tasks(reactor=reactor, command_prefix=None)
    return reactor


def for_github_clone(user, project):
    git_url = 'https://github.com/{0}/{1}'.format(user, project)
    return for_git_clone(git_url)


def for_git_clone(git_url):
    reactor = TaskReactor()
    reactor.add_task(ShellCommandTask('git clone {0}'.format(git_url)))
    project = determine_project_name_from_git_url(git_url)
    _add_common_tasks(reactor=reactor,
                      command_prefix='cd {0} && '.format(project),
                      project=project)
    return reactor


def _add_common_tasks(reactor, command_prefix, project=None):
    _add_preconditions(reactor, project)
    commands = ['virtualenv {0} --clear'.format(VIRTUALENV_NAME),
                'source {0}/bin/activate && pip install pybuilder'.format(VIRTUALENV_NAME),
                'source {0}/bin/activate && pyb install_dependencies'.format(VIRTUALENV_NAME),
                'source {0}/bin/activate && pyb -v'.format(VIRTUALENV_NAME)]

    if command_prefix:
        expanded_commands = [command_prefix + command for command in commands]
    else:
        expanded_commands = commands
    for command in expanded_commands:
        reactor.add_task(ShellCommandTask(command))


def _add_preconditions(reactor, project):
    if project:
        reactor.add_task(PreconditionTask(lambda: os.path.exists('{0}/build.py'.format(project)),
                                          'Build descriptor ({0}/build.py) should exist'.format(project)))
    else:
        reactor.add_task(PreconditionTask(lambda: os.path.exists('build.py'),
                                          'Build descriptor (build.py) should exist'))

    virtualenv_installed_if_0 = ShellCommandTask('command -v virtualenv', ignore_failures=True).execute
    reactor.add_task(PreconditionTask(
        lambda: virtualenv_installed_if_0() == 0,
        'Virtualenv should be installed and callable'))


class TaskReactor(object):

    def __init__(self):
        self.tasks = []

    def get_tasks(self):
        return self.tasks

    def add_task(self, task):
        self.tasks.append(task)
