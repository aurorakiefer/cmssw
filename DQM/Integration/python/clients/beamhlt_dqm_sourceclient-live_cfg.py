from __future__ import print_function
import FWCore.ParameterSet.Config as cms

# Define once the BeamSpotOnline record name,
# will be used both in BeamMonitor setup and in payload creation/upload
BSOnlineRecordName = 'BeamSpotOnlineHLTObjectsRcd'
BSOnlineTag = 'BeamSpotOnlineHLT'
BSOnlineJobName = 'BeamSpotOnlineHLT'
BSOnlineOmsServiceUrl = 'http://cmsoms-services.cms:9949/urn:xdaq-application:lid=100/getRunAndLumiSection'
useLockRecords = True

import sys
from Configuration.Eras.Era_Run3_cff import Run3
process = cms.Process("BeamMonitor", Run3)

# Message logger
#process.load("FWCore.MessageLogger.MessageLogger_cfi")
#process.MessageLogger = cms.Service("MessageLogger",
#    debugModules = cms.untracked.vstring('*'),
#    cerr = cms.untracked.PSet(
#        FwkReport = cms.untracked.PSet(
#            optionalPSet = cms.untracked.bool(True),
#            reportEvery = cms.untracked.int32(1000),
#            limit = cms.untracked.int32(999999)
#        )
#    ),
#    destinations = cms.untracked.vstring('cerr'),
#)

# switch
live = True # FIXME
unitTest = False

if 'unitTest=True' in sys.argv:
  live=False
  unitTest=True
  useLockRecords = False

# Common part for PP and H.I Running
#-----------------------------
if unitTest:
  process.load("DQM.Integration.config.unittestinputsource_cfi")
  from DQM.Integration.config.unittestinputsource_cfi import options

  # Overwrite source of the unitTest to use a streamer file instead of the DAS query output
  print("[beamhlt_dqm_sourceclient-live_cfg]:: Overriding DAS input to use a streamer file")

  # Read streamer files from https://github.com/cms-data/DQM-Integration
  import os
  dqm_integration_data = [os.path.join(dir,'DQM/Integration/data') for dir in os.getenv('CMSSW_SEARCH_PATH','').split(":") if os.path.exists(os.path.join(dir,'DQM/Integration/data'))][0]

  # Set the process source
  process.source = cms.Source("DQMStreamerReader",
      runNumber = cms.untracked.uint32(346373),
      runInputDir = cms.untracked.string(dqm_integration_data),
      SelectEvents = cms.untracked.vstring('*'),
      streamLabel = cms.untracked.string('streamDQMOnlineBeamspot'),
      scanOnce = cms.untracked.bool(True),
      minEventsPerLumi = cms.untracked.int32(1000),
      delayMillis = cms.untracked.uint32(500),
      nextLumiTimeoutMillis = cms.untracked.int32(0),
      skipFirstLumis = cms.untracked.bool(False),
      deleteDatFiles = cms.untracked.bool(False),
      endOfRunKills  = cms.untracked.bool(False),
      inputFileTransitionsEachEvent = cms.untracked.bool(False)
  )

elif live:
  # for live online DQM in P5
  process.load("DQM.Integration.config.inputsource_cfi")
  from DQM.Integration.config.inputsource_cfi import options
  # new stream label
  process.source.streamLabel = cms.untracked.string('streamDQMOnlineBeamspot')
else:
  process.load("DQM.Integration.config.fileinputsource_cfi")
  from DQM.Integration.config.fileinputsource_cfi import options

# for testing in lxplus
#process.load("DQM.Integration.config.fileinputsource_cfi")
#from DQM.Integration.config.fileinputsource_cfi import options

#--------------------------
# HLT Filter
# 0=random, 1=physics, 2=calibration, 3=technical
#--------------------------
process.hltTriggerTypeFilter = cms.EDFilter("HLTTriggerTypeFilter",
    SelectedTriggerType = cms.int32(1)
)

#-----------------------------
# DQM Live Environment
#-----------------------------
process.load("DQM.Integration.config.environment_cfi")
process.dqmEnv.subSystemFolder = 'BeamMonitorHLT'
process.dqmSaver.tag           = 'BeamMonitorHLT'
process.dqmSaver.runNumber     = options.runNumber
process.dqmSaverPB.tag         = 'BeamMonitorHLT'
process.dqmSaverPB.runNumber   = options.runNumber

