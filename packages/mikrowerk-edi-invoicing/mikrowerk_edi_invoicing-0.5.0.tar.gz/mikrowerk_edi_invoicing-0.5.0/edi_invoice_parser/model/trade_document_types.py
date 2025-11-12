from dataclasses import dataclass
from decimal import Decimal
import datetime

"""
UBL Document Type (XML Root)	Description	UNCL 1001 Code (Example)
"""

ubl_doc_codes = {
    "ApplicationResponse": ('ApplicationResponse', 431, 'Response to an application/message'),
    "Catalogue": ('Catalogue', 71, 'Product catalogue'),
    "CatalogueRequest": ('CatalogueRequest', 171, 'Catalogue request'),
    "CreditNote": ('CreditNote', 381, 'Commercial Credit note'),
    "DebitNote": ('DebitNote', 383, 'Debit note'),
    "DespatchAdvice": ('DespatchAdvice', 250, 'Despatch advice (Advance Ship Notice)'),
    "Invoice": ('Invoice', 380, 'Commercial Invoice'),
    "Order": ('Order', 220, 'Order'),
    "OrderChange": ('OrderChange', 222, 'Order change'),
    "OrderResponse": ('OrderResponse', 255, 'Order response (confirmation/rejection)'),
    "Quotation": ('Quotation', 83, 'Quotation'),
    "RequestForQuotation": ('RequestForQuotation', 135, 'Request for quotation'),
    "RemittanceAdvice": ('RemittanceAdvice', 256, 'Remittance advice'),
    "Statement": ('Statement', 86, 'Account statement / Balance confirmation'),
    "UtilityStatement": ('Utility statement', 490, 'Statement (electricity, gas, etc.)'),
}


@dataclass
class TradePartyAddress:
    post_code: str = None
    city_name: str = None
    country_id: str = None
    country_subdivision_id: str = None
    address_line_1: str = None
    address_line_2: str = None
    address_line_3: str = None


@dataclass
class TradePartyContact:
    name: str
    department_name: str = None
    telephone: str = None
    fax: str = None
    email: str = None


@dataclass
class TradeParty:
    name: str
    vat_registration_number: str = None
    fiscal_registration_number: str = None
    legal_registration_number: str = None
    address: TradePartyAddress = None
    contact: TradePartyContact = None


@dataclass
class AppliedTradeTax:
    name: str
    type_code: str = None
    category_code: str = None
    applicable_percent: Decimal = None
    basis_amount: Decimal = None
    calculated_amount: Decimal = None


@dataclass
class TradeLine:
    pos_number: int
    article_code: str = None
    name: str = None
    description: str = None
    quantity: Decimal = None
    unit_of_measure: str = None
    unit_price: Decimal = None
    total_net: Decimal = None
    tax: AppliedTradeTax = None
    total_amount: Decimal = None


@dataclass
class TradeCurrency:
    amount: Decimal
    currency_code: str


@dataclass
class BankAccount:
    iban: str
    bic: str = None
    name: str = None


@dataclass
class FinancialCard:
    id: str
    cardholder_name: str | None = None


@dataclass
class PaymentMeans:
    id: str = None
    type_code: str = None
    information: str = None
    financial_card: FinancialCard = None
    payee_account: BankAccount = None


@dataclass
class TradeDocument:
    """
    Model of a Trade Document
    """
    name: str
    doc_type_code: tuple  # Document Type Code: ubl_doc_codes
    doc_id: str = None
    issued_date_time: datetime = None  # 'Date'
    languages: str = None  # 'Languages'
    notes: str = None  # 'Notes'
    sender_reference: str = None  # 'Buyer Reference'
    receiver_reference: str = None
    dispatch_reference: str = None
    sales_order_reference: str = None
    sender: TradeParty = None
    receiver: TradeParty = None
    currency_code: str = None  # 'Currency Code'
    payment_means: PaymentMeans = None
    payment_terms: str = None  # 'Payment Terms'
    line_total_amount: Decimal = None  # 'Line Total Amount'
    charge_total_amount: Decimal = None  # 'Charge Total Amount'
    allowance_total_amount: Decimal = None  # 'Allowance Total Amount'
    tax_basis_total_amount: Decimal = None
    tax_total_amount: Decimal = None  # 'Tax Grand Total Amount'
    grand_total_amount: Decimal = None  # 'Grand Total Amount'
    total_prepaid_amount: Decimal = None  # 'Total Prepaid Amount'
    due_payable_amount: Decimal = None  # 'Due Payable Amount'
    trade_line_items: [TradeLine] = None
    applicable_trade_taxes: [AppliedTradeTax] = None
