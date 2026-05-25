from climara.graphics._capabilities import graphics_capabilities


def main():
    caps = graphics_capabilities()

    print("climara graphics capabilities")
    print()

    for name, value in caps.__dict__.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()
