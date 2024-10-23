from diskcache import Cache
from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.dataset import DataSet
from playhouse.kv import KeyValue
from peewee import Database, BlobField, IntegerField
from pyperf import Runner
from common import run_db_bench
from hashlib import shake_256
from functools import partial

loop_N = 32
value_N = 1024
value_out = shake_256(b'', usedforsecurity=False).digest(value_N)

def diskcache_kv_set(tmpdir):
    store = Cache(tmpdir)
    for i in range(loop_N):
        store[i] = value_out

def diskcache_kv_set_tx(tmpdir):
    store = Cache(tmpdir)
    with store.transact():
        for i in range(loop_N):
            store[i] = value_out

def diskcache_kv_get(tmpdir):
    store = Cache(tmpdir)
    for i in range(loop_N):
        v = store[i]
        assert v == value_out

def diskcache_kv_get_tx(tmpdir):
    store = Cache(tmpdir)
    with store.transact():
        for i in range(loop_N):
            v = store[i]
            assert v == value_out

def dataset_kv_setup(tmpdir, init_data=False):
    db = KeyValue(database=SqliteExtDatabase(tmpdir + '/test.db', pragmas={
        # Eqv diskcache settings
        'journal_mode': 'wal',
        'cache_size': 2**13,  # 64MB
        'auto_vacuum': 1,
        'mmap_size': 2**26,
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
        'synchronous': 0}), key_field=IntegerField(primary_key=True), value_field=BlobField())

    if init_data:
        dataset_kv_set_batch(None, db)

    return db

def dataset_kv_set(tmpdir, db):
    for i in range(loop_N):
        db[i] = value_out

def dataset_kv_set_batch(tmpdir, db):
    update = {str(i): value_out for i in range(loop_N)}
    db.update(**update)

def dataset_kv_get(tmpdir, db):
    for i in range(loop_N):
        v = db[i]
        assert v == value_out

def dataset_kv_get_range(tmpdir, db):
    data = db[db.key < loop_N]
    assert len(data) == loop_N
    for v in data:
        assert v == value_out

runner = Runner()
run_db_bench('diskcache-kv-set', diskcache_kv_set, runner=runner)
run_db_bench('diskcache-kv-set-transact', diskcache_kv_set_tx, runner=runner)
run_db_bench('diskcache-kv-get', diskcache_kv_get, setup_fn=diskcache_kv_set_tx, runner=runner)
run_db_bench('diskcache-kv-get-transact', diskcache_kv_get_tx, setup_fn=diskcache_kv_set_tx, runner=runner)

run_db_bench('dataset-kv-set', dataset_kv_set, setup_fn=dataset_kv_setup, runner=runner)
run_db_bench('dataset-kv-set-batch', dataset_kv_set_batch, setup_fn=dataset_kv_setup, runner=runner)
run_db_bench('dataset-kv-get', dataset_kv_get, setup_fn=partial(dataset_kv_setup, init_data=True), runner=runner)
run_db_bench('dataset-kv-get-range', dataset_kv_get_range, setup_fn=partial(dataset_kv_setup, init_data=True), runner=runner)

