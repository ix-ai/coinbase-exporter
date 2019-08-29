#!/usr/bin/env python3
""" Connects to Coinbase and exposes data to prometheus """

import logging
import time
import os
import sys
import pygelf
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


def configure_logging():
    """ Configures the logging """
    gelf_enabled = False

    if os.environ.get('GELF_HOST'):
        GELF = pygelf.GelfUdpHandler(
            host=os.environ.get('GELF_HOST'),
            port=int(os.environ.get('GELF_PORT', 12201)),
            debug=True,
            include_extra_fields=True,
            _ix_id=os.path.splitext(sys.modules['__main__'].__file__)[0][1:],  # sets it to 'coinbase-exporter'
        )
        LOG.addHandler(GELF)
        gelf_enabled = True
    LOG.info('Initialized logging with GELF enabled: {}'.format(gelf_enabled))


class CoinbaseCollector:
    """The main class"""
    _api_key = None
    _api_secret = None
    _cb = None
    cb_accounts = []

    def __init__(self):
        self.fiat = os.environ.get("FIAT", 'EUR')
        self._api_key = os.environ.get("API_KEY")
        self._api_secret = os.environ.get("API_SECRET")
        if not self._api_key or not self._api_secret:
            raise ValueError("Missing API_KEY or API_SECRET environment variable.")
        self._cb = Client(self._api_key, self._api_secret)

    def get_transactions(self, account):
        """ Gets the transactions history from coinbase """
        all_txns = []
        starting_after = None
        while True:
            txns = self._cb.get_transactions(account['id'], limit=100, starting_after=starting_after)
            if txns.pagination.next_starting_after is not None:
                starting_after = txns.pagination.next_starting_after
                for tx in txns.data:
                    all_txns.append(tx)
                time.sleep(1)  # Let's not hit the rate limiting
            else:
                for tx in txns.data:
                    all_txns.append(tx)
                break

        for tx in all_txns:
            LOG.debug('Found tx: {} for {} {}'.format(tx.id, tx.amount.amount, tx.amount.currency))
        return all_txns

    def get_accounts(self):
        """ Establishes the connection to coinbase and saves the accounts in self.cb_accounts """
        accounts_data = []
        accounts = self._cb.get_accounts()
        for account in accounts['data']:
            time.sleep(1)
            account['transactions'] = self.get_transactions(account=account)
            accounts_data.append(account)
        if accounts_data:
            self.cb_accounts = accounts_data

    def describe(self):
        """ Just a needed method, so that collect() isn't called at startup """
        return []

    def collect(self):
        "The actual collecting class"

        self.get_accounts()
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

        if self.cb_accounts:
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
                if cb_account['balance']['currency'] != self.fiat:
                    transaction = self.sum_transactions(account=cb_account)
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

    def sum_transactions(self, account):
        """ Calculates the total transaction sum for FIAT """
        account_transaction = {
            'amount': float(0),
            'currency': self.fiat,
            'target_currency': account['balance']['currency'],
            'account': account['id'],
        }
        for tx in account['transactions']:
            if (
                    tx['type'] in ['buy', 'sell']
                    and tx['status'] in ['completed']
                    and tx['native_amount']['currency'] == account_transaction['currency']
                    and account_transaction['currency'] != tx['amount']['currency']
            ):
                account_transaction['amount'] += float(tx['native_amount']['amount'])

        return account_transaction


if __name__ == '__main__':
    configure_logging()
    PORT = int(os.environ.get('PORT', '9308'))
    LOG.info("Starting on port {}".format(PORT))
    REGISTRY.register(CoinbaseCollector())
    start_http_server(PORT)
    while True:
        time.sleep(1)
