$(document).ready(function() {
	var screenX = screen.width,
	    screenY = screen.height;
	if (screenX == 320) {
	    $("body").attr("class","small");
	}
	if ($(window).width()<=800) {
	    $("body").attr("class","small");
	}
	if ($(window).width()<=600) {
	    $("body").attr("class","tiny");
	}
    }
    );
