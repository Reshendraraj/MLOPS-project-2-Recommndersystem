import joblib
import comet_ml
import os
import numpy as np
from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping
from src.logger import get_logger
from src.custom_exception import CustomException
from src.base_model import BaseModel
from config.paths_config import *
from tensorflow.keras import backend as K

logger = get_logger(__name__)

class ModelTraining:
    def __init__(self, data_path):
        self.data_path = data_path
        self.experiment = comet_ml.Experiment(
            api_key="CZU0KH5B5u9VUJQaOH1Gy7RlQ",
            project_name="mlops-project-2",
            workspace="reshendraraj"
        )
        logger.info("Model Training and COMET ML initialized..")
    
    def load_data(self):
        try:
            # Load training and testing data
            X_train_array = joblib.load(X_TRAIN_ARRAY)
            X_test_array = joblib.load(X_TEST_ARRAY)
            y_train = joblib.load(Y_TRAIN)
            y_test = joblib.load(Y_TEST)

            logger.info("Data loaded successfully for Model Training")
            return X_train_array, X_test_array, y_train, y_test
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise CustomException("Failed to load data", e)
        
    def train_model(self):
        try:
            X_train_array, X_test_array, y_train, y_test = self.load_data()

            # Get number of users and anime from the encoded data
            n_users = len(joblib.load(USER2USER_ENCODED))
            n_anime = len(joblib.load(ANIME2ANIME_ENCODED))

            # Initialize BaseModel
            base_model = BaseModel(config_path=CONFIG_PATH)
            model = base_model.RecommenderNet(n_users=n_users, n_anime=n_anime)

            # Learning rate scheduler configuration
            start_lr = 0.00001
            min_lr = 0.0001
            max_lr = 0.00005
            batch_size = 10000

            ramp_up_epochs = 5
            sustain_epochs = 0
            exp_decay = 0.8

            def lrfn(epoch):
                if epoch < ramp_up_epochs:
                    return (max_lr - start_lr) / ramp_up_epochs * epoch + start_lr
                elif epoch < ramp_up_epochs + sustain_epochs:
                    return max_lr
                else:
                    return (max_lr - min_lr) * exp_decay ** (epoch - ramp_up_epochs - sustain_epochs) + min_lr
            
            lr_callback = LearningRateScheduler(lrfn, verbose=0)

            # Model checkpoint and early stopping
            model_checkpoint = ModelCheckpoint(
                filepath=CHECKPOINT_FILE_PATH,
                save_weights_only=True,
                monitor="val_loss",
                mode="min",
                save_best_only=True
            )

            early_stopping = EarlyStopping(
                patience=3,
                monitor="val_loss",
                mode="min",
                restore_best_weights=True
            )

            my_callbacks = [model_checkpoint, lr_callback, early_stopping]

            # Create directories if they don't exist
            os.makedirs(os.path.dirname(CHECKPOINT_FILE_PATH), exist_ok=True)
            os.makedirs(MODEL_DIR, exist_ok=True)
            os.makedirs(WEIGHTS_DIR, exist_ok=True)

            # Train the model
            try:
                history = model.fit(
                    x=X_train_array,
                    y=y_train,
                    batch_size=batch_size,
                    epochs=10,
                    verbose=1,
                    validation_data=(X_test_array, y_test),
                    callbacks=my_callbacks
                )
                
                # Load best weights from checkpoint
                model.load_weights(CHECKPOINT_FILE_PATH)
                logger.info("Model training completed.")



                # Log metrics for each epoch
                for epoch in range(len(history.history['loss'])):
                    train_loss = history.history["loss"][epoch]
                    val_loss = history.history["val_loss"][epoch]

                    # Log training and validation loss
                    self.experiment.log_metric('train_loss', train_loss, step=epoch)
                    self.experiment.log_metric('val_loss', val_loss, step=epoch)

            except Exception as e:
                logger.error(f"Error during model training: {e}")
                raise CustomException("Model training failed", e)
            
            # Save model and weights after training
            self.save_model_weights(model)

        except Exception as e:
            logger.error(f"Error during model training process: {e}")
            raise CustomException("Error during Model Training Process", e)
        
    def extract_weights(self, layer_name, model):
        try:
            weight_layer = model.get_layer(layer_name)
            weights = weight_layer.get_weights()[0]
            weights = weights / np.linalg.norm(weights, axis=1).reshape((-1, 1))
            logger.info(f"Extracting weights for {layer_name}")
            return weights
        except Exception as e:
            logger.error(f"Error during weight extraction: {e}")
            raise CustomException("Error during weight extraction process", e)
    
    def save_model_weights(self, model):
        try:
            # Save the entire model
            model.save(MODEL_PATH)
            logger.info(f"Model saved to {MODEL_PATH}")

            # Extract weights from embedding layers
            user_weights = self.extract_weights('user_embedding', model)
            anime_weights = self.extract_weights('anime_embedding', model)

            # Save weights to files
            joblib.dump(user_weights, USER_WEIGHTS_PATH)
            joblib.dump(anime_weights, ANIME_WEIGHTS_PATH)

        

            # Log assets (model and weights) to COMET ML or other experiment tracker
            self.experiment.log_asset(MODEL_PATH)
            self.experiment.log_asset(ANIME_WEIGHTS_PATH)
            self.experiment.log_asset(USER_WEIGHTS_PATH)

            logger.info("User and Anime weights saved successfully....")
        except Exception as e:
            logger.error(f"Error during saving model and weights: {e}")
            raise CustomException("Error during saving model and weights process", e)

if __name__ == "__main__":
    model_trainer = ModelTraining(PROCESSED_DIR)
    model_trainer.train_model()
