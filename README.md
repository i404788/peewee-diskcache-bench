# Peewee vs Diskcache Benchmark

This is a benchmark specifically for Peewee's `Dataset` against `diskcache`s Cache. 
They both (can) use `sqlite` under the hood, however they have different options in querying. 
The benchmark runs multiple scenarios:
* A key-value store for blobs
  * Peewee's `KeyValue` supports (concurrent) bisected operations (set, get, del)
  * `diskcache`'s supports `transact`ions 
* A multi-key-value store where multiple keys may reference the same value
* ~A key-document store where the document is queried (diskcache using an index, dataset using sqlite)~
  

Both size & speed will be tested.

## Requirements

* `dust` cli tool
* `pyperf` for benchmarking

## Results

### Key-Value

Summary:

Diskcache is quite a bit faster for individual key operations (1.25x-2.44x), however for multi-key operations peewee is significantly faster (5.25x-8.5x).
All runs (`*set*` & `*get*`) perform the same amount of work with the same data, but using the different methods.


```
diskcache-kv-set: Mean +- std dev: 2.89 ms +- 0.04 ms
diskcache-kv-set-transact: Mean +- std dev: 2.08 ms +- 0.02 ms
diskcache-kv-get: Mean +- std dev: 1.45 ms +- 0.02 ms
diskcache-kv-get-transact: Mean +- std dev: 1.37 ms +- 0.02 ms
dataset-kv-set: Mean +- std dev: 3.74 ms +- 0.09 ms
dataset-kv-set-batch: Mean +- std dev: 396 us +- 7 us
dataset-kv-get: Mean +- std dev: 3.55 ms +- 0.07 ms
dataset-kv-get-range: Mean +- std dev: 161 us +- 2 us
```


<details>

