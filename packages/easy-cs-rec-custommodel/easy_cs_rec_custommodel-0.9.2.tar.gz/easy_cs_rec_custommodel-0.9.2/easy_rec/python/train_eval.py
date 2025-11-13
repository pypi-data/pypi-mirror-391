# -*- encoding:utf-8 -*-
# Copyright (c) Alibaba, Inc. and its affiliates.
import argparse
import json
import logging
import os
import sys
import warnings

import tensorflow as tf

from easy_rec.python.main import _train_and_evaluate_impl
from easy_rec.python.protos.pipeline_pb2 import EasyRecConfig
from easy_rec.python.protos.train_pb2 import DistributionStrategy
from easy_rec.python.utils import config_util
from easy_rec.python.utils import ds_util
from easy_rec.python.utils import estimator_utils
from easy_rec.python.utils import fg_util
from easy_rec.python.utils import hpo_util
from easy_rec.python.utils.config_util import process_neg_sampler_data_path
from easy_rec.python.utils.config_util import set_eval_input_path
from easy_rec.python.utils.config_util import set_train_input_path

py_root_dir_path = os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
print(f'py_root_dir_path:{py_root_dir_path}')
sys.path.append(py_root_dir_path)

logging.basicConfig(level=logging.INFO)
warnings.filterwarnings('ignore')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

if tf.__version__.startswith('1.'):
  from tensorflow.python.platform import gfile
else:
  import tensorflow.io.gfile as gfile

from easy_rec.python.utils.distribution_utils import set_tf_config_and_get_train_worker_num_on_ds  # NOQA

if tf.__version__ >= '2.0':
  tf = tf.compat.v1

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)

logging.basicConfig(
    format='[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d : %(message)s',
    level=logging.INFO)


def _get_file_path(root_path, file_list):
  # 获取该目录下所有的文件名称和目录名称
  dir_or_files = os.listdir(root_path)
  for dir_file in dir_or_files:
    # 获取目录或者文件的路径
    dir_file_path = os.path.join(root_path, dir_file)
    # 判断该路径为文件还是路径
    if os.path.isdir(dir_file_path):
      # 递归获取所有文件和目录的路径
      _get_file_path(dir_file_path, file_list)
    else:
      if not str(dir_file_path).__contains__('_SUCCESS'):
        file_list.append(dir_file_path)


def get_vocab_list(vocab_path):
  with gfile.GFile(vocab_path, 'r') as fin:
    vocabulary_list = [str(line).strip() for line in fin]
    return vocabulary_list


def get_file_path_list(root_path):
  file_list = []
  _get_file_path(root_path, file_list)
  return file_list