# Configure tag and jobName if running Playback system
if process.isDqmPlayback.value :
  BSOnlineTag = BSOnlineTag + 'Playback'
  BSOnlineJobName = BSOnlineJobName + 'Playback'
  BSOnlineOmsServiceUrl = ''
  useLockRecords = False

#-----------------------------
# BeamMonitor
#-----------------------------
process.load("DQM.BeamMonitor.BeamMonitor_cff")

#---------------
# Calibration
#---------------
# Condition for P5 cluster
process.load("DQM.Integration.config.FrontierCondition_GT_cfi")
process.GlobalTag.DBParameters.authenticationPath = cms.untracked.string('.')
# Condition for lxplus: change and possibly customise the GT
#from Configuration.AlCa.GlobalTag import GlobalTag as gtCustomise
#process.GlobalTag = gtCustomise(process.GlobalTag, 'auto:run2_data', '')

# Change Beam Monitor variables
process.dqmBeamMonitor.useLockRecords = cms.untracked.bool(useLockRecords)
if process.dqmRunConfig.type.value() == "production":
  process.dqmBeamMonitor.BeamFitter.WriteAscii = True
  process.dqmBeamMonitor.BeamFitter.AsciiFileName = '/nfshome0/yumiceva/BeamMonitorDQM/BeamFitResults.txt'
  process.dqmBeamMonitor.BeamFitter.WriteDIPAscii = True
  process.dqmBeamMonitor.BeamFitter.DIPFileName = '/nfshome0/dqmpro/BeamMonitorDQM/BeamFitResults.txt'
else:
  process.dqmBeamMonitor.BeamFitter.WriteAscii = False
  process.dqmBeamMonitor.BeamFitter.AsciiFileName = '/nfshome0/yumiceva/BeamMonitorDQM/BeamFitResults.txt'
  process.dqmBeamMonitor.BeamFitter.WriteDIPAscii = True
  process.dqmBeamMonitor.BeamFitter.DIPFileName = '/nfshome0/dqmdev/BeamMonitorDQM/BeamFitResults.txt'

process.dqmcommon = cms.Sequence(process.dqmEnv
                               * process.dqmSaver*process.dqmSaverPB)

process.monitor = cms.Sequence(process.dqmBeamMonitor)

#-----------------------------------------------------------
# process customizations included here
from DQM.Integration.config.online_customizations_cfi import *
process = customise(process)

# Digitisation: produce the TCDS digis containing BST record
from EventFilter.OnlineMetaDataRawToDigi.tcdsRawToDigi_cfi import *
process.tcdsDigis = tcdsRawToDigi.clone()

#------------------------
# Set rawDataRepacker (HI and live) or rawDataCollector (for all the rest)
if (process.runType.getRunType() == process.runType.hi_run and live):
    rawDataInputTag = "rawDataRepacker"
elif unitTest:
    # This is needed until we update the streamer files used for the unitTest
    rawDataInputTag = "rawDataCollector"
else:
    # Use raw data from selected TCDS FEDs (1024, 1025)
    rawDataInputTag = "hltFEDSelectorTCDS"

process.tcdsDigis.InputLabel = rawDataInputTag

#-----------------------------------------------------------
# Swap offline <-> online BeamSpot as in Express and HLT
import RecoVertex.BeamSpotProducer.onlineBeamSpotESProducer_cfi as _mod
process.BeamSpotESProducer = _mod.onlineBeamSpotESProducer.clone()
import RecoVertex.BeamSpotProducer.BeamSpotOnline_cfi
process.offlineBeamSpot = RecoVertex.BeamSpotProducer.BeamSpotOnline_cfi.onlineBeamSpotProducer.clone()

#--------------------------
# Proton-Proton Stuff
#--------------------------

