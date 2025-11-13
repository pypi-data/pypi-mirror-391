import sys
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen, TimeoutExpired

from experl.utils.logging_utils import get_logger


log = get_logger(__name__)


class ProcessRunner:

    @staticmethod
    def run_stage(
        stage_name: str, script_path: str, args: list, timeout: int = 5
    ) -> int:
        stage_name = stage_name or Path(script_path).stem
        command = [sys.executable, "-m", script_path] + args
        log.info(f"\nStarting stage: {stage_name}")
        log.info(f"Command: {' '.join(command)}")

        try:
            with Popen(
                command,
                stdout=PIPE,
                stderr=STDOUT,
                text=True,
                bufsize=1,
            ) as process:
                for line in process.stdout:
                    log.info(f"[{stage_name}] {line.strip()}")

                if process.stderr is not None:
                    for err_line in process.stderr:
                        log.error(f"[{stage_name}][stderr] {err_line.strip()}")

                process.wait(timeout=timeout)
                return_code = process.returncode

                if return_code == 0:
                    log.info(f"Stage '{stage_name}' completed successfully.")
                else:
                    error_msg = (
                        f"Stage '{stage_name}' failed with return code {return_code}."
                    )
                    log.error(error_msg)
                    raise Exception(error_msg)

                return return_code

        except TimeoutExpired as ex:
            log.error(f"Stage '{stage_name}' timed out after {timeout} seconds.")
            raise ex
        except FileNotFoundError as ex:
            log.error(f"Script not found: {script_path} - Error : {ex}")
            raise ex
        except KeyboardInterrupt:
            log.warning(f"Stage '{stage_name}' interrupted by user.")
            process.terminate()
            return 130
        except Exception as ex:
            log.error(f"Unexpected error during stage '{stage_name}': {ex}")
            raise ex
        finally:
            if process and process.poll() is None:
                process.kill()
                log.warning(f"Force-killed process for stage '{stage_name}'.")
