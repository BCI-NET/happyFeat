import sys
import os
import json
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit

from Visualization_Data import *
from featureExtractUtils import *
from modifyOpenvibeScen import *
import bcipipeline_settings as settings

class Features:
    Rsigned = []
    electrodes_orig = []
    electrodes_final = []
    power_right = []
    power_left = []
    freqs_left = []
    time_left = []
    time_right = []
    time_length = []


class Dialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        ### GET PARAMS FROM JSON FILE...
        self.dataNp1 = []
        self.dataNp2 = []
        self.Features = Features()
        # self.PipelineParams = PipelineParams()

        # readJsonFile(jsonfullpath)
        self.scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        print(self.scriptPath)
        jsonfullpath = os.path.join(self.scriptPath, "generated", "params.json")
        with open(jsonfullpath) as jsonfile:
            self.parameterDict = json.load(jsonfile)

        ### CREATE INTERFACE...
        self.setWindowTitle('Feature Extraction')
        self.dlgLayout = QHBoxLayout()

        # FEATURE VISUALIZATION PART
        self.layoutLeft = QVBoxLayout()
        self.layoutLeft.setAlignment(QtCore.Qt.AlignTop)
        self.label = QLabel('----- VISUALIZE FEATURES -----')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layoutLeft.addWidget(self.label)

        self.formLayoutExtract = QFormLayout()

        # Param : Path 1
        self.path1 = QLineEdit()
        pathSpectrum1 = os.path.join(self.scriptPath, "generated", "spectrumAmplitude-Left.csv")
        self.path1.setText(pathSpectrum1)
        self.formLayoutExtract.addRow('Path1:', self.path1)
        # Param : Path 2
        self.path2 = QLineEdit()
        pathSpectrum2 = os.path.join(self.scriptPath, "generated", "spectrumAmplitude-Right.csv")
        self.path2.setText(pathSpectrum2)
        self.formLayoutExtract.addRow('Path2:', self.path2)

        # Param : fmin for frequency based viz
        self.userFmin = QLineEdit()
        self.userFmin.setText('1')
        self.formLayoutExtract.addRow('fMin (for PSD and r2map)', self.userFmin)
        # Param : fmax for frequency based viz
        self.userFmax = QLineEdit()
        self.userFmax.setText('40')
        self.formLayoutExtract.addRow('fMax (for PSD and r2map)', self.userFmax)

        # Param : Electrode to use for PSD display
        self.electrodePsd = QLineEdit()
        self.electrodePsd.setText('FC1')
        self.formLayoutExtract.addRow('Electrode to use for PSD', self.electrodePsd)
        # Param : Frequency to use for Topography
        self.freqTopo = QLineEdit()
        self.freqTopo.setText('15')
        self.formLayoutExtract.addRow('Frequency to use for Topography (Hz)', self.freqTopo)

        self.layoutLeft.addLayout(self.formLayoutExtract)

        self.layoutLeftButtons = QVBoxLayout()

        self.btn_load_files = QPushButton("Load spectrum files")
        self.btn_r2map = QPushButton("Plot R2Map")
        self.btn_timefreq = QPushButton("Plot Time/Freq Analysis")
        # self.btn_psd = QPushButton("Plot PSD for Spec. Freq.")
        self.btn_topo = QPushButton("Plot Topography for Spec. Freq.")
        self.btn_psd_r2 = QPushButton("Plot R2 and PSD")

        self.layoutLeftButtons.addWidget(self.btn_load_files)
        self.layoutLeftButtons.addWidget(self.btn_r2map)
        self.layoutLeftButtons.addWidget(self.btn_timefreq)
        self.layoutLeftButtons.addWidget(self.btn_topo)
        self.layoutLeftButtons.addWidget(self.btn_psd_r2)

        self.layoutLeft.addLayout(self.layoutLeftButtons)
        self.dlgLayout.addLayout(self.layoutLeft)

        # FEATURE SELECTION PART
        self.layoutRight = QVBoxLayout()
        self.layoutRight.setAlignment(QtCore.Qt.AlignTop)
        self.qvBoxLayouts = [None, None]
        self.qvBoxLayouts[0] = QFormLayout()
        self.qvBoxLayouts[1] = QVBoxLayout()
        self.layoutRight.addLayout(self.qvBoxLayouts[0])
        self.layoutRight.addLayout(self.qvBoxLayouts[1])

        self.label2 = QLabel('----- SELECT FEATURES FOR TRAINING -----')
        self.label2.setAlignment(QtCore.Qt.AlignCenter)
        textFeatureSelect = "Enter pair : ELECTRODE;FREQUENCY (separated with \";\")"
        textFeatureSelect = str(textFeatureSelect + "\n(Use \":\" for frequency range)")
        textFeatureSelect = str(textFeatureSelect + "\n  Ex: FCz;14:22")
        textFeatureSelect = str(textFeatureSelect + "\n  Ex: C4;22")
        self.label3 = QLabel(textFeatureSelect)

        self.qvBoxLayouts[0].addWidget(self.label2)
        self.qvBoxLayouts[0].addWidget(self.label3)

        self.selectedFeats = []
        # Param Output 1 : First selected pair of Channels / Electrodes
        # We'll add more with a button
        self.selectedFeats.append(QLineEdit())
        self.selectedFeats[0].setText('C4;22')
        pairText = "Selected Feats Pair"
        self.qvBoxLayouts[0].addRow(pairText, self.selectedFeats[0])

        self.btn_addPair = QPushButton("Add Feature")
        self.btn_removePair = QPushButton("Remove Last Feat")
        self.btn_selectFeatures = QPushButton("Select features and generate scenarios")
        self.btn_runTrain = QPushButton("Run classifier training scenario")

        self.qvBoxLayouts[1].addWidget(self.btn_addPair)
        self.qvBoxLayouts[1].addWidget(self.btn_removePair)
        self.qvBoxLayouts[1].addWidget(self.btn_selectFeatures)
        self.qvBoxLayouts[1].addWidget(self.btn_runTrain)

        self.dlgLayout.addLayout(self.layoutRight)

        # display initial layout
        self.setLayout(self.dlgLayout)
        self.initialWindow()

    def load_files(self, path1, path2):
        data1 = load_csv_cond(path1)
        data2 = load_csv_cond(path2)
        if data1.empty or data2.empty:
            msg = QMessageBox()
            msg.setText("Please wait while OpenViBE finishes writing CSV files.")
            msg.exec_()
        else:
            self.dataNp1 = data1.to_numpy()
            self.dataNp2 = data2.to_numpy()
            self.extract_features()
            self.plotWindow()

    def extract_features(self):
        # time = self.PipelineParams.trialLengthSec
        # trials = self.PipelineParams.trialNb
        # nbElectrodes = len(self.PipelineParams.electrodeList)
        # n_bins = self.PipelineParams.fftBins
        # winLen = self.PipelineParams.burgWindowLength
        # winOverlap = self.PipelineParams.burgWindowOverlap

        time = float(self.parameterDict["TrialLength"])
        trials = int(self.parameterDict["TrialNb"])
        electrodeListStr = self.parameterDict["ChannelNames"]
        electrodeList = electrodeListStr.split(";")
        nbElectrodes = len(electrodeList)
        n_bins = int((int(self.parameterDict["PsdSize"]) / 2) + 1)
        winLen = float(self.parameterDict["TimeWindowLength"])
        winOverlap = float(self.parameterDict["TimeWindowShift"])

        power_right, power_left, time_left, time_right, time_length = Extract_Data_to_compare(self.dataNp1,
                                                                                              self.dataNp2,
                                                                                              time, trials,
                                                                                              nbElectrodes,
                                                                                              n_bins,
                                                                                              winLen, winOverlap)

        # Statistical Analysis
        electrodes_orig = channel_generator(nbElectrodes, 'TP9', 'TP10')
        freqs_left = np.arange(0, n_bins)
        Rsigned = Compute_Rsquare_Map_Welch(power_right[:, :, :(n_bins-1)], power_left[:, :, :(n_bins-1)])
        # Rsigned = Compute_Rsquare_Map_Welch(power_right[:, :, :(fs/2)], power_left[:, :, :(fs/2)])
        Rsigned_2, electrodes_final, power_left_2, power_right_2 = Reorder_Rsquare(Rsigned, electrodes_orig, power_left, power_right)

        self.Features.electrodes_orig = electrodes_orig
        self.Features.power_right = power_right_2
        self.Features.power_left = power_left_2
        self.Features.time_left = time_left
        self.Features.time_right = time_right
        self.Features.time_length = time_length
        self.Features.freqs_left = freqs_left
        self.Features.electrodes_final   = electrodes_final
        self.Features.Rsigned = Rsigned_2


    def initialWindow(self):
        self.btn_load_files.clicked.connect(lambda: self.load_files(self.path1.text(), self.path2.text()))
        self.btn_r2map.setEnabled(False)
        self.btn_timefreq.setEnabled(False)
        # self.btn_psd.setEnabled(False)
        self.btn_topo.setEnabled(False)
        self.btn_psd_r2.setEnabled(False)
        self.btn_addPair.setEnabled(False)
        self.btn_removePair.setEnabled(False)
        self.btn_selectFeatures.setEnabled(False)
        self.btn_runTrain.setEnabled(False)
        self.selectedFeats[0].setEnabled(False)
        self.show()

    def plotWindow(self):

        fres = 1
        # fs = self.PipelineParams.fSampling
        fs = 500

        self.btn_r2map.clicked.connect(lambda: self.btnR2(fres))
        self.btn_timefreq.clicked.connect(lambda: self.btnTimeFreq(fres))
        # self.btn_psd.clicked.connect(lambda: self.btnPsd(fres))
        self.btn_topo.clicked.connect(lambda: self.btnTopo(fres, fs))
        self.btn_addPair.clicked.connect(lambda: self.btnAddPair())
        self.btn_removePair.clicked.connect(lambda: self.btnRemovePair())
        self.btn_selectFeatures.clicked.connect(lambda: self.btnSelectFeatures())
        self.btn_psd_r2.clicked.connect(lambda: self.btnpsdR2(fres))

        self.btn_load_files.setEnabled(False)
        self.btn_r2map.setEnabled(True)
        self.btn_timefreq.setEnabled(True)
        # self.btn_psd.setEnabled(True)
        self.btn_topo.setEnabled(True)
        self.btn_addPair.setEnabled(True)
        self.btn_removePair.setEnabled(True)
        self.selectedFeats[0].setEnabled(True)
        self.btn_selectFeatures.setEnabled(True)
        self.btn_psd_r2.setEnabled(True)

        self.show()

    def btnR2(self, fres):
        plot_stats(self.Features.Rsigned,
                   self.Features.freqs_left,
                   self.Features.electrodes_final,
                   fres, int(self.userFmin.text()), int(self.userFmax.text()))

    def btnTimeFreq(self, fres):
        print("TimeFreq for electrode: " + self.electrodePsd.text())
        qt_plot_tf(self.Features.time_right, self.Features.time_left,
                   self.Features.time_length, self.Features.freqs_left,
                   self.Features.electrodes_final, self.electrodePsd.text(),
                   fres, int(self.userFmin.text()), int(self.userFmax.text()))

    def btnPsd(self, fres):
        qt_plot_psd(self.Features.power_right, self.Features.power_left,
                    self.Features.freqs_left, self.Features.electrodes_final,
                    self.electrodePsd.text(),
                    fres, int(self.userFmin.text()), int(self.userFmax.text()))

    def btnpsdR2(self, fres):
        qt_plot_psd_r2(self.Features.Rsigned,
                       self.Features.power_right, self.Features.power_left,
                       self.Features.freqs_left, self.Features.electrodes_final,
                       self.electrodePsd.text(),
                       fres, int(self.userFmin.text()), int(self.userFmax.text()))

    def btnTopo(self, fres, fs):
        print("Freq Topo: " + self.freqTopo.text())
        qt_plot_topo(self.Features.Rsigned, self.Features.electrodes_final,
                     int(self.freqTopo.text()), fres, fs)

    def btnAddPair(self):
        self.selectedFeats.append(QLineEdit())
        self.selectedFeats[-1].setText('C4;22')
        self.qvBoxLayouts[0].addRow("Selected Feats Pair", self.selectedFeats[-1])

    def btnRemovePair(self):
        if len(self.selectedFeats) > 1:
            result = self.qvBoxLayouts[0].getWidgetPosition(self.selectedFeats[-1])
            self.qvBoxLayouts[0].removeRow(result[0])
            self.selectedFeats.pop()

    def btnSelectFeatures(self):
        selectedFeats = []

        # Checks :
        # No empty field
        # frequencies in acceptable ranges
        # channels in list
        channelList = self.Features.electrodes_final
        n_bins = int((int(self.parameterDict["PsdSize"]) / 2) + 1)
        for idx, feat in enumerate(self.selectedFeats):
            if feat.text() == "":
                msg = QMessageBox()
                msg.setText("Pair "+str(idx+1)+" is empty...")
                msg.exec_()
                return

            [chan, freqstr] = feat.text().split(";")
            if chan not in channelList:
                msg = QMessageBox()
                msg.setText("Channel in pair " + str(idx + 1) + " (" + str(chan) + ") is not in the list...")
                msg.exec_()
                return

            freqs = freqstr.split(":")
            for freq in freqs:
                if not freq.isdigit():
                    msg = QMessageBox()
                    msg.setText("Frequency in pair " + str(idx + 1) + " (" + str(freq) + ") has an invalid format, must be an integer...")
                    msg.exec_()
                    return
                if int(freq) >= n_bins:
                    msg = QMessageBox()
                    msg.setText("Frequency in pair " + str(idx + 1) + " (" + str(freq) + ") is not in the acceptable range...")
                    msg.exec_()
                    return
            selectedFeats.append(feat.text().split(";"))
            print(feat)

        scenName = settings.templateScenFilenames[2]
        fullScenPath = os.path.join(self.scriptPath, "generated", scenName)

        # TODO : create new function "modifyscenario", creating "branches" of pipelines
        modifyTrainScenario(selectedFeats, fullScenPath)

        textGoodbye = "The training scenario using\n\n"
        for i in range(len(selectedFeats)):
            textGoodbye = str(textGoodbye +"  Channel " + str(selectedFeats[i][0]) + " at " + str(selectedFeats[i][1])+ " Hz\n")
        textGoodbye = str(textGoodbye + "\n... has been generated under:\n\n" + str(fullScenPath))

        msg = QMessageBox()
        msg.setText(textGoodbye)
        msg.exec_()




