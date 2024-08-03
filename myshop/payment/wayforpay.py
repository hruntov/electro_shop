import requests
import hashlib
import hmac
import json
from random import randint
import time
from typing import Optional, List, Dict


API_URL = 'https://api.wayforpay.com/api'


class InvoiceCreateResult:
    def __init__(self, invoice_url, reason, reason_code, qr_code, orderReference):
        self.invoiceUrl = invoice_url
        self.reason = reason
        self.reasonCode = reason_code
        self.qrCode = qr_code
        self.orderReference = orderReference

    def json(self):
        return self.__dict__


class InvoiceStatusResult:
    def __init__(self, response_dict: Dict, reason: str, reasonCode: Optional[str],
                 orderReference: str, amount: str, currency: str, authCode: Optional[str],
                 createdDate: Optional[str], processingDate: Optional[str], cardPan: Optional[str],
                 cardType: Optional[str], issuerBankCountry: Optional[str],
                 issuerBankName: Optional[str], transactionStatus: Optional[str],
                 refundAmount: Optional[str], settlementDate: Optional[str],
                 settlementAmount: Optional[str], fee: Optional[str],
                 merchantSignature: Optional[str]):
        """
        Initializes the InvoiceStatusResult class.

        Args:
            response_dict (Dict): The response dictionary from the API.
            reason (str): The reason for any error that occurred.
            reasonCode (Optional[str]): The reason code for any error that occurred.
            orderReference (str): The order reference number.
            amount (str): The amount of the transaction.
            currency (str): The currency of the transaction.
            authCode (Optional[str]): The authorization code of the transaction.
            createdDate (Optional[str]): The creation date of the invoice.
            processingDate (Optional[str]): The processing date of the transaction.
            cardPan (Optional[str]): The card number used in the transaction.
            cardType (Optional[str]): The type of the card used.
            issuerBankCountry (Optional[str]): The country of the issuer bank.
            issuerBankName (Optional[str]): The name of the issuer bank.
            transactionStatus (Optional[str]): The status of the transaction.
            refundAmount (Optional[str]): The refunded amount.
            settlementDate (Optional[str]): The settlement date.
            settlementAmount (Optional[str]): The settlement amount.
            fee (Optional[str]): The fee for the transaction.
            merchantSignature (Optional[str]): The merchant's signature.

        """
        self.response_dict = response_dict
        self.reason = reason
        self.reasonCode = reasonCode
        self.orderReference = orderReference
        self.amount = amount
        self.currency = currency
        self.authCode = authCode
        self.createdDate = createdDate
        self.processingDate = processingDate
        self.cardPan = cardPan
        self.cardType = cardType
        self.issuerBankCountry = issuerBankCountry
        self.issuerBankName = issuerBankName
        self.transactionStatus = transactionStatus
        self.refundAmount = refundAmount
        self.settlementDate = settlementDate
        self.settlementAmount = settlementAmount
        self.fee = fee
        self.merchantSignature = merchantSignature

    def json(self):
        return self.__dict__


class WayForPay:
    def __init__(self, key, domain_name):
        self.__key = key
        self.__domain_name = domain_name

    def hash_md5(self, string):
        hash_result = hmac.new(
            self.__key.encode('utf-8'),
            string.encode('utf-8'),
            hashlib.md5
        ).hexdigest()

        return hash_result

    def create_invoice(self, merchantAccount, merchantAuthType, amount, currency, *args, **kwargs):
        orderReference = f"DH{randint(1000000000, 9999999999)}"
        orderDate = int(time.time())

        productNames = kwargs.get('productNames', [])
        productPrices = kwargs.get('productPrices', [])
        productCounts = kwargs.get('productCounts', [])

        product_names_data = ';'.join(map(str, productNames))
        product_counts_data = ';'.join(map(str, productCounts))
        product_prices_data = ';'.join(map(str, productPrices))

        string = f'{merchantAccount};{self.__domain_name};{orderReference};{orderDate};{amount};{currency};{product_names_data};{product_counts_data};{product_prices_data}'

        params = {
            "transactionType": "CREATE_INVOICE",
            "merchantSecretKey": self.__key,
            "merchantAccount": merchantAccount,
            "merchantAuthType": merchantAuthType,
            "merchantDomainName": self.__domain_name,
            "merchantSignature": self.hash_md5(string),
            "apiVersion": "1",
            "orderReference": orderReference,
            "orderDate": orderDate,
            "amount": amount,
            "currency": currency,
            "productName": productNames,
            "productPrice": productPrices,
            "productCount": productCounts,
        }

        try:
            result = requests.post(url=API_URL, json=params)
            response_dict = json.loads(result.text)

            invoice_url = response_dict["invoiceUrl"]
            reason = response_dict.get("reason", None)
            reason_code = response_dict.get("reasonCode", None)
            qr_code = response_dict.get("qrCode", None)

            return InvoiceCreateResult(invoice_url, reason, reason_code, qr_code, orderReference)

        except Exception as e:
            print(f'Error: {e}')
            return False

    def check_invoice(self, merchantAccount, orderReference):
        apiVersion = '1'
        string = f"{merchantAccount};{orderReference}"

        params = {
            "transactionType": "CHECK_STATUS",
            "merchantSecretKey": self.__key,
            "merchantAccount": merchantAccount,
            "orderReference": orderReference,
            "merchantSignature": self.hash_md5(string),
            "apiVersion": apiVersion
        }

        try:
            result = requests.post(url=API_URL, json=params)

            if result.status_code == 200:
                response_dict = json.loads(result.text)
                reason = response_dict["reason"]
                reasonCode = response_dict.get("reasonCode", None)
                orderReference = response_dict.get("orderReference", None)
                amount = response_dict.get("amount", None)
                currency = response_dict.get("currency", None)
                authCode = response_dict.get("authCode", None)
                createdDate = response_dict.get("createdDate", None)
                processingDate = response_dict.get("processingDate", None)
                cardPan = response_dict.get("cardPan", None)
                cardType = response_dict.get("cardType", None)
                issuerBankCountry = response_dict.get("issuerBankCountry", None)
                issuerBankName = response_dict.get("issuerBankName", None)
                transactionStatus = response_dict.get("transactionStatus", None)
                refundAmount = response_dict.get("refundAmount", None)
                settlementDate = response_dict.get("settlementDate", None)
                settlementAmount = response_dict.get("settlementAmount", None)
                fee = response_dict.get("fee", None)
                merchantSignature = response_dict.get("merchantSignature", None)

                return InvoiceStatusResult(response_dict, reason, reasonCode, orderReference, amount, currency, authCode, createdDate, processingDate, cardPan, cardType, issuerBankCountry, issuerBankName, transactionStatus, refundAmount, settlementDate, settlementAmount, fee, merchantSignature)

        except Exception as e:
            print(f'Error: {e}')
            return None

    def delete_invoice(self, merchantAccount, orderReference):
        try:
            apiVersion = '1'
            string = f"{merchantAccount};{orderReference}"
            params = {
                "transactionType": "REMOVE_INVOICE",
                "merchantSecretKey": self.__key,
                "merchantAccount": merchantAccount,
                "orderReference": orderReference,
                "merchantSignature": self.hash_md5(string),
                "apiVersion": apiVersion
            }
            result = requests.post(url=API_URL, json=params)

            if result.status_code == 200:
                return True

        except Exception as e:
            print(f'Error: {e}')
            return None

    def generate_signature(self, data):
        message = ';'.join(data).encode('utf-8')
        return hmac.new(self.__key.encode('utf-8'), message, hashlib.md5).hexdigest()
