import json
import logging
import platform
import time
import uuid

import awkward as ak
import coffea
from coffea import processor
from coffea.nanoevents import NanoAODSchema

from .cluster_manager import ClusterManager
from .processor import TriggerProcessor

logger = logging.getLogger(__name__)


class TriggerLoader:
    def __init__(self,
        sample_json: str,
        transform: callable,
        output_path: str,
    ):
        self.transform = transform
        self.fileset = self._load_sample_json(sample_json)
        self.output_path = output_path
        self.run_uuid = str(uuid.uuid4())

    def _build_processor(self):
        run_meta = {
            "run_uuid": self.run_uuid,
            "fileset_size": sum(len(v) if isinstance(v, list) else 1 for v in self.fileset.values()),
            "coffea_version": coffea.__version__,
            "awkward_version": ak.__version__,
            "python_version": platform.python_version(),
        }

        return TriggerProcessor(
            output_path=self.output_path,
            transform=self.transform,
            compression="zstd",
            add_uuid=False,
            run_uuid=self.run_uuid,
            run_metadata=run_meta,
        )

    def _load_sample_json(self, sample_json: str) -> dict:
        with open(sample_json) as f:
            return json.load(f)

    def _write_run_metadata_file(self, path: str, duration_s: float | None = None):
        meta_path = f"{path}/run_metadata.json"
        data = {
            "run_uuid": self.run_uuid,
            "duration_seconds": duration_s,
        }
        with open(meta_path, "w") as f:
            json.dump(data, f, indent=2)

    def _run(self, runner: processor.Runner, label: str):
        logger.log(f"Starting processing ({label})...")
        start = time.time()
        proc = self._build_processor()
        acc = runner(
            self.fileset,
            treename="Events",
            processor_instance=proc
        )
        elapsed = time.time() - start
        self._write_run_metadata_file(self.output_path, elapsed)
        logger.log(f"Finished in {elapsed:.2f}s (run_uuid={self.run_uuid})")
        return acc

    def run_distributed(self, cluster_type: str, cluster_config: dict,
                        chunksize: int = 100_000, jobs: int = 1):
        with ClusterManager(cluster_type, cluster_config, jobs) as client:
            executor = processor.DaskExecutor(client=client)
            runner = processor.Runner(
                executor=executor,
                schema=NanoAODSchema,
                chunksize=chunksize
            )
            self._run(runner, f"Distributed ({cluster_type})")

    def run_local(self, num_workers: int = 4, chunksize: int = 100_000):
        """
        Run processing locally using a multi-processing executor.
        """
        executor = processor.FuturesExecutor(workers=num_workers)
        runner = processor.Runner(
            executor=executor,
            schema=NanoAODSchema,
            chunksize=chunksize
        )
        self._run(runner, f"Local ({num_workers} workers)")
