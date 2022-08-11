/*
 * Скрипты для управления просмотром грозовых данных.
 * Есть два режима просмотра. 
 * Просмотр в реальном времени.
 * Просмотр за некоторый период времени.
 */


$(document).ready(function(){


	// Считаем данные с конфигурационного файла
	$.ajax( {
		async:		false, 
		type: 		"GET",
		url: 		"php/getstart.php",
		dataType: 	"json",
		success: 	function( startdata ) {
			tails = startdata.tails;
			minZoom = startdata.minZoom;
			maxZoom = startdata.maxZoom;
			latitude = startdata.latitude;
			longitude = startdata.longitude;
			zoom = startdata.zoom;
		}
	});

	//Определяем карту, координаты центра и начальный масштаб 
	map = L.map('map').setView([latitude, longitude], zoom);

	// Добавляем на нашу карту слой OpenStreetMap
	L.tileLayer(
		tails, 
		{
			minZoom: minZoom,
			maxZoom: maxZoom,
			attribution: '(c) OSM contributors'
		}
	).addTo(map);

	// Создадим слой-группу, чтобы потом было удобно пачкой удалять метки
	LG = L.layerGroup();

	/*
	 *			 		ПЕРВОНАЧАЛЬНАЯ ЗАГРУЗКА СТАНИЦЫ
	 *
	 * Загрузим данные из кук. Чтобы продолжить работать в том же режиме, что и в предыдущей сессии.
	 * В куках может хранится либо переменные from и to, либо переменная realtime.
	 * Первые означают, что в предыдущей сессии был выбран режим просмотра данных за некоторый период времени.
	 * Наличие в куках переменной realtime - значит был включен просмотр в реальном времени.
	 */

	// Попытка считать переменную from из кук, т.е. предполагаем, что был включен режим просмотра диапазона времени
	day = getCookie("day");

	// Если переменная form не существует, то проверим наличие включенного ранее режима просмотра в реальном времени
	if( day == null ) {

		// Попытка считать переменную realtime из кук, т.е. предполагаем, что бы включен режим просмотра реального времени
		realtime = getCookie("realtime"); 
		
		// Если в прошой сессии не был включен ни один режим, то включаем режим просмотра реального времени с диапазоном в полчаса
		if( realtime == null ) realtime = 1;
		
		// Схораним в куках выбранный режим
		setCookie("realtime",realtime);
  		
		// Включем радиокнопку для выбранного режима в форме и отобразим данные просмотра в титуле
  		$("input:radio[value="+ realtime +"]").attr('checked', 'checked');
		$("#message").text("Реальное время, интервал: " + $("#realtime-span-"+ realtime).text());
		$("#load-oldtime").hide();
		realtime_select();
	}
	// Если в прошлой сессии был включен режим просмотра диапазона событий
	else {

		// Считаем из кук дату просмотра
		$("#day").val(getCookie("day"));

		oldtime_count();		
		oldtime_select();
	}
});

