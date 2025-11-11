'''
This module is a wrapper for ultralytics YOLOV8 and RTDETR models.
'''
from ultralytics import YOLO, RTDETR
import cv2
import pandas as pd
from tqdm import tqdm
import random, os
from pathlib import Path
import torch

class Detector:
    def __init__(self,
                 model:str='yolo',
                 weights:str='x',
                 conf:float=0.25,
                 nms:float=0.7,
                 max_det:int=300, 
                 device:str='auto',
                 half:bool=False):
        '''
        Initialize the Detector class.
        Parameters:
            model: 'yolo' (default), 'rtdetr'
            weights: 'x' - extra-large (default), 'l' - large, 'm' - mdium, 's' - small, 'n' - nano, '.pt' - custom model weights
            conf: 0.25 (default) - confidence threshold
            nms: 0.7 (default) - non-max suppression threshold
            max_det: 300 (default) - maximum number of detections per image
            device: 'auto' (default), 'cuda', 'cpu', 'mps'
            half: False (default), True
        '''
        # Load model
        cwd = Path(__file__).parent.absolute()
        if model == 'yolo':
            if weights in ['x', 'l', 'm', 's', 'n']:
                model_path = os.path.join(cwd, 'models/yolov8'+weights+'.pt')
            elif ".pt" in weights:
                model_path = os.path.join(cwd, 'models/'+weights)
        elif model == 'yolo11':
            if weights in ['x', 'l', 'm', 's', 'n']:
                model_path = os.path.join(cwd, 'models/yolo11'+weights+'.pt')
            elif ".pt" in weights:
                model_path = os.path.join(cwd, 'models/'+weights)

        elif model == 'rtdetr':
            if weights in ['x', 'l']:
                model_path = os.path.join(cwd, 'models/rtdetr-'+weights+'.pt')
            elif ".pt" in weights:
                model_path = os.path.join(cwd, 'models/'+weights)
            else:
                model_path = os.path.join(cwd, 'models/rtdetr-x.pt')
        #elif model == 'nas':
        #    if weights in ['l', 'm', 's']:
        #        model_path = os.path.join(cwd, 'models/yolo_nas_'+weights+'.pt')
        #    elif ".pt" in weights:
        #        model_path = os.path.join(cwd, 'models/'+weights)
        #    else:
        #        model_path = os.path.join(cwd, 'models/yolo_nas_l.pt')
        else:
            raise Exception('Invalid detection model type!')
        
        if model == 'yolo' or model == 'yolo11':
            self.model = YOLO(model_path)
        elif model == 'rtdetr':
            self.model = RTDETR(model_path)
        #elif model == 'nas':
        #    self.model = NAS(model_path)
        else:
            raise Exception('Invalid model weights!')  
        
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

    def detect(self,
               input_video:str,
               iou_file:str=None,
               video_index:int=None,
               video_tot:int=None,
               start_frame:int=None,
               end_frame:int=None,
               verbose:bool=True) -> pd.DataFrame:
        '''
        Detect objects in a video file.
        Parameters:
            input_video: path to the input video file
            iou_file: path to the output file
            video_index: index of the video in the batch
            video_tot: total number of videos in the batch
            start_frame: start frame number
            end_frame: end frame number
            verbose: True (default), False
        Returns:
            df: pandas DataFrame containing the detection results
        '''
        # open input video
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            print('Failed to open the video!')

        random.seed(3)  # deterministic bbox colors
        results = []

        video_fps = int(cap.get(cv2.CAP_PROP_FPS))                    #original fps
        if start_frame:
            if (start_frame > int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1) or (start_frame < 0):
                start_frame = 0    
        else:
            start_frame = 0

        if end_frame:
            if (end_frame > int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1) or (end_frame < 0):
                end_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1    
        else:
            end_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1

        if start_frame>=end_frame:
            raise Exception('The given start time exceeds the end time!')
        
        frame_total = end_frame - start_frame
        if verbose:      
            pbar = tqdm(total=frame_total, unit=" frames")
            if video_index and video_tot: 
                pbar.set_description_str("Detecting {} of {}".format(video_index, video_tot))
            else:
                pbar.set_description_str("Detecting ")

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        while cap.isOpened():
            pos_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            ret, frame = cap.read()
            if (not ret) or (pos_frame>end_frame):
                break
            
            detects = self.model.predict(frame, verbose=False, conf=self.conf, iou=self.nms, max_det=self.max_det, 
                                         device=self.device, half=self.half)   
            if len(detects)>0:
                detect = detects[0]    

                xyxy = pd.DataFrame(detect.boxes.xyxy.tolist(), columns=['x', 'y', 'x2', 'y2'])
                cls = pd.DataFrame(detect.boxes.cls.tolist(), columns=['class'])
                conf = pd.DataFrame(detect.boxes.conf.tolist(), columns = ['conf'])
                result = pd.concat([xyxy, conf, cls], axis=1)
                result.insert(0, 'frame', pos_frame)
                result.insert(1, 'res', -1)
                results.append(result)

            if verbose:
                pbar.update()

        if verbose:
            pbar.close()
        cap.release()
        #cv2.destroyAllWindows()

        df = pd.concat(d for d in results if not d.empty) # remove empty dataframes
        #df = pd.concat(results)
        df['x'] = round(df['x'], 1)
        df['y'] = round(df['y'], 1)
        df['w'] = round(df['x2']-df['x'], 0)
        df['h'] = round(df['y2']-df['y'], 0)
        df['conf'] = round(df['conf'], 2)
        df = df[['frame', 'res', 'x', 'y', 'w', 'h', 'conf', 'class']].reindex()

        if iou_file:
            df.to_csv(iou_file, index=False, header=False)
            if verbose:
                print("Wrote to {}".format(iou_file))
        
        return df

    def detect_frames(self, input_video:str, frames:list[int], verbose:bool=False)->pd.DataFrame:
        # open input video
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            print('Failed to open the video!')

        random.seed(3)  # deterministic bbox colors
        results = []

        if verbose:
            pbar = tqdm(total=len(frames), unit=" frames")        
        for pos_frame in frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame)
            ret, frame = cap.read()
            if not ret:
                break
            
            detects = self.model.predict(frame, verbose=False, conf=self.conf, iou=self.nms, max_det=self.max_det, 
                                         device=self.device, half=self.half)   
            if len(detects)>0:
                detect = detects[0]    

                xyxy = pd.DataFrame(detect.boxes.xyxy.tolist(), columns=['x', 'y', 'x2', 'y2'])
                cls = pd.DataFrame(detect.boxes.cls.tolist(), columns=['class'])
                conf = pd.DataFrame(detect.boxes.conf.tolist(), columns = ['conf'])
                result = pd.concat([xyxy, conf, cls], axis=1)
                result.insert(0, 'frame', pos_frame)
                result.insert(1, 'res', -1)
                results.append(result)

            if verbose:
                pbar.update()

        if verbose:
            pbar.close()
        cap.release()

        if len(results) == 0:
            return pd.DataFrame(columns=['frame', 'res', 'x', 'y', 'w', 'h', 'conf', 'class'])
        
        df = pd.concat(d for d in results if not d.empty) # remove empty dataframes
        #df = pd.concat(results)
        df['x'] = round(df['x'], 1)
        df['y'] = round(df['y'], 1)
        df['w'] = round(df['x2']-df['x'], 0)
        df['h'] = round(df['y2']-df['y'], 0)
        df['class'] = round(df['class'], 0)
        df['conf'] = round(df['conf'], 2)
        df = df[['frame', 'res', 'x', 'y', 'w', 'h', 'conf', 'class']].reset_index(drop=True)

        return df

    def detect_v8(self, input_video:str, iou_file:str=None, save:bool=False, verbose:bool=False, show:bool=False):
        detects = self.model.predict(input_video, 
                        verbose=verbose, stream=True, save=save, show=show, device=self.device, half=self.half)
        
        if iou_file:
            results = []
            frame = 0
            for detect in detects:
    
                xywh = pd.DataFrame(detect.boxes.xywh.tolist(), columns=['x', 'y', 'w', 'h'])
                cls = pd.DataFrame(detect.boxes.cls.tolist(), columns=['class'])
                conf = pd.DataFrame(detect.boxes.conf.tolist(), columns = ['conf'])

                result = pd.concat([xywh, conf, cls], axis=1)
                result.insert(0, 'frame', frame) 
                result.insert(1, 'revserve', -1) 

                result['x'] = result['x']-result['w']/2
                result['y'] = result['y']+result['h']/2

                frame += 1

                results.append(result)

            df = pd.concat(results)
            df.to_csv(iou_file, index=False, header=False)

    def detect_batch(self, input_videos:list[str], output_path:str=None, is_overwrite:bool=False, 
                     is_report:bool=True, verbose:bool=False) -> list[str]:
    
        results = []
        total_videos = len(input_videos)
        video_count=0
        for input_video in input_videos:
            video_count+=1

            base_filename = os.path.splitext(os.path.basename(input_video))[0]
            raw_video = input_video #os.path.join(input_path, base_filename+".mp4")

            if verbose:
                print("Processing {} of {} - {}           ".format(video_count, total_videos, raw_video))
            

            if output_path:
                if not os.path.exists(output_path):
                    os.mkdir(output_path)

                iou_file = os.path.join(output_path, base_filename+"_iou.txt")

            if not is_overwrite:
                if os.path.exists(iou_file):
                    if is_report:
                        results.append(iou_file)
                    continue 

            self.detect(input_video=raw_video, iou_file=iou_file, 
                        video_index=video_count, video_tot=total_videos,
                        verbose=verbose)

            results.append(iou_file)

        return results

    @staticmethod
    def get_fps(video:str)->float:
        cap = cv2.VideoCapture(video)
        if not cap.isOpened():
            print('Failed to open the video!')
        fps = cap.get(cv2.CAP_PROP_FPS)
        return fps
    
    @staticmethod
    def get_frames(video:str)->int:
        cap = cv2.VideoCapture(video)
        if not cap.isOpened():
            print('Failed to open the video!')
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return frames

if __name__=='__main__':

    detector = Detector(model='yolo11')
    result = detector.detect('/mnt/d/videos/sample/traffic.mp4', verbose=True)

    print(result)
