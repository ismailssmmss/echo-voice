from app.runtime import get_default_model


def main() -> None:
    print(f"Echo Voice AI worker started. Default model: {get_default_model()}")


if __name__ == "__main__":
    main()
