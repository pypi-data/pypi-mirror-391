from ultralytics import YOLO
import cv2
import pandas as pd
from tqdm import tqdm
import random, os, json
from pathlib import Path
import torch
from shapely.geometry import Polygon as Pol

class Segmentor:
    def __init__(self, model:str='yolov8m-seg.pt', conf:float=0.25, nms:float=0.7, max_det:int=300, device:str='auto', half:bool=False):
        '''
        yolo:  x - yolov8x-seg.pt 
                l - yolov8l-seg.pt
                m - yolov8m-seg.pt
                s - yolov8s-seg.pt
                n - yolov8n-seg.pt
        
        '''
        # Load YOLOV8 model
        cwd = Path(__file__).parent.absolute()
        model_path = os.path.join(cwd, 'models/'+model)
        self.model = YOLO(model_path)     
        self.conf = conf
        self.nms = nms
        self.max_det = max_det

        if device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
        elif device == 'cuda' and torch.cuda.is_available():
            self.device = 'cuda'
        elif device == 'mps' and torch.backends.mps.is_available():
            self.device = 'mps'
        else:
            self.device = 'cpu'        
    
        self.half = half
        self.half = half

    def segment(self, input_video:str, mask_file:str=None,
               video_index:int=None, video_tot:int=None,
               start_frame:int=None, end_frame:int=None, 
               verbose:bool=False):
     
        # open input video
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            print('Failed to open the video!')

        results = []

        video_fps = int(cap.get(cv2.CAP_PROP_FPS))                    #original fps
        if start_frame:
            if start_frame > int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1:
                start_frame = 0    
        else:
            start_frame = 0

        if end_frame:
            if end_frame > int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1:
                end_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1
            elif end_frame < start_frame:
                end_frame = start_frame    
        else:
            end_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1

        if start_frame>end_frame:
            raise Exception('The given start time exceeds the end time!')
        
        frame_total = end_frame - start_frame + 1     
        pbar = tqdm(total=frame_total, unit=" frames")
        if video_index and video_tot: 
            pbar.set_description_str("Segmenting {} of {}".format(video_index, video_tot))
        else:
            pbar.set_description_str("Segmenting ")

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        while cap.isOpened():
            pos_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            ret, frame = cap.read()
            if (not ret) or (pos_frame>end_frame):
                break
            
            detects = self.model.predict(frame, verbose=False, conf=self.conf, iou=self.nms, max_det=self.max_det, half=self.half)   
            if len(detects)>0:
                xyxy = detects[0].boxes.xyxy.tolist()
                xywh = list(map(lambda x: [int(x[0]), int(x[1]), int(x[2]-x[0]), int(x[3]-x[1])], xyxy))
                cls = detects[0].boxes.cls.tolist()
                conf = detects[0].boxes.conf.tolist()
                xy = list(map(lambda x: x.tolist(), detects[0].masks.xy))

                d = {
                    "frame": pos_frame,
                    "res": -1,
                    "class": cls,
                    "conf": conf,
                    "mask": xy}

                results.append(d)

            pbar.update()

        pbar.close()
        cap.release()
        cv2.destroyAllWindows()
        
        if mask_file:
           
            with open(mask_file, "w") as out_file:
                for r in results:
                    json_str = json.dumps(r)
                    out_file.write(json_str)
            if verbose:
                print("Wrote to {}".format(mask_file))
        
        return results
    
    def segment_single(self, input_video:str, frame:int=None):
        return self.segment(input_video, mask_file=None,
               video_index=None, video_tot=None,
               start_frame=frame, end_frame=frame, 
               verbose=False)
    
    def segment_zone(self, input_video:str, frame:int=None, zone:list=None) -> list:
        '''
        Segment the video in a specific zone
        input_video: Path to video
        frame: Frame number to segment
        zone: Polygon zone to segment
        Return:
            List of segmented objects in the zone
        '''        
    
        # open input video
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
                print('Failed to open the video!')

        if frame <0 or frame > int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1:
            raise Exception('The given frame is out of range!')       

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        ret, frame = cap.read()
        if ret:
            x1, y1, x2, y2 = zone
            cropped_frame = frame[y1:y2, x1:x2]           
            detects = self.model.predict(cropped_frame, verbose=False, conf=self.conf, iou=self.nms, max_det=self.max_det, half=self.half)   
            if len(detects)>0:
                if detects[0].masks is not None:
                    xy = list(map(lambda x: x.tolist(), detects[0].masks.xy))
                    print(xy)
                    input('.')
        cap.release()
                
        
if __name__=="__main__":
    
    segmentor = Segmentor()
    #segmentor.segment('/mnt/d/videos/samples/traffic_short.mp4', '/mnt/d/videos/samples/traffic_short_mask.json', start_frame=1, end_frame=1)
    input_video = '/mnt/d/videos/hyde/after_2024-08-15_nw.mp4'
    tracks = pd.read_csv('/mnt/d/videos/hyde/tracks/after_2024-08-15_nw_track_veh_rt.txt')
    tracks.columns = ['frame', 'track', 'x', 'y', 'w', 'h', 'r1', 'r2', 'r3', 'r4']
    dets = tracks[tracks['track'] == 678]
    dets.sort_values(by='frame', inplace=True)
    
    for index, det in dets.iterrows():
        zone = (int(det['x']), int(det['y']), int(det['x'] + det['w']), int(det['y'] + det['h']))
        frame = int(det['frame'])

        segmentor.segment_zone(input_video, frame, zone)  # Segment the specific zone
        print(f"Segmented frame {frame}")