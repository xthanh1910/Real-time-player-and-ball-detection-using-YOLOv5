import os
import cv2
import glob
import json


def process_dataset(root_path, output_path, is_train):
    """
    Hàm chung để xử lý dataset (train hoặc val)
    
    Args:
        root_path: đường dẫn tới dữ liệu đầu vào
        output_path: đường dẫn tới thư mục output
        is_train: True nếu xử lý training data, False nếu xử lý validation data
    """
    video_paths = list(glob.iglob("{}/*/*.mp4".format(root_path)))
    anno_paths = list(glob.iglob("{}/*/*.json".format(root_path)))
    video_wo_ext = [video_path.replace(".mp4", "") for video_path in video_paths]
    anno_wo_ext = [anno_path.replace(".json", "") for anno_path in anno_paths]
    paths = list(set(video_wo_ext) & set(anno_wo_ext)) 

    mode = "train" if is_train else "val"
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    images_dir = os.path.join(output_path, "images", mode)
    labels_dir = os.path.join(output_path, "labels", mode)
    if not os.path.isdir(images_dir):
        os.makedirs(images_dir)
    if not os.path.isdir(labels_dir):
        os.makedirs(labels_dir)
        
    for idx, path in enumerate(paths):
        video = cv2.VideoCapture("{}.mp4".format(path))
        num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        with open("{}.json".format(path), "r") as json_file:
            json_data = json.load(json_file)
        if num_frames != len(json_data["images"]):
            print("Something is wrong with the game {}".format(path))
            paths.remove(path)
        width = json_data["images"][0]["width"]
        height = json_data["images"][0]["height"]
        all_objects = [{"image_id": obj["image_id"], "bbox": obj["bbox"], "category_id": obj["category_id"]}
                       for obj in json_data["annotations"] if obj["category_id"] in [3, 4]]
        frame_counter = 0
        while video.isOpened():
            print(idx, frame_counter)
            flag, frame = video.read()
            if not flag:
                break
            current_object = [obj for obj in all_objects if obj["image_id"] - 1 == frame_counter]
            cv2.imwrite(os.path.join(output_path, "images", mode, "{}_{}.jpg".format(idx, frame_counter)), frame)
            with open(os.path.join(output_path, "labels", mode, "{}_{}.txt".format(idx, frame_counter)), "w") as f:
                for obj in current_object:
                    xmin, ymin, w, h = obj["bbox"]
                    xmin /= width
                    w /= width
                    ymin /= height
                    h /= height
                    if obj["category_id"] == 4:
                        category = 0
                    else:
                        category = 1
                    f.write("{} {:06f} {:06f} {:06f} {:06f}\n".format(category, xmin + w / 2, ymin + h / 2, w, h))
            frame_counter += 1


if __name__ == '__main__':
    output_path = "football_yolo_dataset"
    print("Processing training data...")
    process_dataset(
        root_path="data/football_train",
        output_path=output_path,
        is_train=True
    )
    print("Processing validation data...")
    process_dataset(
        root_path="data/football_test",
        output_path=output_path,
        is_train=False
    )