```
Raw value minimum: 182 ms
Raw value maximum: 194 ms

Number of calibration run: 1
Number of run with values: 20
Total number of run: 21

Number of warmup per run: 1
Number of value per run: 10
Loop iterations per value: 64
Total number of values: 200

Minimum:         2.84 ms
Median +- MAD:   2.89 ms +- 0.03 ms
Mean +- std dev: 2.89 ms +- 0.04 ms
Maximum:         3.03 ms

  0th percentile: 2.84 ms (-2% of the mean) -- minimum
  5th percentile: 2.85 ms (-2% of the mean)
 25th percentile: 2.86 ms (-1% of the mean) -- Q1
 50th percentile: 2.89 ms (-0% of the mean) -- median
 75th percentile: 2.92 ms (+1% of the mean) -- Q3
 95th percentile: 2.95 ms (+2% of the mean)
100th percentile: 3.03 ms (+5% of the mean) -- maximum

Number of outlier (out of 2.78 ms..3.00 ms): 1

diskcache-kv-set: Mean +- std dev: 2.89 ms +- 0.04 ms
Storage usage: 33KB std: 38KB
=====================
Raw value minimum: 130 ms
Raw value maximum: 138 ms

Number of calibration run: 1
Number of run with values: 20
Total number of run: 21

Number of warmup per run: 1
Number of value per run: 10
Loop iterations per value: 64
Total number of values: 200

Minimum:         2.03 ms
Median +- MAD:   2.07 ms +- 0.01 ms
Mean +- std dev: 2.08 ms +- 0.02 ms
Maximum:         2.16 ms

  0th percentile: 2.03 ms (-2% of the mean) -- minimum
  5th percentile: 2.05 ms (-1% of the mean)
 25th percentile: 2.06 ms (-1% of the mean) -- Q1
 50th percentile: 2.07 ms (-0% of the mean) -- median
 75th percentile: 2.08 ms (+0% of the mean) -- Q3
 95th percentile: 2.13 ms (+3% of the mean)
100th percentile: 2.16 ms (+4% of the mean) -- maximum

Number of outlier (out of 2.02 ms..2.12 ms): 13

diskcache-kv-set-transact: Mean +- std dev: 2.08 ms +- 0.02 ms
Storage usage: 21KB std: 34KB
=====================
Raw value minimum: 182 ms
Raw value maximum: 198 ms

Number of calibration run: 1
Number of run with values: 20
Total number of run: 21

Number of warmup per run: 1
Number of value per run: 10
Loop iterations per value: 128
Total number of values: 200

Minimum:         1.42 ms
Median +- MAD:   1.44 ms +- 0.01 ms
Mean +- std dev: 1.45 ms +- 0.02 ms
Maximum:         1.55 ms

  0th percentile: 1.42 ms (-2% of the mean) -- minimum
  5th percentile: 1.43 ms (-1% of the mean)
 25th percentile: 1.44 ms (-1% of the mean) -- Q1
 50th percentile: 1.44 ms (-0% of the mean) -- median
 75th percentile: 1.45 ms (+0% of the mean) -- Q3
 95th percentile: 1.50 ms (+4% of the mean)
100th percentile: 1.55 ms (+7% of the mean) -- maximum

Number of outlier (out of 1.42 ms..1.47 ms): 19

diskcache-kv-get: Mean +- std dev: 1.45 ms +- 0.02 ms
Storage usage: 76KB std: 0KB
=====================
Raw value minimum: 172 ms
Raw value maximum: 187 ms

Number of calibration run: 1
Number of run with values: 20
Total number of run: 21

Number of warmup per run: 1
Number of value per run: 10
Loop iterations per value: 128
Total number of values: 200

Minimum:         1.35 ms
Median +- MAD:   1.36 ms +- 0.01 ms
Mean +- std dev: 1.37 ms +- 0.02 ms
Maximum:         1.46 ms

  0th percentile: 1.35 ms (-2% of the mean) -- minimum
  5th percentile: 1.35 ms (-1% of the mean)
 25th percentile: 1.36 ms (-1% of the mean) -- Q1
 50th percentile: 1.36 ms (-0% of the mean) -- median
 75th percentile: 1.37 ms (+0% of the mean) -- Q3
 95th percentile: 1.41 ms (+3% of the mean)
100th percentile: 1.46 ms (+7% of the mean) -- maximum

Number of outlier (out of 1.34 ms..1.39 ms): 14

diskcache-kv-get-transact: Mean +- std dev: 1.37 ms +- 0.02 ms
Storage usage: 76KB std: 0KB
=====================
Raw value minimum: 115 ms
Raw value maximum: 131 ms

Number of calibration run: 1
Number of run with values: 20
Total number of run: 21

Number of warmup per run: 1
Number of value per run: 10
Loop iterations per value: 32
Total number of values: 200

Minimum:         3.59 ms
Median +- MAD:   3.72 ms +- 0.03 ms
Mean +- std dev: 3.74 ms +- 0.09 ms
Maximum:         4.08 ms

  0th percentile: 3.59 ms (-4% of the mean) -- minimum
  5th percentile: 3.60 ms (-4% of the mean)
 25th percentile: 3.69 ms (-1% of the mean) -- Q1
 50th percentile: 3.72 ms (-1% of the mean) -- median
 75th percentile: 3.76 ms (+1% of the mean) -- Q3
 95th percentile: 3.94 ms (+5% of the mean)
100th percentile: 4.08 ms (+9% of the mean) -- maximum

Number of outlier (out of 3.58 ms..3.87 ms): 29

dataset-kv-set: Mean +- std dev: 3.74 ms +- 0.09 ms
Storage usage: 83KB std: 79KB
=====================
Raw value minimum: 198 ms
Raw value maximum: 225 ms

Number of calibration run: 1
Number of run with values: 20
Total number of run: 21

Number of warmup per run: 1
Number of value per run: 10
Loop iterations per value: 512
Total number of values: 200

Minimum:         387 us
Median +- MAD:   394 us +- 3 us
Mean +- std dev: 396 us +- 7 us
Maximum:         439 us

  0th percentile: 387 us (-2% of the mean) -- minimum
  5th percentile: 388 us (-2% of the mean)
 25th percentile: 392 us (-1% of the mean) -- Q1
 50th percentile: 394 us (-1% of the mean) -- median
 75th percentile: 400 us (+1% of the mean) -- Q3
 95th percentile: 409 us (+3% of the mean)
100th percentile: 439 us (+11% of the mean) -- maximum

Number of outlier (out of 380 us..412 us): 6

dataset-kv-set-batch: Mean +- std dev: 396 us +- 7 us
Storage usage: 63KB std: 23KB
=====================
Raw value minimum: 110 ms
Raw value maximum: 121 ms

Number of calibration run: 1
Number of run with values: 20
Total number of run: 21

Number of warmup per run: 1
Number of value per run: 10
Loop iterations per value: 32
Total number of values: 200

Minimum:         3.43 ms
Median +- MAD:   3.54 ms +- 0.04 ms
Mean +- std dev: 3.55 ms +- 0.07 ms
Maximum:         3.78 ms

  0th percentile: 3.43 ms (-3% of the mean) -- minimum
  5th percentile: 3.45 ms (-3% of the mean)
 25th percentile: 3.50 ms (-1% of the mean) -- Q1
 50th percentile: 3.54 ms (-0% of the mean) -- median
 75th percentile: 3.57 ms (+1% of the mean) -- Q3
 95th percentile: 3.66 ms (+3% of the mean)
100th percentile: 3.78 ms (+6% of the mean) -- maximum

Number of outlier (out of 3.40 ms..3.68 ms): 10

dataset-kv-get: Mean +- std dev: 3.55 ms +- 0.07 ms
Storage usage: 136KB std: 67KB
=====================
Raw value minimum: 160 ms
Raw value maximum: 173 ms

Number of calibration run: 1
Number of run with values: 20
Total number of run: 21

Number of warmup per run: 1
Number of value per run: 10
Loop iterations per value: 1024
Total number of values: 200

Minimum:         156 us
Median +- MAD:   160 us +- 1 us
Mean +- std dev: 161 us +- 2 us
Maximum:         169 us

  0th percentile: 156 us (-3% of the mean) -- minimum
  5th percentile: 158 us (-2% of the mean)
 25th percentile: 159 us (-1% of the mean) -- Q1
 50th percentile: 160 us (-0% of the mean) -- median
 75th percentile: 161 us (+0% of the mean) -- Q3
 95th percentile: 166 us (+3% of the mean)
100th percentile: 169 us (+5% of the mean) -- maximum

Number of outlier (out of 155 us..165 us): 14

dataset-kv-get-range: Mean +- std dev: 161 us +- 2 us
Storage usage: 100KB std: 0KB
```
</details>

