# -*- encoding:utf-8 -*-
# Copyright (c) Alibaba, Inc. and its affiliates.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import logging
import os
import time

import numpy as np
import tensorflow as tf
from tensorflow.python.platform import gfile

from easy_rec.python.inference.predictor_cs import Predictor
from easy_rec.python.protos.dataset_pb2 import DatasetConfig
from easy_rec.python.utils import config_util
from easy_rec.python.utils import numpy_utils
# from easy_rec.python.utils.check_utils import check_split
from easy_rec.python.utils.input_utils import get_type_defaults
from easy_rec.python.utils.tf_utils import get_tf_type

from easy_rec.python.inference.predictor_cs import SINGLE_PLACEHOLDER_FEATURE_KEY  # NOQA

if tf.__version__ >= '2.0':
  tf = tf.compat.v1


class TFRecordPredictor(Predictor):

  def __init__(self,
               model_path,
               data_config,
               with_header=False,
               ds_vector_recall=False,
               fg_json_path=None,
               profiling_file=None,
               selected_cols=None,
               output_sep=chr(1)):
    super(TFRecordPredictor, self).__init__(model_path, profiling_file,
                                            fg_json_path)
    self._output_sep = output_sep
    self._ds_vector_recall = ds_vector_recall
    input_type = DatasetConfig.InputType.Name(data_config.input_type).lower()
    self._with_header = with_header
    self._data_config = data_config
    if 'rtp' in input_type:
      self._is_rtp = True
      self._input_sep = self._data_config.rtp_separator
    else:
      self._is_rtp = False
      self._input_sep = self._data_config.separator

    if selected_cols and not ds_vector_recall:
      self._selected_cols = [int(x) for x in selected_cols.split(',')]
    elif ds_vector_recall:
      self._selected_cols = selected_cols.split(',')
    else:
      self._selected_cols = None
    self.get_type_defaults = get_type_defaults
    self._get_feature_desc()

  def _get_feature_desc(self):
    input_fields = [x for x in self._data_config.input_fields]
    while len(self._data_config.input_fields) > 0:
      self._data_config.input_fields.pop()
    for field in input_fields:
      tmp_names = config_util.auto_expand_names(field.input_name)
      for tmp_name in tmp_names:
        if tmp_name == 'label':
          continue
        one_field = DatasetConfig.Field()
        one_field.CopyFrom(field)
        one_field.input_name = tmp_name
        self._data_config.input_fields.append(one_field)

    self._input_fields = [x.input_name for x in self._data_config.input_fields]
    self._input_dims = [x.input_dim for x in self._data_config.input_fields]
    self._input_field_types = [
        x.input_type for x in self._data_config.input_fields
    ]
    self._input_field_defaults = [
        x.default_val for x in self._data_config.input_fields
    ]
    self.feature_desc = {}
    for x, t, d, s in zip(self._input_fields, self._input_field_types,
                          self._input_field_defaults, self._input_dims):
      d = self.get_type_defaults(t, d)
      t = get_tf_type(t)
      if s == 1:
        self.feature_desc[x] = tf.FixedLenFeature(
            dtype=t, shape=[s], default_value=d)
      else:
        self.feature_desc[x] = tf.FixedLenFeature(
            dtype=t, shape=[s], default_value=[d] * s)

  def _get_reserved_cols(self, reserved_cols):
    if reserved_cols == 'ALL_COLUMNS':
      if self._is_rtp:
        if self._with_header:
          reserved_cols = self._all_fields
        else:
          idx = 0
          reserved_cols = []
          for x in range(len(self._record_defaults) - 1):
            if not self._selected_cols or x in self._selected_cols[:-1]:
              reserved_cols.append(self._input_fields[idx])
              idx += 1
            else:
              reserved_cols.append('no_used_%d' % x)
          reserved_cols.append(SINGLE_PLACEHOLDER_FEATURE_KEY)
      else:
        reserved_cols = self._all_fields
    else:
      reserved_cols = [x.strip() for x in reserved_cols.split(',') if x != '']
    return reserved_cols

  def _parse_tfrecord(self, example):
    try:
      inputs = tf.parse_single_example(example, features=self.feature_desc)
    except AttributeError:
      inputs = tf.io.parse_single_example(example, features=self.feature_desc)
    return inputs

  def _get_num_cols(self, file_paths):
    # try to figure out number of fields from one file
    num_cols = -1
    with gfile.GFile(file_paths[0], 'r') as fin:
      num_lines = 0
      for line_str in fin:
        line_tok = line_str.strip().split(self._input_sep)
        if num_cols != -1:
          assert num_cols == len(line_tok), (
              'num selected cols is %d, not equal to %d, current line is: %s, please check input_sep and data.'
              % (num_cols, len(line_tok), line_str))
        num_cols = len(line_tok)
        num_lines += 1
        if num_lines > 10:
          break
    logging.info('num selected cols = %d' % num_cols)
    return num_cols

  def _get_dataset(self, input_path, num_parallel_calls, batch_size, slice_num,
                   slice_id):
    # file_paths = []
    # for path in input_path.split(','):
    #   for x in gfile.Glob(path):
    #     if not x.endswith('_SUCCESS'):
    #       file_paths.append(x)
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

    def get_file_path_list(root_path):
      file_list = []
      _get_file_path(root_path, file_list)
      return file_list

    file_paths = get_file_path_list(input_path)
    assert len(file_paths) > 0, 'match no files with %s' % input_path

    if self._with_header:
      with gfile.GFile(file_paths[0], 'r') as fin:
        for line_str in fin:
          line_str = line_str.strip()
          self._field_names = line_str.split(self._input_sep)
          break
      print('field_names: %s' % ','.join(self._field_names))
      self._all_fields = self._field_names
    elif self._ds_vector_recall:
      self._all_fields = self._selected_cols
    else:
      self._all_fields = self._input_fields
    if self._is_rtp:
      num_cols = self._get_num_cols(file_paths)
      self._record_defaults = ['' for _ in range(num_cols)]
      if not self._selected_cols:
        self._selected_cols = list(range(num_cols))
      for col_idx in self._selected_cols[:-1]:
        col_name = self._input_fields[col_idx]
        default_val = self._get_defaults(col_name)
        self._record_defaults[col_idx] = default_val
    else:
      self._record_defaults = [
          self._get_defaults(col_name) for col_name in self._all_fields
      ]
    data_compression_type = self._data_config.data_compression_type
    dataset = tf.data.Dataset.from_tensor_slices(file_paths)
    parallel_num = min(num_parallel_calls, len(file_paths))
    dataset = dataset.interleave(
        lambda x: tf.data.TFRecordDataset(
            x, compression_type=data_compression_type),
        cycle_length=parallel_num,
        num_parallel_calls=parallel_num)
    dataset = dataset.shard(slice_num, slice_id)

    for feature in self._reserved_cols:
      self.feature_desc[feature] = tf.FixedLenFeature(
          dtype=tf.string, shape=[1], default_value='P')

    dataset = dataset.map(
        self._parse_tfrecord, num_parallel_calls=num_parallel_calls)

    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(buffer_size=64)

    return dataset

  def _get_writer(self, output_path, slice_id):
    if not gfile.Exists(output_path):
      gfile.MakeDirs(output_path)
    res_path = os.path.join(output_path, 'part-%d.csv' % slice_id)
    table_writer = gfile.GFile(res_path, 'w')
    # table_writer.write(
    #     self._output_sep.join(self._output_cols + self._reserved_cols) + '\n')
    return table_writer

  def _write_lines(self, table_writer, outputs):
    # outputs = '\n'.join(
    #     [self._output_sep.join([str(i) for i in output]) for output in outputs])
    # table_writer.write(outputs + '\n')
    table_writer.write(outputs)

  def _get_reserve_vals(self, reserved_cols_all, outputs, output_vals,
                        score_filter, len_data, start_flag):

    out_put_str = ''
    cnt = 0
    for i in range(len_data):
      score = outputs[i]
      if score >= score_filter:
        for j in range(len(reserved_cols_all)):
          c = reserved_cols_all[j]
          if j == 0:
            if start_flag == 0 and cnt == 0:
              out_put_str += f'{output_vals[c][i]}{self._output_sep}'
            else:
              out_put_str += f'\n{output_vals[c][i]}{self._output_sep}'
          else:
            out_put_str += f'{output_vals[c][i]}{self._output_sep}'
        out_put_str += f'{round(score, 8)}'
      cnt += 1
    return out_put_str

  @property
  def out_of_range_exception(self):
    return (tf.errors.OutOfRangeError)

  def predict_impl(
      self,
      input_path,
      output_path,
      reserved_cols='',
      reserved_cols_all='',
      score_filter=0.0,
      output_cols=None,
      batch_size=1024,
      slice_id=0,
      slice_num=1,
  ):
    if output_cols is None or output_cols == 'ALL_COLUMNS':
      self._output_cols = sorted(self._predictor_impl.output_names)
      logging.info('predict output cols: %s' % self._output_cols)
    else:
      # specified as score float,embedding string
      tmp_cols = []
      for x in output_cols.split(','):
        if x.strip() == '':
          continue
        tmp_keys = x.strip().split(' ')
        tmp_cols.append(tmp_keys[0].strip())
      self._output_cols = tmp_cols

    with tf.Graph().as_default(), tf.Session() as sess:
      num_parallel_calls = 8
      self._reserved_args = reserved_cols
      self._reserved_cols = self._get_reserved_cols(reserved_cols)
      dataset = self._get_dataset(input_path, num_parallel_calls, batch_size,
                                  slice_num, slice_id)
      if hasattr(tf.data, 'make_one_shot_iterator'):
        iterator = tf.data.make_one_shot_iterator(dataset)
      else:
        iterator = dataset.make_one_shot_iterator()
      all_dict = iterator.get_next()

      # input_names = self._predictor_impl.input_names
      table_writer = self._get_writer(output_path, slice_id)

      def _parse_value(all_vals):
        outputs_vals = {}
        for feature in self._reserved_cols:
          outputs_vals[feature] = all_vals.pop(feature)
        return all_vals, outputs_vals

      progress = 0
      sum_t0, sum_t1, sum_t2 = 0, 0, 0

      start_flag = 0
      while True:
        try:
          ts0 = time.time()
          all_vals = sess.run(all_dict)

          ts1 = time.time()
          input_vals, output_vals = _parse_value(all_vals)
          outputs = self._predictor_impl.predict(input_vals, self._output_cols)
          for x in self._output_cols:
            if outputs[x].dtype == np.object:
              outputs[x] = [val.decode('utf-8') for val in outputs[x]]
            elif len(outputs[x].shape) == 2 and outputs[x].shape[1] == 1:
              # automatic flatten only one element array
              outputs[x] = [val[0] for val in outputs[x]]
            elif len(outputs[x].shape) > 1:
              outputs[x] = [
                  json.dumps(val, cls=numpy_utils.NumpyEncoder)
                  for val in outputs[x]
              ]
          # # 输出 顺序 ifa,ip_max,osv_max,language,make,ua  ,score
          # for k in self._reserved_cols:
          #   if k in reserved_cols_all:
          #     pass
          #   else:
          #     raise Exception(f"reserved_cols_all:{reserved_cols_all},k:{k}")

          len_data = len(output_vals['ifa'])
          reserved_cols_all_list = reserved_cols_all.split(',')
          for c in reserved_cols_all_list:
            if c in output_vals and output_vals[c].dtype == np.object:
              output_vals[c] = [
                  val[0].decode('utf-8',
                                errors='ignore').replace('|', '').replace(
                                    '\\', '').replace('"',
                                                      '').replace('\n', '')
                  for val in output_vals[c]
              ]
            else:
              output_vals[c] = ['' for i in range(len_data)]

          ts2 = time.time()
          end_vals = self._get_reserve_vals(reserved_cols_all_list,
                                            outputs['label'], output_vals,
                                            score_filter, len_data, start_flag)
          if end_vals != '':
            start_flag = 1

          # logging.info('predict size: %s' % len(outputs))
          self._write_lines(table_writer, end_vals)

          ts3 = time.time()
          progress += 1
          sum_t0 += (ts1 - ts0)
          sum_t1 += (ts2 - ts1)
          sum_t2 += (ts3 - ts2)
        except self.out_of_range_exception:
          break
        if progress % 10000 == 0:
          logging.info('progress: batch_num=%d sample_num=%d' %
                       (progress, progress * batch_size))
          logging.info('time_stats: read: %.2f predict: %.2f write: %.2f' %
                       (sum_t0, sum_t1, sum_t2))
      logging.info('Final_time_stats: read: %.2f predict: %.2f write: %.2f' %
                   (sum_t0, sum_t1, sum_t2))
      table_writer.close()
      self.load_to_table(output_path, slice_num, slice_id)
      logging.info('Predict %s done.' % input_path)
