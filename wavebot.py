#!/usr/bin/env python
# -*- coding: utf-8 -*-

from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document

import re
from datamodel import userplurkdata

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
  query = re.match('.*\[(.+)\].*', contents)
  blip.AppendText('\n')
  try:
    if query.group(0):
      subquery = query.group(1).split(' ')
      if subquery[0] == 'boy':
        blip.AppendText('%s' % subquery[0])
        blip.AppendText('%s' % properties)
        #blip.AppendText('%s' % context.GetBlipById(properties['blipId']))
        #blip.AppendInlineBlip().GetDocument().AppendText('\nPlease type a value for all form elements.')
        #blip.SetAnnotation(document.Range(),"link/manual", 'http://google.com')
        #Notify(context)
        #newblip = context.GetBlipById(properties['blipId']).CreateChild()
        #newblip.GetDocument().SetText('New blip!! Ya!')
      elif subquery[0] == 'girl':
        blip.AppendText('%s' % subquery[0])
      elif subquery[0] == 'show':
        try:
          showuser = userplurkdata.gql('where uname = :1' , subquery[1])
          blip.AppendText(u"u want to show %s \n" % subquery[1])
          for i in showuser:
            blip.AppendText(u"%s \n" % (i.uname))
            m = re.search(i.uname, contents)
            blip.SetAnnotation(document.Range(m.start(),m.end()),"link/manual",'http://www.plurk.com/%s' % i.uname)
            if i.avatar:
              blip.AppendElement(document.Image('http://avatars.plurk.com/%s-big%s.jpg' % (i.key().id_or_name(),i.avatar)))
            else:
              blip.AppendText('(No avatar.)')
        except:
          blip.AppendText(u"No people!!")
      else:
        # No match keywords
        blip.AppendText(u"I don't know what do you mean. → %s." % subquery[0])
    else:
      # No match keywords
      pass
    image = document.Image('http://plurkii.appspot.com/favicon.ico')
    blip.AppendElement(image)
  except:
    # No keywords
    ## Out off here whithin statable.
    blip.AppendText(u"I don't know what do you mean. → %s \n view howto." % contents)

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
