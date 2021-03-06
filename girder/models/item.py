#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright 2013 Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import datetime

from .model_base import Model, ValidationException
from girder.constants import AccessType


class Item(Model):
    """
    Items are leaves in the data hierarchy. They can contain 0 or more
    files within them, and can also contain arbitrary metadata.
    """

    def initialize(self):
        self.name = 'group'
        self.ensureIndices(['lowerName'])

    def validate(self, doc):
        doc['name'] = doc['name'].strip()
        doc['description'] = doc['description'].strip()

        if not doc['name']:
            raise ValidationException('Item name must not be empty.', 'name')

        # Ensure unique name among sibling items
        q = {
            'name': doc['name'],
            'folderId': doc['folderId']
            }
        if '_id' in doc:
            q['_id'] = {'$ne': doc['_id']}
        duplicates = self.find(q, limit=1, fields=['_id'])
        if duplicates.count() != 0:
            raise ValidationException('An item with that name already'
                                      'exists in that folder.', 'name')

        # Ensure unique name among sibling folders
        q = {
            'parentId': doc['folderId'],
            'name': doc['name'],
            'parentCollection': 'folder'
            }
        duplicates = self.model('folder').find(q, limit=1, fields=['_id'])
        if duplicates.count() != 0:
            raise ValidationException('A folder with that name already'
                                      'exists here.', 'name')

        return doc

    def remove(self, item):
        """
        Delete an item, and all references to it in the database.

        :param item: The item document to delete.
        :type item: dict
        """

        # TODO delete everything underneath this item

        # Delete the item itself
        Model.remove(self, item)

    def search(self, query, user=None, limit=50, offset=0, sort=None):
        """
        Search for items with full text search.

        TODO
        1. Find all items that match the text search.
        2. Filter them by ensuring read access on their parent folder. As we
        fetch parent folders, keep a cache dict mapping folder ID to either
        (True | False), representing whether the user has read access to that
        folder, so we can lookup in the cache quickly without having to run to
        the database to check every time. There should be a high cache hit rate
        since items with similar text have a good chance of residing in the
        same folder, or a small set of folders.
        """
        folderAccess = {}
        return []

    def createItem(self, name, creator, folder, description=''):
        """
        Create a new item. The creator will be given admin access to it.

        :param name: The name of the item.
        :type name: str
        :param description: Description for the folder.
        :type description: str
        :param folder: The parent folder of the item.
        :param creator: User document representing the creator of the group.
        :type creator: dict
        :returns: The item document that was created.
        """
        now = datetime.datetime.now()

        if not type(creator) is dict or not '_id' in creator:
            # Internal error -- this shouldn't be called without a user.
            raise Exception('Creator must be a user.')

        return self.save({
            'name': name,
            'description': description,
            'folderId': folder['_id'],
            'creatorId': creator['_id'],
            'created': now,
            'updated': now,
            'size': 0
            })
