/* 
 * Набор скриптов для просмотра грозовых событий за выбранный период времени
 */
function oldtime_count(){
	$.ajax({
		type:		"GET",
		url: 		"php/oldtime.php?count=yes&day="+$("#day").val()+"&from="+$("#from").val()+"&to="+$("#to").val(),
		dataType: 	"json",
		success: 	function(strike){

			$("#load-oldtime").show();
			
			if( strike.count > 0 ) {
				$("#load-oldtime").text("Загрузить (" + strike.count+ ") событий");
			}
			else {
				$("#load-oldtime").text("Грозовые события не найдены");
			}
		}
	});
}

function oldtime_select(){
		
	// Остановить таймер просмотра реального времени
	if (typeof timerRT !=="undefined") {
		clearInterval(timerRT);
	}

	// Сохраним в куки выбранный диапазон событий
	setCookie("day",$("#day").val());
	setCookie("from",$("#from").val());
	setCookie("to",$("#to").val());

	// Удалим из кук данные о просмотре в реальном времени
	deleteCookie("realtime");

	// Уберем отметку на выбранном интервале для просмотра в реальном времени
	$("input:radio[name=realtime]:checked").prop("checked",false);

	// Сделаем запрос на сервер для получения информации по выбранному времени просмотра событий
	$.ajax({
		type:		"GET",
		url: 		"php/oldtime.php?count=no&day="+$("#day").val()+"&from="+$("#from").val()+"&to="+$("#to").val(),
		dataType: 	"json",
		success: 	function(strike){

			// Выведем информацию о текущем режиме просмотра
			$("#message").text("День: " + $("#day").val() + " с: " + $("#from").val() + "ч. до: " + $("#to").val() + "ч. (" + strike.count +")");

			$("#location").text("Доступны датчики: " + (strike.location[1]==false?'':strike.location[1]) + ((strike.location[1]!=false&&strike.location[2]!==false)?', ':'') + (strike.location[2]==false?'':strike.location[2]) );

			$("#error").html(strike.error[1] + (strike.error[1]!=''?'<br/>':'') + strike.error[2]);

			// очистим старыет точки
			LG.clearLayers();
		
			// проверим, есть ли сообщение об ошибке (например, в указанновм диапазоне дат не найдены грозовые события)
			if( strike.count > 0 ) {

				//  переберем все полученные данные
				$.each(strike.data, function( key, val ) {

					// рисуем метку
					var c1 = L.circleMarker([val.latitude, val.longitude], {
						stroke: true, 
						color: '#000', 
						weight: 1, 
						radius: 4, 
						fillColor: '#bbf', 
						fillOpacity: 0.5
					});
					c1.bindPopup(val.popup);
					LG.addLayer(c1);

				});

				// отображаем на карте
				LG.addTo(map);
			}
		}
	});
}



/*
 * Функция для работы с полем дата (описываем настройки и реакцию)
 */
$(document).ready(function(){

	// костыль УДАЛИТЬ!!!!! - написано, если нет связи с mindate.php или он отработал с ошибкой
	minDate = '';

	// получим из базы минимальную дату 
	$.ajax({
		async:		false, 
		type: 		"GET",
		url: 		"php/mindate.php",
		dataType: 	"json",
		success: 	function(date){
			minDate = new Date(date.year,date.month-1,date.day)
		}
	});

	//
	$.datepicker.setDefaults( $.datepicker.regional[ "ru" ] );

	//
	day = $("#day").datepicker({
		defaultDate: 	"+1w",
		changeMonth: 	true,
		changeYear: 	true,
		dateFormat: 	"dd/mm/yy",
		minDate: 		minDate,
		maxDate: 		new Date()
	})
	.on( "change", function() {
		oldtime_count();
    });
    
	function getDate( element ) {
		var date;
		try {
			date = $.datepicker.parseDate( "dd/mm/yy", element.value );
		} catch( error ) {
			date = null;
		}
		return date;
	}
});



/*
 * Функция для работы с выпадающими списками, содержащими часы
 */
$(document).ready(function(){
		
	var to = getCookie("to");
	var from = getCookie("from");

	// заполним значениями часов по умолчанию
	if( from == null ) {
		
		for( var i = 0; i <= 23; i++ ) {
			$("#from").append('<option value="'+i+'">'+i+'&#176;&#176;</option>');
		}
		$('#from option[value="0"]').attr("selected", "selected");
	}
	else {
		for( var i = 0; i < to; i++ ) {
			$("#from").append('<option value="'+i+'" selected>'+i+'&#176;&#176;</option>');
		}
		$("#from").val(from);
	}

	if( to == null ) {
		
		for( var i = 1; i <= 24; i++ ) {
			$("#to").append('<option value="'+i+'">'+i+'&#176;&#176;</option>');
		}
		$('#to option[value="24"]').attr("selected", "selected");
	}
	else {
		
		for( var i = (from*1+1); i <= 24; i++ ) {
			$("#to").append('<option value="'+i+'">'+i+'&#176;&#176;</option>');
		}
		$("#to").val(to);
	}

	// если выбрали врямя С, то подкорректируем список время ДО
	$("#from").change(function() {

		// получим текущее значение из списка "время ДО"
		var sel = $('#to').val();
		
		// очистим список "вермя ДО"
		$("#to").empty();

		// заполним список "время ДО" от значения "время С" до 24-00 
		for( var i = ($("#from").val()*1+1) ; i <= 24 ; i++ ) {
			$("#to").append('<option value="'+i+'">'+i+'&#176;&#176;</option>');
		}

		// вернем отметку текущего значения "время ДО"
		$('#to option[value="'+sel+'"]').attr("selected", "selected");

		if( $("#day").val() != "" ) {
			oldtime_count();
		}
 	});

	// если выбрали время ДО, откорректируем список время С
	$("#to").change(function() {

		// 
		var sel = $('#from').val();
		
		//
		$("#from").empty();
		
		//
		for( var i = 0 ; i < $("#to").val() ; i++ ) {
			$("#from").append('<option value="'+i+'">'+i+'&#176;&#176;</option>');
		}

		// 
		$('#from option[value="'+sel+'"]').attr("selected", "selected");

		if( $("#day").val() != "" ) {
			oldtime_count();		
		}
 	});

 		// если выбрали время ДО, откорректируем список время С
	$("#load-oldtime").click(function() {
		oldtime_select();
		$("#oldtime").hide(300);
		$("#ctrl-oldtime").removeClass("pressed");
		$("#ctrl-oldtime").addClass("unpressed");
		flagOldtime = false;
	});
});

