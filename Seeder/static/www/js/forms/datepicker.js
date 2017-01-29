$(document).ready(function(){
	$.datepicker.regional['cs'] = {
		closeText: 'Zav\u0159ít',
		prevText: '&#x3c;D\u0159íve',
		nextText: 'Pozd\u011bji&#x3e;',
		currentText: 'Nyní',
		monthNamesShort: ['Leden','Únor','B\u0159ezen','Duben','Kv\u011bten','\u010cerven','\u010cervenec','Srpen','Zá\u0159í','\u0158íjen','Listopad','Prosinec'],
		/*monthNamesShort: ['led','úno','b\u0159e','dub','kv\u011b','\u010der','\u010dvc','srp','zá\u0159','\u0159íj','lis','pro'],*/
		dayNames: ['ned\u011ble', 'pond\u011blí', 'úterý', 'st\u0159eda', '\u010dtvrtek', 'pátek', 'sobota'],
		dayNamesShort: ['Ne', 'Po', 'Út', 'St', '\u010ct', 'Pá', 'So'],
		dayNamesMin: ['Ne','Po','Út','St','\u010ct','Pá','So'],
		weekHeader: 'Týd',
		timeFormat: 'hh:mm',
		firstDay: 1,
		isRTL: false,
		showMonthAfterYear: false,
		yearSuffix: '',
        changeMonth: true,
        changeYear: true,
        dateFormat: 'd.m.yy',
        yearRange: '2000:2030'
	};
	$('input.datepicker').datepicker($.datepicker.regional['cs']);
	$('input.datepicker').datepicker({ duration: 'fast' });
	$('input.datepicker').datepicker({ showAnim: '' });
	$('input.datepicker').datepicker({ altField: '#actualDate' });
	$('input.datepicker').datepicker({ minDate: '-20', maxDate: '+12M +10D' });

});