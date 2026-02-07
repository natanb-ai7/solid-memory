"""
Validation utilities for lease program data.
"""
from dataclasses import dataclass
from typing import Iterable, List

from parsers.pdf_program import LeaseProgram


@dataclass
class ValidationIssue:
    message: str
    severity: str = "warning"


@dataclass
class ValidatedProgram:
    program: LeaseProgram
    issues: List[ValidationIssue]
    is_valid: bool


def validate_programs(programs: Iterable[LeaseProgram]) -> List[ValidatedProgram]:
    """
    Apply validation rules to a collection of lease programs.

    Rules enforced:
    - residual percent must be between 30 and 80
    - money factor must be below 0.01
    - MSRP must be positive
    """

    validated: List[ValidatedProgram] = []
    for program in programs:
        issues: List[ValidationIssue] = []

        if not 30 <= program.residual_percent <= 80:
            issues.append(
                ValidationIssue(
                    message=f"Residual {program.residual_percent} is outside 30-80%", severity="error"
                )
            )

        if program.money_factor >= 0.01:
            issues.append(ValidationIssue(message=f"Money factor {program.money_factor} >= 0.01", severity="error"))

        if program.msrp <= 0:
            issues.append(ValidationIssue(message="MSRP must be positive", severity="error"))

        validated.append(ValidatedProgram(program=program, issues=issues, is_valid=len(issues) == 0))

    return validated
