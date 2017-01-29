$(function(){
	
	$.nette.init();

	$("#main-search .query").on("propertychange change keyup paste input", function(){
		$("#main-search input.submit").show();
	});
	
	$(".small-searchbox-wrapper .text").on("propertychange change keyup paste input", function(){
		$(".small-searchbox-wrapper input.submit").show();
	});
	
	$(".checkbox-wrapper").click(function() {
		$(this).find(".false-checkbox").toggleClass("checked");
		
		var checkbox = $(this).find("input[type='checkbox']");

		if( !checkbox.prop("checked") ){
			checkbox.prop("checked",true);
		} else {
			checkbox.prop("checked",false);
		}
	});

	$('.scrollToDiv').click(function(event) {

		event.preventDefault();
		var scrollDiv = $(this).attr('href');

		var position = $(''+scrollDiv+'').position();
		var positionTop = position.top;

		$('html, body').stop().animate({
			scrollTop: positionTop
		}, 900);
	});	
	
	$(".search-icon").click(function() {
		$(".small-searchbox-wrapper").slideToggle( "fast", function() {});
		$(".small-searchbox-wrapper input.text").focus();
		return false;
	});	
	
});

