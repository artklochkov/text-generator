# -*- coding: utf-8 -*-
import os
from collections import Counter
import string
import random
import argparse

"""main class for fitting text model and text generation"""
class text_generator(object):
    DEFAULT_PATH = 'texts.txt'
    SENTENCE_CHAR_LENGTH_TRESHOLD = 3
    SPECIAL_SYMBOLS_LIST = ['\xe2\x80\x99', '\xe2\x80\x9d', '\x9c', '\x98']
    TRANSLATE_TABLE = {ord(c): None for c in string.punctuation.replace('.', '').join(SPECIAL_SYMBOLS_LIST)}

    def __init__(self, depth=1):
        self.depth = depth

    def __get_keys(self, words):
        assert len(words) > 0
        if self.depth == 0:
            return
        if self.depth >= len(words):
            return
        for position in xrange(len(words) - self.depth):
            yield tuple(words[position:position + self.depth]), words[position + self.depth]

    def __clear_text(self, text):
        text = unicode(text, encoding='utf-8')
        text = text.strip()
        text = text.lower()
        text = text.translate(self.TRANSLATE_TABLE)
        return text

    def __list_to_distribution(self, object_list):
        object_dist = dict()
        object_list = Counter(object_list)
        length_summary = float(sum(object_list.values()))
        assert length_summary > 0
        for key, value in object_list.items():
            object_dist[key] = value / length_summary
        return object_dist

    def fit(self, filepath=DEFAULT_PATH):
        paragraph_lengths = list()
        sentence_lengths = list()
        markov_counter = dict()
        words_list = list()
        processed_counter = 0
        for line in open(filepath, 'r'):
            if len(line) <= self.SENTENCE_CHAR_LENGTH_TRESHOLD:
                continue
            line = self.__clear_text(line)
            sentences = line.split('.')
            paragraph_lengths.append(len(sentences))
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) <= self.SENTENCE_CHAR_LENGTH_TRESHOLD:
                    continue
                sentence_lengths.append(len(sentence.split()))
                words_in_sentence = sentence.split()
                words_list.extend(words_in_sentence)
                # calculate markov words distribution
                keys = self.__get_keys(words_in_sentence)
                for key, word in keys:
                    if key in markov_counter:
                        distribution = markov_counter[key]
                        distribution.append(word)
                    else:
                        markov_counter[key] = [word]

        processed_counter += 1
        if processed_counter % 100 == 0:
            print processed_counter, ' files processed'

        # convert counters to distributions
        self.paragraph_dist = self.__list_to_distribution(paragraph_lengths)
        self.sentences_dist = self.__list_to_distribution(sentence_lengths)
        self.words_dist = self.__list_to_distribution(words_list)

        # converting markov counters to distributions
        self.markov_dist = dict()
        for key, value in markov_counter.iteritems():
            self.markov_dist[key] = self.__list_to_distribution(value)

    def __random_pick(self, some_list, probabilities):
        x = random.uniform(0, 1)
        cumulative_probability = 0.0
        for item, item_probability in zip(some_list, probabilities):
            cumulative_probability += item_probability
            if x < cumulative_probability:
                break
        return item

    def __generate_from_distribution(self, distribution):
        if len(distribution) == 0:
            return None
        distribution = zip(*distribution.items())
        words = list(distribution[0])
        probabilities = list(distribution[1])
        assert len(words) == len(probabilities)
        generated_word = self.__random_pick(words, probabilities)
        return generated_word

    def __construct_sentence_from_words(self, words):
        if len(words) > 0:
            words[0] = words[0].title()
        return ' '.join(words) + '.'

    def __generate_sentence(self, length):
        words_in_sentence = []
        for word_counter in xrange(min(length, self.depth)):
            word = self.__generate_from_distribution(self.words_dist)
            words_in_sentence.append(word)
        if length > self.depth:
            for word_counter in xrange(length - self.depth):
                key = tuple(words_in_sentence[-self.depth:])
                if key not in self.markov_dist:
                    current_distribution = self.words_dist
                else:
                    current_distribution = self.markov_dist[key]
                word = self.__generate_from_distribution(current_distribution)
                words_in_sentence.append(word)
        return self.__construct_sentence_from_words(words_in_sentence)

    def generate(self, length):
        length_summary = 0
        text = ''
        while length_summary < length:
            paragraph_length = self.__generate_from_distribution(self.paragraph_dist)
            sentences = []
            for sentence_counter in xrange(paragraph_length):
                sentence_length = self.__generate_from_distribution(self.sentences_dist)
                if length_summary + sentence_length > length:
                    sentence_length = length - length_summary
                    break
                sentence = self.__generate_sentence(sentence_length)
                sentences.append(sentence)
                length_summary += sentence_length
                sentence_length = 0
            if sentence_length > 0:
                sentence = self.__generate_sentence(sentence_length)
                sentences.append(sentence)
                length_summary += sentence_length
            text = text + ' '.join(sentences) + os.linesep
        return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', metavar='path', type=str, help='path to source texts')
    parser.add_argument('--size', metavar='size', type=int, help='output text size')
    parser.add_argument('--depth', metavar='depth', type=int, help='markov chain depth')
    parser.add_argument('--out', metavar='out', type=str, help='path to generated text')
    params = dict()

    try :
        params = vars(parser.parse_args())
    except (Exception):
        parser.print_help()

    generator = text_generator(depth=int(params['depth']))
    generator.fit(params['path'])
    text = generator.generate(int(params['size']))
    with open(params['out'], 'w') as out:
        out.write(text.encode('utf-8'))
        out.close()

if __name__ == '__main__':
    main()
