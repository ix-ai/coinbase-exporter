#!/usr/bin/env python3
""" Connects to Coinbase and exposes data to prometheus """
import logging
import time
import os
import sys
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily
from coinbase.wallet.client import Client

LOG = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=os.environ.get("LOGLEVEL", "INFO"),
    format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class CoinbaseCollector:
    """The main class"""
    _api_key = None
    _api_secret = None
    _cb = None
    cb_accounts = []

    def __init__(self):
        self.default_currency = os.environ.get("DEFAULT_CURRENCY", 'USD')
        self._api_key = os.environ.get("API_KEY")
        self._api_secret = os.environ.get("API_SECRET")
        if not self._api_key or not self._api_secret:
            raise ValueError("Missing API_KEY or API_SECRET environment variable.")
        self._cb = Client(self._api_key, self._api_secret)

    def _get_transactions(self, account, last_transactions=None):
        if last_transactions:
            transactions = last_transactions
        else:
            transactions = self._cb.get_transactions(account['id'], limit=100)
        LOG.debug('starting _get_transactions')
        LOG.debug(transactions)

        if transactions.get('pagination') and transactions['pagination']:
            if transactions['pagination'].get('next_uri'):
                new_transactions = self._cb.get_transactions(
                    account['id'],
                    limit=2,
                    starting_after=transactions['pagination']['starting_after']
                )
                if new_transactions.get('pagination') and new_transactions['pagination'].get('next_uri'):
                    transactions['pagination'] = new_transactions['pagination']
                for transaction in new_transactions['data']:
                    transactions['data'].append(transaction)
        else:
            LOG.debug("no more pagination")

        if transactions.get('pagination') and transactions['pagination']:
            transactions = self._get_transactions(account=account, last_transactions=transactions)
        else:
            LOG.debug("no more pagination 2")
        LOG.debug(transactions)
        return transactions

    def _connect_coinbase(self):
        accounts_data = []
        accounts = self._cb.get_accounts()
        for account in accounts['data']:
            time.sleep(1)
            account['transactions'] = self._get_transactions(account=account)
            accounts_data.append(account)
            # LOG.debug(account)
        if accounts_data:
            self.cb_accounts = accounts_data

    def describe(self):
        return []

    def collect(self):
        "The actual collecting class"

        self._connect_coinbase()
        metrics = {
            'account_balance': GaugeMetricFamily(
                'account_balance',
                'Account Balance',
                labels=['source_currency', 'currency', 'account', 'type']
            ),
            'coinbase_account_transaction_amount': GaugeMetricFamily(
                'coinbase_account_transaction_amount',
                'Transaction History',
                labels=['source_currency', 'currency', 'account', 'target_currency']
            ),
        }

        if self._cb:
            for cb_account in self.cb_accounts:
                metrics['account_balance'].add_metric(
                    value=float(cb_account['balance']['amount']),
                    labels=[
                        cb_account['balance']['currency'],
                        cb_account['balance']['currency'],
                        cb_account['id'],
                        'coinbase',
                    ]
                )
                if cb_account['balance']['currency'] != self.default_currency:
                    transaction = self._get_transaction_sum(account=cb_account)
                    metrics['coinbase_account_transaction_amount'].add_metric(
                        value=float(transaction['amount']),
                        labels=[
                            transaction['currency'],
                            transaction['currency'],
                            transaction['account'],
                            transaction['target_currency']
                        ]
                    )
            for m in metrics.values():
                yield m

    def _get_transaction_sum(self, account):
        account_transaction = {
            'amount': float(0),
            'currency': self.default_currency,
            'target_currency': account['balance']['currency'],
            'account': account['id'],
        }
        if 'data' in account['transactions']:
            for transaction in account['transactions']['data']:
                if (
                        transaction['type'] in ['buy', 'sell']
                        and transaction['status'] in ['completed']
                        and transaction['native_amount']['currency'] == account_transaction['currency']
                        and account_transaction['currency'] != transaction['amount']['currency']
                ):
                    account_transaction['amount'] += float(transaction['native_amount']['amount'])

        return account_transaction


if __name__ == '__main__':
    REGISTRY.register(CoinbaseCollector())
    port = 9308
    start_http_server(port)
    LOG.info('Listening for requests on port {}'.format(port))
    while True:
        time.sleep(1)
