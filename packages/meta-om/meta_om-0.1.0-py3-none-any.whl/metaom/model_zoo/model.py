import numpy as np
import acl

# 常量定义
NPY_FLOAT32 = 11
ACL_MEM_MALLOC_HUGE_FIRST = 0
ACL_MEMCPY_HOST_TO_DEVICE = 1
ACL_MEMCPY_DEVICE_TO_HOST = 2
ACL_SUCCESS = 0


class AscendModel:
    """Ascend模型封装类"""

    def __init__(self, model_path, device_id=0):
        """初始化模型"""
        self.device_id = device_id
        self.model_path = model_path
        self._initialized = False
        self._resources = {}

        try:
            self._initialize()
            self._load_model()
            self._initialized = True
        except Exception as e:
            self._safe_release()
            raise RuntimeError(f"Failed to initialize Ascend model: {e}")

    def _initialize(self):
        """初始化ACL环境"""
        # 初始化ACL
        ret = acl.init()
        self._check_result(ret, "acl init")

        # 设置设备
        ret = acl.rt.set_device(self.device_id)
        self._check_result(ret, "set device")

        # 创建上下文
        context, ret = acl.rt.create_context(self.device_id)
        self._check_result(ret, "create context")
        self._resources['context'] = context

        # 创建流
        stream, ret = acl.rt.create_stream()
        self._check_result(ret, "create stream")

    def _load_model(self):
        """加载模型并准备输入输出"""
        # 加载模型
        model_id, ret = acl.mdl.load_from_file(self.model_path)
        self._check_result(ret, "load model")
        self._resources['model_id'] = model_id

        # 创建模型描述
        model_desc = acl.mdl.create_desc()
        ret = acl.mdl.get_desc(model_desc, model_id)
        self._check_result(ret, "get model description")
        self._resources['model_desc'] = model_desc

        # 准备输入数据集
        input_dataset = self._create_input_dataset(model_desc)
        self._resources['input_dataset'] = input_dataset

        # 准备输出数据集
        output_dataset = self._create_output_dataset(model_desc)
        self._resources['output_dataset'] = output_dataset

    def _create_input_dataset(self, model_desc):
        """创建输入数据集"""
        input_size = acl.mdl.get_num_inputs(model_desc)
        input_dataset = acl.mdl.create_dataset()
        for i in range(input_size):
            input_buffer_size = acl.mdl.get_input_size_by_index(model_desc, i)
            input_buffer, ret = acl.rt.malloc(input_buffer_size, ACL_MEM_MALLOC_HUGE_FIRST)
            self._check_result(ret, "create input buffer")

            data = acl.create_data_buffer(input_buffer, input_buffer_size)
            acl.mdl.add_dataset_buffer(input_dataset, data)

        return input_dataset

    def _create_output_dataset(self, model_desc):
        """创建输出数据集"""
        output_size = acl.mdl.get_num_outputs(model_desc)
        output_dataset = acl.mdl.create_dataset()
        for i in range(output_size):
            output_buffer_size = acl.mdl.get_output_size_by_index(model_desc, i)
            output_buffer, ret = acl.rt.malloc(output_buffer_size, ACL_MEM_MALLOC_HUGE_FIRST)
            self._check_result(ret, "create output buffer")

            data = acl.create_data_buffer(output_buffer, output_buffer_size)
            acl.mdl.add_dataset_buffer(output_dataset, data)

        return output_dataset

    def _check_result(self, ret, operation_name):
        """检查ACL操作结果"""
        if ret != ACL_SUCCESS:
            raise RuntimeError(f"{operation_name} failed, error code: {ret}")

    def run(self, images):
        """运行模型推理"""
        if not self._initialized:
            raise RuntimeError("Model is not initialized")

        # 拷贝数据到设备
        self._copy_input_to_device(images)

        # 执行模型
        ret = acl.mdl.execute(self._resources['model_id'],
                              self._resources['input_dataset'],
                              self._resources['output_dataset'])
        self._check_result(ret, "model execute")

        # 获取输出结果
        outputs = self._get_output_results()
        return outputs

    def _copy_input_to_device(self, images):
        """拷贝输入数据到设备"""
        policy = ACL_MEMCPY_HOST_TO_DEVICE
        input_num = acl.mdl.get_dataset_num_buffers(self._resources['input_dataset'])

        for i in range(input_num):
            if "bytes_to_ptr" in dir(acl.util):
                bytes_data = images[i].tobytes()
                ptr = acl.util.bytes_to_ptr(bytes_data)
            else:
                ptr = acl.util.numpy_to_ptr(images[i])
            input_data_buffer = acl.mdl.get_dataset_buffer(self._resources['input_dataset'], i)
            input_data_buffer_addr = acl.get_data_buffer_addr(input_data_buffer)
            input_data_size = acl.get_data_buffer_size(input_data_buffer)
            ret = acl.rt.memcpy(input_data_buffer_addr,
                                input_data_size,
                                ptr,
                                input_data_size,
                                policy)
            self._check_result(ret, "input memcpy")

    def _get_output_results(self):
        """获取输出结果"""
        outputs = []
        output_size = acl.mdl.get_num_outputs(self._resources['model_desc'])

        for output_index in range(output_size):
            output_data = self._get_single_output(output_index)
            if output_data is not None:
                outputs.append(output_data)

        return outputs

    def _get_single_output(self, output_index):
        output_data_buffer = acl.mdl.get_dataset_buffer(self._resources['output_dataset'], output_index)
        output_data_buffer_addr = acl.get_data_buffer_addr(output_data_buffer)
        output_data_size = acl.get_data_buffer_size(output_data_buffer)

        try:
            # 分配主机内存
            ptr, ret = acl.rt.malloc_host(output_data_size)
            self._check_result(ret, "malloc host for output")

            # 拷贝数据到主机
            ret = acl.rt.memcpy(ptr,
                                output_data_size,
                                output_data_buffer_addr,
                                output_data_size,
                                ACL_MEMCPY_DEVICE_TO_HOST)
            self._check_result(ret, "output memcpy")

            # 获取输出维度
            dims, ret = acl.mdl.get_cur_output_dims(self._resources['model_desc'], output_index)
            self._check_result(ret, "get output dims")
            out_dim = dims['dims']

            # 转换输出数据
            if "ptr_to_bytes" in dir(acl.util):
                bytes_data = acl.util.ptr_to_bytes(ptr, output_data_size)
                output = np.frombuffer(bytes_data, dtype=np.float32).reshape(tuple(out_dim))
            else:
                output = acl.util.ptr_to_numpy(ptr, tuple(out_dim), NPY_FLOAT32)

            # 确保主机内存被释放
            ret = acl.rt.free_host(ptr)
            self._check_result(ret, "free host")

            return output
        except Exception as e:
            print(f"Error getting output {output_index}: {e}")
            return None

    def release(self):
        """释放所有资源"""
        self._safe_release()

    def _safe_release(self):
        """安全释放资源"""
        resources_to_free = ['input_dataset', 'output_dataset', 'model_desc', 'model_id', 'context']

        for resource_name in resources_to_free:
            if resource_name in self._resources:
                self._free_resource(resource_name)

        ret = acl.rt.reset_device(self.device_id)
        self._check_result(ret, "reset device")

        ret = acl.finalize()
        self._check_result(ret, "acl finalize")

        self._initialized = False
        self._resources.clear()

    def _free_resource(self, resource_name):
        """释放特定资源"""
        try:
            resource = self._resources[resource_name]

            if resource_name in ['input_dataset', 'output_dataset']:
                number = acl.mdl.get_dataset_num_buffers(resource)
                for i in range(number):
                    data_buf = acl.mdl.get_dataset_buffer(resource, i)
                    if data_buf:
                        acl.destroy_data_buffer(data_buf)
                acl.mdl.destroy_dataset(resource)

            elif resource_name == 'model_desc':
                acl.mdl.destroy_desc(resource)

            elif resource_name == 'model_id':
                ret = acl.mdl.unload(resource)
                self._check_result(ret, "unload model")

            elif resource_name == 'context':
                ret = acl.rt.destroy_context(resource)
                self._check_result(ret, "destroy context")

        except Exception as e:
            print(f"Warning: Error freeing {resource_name}: {e}")


def load_model(model_path, device_id=0):
    return AscendModel(model_path, device_id)


def run(images, model):
    images = images if isinstance(images, list) else [images]
    if isinstance(model, AscendModel):
        return model.run(images)
    else:
        return None


def release(model):
    if isinstance(model, AscendModel):
        model.release()
