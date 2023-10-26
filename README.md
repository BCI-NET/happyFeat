# HappyFeat - Interactive framework for clinical BCI applications

HappyFeat is a software aiming to to simplify the use of BCI pipelines in clinical settings. More precisely, it is a **software assitant for extracting and selecting classification features for BCI**.

It gathers all necessary manipulations and analysis in a single convenient GUI, and automates experimental or analytic parameters. The resulting workflow allows for effortlessly selecting the best features, helping to achieve good BCI performance in time-constrained environments. Alternative features based on Functional Connectivity can be used and compared or combined with Power Spectral Density, allowing a network-oriented approach. 

It consists of Qt-based GUIs and Python toolboxes, allowing to realize all steps for customizing and fine-tuning a BCI system: feature extraction & selection, classifier training.

HappyFeat also allows to interface with BCI softwares (OpenViBE for the moment!) in order to facilitate the whole BCI workflow, from data acquisition to online classification.

The focus is put on ease of use, trial-and-error training of the classifier, and fast and efficient analysis of features of interest from BCI sessions.

## Key Features

* **Easy to use GUI** allowing to extract and visualize classification features, and select the most relevant ones for training a classifier.
* Use **Spectral Power** or **Coherence-based** features for classification. HappyFeat allows to extract & visualize both types of features in parallel, and **mix them at the training level**.
* Feature selection and classifier training can be done multiple times in a row, until satisfactory results are achieved.
* A **worspace management system** keeps tracks of all extraction- and training-related manipulations, and enables a high degree of reproducibility.


* Available pipelines: 
  * Power Spectrum (Burg method)
  * Functional Connectivity: Coherence-based Node Strength (Spectral Coherence, Imaginary part of Coherence)
  * Mixing Both PSD and Connectivity
* Available classifiers:
  * LDA
  * *more coming soon!*

* *Coming soon: More Features!*
  * *More feature classes, more classification algos*
  * *Particle swarm algorithm for determining optimal AutoRegressive model order*

* *Coming soon: Standalone Python software!*
  * *Run the offline analysis (extraction, visualization, selection, training) without the need of a BCI software*
 
* *Coming soon: compatibility with more BCI software!*

# Requirements

* Python 3.9 or more recent
* Python packages : shutils / PyQt5 / numpy / MNE / matplotlib / scipy / spectrum / statsmodel / pandas
* OpenViBE Version 3.5.0: http://openvibe.inria.fr/downloads/

# Installation

Clone the project to a local directory. 

To install the requirements, open a console/command prompt, change to your cloned folder and type:
        pip install -r requirements.txt

Everything from there on is managed directly from the cloned directory.

# Full documentation

Go to docs/index.md for more details!

# License

This software is licensed using BSD 3-Clause. Please refer to LICENSE.md for more details.
