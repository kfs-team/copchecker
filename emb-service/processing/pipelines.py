import time
from typing import Dict, Any
from datetime import datetime, timezone

from loguru import logger

from .operators import Operator


class Pipeline:
    def __init__(self, *operators: Operator, output_field: str):
        self.operators = operators
        self.output_field = output_field

    def run(self, **data: Any):
        cache = data.copy()
        logger.info("Pipeline started for video ")
        cache['start_time'] = self.get_current_utc_time_iso()
        for i, operator in enumerate(self.operators, start=1):
            st_time = time.time()

            retval = operator.run(**cache)
            cache.update(retval)

            end_time = time.time()
            logger.info(
                f"[STEP {i}/{len(self.operators)}] {operator.__class__.__name__}: "
                f"Completed, execution time: {end_time - st_time:.2e} sec"
            )
        return cache[self.output_field]

    @staticmethod
    def get_current_utc_time_iso():
        now_utc = datetime.now(timezone.utc)
        iso_time_str = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        return iso_time_str
