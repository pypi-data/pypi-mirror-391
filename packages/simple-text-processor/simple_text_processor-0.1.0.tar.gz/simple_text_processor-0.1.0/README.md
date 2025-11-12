SimpleTextProcessor

A lightweight utility library for quick text preparation in machine learning and NLP tasks.

This package provides simple functions for

Cleaning Removing punctuation, converting to lowercase, and handling special characters.

Vectorization Creating a simple Bag-of-Words (BoW) vector representation from a list of documents.

Installation

Since this package is small, it only requires numpy as a dependency for the vectorization function.

pip install simple-text-processor


Usage

1. Clean Text

from simple_text_processor import clean_text

text = Hello World! This is a Test sentence with some Numb3rs.
cleaned_text = clean_text(text)
print(cleaned_text)
# Output hello world this is a test sentence with some numb rs


2. Simple Bag-of-Words Vectorizer

from simple_text_processor import simple_vectorize

documents = [
    The sun is shining brightly.,
    A sunny day is a happy day.,
    The moon is out tonight.,
]

vectors, vocabulary = simple_vectorize(documents)

print(Vocabulary, vocabulary)
# Output Vocabulary {'the' 0, 'sun' 1, 'is' 2, 'shining' 3, 'brightly' 4, 'a' 5, 'sunny' 6, 'day' 7, 'happy' 8, 'moon' 9, 'out' 10, 'tonight' 11}

print(nVectors (BoW)n, vectors)
# Output (Numpy array of word counts)
# [[1 1 1 1 1 0 0 0 0 0 0 0]
#  [0 0 1 0 0 1 1 2 1 0 0 0]
#  [1 0 1 0 0 0 0 0 0 1 1 1]]
