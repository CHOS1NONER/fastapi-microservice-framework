from enum import IntEnum


class ProductStatus(IntEnum):
    SALE = 1
    OFFLINE = 2

    def is_sale(self):
        return self == ProductStatus.SALE
