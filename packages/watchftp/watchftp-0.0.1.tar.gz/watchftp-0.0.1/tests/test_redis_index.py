import asyncio
import time
import unittest
import uuid

from watchftp.connectors.base import RemoteEntry
from watchftp.index import IndexEntry
from watchftp.redis import RedisIndexStore
from watchftp.settings import WatchConfig, WatchPath

REDIS_URL = "redis://127.0.0.1:6379/0"


class RedisIndexStoreTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        tenant = f"test-{uuid.uuid4().hex}"
        self.config = WatchConfig(
            tenant_id=tenant,
            protocol="sftp",
            host="localhost",
            username="svc",
            watch_paths=[WatchPath(root="/", include=["**/*"])],
            event_bus="redis_stream",
            redis_url=REDIS_URL,
        )
        self.store = RedisIndexStore(self.config)
        await self.store.start()
        await self.store.clear()

    async def asyncTearDown(self):
        await self.store.clear()
        await self.store.stop()

    async def test_roundtrip(self):
        created = [
            RemoteEntry(path="/a.txt", type="file", size=10, mtime=time.time(), unique=None, perms=None, metadata=None),
            RemoteEntry(path="/dir", type="dir", size=None, mtime=time.time(), unique=None, perms=None, metadata=None),
        ]
        await self.store.persist(created=created, deleted=[], modified=[])
        restored = await self.store.load_index()
        restored_map = {entry.path: entry for entry in restored}
        self.assertEqual(len(restored_map), len(created))
        self.assertEqual(restored_map["/a.txt"].size, created[0].size)

        modified_entry = RemoteEntry(
            path="/a.txt",
            type="file",
            size=20,
            mtime=time.time(),
            unique=None,
            perms=None,
            metadata=None,
        )
        await self.store.persist(created=[], deleted=[], modified=[(IndexEntry.from_remote(created[0]), modified_entry)])
        restored = await self.store.load_index()
        restored_map = {entry.path: entry for entry in restored}
        self.assertEqual(restored_map["/a.txt"].size, 20)

        await self.store.persist(created=[], deleted=[IndexEntry.from_remote(created[1])], modified=[])
        restored = await self.store.load_index()
        self.assertNotIn("/dir", {entry.path for entry in restored})

    async def test_hotness_tracking(self):
        now = time.time()
        await self.store.record_hot("/root", now)
        hot = await self.store.load_hotness()
        self.assertIn("/root", hot)
        self.assertAlmostEqual(hot["/root"], now, delta=1)


if __name__ == "__main__":
    unittest.main()
