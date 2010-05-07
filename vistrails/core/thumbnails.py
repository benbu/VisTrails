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

""" Utilities for dealing with the thumbnails """
import os
import os.path
import shutil
import time
import uuid
from core import debug
from core.configuration import get_vistrails_configuration, \
      get_vistrails_persistent_configuration
from core.utils import VistrailsInternalError

############################################################################
class CacheEntry(object):
    def __init__(self, abs_name, name, time, size):
        self.abs_name = abs_name
        self.name = name
        self.time = time
        self.size = size
        
class ThumbnailCache(object):
    _instance = None
    IMAGE_MAX_WIDTH = 200 
    class ThumbnailCacheSingleton(object):
        def __call__(self, *args, **kw):
            if ThumbnailCache._instance is None:
                obj = ThumbnailCache(*args, **kw)
                ThumbnailCache._instance = obj
            return ThumbnailCache._instance
        
    getInstance = ThumbnailCacheSingleton()
    
    def __init__(self):
        self.elements = {}
        self.vtelements = {}
        self.conf = None
        conf = get_vistrails_configuration()
        if conf.has('thumbs'):
            self.conf = conf.thumbs
        self.init_cache()
        
    def get_directory(self):
        if self.conf.check('cacheDirectory'):
            thumbnail_dir = self.conf.cacheDirectory
            if not os.path.exists(thumbnail_dir):
                raise VistrailsInternalError("Cannot find %s" % thumbnail_dir)
            return thumbnail_dir
        
        raise VistrailsInternalError("'thumbs.cacheDirectory' not"
                                     " specified in configuration")
        return None
    
    def init_cache(self):
        for root,dirs, files in os.walk(self.get_directory()):
            for f in files:
                fname = os.path.join(root,f)
                statinfo = os.stat(fname)
                size = int(statinfo[6])
                time = float(statinfo[8])
                entry = CacheEntry(fname, f, time, size)
                self.elements[f] = entry
                
    def get_abs_name_entry(self,name):
        """get_abs_name_entry(name) -> str 
        It will look for absolute file path of name in self.elements and 
        self.vtelements. It returns None if item was not found.
        
        """
        try:
            return self.elements[name].abs_name
        except KeyError, e:
            try:
                return self.vtelements[name].abs_name
            except KeyError, e:
                return None
        
    def size(self):
        size = 0
        for entry in self.elements.itervalues():
            size += entry.size
        return size

    def move_cache_directory(self, sourcedir, destdir):
        """change_cache_directory(sourcedir: str, dest_dir: str) -> None"
        Moves files from sourcedir to destdir
        
        """
        if os.path.exists(destdir):
            for entry in self.elements.itervalues():
                try:
                    srcname = entry.abs_name
                    dstname = os.path.join(destdir,entry.name)
                    shutil.move(srcname,dstname)
                    entry.abs_name = dstname
                        
                except shutil.Error, e:
                    debug.warning("Could not move thumbnail from %s to %s: %s" \
                                  % (sourcedir, destdir, str(e)))
                    
    def remove_lru(self,n=1):
        elements = self.elements.values()
        elements.sort(key=lambda obj: obj.time)
        num = min(n,len(elements))
        debug.critical("Will remove %s elements from cache..."%num)
        debug.critical("Cache has %s elements and %s bytes"%(len(elements),
                                                             self.size()))
        for i in range(num):
            try:
                del self.elements[elements[i].name]    
                os.unlink(elements[i].abs_name)
            except os.error, e:
                debug.warning("Could not remove file %s:"(elements[i].abs_name,
                                                          str(e)))
    def remove(self,key):
        if key in self.elements.keys():
            entry = self.elements[key]
            del self.elements[key]
            os.unlink(entry.abs_name)
        elif key in self.vtelements.keys():
            entry = self.vtelements[key]
            del self.vtelements[key]
            os.unlink(entry.abs_name)
            
    def clear(self):
        self.elements = {}
        self._delete_files(self.get_directory())
        
    def add_entry_from_cell_dump(self, folder, key=None):
        """create_entry_from_cell_dump(folder: str) -> str
        Creates a cache entry from images in folder by merge them in a single 
        image and returns the name of the image in cache.
        If a valid key is provided, it will use it as the name of the 
        image file.
        
        """
        
        image = self._merge_thumbnails(folder)
        fname = None
        if image != None:
            fname = "%s.png" % str(uuid.uuid1())
            abs_fname = self._save_thumbnail(image, fname) 
            statinfo = os.stat(abs_fname)
            size = int(statinfo[6])
            time = float(statinfo[8])
            entry = CacheEntry(abs_fname, fname, time, size)
            #remove old element
            if key:
                self.remove(key)
            if self.size() + size > self.conf.cacheSize*1024*1024:
                self.remove_lru(10)
                
            self.elements[fname] = entry
        return fname
        
    def add_entries_from_files(self, absfnames):
        """add_entries_from_files(absfnames: list of str) -> None
        In this case the files already exist somewhere on disk.
        We just keep references to them.
        
        """
        for abs_fname in absfnames:
            fname = os.path.basename(abs_fname)
            statinfo = os.stat(abs_fname)
            size = int(statinfo[6])
            time = float(statinfo[8])
            entry = CacheEntry(abs_fname, fname, time, size)
            self.vtelements[fname] = entry

    @staticmethod
    def _delete_files(dirname):
        """delete_files(dirname: str) -> None
        Deletes all files inside dirname
    
        """
        try:
            for root, dirs, files in os.walk(dirname):
                for fname in files:
                    os.unlink(os.path.join(root,fname))
                    
        except OSError, e:
            debug.warning("Error when removing thumbnails: %s"%str(e))
    
    @staticmethod
    def _merge_thumbnails(folder):
        """_merge_thumbnails(folder: str) -> QImage 
        Generates a single image formed by all the images in folder 
        
        """
        from PyQt4 import QtCore, QtGui
        height = 0
        width = 0
        pixmaps = []
        for root, dirs, files in os.walk(folder):
            for f in files:
                pix = QtGui.QPixmap(os.path.join(root,f))
                pixmaps.append(pix)
                #width += pix.width()
                #height = max(height, pix.height())
                height += pix.height()
                width = max(width,pix.width())
        if len(pixmaps) > 0:        
            finalImage = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)
            painter = QtGui.QPainter(finalImage)
            x = 0
            for pix in pixmaps:
                painter.drawPixmap(0, x, pix)
                x += pix.height()
            painter.end()
            if width > ThumbnailCache.IMAGE_MAX_WIDTH:
                finalImage = finalImage.scaledToWidth(ThumbnailCache.IMAGE_MAX_WIDTH,
                                                      QtCore.Qt.SmoothTransformation)
        else:
            finalImage = None
        return finalImage

    def _save_thumbnail(self, pngimage, fname):
        """_save_thumbnail(pngimage:QImage, fname: str) -> str 
        Returns the absolute path of the saved image
        
        """
        png_fname = os.path.join(self.get_directory(), fname)
        if os.path.exists(png_fname):
            os.unlink(png_fname)
        pngimage.save(png_fname)
        return png_fname

    def _copy_thumbnails(self, thumbnails):
        """_copy_thumbnails(thumbnails: list of str) -> None """
        local_dir = get_thumbnail_dir()
        for thumb in thumbnails:
            local_thumb = os.path.join(local_dir, os.path.basename(thumb))
            if os.path.exists(thumb) and not os.path.exists(local_thumb):
                shutil.copyfile(thumb, local_thumb)
