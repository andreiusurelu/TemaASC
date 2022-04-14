"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
    def add_to_cart(self, cart_id, product, quantity):
        i = 0
        while i < quantity:
            if self.marketplace.add_to_cart(cart_id, product):
                i = i + 1
            else:
                time.sleep(self.retry_wait_time)

    def remove_to_cart(self, cart_id, product, quantity):
        i = 0
        while i < quantity:
            i = i + 1
            self.marketplace.remove_from_cart(cart_id, product)

    def run(self):
        for cart in self.carts:
            cart_id = self.marketplace.new_cart()
            for command in cart:
                command_type = command.get("type")
                command_prod = command.get("product")
                command_quantity = command.get("quantity")
                if command_type == "add":
                    self.add_to_cart(cart_id, command_prod, command_quantity)
                elif command_type == "remove":
                    self.remove_to_cart(cart_id, command_prod, command_quantity)
                else:
                    continue
            for product in self.marketplace.place_order(cart_id):
                print(self.name + " bought " + str(product))