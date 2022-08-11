<?php
/* 
 * 
 * Класс позволяющий соединяться с базой PostgreSQL
 * 
 * Парметры подключения к БД postgresql должны быть описаны в конфигурационном файле (напрмире config.ini)
 * пример:
 * [BD_PostgreSQL]
 * host            ="localhost"   ; адрес хоста с базой данных
 * base            ="arista"      ; имя базы данных
 * user            ="root"        ; имя пользователя базы данных
 * password        ="borland"     ; пароль
 *
 * Пример использования:
 * 
 * // подключим класс
 * include('php/base/postgresql_base.php');
 * 
 * // соединимся с базой
 * $pg = new base('ini/config.ini');
 * 
 */

class grozaException extends Exception{}

class base {

	// 
	public $bd;
	public $table;
	public $location;

	/* конструктор класса
	 *         получает:
	 *                     $ini   - путь до файла и имя файла конфигурации БД
	 */
	public function __construct($ini) {

		// проверим наличие ini файла
		if(!file_exists($ini)) {

			throw new grozaException ('Отсутствует файл  ('.$ini.').');
		}

		// читаем ини файл
		$INI = parse_ini_file($ini, TRUE);
		$this->table = $INI['BD_PostgreSQL']['table'];
		$this->location = $INI['BD_PostgreSQL']['location'];

		// пытаемся соединиться с хостом на котором расположена БД
		$this->bd = pg_connect( 'host = '.$INI['BD_PostgreSQL']['host'].' dbname = '.$INI['BD_PostgreSQL']['base'].' user = '.$INI['BD_PostgreSQL']['user'].' password = '.$INI['BD_PostgreSQL']['password'] );

		// если не удалось соединится с базой данных
		if( $this->bd == false ) {

			throw new grozaException ('Нет соединения с '.$INI['BD_PostgreSQL']['host'].'.');
		}
	}



	/*
	 * Функция выполняет ручной запрос
	 *         Получает:
	 *                  $zapros    - выполняемый запрос
	 *         Возвращает:
	 *                    возвращает ассоциативный массив
	 */
	function manual( $zapros ) {

		//
		$result = '';
		
		// выполним запрос
		$res = pg_query($this->bd, $zapros);

		// если результат успешный
		if( !$res ) {
			throw new grozaException ('Ошибка при выполнении запроса.');
		}
			
		// обработаем результат
		while( $row = pg_fetch_array($res) ) {
				
			$result[]=$row;
		}
      	return $result;
	}

}
?>
