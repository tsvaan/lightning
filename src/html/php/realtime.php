<?php 

/*
 * Скрипт связывается с базами данных и получает данные по грозовым ударам за последние X часов
 *
 * Входные параметры realtime = [1 - 6] определяет время (Х часов) за которое нужны грозовые события
 * metkaN - время последнего события, все события прошедшие позже являются новыми
 *
 * Возвращает скрипту front-end данные в формате json данные по каждой из N баз
 * Если есть какие-то ошибки, текст ошибки складывается в error
 * Есть ли есть соединение с базойN, то в location расположение датчика, иначе location => false
 * metkaN - определяет время последнего события, если запрос приходит с metka!=0, то события произошедшие позднее помечаем индексом 0
 * Есть ли есть данные из баз, то в data координаты событий, иначе пустой массив
 * Количество событий в count
 */

// установим местное время
date_default_timezone_set('Asia/Novosibirsk'); 

// скрипты для раблоты с базой данных
include('postgresql.php'); 

// Заготовка для выходных данных
$result = array();
$result['error'] = array('1' => '', '2' => '');
$result['location'] = array('1' => false, '2' => false);
$result['metka'] = array('1' => 0, '2' => 0);
$result['count'] = 0;
$result['data'] = array();

// Проверяем соотвествие входных параметров. Параметр, определяющий время Х, должен быть равен целому числу в диапазоне [1-6]
if( !isset($_GET['realtime']) || $_GET['realtime'] < 1 || $_GET['realtime'] > 6 ) {

	$_GET['realtime'] = 1;
}

// Проверяем соотвествие входных параметров. Параметр, определяющий время последнего полученного грозовго события
$_GET['metka1'] = isset($_GET['metka1']) ? $_GET['metka1'] : 0; 
$_GET['metka2'] = isset($_GET['metka2']) ? $_GET['metka2'] : 0; 

// Подключим первую базу с грозовыми событиями и выполним запрос для получения грозовых событий в реальном времени
try { 
	
	$pg1 = new base('../bd1.ini');
	$arr1 = getRes($pg1, $_GET['metka1']);
	$result['location'][1] = $arr1['location'];
	$result['metka'][1] = $arr1['metka'];
	$result['count'] += $arr1['count'];
	$result['data'] = array_merge($result['data'], $arr1['data']);
}
catch (grozaException $e) {

	$result['error'][1] = $e->getMessage();
}

// Подключим вторую базу с грозовыми событиями и выполним запрос для получения минимальной дате, которая есть в базе
try { 

	$pg2 = new base('../bd2.ini');
	$arr2 = getRes($pg2, $_GET['metka2']);
	$result['location'][2] = $arr2['location'];
	$result['metka'][2] = $arr2['metka'];
	$result['count'] += $arr2['count'];
	$result['data'] = array_merge($result['data'], $arr2['data']);
}
catch (grozaException $e) {

	$result['error'][2] = $e->getMessage();
}

// Вернем результат скрипту на front-end
print json_encode( $result );
//print '<pre>'; print_r($result);


/* Функция делает запрос к базе данных ($pg) и получается список событий за последние Х часов определенных перменной $_GET['realtime']
 * Возвращает массив с данными error, error_text, count, data, location 
 */
function getRes($pg, $metka) {

	// массив временных значений (в часах)
	$interval = array(.5,1,2,8,12,24); 

	// запрос к базе на получение данных
	$res = $pg->manual('SELECT * FROM "'.$pg->table.'" WHERE (time_date > NOW() - INTERVAL \''.$interval[$_GET['realtime']-1].' HOUR\')'); 
	
	// если данные найдены 
	if( $res != false ) {

		$arr = razbor($res, $interval, 5, $pg->location );

		// запрос к базе и получение самых свежих грозовых событий
		if( $metka !=0 ) {

			// запрос к базе на получение данных
			//$newres = $pg->manual('SELECT * FROM "'.$pg->table.'" WHERE ( date_trunc(\'second\',time_date) > \''.$metka.'\')'); 
			$newres = $pg->manual('SELECT * FROM "'.$pg->table.'" WHERE ( time_date > \''.$metka.'\')'); 

			if( $newres != false ) {
			
				// сформируем массив, содержащий долготу и широту 
				$newarr = razbor($newres, $interval, 0, $pg->location ); 
				$arr = array_merge( $arr, $newarr);
			}
		}
	}

	return array(
		'count' => isset($arr)?count($arr):0, 
		'data' => isset($arr)?$arr:array(), 
		'location' => $pg->location, 
		//'metka' => isset($arr)?max(array_column($arr,'time_date')):0
		'metka' => isset($arr)?max(array_column($arr,'time_stamp')):0
	);
}

// сформируем массив, содержащий долготу, широту, время грозового события и цифровую отметку отметка меняется в диапазоне от 0 до maxindex
function razbor($res, $interval, $maxindex, $location) {

	$arr = array(); 
	
	for( $i=0 ; $i<count($res) ; $i++ ) { 

		// определим индекс точки - по нему определяем свойства показа
		if( $maxindex > 0) {
			$index = ceil( (time()-strtotime($res[$i]['time_date']))/$interval[$_GET['realtime']-1]/60/60*$maxindex);
			$index = $index>$maxindex ? $maxindex : $index; 
			$index = $index<1 ? 1 : $index; 
		}
		else {
			$index = 0;
		}

		// сформируем массив грозовых событий
		$arr[] = array(	
			//'time_date' => date('j-m-Y H:i:s', strtotime($res[$i]['time_date'])), 
			'time_stamp' => $res[$i]['time_date'], 
			'popup' => $location.' ('.date('j-m-Y H:i:s', strtotime($res[$i]['time_date'])).')',
			'longitude' => $res[$i]['longitude'], 
			'latitude' => $res[$i]['latitude'],
			'index' => $index ); 
	}
	return $arr;
}
?>