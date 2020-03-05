<?php

// '/cloudsql/my-playground:asia-east1:wordpress-db';

$dbhost = getenv('dbhost', true) ?: 'unknown';
$dbName = getenv('db', true) ?: 'wordpress';
$dbUser = getenv('user', true) ?: 'unknow-user';
$dbPass = getenv('password', true) ?: 'none';
$dbSocket = getenv('dbSocket', true) ?: 'unknown';


$sqli = new mysqli(null, $dbUser, $dbPass, $dbName, null, $dbSocket);

echo  "Connecting to the database \n";

echo  sprintf("dbhost: %s!\n", $dbhost);
echo  sprintf("Server Name: %s!\n", $dbName);
echo  sprintf("User Name: %s!\n", $dbUser);
echo  sprintf("Password: %s!\n", $dbPass);
echo  sprintf("Socket: %s!\n", $dbSocket);

if ($sqli->connect_error) {


    die("Connection failed: " . $sqli->connect_error);
}
else
{     
	echo "DB Connected Successfully. Host info: " . mysqli_get_host_info($sqli);
}

?>

