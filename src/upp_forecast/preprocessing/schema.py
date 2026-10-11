"""Schema contracts for preprocessing outputs."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ColumnSchema:
    name: str
    dtype: str
    nullable: bool = True


@dataclass(frozen=True, slots=True)
class TermCleaningSchema:
    academic_year_col: str = "ACADEMIC_YEAR"
    term_col: str = "TERM"
    raw_term_col: str = "raw_term"
    term_academic_year_col: str = "term_academic_year"
    teaching_period_label_col: str = "teaching_period_label"
    calendar_system_col: str = "calendar_system"
    term_order_col: str = "term_order"
    period_delta_col: str = "period_delta"
    period_start_fraction_col: str = "period_start_fraction"
    period_time_col: str = "period_time"
    term_key_col: str = "term_key"

    @property
    def required_input_columns(self) -> tuple[str, ...]:
        return (self.academic_year_col, self.term_col)

    @property
    def output_columns(self) -> tuple[str, ...]:
        return (
            self.raw_term_col,
            self.term_academic_year_col,
            self.teaching_period_label_col,
            self.calendar_system_col,
            self.term_order_col,
            self.period_delta_col,
            self.period_start_fraction_col,
            self.period_time_col,
            self.term_key_col,
        )

    @property
    def metadata_columns(self) -> tuple[str, ...]:
        return self.output_columns