### Multi-key/value
```
peewee-mkv-serial-insert: Mean +- std dev: 220 ms +- 3 ms
peewee-mkv-serial-insert-transaction: Mean +- std dev: 177 ms +- 4 ms
peewee-mkv-batch-insert: Mean +- std dev: 33.7 ms +- 1.3 ms
peewee-mkv-batch-insert-indexed: Mean +- std dev: 35.5 ms +- 1.3 ms
peewee-mkv-serial-read: Mean +- std dev: 345 ms +- 3 ms
peewee-mkv-serial-read-indexed: Mean +- std dev: 349 ms +- 4 ms
peewee-mkv-raw-serial-read: Mean +- std dev: 16.9 ms +- 0.3 ms
peewee-mkv-raw-serial-read-indexed: Mean +- std dev: 16.9 ms +- 0.3 ms
peewee-mkv-batch-read: Mean +- std dev: 24.4 ms +- 0.4 ms
peewee-mkv-batch-read-indexed: Mean +- std dev: 24.7 ms +- 0.6 ms

diskcache-mkv-insert: Mean +- std dev: 111 ms +- 2 ms
diskcache-mkv-read: Mean +- std dev: 33.9 ms +- 0.4 ms
```

While peewee can be faster, for unbatched queries it's significantly slower; additionally raw SQL is ~20x faster.
Additionally in the process of making the benchmark I found significant footguns in the querying system used by peewee (invalid syntax being accepted).
