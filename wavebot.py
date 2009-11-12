#!/usr/bin/env python
# -*- coding: utf-8 -*-

from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document

def OnParticipantsChanged(properties, context):
  """Invoked when any participants have been added/removed."""
  added = properties['participantsAdded']
  for p in added:
    Notify(context)

def OnRobotAdded(properties, context):
  """Invoked when the robot has been added."""
  #root_wavelet = context.GetBlipById(properties['blipId'])
  #root_wavelet.GetRootWavelet().CreateBlip().GetDocument().SetText("I'm alive!")
  #sub_blip = root_wavelet.CreateChild()
  #sub_blip.GetDocument().AppendText("I'm alive!")
  #root_wavelet = context.GetRootWavelet()
  #root_wavelet.CreateBlip().GetDocument().SetText("I'm alive!")
  blip = context.GetBlipById(properties['blipId']).GetDocument()
  contents = blip.GetText()
  blip.AppendText("GOGOGO!!!(%s)" % contents)
  image = document.Image('https://wave.google.com/wave/static/images/logo_preview.png')
  blip.AppendElement(image)
  blip.AppendElement(document.Range())
  blip.AppendText('\nEnd')


def Notify(context):
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().SetText("Hi everybody!")

if __name__ == '__main__':
  myRobot = robot.Robot('Plurkii!', 
      image_url='http://plurkii.appspot.com/favicon.ico',
      version='22',
      profile_url='http://plurkii.appspot.com/')
  #myRobot.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED, OnParticipantsChanged)
  myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
  #myRobot.RegisterHandler(events.DOCUMENT_CHANGED, OnRobotAdded)
  myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnRobotAdded)
  myRobot.Run(debug=True)
