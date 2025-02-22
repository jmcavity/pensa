Contribute
==========

You can support PENSA in several different ways: by reporting bugs and flaws, by requesting new functionality that would benefit your work, or by writing or improving code. 
We are always happy to help and to hear about your work and your success stories.

Report a bug or request a feature
***********************************

PENSA is open-source and available on `Github <https://github.com/drorlab/pensa>`_. Please submit issues or requests using the `issue tracker <https://github.com/drorlab/pensa/issues>`_.

Add new functionality 
***********************************

We welcome any kind of contributions to improve or expand the PENSA code. In particular, we are interested in readers for new feature types and new ways to analyze and compare structural ensembles. PENSA is maintained on `Github <https://github.com/drorlab/pensa>`_ so you can fork it and create a pull request. Please make sure to properly test your contribution before the request. For large or complicated contributions, please get in contact so we can coordinate them with you. We explain one of the most straightforward cases (featurizer) below:

New featurizer
-----------------------------------
To add the possibility to read a new kind of features, add a module file to the folder :mod:`pensa/features <pensa.features>` that contains your reader functions. These reader functions should return a list with feature names and a numpy array with the corresponding values. Use one of the existing featurizers as a template.

Want to help but not sure how?
***********************************

Check our `to do list <https://github.com/drorlab/pensa/blob/master/TODO.md>`_ for inspiration. We have much more ideas than time to implement them all. Just pick something from the list and let us know that you work on it. Feel free to reach out for questions!

