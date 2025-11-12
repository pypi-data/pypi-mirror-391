from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any
from .base import BaseToolCallModel
import json


class Category(BaseModel):
    id: Union[int, str] = Field(default=0)
    name: str = Field(default="")
    imagePath: Optional[str] = None
    s3Url: Optional[str] = None

    def filter_for_llm(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Supplier(BaseModel):
    id: Union[int, str] = Field(default=0)
    name: str = Field(default="")
    categoryId: Union[int, str] = Field(default=0)
    s3Url: Optional[str] = Field(default="")

    def filter_for_llm(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Value(BaseModel):
    value: int
    name: str

    def filter_for_llm(self):
        return {
            "value": self.value,
            "name": self.name,
        }


class FieldOptions(BaseModel):
    identName: str = Field(default="")
    name: str = Field(default="")
    order: int = Field(default=0)
    type: str = Field(default="")
    pattern: Optional[str] = None
    minValue: Optional[int] = None
    maxValue: Optional[int] = None
    fieldSize: Optional[int] = None
    isMain: Optional[bool] = None
    valueList: Optional[List[Value]] = None

    def filter_for_llm(self):
        return {
            "identName": self.identName,
            "name": self.name,
            "order": self.order,
            "type": self.type,
            "pattern": self.pattern if self.pattern else None,
            "minValue": self.minValue if self.minValue else None,
            "maxValue": self.maxValue if self.maxValue else None,
            "fieldSize": self.fieldSize if self.fieldSize else None,
            "isMain": self.isMain if self.isMain else None,
            "valueList": [x.filter_for_llm() for x in self.valueList]
            if self.valueList
            else [],
        }


class Response(BaseModel):
    payload: List[Category] = Field(default_factory=list)
    code: Optional[Union[int, str]] = Field(default=None)


class SuppliersField(Response):
    checkUp: bool = Field(default=False)
    checkUpWithResponse: bool = Field(default=False)
    checkUpAfterPayment: bool = Field(default=False)
    fieldList: List[FieldOptions] = Field(default_factory=list)


class SupplierFieldsResponse(BaseToolCallModel, Response):
    payload: SuppliersField = Field(default_factory=SuppliersField)

    def filter_for_llm(self):
        return json.dumps(
            self.payload.filter_for_llm(),
            ensure_ascii=False,
            indent=2,
        )


class SupplierByCategoryResponse(BaseToolCallModel, Response):
    payload: List[Supplier] = Field(default_factory=list)

    def filter_for_llm(self):
        return json.dumps(
            [x.filter_for_llm() for x in self.payload],
            ensure_ascii=False,
            indent=2,
        )


class CategoriesResponse(BaseToolCallModel, Response):
    payload: List[Category] = Field(default_factory=list)

    def filter_for_llm(self):
        return json.dumps(
            [x.filter_for_llm() for x in self.payload],
            ensure_ascii=False,
            indent=2,
        )


class ClientDetails(BaseModel):
    clientId: str
    phoneNumber: str


class FinanceDetails(BaseModel):
    paymentToken: str
    expiryDate: str
    paymentSystem: str
    bankCode: str
    mfo: str


class OperationDetails(BaseModel):
    type: str


class PaymentDetails(BaseModel):
    amount: str
    categoryId: str
    currency: str


class SupplierDetails(BaseModel):
    supplierId: str
    regionId: str
    paymentNo: str
    paymentNo1: str
    paymentNo2: str
    paymentNo3: str
    paymentNo4: str


class PaymentManagerPaymentRequest(BaseModel):
    """
    Payment Manager Payment Request
        endpoint: /retail/payment-manager/paynet/v1/payment
    """

    clientDetails: ClientDetails
    financeDetails: FinanceDetails
    operationDetails: OperationDetails
    paymentDetails: PaymentDetails
    paymentServiceProvider: str
    supplierDetails: SupplierDetails


class ResponseItem(BaseModel):
    name: str
    value: str
    type: str
    order: int

    def filter_for_llm(self):
        return str(
            {
                "name": self.name,
                "value": self.value,
            }
        )


class OfdDetails(BaseModel):
    qr: str
    receiptType: str
    terminalId: str
    chequeId: str
    fiscalSign: str

    def filter_for_llm(self):
        return str(
            {
                "receiptType": self.receiptType,
            }
        )


class PaymentData(BaseModel):
    id: str
    transactionId: str
    response: list[ResponseItem]
    ofd: OfdDetails

    def filter_for_llm(self):
        return str(
            {
                "response": [x.filter_for_llm() for x in self.response],
                "ofd": self.ofd.filter_for_llm(),
            }
        )


class PaymentManagerPaymentResponse(BaseModel):
    """
    Payment Manager Payment Response
        endpoint: /retail/payment-manager/paynet/v1/payment
    """

    data: PaymentData

    def filter_for_llm(self):
        return str(self.data.filter_for_llm())


class Detail(BaseModel):
    id: int
    phoneNumber: str
    language: str
    category: str
    supplierId: str
    paymentNo: str
    paymentNo1: Optional[str]
    paymentNo2: Optional[str]
    paymentNo3: Optional[str]
    paymentNo4: Optional[str]
    regionId: Optional[str]
    detailImage: Optional[str]
    supplierName: str
    checkUp: bool
    isMobile: Optional[Any]
    isMain: Optional[str]
    thresholdAmount: Optional[int]

    def filter_for_llm(self):
        return str(
            {
                "id": self.id,
                "category": self.category,
                "supplierId": self.supplierId,
                "paymentNo": self.paymentNo,
                "paymentNo1": self.paymentNo1,
                "paymentNo2": self.paymentNo2,
                "paymentNo3": self.paymentNo3,
                "paymentNo4": self.paymentNo4,
                "supplierName": self.supplierName,
                "thresholdAmount": self.thresholdAmount,
            }
        )


class Home(BaseModel):
    id: int
    clientId: str
    name: str
    homeImage: Optional[str]
    isVisible: bool
    details: List[Detail]

    def filter_for_llm(self):
        return str(
            {
                "id": self.id,
                "name": self.name,
                "isVisible": self.isVisible,
                "details": [x.filter_for_llm() for x in self.details],
            }
        )


class RetailHomeResponse(BaseModel):
    status: str
    workflowId: str
    body: List[List[Home]]

    def filter_for_llm(self):
        if self.status == "COMPLETED":
            output = {"status": "success", "data": []}
            for body in self.body:
                body_values = []
                for x in body:
                    body_values.append(x.filter_for_llm())
                output["data"].append(body_values)
            return str(output)
        else:
            return "Error getting home utility suppliers: " + self.status


class RetailHomeRequest(BaseModel):
    clientId: str


if __name__ == "__main__":
    import sys
    import os

    sys.path.append(os.getcwd())
    from tests.cache_responses import (
        supplier_fields_response,
        suppliers_list_response,
    )

    a = SupplierByCategoryResponse(**suppliers_list_response)
    b = SupplierFieldsResponse(**supplier_fields_response)
    print(a)
    print(b)
