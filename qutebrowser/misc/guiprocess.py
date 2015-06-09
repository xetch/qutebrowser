# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2015 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""A QProcess which shows notifications in the GUI."""

import shlex

from PyQt5.QtCore import pyqtSlot, QProcess, QIODevice, QProcessEnvironment

from qutebrowser.utils import message, log

# A mapping of QProcess::ErrorCode's to human-readable strings.

ERROR_STRINGS = {
    QProcess.FailedToStart: "The process failed to start.",
    QProcess.Crashed: "The process crashed.",
    QProcess.Timedout: "The last waitFor...() function timed out.",
    QProcess.WriteError: ("An error occurred when attempting to write to the "
                          "process."),
    QProcess.ReadError: ("An error occurred when attempting to read from the "
                         "process."),
    QProcess.UnknownError: "An unknown error occurred.",
}


class GUIProcess:

    """An external process which shows notifications in the GUI.

    Args:
        proc: The underlying QProcess.
        cmd: The command which was started.
        args: A list of arguments which gets passed.
        started: Whether the underlying process is started.
        error: An error code (QProcess::ProcessError) or None.
        _win_id: The window ID this process is used in.
        _what: What kind of thing is spawned (process/editor/userscript/...).
               Used in messages.
        _verbose: Whether to show more messages.
    """

    def __init__(self, win_id, what, *, verbose=False, additional_env=None,
                 parent=None):
        self._win_id = win_id
        self._what = what
        self._verbose = verbose
        self.error = None
        self.started = False
        self.cmd = None
        self.args = None
        self.exit = None

        self.proc = QProcess(parent)
        self.proc.error.connect(self.on_error)
        self.proc.finished.connect(self.on_finished)
        self.proc.started.connect(self.on_started)

        if additional_env is not None:
            procenv = QProcessEnvironment.systemEnvironment()
            for k, v in additional_env.items():
                procenv.insert(k, v)
            self.proc.setProcessEnvironment(procenv)

    @pyqtSlot(QProcess.ProcessError)
    def on_error(self, error):
        """Show a message if there was an error while spawning."""
        self.error = error
        msg = ERROR_STRINGS[error]
        message.error(self._win_id, "Error while spawning {}: {}".format(
                      self._what, msg), immediately=True)

    @pyqtSlot(int, QProcess.ExitStatus)
    def on_finished(self, code, status):
        """Show a message when the process finished."""
        self.started = False
        self.exit = code
        log.procs.debug("Process finished with code {}, status {}.".format(
            code, status))
        if status == QProcess.CrashExit:
            message.error(self._win_id,
                          "{} crashed!".format(self._what.capitalize()),
                          immediately=True)
        elif status == QProcess.NormalExit and code == 0:
            if self._verbose:
                message.info(self._win_id, "{} exited successfully.".format(
                    self._what.capitalize()))
        else:
            assert status == QProcess.NormalExit
            message.error(self._win_id, "{} exited with status {}.".format(
                self._what.capitalize(), code))

    @pyqtSlot()
    def on_started(self):
        """Called when the process started successfully."""
        log.procs.debug("Process started.")
        assert not self.started
        self.started = True

    def _pre_start(self, cmd, args):
        """Prepare starting of a QProcess."""
        if self.started:
            raise ValueError("Trying to start a running QProcess!")
        self.cmd = cmd
        self.args = args
        if self._verbose:
            fake_cmdline = ' '.join(shlex.quote(e) for e in [cmd + args])
            message.info(self._win_id, 'Executing: ' + fake_cmdline)

    def start(self, cmd, args, mode=QIODevice.ReadWrite):
        """Convenience wrapper around QProcess::start."""
        log.procs.debug("Starting process.")
        self._pre_start(cmd, args)
        self.proc.start(cmd, args, mode)

    def start_detached(self, cmd, args, cwd=None):
        """Convenience wrapper around QProcess::startDetached."""
        log.procs.debug("Starting detached.")
        self._pre_start(cmd, args)
        ok = self.proc.startDetached(cmd, args, cwd)

        if ok:
            log.procs.debug("Process started.")
            self.started = True
        else:
            message.error(self._win_id, "Error while spawning {}: {}.".format(
                          self._what, self.proc.error()), immediately=True)
