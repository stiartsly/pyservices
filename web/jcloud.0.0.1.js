$(document).ready(function() {
	$("#instAppTxt").attr("value", "thunder");

	function invokeGetMethod(serviceUrl, args, succFunc) {
		$.get(serviceUrl, args, succFunc, "json");
	}

	function invokePostMethod(appName, appVer, action, postFunc) {
        if (appVer != "") {
            verArgs = ";ver=" + appVer
        } else {
            verArgs = ""
        }
		var args = "app=" + appName + verArgs + ";action=" + action;
		$.post("appservice", args, function(data, status) {
			switch(data.result) {
			case "ESuccess": break;
			default: $("#result").text(data.result); return;
			}
			postFunc(appName);
			$("#result").text(data.result);
		},
		"json");
	}

    function displayAvaiAppList(appName, appVer) {
        appDiv = document.createElement("div");
        appDiv.innerHTML = appName;
        appDiv.onclick = function() {
            appInfo = $(this).text() + ":" + $(this).attr("version")
            $("#instAppTxt").attr("value", appInfo)
        }
		$(appDiv).attr("class", "appName");
		$(appDiv).attr("version", appVer);

        verDiv = document.createElement("div");
        verDiv.innerHTML = appVer;
        
        div = document.createElement("div");
        $(div).append(appDiv, verDiv);
        return div
    }

	$("#getListBtn").click(function() {
		var els = $("#appList").children();
		for (i = 0; i < els.length; i++) {
			els[i].remove();
		}

        var url = "appservice/availableAppList";
		invokeGetMethod(url, function(data, status) {
			/* {"message": [ 
					{"appName": "thunder",       "appVer": "0.0.1" },
					{"appName": "cameraservice", "appVer": "0.0.3" }
					],
				"result": "ESuccess"
			   }*/
            if (data.result != "ESuccess") {
                $("#result").text(data.result);
                return ;
            }
            for (i = 0; i < data.message.length; i++) {
                appName = data.message[i].appName;
                appVer  = data.message[i].appVer;

                div = displayAvaiAppList(appName, appVer);
                $("#appList").append(div);
            }
			$("#result").text(data.result);
		});
	});
	$("#getListBtn").click();

	function displayInstedAppItem(appName, actionVal) {
        actionArray = ["Enable", "Disable", "Uninstall" ];
		if ($.inArray(actionVal, actionArray) < 0)
			return ;

		function createInputBtn(actionVal) {
			var el= document.createElement("input");
			$(el).attr("type"   , "button");
        	$(el).attr("class"  , "instAppBtnCls");
        	$(el).attr("value"  , actionVal);
		
			return el;
		}

		var div = document.createElement("div");
		$(div).attr("id"    , appName);

		var el= document.createElement("a");
		el.innerHTML = appName
		$(el).attr("class" , "instApp");
		$(el).attr("target", "_blank");
		$(el).attr("href"  , "appservice/" + appName + "/");
		$(div).append(el);

		$(div).append(createInputBtn(actionVal))
		$(div).append(createInputBtn("Uninstall"))

		$("#instAppList").append(div);
		$("input.instAppBtnCls").click(function() {
		
			var action=$(this).attr("value");
			var btn = $(this);
			switch(action) {
			case "Disable": 
				invokePostMethod(appName,"", action, function(args) {
					btn.attr("value", "Enable");
				});
				break;
			case "Enable":
				invokePostMethod(appName,"",action, function(args) {
					btn.attr("value", "Disable");
				});
				break;
			case "Uninstall":
				invokePostMethod(appName,"",action, function(args) {
					$("#" + appName).remove();
				});
				break;
			default:
				alert("default routine action:##" + action + "#####");
			}
		});
	}

	/* the click action  for installing an app with given name */
	$("#instAppBtn").click(function() {
		/* install an app with given name .*/
		var appInfo= $("#instAppTxt").val().split(":");
        appName = appInfo[0];
        appVer  = appInfo[1];
		invokePostMethod(appName, appVer, "Install", function(args) {
			displayInstedAppItem(args, "Disable");
		});
	});

	$("#getInstAppsBtn").click(function() {
        var url = "appservice/installedAppList";
		invokeGetMethod(url, function(data, status) {
			/* response json text */
			/* {"message": [ 
					{"appName": "thunder",       "appStatus": "Enabled"  },
					{"appName": "cameraservice", "appStatus": "Disabled" }
					],
				"result": "ESuccess"
			   }*/
			function status2actionVal(status) {
				switch (status) {
				case "Enabled" : return "Disable"  ;
				case "Disabled": return "Enable"   ;
				default        : return "Undefined";
				}
			}
			for (i = 0; i < data.message.length; i++) {
				displayInstedAppItem(data.message[i].appName,
					status2actionVal(data.message[i].appStatus));
			}
        });
	});
	$("#getInstAppsBtn").hide();
	$("#getInstAppsBtn").click();
});


