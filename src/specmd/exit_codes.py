"""Exit Status Contract (SPECMD_CLI_ICD.md section 10)."""

SUCCESS = 0
FINDINGS = 1
USAGE_ERROR = 2
INPUT_ERROR = 3
CAPABILITY_UNAVAILABLE = 4
WRITE_ERROR = 5
INTERNAL_ERROR = 6

# ICD-EXIT-001: exit status and JSON `status` must be consistent.
STATUS_TO_EXIT = {
    "succeeded": SUCCESS,
    "findings": FINDINGS,
    "indeterminate": INPUT_ERROR,
    "failed": INTERNAL_ERROR,
}
