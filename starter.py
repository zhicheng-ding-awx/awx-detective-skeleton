import asyncio
import json
import signal
import ssl
from dataclasses import dataclass
from typing import Tuple, TypedDict

import certifi
import requests
import websockets
from print_color import print

# ========================== #
# Fill in your details here  #
# ========================== #
USERNAME = ""
PASSWORD = ""
# ========================== #
# Fill in your details here  #
# ========================== #

currenciesDict = {
    "USDUSD": 1.000000000,
    "EURUSD": 1.080000000,
    "JPYUSD": 0.006700000,
    "GBPUSD": 1.270000000,
    "AUDUSD": 0.660000000,
    "CADUSD": 0.740000000,
    "CHFUSD": 1.100000000,
    "CNYUSD": 0.140000000,
    "SEKUSD": 0.093000000,
    "NZDUSD": 0.610000000,
    "MXNUSD": 0.058000000,
    "SGDUSD": 0.740000000,
    "HKDUSD": 0.130000000,
    "NOKSGD": 0.124324324,
    "NOKSEK": 0.989247312,
    "KRWAUD": 0.001136364,
    "KRWCAD": 0.001013514,
    "TRYCNY": 0.221428571,
    "INRCNY": 0.085714286,
    "INRKRW": 16.000000000,
    "BRLKRW": 253.333333333,
    "BRLMXN": 3.275862069,
    "ZARHKD": 0.407692308,
    "RUBMXN": 0.189655172,
    "DKKBRL": 0.736842105,
    "DKKCAD": 0.189189189,
    "PLNINR": 20.833333333,
    "PLNHKD": 1.923076923,
    "THBKRW": 36.000000000,
    "THBPLN": 0.108000000,
    "IDRZAR": 0.001169811,
    "IDRCAD": 0.000083784,
    "HUFTRY": 0.090322581,
    "HUFSEK": 0.030107527,
    "CZKMXN": 0.741379310,
    "CZKINR": 3.583333333,
    "ILSSGD": 0.364864865,
    "CLPMXN": 0.018965517,
    "CLPINR": 0.091666667,
    "PHPKRW": 24.000000000,
    "PHPCZK": 0.418604651,
    "AEDCHF": 0.245454545,
    "AEDINR": 22.500000000,
    "COPRUB": 0.023636364,
    "SARZAR": 5.094339623,
    "SARCAD": 0.364864865,
    "MYRINR": 17.500000000,
    "MYRRUB": 19.090909091,
    "RONPLN": 0.880000000,
    "RONHUF": 78.571428571,
    "PENRON": 1.227272727,
    "PENTHB": 10.000000000,
    "ARSEUR": 0.001111111,
    "EGPPEN": 0.077777778,
    "NGNCAD": 0.000905405,
    "BDTCZK": 0.211627907,
    "BDTMYR": 0.043333333,
    "VNDTHB": 0.001444444,
    "USDEUR": 0.925925926,
    "USDJPY": 149.253731343,
    "USDGBP": 0.787401575,
    "USDAUD": 1.515151515,
    "USDCAD": 1.351351351,
    "USDCHF": 0.909090909,
    "USDCNY": 7.142857143,
    "USDSEK": 10.752688172,
    "USDNZD": 1.639344262,
    "USDMXN": 17.241379310,
    "USDSGD": 1.351351351,
    "USDHKD": 7.692307692,
    "SGDNOK": 8.043478261,
    "SEKNOK": 1.010869565,
    "AUDKRW": 880.000000000,
    "CADKRW": 986.666666667,
    "CNYTRY": 4.516129032,
    "CNYINR": 11.666666667,
    "KRWINR": 0.062500000,
    "KRWBRL": 0.003947368,
    "MXNBRL": 0.305263158,
    "HKDZAR": 2.452830189,
    "MXNRUB": 5.272727273,
    "BRLDKK": 1.357142857,
    "CADDKK": 5.285714286,
    "INRPLN": 0.048000000,
    "HKDPLN": 0.520000000,
    "KRWTHB": 0.027777778,
    "PLNTHB": 9.259259259,
    "ZARIDR": 854.838709677,
    "CADIDR": 11935.483870968,
    "TRYHUF": 11.071428571,
    "SEKHUF": 33.214285714,
    "MXNCZK": 1.348837209,
    "INRCZK": 0.279069767,
    "SGDILS": 2.740740741,
    "MXNCLP": 52.727272727,
    "INRCLP": 10.909090909,
    "KRWPHP": 0.041666667,
    "CZKPHP": 2.388888889,
    "CHFAED": 4.074074074,
    "INRAED": 0.044444444,
    "RUBCOP": 42.307692308,
    "ZARSAR": 0.196296296,
    "CADSAR": 2.740740741,
    "INRMYR": 0.057142857,
    "RUBMYR": 0.052380952,
    "PLNRON": 1.136363636,
    "HUFRON": 0.012727273,
    "RONPEN": 0.814814815,
    "THBPEN": 0.100000000,
    "EURARS": 900.000000000,
    "PENEGP": 12.857142857,
    "CADNGN": 1104.477611940,
    "CZKBDT": 4.725274725,
    "MYRBDT": 23.076923077,
    "THBVND": 692.307692308,
}

