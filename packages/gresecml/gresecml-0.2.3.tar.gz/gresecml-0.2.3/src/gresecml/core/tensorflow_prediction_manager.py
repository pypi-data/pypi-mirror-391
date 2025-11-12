import tensorflow as tf
import keras
from importlib import resources

def tensorflow_predict(input_data: dict) -> dict[str, float]:
    """Make predictions using a TensorFlow model and input data.
    
    Args:
        input_data (dict): Input data for making predictions.
    
    Returns:
        dict[str, float]: Dictionary of predictions made by the model. prediction_normal and prediction_portscan
    """
    # Load the TensorFlow model
    model = load_model()

    # Convert input data to tensors
    input_dict = {name: tf.convert_to_tensor([value]) for name, value in input_data.items()}

    # Make predictions
    try:
        preds = model(input_dict)
    except Exception:
        raise RuntimeError("Failed to make predictions with the TensorFlow model.")
    
    try:
        # Update output dictionary if more categories are added in the future
        output_dict = {
            "prediction_normal": float(preds[0][0]),
            "prediction_portscan": float(preds[0][1]),
        }
    except Exception:
        raise RuntimeError("Failed to process predictions from the TensorFlow model.")

    return output_dict


# Load TensorFlow model from package resources
def load_model():
    """Load TensorFlow model from package resources."""
    # Use with to get a temporary path to the model file
    with resources.path('gresecml.ml_models', 'tensorflow.keras') as model_path:
        model = keras.models.load_model(model_path)
    return model