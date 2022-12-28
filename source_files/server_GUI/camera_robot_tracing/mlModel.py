import tensorflow as tf
import cv2
from camera_robot_tracing.object_detection.utils import visualization_utils as vis_utils
from camera_robot_tracing.object_detection.utils import label_map_util as label_util
from tensorflow.python.ops.numpy_ops import np_config

class FindRoboNNetwork:

    def __init__(self):
        np_config.enable_numpy_behavior()
        #category_id = label_util.create_category_index_from_labelmap('camera_robot_tracing/detected/data/tf_label_map.pbtxt', use_display_name=True)
        self.model = tf.saved_model.load('camera_robot_tracing/detected/training/export/saved_model/')

    def get_frame_from_tensor(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_tensor = tf.convert_to_tensor(img_rgb)
        img_tensor = img_tensor[tf.newaxis ,...]
        img_tensor = img_tensor[: ,: ,:, :3]
        result = self.model(img_tensor)
        result = {key: value.numpy() for key, value in result.items()}

        vis_utils.visualize_boxes_and_labels_on_image_array(
            img,
            result['detection_boxes'][0],
            (result['detection_classes'][0] + 0).astype(int),
            result['detection_scores'][0],
            {"id": "Robot"},
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=.90,
            agnostic_mode=False
        )
        return img

    def get_bbox_from_tensor(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_tensor = tf.convert_to_tensor(img_rgb)
        img_tensor = img_tensor[tf.newaxis ,...]
        img_tensor = img_tensor[: ,: ,:, :3]
        result = self.model(img_tensor)
        result = {key :value.numpy() for key ,value in result.items()}

        boxes = result['detection_boxes'][0]
        scores = result['detection_scores'][0]
        min_score_thresh = .90

        coordinates = []
        for i in range(len(boxes)):
            if scores[i] > min_score_thresh:
                # class_name = category_id[result['detection_classes'][0][i]]['name']
                boxes[i][0] = boxes[i][0 ] *img.shape[0]
                boxes[i][2] = boxes[i][2 ] *img.shape[0]
                boxes[i][1] = boxes[i][1 ] *img.shape[1]
                boxes[i][3] = boxes[i][3 ] *img.shape[1]

                coordinates.append({
                    "name": 'Robot', #category_id[result['detection_classes'][0][i]]['name'],
                    "boxes": boxes[i]
                })

        points = []
        for i in range(len(coordinates)):
            points.append({
                'name': coordinates[i]['name'],
                'point': [coordinates[i]['boxes'][1 ] +((coordinates[i]['boxes'][3 ] -coordinates[i]['boxes'][1]) ) /2
                          ,coordinates[i]['boxes'][0 ] +((coordinates[i]['boxes'][2 ] -coordinates[i]['boxes'][0] ) /2)]
            })
        print(points)
        return points