# metaom

metaom部署通用框架

## 1、安装最新版 meta-cv

    pip install meta-cv

## 2、安装最新版 meta-hb

    pip install meta-om

## 3、目标检测示例（参考[detection_demo.py](detection_demo.py)代码）

    import cv2, platform
    import metaom as m

    Detection = m.Detection

    y = DetectionDetection(
        model_path='models/yolov8m-seg_quantized_model.om',
        input_width=640,
        input_height=480,
        use_preprocess=True,
        pad=True,
        confidence_thresh=0.5,
        nms_thresh=0.3,
        class_names=classnames,
        device_id=0)
    
    batch_size = 1
    img = cv2.imread('models/bus.jpg')
    img_list = [img[:, :, ::-1]] * batch_size if batch_size > 1 else img[:, :, ::-1]
    _dets, _scores, _labels = y.predict(img_list)
    
    # 显示
    y.show(img, _dets[-1], _scores[-1], _labels[-1])
    cv2.imwrite("models/bus.png", img)

## 4、实例分割示例（参考[segment_demo.py](segment_demo.py)代码）

    import cv2, platform
    import metaom as m

    Segment = m.Segment

    y = Segment(
        model_path='models/yolov8m-seg_quantized_model.om',
        input_width=640,
        input_height=480,
        use_preprocess=True,
        pad=True,
        confidence_thresh=0.5,
        nms_thresh=0.3,
        class_names=classnames,
        device_id=0)
    
    batch_size = 1
    img = cv2.imread('models/bus.jpg')
    img_list = [img[:, :, ::-1]] * batch_size if batch_size > 1 else img[:, :, ::-1]
    _dets, _scores, _labels = y.predict(img_list)
    
    # 显示
    y.show(img, _dets[-1], _scores[-1], _labels[-1])
    cv2.imwrite("models/bus.png", img)