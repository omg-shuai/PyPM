# -*- coding: utf-8 -*-

import numpy as np
from sklearn import preprocessing
from sklearn.datasets import load_wine

from keras import backend as K
from keras.layers import Input, Dense
from keras.models import Model
from keras.models import load_model
from keras.callbacks import EarlyStopping

class FcSparseAutoencoder:
    
    def __init__(self, x, hidden_dims):
        
        self.x = x
        
        self.hidden_dims = np.array(hidden_dims)
        
    def construct_model(self, p=0.01, beta=1, encode_activation='sigmoid', decode_activation='sigmoid', use_linear=True):
        
        def sparse_constraint(activ_matrix):

            p_hat = K.mean(activ_matrix) # average over the batch samples
            #KLD = p*(K.log(p)-K.log(p_hat)) + (1-p)*(K.log(1-p)-K.log(1-p_hat))
            KLD = p*(K.log(p/p_hat)) + (1-p)*(K.log(1-p/1-p_hat))
            
            return -beta * K.sum(KLD) # sum over the layer units
    
        input_layer = Input(shape=(self.x.shape[1], ))
        
        # AE
        if self.hidden_dims.shape[0] == 1:
            
            latent_layer = Dense(self.hidden_dims[0], activation = encode_activation, activity_regularizer=sparse_constraint)(input_layer)
            
            if use_linear == True:
                output_layer = Dense(self.x.shape[1], activation = 'linear')(latent_layer)
            else:
                output_layer = Dense(self.x.shape[1], activation = decode_activation)(latent_layer)
            
        # DAE
        else:
            
            encode_layer = Dense(self.hidden_dims[0], activation = encode_activation, activity_regularizer=sparse_constraint)(input_layer)
            for i in range(self.hidden_dims.shape[0]//2 - 1):
                encode_layer = Dense(self.hidden_dims[i + 1], activation = encode_activation, activity_regularizer=sparse_constraint)(encode_layer)
            
            latent_layer = Dense(self.hidden_dims[self.hidden_dims.shape[0]//2], activation = encode_activation, activity_regularizer=sparse_constraint)(encode_layer)
            
            decode_layer = Dense(self.hidden_dims[self.hidden_dims.shape[0]//2 + 1], activation = decode_activation, activity_regularizer=sparse_constraint)(latent_layer)
            for i in range(self.hidden_dims.shape[0]//2 - 1):
                decode_layer = Dense(self.hidden_dims[self.hidden_dims.shape[0]//2 + 2 + i], activation = decode_activation, activity_regularizer=sparse_constraint)(decode_layer)
            
            if use_linear == True:
                output_layer = Dense(self.x.shape[1], activation = 'linear')(decode_layer)
            else:
                output_layer = Dense(self.x.shape[1], activation = decode_activation)(decode_layer)
           
        self.FcSparseAutoencoder = Model(input=input_layer, output=output_layer)
        self.FcSparseEncoder = Model(input=input_layer, output=latent_layer)
        
    def train_model(self, epochs=1000, batch_size=100, optimizer='Adam', loss='mean_squared_error', use_Earlystopping=True):
        
        self.FcSparseAutoencoder.compile(optimizer=optimizer, loss=loss)
        
        if use_Earlystopping == True:
            self.history = self.FcSparseAutoencoder.fit(self.x, self.x, epochs = epochs, batch_size = batch_size, shuffle = True, 
                                    validation_split = 0.10, callbacks = [EarlyStopping(monitor='val_loss', patience = 10)])
        else:
            self.history = self.FcSparseAutoencoder.fit(self.x, self.x, epochs = epochs, batch_size = batch_size, shuffle = True)
        
    def get_features(self, x_test):
        
        return self.FcSparseEncoder.predict(x_test)
        
    def get_reconstructions(self, x_test):
        
        return self.FcSparseAutoencoder.predict(x_test)
        
    def save_model(self, FcSparseAutoencoder_name=None, FcSparseEncoder_name=None):
        
        if FcSparseAutoencoder_name != None:
            self.FcSparseAutoencoder.save(FcSparseAutoencoder_name + '.h5')
        else:
            print("FcSparseAutoencoder is not saved !")
        if FcSparseEncoder_name != None:
            self.FcSparseEncoder.save(FcSparseEncoder_name + '.h5')
        else:
            print("FcSparseEncoder is not saved !")
        
    def load_model(self, FcSparseAutoencoder_name=None, FcSparseEncoder_name=None):
        
        if FcSparseAutoencoder_name != None:
            self.FcSparseAutoencoder = load_model(FcSparseAutoencoder_name + '.h5')
        else:
            print("FcSparseAutoencoder is not load !")
        if FcSparseEncoder_name != None:
            self.FcSparseEncoder = load_model(FcSparseEncoder_name + '.h5')
        else:
            print("FcSparseEncoder is not load !")
        
if __name__ == '__main__':

    # load data and preprocess
    data = load_wine().data
    StandardScaler = preprocessing.StandardScaler().fit(data)
    train_data = StandardScaler.transform(data)
    
    # Build a SparseAutoencoder
    SparseAutoencoder = FcSparseAutoencoder(train_data, [20, 10, 20])
    SparseAutoencoder.construct_model()
    
    # Train model
    SparseAutoencoder.train_model()
    
    # Save model
    SparseAutoencoder.save_model('SparseAutoencoder', 'SparseEncoder')
    
    # Get features & reconstructions
    Features = SparseAutoencoder.get_features(train_data)
    Reconstructions = SparseAutoencoder.get_reconstructions(train_data)
    