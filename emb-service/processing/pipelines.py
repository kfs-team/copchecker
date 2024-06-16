import time
from typing import Dict, Any

from loguru import logger

from .operators import Operator


class Pipeline:
    def __init__(self, *operators: Operator, output_field: str):
        self.operators = operators
        self.output_field = output_field

    def run(self, **data: Any):
        cache = data.copy()
        logger.info("Pipeline started for video ")
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
