<?php

/*
 * Скрипт получает минимальную дату, которая есть в базах данных.
 */ 

// установим местное время
date_default_timezone_set('Asia/Novosibirsk'); 

// скрипты для раблоты с базой данных
include('postgresql.php'); 

$result = array();
$result['error'] = array('','');
$min = date('Y-m-d');

// Подключим первую базу с грозовыми событиями и выполним запрос для получения минимальной дате, которая есть в базе
try {

	$pg1 = new base('../bd1.ini');
	$res1 = $pg1->manual('SELECT MIN(time_date) FROM "'.$pg1->table.'"');
	$min = $res1[0]['min'];
}
catch (grozaException $e) {

	$result['error'][1] = $e->getMessage();
}

// Подключим вторую базу с грозовыми событиями и выполним запрос для получения минимальной дате, которая есть в базе
try {

	$pg2 = new base('../bd2.ini');
	$res2 = $pg2->manual('SELECT MIN(time_date) FROM "'.$pg2->table.'"');
	$min = $min>$res2[0]['min']? $res2[0]['min'] : $min;
}
catch (grozaException $e) {

	$result['error'][2] = $e->getMessage();
}

// 
if( isset($min) ) {
	$result['year']	= mb_substr($min,0,4);
	$result['month'] = mb_substr($min,5,2); 
	$result['day'] = mb_substr($min,8,2);
} 

print json_encode( $result );

?>
