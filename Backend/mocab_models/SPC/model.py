import yaml
import pandas as pd
import tensorflow as tf

from joblib import dump, load
from sklearn.preprocessing import OneHotEncoder
from keras import metrics
from tensorflow.keras.optimizers.legacy import Adam


def config(base_path):
    """
    Function config會設定model的參數
    """
    with open(f'{base_path}/config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)
    return config


def encode(x_train, x_test, y_train, y_test, base_path):
    """
    Function encode會將資料轉譯成model prefer的category
    """
    df_x = pd.concat([x_train, x_test])

    try:
        enc = load(f'{base_path}/encoder.joblib')
    except FileNotFoundError:
        enc = OneHotEncoder(drop='first').fit(df_x.astype(str))
        dump(enc, f'{base_path}/encoder.joblib')

    column_enc = list(enc.feature_names_in_)
    x_train = x_train.reindex(columns=column_enc)
    x_test = x_test.reindex(columns=column_enc)

    x_train = enc.transform(x_train.astype(str))
    x_test = enc.transform(x_test.astype(str))
    x_train = pd.DataFrame(x_train.toarray(), columns=enc.get_feature_names())
    x_test = pd.DataFrame(x_test.toarray(), columns=enc.get_feature_names())

    return x_train, x_test, y_train, y_test


def train(x_train, y_train, base_path):
    conf = config(base_path)
    METRICS = [
        metrics.Precision(thresholds=conf['set_thres']),
        metrics.Recall(thresholds=conf['set_thres']),
        metrics.AUC()
    ]

    # Load and compile Keras model
    opt_adam = Adam(learning_rate=conf['lr_rate'])
    model = tf.keras.models.load_model(f"{base_path}/register_model")
    model.compile(optimizer=opt_adam, loss=tf.losses.BinaryFocalCrossentropy(gamma=2.0), metrics=METRICS)

    model.fit(x_train, y_train, batch_size=16, epochs=conf['epoch'], verbose=2)

    model.save(f"{base_path}/new_model")

    return True


def get_model(model_type, base_path):
    if model_type == 'register':
        return tf.keras.models.load_model(f"{base_path}/register_model")
    elif model_type == 'new':
        return tf.keras.models.load_model(f"{base_path}/new_model")
    else:
        return None


def predict(data, base_path, model_type="register"):
    enc = load(f'{base_path}/encoder.joblib')
    column_enc = list(enc.feature_names_in_)
    df = pd.DataFrame(columns=column_enc)
    df.loc[0] = data
    df = enc.transform(df.astype(int).astype(str))
    df = pd.DataFrame(df.toarray(), columns=enc.get_feature_names())
    model = tf.keras.models.load_model(f"{base_path}/{model_type}_model")
    result = model.predict(df)
    return result[0]
