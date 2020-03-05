<?php
//$servername = "";
//$username = "";
//$password = "";
$servername = getenv('servername', true) ?: 'unknown';
$username = getenv('username', true) ?: 'unknow-user';
$password = getenv('password', true) ?: 'none';
     
     
     
	echo  "Connecting to the database \n";
	echo  sprintf("Server Name: %s!\n", $servername);
	echo  sprintf("User Name: %s!\n", $username);
	echo  sprintf("Password: %s!\n", $password);

// Create connection
// $sqli = new mysqli(null, $dbUser, $dbPass, $dbName, null, $dbSocket);

 $conn = new mysqli($servername, $username, $password);

// // Check connection
 if ($conn->connect_error) {
     die("Connection failed: " . $conn->connect_error);
     }

     echo "DB Connected successfully";
?>

