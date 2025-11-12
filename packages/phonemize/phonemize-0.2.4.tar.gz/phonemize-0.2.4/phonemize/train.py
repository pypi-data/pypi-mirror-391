import os
from pathlib import Path

import torch
from torch.distributed import init_process_group

from phonemize.model.model import load_checkpoint, ModelType, \
    create_model
from phonemize.preprocessing.text import Preprocessor
from phonemize.training.trainer import Trainer
from phonemize.utils.io import read_config
from phonemize.utils.logging import get_logger

logger = get_logger(__name__)


def train(rank: int,
          num_gpus: int,
          config_file: str,
          checkpoint_file: str = None) -> None:
    """
    Runs training of a transformer model.

    Args:
      rank (int): Device id
      num_gpus (int): Number of devices
      config_file (str): Path to the config.yaml that stores all necessary parameters.
      checkpoint_file (str, optional): Path to a model checkpoint to resume training for (e.g. latest_model.pt)

    Returns:
        None: The model checkpoints are stored in a folder provided by the config.

    """

    config = read_config(config_file)

    # choose device early so checkpoints can be loaded onto the correct device
    device = torch.device(f'cuda:{rank}') if num_gpus > 0 else torch.device('cpu')

    # initialize distributed process group if requested
    if num_gpus > 1:
        # use safe lookups with sensible defaults
        master_addr = config['training'].get('ddp_host', '127.0.0.1')
        master_port = config['training'].get('ddp_port', 12355)
        os.environ["MASTER_ADDR"] = str(master_addr)
        os.environ["MASTER_PORT"] = str(master_port)
        init_process_group(backend=config['training'].get('ddp_backend', 'nccl'),
                           rank=rank,
                           world_size=num_gpus)

    if checkpoint_file is not None:
        logger.info(f'Restoring model from checkpoint: {checkpoint_file}')
        # load checkpoint onto the selected device
        model, checkpoint = load_checkpoint(checkpoint_file, device=device)
        model.train()
        step = checkpoint.get('step', 0)
        logger.info(f'Loaded model with step: {step}')
        # overwrite only when the checkpoint contains the key
        for key, val in config.get('training', {}).items():
            val_orig = checkpoint.get('config', {}).get('training', {}).get(key)
            if val_orig is not None and val_orig != val:
                logger.info(f'Overwriting training param: {key} {val_orig} --> {val}')
                checkpoint['config']['training'][key] = val
        config = checkpoint.get('config', config)
        model_type = ModelType(config['model']['type'])
    else:
        logger.info('Initializing new model from config...')
        preprocessor = Preprocessor.from_config(config)
        model_type = config['model']['type']
        model_type = ModelType(model_type)
        model = create_model(model_type, config=config)
        checkpoint = {
            'preprocessor': preprocessor,
            'config': config,
        }

    checkpoint_dir = Path(config['paths']['checkpoint_dir'])
    logger.info(f'Checkpoints will be stored at {checkpoint_dir.absolute()}')
    loss_type = 'cross_entropy' if model_type.is_autoregressive() else 'ctc'

    # device was chosen earlier

    use_ddp = True if num_gpus > 1 else False

    trainer = Trainer(checkpoint_dir=checkpoint_dir, device=device, rank=rank, use_ddp=use_ddp, loss_type=loss_type)
    trainer.train(model=model,
                  checkpoint=checkpoint,
                  store_phoneme_dict_in_model=config['training']['store_phoneme_dict_in_model'])
