"""Make sure slots are decorated with @pyqtSlot."""

import astroid
from pylint import interfaces, checkers
from pylint.checkers import utils


class PyQtSlotChecker(checkers.BaseChecker):

    """Checker to check if slots are decorated with @pyqtSlot."""

    __implements__ = interfaces.IAstroidChecker
    name = 'pyqt-slot'

    msgs = {
        'W9500': ('Slot not decorated with @pyqtSlot', 'pyqt-slot', None),
    }

    @utils.check_messages('pyqt-slot')
    def visit_callfunc(self, node):
        """Visit a CallFunc node."""
        if hasattr(node, 'func'):
            if getattr(node.func, 'name', None) == 'connect':
                import pdb; pdb.set_trace()

def register(linter):
    """Register this checker."""
    linter.register_checker(PyQtSlotChecker(linter))
