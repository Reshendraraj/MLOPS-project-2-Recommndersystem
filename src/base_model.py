from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Dot, Flatten, Dense, Activation, BatchNormalization
from src.logger import get_logger
from src.custom_exception import CustomException
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class BaseModel:
    def __init__(self, config_path):
        try:
            self.config = read_yaml(config_path)
            logger.info("Loaded configuration from config.yaml")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise CustomException("Error loading configuration", e)

    def RecommenderNet(self, n_users, n_anime):
        try:
            # Extract embedding size and model parameters from config
            embedding_size = self.config["model"]["embedding_size"]
            loss = self.config["model"]["loss"]
            optimizer = self.config["model"]["optimizer"]
            metrics = self.config["model"]["metrics"]

            logger.info(f"Creating model with {n_users} users and {n_anime} anime")
            logger.info(f"Embedding size: {embedding_size}")
            logger.info(f"Loss function: {loss}")
            logger.info(f"Optimizer: {optimizer}")
            logger.info(f"Metrics: {metrics}")
            logger.info(f"Number of users: {n_users}, Number of anime: {n_anime}")

            # Define Inputs
            user = Input(name="user", shape=[1])
            anime = Input(name="anime", shape=[1])

            # Embedding layers for users and anime
            user_embedding = Embedding(name="user_embedding", input_dim=n_users, output_dim=embedding_size)(user)
            anime_embedding = Embedding(name="anime_embedding", input_dim=n_anime, output_dim=embedding_size)(anime)

            # Dot product for the interactions
            x = Dot(name="dot_product", normalize=True, axes=2)([user_embedding, anime_embedding])
            x = Flatten()(x)

            # Dense layer followed by BatchNormalization and Activation
            x = Dense(1, kernel_initializer='he_normal')(x)
            x = BatchNormalization()(x)
            x = Activation("sigmoid")(x)

            # Create model with user and anime as inputs
            model = Model(inputs=[user, anime], outputs=x)

            # Compile model with loss, optimizer, and metrics from config
            model.compile(
                loss=loss,
                optimizer=optimizer,
                metrics=metrics
            )

            logger.info("Model created and compiled successfully.")
            return model
        except KeyError as e:
            logger.error(f"Configuration missing key: {e}")
            raise CustomException(f"Missing key in configuration: {e}")
        except Exception as e:
            logger.error(f"Error occurred during model architecture: {e}")
            raise CustomException("Failed to create model", e)
