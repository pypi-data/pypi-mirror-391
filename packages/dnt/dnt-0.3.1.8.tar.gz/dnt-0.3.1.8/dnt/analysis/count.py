# pylint: disable=too-many-arguments
'''
This script is used to count the number of tracks that passing a reference line for post-analysis
last modified: 2021-09-30
'''
from shapely.geometry import Polygon, LineString
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
import numpy as np

class Count:
    '''
    Count tracks that passing a reference line for post-analysis
    Methods:
        __init__(): initialize the class
        count_tracks_by_line(): 
            count tracks that passing a reference line for post-analysis
    '''
    def __init__(self) -> None:
        self.track_fields = ['frame', 'track_id', 'x', 'y', 'w', 'h', 'r1', 'r2', 'r3', 'r4']

    def count_tracks_by_line(self,
                             tracks:pd.DataFrame=None,
                             track_file:str=None,
                             line: LineString=None,
                             video_index:int=None,
                             video_tot:int=None,
                             verbose:bool=True) -> pd.DataFrame:
        '''
        Count tracks that passing a reference line for post-analysis
            Inputs:
                tracks - a DataFrame of tracks, if None (default), read track_file
                track_file -  a txt file contains tracks, 
                line - the reference line, LineString(pointA, pointB)
                video_index - the index of video for processing
                video_tot - the total number of videos
                verbose - if True, show progress bar
            Return:
                A DataFrame of track_id, frame, direction, count
        '''
        # Load tracks
        if tracks is None:
            tracks = pd.read_csv(track_file, header=None)
        if len(tracks.columns) != len(self.track_fields):
            raise Exception("The tracks format is incorrect!")
        tracks.columns = self.track_fields
        track_ids = tracks['track_id'].unique()

        # Create a GeoDataFrame of tracks
        geo = tracks.apply(lambda track: Polygon([(track['x'], track['y']),
                                                (track['x'] + track['w'], track['y']),
                                                (track['x'] + track['w'], track['y'] + track['h']),
                                                (track['x'], track['y'] + track['h'])]),
                                                axis =1)
        geo_tracks = gpd.GeoDataFrame(tracks, geometry=geo)
        point_a = np.array(line.coords[0])
        point_b = np.array(line.coords[1])

        # Interate through all tracks
        if verbose:
            pbar = tqdm(total=len(track_ids), unit=' tracks')
            if video_index and video_tot:
                pbar.set_description_str("Counting {} of {}".format(video_index, video_tot))
            else:
                pbar.set_description_str("Counting")
        intersected_tracks = []
        intersected_frames = []
        intersected_direct = []

        for track_id in track_ids:
            selected = geo_tracks.loc[(geo_tracks['track_id']==track_id)].copy()
            if len(selected)>0:
                selected['intersected'] = line.intersects(selected.geometry).values.tolist()
                intersected = selected.loc[(selected['intersected']==True)].copy()
                if len(intersected) > 0:
                    intersected.sort_values(by='frame', inplace=True)
                    if not track_id in intersected_tracks:
                        intersected_tracks.append(track_id)
                        frame_pos = int(len(intersected)/2)
                        intersected_frames.append(intersected['frame'].values[frame_pos])

                        # center point of the first frame
                        point_c = np.array((intersected.iloc[0]['x'] + intersected.iloc[0]['w']/2,
                                    intersected.iloc[0]['y'] + intersected.iloc[0]['h']/2))
                        d = 2  # right
                        if np.cross(point_c-point_a, point_b-point_a) < 0:
                            d = 1 # left
                        intersected_direct.append(d)
            if verbose:
                pbar.update()
                
        if verbose:
            pbar.close()

        results = pd.DataFrame(
            {
                'track_id': intersected_tracks,
                'frame': intersected_frames,
                'direction': intersected_direct,
            }
        )
        results.sort_values(by='frame', inplace=True)
        results = results.reset_index(drop=True)
        results['count'] = results.index + 1

        return results