def change_pipeline_config(pipeline_config: EasyRecConfig):
  for data in pipeline_config.feature_config.features:
    # print("****"*10)
    vocab_file = data.vocab_list
    if vocab_file:
      vocab_file_new = get_file_path_list(
          f'{data_root_path_input}/{vocab_file.pop()}')[0]
      # print(vocab_file_new)
      vocab_list = get_vocab_list(vocab_file_new)
      for vocab in vocab_list:
        data.vocab_list.append(vocab)

  train_input_path = f'{data_root_path_input}/{pipeline_config.train_input_path}'
  train_input_path_new = get_file_path_list(train_input_path)
  pipeline_config.train_input_path = ','.join(train_input_path_new)

  eval_input_path = f'{data_root_path_input}/{pipeline_config.eval_input_path}'
  eval_input_path_new = get_file_path_list(eval_input_path)
  pipeline_config.eval_input_path = ','.join(eval_input_path_new)

  model_dir = pipeline_config.model_dir
  pipeline_config.model_dir = f'{data_root_path_output}/{model_dir}'

  pipeline_config.data_config.batch_size = batch_size
  pipeline_config.data_config.num_epochs = num_epochs

  pipeline_config.train_config.log_step_count_steps = int(train_sample_cnt /
                                                          batch_size)
  pipeline_config.train_config.save_checkpoints_steps = int(train_sample_cnt /
                                                            batch_size)

  pipeline_config.train_config.optimizer_config[
      0].adam_optimizer.learning_rate.exponential_decay_learning_rate.initial_learning_rate = initial_learning_rate


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--pipeline_config_path',
      type=str,
      # default="/Users/chensheng/PycharmProjects/EasyRec/samples/model_config/deepfm_on_criteo_tfrecord.config",
      default='/Users/chensheng/PycharmProjects/EasyRec/samples/model_config/custom_model.config',
      help='Path to pipeline config file.')

  parser.add_argument(
      '--pkg_label',
      type=str,
      default='aaa194_THA_ios_20250927_20251011(test)',
      help='Path to pipeline config file.')

  parser.add_argument(
      '--data_root_path_input',
      type=str,
      default='/Users/chensheng/PycharmProjects/EasyRec/data/test/cs_data')

  parser.add_argument(
      '--data_root_path_output',
      type=str,
      default='/Users/chensheng/PycharmProjects/EasyRec/data/test/cs_data/output'
  )

  parser.add_argument(
      '--train_sample_cnt',
      type=int,
      default=27000,
      help='训练集合的样本数,该数与save_checkpoints_steps 数值相等')

  parser.add_argument(
      '--batch_size',
      type=int,
      default=3000,
  )

  parser.add_argument(
      '--num_epochs',
      type=int,
      default=1,
  )
  parser.add_argument(
      '--initial_learning_rate',
      type=float,
      default=0.001,
  )

  parser.add_argument(
      '--continue_train',
      action='store_true',
      default=False,
      help='continue train using existing model_dir')
  parser.add_argument(
      '--hpo_param_path',
      type=str,
      default=None,
      help='hyperparam tuning param path')
  parser.add_argument(
      '--hpo_metric_save_path',
      type=str,
      default=None,
      help='hyperparameter save metric path')
  parser.add_argument(
      '--model_dir',
      type=str,
      default=None,
      help='will update the model_dir in pipeline_config')
  parser.add_argument(
      '--train_input_path',
      type=str,
      nargs='*',
      default=None,
      help='train data input path')
  parser.add_argument(
      '--eval_input_path',
      type=str,
      nargs='*',
      default=None,
      help='eval data input path')
  parser.add_argument(
      '--fit_on_eval',
      action='store_true',
      default=False,
      help='Fit evaluation data after fitting and evaluating train data')
  parser.add_argument(
      '--fit_on_eval_steps',
      type=int,
      default=None,
      help='Fit evaluation data steps')
  parser.add_argument(
      '--fine_tune_checkpoint',
      type=str,
      default=None,
      help='will update the train_config.fine_tune_checkpoint in pipeline_config'
  )
  parser.add_argument(
      '--edit_config_json',
      type=str,
      default=None,
      help='edit pipeline config str, example: {"model_dir":"experiments/",'
      '"feature_config.feature[0].boundaries":[4,5,6,7]}')
  parser.add_argument(
      '--ignore_finetune_ckpt_error',
      action='store_true',
      default=False,
      help='During incremental training, ignore the problem of missing fine_tune_checkpoint files'
  )
  parser.add_argument(
      '--odps_config', type=str, default=None, help='odps config path')
  parser.add_argument(
      '--is_on_ds', action='store_true', default=False, help='is on ds')
  parser.add_argument(
      '--check_mode',
      action='store_true',
      default=False,
      help='is use check mode')
  parser.add_argument(
      '--selected_cols', type=str, default=None, help='select input columns')
  parser.add_argument('--gpu', type=str, default=None, help='gpu id')
  args, extra_args = parser.parse_known_args()

  data_root_path_input = args.data_root_path_input
  data_root_path_output = args.data_root_path_output

  train_sample_cnt = args.train_sample_cnt
  batch_size = args.batch_size
  num_epochs = args.num_epochs
  initial_learning_rate = args.initial_learning_rate
  pkg_label = args.pkg_label

  if args.gpu is not None:
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu

  edit_config_json = {}
  if args.edit_config_json:
    edit_config_json = json.loads(args.edit_config_json)

  if extra_args is not None and len(extra_args) > 0:
    config_util.parse_extra_config_param(extra_args, edit_config_json)

  if args.pipeline_config_path is not None:
    pipeline_config = config_util.get_configs_from_pipeline_file(
        args.pipeline_config_path, False)
    if args.selected_cols:
      pipeline_config.data_config.selected_cols = args.selected_cols
    if args.model_dir:
      pipeline_config.model_dir = args.model_dir
      logging.info('update model_dir to %s' % pipeline_config.model_dir)
    if args.train_input_path:
      set_train_input_path(pipeline_config, args.train_input_path)
    if args.eval_input_path:
      set_eval_input_path(pipeline_config, args.eval_input_path)

    if args.fine_tune_checkpoint:
      ckpt_path = estimator_utils.get_latest_checkpoint_from_checkpoint_path(
          args.fine_tune_checkpoint, args.ignore_finetune_ckpt_error)

      if ckpt_path:
        pipeline_config.train_config.fine_tune_checkpoint = ckpt_path

    if pipeline_config.fg_json_path:
      fg_util.load_fg_json_to_config(pipeline_config)

    if args.odps_config:
      os.environ['ODPS_CONFIG_FILE_PATH'] = args.odps_config

    if len(edit_config_json) > 0:
      fine_tune_checkpoint = edit_config_json.get('train_config', {}).get(
          'fine_tune_checkpoint', None)
      if fine_tune_checkpoint:
        ckpt_path = estimator_utils.get_latest_checkpoint_from_checkpoint_path(
            args.fine_tune_checkpoint, args.ignore_finetune_ckpt_error)
        edit_config_json['train_config']['fine_tune_checkpoint'] = ckpt_path
      config_util.edit_config(pipeline_config, edit_config_json)

    process_neg_sampler_data_path(pipeline_config)

    if args.is_on_ds:
      ds_util.set_on_ds()
      set_tf_config_and_get_train_worker_num_on_ds()
      if pipeline_config.train_config.fine_tune_checkpoint:
        ds_util.cache_ckpt(pipeline_config)

    if pipeline_config.train_config.train_distribute in [
        DistributionStrategy.HorovodStrategy,
    ]:
      estimator_utils.init_hvd()
    elif pipeline_config.train_config.train_distribute in [
        DistributionStrategy.EmbeddingParallelStrategy,
        DistributionStrategy.SokStrategy
    ]:
      estimator_utils.init_hvd()
      estimator_utils.init_sok()

    if args.hpo_param_path:
      with gfile.GFile(args.hpo_param_path, 'r') as fin:
        hpo_config = json.load(fin)
        hpo_params = hpo_config['param']
        config_util.edit_config(pipeline_config, hpo_params)
      config_util.auto_expand_share_feature_configs(pipeline_config)
      _train_and_evaluate_impl(pipeline_config, args.continue_train,
                               args.check_mode)
      hpo_util.save_eval_metrics(
          pipeline_config.model_dir,
          metric_save_path=args.hpo_metric_save_path,
          has_evaluator=False)
    else:

      change_pipeline_config(pipeline_config)
      if args.continue_train:
        pass
      else:
        model_dir = pipeline_config.model_dir
        print(f'model_dir:{model_dir}')
        os.system(f'rm -rf {model_dir}')

      config_util.auto_expand_share_feature_configs(pipeline_config)
      _train_and_evaluate_impl(
          pkg_label,
          pipeline_config,
          args.continue_train,
          args.check_mode,
          fit_on_eval=args.fit_on_eval,
          fit_on_eval_steps=args.fit_on_eval_steps)
  else:
    raise ValueError('pipeline_config_path should not be empty when training!')
