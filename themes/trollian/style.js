{"main":
 {"style": "background-image:url($path/tnbg2.png);background-color:rgba(255,255,255,0);",
  "size": [300, 620],
  "icon": "$path/trayicon3.png",
  "newmsgicon": "$path/trayicon.gif",
  "windowtitle": "TROLLIAN",
  "close": { "image": "$path/x.gif",
             "loc": [275, 0]},
  "minimize": { "image": "$path/m.gif",
                "loc": [255, 0]},
  "menubar": { "style": "font-family: 'Courier New'; font-weight: bold; font-size: 12px;" },
  "menu" : { "style": "font-family: 'Courier New'; font-weight: bold; font-size: 12px; background-color: #e5000f; border:2px solid #ff0000",
             "selected": "background-color: #ff0000",
             "menuitem": "margin-right:10px;",
             "loc": [10,0]
           },
  "sounds": { "alertsound": "$path/alarm.wav" },
  "menus": {"client": {"_name": "GRUBBER",
                       "options": "OPTIONS",
                       "exit": "ABSCOND"},
            "profile": {"_name": "HEMOSPECTRUM",
                        "switch": "SWITCH",
                        "theme": "THEME",
                        "quirks": "ANNOYING"},
            "rclickchumlist": {"pester": "TROLL",
                               "removechum": "REMOVE LOSER"}
           },
  "chums": { "style": "background-color: black;color: white;font: bold;font-family: 'Courier New';selection-background-color:#ffb6b6; ",
             "loc": [20, 65],
             "size": [266, 270],
             "moods": { "chummy": { "icon": "$path/chummy.gif",
                                    "color": "white" },
                        "offline": { "icon": "$path/offline.gif",
                                     "color": "#919191"},
                        "rancorous": { "icon": "$path/rancorous.gif",
                                       "color": "red" },
						"detestful": { "icon": "$path/detestful.gif",
									   "color": "red" },
						"devious": { "icon": "$path/devious.gif",
									 "color": "white" },
						"discontent": { "icon": "$path/discontent.gif",
										"color": "white" },
						"distraught": { "icon": "$path/distraught.gif",
										"color": "white" },
						"ecstatic": { "icon": "$path/estatic.gif",
									  "color": "white" },
						"pleasant": { "icon": "$path/pleasant.gif",
									  "color": "white" },
						"relaxed": { "icon": "$path/relaxed.gif",
									 "color": "white" },
						"sleek": { "icon": "$path/sleek.gif",
								   "color": "white" },
						"smooth": { "icon": "$path/smooth.gif",
									"color": "white" },
						"unruly": { "icon": "$path/unruly.gif",
									"color": "white" }
                      }
           },
  "mychumhandle": { "label": { "text": "MYTROLLTAG",
                               "loc": [85,410],
                               "style": "color:black;font:bold;" },
                    "handle": { "style": "border:3px solid #550000; background: black; color:white;",
                                "loc": [20,430],
                                "size": [220,30] },
                    "colorswatch": { "loc": [243,430],
                                     "size": [40,30],
                                     "text": "" }
                  },
  "defaultwindow": { "style": "background: #e5000f; font-family:'Courier New';font:bold;selection-background-color:#ffb6b6; " 
                   },
  "addchum": { "style": "background: black; border:5px solid #550000; font: bold;color:white;",
               "loc": [20,340],
               "size": [100, 40],
               "text": "ADD LOSER"
             },
  "pester": { "style": "background: black; border:5px solid #550000; font: bold;color:white;",
               "loc": [130,340],
               "size": [100, 40],
               "text": "TROLL"
             },
  "defaultmood": 7,
  "moodlabel": { "style": "",
				 "loc": [20, 430],
				 "text": "MOODS"
			   },
  "moods": [
      { "style": "text-align:left; background: black; border:3px solid black; padding: 5px;color:#dbdbdb;", 
		"selected": "text-align:left; background: white; border:3px solid black; padding: 5px;font: bold;",
		"loc": [20, 470],
		"size": [133, 30],
	    "text": "ECSTATIC",
		"icon": "$path/estatic.gif",
		"mood": 7
	  },
	  { "style": "text-align:left; background: black; border:3px solid black; padding: 5px;color: #dbdbdb", 
		"selected": "text-align:left; background: white; border:3px solid black; padding: 5px;font: bold;",
		"loc": [20, 497],
		"size": [133, 30],
		"text": "RELAXED",
		"icon": "$path/relaxed.gif",
		"mood": 8
	  },
	  { "style": "text-align:left; background: black; border:3px solid black; padding: 5px;color:#dbdbdb;", 
		"selected": "text-align:left; background: white; border:3px solid black; padding: 5px;font: bold;",
		"loc": [20, 524],
		"size": [133, 30],
		"text": "DISCONTENT",
		"icon": "$path/discontent.gif",
		"mood": 9
	  },
	  { "style": "text-align:left; background: black; border:3px solid black; padding: 5px;color:#dbdbdb;", 
		"selected": "text-align:left; background: white; border:3px solid black; padding: 5px;font: bold;",
		"loc": [150, 470],
		"size": [133, 30],
		"text": "DEVIOUS",
		"icon": "$path/devious.gif",
		"mood": 10
	  },
	  { "style": "text-align:left; background: black; border:3px solid black; padding: 5px;color:#dbdbdb;", 
		"selected": "text-align:left; background: white; border:3px solid black; padding: 5px;font: bold;",
		"loc": [150, 497],
		"size": [133, 30],
		"text": "SLEEK",
		"icon": "$path/sleek.gif",
		"mood": 11
	  },
	  { "style": "text-align:left; background: red; border:3px solid black; padding: 5px;", 
		"selected": "text-align:left; background: red; border:3px solid black; padding: 5px;font: bold;",
		"loc": [150, 524],
		"size": [133, 30],
		"text": "DETESTFUL",
		"icon": "$path/detestful.gif",
		"mood": 12
	  },
	  { "style": "text-align:center; background: #919191; border:3px solid black; padding: 5px;", 
		"selected": "text-align:center; background: #919191; border:3px solid black; padding: 5px;font: bold;",
		"loc": [20, 551],
		"size": [263, 30],
		"text": "ABSCOND",
		"icon": "$path/offline.gif",
		"mood": 2
	  }
  ]
 },
 "convo":
 {"style": "background: #e5000f; font-family: 'Courier New'",
  "size": [600, 500],
  "chumlabel": { "style": "background: rgba(255, 255, 255, 25%);",
                 "text" : "trolling $handle" 
               },
  "textarea": {
      "style": "background: white;font:bold;"
  },
  "input": {
      "style": "background: white;"
  },
  "tabs": {
      "style": "",
      "newmsgcolor": "red",
      "tabstyle": 0
  },
  "text": {
      "beganpester": "began trolling",
      "ceasepester": "gave up trolling"
  }
 }
 
}
