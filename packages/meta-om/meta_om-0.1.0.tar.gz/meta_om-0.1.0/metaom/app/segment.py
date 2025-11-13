import metacv as mc
from ..model_zoo import load_model, run, release


class Segment(mc.Segment):
    def __init__(self,
                 model_path: str,
                 input_width: int,
                 input_height: int,
                 use_preprocess=True,
                 pad=None,
                 normal=None,
                 mean=None,
                 std=None,
                 swap=None,
                 confidence_thresh=None,
                 nms_thresh=None,
                 class_names=None,
                 device_id=0):
        super().__init__(model_path,
                         input_width,
                         input_height,
                         use_preprocess,
                         pad,
                         normal,
                         mean,
                         std,
                         swap,
                         confidence_thresh,
                         nms_thresh,
                         class_names)
        self.device_id = device_id
        self.model = None
        self.det_output = None
        self.initialize_model()

    def initialize_model(self):
        self.model = load_model(self.model_path, self.device_id)

    def infer(self, image):
        # 由继承类实现模型推理
        outputs = run(image, self.model)
        self.det_output = outputs[0]
        batch_size = len(image) if isinstance(image, list) else 1
        self.mask_output = outputs[1].reshape((batch_size, 32, -1))

    def __del__(self):
        release(self.model)
