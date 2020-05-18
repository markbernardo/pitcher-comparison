#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 10:35:28 2020

@author: mgbernardo
"""
import re
import pandas as pd
import numpy as np

#master pitch movement data from baseball savant
mlb_main = pd.read_csv('mlb_movement.csv').rename(columns={'pitcher_id':'pitcher',' first_name':'first_name',})
              
#create list of all release heights
release_height = pd.concat([pd.read_csv('2019_righties_1.csv').filter(['pitcher', 'p_throws','release_pos_z']).groupby('pitcher').release_pos_z.mean(), 
                            pd.read_csv('2019_lefties.csv').filter(['pitcher', 'p_throws','release_pos_z']).groupby('pitcher').release_pos_z.mean()])

#create list of pitcher handedness
pitch_hand = pd.Series(mlb_main['pitch_hand'].values, index=mlb_main['pitcher']).rename('pitch_hand')
pitch_hand = pitch_hand.loc[~pitch_hand.index.duplicated(keep='first')]

#pitch arsenal distribution dataframe
pitch_dist = pd.read_csv('pitch_arsenals.csv').rename(columns={' first_name':'first_name',})

#join release height to pivot table
pitch_dist = pitch_dist.join(release_height, on = 'pitcher', how = 'inner')
pitch_dist = pitch_dist.join(pitch_hand, on = 'pitcher', how = 'inner')

#extract responses
response_df = pd.read_csv('responses.csv')

#clean percentage columns
type_list = ['n_ff','n_si','n_fc','n_sl','n_ch','n_cu','n_fs']
for i in type_list:
    response_df[i] = response_df[i].str.replace('\W', '')

#keep first letter of hand and slot columns
response_df['hand'] = response_df['hand'].str[0]
response_df['slot'] = response_df['slot'].str[0]

#returns MLB release height ranges based on user arm slot
def slot_range(response):
    if response['slot'] == 'H':
        return [5.7, 10.0]
    if response['slot'] == 'T':
        return [5.1, 5.6999]
    if response['slot'] == 'L':
        return [4.0, 5.0999]
    if response['slot'] == 'S':
        return [0, 3.9999]

#creates list of pitches based on responses
def pitch_list(response):
    pitch_list = []
    for i in type_list:
        if response[i] != '0' and response[i] != 0:
            pitch_list.append(i)
    return pitch_list


def similar_pitchers(response):
    results_list = []
    for i in range(len(pitch_dist)):
        if (response['hand'] == pitch_dist.iloc[i]['pitch_hand'] and 
            slot_range(response)[0] < pitch_dist.iloc[i]['release_pos_z'] <= slot_range(response)[1] and
            pitch_list(response) == pitch_list(pitch_dist.iloc[i])):
            results_list.append(pitch_dist.iloc[i])
    if len(results_list) == 0:
        return 'No similar pitchers found. You\'re one of a kind ;)'
    else:
        return results_list
