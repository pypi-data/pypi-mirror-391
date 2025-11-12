"""Allow hdc_installer to be executable through `python -m hdc_installer`."""

from .cli import main

if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
