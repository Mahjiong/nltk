# Natural Language Toolkit: Language Models
#
# Copyright (C) 2001-2018 NLTK Project
# Author: Ilia Kurenkov <ilia.kurenkov@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals, division

from nltk import compat
from nltk.lm.api import LanguageModel, Smoothing
from nltk.lm.smoothing import WittenBell, KneserNey


@compat.python_2_unicode_compatible
class MLE(LanguageModel):
    """Class for providing MLE ngram model scores.

    Inherits initialization from BaseNgramModel.
    """

    def unmasked_score(self, word, context=None):
        """Returns the MLE score for a word given a context.

        Args:
        - word is expcected to be a string
        - context is expected to be something reasonably convertible to a tuple
        """
        return self.context_counts(context).freq(word)


@compat.python_2_unicode_compatible
class Lidstone(LanguageModel):
    """Provides Lidstone-smoothed scores.

    In addition to initialization arguments from BaseNgramModel also requires
    a number by which to increase the counts, gamma.
    """

    def __init__(self, gamma, *args, **kwargs):
        super(Lidstone, self).__init__(*args, **kwargs)
        self.gamma = gamma

    def unmasked_score(self, word, context=None):
        """Add-one smoothing: Lidstone or Laplace.

        To see what kind, look at `gamma` attribute on the class.

        """
        counts = self.context_counts(context)
        word_count = counts[word]
        norm_count = counts.N()
        return (word_count + self.gamma) / (norm_count + len(self.vocab) * self.gamma)


@compat.python_2_unicode_compatible
class Laplace(Lidstone):
    """Implements Laplace (add one) smoothing.

    Initialization identical to BaseNgramModel because gamma is always 1.
    """

    def __init__(self, *args, **kwargs):
        super(Laplace, self).__init__(1, *args, **kwargs)


class InterpolatedLanguageModel(LanguageModel):

    def __init__(self, smoothing_cls, *args, **kwargs):
        assert issubclass(smoothing_cls, Smoothing)
        params = kwargs.pop("params", {})
        super().__init__(*args, **kwargs)
        self.estimator = smoothing_cls(self.vocab, self.counts, **params)

    def unmasked_score(self, word, context=None):
        if not context:
            return self.estimator.unigram_score(word)
        alpha, gamma = self.estimator.alpha_gamma(word, context)
        return alpha + gamma * self.unmasked_score(
            word, context[1:]
        )


class WittenBellInterpolated(InterpolatedLanguageModel):
    def __init__(self, *args, **kwargs):
        super().__init__(WittenBell, *args, **kwargs)


class KneserNeyInterpolated(InterpolatedLanguageModel):
    def __init__(self, *args, discount=0.1, **kwargs):
        super().__init__(KneserNey, *args, params={"discount": discount}, **kwargs)
