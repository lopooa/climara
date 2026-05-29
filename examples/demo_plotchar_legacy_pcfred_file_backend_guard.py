from pathlib import Path
from tempfile import TemporaryDirectory

from climara.graphics._plotchar_legacy_pcfred_file_backend import (
    LegacyPcfredFileBackend,
)
from climara.graphics._plotchar_legacy_pcfred_provider import (
    LegacyPcfredDataProvider,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        inda = root / "demo_inda.dat"
        idda = root / "demo_idda.dat"

        inda.write_bytes(b"demo inda placeholder")
        idda.write_bytes(b"demo idda placeholder")

        backend = LegacyPcfredFileBackend.from_paths(
            inda_path=inda,
            idda_path=idda,
        )

        provider = LegacyPcfredDataProvider(
            backend=backend,
        )

        try:
            provider.record_for_inda_index(385)
        except PlotcharUnsupportedError as exc:
            print("file-backed PCFRED read guarded:")
            print(exc)
        else:
            raise AssertionError(
                "file-backed PCFRED backend should remain guarded until record layout is decoded"
            )

        missing_backend = LegacyPcfredFileBackend.from_paths(
            inda_path=root / "missing_inda.dat",
            idda_path=idda,
        )

        missing_provider = LegacyPcfredDataProvider(
            backend=missing_backend,
        )

        try:
            missing_provider.record_for_inda_index(385)
        except PlotcharUnsupportedError as exc:
            print()
            print("missing INDA resource guarded:")
            print(exc)
        else:
            raise AssertionError("missing INDA resource should be guarded")

    print()
    print("✅ legacy PCFRED file backend guard demo passed")


if __name__ == "__main__":
    main()
