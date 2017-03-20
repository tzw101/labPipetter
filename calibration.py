# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Feb 14 2017)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = 'Calibration', pos = wx.DefaultPosition, size = wx.Size( 200,200 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL, name = u"Calibration" )

		self.SetSizeHintsSz( wx.Size( 200,200 ), wx.Size( 200,200 ))

		bSizer3 = wx.BoxSizer( wx.VERTICAL )

		self.image = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( u"C:\\Users\\user\\Desktop\\arrow.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.image, 1, wx.ALL|wx.EXPAND, 5 )

		gSizer2 = wx.GridSizer( 0, 2, 0, 0 )

		self.axis = wx.CheckBox( self, wx.ID_ANY, u"z-axis", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.axis, 0, wx.ALL, 5 )

		self.cancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.cancel, 0, wx.ALL, 5 )

		self.tenFolds = wx.CheckBox( self, wx.ID_ANY, u"10x", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.tenFolds, 0, wx.ALL, 5 )


		bSizer3.Add( gSizer2, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer3 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.image.Bind( wx.EVT_LEFT_DOWN, self.arrow )
		self.cancel.Bind( wx.EVT_BUTTON, self.reset )
		self.tenFolds.Bind( wx.EVT_CHECKBOX, self.multiply10 )
		self.axis.Bind( wx.EVT_CHECKBOX, self.z_axis )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def arrow( self, event ):
		event.Skip()

	def reset( self, event ):
		event.Skip()

	def multiply10( self, event ):
		event.Skip()

	def z_axis( self, event ):
		event.Skip()



