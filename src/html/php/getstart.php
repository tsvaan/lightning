<?php

/* 0.0.1
 * Получим параметры для старта приложения и пердадим их скрипту
 */ 

// читаем ини файл
$INI = parse_ini_file('../config.ini', TRUE);
    
// отправим данные клиенту
print json_encode(array('tails' => $INI['LeafLet']['tails'], 
						'minZoom' => $INI['LeafLet']['minZoom'], 
						'maxZoom' => $INI['LeafLet']['maxZoom'], 
						'latitude' => $INI['LeafLet']['latitude'], 
						'longitude' => $INI['LeafLet']['longitude'], 
						'zoom' => $INI['LeafLet']['zoom']));
?>