if (process.runType.getRunType() == process.runType.pp_run or
    process.runType.getRunType() == process.runType.pp_run_stage1 or
    process.runType.getRunType() == process.runType.hpu_run or
    process.runType.getRunType() == process.runType.hi_run or
    process.runType.getRunType() == process.runType.commissioning_run):

    print("[beamhlt_dqm_sourceclient-live_cfg]:: Running pp")

    process.load("RecoVertex.BeamSpotProducer.BeamSpot_cfi")

    process.dqmBeamMonitor.monitorName = 'BeamMonitorHLT'

    process.dqmBeamMonitor.OnlineMode = True              
    process.dqmBeamMonitor.recordName = BSOnlineRecordName

    process.dqmBeamMonitor.resetEveryNLumi   = 5
    process.dqmBeamMonitor.resetPVEveryNLumi = 5

    process.dqmBeamMonitor.PVFitter.minNrVerticesForFit = 20
    process.dqmBeamMonitor.PVFitter.minVertexNdf        = 10
  
    # some inputs to BeamMonitor
    if(process.runType.getRunType() == process.runType.hi_run):
      process.dqmBeamMonitor.BeamFitter.TrackCollection = 'hltPFMuonMergingPPOnAA'
      process.dqmBeamMonitor.primaryVertex              = 'hltVerticesPFFilterPPOnAA'
      process.dqmBeamMonitor.PVFitter.VertexCollection  = 'hltVerticesPFFilterPPOnAA'
    else:
      process.dqmBeamMonitor.BeamFitter.TrackCollection = 'hltPFMuonMerging'
      process.dqmBeamMonitor.primaryVertex              = 'hltVerticesPFFilter'
      process.dqmBeamMonitor.PVFitter.VertexCollection  = 'hltVerticesPFFilter'

    # keep checking this with new release expected close to 1
    process.dqmBeamMonitor.PVFitter.errorScale = 0.95

    #TriggerName for selecting pv for DIP publication, NO wildcard needed here
    #it will pick all triggers which have these strings in their name
    process.dqmBeamMonitor.jetTrigger = cms.untracked.vstring(
        "HLT_HT300_Beamspot", "HLT_HT300_Beamspot",
        "HLT_PAZeroBias_v", "HLT_ZeroBias_", "HLT_QuadJet",
        "HLT_HI",
        "HLT_PixelClusters")

    process.dqmBeamMonitor.hltResults = "TriggerResults::HLT"

    #---------
    # Upload BeamSpotOnlineObject (HLTRcd) to CondDB
    if unitTest == False:
      process.OnlineDBOutputService = cms.Service("OnlineDBOutputService",
        DBParameters = cms.PSet(
                                messageLevel = cms.untracked.int32(0),
                                authenticationPath = cms.untracked.string('.')
                               ),

        # Upload to CondDB
        connect = cms.string('oracle://cms_orcon_prod/CMS_CONDITIONS'),
        preLoadConnectionString = cms.untracked.string('frontier://FrontierProd/CMS_CONDITIONS'),
        runNumber = cms.untracked.uint64(options.runNumber),
        omsServiceUrl = cms.untracked.string(BSOnlineOmsServiceUrl),
        latency = cms.untracked.uint32(2),
        autoCommit = cms.untracked.bool(True),
        saveLogsOnDB = cms.untracked.bool(True),
        jobName = cms.untracked.string(BSOnlineJobName), # name of the DB log record
        toPut = cms.VPSet(cms.PSet(
            record = cms.string(BSOnlineRecordName),
            tag = cms.string(BSOnlineTag),
            timetype = cms.untracked.string('Lumi'),
            onlyAppendUpdatePolicy = cms.untracked.bool(True)
        )),
        frontierKey = cms.untracked.string(options.runUniqueKey)
      )

    else:
      process.OnlineDBOutputService = cms.Service("OnlineDBOutputService",
        DBParameters = cms.PSet(
                                messageLevel = cms.untracked.int32(0),
                                authenticationPath = cms.untracked.string('.')
                                ),

        # Upload to CondDB
        connect = cms.string('sqlite_file:BeamSpotOnlineHLT.db'),
        preLoadConnectionString = cms.untracked.string('sqlite_file:BeamSpotOnlineHLT.db'),
        runNumber = cms.untracked.uint64(options.runNumber),
        lastLumiFile = cms.untracked.string('src/DQM/Integration/python/clients/last_lumi.txt'),
        latency = cms.untracked.uint32(2),
        autoCommit = cms.untracked.bool(True),
        toPut = cms.VPSet(cms.PSet(
            record = cms.string(BSOnlineRecordName),
            tag = cms.string(BSOnlineTag),
            timetype = cms.untracked.string('Lumi'),
            onlyAppendUpdatePolicy = cms.untracked.bool(True)
        )),
        frontierKey = cms.untracked.string(options.runUniqueKey)
      )

    print("Configured frontierKey", options.runUniqueKey)

    process.p = cms.Path( process.hltTriggerTypeFilter
                        * process.tcdsDigis
                        * process.dqmcommon
                        * process.offlineBeamSpot
                        * process.monitor )

print("Final Source settings:", process.source)

