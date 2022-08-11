<?php

/*
 * Скрипт связывается с базами данных и получает данные по грозовым ударам за заданный диапазон времени
 *
 * Входные параметры day - день за который мы хотим получить информацию 
 * from и to начало и конец временного диапазона в часах
 *
 * Возвращает скрипту front-end данные в формате json данные по каждой из N баз
 * Если есть какие-то ошибки, текст ошибки складывается в error
 * Есть ли есть соединение с базойN, то в location расположение датчика, иначе location => false
 * Есть ли есть данные из баз, то в data координаты событий, иначе пустой массив
 * Количество событий в count
 */

// установим местное время
date_default_timezone_set('Asia/Novosibirsk'); 

// скрипты для раблоты с базой данных
include('postgresql.php'); 



/*
 *  Проверка входных значений на адеркватность
 */
if( !isset($_GET['count']) ) {
	$_GET['count'] = 'no';
}

if( !isset($_GET['day']) ) {
	$_GET['day'] = date('d/m/Y');
}

if( !isset($_GET['from']) || $_GET['from'] <0 || $_GET['from'] > 23 ) {
	$_GET['from'] = 0;
}

if( !isset($_GET['to']) || $_GET['to'] <1 || $_GET['to'] > 24 ) {
	$_GET['from'] = 0;;
	$_GET['to'] = 1;
}

// или тестовые данные, если нужно - php/oldtime.php?day=15/04/2017&from=0&to=1
/*
$_GET['day']='15/04/2017';
$_GET['from'] = 0;
$_GET['to'] = 1;
*/



/*
 * Заготовка для выходных данных
 */
$result = array();
$result['error'] = array('1' => '', '2' => '');
$result['location'] = array('1' => false, '2' => false);
$result['count'] = 0;
$result['data'] = array();



/*
 * Подключим первую и вторую базу с грозовыми событиями и выполним запрос для получения грозовых событий
 */
try { 
	
	$pg1 = new base('../bd1.ini');
	$arr1 = getRes($pg1);
	$result['location'][1] = $arr1['location'];
	$result['count'] += $arr1['count'];
	if($_GET['count'] =='no') {
		$result['data'] = array_merge($result['data'], $arr1['data']);
	}
}
catch (grozaException $e) {

	$result['error'][1] = $e->getMessage();
}
try { 

	$pg2 = new base('../bd2.ini');
	$arr2 = getRes($pg2);
	$result['location'][2] = $arr2['location'];
	$result['count'] += $arr2['count'];
	if($_GET['count'] =='no') {
		$result['data'] = array_merge($result['data'], $arr2['data']);
	}
}
catch (grozaException $e) {

	$result['error'][2] = $e->getMessage();
}

// Вернем результат скрипту на front-end
print json_encode( $result );
//print '<pre>'; print_r($result);



/*
 *
 */
function getRes($pg) {

	// запрос к базе на получение данных
	$from = mb_substr($_GET['day'],6).mb_substr($_GET['day'],3,2).mb_substr($_GET['day'],0,2).' '.$_GET['from'].':00:00';
	$to = mb_substr($_GET['day'],6).mb_substr($_GET['day'],3,2).mb_substr($_GET['day'],0,2).' '.($_GET['to']==24?'23:59:59.999999':$_GET['to'].':00:00');
	$res = $pg->manual('SELECT * FROM "'.$pg->table.'" WHERE time_date BETWEEN \''.$from.'\' AND \''.$to.'\'');

	// если данные найдены 
	if( $res != false ) {

		// создадим массив с данными в формате JSON (дата и время события для попапа и координаты метки)
		$arr = array(); 
		for( $i=0 ; $i<count($res) ; $i++ ) { 
			$arr[] = array(	
				'time_date' => date('j-m-Y H:i:s', strtotime($res[$i]['time_date'])), 
				'popup' => $pg->location.' ('.date('j-m-Y H:i:s', strtotime($res[$i]['time_date'])).')',
				'longitude' => $res[$i]['longitude'], 
				'latitude' => $res[$i]['latitude']); 
		}
	}

	return array(
		'count' => isset($arr)?count($res):0, 
		'data' => isset($arr)?$arr:array(), 
		'location' => $pg->location
	);
}
?>