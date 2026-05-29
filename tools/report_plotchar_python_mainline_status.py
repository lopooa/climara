from __future__ import annotations


def main():
    print("climara Plotchar implementation direction")
    print("========================================")
    print()
    print("Mainline:")
    print("- Read complete NCL/HLU/GSN source semantics.")
    print("- Reimplement the semantics in Python inside climara.")
    print("- Keep unsupported PLCHHQ/font/function-code/Down-text behavior guarded.")
    print()
    print("Not mainline:")
    print("- Requiring users to install or compile NCL/NCAR Graphics libraries.")
    print("- Treating ctypes/shared-library access as required runtime behavior.")
    print("- Using fixed-width, character-count, SVG text metrics, browser metrics, or visual tuning.")
    print()
    print("Current Python implementation boundary:")
    print("- Python PCSETI / PCSETR / PCSETC / PCGETR state model is implemented for the TextItem measurement parameters.")
    print("- Python PLCHHQ text-extent computation is still guarded and must be mapped from the NCL source before being enabled.")


if __name__ == "__main__":
    main()
