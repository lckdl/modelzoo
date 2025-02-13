# YAML params for PyTorch models

## Model params

### Common

| Parameter Name | Description |
| --- | --- |
| mixed_precision | Whether to use mixed precision training or not. (`bool`, optional) Default: `None` |
| use_bfloat16 | Whether to use bfloat16 data type instead of float32. See [more](https://docs.cerebras.net/en/latest/general/cs-1-data-formats.html?#bfloat16-floating-type) (`bool`, optional) Default: `False` |

### Transformer based models

| Parameter Name | Description | Supported Models |
| --- | --- | --- |
| allow_multireplica | Whether to allow multiple replicas for the same graph. See [more](https://docs.cerebras.net/en/latest/original/general/multi-replica-data-parallel-training.html). This param is same as `multireplica` in [runconfig section](#runconfig-params). (`bool`, optional)  Default: `False` | Pipeline mode only |
| attention_dropout_rate | Dropout rate for attention layer. (`float`, optional) Default: same as `dropout` | All |
| attention_kernel | Attention kernel to use. Accepted values: <br> `None` - compiler selects the kernel.<br>`"default"` - Default implementation.<br>`"optimized_beta"` - Optimized implementation. Beta feature, support is limited.<br>(`str`/`None`, optional) Default: `None` | All |
| attention_softmax_fp32 | Whether to use fp32 precision for attention softmax. (`bool`, optional)  Default: `True`) | All |
| attention_type | Type of attention. Accepted values:<br>`"dot_product"`<br>`"scaled_dot_product"`.<br>(`str`,  optional) Default: `"scaled_dot_product"` | All |
| d_ff | Size of the intermediate feed forward layer in each `T5Block`. (`int`,  optional) Default: `2048` | T5, Transformer |
| d_kv | Size of the query/key/value projections per attention head. `d_kv` does *not* have to be equal to `d_model//num_heads`. (`int`,  optional) Default: `64` | T5, Transformer |
| d_model | The number of expected features in the encoder/decoder inputs. (`int`,  optional) Default `512` | All |
| decoder_nonlinearity | Type of nonlinearity to be used in decoder. (`str`,  optional) Default: `"relu"` | T5, Transformer |
| decoder_num_hidden_layers | Number of hidden layers in the Transformer decoder. Will use the same value as `num_layers` if not set. (`int`, optional) | T5, Transformer |
| disable_nsp | Whether to disable the next sentence prediction task. (`bool`, optional) Default: False | BERT (pre-training, fine-tuning) |
| dropout_rate | The dropout probability for all fully connected layers. (`float`, optional), Default: `0.1` | All |
| embedding_dropout_rate | Dropout rate for embeddings. (`float`, optional) Default: `0.1` | All |
| embedding_initializer | Initializer to use for embeddings. See [supported initializers](./common/pytorch/model_utils/create_initializer.py). (`str`, optional) Default: "normal" | GPT2, GPT3, GPTJ |
| enable_vts | Whether to enable variable tensor shapes. See [more](https://docs.cerebras.net/en/latest/pytorch-docs/pytorch-vts.html). (`bool`, optional) Default: `False` | Pipeline mode only: BERT (pre-training), T5, Transformer |
| encoder_nonlinearity | Type of nonlinearity to be used in encoder. (`str`, optional) Default: varies per model | BERT (pre-training, fine-tuning), T5, Transformer |
| encoder_num_hidden_layers  | Number of hidden layers in the encoder. (`int`, optional) Default: `6` | T5, Transformer |
| extra_ids | The number of extra ids used for additional vocabulary items  (`int`, optional) Default: `0` | T5, Transformer
| filter_size |  Dimensionality of the feed-forward layer in the Transformer block. (`int`, optional) Default: `3072` |  BERT (pre-training, fine-tuning), GPT2, GPT3, GPTJ |
| hidden_size | The size of the transformer hidden layers (`int`, optional) Default: `768` |  BERT (pre-training, fine-tuning), GPT2, GPT3, GPTJ |
| initializer | The initializer to be used for all the initializers used in the model. See [supported initializers](./common/pytorch/model_utils/create_initializer.py). (`str`, optional) Default: varies based on model | BERT (pre-training, fine-tuning), GPT2, GPT3, GPTJ |
| initializer_range | The standard deviation of the truncated_normal_initializer as the default initializer. (`float`, optional) Default: `0.02` | BERT (pre-training), GPT2, GPT3, GPTJ |
| layer_norm_epsilon | The epsilon value used in layer normalization layers. (`float`, optional) Default: `1e-5`)| All |
| lm_loss_weight | Value that scales loss by the mean number of predictions per sequence in the dataset. This number varies per dataset and can be calculated by getting the reciprocal of average number of tokens per sequence in the training dataset. This is only needed when setting loss scaling to `"batch_size"`.  (`float`, optional) Default: `1.0` | T5, Transformer |
| loss_scaling | The scaling type used to calculate the loss. Accepts: <br> `batch_size`, `num_tokens`. See [more](https://docs.cerebras.net/en/latest/wsc/general/num-tokens-loss-scaling.html). (`str`, optional) Default: `num_tokens` | GPT2, GPT3, GPTJ |
| loss_weight | The weight for the loss scaling when `loss_scaling: "batch_size"`, generally set to `1/max_sequence_length`. (`float`, optional) Default: `1.0` | GPT2, GPT3, GPTJ |
| max_position_embeddings | The maximum sequence length that the model can handle. (`int`, optional) Default: `1024` | All |
| mlm_loss_scaling | A string specifying the scaling factor type used for the language modeling loss. Accepts one of: `"num_masked"` - uses the off-the shelf loss scaling by number of valid (non-padding) tokens the cross entropy loss function (applicable in weight streaming mode only), `"precomputed_num_masked"` - uses loss scaling from the computed num valid masks in the data loader, when enabling `dynamic_loss_weight` in the data loader params, `"batch_size"` - uses loss scaling by `"batch_size"` and `lm_loss_weight` should be provided when using `"batch_size"`. (`str`, optional) Default: `"batch_size"` | T5, Transformer |
| mlm_loss_weight | The weight for the masked language modeling loss used when scaling the loss with `"batch_size"`. This number varies per dataset and can be calculated by getting the reciprocal of average number of masked tokens per sequence in the training dataset. (`float`, optional) Default: `1.0` | BERT (pre-training) |
| nonlinearity | The non-linear activation function used in the feed forward network in each transformer block. See list of non-linearity functions [here](https://pytorch.org/docs/stable/nn.html#non-linear-activations-weighted-sum-nonlinearity). Some may have to use `autogen_policy: "medium"`. (`str`, optional) Default: varies per model | BERT (pre-training, fine-tuning), GPT2, GPT3, GPTJ |
| num_heads | The number of attention heads in the multi-head attention layer. (`int`, optional) Default: varies per model| All |
| num_hidden_layers | Number of hidden layers in the Transformer encoder/decoder. (`int`, optional) Default: `12` | All |
| output_layer_initializer | The name of the initializer for the weights of the output layer. See [supported initializers](./common/pytorch/model_utils/create_initializer.py). (str, optional) Default: varies based on model | GPT2, GPT3, GPTJ |
| position_embedding_type | The type of position embedding to use in the model. Can be one of: `"fixed"` - Sinusoidal from original [Transformer](https://arxiv.org/abs/1706.03762), `"relative"` - Relative position embedding, [to exploit pairwise, relative positional information](https://arxiv.org/abs/1803.02155)., `"rotary"` - a.k.a [RoPE](https://arxiv.org/pdf/2104.09864v4.pdf) , `"learned"` - Learned embedding matrix, `None` (`str`, optional) Default: varies per model | All |
| precision_opt_level | Setting to control the level of numerical precision used for training runs for large NLP models in weight-streaming. See [more](https://docs.cerebras.net/en/latest/general/performance-optimization.html?#precision-optimization-level). (`int`, optional) Default: `1` | Weight streaming mode only |
| relu_dropout_rate | The dropout rate for ReLU activation function. (`float`, optional) Default: varies per model | T5, Transformer |
| residual_dropout_rate | The dropout rate for residual connections. (`float`, optional) Default: `0.1` | GPTJ |
| rotary_dim | The number of dimensions used for the rotary position encoding. Must be an even number. (`int`, optional) Default: `None` | GPTJ |
| share_embedding_weights | Whether to share the embedding weights between the input and out put embedding. (`bool`, optional) Default: `True` | All |
| share_encoder_decoder_embedding | Whether to share the embedding weights between the encoder and decoder (`bool`, optional) Default: `True`| T5, Transformer |
| src_vocab_size | The size of the source vocabulary. Max supported value: `512000`. (`int`, optional) Default: `32128` | T5, Transformer |
| tgt_vocab_size | The size of the target vocabulary. Max supported value: `512000`. (`int`, optional) Default: `32128` | T5, Transformer |
| use_bias_in_output | Whether to use bias in the final output layer. (`bool`, optional) Default: `False` | GPT2, GPT3, GPTJ |
| use_dropout_outside_residual_path | Whether to set dropout calculations outside of the residual path. (`bool`, optional) Default: `True` for T5, `False` for Transformer | T5, Transformer |
| use_ffn_bias | Whether to use bias in the feedforward network (FFN). (`bool`, optional) Default: varies per model | All |
| use_ffn_bias_in_attention | Whether to include bias in the attention layer for feed-forward network (FFN). (`bool`, optional) Default: varies per model | All |
| use_position_embedding | Whether to use position embedding in the model. (`bool`, optional) Default: `True` | GPT2, GPT3 |
| use_pre_encoder_decoder_dropout | Whether to use dropout layer after positional embedding layer and encoder/decoder. (`bool`, optional) Default: `False` | T5, Transformer |
| use_pre_encoder_decoder_layer_norm | Whether to use layer norm before passing input tensors into encoder/decoder. (`bool`, optional) Default: `True` | T5, Transformer |
| use_projection_bias_in_attention | Whether to include bias in the attention layer for projection.  (`bool`, optional) Default: varies per model | All |
| use_t5_layer_norm | Whether to use T5 layer norm (with no mean subtraction and bias correction) or use the regular `nn.LayerNorm` module. (`bool`, optional) Default: `False` | T5, Transformer |
| use_transformer_initialization | The Transformer model tends to converge best with a scaled variant on Xavier uniform initialization used for linear layers. This contrasts the initialization used for the original T5 paper, which uses He normal initialization for linear layers. Setting this flag to `True` switches the initialization to the Transformer specific scaled Xavier initialization. (`bool`, optional) Default: `False` | T5, Transformer |
| use_untied_layer_norm | Whether to use untied layer normalization. (`bool`, optional) Default: `False` | GPTJ |
| vocab_size | The size of the vocabulary used in the model. Max supported value: `512000`. (`int`, optional) Default: varies per model | All |

### Computer Vision models

| Parameter | Description | Supported Models |
| --- | --- | --- |
| bias_initializer | Initializer for the bias. (`str`, optional) Default: `"zeros"` | UNet |
| convs_per_block | List of conv specifications for each conv in the block. (`List[str]`, required) | UNet |
| decoder_filters | List of filter sizes for each block in the decoder. (`List[str]`, required) | UNet |
| downscale_bottleneck | Whether to downsample the spatial dimensions in the UNet bottleneck block. (`bool`, optional) Default: `False`| UNet |
| downscale_encoder_blocks | Determine whether each block in the Encoder includes downsampling. Length of the list must correspond to the number of UNetBlocks in the Encoder. If a single bool is provided, all blocks will use this value. (`bool`/`List[bool]`, optional) Default: `True` | UNet |
| downscale_first_conv | If True, the first convolution operation in each UNetBlock will be downscaled. If False, the last convolution in each UNetBlock will be downscaled. (`bool`, optional) Default: `False` | UNet |
| downscale_method | Downscaling method at the end of each block. One of  `"max_pool"` or `"strided_conv"`. (`str`, optional) Default: `"max_pool"` | UNet |
| enable_bias | Whether to include a bias operation following convolution layers. By default, bias will only be included when no normalization is used after the convolution layers. | UNet |
| encoder_filters | List of filter sizes for each block in the encoder. (`List[str]`, required) | UNet |
| eval_ignore_classes | List of classes to ignore during evaluation of model. (`List[int]`, optional) | UNet |
| eval_metrics | List of evaluation metrics to use during training and validation. Available options are accuracy (`Acc`), mean IOU (`mIOU`) or Dice (`DSC`).  (`List[str]`, optional). | UNet |
| initializer | Initializer for the convolution weights. See [supported initializers](./common/pytorch/model_utils/create_initializer.py) (`str`, required) | UNet |
| input_channels | Number of channels in the input images to the model. (`int`, required) | UNet |
| loss |  Loss type, supported: values: `"bce"`, `"multilabel_bce"`, `"ssce"` (`str`, required) | UNet |
| nonlinearity | Activation function used in the model following convolutions in the encoder and decoder. (`str`, required) | UNet |
| norm_kwargs | args to be passed to norm layers during initialization. For <br>`norm_type` = `group`, `norm_kwargs` must include `num_groups` key value pair. <br>`norm_type` = `layer`, `norm_kwargs` must include `normalized_shape` key value pair. <br>(`dict`, optional) Default: `None` | UNet |
| norm_layer | Type of normalization to be used. See [supported norm layers]](./vision/pytorch/layers/normalizations.py). (`str`, optional) Default: `"batchnorm2d"` | UNet |
| residual_blocks | Flag for using residual connections at the end of each block. (`bool`, optional) Default: `False` | UNet |
| skip_connect | Flag for if the model concatenates encoder outputs to decoder inputs. (`bool`, optional) Default: `True` | UNet |
| use_conv3d | Whether to use 3D convolutions in the model. (`bool`, optional) Default: `False` | UNet |

## Data loader params

### Common

| Parameter Name | Description |
| --- | --- |
| batch_size | Batch size of the data. (`int`, required) |
| data_dir | Path/s to the data files to use. (`str`/`List[str]`, required) |
| data_processor | Name of the data processor to be used. (`str`, required)  |
| mixed_precision | Flag to cast input to fp16. (`bool`, optional) Default: `None` | All |
| num_workers | Number of workers to use in the dataloader. See [more](https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader). (`int`, optional) Default: `0` |
| persistent_workers | For multi-worker dataloader controls if the workers are recreated at the end of each epoch (see [PyTorch docs](https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader)). (`bool`, optional) Default: `True` |
| prefetch_factor |  Number of samples loaded in advance by each worker. (`int`, optional) Default: `10` |
| shuffle | Flag to enable data shuffling. (`bool`, optional) Default: `True` |
| shuffle_buffer | Size of shuffle buffer in samples. (`int`, optional) Default: `10 * batch_size` |
| shuffle_seed | Shuffle seed. (`int`, optional) Default: `None` |

### Transformers

| Parameter Name | Description | Supported Models |
| --- | --- | --- |
| buckets | A list of boundaries for sequence lengths to bucket together in order to speed up VTS/VSL. (`list`, optional) Default: `None` | BERT (pre-training), T5, Transformer <br> (only pipeline execution)|
| do_lower | Flag to lower case the texts. (`bool`, optional) Default: `False` | BERT (pre-training, fine-tuning), T5, Transformer |
| dynamic_loss_weight | Flag to dynamically scale the loss. If set, will divide the loss for a token by the length of the sequence that the token comes from. Use with `"precomputed_num_tokens"` loss scaling. (`bool`, optional) Default: `False` | T5, Transformer |
| dynamic_mlm_scale | Flag to dynamically scale the loss. If set, MLM Loss is scaled by the number of masked tokens in the current batch using the `masked_lm_weights` from the input data features.  (`bool`, optional) Default: `False` | BERT (pre-training) |
| extra_ids | Number of sentinel tokens for T5 objective. (`int`, optional) Default: `0` | T5, Transformer |
| masked_lm_prob  | Ratio of the masked tokens over the sequence length. (`float`, optional) Default: `0.15`| BERT (pre-training) |
| max_predictions_per_seq  |  Maximum number of masked tokens per sequence. (`int`, required) | BERT (pre-training) |
| max_sequence_length  | Maximum sequence length of the input data. (`int`, optional) Default: varies per model | All |
| src_data_dir | Path to directory containing all the files of tokenized data for source sequence. (`str`, required) | T5, Transformer |
| src_max_sequence_length | Largest possible sequence length for the input source sequence. If longer it will be truncated. All other sequences padded to this length. (`int`, required) | T5, Transformer |
| src_vocab_file | Path to vocab file for source input. (`str`, required) | T5, Transformer |
| tgt_data_dir | Path to directory containing all the files of tokenized data for target sequence. (`str`, required) | T5, Transformer |
| tgt_max_sequence_length | Largest possible sequence length for the input target sequence. If longer it will be truncated. All other sequences padded to this length. (`int`, required) | T5, Transformer |
| tgt_vocab_file | Path to vocab file for target input. (`str`, required) | T5, Transformer |
| vocab_file | Path to vocab file. (`str`, required) | BERT (pre-training, fine-tuning) |
| vocab_size | The size of the vocabulary used in the model. (`int`, required) | BERT (pre-training, fine-tuning) |

### Computer Vision

| Parameter Name | Description | Supported Models |
| --- | --- | --- |
| aggregate_cartilage | For SKM-TEA dataset only. Combines medial and lateral classes into single class. (`bool`, optional) Default: `True` | UNet |
| augment_data | Apply data augmentation to the data. (`bool`, optional) Default: `True` | UNet |
| class_id | For the Severstal Dataset this sets which class id to be considered as the positive class. All other classes will be considered negative examples. (`int`, optional) | UNet |
| echo_type | For SKM-TEA dataset only. Specifies training data configuration. Allowed options are: `echo1`, `echo2`, or `root_sum_of_squares`. (`str`, required) Default: `echo1` | UNet |
| image_shape | Expected shape of output images in format (H, W, C), (`List[int]`, required) | UNet |
| normalize_data_method | Specify the strategy to normalize the input data. One of: `"zero_centered"`,`"zero_one"`,`"standard_score"`. (`str`, required) | UNet |
| num_classes | Number of classes in the training dataset. (`int`, required) | UNet |
| train_test_split | Percentage of data to be used in the training dataset. | UNet |
| use_fast_dataloader | If set to True, mapstyle datasets that use the UNetDataProcessor perform faster data processing. (`bool`, optional) Default: `False` | UNet |
| use_worker_cache | If set to True data will be read from local SSD memory on the individual worker nodes during training. If the data does not exist on the worker nodes it will be automatically copied from the host node. This will cause a slowdown the first time this copy takes place. (`bool`, optional) Default: `True` | UNet |

## Optimizer params

| Parameter Name | Description |
| --- | --- |
| initial_loss_scale | Initial loss scale to be used in the grad scale. (`int`, optional) Default: `2 ** 15` |
| learning_rate | Learning rate scheduler to be used. See [supported LR schedulers](https://docs.cerebras.net/en/latest/pytorch-docs/pytorch-ops/supported-pt-learning-rate-schedulers.html). (`dict`, required) |
| log_summaries | Flag to log per layer gradient norm in Tensorboard (`bool`, optional) Default: `False` |
| loss_scaling_factor | Loss scaling factor for gradient calculation in learning step. (`float`/`str`, optional) Default: `1.0` |
| max_gradient_norm | Max norm of the gradients for learnable parameters. Used for gradient clipping.(`float`, optional) Default: `None` |
| min_loss_scale | The minimum loss scale value that can be chosen by dynamic loss scaling. (`float`, optional) Default: `None` |
| max_loss_scale | The maximum loss scale value that can be chosen by dynamic loss scaling. (`float`, optional) Default: `None` |
| optimizer_type | Optimizer to be used. See [supported optimizers](https://docs.cerebras.net/en/latest/pytorch-docs/pytorch-ops/supported-pytorch-optimizers.html). (`str`, required) |

## Runconfig params

| Key | Description | Supported mode |
| --- | --- | --- |
| autogen_policy | The autogen policy for weight streaming appliance mode. <br>Can be one of: `"default"`, `"disabled"`, `"mild"`, `"medium"`, `"aggressive"`. See [more](https://docs.cerebras.net/en/latest/wsc/general/autogen.html).<br> (`str`, optional) Default: `None` | CSX (weight streaming) |
| autoload_last_checkpoint | Flag to automatically load the last checkpoint in the `model_dir`. (`bool`, optional) Default: `True` | All |
| check_loss_values | Flag to check the loss values to see if it is `Nan/inf`. (`bool`, optional) Default: `True` | All | 
| checkpoint_path | The path to load checkpoints from during training. (`str`, optional) Default: `None` | All |
| checkpoint_steps | The number of steps between saving model checkpoints during training. `0` means no checkpoints saved. (`int`, optional) Default: `0` | All |
| compile_dir | Compile directory where compile artifacts will be written. (`str`, optional) Default: `None` | All |
| compile_only | Enables compile only workflow. (`bool`, optional) Default: `False` | All |
| credentials_path | Credentials for cluster access. If `None`, the value from a pre-configured location will be used if available. (`str`, optional) Default: `None`| CSX |
| debug_args_path | ath to debugs args file.  (`str`, optional) Default: `None` | CSX |
| dist_addr | To init master_addr and master_port of distributed. (`str`, optional) Default: `localhost:8888` | GPU |
| dist_backend | Distributed backend engine. (`str`, optional) Default: `"nccl"` | GPU |
| enable_distributed | Flag to enable distributed training on GPU. (`bool`, optional) Default: `False` | GPU |
| enable_summaries | Enable summaries when running on CS-X hardware. (`bool`, optional) Default: `False` | CSX |
| eval_frequency | Specifies the evaluation frequency during training. Only used for `train_and_eval` mode.  (`int`, optional) Default: `None` | All |
| eval_steps | Specifies the number of steps to run the model evaluation. (`int`, optional) Default: `None` | All |
| execution_strategy | Specifies the execution strategy for CS-X run. One of: `"weight_streaming"`, `"pipeline"`. Default: Set through command line | CSX |
| experimental_api | Flag to enable experimental PyTorch API. (`bool`, optional) Default: `False` | CSX |
| init_method | URL specifying how to initialize the process group. (`str`, optional) Default: `"env://"` | GPU |
| is_pretrained_checkpoint | Flag indicating that the provided checkpoint is from a pre-training run. <br>If set, training will begin from step `0` after loading the matching weights from the checkpoint and ignoring the optimizer state if present in the checkpoint.  (`bool`, optional) Default: `False` | All |
| job_labels | A list of equal-sign-separated key value pairs served as job labels. (`str`, optional) Default: `None` | CSX |
| log_steps | Specifies the number of steps between logging during training. Same number controls the summary steps in Tensorboard. (`int`, optional) Default: `None` | All |
| logging | Specifies the logging level during training. (`str`, optional) Default: `"INFO"` | All |
| max_steps | Specifies the maximum number of steps for training. `max_steps` is optional unless neither `num_epochs` nor `num_steps` are provided, in which case `max_steps` must be provided. (`int`, required) | All |
| mgmt_address | The address of the management service used for coordinating the training job as `<host>:<port>`. (`str`, optional) | CSX |
| mode | The mode of the training job, either '`"train"`', '`"eval"`', `"eval_all"` or `"train_and_eval"`. (`str`, required) | All |
| model_dir | The directory where the model checkpoints and other metadata will be saved during training. (`str`, optional) Default: `./model_dir` | All |
| mount_dirs | A list of paths to be mounted to the appliance containers. It should generally contain path to the directory containing the Cerebras model zoo and data dir. (`List[str]`, optional) Default: `None` | CSX |
| multireplica | Whether to allow multiple replicas for the same graph. See [more](https://docs.cerebras.net/en/latest/original/general/multi-replica-data-parallel-training.html). This param is same as `allow_multireplica` in [model section](#model-params). (`bool`, optional)  Default: `False` | CSX (pipeline mode) |
| num_act_servers |  Number of activation servers per CS-X dedicated to stream samples to the WSE. Input workers stream data to these activation servers, and the activation servers to hold and further stream the data to the WSE. For LLMs, we generally choose 1 because they're compute-bound. For CV models we choose a higher number, a crude rule of thumb is to have one activation server for every 4 workers (i.e. `num_workers_per_csx // 4 if num_workers_per_csx > 4, else 1`). It is suggested to keep the default values for this param when possible. (`int`, optional) Default: `1` | CSX |
| num_csx | The number of CSX systems to use in Cerebras WSE cluster. (`int`, optional) Default: `1` | CSX (weight streaming) |
| num_epochs | The number of epochs to train for. (`int`, optional) Default: `None` | All |
| num_replicas | The number of replicas to use in multi-replica mode. (`int`, optional) Default: `-1` | CSX (pipeline) |
| num_steps | The number of steps to train for. (`int`, optional) Default: `None` | All |
| num_wgt_servers | Upper bound on the number of MemoryX servers used for storing the model weights. Compilation may choose a smaller number depending on the model topology. A sensible upper bound (currently 24) is selected if a value is not provided. (`int`, optional) Default: `None` | CSX (weight streaming) |
| num_workers_per_csx | Number of input workers, per CSX, to use for streaming samples. This setting depends on whether the model is compute-bound or input-bound and how efficient the dataloader implementation is. For compute-bound models (e.g., LLM), even 1 input worker per csx is enough to saturate the input buffers on CSX systems. But for smaller models a larger number may be used. For Weight Streaming execution strategy, we currently default to 1 worker per CSX and for Pipeline execution strategy we default to 8, which is the max supported. (`int`, optional) Default: `0` | CSX |
| python_paths | A list of paths to be exported into `PYTHONPATH` for worker containers. It should generally contain path to the directory containing the Cerebras model zoo. (`List[str]`, optional) Default: `None` | CSX |
| save_initial_checkpoint | Whether to save an initial checkpoint before training starts. (`bool`, optional) Default: `False` | All |
| save_losses | Whether to save the loss values during training. (`bool`, optional) Default: `True` | All |
| seed | The seed to use for random number generation for reproducibility. (`int`, optional) Default: `None` | All |
| steps_per_epoch | The number of steps per epoch. (`int`, optional) Default: `None` | All |
| sync_batchnorm | Whether to use synchronized batch normalization on multi GPU setup. (`bool`, optional) Default: `False` | GPU |
| target_device | The target device to run the training on. One of: `CPU`, `GPU`, `CSX`. Required in command line. (`str`, optional) Default: command line value | All |
| use_cs_grad_accum | Whether to use gradient accumulation to support larger batch sizes. (`bool`, optional) Default: `False` | CSX |
| validate_only | Enables validate only workflow, stops the compilation at kernel matching stage for weight streaming mode and at the graph optimization stage. (`bool`, optional) Default: `False` | CSX |
