# easy_rec/python/model/custom_model.py

import tensorflow as tf

from easy_rec.python.model.easy_rec_model import EasyRecModel

if tf.__version__ >= '2.0':
  tf = tf.compat.v1


class MultiHeadAttention(tf.compat.v1.keras.layers.Layer):

  def __init__(self, num_heads, d_model):
    super(MultiHeadAttention, self).__init__()
    self.num_heads = num_heads
    self.d_model = d_model

    assert d_model % num_heads == 0

    self.depth = d_model // num_heads

    self.wq = tf.compat.v1.keras.layers.Dense(d_model)
    self.wk = tf.compat.v1.keras.layers.Dense(d_model)
    self.wv = tf.compat.v1.keras.layers.Dense(d_model)

    self.dense = tf.compat.v1.keras.layers.Dense(d_model)

  def split_heads(self, x, batch_size):
    x = tf.reshape(x, (batch_size, 15, self.num_heads, self.depth))
    return tf.transpose(x, perm=[0, 2, 1, 3])

  def __call__(self, q, k, v, mask):
    batch_size = tf.shape(q)[0]

    q = self.wq(q)
    k = self.wk(k)
    v = self.wv(v)

    q = self.split_heads(q, batch_size)
    k = self.split_heads(k, batch_size)
    v = self.split_heads(v, batch_size)

    scaled_attention, attention_weights = self.scaled_dot_product_attention(
        q, k, v, mask)

    scaled_attention = tf.transpose(scaled_attention, perm=[0, 2, 1, 3])
    concat_attention = tf.reshape(scaled_attention,
                                  (batch_size, 15, self.d_model))

    output = self.dense(concat_attention)

    return output, attention_weights

  def scaled_dot_product_attention(self, q, k, v, mask):
    matmul_qk = tf.matmul(q, k, transpose_b=True)

    dk = tf.cast(tf.shape(k)[-1], tf.float32)
    scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)

    if mask is not None:
      scaled_attention_logits += (mask * -1e9)

    attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)

    output = tf.matmul(attention_weights, v)

    return output, attention_weights


