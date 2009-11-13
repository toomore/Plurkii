#!/usr/bin/env python
# -*- coding: utf-8 -*-

from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document

import re

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
  howto = """
Welcome to use Plurkii-wave-bot
You can type below keywords in reply to get more information.
  [boy] => Random to show a boy.
  [girl] => Random to show a girl.
  [show PLURK_ID] => To show a user plurk information."""
  blip.AppendText(howto)
  blip.AppendElement(document.Image('http://plurkii.appspot.com/favicon.ico'))

def OnSubmit(properties, context):
  blip = context.GetBlipById(properties['blipId']).GetDocument()
  contents = blip.GetText()
  query = re.match('.*\[(.+) (.+)\].*', contents)
  blip.AppendText('\n')
  try:
    if query.group(0):
      if query.group(1)  == 'boy':
        blip.AppendText("%s - %s" % (query.group(1),query.group(2)))
      else:
        #blip.AppendText("ELSE = %s,%s" % (query.group(1),query.group(2)))
        blip.AppendText(u"I don't know what do you mean. → %s" % contents)
    else:
      pass
  except:
    blip.AppendText(u"I don't know what do you mean. → %s \n view howto." % contents)
  image = document.Image('http://plurkii.appspot.com/favicon.ico')
  blip.AppendElement(image)

def Notify(context):
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().SetText("Hi everybody!")

if __name__ == '__main__':
  myRobot = robot.Robot('Plurkii!', 
      image_url='http://plurkii.appspot.com/favicon.ico',
      version='26',
      profile_url='http://plurkii.appspot.com/')
  #myRobot.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED, OnParticipantsChanged)
  myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
  #myRobot.RegisterHandler(events.DOCUMENT_CHANGED, OnRobotAdded)
  myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnSubmit)
  myRobot.Run(debug=True)
