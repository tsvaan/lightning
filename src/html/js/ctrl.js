/*
 * Реакция при нажатии на кнопки управления режимом просмотра
 * Если нажимаем на верхнюю кнопку - сделаем ее активной, затем покажем окно с параметрами просмотра в реальном времени
 * и, при необходимости, сделаем неактивной нижнюю кнопку и спрячем окно с параметрами просмотра в диапазоне событий
 * Алгоритм действий при нажатии на нижнюю кнопку - аналогичный
 */


// Переменная-флаг, true - если окно с выбором параметров просмотра в реальном времени активно. 
var flagRealtime = false;

// Переменная-флаг, true - если окно с выбором параметров просмотра в диапазоне времени активно.
var flagOldtime = false;

$(document).ready(function(){

	// Нажали на кнопку "просмотр в реальном времени"
	$("#ctrl-realtime, #rezim_realtime").click(function(){

		// Если окошко "параметры просмотра в реальном времени" еще не активно
		if (!flagRealtime) {
			// Отметим кнопку "просмотр в реальном времени" как активную
			$("#ctrl-realtime").removeClass("unpressed");
			$("#ctrl-realtime").addClass("pressed");
			// Покажем окошко "параметры просмотра в реальном времени"
			flagRealtime = true;
			$("#realtime").show(300);
			// Возможно была активна кнопка "просмотр диапазона событий" - сделаем ее неактивной
			if (flagOldtime) {
				$("#ctrl-oldtime").removeClass("pressed");
				$("#ctrl-oldtime").addClass("unpressed");
				// Возможно было активно окно "просмотр диапазона событий" - сделаем его неактивным
				flagOldtime = false
				$("#oldtime").hide(300);
			}
		}
		// Если окошко "параметры просмотра в реальном времени" было активно
		else {

			// Отметим кнопку "просмотр в реальном времени" как неактивную
			$("#ctrl-realtime").removeClass("pressed");
			$("#ctrl-realtime").addClass("unpressed");
			// Отметим флаг и спрячем окошко "параметры просмотра в реальном времени"
			flagRealtime = false
			$("#realtime").hide(300);	
		}
	});

	// Нажали на кнопку "просмотр диапазона событий"
	$("#ctrl-oldtime, #rezim_oldtime").click(function(){

		if (!flagOldtime) {
			// Отметим кнопку "просмотр в диапазона событий" как активную
			$("#ctrl-oldtime").removeClass("unpressed");
			$("#ctrl-oldtime").addClass("pressed");
			// Покажем окошко "параметры просмотра диапазона событий"
			flagOldtime = true;
			$("#oldtime").show(300);
			// Возможно была активна кнопка "просмотр в реальном времени" - сделаем ее неактивной
			if (flagRealtime) {
				$("#ctrl-realtime").removeClass("pressed");
				$("#ctrl-realtime").addClass("unpressed");
				// Возможно было активно окно "просмотр в реальном времени" - сделаем его неактивным
				flagRealtime = false
				$("#realtime").hide(300);
			}
		}
		// Если окошко "параметры просмотра диапазона событий" было активно
		else {
			
			// Отметим кнопку "просмотр диапазона событий" как неактивную
			$("#ctrl-oldtime").removeClass("pressed");
			$("#ctrl-oldtime").addClass("unpressed");
			// Отметим флаг и спрячем окошко "параметры просмотра в реальном времени"
			flagOldtime = false
			$("#oldtime").hide(300);	
		}
	});
});