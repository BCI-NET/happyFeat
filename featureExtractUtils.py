from Statistical_analysis import *
import pandas as pd
import dask.dataframe as dsk
import csv
import numpy as np

def channel_generator(number_of_channel, Ground, Ref):
    if number_of_channel == 32:
        electrodes = ['Fp1', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8', 'FC5', 'FC1', 'FC2', 'FC6', 'T7', 'C3', 'Cz', 'C4',
                      'T8', 'TP9', 'CP5', 'CP1', 'CP2', 'CP6', 'TP10', 'P7', 'P3', 'Pz', 'P4', 'P8', 'PO9', 'O1', 'Oz',
                      'O2', 'PO10']
        for i in range(len(electrodes)):
            if electrodes[i] == Ground:
                index_gnd = i
            if electrodes[i] == Ref:
                index_ref = i
        electrodes[index_gnd] = 'AFz'
        electrodes[index_ref] = 'FCz'

    if number_of_channel >= 64:
        electrodes = ['FP1', 'FP2', 'F7', 'F3', 'Fz', 'F4', 'F8', 'FC5', 'FC1', 'FC2', 'FC6', 'T7', 'C3', 'Cz', 'C4',
                      'T8', 'TP9', 'CP5', 'CP1', 'CP2', 'CP6', 'TP10', 'P7', 'P3', 'Pz', 'P4', 'P8', 'PO9', 'O1', 'Oz',
                      'O2', 'PO10', 'AF7', 'AF3', 'AF4', 'AF8', 'F5', 'F1', 'F2', 'F6', 'FT9', 'FT7', 'FC3', 'FC4',
                      'FT8', 'FT10', 'C5', 'C1', 'C2', 'C6', 'TP7', 'CP3', 'CPz', 'CP4', 'TP8', 'P5', 'P1', 'P2', 'P6',
                      'PO7', 'PO3', 'POz', 'PO4', 'PO8']
        for i in range(len(electrodes)):
            if electrodes[i] == Ground:
                index_gnd = i
            if electrodes[i] == Ref:
                index_ref = i
        electrodes[index_gnd] = 'AFz'
        electrodes[index_ref] = 'FCz'

    return electrodes

def elecGroundRef(electrodeList, ground, ref):
    # Replace "ground" and "ref" electrodes (eg TP9/TP10) with new grounds and ref (eg AFz and FCz)
    # If newground or newref alreayd present, all good!
    # if old ground or old ref not present, then return empty list

    newElecList = electrodeList.copy()
    newGround = 'AFz'
    newRef = 'FCz'
    if ground in newElecList:
        idx = newElecList.index(ground)
        newElecList[idx] = newGround
    if ref in newElecList:
        idx = newElecList.index(ref)
        newElecList[idx] = newRef

    if newGround not in newElecList or newRef not in newElecList:
        return None

    return newElecList

def load_csv_pd(file):
    # Read data from CSV file with pandas
    # Practical due to automatic conversion to DataFrame.
    # But very slow with big files.
    data = pd.read_csv(file)
    return data

def load_csv_np(file):
    # Read data from CSV file with numpy
    # Very fast. But need to separate header & data.
    # Here it's specific for OpenViBE CSV structure.
    # Header : ['Time:dim1xdim2' , 'End time', 'Chan1', 'Chan2', ... , 'ChanN', 'Event Id', 'Event Date', 'Event Duration']
    # For the data, we discard the last 3 cols (not used in our case)
    header = np.loadtxt(file, dtype=str, delimiter=',', max_rows=1)
    nbcols = header.size-3
    data = np.loadtxt(file, dtype=float, delimiter=',', skiprows=1, usecols=list(range(nbcols)))
    return header, data

def Extract_CSV_Data(data_cond, trialLength, nbElectrodes, bins, n_window, shift):
    # shift = n_window - overlap
    length = int(np.floor(trialLength / shift))
    data = data_cond[:, 2:]
    data = data[:, :nbElectrodes * bins]

    nbTrials = int(np.shape(data)[0] / length)

    power = np.zeros([nbTrials, nbElectrodes, bins])
    timefreq = np.zeros([nbTrials, nbElectrodes, length, bins])

    for i in range(power.shape[0]):
        for j in range(power.shape[1]):
            power[i, j, :] = data[(i * length):(i * length + length), (j * bins):(j * bins + bins)].mean(axis=0)
            timefreq[i, j, :, :] = data[(i * length):(i * length + length), (j * bins):(j * bins + bins)]

    return power, timefreq

def Extract_Connect_CSV_Data(data_cond, trialLength, nbElectrodes, bins, connectLength, connectOverlap):
    # Only keep the actual data, discard time & stimulations info...
    data = data_cond[:, 2:]
    data = data[:, :bins*nbElectrodes*nbElectrodes]

    shift = connectLength * (1.0-connectOverlap/100.0)
    length = int(np.floor(trialLength / shift))
    nbTrials = int(np.shape(data)[0] / length)

    connectivityMatrix = np.zeros([nbTrials, bins, nbElectrodes, nbElectrodes])
    for i in range(connectivityMatrix.shape[0]):
        for j in range(connectivityMatrix.shape[1]):
            for k in range(connectivityMatrix.shape[2]):
                connectivityMatrix[i, j, k, :] = data[(i * length):(i * length + length),
                                                 (j*nbElectrodes*nbElectrodes + k*nbElectrodes):(j*nbElectrodes*nbElectrodes + k*nbElectrodes + nbElectrodes)].mean(axis=0)

    return connectivityMatrix

def psdSizeToFreqRes(psdSize, fSamp):
    return float(fSamp) / float(psdSize)

def freqResToPsdSize(fRes, fSamp):
    return int(fSamp / fRes)

def samplesToTime(samples, fSamp):
    return float(samples)/float(fSamp)

def timeToSamples(time, fSamp):
    return int(float(time)*float(fSamp))
