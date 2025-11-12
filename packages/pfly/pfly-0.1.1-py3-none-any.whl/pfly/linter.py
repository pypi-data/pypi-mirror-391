from pathlib import Path
from typing import List, Dict, Optional
import yaml
from pfly.policies.exception_exc_info import ExceptionExcInfoPolicy
from pfly.policies.log_loop import LogLoopPolicy
from pfly.file_collector import FileCollector
from pfly.violation import Violation


class Linter:
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.logger_names = self.config.get(
            "logger_names", ["logging", "logger", "log"]
        )
        self.file_collector = FileCollector(self.config)

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        if config_path and config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def lint(self, path: Path) -> List[Violation]:
        files = self.file_collector.collect_files(path)
        return self._lint_sequential(files)

    def _lint_sequential(self, files: List[Path]) -> List[Violation]:
        violations = []
        for file_path in files:
            violations.extend(self._lint_file(file_path))
        return violations

    def _lint_parallel(self, files: List[Path], jobs: int) -> List[Violation]:
        # TODO: Implement parallel linting using ProcessPoolExecutor
        return self._lint_sequential(files)

    def _lint_file(self, file_path: Path) -> List[Violation]:
        violation_dicts = []

        try:
            with open(file_path) as f:
                code = f.read()

            if "exception_exc_info" in self.config:
                policy_config = self.config["exception_exc_info"]
                levels = policy_config.get("levels", ["error"])
                violation_dicts.extend(
                    ExceptionExcInfoPolicy.check(
                        code, file_path, levels, self.logger_names
                    )
                )

            if "log_loop" in self.config:
                policy_config = self.config["log_loop"]
                levels = policy_config.get("levels", ["info", "debug"])
                violation_dicts.extend(
                    LogLoopPolicy.check(code, file_path, levels, self.logger_names)
                )

        except Exception:
            pass

        # Convert dicts to Violation objects
        return [Violation.from_dict(v) for v in violation_dicts]