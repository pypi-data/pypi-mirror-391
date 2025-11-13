# client.py
import warnings

warnings.warn(
    (
        "Deprecation Warning: `client` is deprecated and will not be supported "
        "after version 0.1.41 of vouchervision-go-client.\n"
        "Please switch to the new import style:\n"
        "    from VoucherVision import process_vouchers, process_vouchers_urls"
    ),
    DeprecationWarning,
    stacklevel=2,
)

from VoucherVision import (
    process_vouchers,
    process_vouchers_urls,
    process_image,
    process_image_file,
    process_image_by_url,
    save_results_to_xlsx,
    save_results_to_csv,
    main,  # keep CLI entry point working
)

__all__ = [
    "process_vouchers",
    "process_vouchers_urls",
    "process_image",
    "process_image_file",
    "process_image_by_url",
    "save_results_to_xlsx",
    "save_results_to_csv",
    "main",
]