def perform_conversion(sourceCurrency: str, targetCurrency: str):
    input = sourceCurrency + targetCurrency
    if input in currenciesDict:
        return currenciesDict[input]
    else:
        return None

@dataclass(frozen=True)
class TransactionLimit:
    amount: float
    currency: str


@dataclass(frozen=True)
class CardDetails:
    cardId: str
    accountId: str
    issuedLocation: str
    number: str
    expiryMonth: int
    expiryYear: int
    cvv: int
    checksum: str
    transactionLimit: TransactionLimit
    dynamicRules: list

@dataclass(frozen=True)
class Transaction:
    id: str
    transactionId: str
    transactionCurrency: str
    transactionAmount: float
    merchant: str
    cardDetails: CardDetails


class ApprovalDecision(TypedDict):
    id: str
    approval: bool


# ======================================== #
# TRANSACTION PROCESSING LOGIC STARTS HERE #
# ======================================== #


def should_process(transaction: Transaction) -> bool:

    print("_________________________")
    print(transaction)
    print("Rejecting transaction, it is fraudulent!!", color="green")

    return False


# ======================================== #
# TRANSACTION PROCESSING LOGIC ENDS HERE   #
# ======================================== #


def parse_transaction(message: str) -> Transaction | None:
    if message.startswith('{"id"'):
        try:
            transaction_data = json.loads(message)

            card_details_data = transaction_data.pop("cardDetails", {})

            transaction_limit_data = card_details_data.pop("transactionLimit", {})
            transaction_limit = TransactionLimit(**transaction_limit_data)

            dynamic_rules = card_details_data.pop("dynamicRules", [])

            card_details = CardDetails(
                **card_details_data, transactionLimit=transaction_limit, dynamicRules=dynamic_rules
            )

            transaction = Transaction(**transaction_data, cardDetails=card_details)
            return transaction

        except json.JSONDecodeError:
            print("Failed to decode JSON message:", message, color="magenta")
            return None

        except KeyError as e:
            print(f"Missing key in transaction data: {e}", color="magenta")
            return None

    else:
        print("Message received:", message, color="yellow")
        return None


def handle_transaction(transaction: Transaction) -> ApprovalDecision:
    should_process_transaction = should_process(transaction)

    decision: ApprovalDecision = {
        "id": transaction.id,
        "approval": should_process_transaction,
    }
    return decision


APP_URL = "https://awx-detective-7bytp.ondigitalocean.app/api/v1/login"
WEBSOCKET_URL = "wss://awx-detective-7bytp.ondigitalocean.app/api/v1/transaction_feed"


async def listen_to_transactions(ssl_context: ssl.SSLContext, jwt: str) -> None:
    headers = {"Authorization": f"Bearer {jwt}"}

    async with websockets.connect(
        WEBSOCKET_URL, additional_headers=headers, ssl=ssl_context
    ) as websocket:
        try:
            async for message in websocket:
                transaction = parse_transaction(message)  # type: ignore

                if transaction:
                    decision = handle_transaction(transaction)
                    await websocket.send(json.dumps(decision))

        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e.code}, reason: {e.reason}", color="magenta")
        except Exception as e:
            print(f"Error: {e}", color="magenta")


def setup_and_auth() -> Tuple[ssl.SSLContext, str]:
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(certifi.where())

    payload = json.dumps({"username": USERNAME, "password": PASSWORD})
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", APP_URL, headers=headers, data=payload)
    try:
        data = json.loads(response.text)
    except Exception as e:
        raise ValueError("Incorrect Username Or Password!", e)

    jwt = data.get("token")
    return ssl_context, jwt


async def shutdown(loop) -> None:
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


def main() -> None:
    loop = asyncio.new_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(loop)))

    try:
        ssl_context, jwt = setup_and_auth()
        loop.run_until_complete(listen_to_transactions(ssl_context, jwt))
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        loop.close()


if __name__ == "__main__":
    main()
