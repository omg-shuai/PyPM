# -*- coding: utf-8 -*-

import numpy as np

from keras.layers import Input, Dense
from keras.models import Model
from keras.models import load_model
from keras.callbacks import EarlyStopping

class FcDenoiseAutoencoder:
    """
    Fully connected denoising autoencoder (DAE)
    
    Parameters
    ----------
    x (n_samples, n_features) - The training input samples
    hidden_dims (List) - The structure of autoencoder
    corrupt (str, optional, default='Gaussian') - The type of corruption
    corrupt_rate (float, default=0.5) - The rate of corruption
    
    Attributes
    ----------
    FcDenoiseAutoencoder (network) - The model of denoising autoencoder
    FcDenoiseEncoder (network) - The encoder part  
    
    Example
    -------
    >>> from sklearn import preprocessing
    >>> from sklearn.datasets import load_wine
    >>> from pypm.models.fc_denoise_autoencoder import FcDenoiseAutoencoder
    >>> # Load data
    >>> data = load_wine().data
    array([[1.423e+01, 1.710e+00, 2.430e+00, ..., 1.040e+00, 3.920e+00 ...
    >>> StandardScaler = preprocessing.StandardScaler().fit(data)
    >>> train_data = StandardScaler.transform(data)
    array([[ 1.51861254, -0.5622498 ,  0.23205254, ...,  0.36217728 ...
    >>> # Build a denoise autoencoder
    >>> DenoiseAutoencoder = FcDenoiseAutoencoder(train_data, [10, 6, 10], corrupt='binary')
    >>> DenoiseAutoencoder.construct_model()
    >>> # Train model
    >>> DenoiseAutoencoder.train_model() 
    >>> # Save model
    >>> DenoiseAutoencoder.save_model('DenoiseAutoencoder', 'DenoiseEncoder')
    >>> # Get features & reconstructions
    >>> Features = DenoiseAutoencoder.get_features(train_data)
    array([[0.09853178, 0.1520491 , 0.01192483, 0.00760067, 0.0273003 ...
    >>> Reconstructions = DenoiseAutoencoder.get_reconstructions(train_data)
    array([[ 1.203124  , -0.39634925,  0.36789453, ...,  0.61248255 ...
    
    """
    
    def __init__(self, x, hidden_dims, corrupt='Gaussian', corrupt_rate=0.5):
        
        self.x = x
        if corrupt == 'Gaussian':
            self.x_corrupted = x + corrupt_rate * np.random.normal(loc=0.0, scale=1.0, size=x.shape)
        if corrupt == 'binary':
            self.x_corrupted = x * np.random.binomial(n=1, p=corrupt_rate, size=x.shape)
        self.hidden_dims = np.array(hidden_dims)
        
    def construct_model(self, encode_activation='sigmoid', decode_activation='sigmoid', use_linear=True):
    
        input_layer = Input(shape=(self.x.shape[1], ))
        
        # AE
        if self.hidden_dims.shape[0] == 1:
            
            latent_layer = Dense(self.hidden_dims[0], activation = encode_activation)(input_layer)
            
            if use_linear == True:
                output_layer = Dense(self.x.shape[1], activation = 'linear')(latent_layer)
            else:
                output_layer = Dense(self.x.shape[1], activation = decode_activation)(latent_layer)
            
        # DAE
        else:
            
            encode_layer = Dense(self.hidden_dims[0], activation = encode_activation)(input_layer)
            for i in range(self.hidden_dims.shape[0]//2 - 1):
                encode_layer = Dense(self.hidden_dims[i + 1], activation = encode_activation)(encode_layer)
            
            latent_layer = Dense(self.hidden_dims[self.hidden_dims.shape[0]//2], activation = encode_activation)(encode_layer)
            
            decode_layer = Dense(self.hidden_dims[self.hidden_dims.shape[0]//2 + 1], activation = decode_activation)(latent_layer)
            for i in range(self.hidden_dims.shape[0]//2 - 1):
                decode_layer = Dense(self.hidden_dims[self.hidden_dims.shape[0]//2 + 2 + i], activation = decode_activation)(decode_layer)
            
            if use_linear == True:
                output_layer = Dense(self.x.shape[1], activation = 'linear')(decode_layer)
            else:
                output_layer = Dense(self.x.shape[1], activation = decode_activation)(decode_layer)
           
        self.FcDenoiseAutoencoder = Model(input=input_layer, output=output_layer)
        self.FcDenoiseEncoder = Model(input=input_layer, output=latent_layer)
        
    def train_model(self, epochs=1000, batch_size=100, optimizer='Adam', loss='mean_squared_error', use_Earlystopping=True):
        
        self.FcDenoiseAutoencoder.compile(optimizer=optimizer, loss=loss)
        
        if use_Earlystopping == True:
            self.history = self.FcDenoiseAutoencoder.fit(self.x_corrupted, self.x, epochs = epochs, batch_size = batch_size, shuffle = True, 
                                    validation_split = 0.10, callbacks = [EarlyStopping(monitor='val_loss', patience = 30)])
        else:
            self.history = self.FcDenoiseAutoencoder.fit(self.x, self.x, epochs = epochs, batch_size = batch_size, shuffle = True)
        
    def get_features(self, x_test):
        
        return self.FcDenoiseEncoder.predict(x_test)
        
    def get_reconstructions(self, x_test):
        
        return self.FcDenoiseAutoencoder.predict(x_test)
        
    def save_model(self, FcDenoiseAutoencoder_name=None, FcDenoiseEncoder_name=None):
        
        if FcDenoiseAutoencoder_name != None:
            self.FcDenoiseAutoencoder.save(FcDenoiseAutoencoder_name + '.h5')
        else:
            print("FcDenoiseAutoencoder is not saved !")
        if FcDenoiseEncoder_name != None:
            self.FcDenoiseEncoder.save(FcDenoiseEncoder_name + '.h5')
        else:
            print("FcDenoiseEncoder is not saved !")
        
    def load_model(self, FcDenoiseAutoencoder_name=None, FcDenoiseEncoder_name=None):
        
        if FcDenoiseAutoencoder_name != None:
            self.FcDenoiseAutoencoder = load_model(FcDenoiseAutoencoder_name + '.h5')
        else:
            print("FcDenoiseAutoencoder is not load !")
        if FcDenoiseEncoder_name != None:
            self.FcDenoiseEncoder = load_model(FcDenoiseEncoder_name + '.h5')
        else:
            print("FcDenoiseEncoder is not load !")
        