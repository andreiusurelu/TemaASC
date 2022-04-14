"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        Thread.__init__(self, **kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time

    def publish(self, producer_id, product, quantity, wait_time):
        i = 0
        while i < quantity:
            if self.marketplace.publish(producer_id, product):
                i = i + 1
                time.sleep(wait_time)
            else:
                time.sleep(self.republish_wait_time)

    def run(self):
        while True:
            producer_id = self.marketplace.register_producer()
            for product in self.products:
                self.publish(producer_id, product[0], product[1], product[2])
