# Quick TSBS

Scripts to run TSBS easier :D

# Quick Start
1. Clone this project and initialize submodules.

    ```
    cd quick-tsbs
    git submodule update --init --recursive
    ```

2. Build TSBS and generate data for benchmarks.

    ```
    python3 main.py generate
    ```

    This command puts all generated assets under `./workspace` directory. We call `./workspace` the `$WORKSPACE` directory.

3. Start greptimedb. You need to build and run greptimedb manually.
    ```
    cargo run --release -- standalone start
    ```

4. Bench greptimedb.
    ```
    python3 main.py greptime
    ```
    Note that you need to clean greptimedb's data directory manually before benchmark.


# Configuration
You could modify `$WORKSPACE/tsbs_load_greptime_config.yaml` to overwrite the default benchmark configuration.

Only the following configurations can take effect:
```yaml
data-source:
  file:
    location: ./file-from-tsbs-generate-data
loader:
  db-specific:
    gzip: true
    urls: http://localhost:8086
  runner:
    batch-size: "10000"
    workers: "1"
```
