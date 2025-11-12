from typing import Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field
from datetime import datetime
from .base import BaseToolCallModel
import json


class Brand(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class MainCategoryParent(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    depth: Optional[int] = None
    parent: Optional[Dict[str, Any]] = None


class MainCategory(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    depth: Optional[int] = None
    parent: Optional[MainCategoryParent] = None
    exist_children: Optional[bool] = None
    product_count: Optional[int] = None
    order: Optional[int] = None
    status: Optional[int] = None
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None


class Merchant(BaseModel):
    id: Optional[Union[int, str]] = None
    name: Optional[str] = None
    logo: Optional[str] = None
    type: Optional[Dict[str, Any]] = None
    status: Optional[Dict[str, Any]] = None
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None


class Offer(BaseModel):
    id: Optional[Union[int, str]] = None
    original_price: Optional[Union[str, int, float]] = None
    price: Optional[Union[str, int, float]] = None
    three_month_price: Optional[Union[str, int, float]] = Field(
        default=None, alias="3_month_price"
    )
    six_month_price: Optional[Union[str, int, float]] = Field(
        default=None, alias="6_month_price"
    )
    nine_month_price: Optional[Union[str, int, float]] = Field(
        default=None, alias="9_month_price"
    )
    twelve_month_price: Optional[Union[str, int, float]] = Field(
        default=None, alias="12_month_price"
    )
    eighteen_month_price: Optional[Union[str, int, float]] = Field(
        default=None, alias="18_month_price"
    )
    discount: Optional[bool] = None
    discount_percent: Optional[Union[str, int, float]] = None
    discount_start_at: Optional[Union[datetime, str]] = None
    discount_expire_at: Optional[Union[datetime, str]] = None

    merchant: Optional[Merchant] = None
    status: Optional[Dict[str, Any]] = None
    market_type: Optional[
        Literal[
            "b2c",
            "b2b",
            "B2B",
            "B2C",
            "G2B",
            "G2C",
            "C2C",
            "C2B",
            "B2G",
            "G2G",
            "G2C",
            "g2b",
            "g2c",
            "c2c",
            "c2b",
            "b2g",
            "g2g",
            "g2c",
        ]
    ] = None

    def filter_for_llm(self):
        return {
            "price": self.price if self.price else None,
            "merchant": self.merchant.name if self.merchant else None,
            "status": self.status if self.status else None,
            "six_month_price": self.six_month_price if self.six_month_price else None,
            "twelve_month_price": (
                self.twelve_month_price if self.twelve_month_price else None
            ),
        }


class Meta(BaseModel):
    current_page: Optional[int] = Field(default=1, alias="current_page")
    from_: Optional[int] = Field(default=1, alias="from")
    last_page: Optional[int] = Field(default=1, alias="last_page")
    path: Optional[str] = Field(default=None, alias="path")
    per_page: Optional[int] = Field(default=1, alias="per_page")
    to: Optional[int] = Field(default=1, alias="to")
    total: Optional[int] = Field(default=1, alias="total")


class Installment(BaseModel):
    period: Optional[int] = None
    price: Optional[Union[str, int, float]] = None


class Price(BaseModel):
    is_active: Optional[bool] = None
    original: Optional[Union[str, int, float]] = None
    price: Optional[Union[str, int, float]] = None
    monthly: Optional[Union[str, int, float]] = None
    installments: Optional[list[Installment]] = None

    def filter_for_llm(self):
        return {
            "original": self.original if self.original else None,
            "price": self.price if self.price else None,
            "monthly": self.monthly if self.monthly else None,
            "installments": (
                [x.model_dump() for x in self.installments]
                if self.installments
                else None
            ),
        }


class ProductItem(BaseModel):
    id: Optional[Union[int, str]] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    offer_id: Optional[int] = None
    brand: Optional[Brand] = None
    category: Optional[MainCategory] = None
    short_name: Optional[str] = None
    images: Optional[Dict[str, str | list[str]]] = None
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None
    count: Optional[int] = None
    tracking: Optional[bool] = None
    offers: Optional[list[Offer]] = None
    price: Optional[Price] = None
    view_count: Optional[int] = None
    order_count: Optional[int] = None
    like_count: Optional[int] = None
    rate: Optional[int] = None
    cancelled_count: Optional[int] = None

    def filter_for_llm(self):
        return {
            "name": self.name if self.name else None,
            "brand": self.brand.name if self.brand else None,
            "price": self.price.filter_for_llm() if self.price else None,
        }


class SearchProductsResponse(BaseToolCallModel, BaseModel):
    products: Optional[list[ProductItem]] = None
    meta: Optional[Meta] = None

    def filter_for_llm(self):
        data = [x.filter_for_llm() for x in self.products] if self.products else []
        return json.dumps(data, ensure_ascii=False, indent=2)


class CartItemPrice(BaseModel):
    quantity: Optional[int] = None
    original: Optional[Union[str, int, float]] = None
    total_price: Optional[Union[str, int, float]] = None
    monthly: Optional[Union[str, int, float]] = None

    def filter_for_llm(self):
        return {
            "quantity": self.quantity if self.quantity else None,
            "original": self.original if self.original else None,
            "total_price": self.total_price if self.total_price else None,
            "monthly": self.monthly if self.monthly else None,
        }


class CartItem(BaseModel):
    offer_id: Optional[Union[int, str]] = None
    product_id: Optional[Union[int, str]] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    remote_id: Optional[str] = None
    image: Optional[str | Dict[str, str]] = None
    quantity: Optional[int] = None
    price: Optional[CartItemPrice] = None

    def filter_for_llm(self):
        return {
            "name": self.name if self.name else None,
            "quantity": self.quantity if self.quantity else None,
            "price": self.price.filter_for_llm() if self.price else None,
        }


class Shipping(BaseModel):
    method: Optional[int] = None
    price: Optional[Union[str, int, float]] = None
    address_id: Optional[Union[int, str]] = None
    address: Optional[str] = None
    pick_point_id: Optional[str] = None


class CartMerchant(BaseModel):
    id: Optional[Union[int, str]] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    logo: Optional[str] = None
    items: Optional[list[CartItem]] = None
    shipping: Optional[Shipping] = None

    def filter_for_llm(self):
        return {
            "id": self.id if self.id else None,
            "name": self.name if self.name else None,
            "items": [x.filter_for_llm() for x in self.items] if self.items else None,
            # "shipping": self.shipping.filter_for_llm() if self.shipping else None, # disable shipping info for now
        }


class CartTotal(BaseModel):
    total_product_quantity: Optional[int] = None
    total_product_price: Optional[Union[str, int, float]] = None
    total_insurance_price: Optional[Union[str, int, float]] = None
    total_price: Optional[Union[str, int, float]] = None
    installment_period: Optional[int] = None
    total_monthly_installment_price: Optional[Union[str, int, float]] = None
    total_shipping_price: Optional[Union[str, int, float]] = None

    def filter_for_llm(self):
        return {
            "total_product_quantity": (
                self.total_product_quantity if self.total_product_quantity else None
            ),
            "total_product_price": (
                self.total_product_price if self.total_product_price else None
            ),
        }


class CartData(BaseModel):
    merchants: Optional[list[CartMerchant]] = None
    total: Optional[CartTotal] = None

    def filter_for_llm(self):
        return {
            "merchants": (
                [x.filter_for_llm() for x in self.merchants] if self.merchants else None
            ),
            "total": self.total.filter_for_llm() if self.total else None,
        }


class CartResponse(BaseToolCallModel, BaseModel):
    status: Optional[int] = None
    message: Optional[str] = None
    data: Optional[CartData] = None

    def filter_for_llm(self):
        return {"data": self.data.filter_for_llm() if self.data else None}
