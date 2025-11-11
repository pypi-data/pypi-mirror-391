from ._core import whoruv, format_python_info


def main() -> None:
    print(format_python_info(whoruv()))


if __name__ == "__main__":
    main()
