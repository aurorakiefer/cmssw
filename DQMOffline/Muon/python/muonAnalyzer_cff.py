import FWCore.ParameterSet.Config as cms

from DQMOffline.Muon.muonRecoOneHLT_cfi import *
from DQMOffline.Muon.muonEfficiencyAnalyzer_cfi import *
from DQMOffline.Muon.diMuonHistograms_cfi import *
from DQMOffline.Muon.muonKinVsEtaAnalyzer_cfi import *
from DQMOffline.Muon.muonRecoAnalyzer_cfi import *
from DQMOffline.Muon.muonEnergyDepositAnalyzer_cfi import *
from DQMOffline.Muon.segmentTrackAnalyzer_cfi import *
from DQMOffline.Muon.muonSeedsAnalyzer_cfi import *
from DQMOffline.Muon.muonPFAnalyzer_cfi import *
from DQMOffline.Muon.triggerMatchMonitor_cfi import *

muonAnalyzer = cms.Sequence(muonEnergyDepositAnalyzer*
                            muonSeedsAnalyzer*
                            muonRecoAnalyzer*
                            glbMuonSegmentAnalyzer*
                            staMuonSegmentAnalyzer*
                            muonKinVsEtaAnalyzer*
                            diMuonHistos*
                            EfficiencyAnalyzer*
                            muonPFsequence*
                            muonRecoOneHLT)



muonAnalyzer_miniAOD = cms.Sequence(muonRecoAnalyzer_miniAOD* 
                                    muonKinVsEtaAnalyzer_miniAOD*
                                    diMuonHistos_miniAOD*
                                    EfficiencyAnalyzer_miniAOD*
                                    triggerMatchMonitor_miniAOD)

muonAnalyzer_noHLT = cms.Sequence(muonEnergyDepositAnalyzer*
                                  muonSeedsAnalyzer*
                                  muonRecoAnalyzer*
                                  glbMuonSegmentAnalyzer*
                                  staMuonSegmentAnalyzer*
                                  muonKinVsEtaAnalyzer*
                                  diMuonHistos*
                                  EfficiencyAnalyzer* 
                                  muonPFsequence)
