import numpy as np
import pandas as pd
from tqdm import tqdm
from ..detect import Detector
from ..engine.iob import iobs

class ReClass:
    def __init__(self,
                 num_frames:int=25,
                 threshold:float=0.75,
                 model:str='rtdetr',
                 weights:str='x',
                 device:str='auto',
                 default_class:int=0,
                 match_class:list=[1, 36]) -> None:
        """
        Re-classify tracks based on detection results
        Parameters:
            num_frames: Number of frames to consider for re-classification, default 25
            threshold: Threshold for matching, default 0.75
            model: Detection model to use, default 'rtdetr'
            weights: Weights for the detection model, default 'x'
            device: Device to use for detection, default 'auto'
            default_class: Default class to assign if no match found, default 0 (pedestrian)
            match_class: List of classes to match, default [1, 36] (bicycle, skateboard/scooter)
        """
        self.detector = Detector(model=model, device=device)
        self.num_frames = num_frames
        self.threshold = threshold
        self.default_class = default_class
        self.match_class = match_class
           
    def match_mmv(self, track:pd.DataFrame, dets:pd.DataFrame)->tuple:
    
        score = 0
        cnt = 0
        for idx, row in track.iterrows():
            bboxes = row[['x', 'y', 'w', 'h']].values.reshape(1, -1)
            det = dets[dets['frame'] == row['frame']]
            if len(det) > 0:
                match_bboxes = det[['x', 'y', 'w', 'h']].values
                _, overlaps_mmv = iobs(bboxes, match_bboxes)
                max_overlap = np.max(overlaps_mmv)
                if max_overlap >= self.threshold:
                    score += max_overlap
                    cnt += 1

        if cnt > 0:
            avg_score = score/cnt
        else:
            avg_score = 0
        hit = True if avg_score >= self.threshold else False

        return hit, avg_score

    def re_classify(self,
                    tracks:pd.DataFrame,
                    input_video:str,
                    track_ids:list=None,
                    out_file:str=None,
                    verbose:bool=True)->pd.DataFrame:
        """
        Re-classify tracks
        Parameters:
            tracks: DataFrame with target tracks
            input_video: Path to video
            track_ids: List of track IDs for re-classify, if None re-classify all tracks, default None
            default_cls: Default class to assign if no match found, default 0 (pedestrian)
            match_cls: List of classes to match, default [1, 36] (bicycle, skateboard/scooter)
            out_file: Path to save re-classified tracks, default None
        Returns:
            DataFrame with re-classified tracks (track_id, cls, avg_score)
        """

        if track_ids is None:
            track_ids = tracks['track'].unique().tolist()

        results = []
        if verbose:
            pbar = tqdm(total=len(track_ids), unit='track', desc='Re-classifying tracks')
        for track_id in track_ids:
            
            target_track = tracks[tracks['track'] == track_id].copy()
            target_track['area'] = target_track['w'] * target_track['h']
            target_track.sort_values(by='area', inplace=True, ascending=False)

            if len(target_track) >= self.num_frames:
                top_frames = target_track.head(self.num_frames)
            else:
                top_frames = target_track

            dets = self.detector.detect_frames(input_video, top_frames['frame'].values.tolist())

            matched = [] 
            for cls in self.match_class:
                match_dets = dets[dets['class'] == cls]
                hit, avg_score = self.match_mmv(top_frames, match_dets)
                if hit:
                    matched.append((cls, avg_score))
            
            if len(matched) > 0:
                cls, avg_score = max(matched, key=lambda x: x[1])
            else:
                cls = self.default_class
                avg_score = 0

            results.append([track_id, cls, round(avg_score, 2)])
            if verbose:
                pbar.update()
        if verbose:
            pbar.close()

        df = pd.DataFrame(results, columns=['track', 'cls', 'avg_score'])
        if out_file:
            df.to_csv(out_file, index=False)

        return df   