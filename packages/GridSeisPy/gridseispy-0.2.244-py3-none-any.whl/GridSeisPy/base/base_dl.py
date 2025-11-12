import pytorch_lightning as pl
from pathlib import Path
import torch
from typing import Annotated
from pytorch_lightning.callbacks import ModelCheckpoint, CustomProgressBar

from .base_config import BaseConfig



class PLDataModule(pl.LightningDataModule):
    class DefaultConfig(BaseConfig):
        pass 

    def __init__(self, config_dict: dict=None):
        super().__init__()
        # 配置参数, 如果config_dict为None, 则使用默认配置
        cfg = self.DefaultConfig() if config_dict is None else self.DefaultConfig.from_dict(config_dict)
        self.cfg: self.DefaultConfig = cfg

    def setup(self, stage: str):
        raise NotImplementedError("子类必须实现此方法")

    def sparse_collate_fn(self, batch):
        pass

    def train_dataloader(self):
        raise NotImplementedError("子类必须实现此方法")
    
    def val_dataloader(self):
        raise NotImplementedError("子类必须实现此方法")

    def test_dataloader(self):
        pass


class PLModel(pl.LightningModule):
    class DefaultConfig(BaseConfig):
        pass 

    def __init__(self, config_dict: dict=None):
        super().__init__()
        self.save_hyperparameters(config_dict)
        cfg = self.DefaultConfig() if config_dict is None else self.DefaultConfig.from_dict(config_dict)
        self.cfg: self.DefaultConfig = cfg


    def get_scaler(self):
        """获取标准化参数"""
        raise NotImplementedError("子类必须实现此方法")

# 获取当前文件所在目录，然后构建相对路径
_BASE_DIR = Path(__file__).parent.parent  # Modeling 目录
_DATASET_DIR = _BASE_DIR / "dataset"
_OUTPUT_DIR = _BASE_DIR / "out"
class PLTrainer(object):

    class DefaultConfig(BaseConfig):
        # 不变参数
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # 必设参数

        # 基础参数
        experiment_name: Annotated[str, '模型参数文件名称'] = 'PLTrainer-test1'
        max_epochs: Annotated[int, '最大训练轮数'] = 20
        cache_path: Annotated[str, '缓存路径'] = str(_OUTPUT_DIR)
        output_dir: Annotated[str, '输出目录'] = str(_DATASET_DIR / "grid_model" / "predictions")

        # 训练器参数
        monitor: Annotated[str, '监控指标'] = 'val/attr'
        accelerator: Annotated[str, '加速器'] = 'auto'
        precision: Annotated[str, '精度'] = 'bf16-mixed' if torch.cuda.is_available() else 32
        gradient_clip_val: Annotated[float|int, '梯度裁剪值'] = 1.0
        log_every_n_steps: Annotated[int, '日志记录步数'] = 10

    def __init__(self, cfg_dict: dict=None):
        cfg = self.DefaultConfig() if cfg_dict is None else self.DefaultConfig.from_dict(cfg_dict)
        self.cfg: PLTrainer.DefaultConfig = cfg

        # 初始化回调函数
        self.checkpoint_callback = ModelCheckpoint(
            monitor=self.cfg.monitor,  # 监控验证损失（无斜杠键，便于引用）
            dirpath=Path(self.cfg.cache_path) / 'checkpoints',
            filename=self.cfg.experiment_name + '-best-{epoch:02d}-{monitor:.4f}',
            save_top_k=1,
            mode='min',
            save_last=True,  # 保存最后一个检查点以供恢复
        )

        # 初始化进度条回调函数
        self.progress_bar_callback = CustomProgressBar()  

        # 初始化日志记录器
        self.logger = pl.loggers.TensorBoardLogger(Path(self.cfg.cache_path) / 'logs', name=self.cfg.experiment_name)

        # 初始化训练器
        self.trainer = pl.Trainer(
            max_epochs=self.cfg.max_epochs,
            accelerator=self.cfg.accelerator,
            precision=self.cfg.precision,
            gradient_clip_val=self.cfg.gradient_clip_val,
            callbacks=[self.checkpoint_callback, self.progress_bar_callback],
            logger=self.logger,
            log_every_n_steps=self.cfg.log_every_n_steps
            )
    def _get_best_checkpoint_path(self) -> str:
        """
        获取最佳检查点文件路径
        
        问题说明：
        - ModelCheckpoint 的 best_model_path 和 last_model_path 只在训练过程中设置
        - 如果重新创建 PLTrainer 实例，这些属性是空的（初始化为空字符串）
        - 因此需要从文件系统中查找检查点文件
        
        查找顺序：
        1. 尝试使用 checkpoint_callback 的属性（如果训练刚完成，这些属性可能有值）
        2. 从配置的 dirpath 中查找检查点文件（可靠方案）
        """
        checkpoints_dir = Path(self.checkpoint_callback.dirpath) if self.checkpoint_callback.dirpath else Path(self.cfg.cache_path) / 'checkpoints'
        
        # 方法1: 尝试使用 checkpoint_callback 的属性（仅在训练刚完成后有效）
        if self.checkpoint_callback.last_model_path:
            last_path = self.checkpoint_callback.last_model_path
            if Path(last_path).exists():
                return last_path
        
        if self.checkpoint_callback.best_model_path:
            best_path = self.checkpoint_callback.best_model_path
            if Path(best_path).exists():
                return best_path
        
        # 方法2: 从文件系统查找（可靠方案，适用于重新运行脚本的情况）
        # 优先查找最佳模型文件（文件名包含 "best"）
        best_ckpt_files = list(checkpoints_dir.glob(f'{self.cfg.experiment_name}-best-*.ckpt'))
        if best_ckpt_files:
            # 按修改时间排序，取最新的（最新的就是最好的）
            best_ckpt_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return str(best_ckpt_files[0])
        
        # 方法3: 如果找不到最佳模型，尝试使用最后一个检查点
        last_ckpt = checkpoints_dir / 'last.ckpt'
        if last_ckpt.exists():
            return str(last_ckpt)
        
        # 如果都找不到，抛出详细的错误信息
        raise FileNotFoundError(
            f"找不到模型检查点文件。请确保已完成训练。\n"
            f"检查点目录: {checkpoints_dir}\n"
            f"期望的文件模式: {self.cfg.experiment_name}-best-*.ckpt 或 last.ckpt\n"
            f"当前 ModelCheckpoint 状态（可能为空，因为这是新创建的实例）:\n"
            f"  - last_model_path: '{self.checkpoint_callback.last_model_path}'\n"
            f"  - best_model_path: '{self.checkpoint_callback.best_model_path}'"
        )


    def train(self, model: PLModel, data_module: PLDataModule):
        raise NotImplementedError("子类必须实现此方法")

    def predict(self):
        raise NotImplementedError("子类必须实现此方法")