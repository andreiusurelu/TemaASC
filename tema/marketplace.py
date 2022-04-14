"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock
import unittest
import logging
from .product import Tea
from .product import Coffee
import time
from logging.handlers import RotatingFileHandler
# from queue import Queue


class TestMarketplace(unittest.TestCase):
    def setUp(self):
        queue_size_per_producer = 10
        self.marketplace = Marketplace(queue_size_per_producer)
        self.product_tea = Tea('ceai', 10, 'Tea')
        self.product_coffee = Coffee('cafea', 12, '5.09', 'MEDIUM')

    def test_register_producer(self):
        self.assertEqual(self.marketplace.register_producer(),
                         self.marketplace.producer_id-1, 'incorrect producer id')

    def test_publish(self):
        producer_id = self.marketplace.register_producer()
        self.assertEqual(producer_id, self.marketplace.producer_id-1, 'Incorrect producer id')
        self.assertEqual(self.marketplace.publish(producer_id, self.product_coffee),
                         True, 'failed to publish')

    def test_new_cart(self):
        self.assertEqual(self.marketplace.new_cart(), self.marketplace.cart_id-1, 'incorrect cart id')

    def test_add_to_cart(self):
        self.test_publish()
        cart_id = self.marketplace.new_cart()
        self.assertEqual(cart_id, self.marketplace.cart_id-1, 'Incorrect cart id')
        self.assertEqual(self.marketplace.add_to_cart(cart_id, self.product_coffee), True, 'failed to add to cart')

    def test_remove_from_cart(self):
        self.test_publish()
        cart_id = self.marketplace.new_cart()
        self.assertEqual(cart_id, self.marketplace.cart_id - 1, 'Incorrect cart id')
        self.assertEqual(self.marketplace.add_to_cart(cart_id, self.product_coffee), True, 'failed to add to cart')
        self.marketplace.remove_from_cart(cart_id, self.product_coffee)
        self.assertEqual(self.marketplace.cart_queues.get(cart_id), [], 'failed to remove from cart')

    def test_place_order(self):
        self.test_publish()
        cart_id = self.marketplace.new_cart()
        self.assertEqual(cart_id, self.marketplace.cart_id - 1, 'Incorrect cart id')
        self.assertEqual(self.marketplace.add_to_cart(cart_id, self.product_coffee), True, 'failed to add to cart')


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        self.queue_size_per_producer = queue_size_per_producer
        self.prod_gen_lock = Lock()
        self.cons_gen_lock = Lock()
        self.producer_id = 0
        self.cart_id = 0
        self.producer_queues = {}
        self.cart_queues = {}
        self.sem_prod = Lock()
        self.sem_con = Lock()
        logging.basicConfig(handlers=[RotatingFileHandler('./marketplace.log', maxBytes=100000, backupCount=10)],
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S', level=logging.INFO)
        logging.Formatter.converter = time.gmtime
        self.logger = logging.getLogger()
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.prod_gen_lock:
            producer_id = self.producer_id
            self.producer_id = self.producer_id + 1
            self.producer_queues[producer_id] = []
            self.logger.info('register_producer new generated id:' + str(producer_id))
        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.logger.info('producer_id: ' + str(producer_id) + "; product: " + str(product))
        self.sem_prod.acquire()
        producer_queue = self.producer_queues.get(producer_id)
        is_not_full = False
        if len(producer_queue) < self.queue_size_per_producer:
            is_not_full = True
            self.producer_queues.get(producer_id).append(product)
            self.logger.info('successfully published by ' + str(producer_id))
        self.sem_prod.release()
        return is_not_full

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.cons_gen_lock:
            cart_id = self.cart_id
            self.cart_id = self.cart_id + 1
            self.cart_queues[cart_id] = []
            self.logger.info('new_cart new generated id:' + str(cart_id))
        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        self.sem_con.acquire()
        self.logger.info('add_to_cart cart_id: ' + str(cart_id) + "; product: " + str(product))
        for key in range(self.producer_id):
            for prod in self.producer_queues[key]:
                if product == prod:
                    self.producer_queues[key].remove(product)
                    self.cart_queues.get(cart_id).append([key, product])
                    self.logger.info('successfully added in cart with id:' + str(cart_id))
                    self.sem_con.release()
                    return True
        self.sem_con.release()
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.sem_con.acquire()
        self.logger.info('remove_from_cart cart_id: ' + str(cart_id) + "; product: " + str(product))
        for producer_id, prod in self.cart_queues.get(cart_id):
            if prod == product:
                self.producer_queues[producer_id].append(product)
                self.cart_queues.get(cart_id).remove([producer_id, prod])
                break
        self.sem_con.release()

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        product_list = []
        for prod_id, prod in self.cart_queues.get(cart_id):
            product_list.append(prod)
        self.logger.info('place_order result:' + str(product_list))
        return product_list