def plot_stats(Rsigned, freqs_left, electrodes, fres, fmin, fmax):
    smoothing  = False
    plot_Rsquare_calcul_welch(Rsigned,np.array(electrodes)[:], freqs_left, smoothing, fres, 10, fmin, fmax)
    plt.show()

def qt_plot_psd_r2(Rsigned, power_right, power_left, freqs_left, electrodesList, electrodeToDisp, fres, fmin, fmax):
    electrodeExists = False
    electrodeIdx = 0
    for idx, elec in enumerate(electrodesList):
        if elec == electrodeToDisp:
            electrodeIdx = idx
            electrodeExists = True
            break

    if not electrodeExists:
        msg = QMessageBox()
        msg.setText("No Electrode with this name found")
        msg.exec_()
    else:
        plot_psd2(Rsigned, power_right, power_left, freqs_left, electrodeIdx, electrodesList, 10, fmin, fmax, fres)
        plt.show()

def qt_plot_psd(power_right, power_left, freqs_left, electrodesList, electrodeToDisp, fres, fmin, fmax):
    electrodeExists = False
    electrodeIdx = 0
    for idx, elec in enumerate(electrodesList):
        if elec == electrodeToDisp:
            electrodeIdx = idx
            electrodeExists = True
            break

    if not electrodeExists:
        msg = QMessageBox()
        msg.setText("No Electrode with this name found")
        msg.exec_()
    else:
        plot_psd(power_right, power_left, freqs_left, electrodeIdx, electrodesList, 10, fmin, fmax, fres)
        plt.show()


def qt_plot_topo(Rsigned, electrodes, frequency, fres, fs):
    topo_plot(Rsigned, round(frequency/fres), electrodes, fres, fs, 'Signed R square')
    plt.show()


def qt_plot_tf(timefreq_right, timefreq_left, time_left, freqs_left, electrodesList, electrodeToDisp, fres, fmin, fmax):
    electrodeExists = False
    electrodeIdx = 0
    for idx, elec in enumerate(electrodesList):
        if elec == electrodeToDisp:
            electrodeIdx = idx
            electrodeExists = True
            break

    if not electrodeExists:
        msg = QMessageBox()
        msg.setText("No Electrode with this name found")
        msg.exec_()
    else:
        time_frequency_map_between_cond(timefreq_right, time_left, freqs_left, electrodeIdx,
                                        fmin, fmax, fres, 10, timefreq_left, electrodesList)
        plt.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    dlg = Dialog()
    sys.exit(app.exec_())

