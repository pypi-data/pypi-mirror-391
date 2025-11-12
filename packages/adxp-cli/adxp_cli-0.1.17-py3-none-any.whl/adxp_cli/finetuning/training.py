from adxp_cli.auth.service import get_credential
from adxp_sdk.auth.credentials import ApiKeyCredentials
from adxp_sdk.finetuning.hub import AXFineTuningHub
import click

# Create AXFineTuningHub instance with credentials
def get_finetuning_hub(use_backend_ai: bool = False):
    headers, config = get_credential()
    # Use credentials-based authentication
    credentials = ApiKeyCredentials(
        api_key=config.token,
        base_url=config.base_url
    )
    return AXFineTuningHub(credentials, use_backend_ai=use_backend_ai)

# [Training 관련]
def create_training(training_data: dict, use_backend_ai: bool = False):
    """Create a new training"""
    try:
        hub = get_finetuning_hub(use_backend_ai=use_backend_ai)
        result = hub.create_training(training_data)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to create training: {e}")

def list_trainings(page=1, size=10, sort=None, filter=None, search=None, ids=None, use_backend_ai: bool = False):
    """List all trainings"""
    try:
        hub = get_finetuning_hub(use_backend_ai=use_backend_ai)
        result = hub.get_trainings(page=page, size=size, sort=sort, filter=filter, search=search, ids=ids)
        click.secho("✅ Trainings listed", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to list trainings: {e}")

def get_training(training_id: str, use_backend_ai: bool = False):
    """Get a training by ID"""
    try:
        hub = get_finetuning_hub(use_backend_ai=use_backend_ai)
        result = hub.get_training_by_id(training_id)
        click.secho("✅ Training retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get training: {e}")

def update_training(training_id: str, training_data: dict, use_backend_ai: bool = False):
    """Update a training"""
    try:
        hub = get_finetuning_hub(use_backend_ai=use_backend_ai)
        result = hub.update_training(training_id, training_data)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to update training: {e}")

def delete_training(training_id: str, use_backend_ai: bool = False):
    """Delete a training"""
    try:
        hub = get_finetuning_hub(use_backend_ai=use_backend_ai)
        result = hub.delete_training(training_id)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to delete training: {e}")

def get_training_status(training_id: str, use_backend_ai: bool = False):
    """Get training status"""
    try:
        hub = get_finetuning_hub(use_backend_ai=use_backend_ai)
        result = hub.get_training_status(training_id)
        click.secho("✅ Training status retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get training status: {e}")

def start_training(training_id: str, use_backend_ai: bool = False):
    """Start a training"""
    try:
        hub = get_finetuning_hub(use_backend_ai=use_backend_ai)
        result = hub.start_training(training_id)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to start training: {e}")

def stop_training(training_id: str, use_backend_ai: bool = False):
    """Stop a training"""
    try:
        hub = get_finetuning_hub(use_backend_ai=use_backend_ai)
        result = hub.stop_training(training_id)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to stop training: {e}")

def force_stop_training(training_id: str, use_backend_ai: bool = False):
    """Force stop a training"""
    try:
        hub = get_finetuning_hub(use_backend_ai=use_backend_ai)
        result = hub.force_stop_training(training_id)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to force stop training: {e}")