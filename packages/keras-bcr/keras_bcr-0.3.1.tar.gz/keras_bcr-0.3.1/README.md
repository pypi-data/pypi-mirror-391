[![PyPI version](https://badge.fury.io/py/keras-bcr.svg)](https://badge.fury.io/py/keras-bcr)
[![PyPi downloads](https://img.shields.io/pypi/dm/keras-bcr)](https://img.shields.io/pypi/dm/keras-bcr)
[![DOI](https://zenodo.org/badge/490336438.svg)](https://zenodo.org/badge/latestdoi/490336438)

# keras-bcr : Batch Correlation Regularizer for TF2/Keras
The batch correlation regularization (BCR) technique adds a penalty loss
if the inputs and outputs before the skip-connection of a specific feature element are correlated.
The correlation coefficients are computed for each feature element seperatly across the current batch.

## Usage `BatchCorrRegularizer`

```py
from keras_bcr import BatchCorrRegularizer
import tensorflow as tf

# The BCR layer is added before the addition of the skip-connection
def build_resnet_block(inputs, units=64, activation="gelu",
                       dropout=0.4, bcr_rate=0.1):
    h = tf.keras.layers.Dense(units=units)(inputs)
    h = h = tf.keras.layers.Activation(activation=activation)(h)
    h = tf.keras.layers.Dropout(rate=dropout)(h)
    h = BatchCorrRegularizer(bcr_rate=bcr_rate)([h, inputs])  # << HERE
    outputs = tf.keras.layers.Add()([h, inputs])
    return outputs

# An model with 3 ResNet blocks
def build_model(input_dim):
    inputs = tf.keras.Input(shape=(input_dim,))
    h = build_resnet_block(inputs, units=input_dim)
    h = build_resnet_block(h, units=input_dim)
    outputs = build_resnet_block(h, units=input_dim)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    return model

INPUT_DIM = 64
model = build_model(input_dim=INPUT_DIM)
model.compile(optimizer=tf.keras.optimizers.Adam(), loss="mean_squared_error")

BATCH_SZ = 128
X_train = tf.random.normal([BATCH_SZ, INPUT_DIM])
y_train = tf.random.normal([BATCH_SZ, INPUT_DIM])

history = model.fit(X_train, y_train, verbose=1, epochs=2)
```

## Explanation
The class `BatchCorrRegularizer` takes the inputs and outputs of neural network layer or block (see `[h, inputs]` in the example above), 
and computes the pearson correlation for each input-output element across a training batch.

```py
from keras_bcr import batch_corr
import tensorflow as tf

BATCH_SIZE = 100
NUM_NEURONS = 1024
a = tf.random.normal((BATCH_SIZE, NUM_NEURONS))
b = tf.random.normal((BATCH_SIZE, NUM_NEURONS))

bcr = batch_corr(a, b)
bcr
# <tf.Tensor: shape=(), dtype=float32, numpy=0.07825338840484619>
```


## Appendix

### Installation
The `keras-bcr` [git repo](http://github.com/ulf1/keras-bcr) is available as [PyPi package](https://pypi.org/project/keras-bcr)

```sh
pip install keras-bcr
pip install git+ssh://git@github.com/ulf1/keras-bcr.git
```

### Install a virtual environment

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
pip install -r requirements-dev.txt --no-cache-dir
pip install -r requirements-demo.txt --no-cache-dir
```

(If your git repo is stored in a folder with whitespaces, then don't use the subfolder `.venv`. Use an absolute path without whitespaces.)

### Python commands

* Jupyter for the examples: `jupyter lab`
* Check syntax: `flake8 --ignore=F401 --exclude=$(grep -v '^#' .gitignore | xargs | sed -e 's/ /,/g')`
* Run Unit Tests: `PYTHONPATH=. pytest`

Publish

```sh
python setup.py sdist 
twine upload -r pypi dist/*
```

### Clean up 

```sh
find . -type f -name "*.pyc" | xargs rm
find . -type d -name "__pycache__" | xargs rm -r
rm -r .pytest_cache
rm -r .venv
```


### Support
Please [open an issue](https://github.com/ulf1/keras-bcr/issues/new) for support.


### Contributing
Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/ulf1/keras-bcr/compare/).


### Acknowledgements
The "Evidence" project was funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) - [433249742](https://gepris.dfg.de/gepris/projekt/433249742) (GU 798/27-1; GE 1119/11-1).

### Maintenance
- till 31.Aug.2023 (v0.2.0) the code repository was maintained within the DFG project [433249742](https://gepris.dfg.de/gepris/projekt/433249742)
- since 01.Sep.2023 (v0.3.0) the code repository is maintained by Ulf Hamster.

