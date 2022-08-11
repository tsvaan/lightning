/* 
 * Действия в случае выбора просмотра в реальном времени
 */


// Свойства кружочков: цвет, радиус, прозрачность
clr = ['#f00', '#00f', '#66f', '#99f', '#bbf', '#fff'];
rds = [12, 9, 6, 5, 4, 4];
pct = [.5, .5, .5, .5, .5, .5, ];

function realtime_show() {
	
	$.ajax({
		type:     "GET",
		url:      "php/realtime.php?realtime="+realtime+"&metka1="+metka1+"&metka2="+metka2,
		dataType: "json",
		success: function(strike){
		
			// Покажем в заголовке информацию о просмотре в реальном времени
			$("#message").text("Реальное время, интервал: " + $("#realtime-span-"+ realtime).text() + " (" + (strike.count) +")");

			$("#location").text("Доступны датчики: " + (strike.location[1]==false?'':strike.location[1]) + ((strike.location[1]!=false&&strike.location[2]!==false)?', ':'') + (strike.location[2]==false?'':strike.location[2]) );

			$("#error").text(strike.error[1]+' '+strike.error[2]);

			metka1 = strike.metka[1];
			metka2 = strike.metka[2];
			
			// очистим старыет точки
			LG.clearLayers();

			// проверим, есть ли сообщение об ошибке (например, в указанновм диапазоне дат не найдены грозовые события)
			if( strike.count > 0 ) {
				
				//  переберем все полученные данные
				$.each(strike.data, function( key, val ) {

					// ставим отметку события
					var c1 = L.circleMarker([val.latitude, val.longitude], {
						stroke: true, 
						color: '#000', 
						weight: 1, 
						radius: rds[val.index], 
						fillColor: clr[val.index], 
						fillOpacity: pct[val.index]
					});
					c1.bindPopup(val.popup+'-'+metka1+'-'+metka2);
					LG.addLayer(c1);
				});
			}

			// отображаем на карте
			LG.addTo(map);
		}
	});
}

function realtime_select() {

	// Определим какой интервал был выбран (0.5 часа, 1 час и т.д. )
	realtime = $("input:radio[name=realtime]:checked").val();

	metka1 = 0;
	metka2 = 0;

	// Сохраним в куках выбранный параметр
	setCookie("realtime",realtime); 

	// Удалим из кук параметры просмотра диапазона событий
	deleteCookie("day"); 
	deleteCookie("from"); 
	deleteCookie("to"); 

	// Уберем из формы ввода выбранные ранее параметры просмотра диапазона событий 
	$("#day").val("");	
	
	//
	$("#load-oldtime").hide();	
	
	// Получить первую порцию данных за весь запрашиваемый период 
	realtime_show();
	
	// Получить обновление с интервалом в 1 секунду
	timerRT = setInterval(function() {
			
		// Получить обнолвения с некоторым периодом
		realtime_show();
	}, 10000);
}

// Функция вызывается в случае если изменили интервал просмотра в реальном времени
$(document).ready(function() {

	$("input:radio").click(function() {
		realtime_select();
		$("#realtime").hide(300);
		$("#ctrl-realtime").removeClass("pressed");
		$("#ctrl-realtime").addClass("unpressed");
		flagRealtime = false
	});
});


