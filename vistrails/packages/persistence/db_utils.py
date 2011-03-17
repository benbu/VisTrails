############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

import os
import sqlite3

class DatabaseAccessSingleton(object):
    def __new__(cls, *args, **kw):
        if DatabaseAccess._instance is None:
            obj = DatabaseAccess(*args, **kw)
            DatabaseAccess._instance = obj
        return DatabaseAccess._instance

class DatabaseAccess(object):
    _instance = None
    def __init__(self, db_file):
        print 'initing DatabaseAccess'
        self.db_file = db_file
        run_schema = False
        if not os.path.exists(db_file):
            run_schema = True
        self.conn = sqlite3.connect(db_file)
        if run_schema:
            print 'running schema'
            print 'schema file:', os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), 'schema.sql')
            cur = self.conn.cursor()
            self.run_sql_file(cur, os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), 'schema.sql'))
        self.model = None

    def set_model(self, model):
        self.model = model

    def run_sql_file(self, cur, sql_file):
        cmd = ''
        for line in open(sql_file):
            cmd += line
            if line.strip().endswith(';'):
                cur.execute(cmd.strip())
                cmd = ''

    def finalize(self):
        self.conn.close()

    def write_database(self, value_dict):
#         db_file = '/vistrails/managed/files.db'
#         self.conn = sqlite3.connect(db_file)

        cur = self.conn.cursor()
        cols, vals = zip(*value_dict.iteritems())
        col_str = ', '.join(cols)
        # print "executing sql:", "INSERT INTO file(%s) VALUES (%s);" % \
        #                 (col_str, ','.join(['?'] * len(vals)))
        # print "  ", vals
        cur.execute("INSERT INTO file(%s) VALUES (%s);" % \
                        (col_str, ','.join(['?'] * len(vals))),
                    vals)
        self.conn.commit()

        if self.model:
            self.model.add_data(value_dict)

    #         cur.execute("SELECT id, name, tags, user, date_created, "
    #                     "date_modified, content_hash, version, signature "
    #                     "FROM file;")

    def read_database(self, cols=None, where_dict=None):
        # self.conn = sqlite3.connect(db_file)
        cur = self.conn.cursor()
        if cols is None:
            cols = ["id", "name", "tags", "user", "date_created",
                    "date_modified", "content_hash", "version", "signature"]
        col_str = ', '.join(cols)
        if where_dict is None or len(where_dict) <= 0:
            cur.execute("SELECT " + ", ".join(cols) + " FROM file;")
        else:
            where_cols, where_vals = zip(*where_dict.iteritems())
            where_str = '=? AND '.join(where_cols) + '=?'
            cur.execute("SELECT " + ", ".join(cols) + " FROM file "
                        "WHERE %s;" % where_str, where_vals)
        return cur.fetchall()

    def search_by_signature(self, signature):
        cur = self.conn.cursor()
        cur.execute("SELECT id, version, name FROM file WHERE signature=? "
                    "ORDER BY date_created DESC LIMIT 1;", (signature,))
        res = cur.fetchone()
        if res:
            return res
        return None

    def get_signature(self, id, version=None):
        cur = self.conn.cursor()
        cur.execute("SELECT signature FROM file where id=? and version=?;", 
                    (id, version))
        res = cur.fetchone()
        if res:
            return res[0]
        return None

    def ref_exists(self, id, version=None):
        cur = self.conn.cursor()
        if version is None:
            cur.execute("SELECT id, version, name, signature FROM file "
                        "WHERE id=?;", (id,))
        else:
            cur.execute("SELECT id, version, name, signature FROM file "
                        "WHERE id=? AND version=?;", (id, version))
        res = cur.fetchone()
        return res is not None