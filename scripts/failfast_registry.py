import logging


class FailFastRegistry:

    def __init__(self):
        self.stages = []

    def register(self, stage_name: str):
        self.stages.append(stage_name)

    def enforce(self, stage_name: str):
        if stage_name not in self.stages:
            raise RuntimeError(
                f"Stage '{stage_name}' not registered in failfast registry."
            )

    def wrap(self, stage_name, func):
        self.register(stage_name)

        def wrapper(*args, **kwargs):
            try:
                logging.info(f"[START] {stage_name}")
                result = func(*args, **kwargs)
                logging.info(f"[END] {stage_name}")
                return result
            except Exception as e:
                logging.error(f"[FAIL] {stage_name}: {str(e)}")
                raise RuntimeError(
                    f"Fail-fast halt at '{stage_name}'"
                )
        return wrapper
