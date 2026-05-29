from climara.graphics._plotchar_legacy_digitization import (
    ASCII_TO_DPC_INDEX,
    IFGR,
    IFRO,
    ICSL,
    ICSU,
    ISZC,
    ISZI,
    ISZP,
    SPIC,
    legacy_digitization_index,
)


def main():
    print("NCL legacy Plotchar digitization constants")
    print("IFRO:", IFRO)
    print("IFGR:", IFGR)
    print("ISZP/ISZI/ISZC:", ISZP, ISZI, ISZC)
    print("ICSU/ICSL:", ICSU, ICSL)
    print("SPIC:", SPIC)
    print()

    print("DPC A:", ASCII_TO_DPC_INDEX[ord("A")])
    print("DPC a:", ASCII_TO_DPC_INDEX[ord("a")])
    print("DPC 0:", ASCII_TO_DPC_INDEX[ord("0")])
    print()

    roman_a = legacy_digitization_index(
        "A",
        font_family="roman",
        size_level="principal",
        case_mode="upper",
    )
    greek_a = legacy_digitization_index(
        "A",
        font_family="greek",
        size_level="principal",
        case_mode="upper",
    )
    roman_indexical_a = legacy_digitization_index(
        "A",
        font_family="roman",
        size_level="indexical",
        case_mode="upper",
    )
    roman_cartographic_a = legacy_digitization_index(
        "A",
        font_family="roman",
        size_level="cartographic",
        case_mode="upper",
    )
    roman_lower_a = legacy_digitization_index(
        "a",
        font_family="roman",
        size_level="principal",
        case_mode="lower",
    )

    print("roman principal upper A:", roman_a)
    print("greek principal upper A:", greek_a)
    print("roman indexical upper A:", roman_indexical_a)
    print("roman cartographic upper A:", roman_cartographic_a)
    print("roman principal lower a:", roman_lower_a)

    assert roman_a == IFRO + ISZP + ICSU + ASCII_TO_DPC_INDEX[ord("A")]
    assert greek_a == IFGR + ISZP + ICSU + ASCII_TO_DPC_INDEX[ord("A")]
    assert roman_indexical_a == IFRO + ISZI + ICSU + ASCII_TO_DPC_INDEX[ord("A")]
    assert roman_cartographic_a == IFRO + ISZC + ICSU + ASCII_TO_DPC_INDEX[ord("A")]
    assert roman_lower_a == IFRO + ISZP + ICSL + ASCII_TO_DPC_INDEX[ord("a")]

    print()
    print("✅ legacy digitization offset demo passed")


if __name__ == "__main__":
    main()
