from functools import partial
from hashlib import shake_256
from diskcache.core import time
from playhouse.db_url import connect
from peewee import *
from playhouse.apsw_ext import APSWDatabase
from playhouse.sqliteq import SqliteQueueDatabase
from diskcache import Cache
from pathlib import Path

from pyperf import Runner
from common import run_db_bench

# import logging
# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

class CompoundRecord(Model):
    smiles = CharField(primary_key=True)
    inchi = CharField()
    record = BlobField()

    @staticmethod
    def get_many(smiles: set[str] | None=None, inchi: set[str] | None=None):
        return CompoundRecord.select().where(
            CompoundRecord.smiles.in_(smiles) |
            CompoundRecord.inchi.in_(inchi)
        )


loop_N = 1024 
value_N = 1024
value_out = shake_256(b'', usedforsecurity=False).digest(value_N)


inchi_mul = int(1e5)
def peewee_mkv_serial_insert(tmpdir, db: Database):
    for i in range(loop_N):
        CompoundRecord.replace(smiles=str(i), inchi=str(i*inchi_mul), record=value_out).execute()

def peewee_mkv_serial_insert_tx(tmpdir, db: Database):
    with db.atomic():
        for i in range(loop_N):
            CompoundRecord.replace(smiles=str(i), inchi=str(i*inchi_mul), record=value_out).execute()


def peewee_mkv_batch_insert(tmpdir, db: Database):
    CompoundRecord.replace_many([
               {'smiles': str(i), 
                'inchi': str(i*inchi_mul), 
                'record': value_out}
           for i in range(loop_N)]).execute()


def peewee_mkv_serial_read(tmpdir, db: Database):
    for i in range(loop_N):
        record = CompoundRecord.get((CompoundRecord.smiles == str(i)) | (CompoundRecord.inchi == str(i*inchi_mul)))
        # print(list(record))
        # print()
        # for i, v in enumerate(record.iterator(db)):
            # print(i, v)


def peewee_mkv_raw_serial_read(tmpdir, db: Database):
    for i in range(loop_N):
        record = db.execute_sql('SELECT DISTINCT * FROM compoundrecord WHERE smiles = ? OR inchi = ?', (str(i), str(i*inchi_mul)))
        # db.execute_sql('SELECT * FROM compoundrecord WHERE  inchi = ?', (str(i*inchi_mul),))


def peewee_mkv_batch_read(tmpdir, db: Database):
    smiles = set()
    inchi = set()
    for i in range(loop_N):
        smiles.add(str(i))
        inchi.add(str(i*inchi_mul))

    v = CompoundRecord.get_many(smiles, inchi).distinct().dicts().execute()
        
def peewee_mkv_setup(tmpdir: str, init_data=False, add_indexes=False):
    db = SqliteDatabase(f'{tmpdir}/data.db', pragmas={
                        'mmap_size': 2**26,
                        'synchronous': 1,
                       'journal_mode': 'wal',
                        # 'read_uncommited': True
                      })
    db.connect()
    # db = SqliteDatabase(f'{tmpdir}/data.db', pragmas={
                       # 'journal_mode': 'wal',
    #                    'auto_vacuum': 1,
    #                    'cache_size': 2**13,
    #                    'mmap_size': 2**26,
    #                    'synchronous': 1
    #                })
    # db = connect(f"sqlite:///{tmpdir}/data.db")

    if add_indexes:
        CompoundRecord.add_index(CompoundRecord.index(CompoundRecord.smiles, unique=True))
        CompoundRecord.add_index(CompoundRecord.index(CompoundRecord.inchi, unique=True))

    db.bind([CompoundRecord])
    db.create_tables([CompoundRecord])

    if init_data:
        peewee_mkv_batch_insert(tmpdir, db)

    return db

def diskcache_mkv_insert(tmpdir):
    store = Cache(tmpdir)
    with store.transact():
        for i in range(loop_N):
            store[str(i)] = {'smiles': str(i), 'inchi': str(i*inchi_mul), 'record': value_out}
            store[str(i*inchi_mul)] = {'ref': str(i)}

def diskcache_mkv_setup(tmpdir) -> Cache:
    store = Cache(tmpdir)
    with store.transact():
        for i in range(loop_N):
            store[str(i)] = {'smiles': str(i), 'inchi': str(i*inchi_mul), 'record': value_out}
            store[str(i*inchi_mul)] = {'ref': str(i)}
    return store
    
def diskcache_mkv_read(tmpdir, store: Cache):
    for i in range(loop_N):
        key = store[str(i*inchi_mul)]['ref']
        v = store[key]

runner = Runner()
run_db_bench('peewee-mkv-serial-insert', peewee_mkv_serial_insert, setup_fn=peewee_mkv_setup, runner=runner)
run_db_bench('peewee-mkv-serial-insert-transaction', peewee_mkv_serial_insert_tx, setup_fn=peewee_mkv_setup, runner=runner)
run_db_bench('peewee-mkv-batch-insert', peewee_mkv_batch_insert, setup_fn=peewee_mkv_setup, runner=runner)
run_db_bench('peewee-mkv-batch-insert-indexed', peewee_mkv_batch_insert, setup_fn=partial(peewee_mkv_setup, add_indexes=True), runner=runner)
run_db_bench('peewee-mkv-serial-read', peewee_mkv_serial_read, setup_fn=partial(peewee_mkv_setup, init_data=True), runner=runner)
run_db_bench('peewee-mkv-serial-read-indexed', peewee_mkv_serial_read, setup_fn=partial(peewee_mkv_setup, init_data=True, add_indexes=True), runner=runner)
run_db_bench('peewee-mkv-raw-serial-read', peewee_mkv_raw_serial_read, setup_fn=partial(peewee_mkv_setup, init_data=True), runner=runner)
run_db_bench('peewee-mkv-raw-serial-read-indexed', peewee_mkv_raw_serial_read, setup_fn=partial(peewee_mkv_setup, init_data=True, add_indexes=True), runner=runner)
run_db_bench('peewee-mkv-batch-read', peewee_mkv_batch_read, setup_fn=partial(peewee_mkv_setup, init_data=True), runner=runner)
run_db_bench('peewee-mkv-batch-read-indexed', peewee_mkv_batch_read, setup_fn=partial(peewee_mkv_setup, init_data=True, add_indexes=True), runner=runner)

run_db_bench('diskcache-mkv-insert', diskcache_mkv_insert, runner=runner)
run_db_bench('diskcache-mkv-read', diskcache_mkv_read, setup_fn=diskcache_mkv_setup, runner=runner)
