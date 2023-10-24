<?php
$path = ".";
if(isset($_GET['pagename']))
{
    $path=$_GET['pagename'];
}

$dh = opendir($path);
$i=1;
while (($file = readdir($dh)) !== false) {
    if($file != "." && $file != ".." && $file != "index.php" && $file != ".htaccess" && $file != "error_log" && $file != "cgi-bin") {
        /*
        if (is_dir($path."/".$file)){
            echo "<img src=\"http://icons.iconarchive.com/icons/yusuke-kamiyamane/fugue/16/folder-horizontal-icon.png\"> ";
            echo "<a href=\"./fileindex.php?pagename=$path/$file\">$file</a><br>";
        }
        else{
            echo "<a href='$path/$file'>$file</a><br>";
        }
        */
        $file_parts = pathinfo($file);
        //if ($file_parts["extension"] == "png") { echo "<img src='$path/$file'>$file> "; }
        if ($file_parts["extension"] == "png") { echo "<img src='$path/$file'> "; }
        //else {echo $file;}
        $i++;
    }
}
closedir($dh);
?>
