############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

from db.domain import DBLoopExec

class LoopExec(DBLoopExec):
    """ Class that stores info for logging a loop execution. """

    def __init__(self, *args, **kwargs):
        DBLoopExec.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self):
        cp = DBLoopExec.__copy__(self)
        cp.__class__ = LoopExec
        return cp

    @staticmethod
    def convert(_loop_exec):
        if _loop_exec.__class__ == LoopExec:
            return
        _loop_exec.__class__ = LoopExec
        from core.log.module_exec import ModuleExec
        for module_exec in _loop_exec.module_execs:
            ModuleExec.convert(module_exec)
        from core.log.group_exec import GroupExec
        for group_exec in _loop_exec.group_execs:
            GroupExec.convert(group_exec)

    ##########################################################################
    # Properties

    id = DBLoopExec.db_id
    ts_start = DBLoopExec.db_ts_start
    ts_end = DBLoopExec.db_ts_end
    completed = DBLoopExec.db_completed
    error = DBLoopExec.db_error

    def _get_duration(self):
        if self.db_ts_end is not None:
            return self.db_ts_end - self.db_ts_start
        return None
    duration = property(_get_duration)

    def _get_module_execs(self):
        return self.db_module_execs
    def _set_module_execs(self, module_execs):
        self.db_module_execs = module_execs
    module_execs = property(_get_module_execs, _set_module_execs)
    def add_module_exec(self, module_exec):
        self.db_add_module_exec(module_exec)

    def _get_group_execs(self):
        return self.db_group_execs
    def _set_group_execs(self, group_execs):
        self.db_group_execs = group_execs
    group_execs = property(_get_group_execs, _set_group_execs)
    def add_group_exec(self, group_exec):
        self.db_add_group_exec(group_exec)
