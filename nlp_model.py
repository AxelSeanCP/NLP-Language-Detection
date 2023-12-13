# -*- coding: utf-8 -*-
"""NLP Model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K1xbZN40uIWEIa4wkbK40bmYHzhs6Pdd

# Import libraries
"""

import tensorflow as tf
import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

nltk.download('punkt')

"""# Load dataset"""

df = pd.read_csv('Language Detection.csv')
df.head(10)

"""# Data cleaning

"""

df.drop_duplicates(subset=["Text"], inplace=True)

# tokenize words
df['Text'] = df['Text'].apply(word_tokenize)

# remove punctuation
df['Text'] = df['Text'].apply(lambda text: ' '.join([word for word in text if word.isalnum()]))

print(df['Text'])

"""# One Hot Encoding"""

bahasa = pd.get_dummies(df['Language'])
df_baru = pd.concat([df, bahasa], axis=1)
df_baru = df_baru.drop(columns=['Language'])
print(df_baru)

"""# Split dataset
in this dataset there is a column named text and 17 other columns with language names
"""

kalimat = df_baru['Text'].values
label = df_baru[['Arabic', 'Danish', 'Dutch', 'English', 'French', 'German', 'Greek', 'Hindi', 'Italian', 'Kannada', 'Malayalam', 'Portugeese',
                 'Russian', 'Spanish', 'Sweedish', 'Tamil', 'Turkish']].values

"""# Split data into train and test

- random_state is used so that you will get the same result as i do
"""

kalimat_latih, kalimat_test, label_latih, label_test = train_test_split(kalimat, label, test_size=0.2, random_state=42)

"""# Tokenization"""

vocab_size = 150000
tokenizer = Tokenizer(num_words=vocab_size, oov_token='x')
tokenizer.fit_on_texts(kalimat_latih)

sekuens_latih = tokenizer.texts_to_sequences(kalimat_latih)
sekuens_test = tokenizer.texts_to_sequences(kalimat_test)

padded_latih = pad_sequences(sekuens_latih, maxlen=200, padding='post')
padded_test = pad_sequences(sekuens_test, maxlen=200, padding='post')

print(f"Kalimat latih: {kalimat_latih} \n")
print(f"Sekuens latih: {sekuens_latih} \n")
print(f"Padded latih: {padded_latih} \n")

"""# Callback function"""

class SantaiDuluGakSih(tf.keras.callbacks.Callback):
  def __init__(self, sabar=5):
    super(SantaiDuluGakSih, self).__init__()
    self.sabar = sabar
    self.gak_sabar = 0

  def on_epoch_end(self, epoch, logs={}):
    if logs.get('accuracy')<0.75 or logs.get('val_accuracy')<0.75:
      self.gak_sabar += 1
    else:
      self.gak_sabar = 0

    if self.gak_sabar >= self.sabar:
      print(f"The model accuracy has been below 75% for {self.gak_sabar} epochs, Stopping training immediatly!!!")
      self.model.stop_training = True

stop_early = SantaiDuluGakSih(sabar=5)

"""# Model creation"""

model = tf.keras.models.Sequential([
    tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=200, input_length=200),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(32, activation="relu"),
    tf.keras.layers.Dense(17, activation="softmax")
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(
    padded_latih,
    label_latih,
    epochs=40,
    batch_size=64,
    validation_data=(padded_test, label_test),
    callbacks=[stop_early],
    verbose=2
)