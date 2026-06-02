import logging
import subprocess
from typing import Callable, List, Optional
from src.context import ProjectContext
from src.schemas import ProcessingStatus

logger = logging.getLogger(__name__)

class AuditLoop:
    """
    Materializes the Agent Protocol from AGENTS.md into a coded interface.
    Ensures agents follow the Plan -> Execute -> Verify cycle.
    """

    def __init__(self, ctx: ProjectContext):
        self.ctx = ctx
        self._current_plan: Optional[str] = None
        self._execution_results = []

    def plan(self, from_status: ProcessingStatus, to_status: ProcessingStatus) -> None:
        """Step 1: State the intended transition."""
        self._current_plan = f"Transitioning images from {from_status} to {to_status}"
        logger.info(f"PLAN: {self._current_plan}")

    def execute_stage(self, stage_name: str, action: Callable[..., any], *args, **kwargs) -> any:
        """Step 3: Execute the change (Step 2 'Instrument' is implied by using this module)."""
        if not self._current_plan:
            raise RuntimeError("AuditLoop error: You must call .plan() before .execute_stage()")
        
        logger.info(f"EXECUTING: {stage_name}")
        try:
            result = action(*args, **kwargs)
            self._execution_results.append((stage_name, True))
            return result
        except Exception as e:
            logger.error(f"EXECUTION FAILED: {stage_name} - {e}")
            self._execution_results.append((stage_name, False))
            raise

    def verify(self, run_tests: bool = True) -> bool:
        """Step 4: Verify the results and system invariants."""
        logger.info("VERIFYING: Running system checks...")
        
        # 1. Check invariants (e.g., status consistency)
        for img_hash, meta in self.ctx.images.items():
            if meta.status == ProcessingStatus.PROCESSED and not meta.face_metrics:
                logger.error(f"Invariant Violation: Image {img_hash} is PROCESSED but has no FaceMetrics.")
                return False

        # 2. Run project tests if requested
        if run_tests:
            logger.info("Running 'make test'...")
            try:
                subprocess.run(["make", "test"], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Verification Failed: 'make test' exited with code {e.returncode}")
                logger.error(e.stderr.decode())
                return False

        logger.info("VERIFICATION PASSED.")
        return True

    def commit(self) -> None:
        """Finalize the loop by persisting state."""
        if not self._execution_results or not all(r[1] for r in self._execution_results):
            raise RuntimeError("AuditLoop error: Cannot commit failed or unexecuted stages.")
            
        self.ctx.save()
        logger.info("COMMIT: State persisted successfully.")
