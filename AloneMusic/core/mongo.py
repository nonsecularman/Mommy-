#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/AloneMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/AloneMusic/blob/master/LICENSE >
#
# All rights reserved.

import json
import os
import asyncio
from ..logging import LOGGER

class MongoMockCollection:
    def __init__(self, db, name):
        self.db = db
        self.name = name

    async def find_one(self, filter):
        async with self.db.lock:
            data = self.db.data.setdefault(self.name, [])
            for doc in data:
                if self._match(doc, filter):
                    return doc
            return None

    async def update_one(self, filter, update, upsert=False):
        async with self.db.lock:
            data = self.db.data.setdefault(self.name, [])
            match_doc = None
            for doc in data:
                if self._match(doc, filter):
                    match_doc = doc
                    break
            
            if not match_doc:
                if upsert:
                    new_doc = filter.copy()
                    # Apply update
                    self._apply_update(new_doc, update)
                    data.append(new_doc)
                    self.db.save()
                    return {"upserted_id": new_doc.get("_id")}
                return {"modified_count": 0}
            
            self._apply_update(match_doc, update)
            self.db.save()
            return {"modified_count": 1}

    async def insert_one(self, document):
        async with self.db.lock:
            data = self.db.data.setdefault(self.name, [])
            # Deep copy to avoid side-effects
            doc = document.copy()
            data.append(doc)
            self.db.save()
            return doc

    async def delete_one(self, filter):
        async with self.db.lock:
            data = self.db.data.setdefault(self.name, [])
            for i, doc in enumerate(data):
                if self._match(doc, filter):
                    data.pop(i)
                    self.db.save()
                    return {"deleted_count": 1}
            return {"deleted_count": 0}

    def find(self, filter=None):
        return MongoMockCursor(self, filter)

    def _match(self, doc, filter):
        if not filter:
            return True
        for k, v in filter.items():
            if k in ("user_id", "chat_id"):
                # Handle potential type mismatches
                if str(doc.get(k)) != str(v):
                    return False
            elif isinstance(v, dict):
                # E.g., {"$gt": 0} or similar operator
                doc_val = doc.get(k)
                if "$gt" in v:
                    if not (doc_val is not None and doc_val > v["$gt"]):
                        return False
                elif "$lt" in v:
                    if not (doc_val is not None and doc_val < v["$lt"]):
                        return False
                else:
                    if doc_val != v:
                        return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    def _apply_update(self, doc, update):
        if "$set" in update:
            for k, v in update["$set"].items():
                doc[k] = v
        if "$unset" in update:
            for k in update["$unset"]:
                if k in doc:
                    del doc[k]

class MongoMockCursor:
    def __init__(self, collection, filter):
        self.collection = collection
        self.filter = filter
        self.index = 0
        self._results = None

    async def _fetch(self):
        if self._results is None:
            async with self.collection.db.lock:
                data = self.collection.db.data.setdefault(self.collection.name, [])
                self._results = [doc for doc in data if self.collection._match(doc, self.filter)]

    def __aiter__(self):
        return self

    async def __anext__(self):
        await self._fetch()
        if self.index >= len(self._results):
            raise StopAsyncIteration
        val = self._results[self.index]
        self.index += 1
        return val

    async def to_list(self, length):
        await self._fetch()
        return self._results[:length]

class MongoMockDB:
    def __init__(self, filepath):
        self.filepath = filepath
        self.lock = asyncio.Lock()
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.data = json.load(f)
            except Exception as e:
                LOGGER("MongoMockDB").error(f"Error loading local DB: {e}")
                self.data = {}
        else:
            self.data = {}

    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            LOGGER("MongoMockDB").error(f"Error saving local DB: {e}")

    def __getattr__(self, name):
        return MongoMockCollection(self, name)

    async def command(self, cmd):
        if cmd == "dbstats":
            return {"dataSize": 1024, "storageSize": 1024}
        return {}

LOGGER(__name__).info("Connecting to your local JSON Database...")
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "local_db.json"))
mongodb = MongoMockDB(db_path)
LOGGER(__name__).info(f"Connected to local JSON Database at {db_path}.")
