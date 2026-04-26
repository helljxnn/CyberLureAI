from backend.app.schemas.analysis_signal import AnalysisSignal


BASE_RISK_SCORE = 5


def add_signal(
    signals: list[AnalysisSignal],
    code: str,
    severity: str,
    score: int,
    description: str,
) -> None:
    signals.append(
        AnalysisSignal(
            code=code,
            severity=severity,
            score=score,
            description=description,
        )
    )


def total_signal_score(signals: list[AnalysisSignal]) -> int:
    return sum(signal.score for signal in signals)
