# -*- coding: utf-8 -*-
import unittest
from generate import text_generator

"""simple tests for text_generator"""
class test_text_generator(unittest.TestCase):

    def setUp(self):
        self.__DEPTH = 1
        self.__SIZE = 100
        self.__TEXT_TO_CLEAR = "That is ',?durty текст с Русскими letters in difFerent cases"
        self.__CLEARED_TEST = u"that is durty текст с русскими letters in different cases"
        self.__LIST_FOR_DISTRIBUTION_CHECKING = [0,1,1,2,2,2,9,9,8,8]
        self.__LIST_DISTRIBUTION_MAP = {0:0.1,1:0.2,2:0.3,9:0.2,8:0.2}
        self.__TEXTS_FOR_TEST = "texts.txt"

    def test_size(self):
        # make sure the shuffled sequence does not lose any elements
        generator = text_generator(self.__DEPTH)
        generator.fit(self.__TEXTS_FOR_TEST)
        text = generator.generate(self.__SIZE)
        self.assertEqual(len(text.split()), self.__SIZE)

    def test_clearing(self):
        # make sure the text clearing working fine
        generator = text_generator(self.__DEPTH)
        result = generator._text_generator__clear_text(self.__TEXT_TO_CLEAR)
        self.assertEqual(result, self.__CLEARED_TEST)

    def text_distribution(self):
        # check correctness of objects in list distribution correctness
        generator = text_generator(self.__DEPTH)
        result = generator.__text_generator__list_to_distribution(self.__LIST_FOR_DISTRIBUTION_CHECKING)
        self.assertEqual(result, self.__LIST_DISTRIBUTION_MAP)

if __name__ == '__main__':
    unittest.main()