class CustomModel(EasyRecModel):

  def __init__(self,
               model_config,
               feature_configs,
               features,
               labels=None,
               is_training=False):
    super(CustomModel, self).__init__(model_config, feature_configs, features,
                                      labels, is_training)
    self.drop_out_rate = 0.05
    self._raw_features, self._raw_feature_lst = self._input_layer(
        self._feature_dict, 'raw_feature')
    self._seq_features, _, _ = self._input_layer(
        self._feature_dict, 'seq_feature', is_combine=False)
    self._multi_head_1_features, _, _ = self._input_layer(
        self._feature_dict, 'multi_head_feature_1', is_combine=False)
    self._multi_head_2_features, _, _ = self._input_layer(
        self._feature_dict, 'multi_head_feature_2', is_combine=False)

    self._seq_features_concat = self._get_features_concat(
        self._get_seq_features_reduce(
            self._seq_features, reduce_type='mean', axis=1, keepdims=False),
        axis=-1)

    self._multi_head_1_features_concat = self._get_features_concat(
        self._get_seq_features_reduce(
            self._multi_head_1_features,
            reduce_type='mean',
            axis=1,
            keepdims=True),
        axis=1)

    self._multi_head_2_features_concat = self._get_features_concat(
        self._get_seq_features_reduce(
            self._multi_head_2_features,
            reduce_type='mean',
            axis=1,
            keepdims=True),
        axis=1)

    self._multi_head_1_layer = MultiHeadAttention(4, 12)
    self._multi_head_2_layer = MultiHeadAttention(4, 12)

    self._multi_head_1_output, _ = self._multi_head_1_layer(
        self._multi_head_1_features_concat, self._multi_head_1_features_concat,
        self._multi_head_1_features_concat, None)

    self._multi_head_2_output, _ = self._multi_head_2_layer(
        self._multi_head_2_features_concat, self._multi_head_2_features_concat,
        self._multi_head_2_features_concat, None)

    self._multi_head_1_output_end = self._get_seq_feature_reduce(
        self._multi_head_1_output, reduce_type='mean', axis=1, keepdims=False)
    self._multi_head_2_output_end = self._get_seq_feature_reduce(
        self._multi_head_2_output, reduce_type='mean', axis=1, keepdims=False)

    self._features_list_1 = [
        self._raw_features, self._seq_features_concat,
        self._multi_head_1_output_end, self._multi_head_2_output_end
    ]
    self.deep_input = self._get_features_concat(self._features_list_1, axis=-1)

  def _get_seq_features_reduce(self, seq_features, reduce_type, axis: int,
                               keepdims: bool):
    assert reduce_type in ['mean', 'sum',
                           'max'], 'reduce_type  must in mean | sum | max'
    assert axis in [-1, 1, 2], 'axis  must in -1 | 1 | 2'
    seq_features_reduce = []
    for feature in seq_features:
      if reduce_type == 'mean':
        seq_features_reduce.append(
            tf.reduce_mean(feature[0], axis=axis, keepdims=keepdims))
      elif reduce_type == 'sum':
        seq_features_reduce.append(
            tf.reduce_sum(feature[0], axis=axis, keepdims=keepdims))
      elif reduce_type == 'max':
        seq_features_reduce.append(
            tf.reduce_max(feature[0], axis=axis, keepdims=keepdims))
      else:
        pass
    return seq_features_reduce

  def _get_seq_feature_reduce(self, seq_feature, reduce_type, axis: int,
                              keepdims: bool):
    assert reduce_type in ['mean', 'sum',
                           'max'], 'reduce_type  must in mean | sum | max'
    assert axis in [-1, 1, 2], 'axis  must in -1 | 1 | 2'
    if reduce_type == 'mean':
      return tf.reduce_mean(seq_feature, axis=axis, keepdims=keepdims)
    elif reduce_type == 'sum':
      return tf.reduce_sum(seq_feature, axis=axis, keepdims=keepdims)
    elif reduce_type == 'max':
      return tf.reduce_max(seq_feature, axis=axis, keepdims=keepdims)
    else:
      pass

  def _get_features_concat(self, features, axis):
    assert axis in [-1, 1, 2], 'axis  must in -1 | 1 | 2'
    return tf.concat(features, axis=axis)

  def build_predict_graph(self):
    # build forward graph
    dnn_1_list = self.get_layer_1(
        self.deep_input, '1:64', prefix='dnn_1_1', n=1)

    dnn_1_2_list = self.get_layer_n(
        dnn_1_list, '1:32', prefix='dnn_1_2', branch_num=2)

    dnn_1_3_list = self.get_layer_n(
        dnn_1_2_list, '1:16', prefix='dnn_1_3', branch_num=2)

    dnn_1_4_list = self.get_layer_n(
        dnn_1_3_list, '1:8', prefix='dnn_1_4', branch_num=2)
    dnn_1_5_list = self.get_layer_n(
        dnn_1_4_list, '1:4', prefix='dnn_1_5', branch_num=2)
    dnn_1_concat = tf.concat(dnn_1_5_list, axis=-1, name='dnn_1_concat')
    dnn_2_1 = tf.keras.layers.Dense(
        units=32, activation='relu', name='dnn_layer_2_1')(
            dnn_1_concat)
    if self.drop_out_rate == 0:
      dnn_2_1_dropout = dnn_2_1
    else:
      dnn_2_1_dropout = tf.keras.layers.Dropout(
          self.drop_out_rate, noise_shape=None, seed=None)(
              dnn_2_1)

    dnn_2_2 = tf.keras.layers.Dense(
        units=16, activation='relu', name='dnn_layer_2_2')(
            dnn_2_1_dropout)
    if self.drop_out_rate == 0:
      dnn_2_2_dropout = dnn_2_2
    else:
      dnn_2_2_dropout = tf.keras.layers.Dropout(
          self.drop_out_rate, noise_shape=None, seed=None)(
              dnn_2_2)

    dnn_2_3 = tf.keras.layers.Dense(
        units=8, activation='relu', name='dnn_layer_2_3')(
            dnn_2_2_dropout)
    if self.drop_out_rate == 0:
      dnn_2_3_dropout = dnn_2_3
    else:
      dnn_2_3_dropout = tf.keras.layers.Dropout(
          self.drop_out_rate, noise_shape=None, seed=None)(
              dnn_2_3)

    dnn_1_sig = tf.keras.layers.Dense(
        units=1, activation='sigmoid', name='dnn_1_sig')(
            dnn_2_3_dropout)

    self._prediction_dict['label'] = dnn_1_sig
    return self._prediction_dict

  def build_loss_graph(self):
    # assert self._model_config.loss_type == LossType.CLASSIFICATION
    loss = tf.keras.losses.BinaryFocalCrossentropy(gamma=2, from_logits=False)
    label = list(self._labels.values())[0]

    self._loss_dict['custom_loss'] = loss(label, self._prediction_dict['label'])

    return self._loss_dict

  def build_metric_graph(self, eval_config):
    metric_dict = {}
    num_thresholds = eval_config.metrics_set[0].auc.num_thresholds
    metric_dict['auc'] = tf.metrics.auc(
        list(self._labels.values())[0],
        self._prediction_dict['label'],
        num_thresholds=num_thresholds)
    return metric_dict

  def get_outputs(self):

    return ['label']

  def get_layer_1(self, input, dnn_layers, prefix, n=2):
    output_list = []
    dnn_layers_list = dnn_layers.split(',')
    for i in range(n):
      for j in range(len(dnn_layers_list)):
        dnn_info_list = dnn_layers_list[j].split(':')
        if j == 0:
          deep_layer = tf.keras.layers.Dense(
              units=int(dnn_info_list[1]),
              activation='relu',
              name=f'dnn_layer_{prefix}_{i}_{j}')(
                  input)

        else:
          deep_layer = tf.keras.layers.Dense(
              units=int(dnn_info_list[1]),
              activation='relu',
              name=f'dnn_layer_{prefix}_{i}_{j}')(
                  deep_layer)
      output_list.append(deep_layer)
    return output_list

  def get_layer_n(self, layer_output_list, dnn_layers, prefix, branch_num=2):
    output_list = []
    dnn_layers_list = dnn_layers.split(',')
    for branch in range(branch_num):
      for i in range(len(layer_output_list)):
        for j in range(len(dnn_layers_list)):
          dnn_info_list = dnn_layers_list[j].split(':')
          if j == 0:
            deep_layer = tf.keras.layers.Dense(
                units=int(dnn_info_list[1]),
                activation='relu',
                name=f'dnn_layer_{prefix}_{branch}_{i}_{j}')(
                    layer_output_list[i])

          else:
            deep_layer = tf.keras.layers.Dense(
                units=int(dnn_info_list[1]),
                activation='relu',
                name=f'dnn_layer_{prefix}_{branch}_{i}_{j}')(
                    deep_layer)
        # deep_layer_end = tf.concat([deep_layer,bundle_info_sum],axis=-1)
        if self.drop_out_rate == 0:
          deep_layer_dropout = deep_layer
        else:
          deep_layer_dropout = tf.keras.layers.Dropout(
              self.drop_out_rate, noise_shape=None, seed=None)(
                  deep_layer)
        output_list.append(deep_layer_dropout)

    return output_list
